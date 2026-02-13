#!/usr/bin/env python3
"""
Additional Test: Error Handling Verification
"""
import requests
import json

BACKEND_URL = "https://boring-chaplygin-2.preview.emergentagent.com/api"

def test_validation_errors():
    """Test that validation still works properly"""
    print("=" * 60)
    print("TESTING: Validation Error Handling")
    print("=" * 60)
    
    # Test missing required fields
    invalid_data = {
        "full_name": "",  # Empty required field
        "email": "invalid-email",  # Invalid email format
        "phone": "123",
        "service": "App Development"
        # Missing project_description
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/bookings", 
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        # Should return validation error (400 or 422)
        if response.status_code in [400, 422]:
            print("✅ SUCCESS: Validation errors properly handled")
            return True
        else:
            print(f"❌ UNEXPECTED: Expected 400/422, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_honeypot_protection():
    """Test that honeypot still blocks spam"""
    print("=" * 60)
    print("TESTING: Honeypot Spam Protection")
    print("=" * 60)
    
    # Valid data but with honeypot field filled (spam indicator)
    spam_data = {
        "full_name": "Spam Bot",
        "email": "spam@example.com",
        "phone": "1234567890",
        "service": "App Development",
        "project_description": "This is spam",
        "company_url": "https://spam.com"  # Honeypot field - should trigger rejection
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/bookings", 
            json=spam_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        # Should return 400 for honeypot detection
        if response.status_code == 400 and "Invalid submission" in response.text:
            print("✅ SUCCESS: Honeypot protection working")
            return True
        else:
            print(f"❌ FAILED: Honeypot not working properly")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🛡️ ADDITIONAL SECURITY & VALIDATION TESTS")
    print()
    
    results = []
    results.append(("Validation Errors", test_validation_errors()))
    results.append(("Honeypot Protection", test_honeypot_protection()))
    
    print("\n" + "=" * 60)
    print("ADDITIONAL TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nAdditional Tests: {passed}/{total} passed")