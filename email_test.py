#!/usr/bin/env python3
"""
TIVROX Email Delivery Test - Using verified email address
"""

import requests
import json

# Backend URL from frontend/.env
BACKEND_URL = "https://honeypot-fix.preview.emergentagent.com/api"

def test_email_with_verified_address():
    """Test booking creation with verified email address to confirm email sending"""
    booking_data = {
        "full_name": "Test User TIVROX",
        "email": "chiluverushivaprasad02@gmail.com",  # Verified email address
        "phone": "+1234567890",
        "service": "Website Development",
        "project_deadline": "2 weeks",
        "project_description": "Testing email delivery functionality for TIVROX consultation booking system",
        "website_type": "Business"
    }
    
    print("🧪 Testing booking creation with verified email address...")
    print("📧 Email should be sent to: chiluverushivaprasad02@gmail.com")
    print()
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/bookings",
            json=booking_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data}")
            print(f"📋 Booking ID: {data.get('booking_id')}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_email_with_verified_address()
    if success:
        print("\n📧 Check backend logs for 'Emails sent for booking' or 'Email sending failed' messages")
        print("📧 If successful, both admin notification and client confirmation emails should be sent")
    exit(0 if success else 1)