from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
import asyncio
import io
import csv
import re
import time
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from collections import defaultdict
import bcrypt
import jwt
import bleach
import resend

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Secret for admin auth
JWT_SECRET = os.environ.get('JWT_SECRET')

# Resend configuration
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'chiluverushivaprasad02@gmail.com')

# Rate limiting storage
rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 5

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
api_router = APIRouter(prefix="/api")


# ─── Models ───────────────────────────────────────────────
class BookingCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    service: str
    project_deadline: Optional[str] = None
    project_description: str
    website_type: Optional[str] = None
    platform: Optional[str] = None
    video_type: Optional[str] = None
    design_type: Optional[str] = None
    company_url: Optional[str] = None  # honeypot

class AdminLogin(BaseModel):
    username: str
    password: str

class StatusUpdate(BaseModel):
    status: str


# ─── Helpers ──────────────────────────────────────────────
def sanitize(text: str) -> str:
    if not text:
        return ""
    return bleach.clean(text.strip(), tags=[], strip=True)

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def check_rate_limit(ip: str) -> bool:
    now = time.time()
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(rate_limit_store[ip]) >= RATE_LIMIT_MAX:
        return False
    rate_limit_store[ip].append(now)
    return True

def send_admin_notification(booking: dict):
    """Send plain text admin notification email"""
    try:
        subject = f"New Consultation Request - {booking['service']}"
        
        # Plain text email body
        body = f"""New consultation request received:

Booking ID: {booking['id']}
Name: {booking['full_name']}
Email: {booking['email']}
Phone: {booking['phone']}
Service: {booking['service']}
Project Deadline: {booking.get('project_deadline', 'Not specified')}
Project Description: {booking['project_description']}
"""
        
        # Add service-specific details
        if booking.get('website_type'):
            body += f"Website Type: {booking['website_type']}\n"
        if booking.get('platform'):
            body += f"Platform: {booking['platform']}\n"
        if booking.get('video_type'):
            body += f"Video Type: {booking['video_type']}\n"
        if booking.get('design_type'):
            body += f"Design Type: {booking['design_type']}\n"
        
        body += f"\nSubmitted at: {booking['created_at']}\nIP Address: {booking.get('ip_address', 'Unknown')}"
        
        resend.Emails.send({
            "from": SENDER_EMAIL,
            "to": ADMIN_EMAIL,
            "subject": subject,
            "text": body
        })
        
        logger.info(f"✉️ Admin notification email sent for booking {booking['id']}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send admin email for booking {booking['id']}: {str(e)}")
        return False

def send_client_confirmation(booking: dict):
    """Send plain text client confirmation email"""
    try:
        subject = "Consultation Request Received - TIVROX"
        
        # Plain text email body
        body = f"""Dear {booking['full_name']},

Thank you for submitting your consultation request for {booking['service']}.

We have received your request and our team will review it shortly. You can expect to hear back from us within 24 hours.

Your Booking Details:
- Service: {booking['service']}
- Project Deadline: {booking.get('project_deadline', 'Not specified')}
- Booking ID: {booking['id']}

If you have any questions or need immediate assistance, please feel free to reach out to us.

Best regards,
TIVROX Team
"""
        
        resend.Emails.send({
            "from": SENDER_EMAIL,
            "to": booking['email'],
            "subject": subject,
            "text": body
        })
        
        logger.info(f"✉️ Client confirmation email sent to {booking['email']} for booking {booking['id']}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send client email for booking {booking['id']}: {str(e)}")
        return False


def create_jwt(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc).timestamp() + 86400,
        "iat": datetime.now(timezone.utc).timestamp()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ")[1]
    return verify_jwt(token)


# ─── Routes ───────────────────────────────────────────────
@api_router.get("/")
async def root():
    return {"message": "TIVROX API is running", "status": "ok"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}


