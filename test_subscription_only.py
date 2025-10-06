#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_test import DhruvAITester

def main():
    print("🚀 Starting Comprehensive Hybrid Subscription System Testing")
    print("=" * 80)
    
    tester = DhruvAITester()
    
    # Authentication first
    print("\n🔐 AUTHENTICATION SETUP")
    if not tester.test_user_login():
        print("⚠️  Login failed, trying registration...")
        if not tester.test_user_registration():
            print("❌ Both login and registration failed. Stopping tests.")
            return 1
    
    # Run the comprehensive subscription system test
    print("\n🎯 RUNNING COMPREHENSIVE SUBSCRIPTION SYSTEM TEST")
    success = tester.test_subscription_system_comprehensive()
    
    # Print final results
    print("\n" + "=" * 80)
    print("📊 SUBSCRIPTION SYSTEM TEST RESULTS")
    print("=" * 80)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if success:
        print("\n✅ COMPREHENSIVE SUBSCRIPTION SYSTEM TEST PASSED!")
        print("🎉 Hybrid subscription system is working correctly!")
    else:
        print("\n❌ COMPREHENSIVE SUBSCRIPTION SYSTEM TEST FAILED!")
        print("⚠️  Some subscription features need attention.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())