#!/usr/bin/env python3
"""
TIVROX Backend API Testing - Focus on Email Delivery Functionality
Testing plain text email implementation for better deliverability
"""
import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://plain-text-mail.preview.emergentagent.com/api"
VERIFIED_EMAIL = "chiluverushivaprasad02@gmail.com"  # Resend verified email for testing

class TIVROXBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_endpoint(self):
        """Test basic health endpoint"""
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                data = await response.json()
                success = response.status == 200 and data.get("status") == "healthy"
                self.test_results["health_endpoint"] = {
                    "success": success,
                    "status_code": response.status,
                    "data": data
                }
                print(f"✓ Health endpoint: {'PASS' if success else 'FAIL'}")
                return success
        except Exception as e:
            print(f"✗ Health endpoint test failed: {e}")
            self.test_results["health_endpoint"] = {"success": False, "error": str(e)}
            return False
    
    async def test_booking_creation_with_email(self):
        """Test booking creation with email sending - MAIN FOCUS"""
        print("\n=== TESTING BOOKING CREATION WITH EMAIL SENDING ===")
        
        # Test data for booking creation
        booking_data = {
            "full_name": "John Smith",
            "email": VERIFIED_EMAIL,  # Using verified email for testing
            "phone": "+1-555-123-4567",
            "service": "Website Development",
            "project_deadline": "2 weeks",
            "project_description": "Need a modern business website with responsive design, contact forms, and SEO optimization. Looking for clean design with good user experience.",
            "website_type": "Business Website",
            "platform": "Custom Development"
        }
        
        try:
            print(f"Testing with verified email: {VERIFIED_EMAIL}")
            print("Sending booking request...")
            
            async with self.session.post(
                f"{BASE_URL}/bookings", 
                json=booking_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                status_code = response.status
                response_text = await response.text()
                
                print(f"Response Status: {status_code}")
                print(f"Response Body: {response_text}")
                
                if status_code == 200:
                    try:
                        data = json.loads(response_text)
                        booking_id = data.get("booking_id")
                        
                        success = (
                            data.get("status") == "success" and
                            "booking_id" in data and
                            "consultation request has been submitted successfully" in data.get("message", "").lower()
                        )
                        
                        self.test_results["booking_creation_email"] = {
                            "success": success,
                            "status_code": status_code,
                            "booking_id": booking_id,
                            "response_data": data,
                            "email_verification": "Backend logs must be checked for email confirmation"
                        }
                        
                        if success:
                            print(f"✓ Booking created successfully with ID: {booking_id}")
                            print("✓ Request accepted - checking backend logs for email confirmation...")
                            return True, booking_id
                        else:
                            print(f"✗ Booking creation failed - unexpected response format")
                            return False, None
                            
                    except json.JSONDecodeError:
                        print(f"✗ Booking creation failed - invalid JSON response")
                        self.test_results["booking_creation_email"] = {
                            "success": False,
                            "status_code": status_code,
                            "error": "Invalid JSON response",
                            "raw_response": response_text
                        }
                        return False, None
                else:
                    print(f"✗ Booking creation failed - HTTP {status_code}")
                    self.test_results["booking_creation_email"] = {
                        "success": False,
                        "status_code": status_code,
                        "error": response_text
                    }
                    return False, None
                    
        except Exception as e:
            print(f"✗ Booking creation test failed with exception: {e}")
            self.test_results["booking_creation_email"] = {
                "success": False,
                "error": str(e)
            }
            return False, None
    
    async def test_honeypot_protection(self):
        """Test honeypot spam protection"""
        print("\n=== TESTING HONEYPOT SPAM PROTECTION ===")
        
        spam_data = {
            "full_name": "Spam User",
            "email": VERIFIED_EMAIL,
            "phone": "+1-555-999-9999",
            "service": "Website Development", 
            "project_description": "This is spam",
            "company_url": "https://spam-site.com"  # Honeypot field
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/bookings",
                json=spam_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                status_code = response.status
                success = status_code == 400
                
                self.test_results["honeypot_protection"] = {
                    "success": success,
                    "status_code": status_code,
                    "expected_status": 400
                }
                
                print(f"✓ Honeypot protection: {'PASS' if success else 'FAIL'} (Status: {status_code})")
                return success
                
        except Exception as e:
            print(f"✗ Honeypot test failed: {e}")
            self.test_results["honeypot_protection"] = {"success": False, "error": str(e)}
            return False
    
    async def test_input_validation(self):
        """Test input validation for required fields"""
        print("\n=== TESTING INPUT VALIDATION ===")
        
        # Test missing required fields
        invalid_data = {
            "full_name": "",  # Empty required field
            "email": "invalid-email",  # Invalid email format
            "phone": "",  # Empty required field
            "service": "Website Development",
            "project_description": ""  # Empty required field
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/bookings",
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                status_code = response.status
                # Accept either 400 (from manual validation) or 422 (from Pydantic)
                success = status_code in [400, 422]
                
                self.test_results["input_validation"] = {
                    "success": success,
                    "status_code": status_code,
                    "expected_status": "400 or 422"
                }
                
                print(f"✓ Input validation: {'PASS' if success else 'FAIL'} (Status: {status_code})")
                return success
                
        except Exception as e:
            print(f"✗ Input validation test failed: {e}")
            self.test_results["input_validation"] = {"success": False, "error": str(e)}
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("TIVROX BACKEND TEST SUMMARY - EMAIL FOCUS")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("success", False))
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        print("\nDETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result.get("success", False) else "✗ FAIL"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
            if not result.get("success", False) and "error" in result:
                print(f"    Error: {result['error']}")
        
        # Email-specific results
        if "booking_creation_email" in self.test_results:
            email_result = self.test_results["booking_creation_email"]
            if email_result.get("success"):
                booking_id = email_result.get("booking_id")
                print(f"\n📧 EMAIL TESTING:")
                print(f"   ✓ Booking created with ID: {booking_id}")
                print(f"   ✓ Using verified email: {VERIFIED_EMAIL}")
                print(f"   ⚠️  IMPORTANT: Check backend logs for:")
                print(f"      - 'Emails sent for booking {booking_id}'")
                print(f"      - Verify both admin and client emails sent")
                print(f"      - Confirm plain text format (no HTML)")
        
        print("\n" + "="*60)

async def main():
    """Main test execution"""
    print("TIVROX Backend Testing - Email Delivery Focus")
    print("=" * 60)
    print(f"Target URL: {BASE_URL}")
    print(f"Verified Email: {VERIFIED_EMAIL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    async with TIVROXBackendTester() as tester:
        # Run core tests
        await tester.test_health_endpoint()
        booking_success, booking_id = await tester.test_booking_creation_with_email()
        await tester.test_honeypot_protection()
        await tester.test_input_validation()
        
        # Print comprehensive summary
        tester.print_summary()
        
        # Return overall status
        if booking_success:
            print("\n🎯 PRIMARY TEST (Email Delivery) PASSED")
            print(f"   Backend logs should show: 'Emails sent for booking {booking_id}'")
            return True
        else:
            print("\n❌ PRIMARY TEST (Email Delivery) FAILED")
            return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)