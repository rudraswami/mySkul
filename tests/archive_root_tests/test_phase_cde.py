#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from backend_test import DhruvAITester
import uuid

def main():
    print("🚀 Starting Phase C, D, E Comprehensive Testing")
    print("=" * 80)
    
    tester = DhruvAITester()
    
    # Authentication first
    print("\n🔐 Authentication Setup:")
    if not tester.test_user_login():
        print("   Login failed, trying registration...")
        if not tester.test_user_registration():
            print("❌ Authentication failed completely. Stopping tests.")
            return
    
    # Phase C: Advanced Guardrails Tests
    print("\n📋 PHASE C: ADVANCED GUARDRAILS TESTS")
    print("-" * 50)
    phase_c_success = tester.test_phase_c_advanced_guardrails_apis()
    
    # Phase D: Enhanced Action Buttons Tests
    print("\n📋 PHASE D: ENHANCED ACTION BUTTONS TESTS")
    print("-" * 50)
    phase_d_success = tester.test_phase_d_enhanced_action_buttons_apis()
    
    # Phase E: Analytics Integration Tests
    print("\n📋 PHASE E: ANALYTICS INTEGRATION TESTS")
    print("-" * 50)
    phase_e_success = tester.test_phase_e_analytics_integration_apis()
    
    # Enhanced Dual Response Integration Tests
    print("\n📋 ENHANCED DUAL RESPONSE INTEGRATION TESTS")
    print("-" * 50)
    dual_response_success = tester.test_enhanced_dual_response_with_guardrails_and_analytics()
    
    # Authentication and Error Handling Tests
    print("\n📋 AUTHENTICATION & ERROR HANDLING TESTS")
    print("-" * 50)
    auth_error_success = tester.test_phase_cde_authentication_and_error_handling()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 PHASE C, D, E COMPREHENSIVE TESTING SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    # Phase-wise results
    print(f"\n📊 PHASE-WISE RESULTS:")
    print(f"Phase C (Advanced Guardrails): {'✅ PASSED' if phase_c_success else '❌ FAILED'}")
    print(f"Phase D (Enhanced Action Buttons): {'✅ PASSED' if phase_d_success else '❌ FAILED'}")
    print(f"Phase E (Analytics Integration): {'✅ PASSED' if phase_e_success else '❌ FAILED'}")
    print(f"Enhanced Dual Response: {'✅ PASSED' if dual_response_success else '❌ FAILED'}")
    print(f"Authentication & Error Handling: {'✅ PASSED' if auth_error_success else '❌ FAILED'}")
    
    # Overall assessment
    phases_passed = sum([phase_c_success, phase_d_success, phase_e_success, dual_response_success, auth_error_success])
    total_phases = 5
    
    if phases_passed == total_phases:
        print("🎉 ALL PHASE C, D, E FEATURES WORKING PERFECTLY!")
    elif phases_passed >= total_phases * 0.8:
        print("✅ MOSTLY SUCCESSFUL! Most Phase C, D, E features working correctly.")
    else:
        print("⚠️  SOME PHASE C, D, E ISSUES DETECTED. Please review failed tests.")
    
    print("=" * 80)
    
    return {
        "phase_c": phase_c_success,
        "phase_d": phase_d_success, 
        "phase_e": phase_e_success,
        "dual_response": dual_response_success,
        "auth_error": auth_error_success,
        "overall_success_rate": tester.tests_passed / tester.tests_run if tester.tests_run > 0 else 0
    }

if __name__ == "__main__":
    results = main()
    print(f"\nFinal Results: {results}")