"""
Unit tests for Neuro-Symbolic AI Tutor
10 test fixtures covering different subjects and scenarios
"""
import pytest
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, '/app/backend')

from prompts.neuro_symbolic_tutor import (
    get_neuro_symbolic_prompt,
    detect_student_emotion,
    generate_ncert_mapping
)
from utils.neuro_symbolic_parser import NeuroSymbolicParser


class TestEmotionDetection:
    """Test emotion detection from student messages"""
    
    def test_detect_confused(self):
        """Test detection of confusion"""
        message = "I don't understand how photosynthesis works"
        emotion = detect_student_emotion(message)
        assert emotion == "confused"
    
    def test_detect_stressed(self):
        """Test detection of stress"""
        message = "I'm so worried about tomorrow's exam, I can't do this"
        emotion = detect_student_emotion(message)
        assert emotion == "stressed"
    
    def test_detect_curious(self):
        """Test detection of curiosity"""
        message = "Why does the moon change shape? I want to know more"
        emotion = detect_student_emotion(message)
        assert emotion == "curious"
    
    def test_detect_excited(self):
        """Test detection of excitement"""
        message = "That was awesome! It makes sense now!"
        emotion = detect_student_emotion(message)
        assert emotion == "excited"
    
    def test_detect_low_confidence(self):
        """Test detection of low confidence"""
        message = "I'm bad at physics, I never understand these problems"
        emotion = detect_student_emotion(message)
        assert emotion == "low_confidence"
    
    def test_detect_neutral(self):
        """Test detection of neutral emotion"""
        message = "Explain Newton's third law"
        emotion = detect_student_emotion(message)
        assert emotion == "neutral"


class TestNCERTMapping:
    """Test NCERT mapping generation"""
    
    def test_jee_mapping(self):
        """Test NCERT mapping for JEE"""
        mapping = generate_ncert_mapping("Physics", "Mechanics", "JEE")
        assert mapping['source_type'] == "NCERT"
        assert mapping['class_range'] == "11-12"
        assert mapping['subject'] == "Physics"
    
    def test_neet_mapping(self):
        """Test NCERT mapping for NEET"""
        mapping = generate_ncert_mapping("Biology", "Cell Biology", "NEET")
        assert mapping['source_type'] == "NCERT"
        assert mapping['class_range'] == "11-12"
        assert mapping['subject'] == "Biology"
    
    def test_upsc_mapping(self):
        """Test NCERT mapping for UPSC"""
        mapping = generate_ncert_mapping("History", "Ancient India", "UPSC")
        assert mapping['source_type'] == "NCERT"
        assert "varies" in mapping['class_range'].lower()


class TestPromptGeneration:
    """Test system prompt generation"""
    
    def test_prompt_includes_sections(self):
        """Test that prompt includes all 8 sections"""
        prompt = get_neuro_symbolic_prompt("Physics", "What is force?", "JEE", "neutral")
        
        # Check all section markers are present
        assert "[SECTION:PRACTICAL_EXPLANATION]" in prompt
        assert "[SECTION:INDIAN_EXAMPLE]" in prompt
        assert "[SECTION:METAPHOR]" in prompt
        assert "[SECTION:VISUAL_SCHEMA]" in prompt
        assert "[SECTION:PROFESSOR_VERIFICATION]" in prompt
        assert "[SECTION:MINI_PRACTICE]" in prompt
        assert "[SECTION:ENCOURAGEMENT]" in prompt
        assert "[SECTION:ASK]" in prompt
    
    def test_prompt_includes_emotion(self):
        """Test that prompt includes emotion awareness"""
        prompt = get_neuro_symbolic_prompt("Mathematics", "Explain calculus", "JEE", "confused")
        assert "confused" in prompt
        assert "Simplify first" in prompt or "Break into small steps" in prompt
    
    def test_prompt_karnataka_context(self):
        """Test that prompt mentions Karnataka/Bengaluru context"""
        prompt = get_neuro_symbolic_prompt("Chemistry", "Explain pH", "NEET", "neutral")
        assert "Karnataka" in prompt or "Bengaluru" in prompt or "BMTC" in prompt or "metro" in prompt


