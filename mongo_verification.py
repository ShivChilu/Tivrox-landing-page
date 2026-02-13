#!/usr/bin/env python3
"""
MongoDB Verification Test - Check if booking was saved
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def verify_booking_in_db(booking_id):
    """Verify the booking was saved to MongoDB"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Find the booking
        booking = await db.bookings.find_one({"id": booking_id}, {"_id": 0})
        
        if booking:
            print("✅ SUCCESS: Booking found in MongoDB!")
            print(f"📋 Booking Details:")
            print(f"   ID: {booking['id']}")
            print(f"   Name: {booking['full_name']}")
            print(f"   Email: {booking['email']}")
            print(f"   Service: {booking['service']}")
            print(f"   Status: {booking['status']}")
            print(f"   Created: {booking['created_at']}")
            return True
        else:
            print("❌ FAILED: Booking not found in MongoDB")
            return False
            
    except Exception as e:
        print(f"❌ ERROR checking MongoDB: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    # Test the booking ID from our test
    booking_id = "722b3574-3dd7-4c74-b8e7-3b561a1c8532"
    print(f"🔍 Verifying booking {booking_id} in MongoDB...")
    
    result = asyncio.run(verify_booking_in_db(booking_id))
    
    if result:
        print("🎉 MongoDB verification PASSED!")
    else:
        print("⚠️ MongoDB verification FAILED!")