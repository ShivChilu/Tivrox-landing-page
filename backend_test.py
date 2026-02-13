#!/usr/bin/env python3
"""
TIVROX Backend Test Suite - Review Request Testing
Testing TIVROX booking system with Resend email integration
"""
import requests
import json
import sys
from datetime import datetime
import os

# Test configuration
BACKEND_URL = "https://honeypot-fix.preview.emergentagent.com/api"

def test_booking_submission_review_request():
    """
    Test POST /api/bookings with exact data from review request:
    - full_name: "Test User"
    - email: "testuser@example.com" 
    - phone: "1234567890"
    - service: "Website Development"
    - project_description: "Need a new website for my business"
    - project_deadline: "2026-03-15"
    """
    print("=" * 70)
    print("TESTING: POST /api/bookings - Review Request Test Data")
    print("=" * 70)
    
    # Exact test data from review request
    booking_data = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "phone": "1234567890",
        "service": "Website Development",
        "project_description": "Need a new website for my business",
        "project_deadline": "2026-03-15"
    }
    
    print(f"📝 Test Data (from review request):")
    for key, value in booking_data.items():
        print(f"   {key}: {value}")
    print()
    
    try:
        # Make the POST request
        print("🚀 Sending POST request to /api/bookings...")
        response = requests.post(
            f"{BACKEND_URL}/bookings", 
            json=booking_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        # Parse response
        try:
            response_json = response.json()
            print(f"📊 Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
            return False
        
        # Verify expected results from review request
        success_checks = []
        
        # 1. Status should be "success"
        if response.status_code == 200:
            success_checks.append(("✅", "Status code 200 received"))
        else:
            success_checks.append(("❌", f"Expected status 200, got {response.status_code}"))
            return False
            
        # 2. Response should include status: "success"
        if response_json.get("status") == "success":
            success_checks.append(("✅", "Status 'success' found in response"))
        else:
            success_checks.append(("❌", f"Expected status 'success', got '{response_json.get('status')}'"))
            
        # 3. booking_id should be returned
        booking_id = response_json.get("booking_id")
        if booking_id:
            success_checks.append(("✅", f"Booking ID received: {booking_id}"))
        else:
            success_checks.append(("❌", "No booking_id in response"))
            
        # 4. Message about successful submission
        message = response_json.get("message", "")
        if "successful" in message.lower() or "success" in message.lower():
            success_checks.append(("✅", f"Success message found: '{message}'"))
        else:
            success_checks.append(("❌", f"No success message found, got: '{message}'"))
        
        # Print all checks
        print("\n📋 VERIFICATION CHECKS:")
        for status, message in success_checks:
            print(f"  {status} {message}")
            
        # Return True only if all checks passed
        failed_checks = [check for check in success_checks if check[0] == "❌"]
        if failed_checks:
            print(f"\n❌ FAILED: {len(failed_checks)} verification(s) failed")
            return False
        else:
            print(f"\n✅ SUCCESS: All {len(success_checks)} verifications passed")
            return True
            
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Connection error - backend may be down")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_honeypot_protection():
    """
    Test honeypot protection with company_url="spam"
    Should return 400 status and be blocked
    """
    print("=" * 70)
    print("TESTING: Honeypot Protection - Should Block Spam")
    print("=" * 70)
    
    # Test data with honeypot triggered
    spam_data = {
        "full_name": "Spam User",
        "email": "spam@example.com", 
        "phone": "1234567890",
        "service": "Website Development",
        "project_description": "This is spam",
        "project_deadline": "2026-03-15",
        "company_url": "spam"  # This should trigger honeypot
    }
    
    print(f"📝 Spam Test Data (company_url='spam'):")
    for key, value in spam_data.items():
        print(f"   {key}: {value}")
    print()
    
    try:
        print("🚀 Sending POST request with honeypot trigger...")
        response = requests.post(
            f"{BACKEND_URL}/bookings",
            json=spam_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📊 Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
        
        # Verify honeypot blocked the request
        if response.status_code == 400:
            print("✅ SUCCESS: Honeypot protection working - blocked with 400 status")
            return True
        else:
            print(f"❌ FAILED: Expected 400 status for honeypot, got {response.status_code}")
            print("❌ Honeypot protection may not be working properly")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_health_endpoint():
    """Test basic health endpoint"""
    print("=" * 70)
    print("TESTING: GET /api/health - Backend Health Check")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📊 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Health endpoint working")
            return True
        else:
            print("❌ FAILED: Health endpoint not working")
            return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_root_endpoint():
    """Test root API endpoint"""
    print("=" * 70) 
    print("TESTING: GET /api/ - Root API Endpoint")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📊 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Root endpoint working")
            return True
        else:
            print("❌ FAILED: Root endpoint not working")
            return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 TIVROX BACKEND TESTING - REVIEW REQUEST")
    print("🔍 Testing Resend email integration and booking system")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"⏰ Test time: {datetime.now().isoformat()}")
    print()
    
    results = []
    
    # Test health first to ensure backend is up
    results.append(("Health Check", test_health_endpoint()))
    
    # Test root API
    results.append(("Root API", test_root_endpoint()))
    
    # Main tests from review request
    results.append(("Booking Submission (Review Data)", test_booking_submission_review_request()))
    results.append(("Honeypot Protection", test_honeypot_protection()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests Passed: {passed}/{total}")
    
    # Additional notes for manual verification
    print("\n" + "=" * 70)
    print("MANUAL VERIFICATION REQUIRED:")
    print("=" * 70)
    print("📧 Check backend logs for email confirmation messages:")
    print("   - '✉️ Admin notification email sent'")
    print("   - '✉️ Client confirmation email sent'") 
    print("   - '📧 Both emails sent successfully'")
    print("   - Admin email: chiluverushivaprasad02@gmail.com")
    print("   - Client email: testuser@example.com")
    print()
    print("🗄️  Check MongoDB for booking storage verification")
    print("   - Booking should be saved with generated booking_id")
    print()
    
    if passed == total:
        print("🎉 ALL AUTOMATED TESTS PASSED!")
        print("⚠️  Please verify backend logs and MongoDB as noted above")
    else:
        print("⚠️ SOME TESTS FAILED!")
        
    print(f"\nExiting with code: {0 if passed == total else 1}")
    sys.exit(0 if passed == total else 1)