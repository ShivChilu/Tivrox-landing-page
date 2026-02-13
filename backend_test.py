#!/usr/bin/env python3
"""
TIVROX Backend Test Suite
Testing booking form submission after dependency fixes
"""
import requests
import json
import sys
from datetime import datetime
import os

# Test configuration
BACKEND_URL = "https://form-submit-debug.preview.emergentagent.com/api"

def test_booking_submission():
    """
    Test POST /api/bookings with valid data as specified in review request
    """
    print("=" * 60)
    print("TESTING: POST /api/bookings - Booking Form Submission")
    print("=" * 60)
    
    # Test data matching the review request requirements
    booking_data = {
        "full_name": "Test Client",
        "email": "testclient@example.com",
        "phone": "7986955634",
        "service": "App Development",
        "platform": "Android",
        "project_deadline": "2026-02-28",
        "project_description": "Testing form submission after dependency fixes"
    }
    
    print(f"📝 Test Data:")
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
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        # Parse response
        try:
            response_json = response.json()
            print(f"📊 Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
        
        # Verify expected results
        if response.status_code == 200:
            print("\n✅ SUCCESS: Status code 200 received")
            
            if "booking_id" in response_json:
                booking_id = response_json["booking_id"]
                print(f"✅ SUCCESS: Booking ID received: {booking_id}")
            else:
                print("❌ ISSUE: No booking_id in response")
                
            if "success" in response_json.get("status", "").lower():
                print("✅ SUCCESS: Success status message received")
            else:
                print("❌ ISSUE: No success status message")
                
        else:
            print(f"\n❌ FAILED: Expected status 200, got {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Connection error")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False
    
    return True

def test_health_endpoint():
    """Test basic health endpoint to verify backend is responsive"""
    print("=" * 60)
    print("TESTING: GET /api/health - Backend Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Response: {response.json()}")
        
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
    print("=" * 60) 
    print("TESTING: GET /api/ - Root API Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Response: {response.json()}")
        
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
    print(f"🎯 TIVROX BACKEND TESTING")
    print(f"🌐 Testing against: {BACKEND_URL}")
    print(f"⏰ Test time: {datetime.now().isoformat()}")
    print()
    
    results = []
    
    # Test health first
    results.append(("Health Check", test_health_endpoint()))
    
    # Test root API
    results.append(("Root API", test_root_endpoint()))
    
    # Test booking submission (main focus)
    results.append(("Booking Submission", test_booking_submission()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("⚠️ SOME TESTS FAILED!")
        sys.exit(1)