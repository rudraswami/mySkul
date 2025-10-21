#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_test import DhruvAITester

def main():
    """Run Auto-Note Mentor session saving and retrieval tests"""
    tester = DhruvAITester()
    
    print("🎯 AUTO-NOTE MENTOR SESSION SAVING AND RETRIEVAL TESTING")
    print("   As requested in review: Test session persistence, listing, and retrieval")
    print("="*80)
    
    # First authenticate
    if not tester.test_user_login():
        print("❌ Authentication failed, cannot proceed")
        return False
    
    # Run the specific test
    success = tester.test_auto_note_mentor_session_saving_and_retrieval()
    
    print("\n" + "="*80)
    if success:
        print("✅ AUTO-NOTE MENTOR SESSION TESTING COMPLETED SUCCESSFULLY")
    else:
        print("❌ AUTO-NOTE MENTOR SESSION TESTING FAILED")
    print("="*80)

if __name__ == "__main__":
    main()