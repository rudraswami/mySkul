#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_test import DhruvAITester

def main():
    """Run subscription flows consistency testing"""
    print("🚀 Starting Subscription Flows Consistency Testing...")
    print("=" * 80)
    
    tester = DhruvAITester()
    
    # Run the specific subscription flows test
    success = tester.test_subscription_flows_consistency()
    
    print("\n" + "=" * 80)
    print("🎯 SUBSCRIPTION FLOWS TESTING COMPLETE")
    
    if success:
        print("✅ ALL SUBSCRIPTION FLOW TESTS PASSED")
        print("   - Backend subscription flows are consistent")
        print("   - All endpoints return proper status codes and payloads")
    else:
        print("❌ SUBSCRIPTION FLOW TESTS FAILED")
        print("   - Critical issues found in subscription flows")
        print("   - Review the detailed output above for specific failures")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)