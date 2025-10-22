#!/usr/bin/env python3
"""
Razorpay Payment Order Creation Testing
Testing the receipt length fix and end-to-end payment order flow
"""

import requests
import json
import jwt
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

class RazorpayPaymentTester:
    def __init__(self):
        self.base_url = "https://tutor-evolution.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.jwt_secret = "dhruv-ai-secure-jwt-secret-key-2025"
        self.test_user_id = "9c4e099e-c2b3-47d6-afec-84dff937c665"
        self.test_email = "razorpay_test@dhruvai.com"
        self.jwt_token = None
        self.test_results = []
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def create_jwt_token(self, user_id: str, email: str) -> str:
        """Create a JWT token for testing"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def check_user_exists(self) -> bool:
        """Check if test user exists in database"""
        self.log(f"Checking if user exists: {self.test_user_id}")
        
        # Try to get user profile with JWT token
        test_token = self.create_jwt_token(self.test_user_id, self.test_email)
        headers = {'Authorization': f'Bearer {test_token}'}
        
        try:
            response = self.session.get(
                f"{self.base_url}/user/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log(f"✅ User exists: {self.test_email}")
                return True
            elif response.status_code == 404:
                self.log(f"⚠️ User not found: {self.test_user_id}")
                return False
            else:
                self.log(f"⚠️ Unexpected response: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Error checking user: {str(e)}", "ERROR")
            return False
    
    def create_test_user(self) -> bool:
        """Create test user in database"""
        self.log(f"Creating test user: {self.test_email}")
        
        # Note: This requires direct database access or admin endpoint
        # For now, we'll assume the user exists or create via API if available
        self.log("⚠️ User creation requires database access - assuming user exists")
        return True
    
    def get_jwt_token(self) -> Optional[str]:
        """Get JWT token for test user"""
        self.log("Generating JWT token for test user")
        
        try:
            token = self.create_jwt_token(self.test_user_id, self.test_email)
            self.jwt_token = token
            self.log(f"✅ JWT token generated: {token[:30]}...")
            return token
        except Exception as e:
            self.log(f"❌ Failed to generate JWT token: {str(e)}", "ERROR")
            return None
    
    def test_payment_order_creation(self, plan_name: str, billing_cycle: str) -> Dict[str, Any]:
        """Test payment order creation for a specific plan"""
        self.log(f"\n{'='*80}")
        self.log(f"Testing: {plan_name} - {billing_cycle}")
        self.log(f"{'='*80}")
        
        if not self.jwt_token:
            self.log("❌ No JWT token available", "ERROR")
            return {
                'success': False,
                'error': 'No JWT token',
                'plan_name': plan_name,
                'billing_cycle': billing_cycle
            }
        
        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'plan_name': plan_name,
            'billing_cycle': billing_cycle
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/subscription/razorpay/create-order",
                json=payload,
                headers=headers,
                timeout=15
            )
            elapsed_time = time.time() - start_time
            
            self.log(f"Response Status: {response.status_code}")
            self.log(f"Response Time: {elapsed_time:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Order created successfully!")
                self.log(f"   Order ID: {data.get('order_id', 'N/A')}")
                self.log(f"   Amount (INR): ₹{data.get('amount_inr', 'N/A')}")
                self.log(f"   Amount (Paise): {data.get('amount', 'N/A')}")
                self.log(f"   Currency: {data.get('currency', 'N/A')}")
                self.log(f"   Key ID: {data.get('key_id', 'N/A')[:20]}...")
                
                # Verify receipt length by checking order_id format
                order_id = data.get('order_id', '')
                self.log(f"   Razorpay Order ID: {order_id}")
                
                # Check if receipt was properly formatted (we can't see it directly, but no error means it worked)
                self.log(f"✅ Receipt validation passed (no length error)")
                
                return {
                    'success': True,
                    'plan_name': plan_name,
                    'billing_cycle': billing_cycle,
                    'order_id': data.get('order_id'),
                    'amount_inr': data.get('amount_inr'),
                    'amount_paise': data.get('amount'),
                    'elapsed_time': elapsed_time,
                    'receipt_valid': True
                }
            else:
                error_data = response.json() if response.text else {}
                error_detail = error_data.get('detail', response.text)
                self.log(f"❌ Order creation failed: {error_detail}", "ERROR")
                
                # Check if it's the receipt length error
                if 'receipt' in str(error_detail).lower() and '40' in str(error_detail):
                    self.log(f"❌ RECEIPT LENGTH ERROR DETECTED!", "ERROR")
                    return {
                        'success': False,
                        'plan_name': plan_name,
                        'billing_cycle': billing_cycle,
                        'error': error_detail,
                        'receipt_error': True
                    }
                
                return {
                    'success': False,
                    'plan_name': plan_name,
                    'billing_cycle': billing_cycle,
                    'error': error_detail,
                    'receipt_error': False
                }
        
        except Exception as e:
            self.log(f"❌ Exception during order creation: {str(e)}", "ERROR")
            return {
                'success': False,
                'plan_name': plan_name,
                'billing_cycle': billing_cycle,
                'error': str(e),
                'exception': True
            }
    
    def test_all_plan_combinations(self):
        """Test all plan and billing cycle combinations"""
        self.log("\n" + "="*80)
        self.log("🧪 TESTING ALL PLAN COMBINATIONS")
        self.log("="*80)
        
        # Test combinations as specified in the review request
        test_cases = [
            ("STARTER", "monthly"),
            ("STARTER", "yearly"),
            ("PRO", "monthly"),
            ("PRO", "yearly"),
        ]
        
        results = []
        for plan_name, billing_cycle in test_cases:
            result = self.test_payment_order_creation(plan_name, billing_cycle)
            results.append(result)
            time.sleep(1)  # Small delay between tests
        
        return results
    
    def check_backend_logs(self):
        """Check backend logs for Razorpay errors"""
        self.log("\n" + "="*80)
        self.log("📋 CHECKING BACKEND LOGS")
        self.log("="*80)
        
        try:
            import subprocess
            
            # Check backend error logs
            self.log("Checking backend error logs...")
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.err.log'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logs = result.stdout
                if 'razorpay' in logs.lower() or 'receipt' in logs.lower():
                    self.log("⚠️ Found Razorpay-related logs:")
                    for line in logs.split('\n'):
                        if 'razorpay' in line.lower() or 'receipt' in line.lower():
                            self.log(f"   {line}")
                else:
                    self.log("✅ No Razorpay errors in recent logs")
            
            # Check backend output logs
            self.log("\nChecking backend output logs...")
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.out.log'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logs = result.stdout
                if 'razorpay' in logs.lower() or 'order created' in logs.lower():
                    self.log("📊 Found Razorpay order creation logs:")
                    for line in logs.split('\n'):
                        if 'razorpay' in line.lower() or 'order' in line.lower():
                            self.log(f"   {line}")
        
        except Exception as e:
            self.log(f"⚠️ Could not check logs: {str(e)}", "WARNING")
    
    def verify_receipt_format(self):
        """Verify the receipt format is correct"""
        self.log("\n" + "="*80)
        self.log("🔍 VERIFYING RECEIPT FORMAT")
        self.log("="*80)
        
        # Simulate the receipt generation logic
        user_id = self.test_user_id
        timestamp = int(datetime.now(timezone.utc).timestamp())
        
        compact_receipt = f"{user_id[:8]}-{timestamp}"
        
        self.log(f"User ID: {user_id}")
        self.log(f"First 8 chars: {user_id[:8]}")
        self.log(f"Timestamp: {timestamp}")
        self.log(f"Generated Receipt: {compact_receipt}")
        self.log(f"Receipt Length: {len(compact_receipt)} characters")
        
        if len(compact_receipt) < 40:
            self.log(f"✅ Receipt length is valid: {len(compact_receipt)} < 40")
            return True
        else:
            self.log(f"❌ Receipt length exceeds limit: {len(compact_receipt)} >= 40", "ERROR")
            return False
    
    def print_final_summary(self, results):
        """Print final test summary"""
        self.log("\n" + "="*80)
        self.log("📊 FINAL TEST SUMMARY - RAZORPAY PAYMENT ORDER CREATION")
        self.log("="*80)
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        receipt_errors = sum(1 for r in results if r.get('receipt_error', False))
        
        self.log(f"\nTotal Tests: {total_tests}")
        self.log(f"Successful: {successful_tests}")
        self.log(f"Failed: {failed_tests}")
        self.log(f"Receipt Errors: {receipt_errors}")
        
        self.log("\n" + "-"*80)
        self.log("DETAILED RESULTS:")
        self.log("-"*80)
        
        for result in results:
            plan = result.get('plan_name', 'N/A')
            cycle = result.get('billing_cycle', 'N/A')
            success = result.get('success', False)
            
            status = "✅ PASS" if success else "❌ FAIL"
            self.log(f"\n{status} - {plan} ({cycle})")
            
            if success:
                self.log(f"   Order ID: {result.get('order_id', 'N/A')}")
                self.log(f"   Amount: ₹{result.get('amount_inr', 'N/A')}")
                self.log(f"   Time: {result.get('elapsed_time', 0):.2f}s")
            else:
                self.log(f"   Error: {result.get('error', 'Unknown error')}")
                if result.get('receipt_error'):
                    self.log(f"   ⚠️ RECEIPT LENGTH ERROR DETECTED!")
        
        self.log("\n" + "="*80)
        
        if successful_tests == total_tests:
            self.log("✅ ALL TESTS PASSED - Payment order creation working correctly!")
            self.log("✅ Receipt length fix is working as expected")
        elif receipt_errors > 0:
            self.log("❌ RECEIPT LENGTH ERRORS DETECTED - Fix not working!")
        else:
            self.log(f"⚠️ {failed_tests} test(s) failed - Check errors above")
        
        self.log("="*80)
    
    def run_all_tests(self):
        """Run all Razorpay payment tests"""
        self.log("\n" + "="*80)
        self.log("🚀 RAZORPAY PAYMENT ORDER CREATION - END-TO-END TESTING")
        self.log("="*80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test User ID: {self.test_user_id}")
        self.log(f"Test Email: {self.test_email}")
        self.log(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Verify receipt format
        self.verify_receipt_format()
        
        # Step 2: Check if user exists
        user_exists = self.check_user_exists()
        
        # Step 3: Create user if needed (or assume exists)
        if not user_exists:
            self.log("\n⚠️ User does not exist - creating test user...")
            self.create_test_user()
        
        # Step 4: Get JWT token
        self.log("\n" + "="*80)
        self.log("🔑 GETTING JWT TOKEN")
        self.log("="*80)
        token = self.get_jwt_token()
        
        if not token:
            self.log("❌ Cannot proceed without JWT token", "ERROR")
            return
        
        # Step 5: Test all plan combinations
        results = self.test_all_plan_combinations()
        
        # Step 6: Check backend logs
        self.check_backend_logs()
        
        # Step 7: Print final summary
        self.print_final_summary(results)
        
        self.log(f"\nTest End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results


if __name__ == "__main__":
    tester = RazorpayPaymentTester()
    results = tester.run_all_tests()