class TestResponseParsing:
    """Test parsing of AI responses"""
    
    def test_parse_practical_explanation(self):
        """Test parsing of practical explanation section"""
        response_text = """
        [SECTION:PRACTICAL_EXPLANATION]
        **👋 Practical Explanation**
        
        Okay, so basically force is a push or pull that makes things move or stop.
        Like when you push your cycle pedal, that's force.
        The harder you push, the faster it goes.
        [/SECTION:PRACTICAL_EXPLANATION]
        """
        
        explanation = NeuroSymbolicParser.extract_section(response_text, 'PRACTICAL_EXPLANATION')
        assert explanation is not None
        assert "force" in explanation.lower()
        assert len(explanation) > 0
    
    def test_parse_visual_schema(self):
        """Test parsing of visual schema JSON"""
        response_text = """
        [SECTION:VISUAL_SCHEMA]
        **🧠 Visual Schema**
        
        {
          "diagram_type": "flow",
          "title": "Force Concept",
          "nodes": [
            {"id": "n1", "label": "Force Applied", "type": "main"},
            {"id": "n2", "label": "Object Moves", "type": "result"}
          ],
          "edges": [
            {"from": "n1", "to": "n2", "label": "causes"}
          ],
          "caption": "Force causes motion"
        }
        [/SECTION:VISUAL_SCHEMA]
        """
        
        schema = NeuroSymbolicParser.parse_visual_schema(response_text)
        assert schema is not None
        assert schema['diagram_type'] == 'flow'
        assert len(schema['nodes']) == 2
        assert len(schema['edges']) == 1
    
    def test_parse_professor_verification(self):
        """Test parsing of professor verification section"""
        response_text = """
        [SECTION:PROFESSOR_VERIFICATION]
        **✅ Professor Verification**
        
        **Steps to prove logic:**
        1. Force is defined as F = ma (Newton's second law)
        2. Mass and acceleration are measured quantities
        3. Therefore force is quantifiable
        4. Experimental verification confirms this relationship
        
        **Source:**
        NCERT Class 11 Physics Chapter 5 - Laws of Motion
        
        **Confidence Score:** 0.95
        [/SECTION:PROFESSOR_VERIFICATION]
        """
        
        verification = NeuroSymbolicParser.parse_professor_verification(response_text)
        assert verification is not None
        assert len(verification['steps']) > 0
        assert 0.0 <= verification['confidence'] <= 1.0  # Just check valid range
        assert verification['confidence'] >= 0.7  # Reasonable confidence
        assert "NCERT" in verification['source']
    
    def test_parse_mini_practice(self):
        """Test parsing of mini practice section"""
        response_text = """
        [SECTION:MINI_PRACTICE]
        **🎯 Mini Practice**
        
        **Question:** If a 2kg object accelerates at 3 m/s², what force is applied?
        
        **Options:**
        A) 5 N
        B) 6 N
        C) 7 N
        D) 8 N
        
        **Hint:** Use F = ma formula
        [/SECTION:MINI_PRACTICE]
        """
        
        practice = NeuroSymbolicParser.parse_mini_practice(response_text)
        assert practice is not None
        assert "2kg" in practice['question']
        assert practice['options'] is not None and len(practice['options']) > 0  # Check options exist and not empty
        assert len(practice['options']) == 4
        assert "F = ma" in practice['hint']
    
    def test_parse_full_response(self):
        """Test parsing of complete response"""
        response_text = """
        [SECTION:PRACTICAL_EXPLANATION]
        Force is a push or pull that changes motion.
        [/SECTION:PRACTICAL_EXPLANATION]
        
        [SECTION:INDIAN_EXAMPLE]
        Like pushing your cycle pedal harder to go faster.
        [/SECTION:INDIAN_EXAMPLE]
        
        [SECTION:METAPHOR]
        Think of it like pressing auto horn - harder press, louder sound.
        [/SECTION:METAPHOR]
        
        [SECTION:VISUAL_SCHEMA]
        {"diagram_type": "flow", "title": "Force", "nodes": [{"id": "n1", "label": "Force", "type": "main"}], "edges": [], "caption": "Force concept"}
        [/SECTION:VISUAL_SCHEMA]
        
        [SECTION:PROFESSOR_VERIFICATION]
        **Steps to prove logic:**
        1. Force equals mass times acceleration
        
        **Source:** NCERT Class 11
        
        **Confidence Score:** 0.9
        [/SECTION:PROFESSOR_VERIFICATION]
        
        [SECTION:MINI_PRACTICE]
        **Question:** What is force?
        **Hint:** Think F=ma
        [/SECTION:MINI_PRACTICE]
        
        [SECTION:ENCOURAGEMENT]
        Good clarity. Keep going.
        [/SECTION:ENCOURAGEMENT]
        
        [SECTION:ASK]
        Want to see examples?
        [/SECTION:ASK]
        """
        
        parsed = NeuroSymbolicParser.parse_full_response(response_text, "Physics", "JEE", "neutral")
        
        assert parsed['practical_explanation'] is not None
        assert parsed['indian_example'] is not None
        assert parsed['metaphor'] is not None
        assert parsed['visual_schema'] is not None
        assert parsed['professor_verification'] is not None
        assert parsed['mini_practice'] is not None
        assert parsed['encouragement'] is not None
        assert parsed['ask'] is not None
        assert parsed['student_emotion'] == "neutral"
        assert parsed['subject'] == "Physics"
        assert parsed['exam_mode'] == "JEE"


if __name__ == "__main__":
    print("=" * 80)
    print("🧪 Running Neuro-Symbolic AI Tutor Unit Tests")
    print("=" * 80)
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
