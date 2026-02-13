#!/usr/bin/env python3
"""
TIVROX Backend API Testing Suite
Focus: Email delivery functionality and booking creation
"""

import requests
import json
import sys
import time
from typing import Dict, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://plain-text-mail.preview.emergentagent.com/api"

class TivroxAPITester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        
        self.results.append(result)
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(result)

    def test_health_endpoint(self):
        """Test GET /api/health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Health Check", True, "API is healthy")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_result("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
        return False

    def test_root_endpoint(self):
        """Test GET /api/ endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "TIVROX API is running" in data.get("message", ""):
                    self.log_result("Root Endpoint", True, "API root responding correctly")
                    return True
                else:
                    self.log_result("Root Endpoint", False, f"Unexpected message: {data}")
            else:
                self.log_result("Root Endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Root Endpoint", False, f"Exception: {str(e)}")
        return False

    def test_valid_booking_creation(self):
        """Test POST /api/bookings with valid data and email sending"""
        booking_data = {
            "full_name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1234567890",
            "service": "Website Development",
            "project_deadline": "2 weeks",
            "project_description": "Need a business website with contact form and online payment integration",
            "website_type": "Business"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/bookings",
                json=booking_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("status") == "success" and 
                    "booking_id" in data and 
                    "consultation request has been submitted successfully" in data.get("message", "")):
                    self.log_result("Valid Booking Creation", True, f"Booking ID: {data['booking_id']}")
                    return data["booking_id"]
                else:
                    self.log_result("Valid Booking Creation", False, f"Unexpected response structure: {data}")
            else:
                self.log_result("Valid Booking Creation", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Valid Booking Creation", False, f"Exception: {str(e)}")
        return None

    def test_missing_required_fields(self):
        """Test POST /api/bookings with missing required fields"""
        invalid_data = {
            "full_name": "John Smith",
            "email": "john.smith@example.com",
            # Missing phone and project_description
            "service": "Website Development"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/bookings",
                json=invalid_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_result("Missing Required Fields Validation", True, "Correctly rejected missing fields")
                return True
            else:
                self.log_result("Missing Required Fields Validation", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Missing Required Fields Validation", False, f"Exception: {str(e)}")
        return False

    def test_invalid_email_format(self):
        """Test POST /api/bookings with invalid email format"""
        invalid_email_data = {
            "full_name": "John Smith",
            "email": "invalid-email-format",
            "phone": "+1234567890",
            "service": "Website Development",
            "project_description": "Test project description"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/bookings",
                json=invalid_email_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_result("Invalid Email Format Validation", True, "Correctly rejected invalid email")
                return True
            else:
                self.log_result("Invalid Email Format Validation", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Email Format Validation", False, f"Exception: {str(e)}")
        return False

    def test_honeypot_detection(self):
        """Test POST /api/bookings with honeypot field filled (should be rejected)"""
        honeypot_data = {
            "full_name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1234567890",
            "service": "Website Development",
            "project_description": "Test project description",
            "company_url": "http://spam.com"  # Honeypot field
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/bookings",
                json=honeypot_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_result("Honeypot Detection", True, "Correctly detected spam submission")
                return True
            else:
                self.log_result("Honeypot Detection", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Honeypot Detection", False, f"Exception: {str(e)}")
        return False

    def test_service_options(self):
        """Test POST /api/bookings with different service options"""
        services = ["Website Development", "Video Editing", "Graphic Design"]
        
        for service in services:
            booking_data = {
                "full_name": f"Test User for {service}",
                "email": f"test.{service.lower().replace(' ', '.')}@example.com",
                "phone": "+1234567890",
                "service": service,
                "project_description": f"Test project for {service} service"
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/bookings",
                    json=booking_data,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        self.log_result(f"Service: {service}", True, "Service accepted")
                    else:
                        self.log_result(f"Service: {service}", False, f"Unexpected response: {data}")
                else:
                    self.log_result(f"Service: {service}", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_result(f"Service: {service}", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all test cases"""
        print("=" * 60)
        print("TIVROX Backend API Testing Suite")
        print("Focus: Email delivery functionality and booking creation")
        print("=" * 60)
        print()
        
        # Basic endpoint tests
        print("📋 Basic Endpoint Tests:")
        self.test_health_endpoint()
        self.test_root_endpoint()
        print()
        
        # Booking creation tests
        print("📝 Booking Creation Tests:")
        booking_id = self.test_valid_booking_creation()
        if booking_id:
            print(f"   📧 Email sending should be logged for booking: {booking_id}")
        print()
        
        # Validation tests
        print("🛡️ Validation Tests:")
        self.test_missing_required_fields()
        self.test_invalid_email_format()
        self.test_honeypot_detection()
        print()
        
        # Service option tests
        print("🔧 Service Option Tests:")
        self.test_service_options()
        print()
        
        # Summary
        print("=" * 60)
        print(f"TEST SUMMARY:")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total: {self.passed + self.failed}")
        print("=" * 60)
        
        if self.failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if "❌ FAIL" in result:
                    print(f"   {result}")
        
        print("\n📧 EMAIL VERIFICATION NOTE:")
        print("   - Check backend logs for 'Emails sent for booking {booking_id}' messages")
        print("   - This confirms successful email API calls to Resend")
        print("   - Actual email delivery should be verified separately")
        
        return self.failed == 0

def main():
    """Main test execution"""
    tester = TivroxAPITester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()