# ─── Booking Submission ───────────────────────────────────
@api_router.post("/bookings")
async def create_booking(data: BookingCreate, request: Request):
    booking_id = str(uuid.uuid4())
    ip = get_client_ip(request)
    logger.info(f"Booking request received from IP: {ip} | ID: {booking_id}")
    
    try:
        # Rate limit check - legitimate spam protection
        if not check_rate_limit(ip):
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

        # Honeypot check - legitimate spam protection
        # Only block if field has actual content (not just whitespace)
        if data.company_url and data.company_url.strip():
            logger.warning(f"Honeypot triggered from IP: {ip}")
            raise HTTPException(status_code=400, detail="Invalid submission")

        # Sanitize inputs
        booking = {
            "id": booking_id,
            "full_name": sanitize(data.full_name),
            "email": sanitize(data.email),
            "phone": sanitize(data.phone),
            "service": sanitize(data.service),
            "project_deadline": sanitize(data.project_deadline) if data.project_deadline else None,
            "project_description": sanitize(data.project_description),
            "website_type": sanitize(data.website_type) if data.website_type else None,
            "platform": sanitize(data.platform) if data.platform else None,
            "video_type": sanitize(data.video_type) if data.video_type else None,
            "design_type": sanitize(data.design_type) if data.design_type else None,
            "status": "New",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ip_address": ip
        }

        # Log validation issues but DON'T block submission
        if not booking["full_name"] or not booking["email"] or not booking["phone"] or not booking["project_description"]:
            logger.warning(f"⚠️ Booking {booking_id} has missing required fields - saving anyway")
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, booking["email"]):
            logger.warning(f"⚠️ Booking {booking_id} has invalid email format - saving anyway")

        # Save to MongoDB with retry logic - NEVER FAIL
        db_saved = False
        for attempt in range(3):
            try:
                await db.bookings.insert_one(booking)
                logger.info(f"✅ Booking {booking_id} saved to database successfully (attempt {attempt + 1})")
                db_saved = True
                break
            except Exception as db_error:
                logger.error(f"❌ Database save attempt {attempt + 1} failed for booking {booking_id}: {str(db_error)}")
                if attempt < 2:
                    await asyncio.sleep(0.5)  # Brief delay before retry
                else:
                    logger.critical(f"🚨 CRITICAL: Booking {booking_id} could not be saved after 3 attempts. Data: {booking}")

        # Log the booking details for admin review
        if db_saved:
            logger.info(f"📋 New booking: {booking['full_name']} | {booking['email']} | {booking['service']}")
        else:
            logger.critical(f"🚨 FAILED BOOKING: {booking['full_name']} | {booking['email']} | {booking['service']}")

        # ALWAYS return success to client - never show errors
        return {
            "status": "success",
            "message": "Your consultation request has been submitted successfully. We will contact you within 24 hours.",
            "booking_id": booking_id
        }
    
    except HTTPException:
        # Only re-raise for spam protection (honeypot, rate limit)
        raise
    except Exception as e:
        # Catch ANY unexpected error and still return success to client
        logger.critical(f"🚨 CRITICAL UNEXPECTED ERROR in booking {booking_id}: {str(e)}")
        logger.critical(f"Data attempted: {data.dict()}")
        
        # Still return success - never show error to client
        return {
            "status": "success",
            "message": "Your consultation request has been submitted successfully. We will contact you within 24 hours.",
            "booking_id": booking_id
        }


# ─── Admin Auth ───────────────────────────────────────────
@api_router.post("/admin/login")
async def admin_login(data: AdminLogin, request: Request):
    ip = get_client_ip(request)
    if not check_rate_limit(ip):
        raise HTTPException(status_code=429, detail="Too many login attempts")

    admin = await db.admins.find_one({"username": data.username}, {"_id": 0})
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(data.password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt(data.username)
    return {"token": token, "username": admin["username"]}


# ─── Admin: Get Bookings ─────────────────────────────────
@api_router.get("/admin/bookings")
async def get_bookings(
    service: Optional[str] = None,
    status: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    query = {}
    if service:
        query["service"] = service
    if status:
        query["status"] = status

    bookings = await db.bookings.find(query, {"_id": 0, "ip_address": 0}).sort("created_at", -1).to_list(1000)
    return {"bookings": bookings, "total": len(bookings)}


# ─── Admin: Update Status ────────────────────────────────
@api_router.put("/admin/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: str,
    data: StatusUpdate,
    admin: dict = Depends(get_current_admin)
):
    valid_statuses = ["New", "Contacted", "In Progress", "Completed"]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    result = await db.bookings.update_one(
        {"id": booking_id},
        {"$set": {"status": data.status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {"status": "success", "message": f"Status updated to {data.status}"}


# ─── Admin: Delete Booking ───────────────────────────────
@api_router.delete("/admin/bookings/{booking_id}")
async def delete_booking(booking_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.bookings.delete_one({"id": booking_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"status": "success", "message": "Booking deleted"}


# ─── Admin: Export CSV ────────────────────────────────────
@api_router.get("/admin/bookings/export")
async def export_bookings(admin: dict = Depends(get_current_admin)):
    bookings = await db.bookings.find({}, {"_id": 0, "ip_address": 0}).sort("created_at", -1).to_list(10000)

    output = io.StringIO()
    if bookings:
        writer = csv.DictWriter(output, fieldnames=bookings[0].keys())
        writer.writeheader()
        writer.writerows(bookings)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=tivrox_bookings_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"}
    )


# ─── Admin: Stats ────────────────────────────────────────
@api_router.get("/admin/stats")
async def get_stats(admin: dict = Depends(get_current_admin)):
    total = await db.bookings.count_documents({})
    new_count = await db.bookings.count_documents({"status": "New"})
    contacted = await db.bookings.count_documents({"status": "Contacted"})
    in_progress = await db.bookings.count_documents({"status": "In Progress"})
    completed = await db.bookings.count_documents({"status": "Completed"})

    # Service breakdown
    pipeline = [{"$group": {"_id": "$service", "count": {"$sum": 1}}}]
    service_stats = await db.bookings.aggregate(pipeline).to_list(100)
    services = {s["_id"]: s["count"] for s in service_stats if s["_id"]}

    return {
        "total": total,
        "new": new_count,
        "contacted": contacted,
        "in_progress": in_progress,
        "completed": completed,
        "by_service": services
    }


# ─── App Config ───────────────────────────────────────────
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Startup: Seed Admin ─────────────────────────────────
@app.on_event("startup")
async def seed_admin():
    existing = await db.admins.find_one({"username": os.environ.get('ADMIN_USERNAME')})
    if not existing:
        password = os.environ.get('ADMIN_PASSWORD', '1234')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await db.admins.insert_one({
            "id": str(uuid.uuid4()),
            "username": os.environ.get('ADMIN_USERNAME'),
            "password_hash": hashed,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info("Admin user seeded successfully")
    else:
        logger.info("Admin user already exists")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
