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
from pydantic import BaseModel, Field, EmailStr
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

# Resend setup
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
JWT_SECRET = os.environ.get('JWT_SECRET')

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
    email: EmailStr
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


# ─── Email Templates ─────────────────────────────────────
def admin_notification_html(booking: dict) -> str:
    return f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 32px; background: #f8fafc; border-radius: 12px;">
        <div style="background: #2563eb; padding: 24px; border-radius: 8px 8px 0 0; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">New Consultation Request</h1>
        </div>
        <div style="background: #ffffff; padding: 32px; border-radius: 0 0 8px 8px; border: 1px solid #e2e8f0;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #64748b; width: 140px;">Name</td><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; font-weight: 600; color: #0f172a;">{booking['full_name']}</td></tr>
                <tr><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #64748b;">Email</td><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #0f172a;">{booking['email']}</td></tr>
                <tr><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #64748b;">Phone</td><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #0f172a;">{booking['phone']}</td></tr>
                <tr><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #64748b;">Service</td><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #2563eb; font-weight: 600;">{booking['service']}</td></tr>
                <tr><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #64748b;">Deadline</td><td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; color: #0f172a;">{booking.get('project_deadline', 'Not specified')}</td></tr>
                <tr><td style="padding: 12px 0; color: #64748b; vertical-align: top;">Description</td><td style="padding: 12px 0; color: #0f172a;">{booking['project_description']}</td></tr>
            </table>
        </div>
        <p style="text-align: center; color: #94a3b8; font-size: 12px; margin-top: 24px;">TIVROX Admin Notification</p>
    </div>
    """

def client_confirmation_html(name: str) -> str:
    return f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 32px; background: #f8fafc; border-radius: 12px;">
        <div style="background: #2563eb; padding: 24px; border-radius: 8px 8px 0 0; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">TIVROX</h1>
        </div>
        <div style="background: #ffffff; padding: 40px 32px; border-radius: 0 0 8px 8px; border: 1px solid #e2e8f0; text-align: center;">
            <h2 style="color: #0f172a; margin: 0 0 16px 0; font-size: 22px;">Thank You, {name}!</h2>
            <p style="color: #64748b; line-height: 1.8; font-size: 16px; margin: 0 0 24px 0;">
                We have received your consultation request and our team is reviewing it. We will respond within <strong style="color: #2563eb;">24 hours</strong>.
            </p>
            <div style="background: #f1f5f9; border-radius: 8px; padding: 20px; margin: 24px 0;">
                <p style="color: #0f172a; margin: 0; font-size: 14px;">
                    If you have any urgent queries, feel free to reach us at<br/>
                    <a href="mailto:chiluverushivaprasad02@gmail.com" style="color: #2563eb; text-decoration: none; font-weight: 600;">chiluverushivaprasad02@gmail.com</a>
                </p>
            </div>
            <p style="color: #94a3b8; font-size: 13px; margin: 24px 0 0 0;">We Build Scalable Digital Systems.</p>
        </div>
    </div>
    """


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
    ip = get_client_ip(request)
    if not check_rate_limit(ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

    # Honeypot check
    if data.company_url:
        raise HTTPException(status_code=400, detail="Invalid submission")

    # Sanitize inputs
    booking = {
        "id": str(uuid.uuid4()),
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

    # Validate required fields
    if not booking["full_name"] or not booking["email"] or not booking["phone"] or not booking["project_description"]:
        raise HTTPException(status_code=400, detail="All required fields must be filled")

    # Email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, booking["email"]):
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Save to MongoDB
    await db.bookings.insert_one(booking)

    # Send emails (non-blocking)
    try:
        # Admin notification
        admin_params = {
            "from": SENDER_EMAIL,
            "to": [ADMIN_EMAIL],
            "subject": f"New Consultation Request - {booking['full_name']}",
            "html": admin_notification_html(booking)
        }
        await asyncio.to_thread(resend.Emails.send, admin_params)

        # Client confirmation
        client_params = {
            "from": SENDER_EMAIL,
            "to": [booking["email"]],
            "subject": "Your Consultation Request - TIVROX",
            "html": client_confirmation_html(booking["full_name"])
        }
        await asyncio.to_thread(resend.Emails.send, client_params)
        logger.info(f"Emails sent for booking {booking['id']}")
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")

    return {
        "status": "success",
        "message": "Your consultation request has been submitted successfully. We will contact you within 24 hours.",
        "booking_id": booking["id"]
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
