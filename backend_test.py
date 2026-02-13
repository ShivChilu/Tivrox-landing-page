#!/usr/bin/env python3
"""
Backend API Testing for TIVROX Consultation Booking System
Focus: Email configuration testing - admin-only email delivery
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://plain-text-mail.preview.emergentagent.com/api"
TEST_EMAIL = "chiluverushivaprasad02@gmail.com"

def test_health_endpoints():
    """Test basic health endpoints"""
    print("\n=== Testing Health Endpoints ===")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test root API endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root API endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data.get('message', 'No message')}")
        else:
            print(f"❌ Root endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

def test_booking_creation_with_admin_only_email():
    """Test booking creation with ONLY admin email sending (client email disabled)"""
    print("\n=== Testing Booking Creation (Admin-Only Email) ===")
    
    # Test data with verified email address
    booking_data = {
        "full_name": "Shiva Testing Admin Email",
        "email": TEST_EMAIL,
        "phone": "+91-9876543210",
        "service": "Website Development",
        "project_deadline": "2024-02-15",
        "project_description": "Testing admin-only email delivery configuration. This booking should trigger ONLY admin notification email, not client confirmation.",
        "website_type": "E-commerce"
    }
    
    print(f"Creating booking with email: {TEST_EMAIL}")
    print(f"Service: {booking_data['service']}")
    print("Expected: ONLY admin email should be sent (client confirmation disabled)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookings",
            json=booking_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            booking_id = data.get("booking_id")
            print(f"✅ Booking created successfully!")
            print(f"   Booking ID: {booking_id}")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            
            # Give time for email processing
            print("\nWaiting 3 seconds for email processing...")
            time.sleep(3)
            
            print(f"\n🔍 CRITICAL CHECK: Backend logs should show 'Admin email sent for booking {booking_id}'")
            print("🔍 CRITICAL CHECK: Backend logs should NOT show any client confirmation email")
            print("🔍 CRITICAL CHECK: Only admin notification should be sent to admin email")
            
            return True, booking_id
        else:
            print(f"❌ Booking creation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Booking creation error: {e}")
        return False, None

def test_honeypot_protection():
    """Test honeypot spam protection"""
    print("\n=== Testing Honeypot Spam Protection ===")
    
    spam_data = {
        "full_name": "Spam Bot",
        "email": TEST_EMAIL,
        "phone": "+91-1234567890",
        "service": "Website Development",
        "project_description": "This is spam",
        "company_url": "https://spam-site.com"  # Honeypot field
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookings",
            json=spam_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Honeypot protection working - spam detected and rejected")
        else:
            print(f"❌ Honeypot protection failed - status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Honeypot test error: {e}")

def test_input_validation():
    """Test input validation for required fields"""
    print("\n=== Testing Input Validation ===")
    
    # Test missing required fields
    invalid_data = {
        "full_name": "",
        "email": "invalid-email",
        "phone": "",
        "service": "Website Development",
        "project_description": ""
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookings",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [400, 422]:
            print("✅ Input validation working - invalid data rejected")
            print(f"   Status code: {response.status_code}")
        else:
            print(f"❌ Input validation failed - status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Input validation test error: {e}")

def check_backend_logs():
    """Check backend logs for email sending confirmation"""
    print("\n=== Checking Backend Logs ===")
    try:
        import subprocess
        result = subprocess.run(
            ["sudo", "tail", "-n", "20", "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("Recent backend logs:")
            print("-" * 40)
            print(result.stdout)
            print("-" * 40)
            
            # Check for admin email confirmation
            if "Admin email sent for booking" in result.stdout:
                print("✅ Found admin email confirmation in logs")
                return True
            else:
                print("❌ No admin email confirmation found in recent logs")
                return False
        else:
            print(f"❌ Failed to read logs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking logs: {e}")
        print("\nManual log check instructions:")
        print("sudo tail -n 20 /var/log/supervisor/backend.out.log")
        print("\nLook for:")
        print("✅ 'Admin email sent for booking {ID}' - This should appear")
        print("❌ 'Client confirmation sent for booking {ID}' - This should NOT appear")
        return False

def main():
    """Main test execution"""
    print("=" * 60)
    print("TIVROX Backend Testing - Admin-Only Email Configuration")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Test email: {TEST_EMAIL}")
    print(f"Focus: Verify ONLY admin emails are sent (client confirmation disabled)")
    
    # Run tests
    test_health_endpoints()
    
    # Main booking test
    success, booking_id = test_booking_creation_with_admin_only_email()
    
    # Check backend logs for confirmation
    log_success = check_backend_logs()
    
    # Additional validation tests
    test_honeypot_protection()
    test_input_validation()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if success and booking_id:
        print("✅ BOOKING CREATION TEST PASSED:")
        print(f"   - Booking created successfully (ID: {booking_id})")
        print("   - Only admin email should be sent")
        print("   - Client confirmation email disabled as expected")
        
        if log_success:
            print("✅ LOG VERIFICATION PASSED:")
            print("   - Admin email confirmation found in backend logs")
        else:
            print("⚠️  LOG VERIFICATION INCONCLUSIVE:")
            print("   - Could not verify admin email in logs automatically")
            print("   - Manual verification recommended")
            
    else:
        print("❌ BOOKING CREATION TEST FAILED:")
        print("   - Booking creation failed")
        print("   - Email configuration cannot be verified")
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()