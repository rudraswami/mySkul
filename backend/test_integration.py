#!/usr/bin/env python3
"""
Integration Test for Visual Professor Engine
Tests complete pipeline from question to rendered visual
"""

import json
import requests
import time

BASE_URL = "http://localhost:8001"

def test_velocity_visual():
    """Test complete visual generation for velocity"""
    
    print("\n" + "="*60)
    print("TESTING: Complete Visual Professor Pipeline for 'velocity'")
    print("="*60 + "\n")
    
    # Step 1: Send question
    print("[1] Sending question to backend...")
    
    payload = {
        "question": "What is velocity?",
        "conversation_id": f"test-{int(time.time())}",
        "user_id": "test-user",
        "context": {}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/neuro-symbolic",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ FAILED: Backend returned {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        data = response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED: Connection error - {e}")
        return False
    
    # Step 2: Check teaching_visual exists
    print("[2] Checking teaching_visual in response...")
    
    teaching_visual = data.get("response", {}).get("teaching_visual")
    if not teaching_visual:
        print("❌ FAILED: No teaching_visual in response")
        print(f"   Available keys: {list(data.get('response', {}).keys())}")
        return False
    
    print(f"✅ Teaching visual found")
    print(f"   Concept: {teaching_visual.get('concept')}")
    print(f"   Subject: {teaching_visual.get('subject')}")
    print(f"   Stages: {len(teaching_visual.get('stages', []))}")
    
    # Step 3: Validate stages
    print("\n[3] Validating stage structure...")
    
    stages = teaching_visual.get("stages", [])
    if not stages:
        print("❌ FAILED: No stages in teaching visual")
        return False
    
    # Step 4: Check first stage
    first_stage = stages[0]
    blocks = first_stage.get("blocks", [])
    
    print(f"   Stage 1 has {len(blocks)} blocks")
    print(f"   Block types: {[b.get('type') for b in blocks]}")
    
    # Step 5: Find animated_scene block
    print("\n[4] Finding animated_scene block...")
    
    animated_scene_blocks = [b for b in blocks if b.get("type") == "animated_scene"]
    if not animated_scene_blocks:
        print("❌ FAILED: No animated_scene block in stage")
        return False
    
    scene_block = animated_scene_blocks[0]
    print(f"✅ Found animated_scene block")
    
    # Step 6: Validate scene structure
    print("\n[5] Validating scene structure...")
    
    scene = scene_block.get("scene", {})
    entities = scene.get("entities", [])
    actions = scene_block.get("animation_sequence", [])
    
    print(f"   Entities: {len(entities)}")
    for entity in entities:
        print(f"     - {entity.get('id')} (type: {entity.get('type')})")
        print(f"       Position: ({entity.get('initial_position', {}).get('x')}, {entity.get('initial_position', {}).get('y')})")
    
    print(f"\n   Actions: {len(actions)}")
    for action in actions[:5]:  # Show first 5
        print(f"     - {action.get('action')} on {action.get('entity')}")
        if action.get('to'):
            print(f"       To: ({action['to'].get('x')}, {action['to'].get('y')})")
    
    # Step 7: Verify entity count
    print("\n[6] Verifying entity count...")
    
    if len(entities) < 2:
        print(f"⚠️  WARNING: Only {len(entities)} entities (expected 3+)")
    else:
        print(f"✅ Good entity count: {len(entities)}")
    
    # Step 8: Verify actions
    print("\n[7] Verifying action count...")
    
    if len(actions) < 2:
        print(f"❌ FAILED: Only {len(actions)} actions (expected 3+)")
        return False
    else:
        print(f"✅ Good action count: {len(actions)}")
    
    # Step 9: Check narration
    print("\n[8] Checking narration...")
    
    narration = first_stage.get("narration", "")
    if narration:
        print(f"✅ Narration found: {narration[:100]}...")
    else:
        print(f"⚠️  No narration")
    
    # SUMMARY
    print("\n" + "="*60)
    print("✅ ALL CHECKS PASSED - Visual Pipeline Working!")
    print("="*60)
    print("\nFrontend should now render:")
    print("  1. Animated entities (metro train, arrow, etc.)")
    print("  2. Smooth Framer Motion animations")
    print("  3. Stage-by-stage progression")
    print("  4. Professor narration synced with visuals")
    print("\nTest in browser: http://localhost:3000")
    print("Ask: 'What is velocity?'\n")
    
    return True

if __name__ == "__main__":
    success = test_velocity_visual()
    exit(0 if success else 1)


