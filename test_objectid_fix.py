#!/usr/bin/env python3
"""
ObjectId Serialization Fix Test Runner
CRITICAL VALIDATION: Test the ObjectId serialization fix for 402 Payment Required errors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_test import DhruvAITester

def main():
    """Run ObjectId serialization fix validation"""
    print("🚨 CRITICAL VALIDATION: OBJECTID SERIALIZATION FIX FOR 402 PAYMENT REQUIRED ERRORS")
    print("="*80)
    
    tester = DhruvAITester()
    
    # Run the ObjectId serialization fix test
    success = tester.test_objectid_serialization_402_fix()
    
    print("\n" + "="*80)
    print("OBJECTID SERIALIZATION FIX VALIDATION RESULTS")
    print("="*80)
    
    if success:
        print("✅ OBJECTID SERIALIZATION FIX VALIDATION: SUCCESS")
        print("   ✅ 402 status codes returned correctly (not 500)")
        print("   ✅ Response structures are properly JSON serialized")
        print("   ✅ No ObjectId serialization errors detected")
        print("   ✅ upsell_info structures are ObjectId-free")
        sys.exit(0)
    else:
        print("❌ OBJECTID SERIALIZATION FIX VALIDATION: FAILED")
        print("   🚨 Critical issues detected in ObjectId serialization")
        print("   🔧 Backend fix may not be working correctly")
        sys.exit(1)

if __name__ == "__main__":
    main()