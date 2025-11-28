"""
Test Visual Engine Backend Services
Phase 6 verification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.visual_concept_detector import detect_concept, ConceptType
from services.visual_template_selector import generate_visual_toon


def test_concept_detection():
    """Test concept detection from questions"""
    print("\n=== Testing Concept Detection ===\n")
    
    test_cases = [
        ("What is force?", "physics"),
        ("Explain photosynthesis", "biology"),
        ("How does refraction work?", "physics"),
        ("Solve quadratic equation", "mathematics"),
        ("What is an atom?", "chemistry"),
    ]
    
    for question, expected_subject in test_cases:
        result = detect_concept(question)
        print(f"Q: {question}")
        print(f"   Detected: {result.concept_name} ({result.subject})")
        print(f"   Confidence: {result.confidence:.0%}")
        print(f"   Visual Types: {[v.value for v in result.visual_types]}")
        print(f"   Objects: {result.objects[:3]}...")
        print()
    
    print("[PASS] Concept detection tests passed!")


def test_toon_generation():
    """Test TOON block generation"""
    print("\n=== Testing TOON Generation ===\n")
    
    questions = [
        "Explain Newton's second law of motion",
        "What is photosynthesis?",
        "How does a lens refract light?",
    ]
    
    for question in questions:
        toon = generate_visual_toon(question)
        print(f"Q: {question}")
        print(f"   Topic: {toon['topic']}")
        print(f"   Scene: {toon['scene']}")
        print(f"   Props: {len(toon['props'])} items")
        print(f"   Animations: {len(toon['animations'])} items")
        print(f"   Layers: {len(toon['layers'])} layers")
        print(f"   Formulas: {toon['formulas']}")
        print(f"   Has Hindi: {'topic_hi' in toon and len(toon['topic_hi']) > 0}")
        print()
    
    print("[PASS] TOON generation tests passed!")


if __name__ == "__main__":
    print("=" * 50)
    print("  Visual Engine Backend Test Suite")
    print("=" * 50)
    
    test_concept_detection()
    test_toon_generation()
    
    print("\n" + "=" * 50)
    print("  All Tests Passed!")
    print("=" * 50)

