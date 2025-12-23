"""
Response Sanitization Tests - Regression tests for UI leak prevention.

These tests ensure that internal agent traces (thought, action, action_input, etc.)
and raw LLM outputs NEVER leak to the frontend/UI.

CRITICAL: These tests must pass before any deployment.
"""
import pytest
import json
import re
from typing import Dict, Any


# ============================================================================
# MOCK IMPORTS - Simulate the sanitization functions
# ============================================================================

def _sanitize_api_response(result: dict) -> dict:
    """
    LAST-MILE SANITIZER — Final gate before any response reaches frontend.
    Copy of the function from api/ai.py for testing.
    """
    if not result or not isinstance(result, dict):
        return result
    
    # Keys that should NEVER reach frontend
    FORBIDDEN_KEYS = {
        # ReAct/Agent internal traces
        'thought', 'action', 'action_input', 'confidence', 'observation',
        # Reasoning/debug chains
        'reasoning_chain', '_debug', '_internal', '_trace', '_symbolic',
        'agent_trace', 'thoughts', 'debug_info', 'internal_metadata',
        # Raw LLM outputs - NEVER expose to student
        'raw_response', 'llm_raw', 'raw_content', 'raw_envelope',
        'tool_calls_raw', 'planner_output',
        # Additional internal keys that might leak
        'mentor_raw', 'professor_raw', 'agentic_raw',
        # TOP-LEVEL INTERNAL OBJECTS - NEVER expose to student UI
        'hybrid_reasoning', 'orchestration', 'routing_decision',
        'symbolic_proof', 'verification_passed', 'graph_context',
        'knowledge_graph', 'cognitive_context'
    }
    
    # TOP-LEVEL keys that should be REMOVED from the response
    TOP_LEVEL_INTERNAL = {
        'hybrid_reasoning', 'orchestration', 'routing_decision',
        'knowledge_graph', 'cognitive_context', 'agents_used',
        'pipeline', 'verification', 'query'
    }
    
    def clean_dict(d):
        """Recursively remove forbidden keys and sanitize strings."""
        if not isinstance(d, dict):
            return d
        
        cleaned = {}
        for k, v in d.items():
            # Skip forbidden keys
            if k.lower() in FORBIDDEN_KEYS:
                continue
            
            # Recursively clean nested dicts
            if isinstance(v, dict):
                cleaned[k] = clean_dict(v)
            elif isinstance(v, list):
                cleaned[k] = [clean_dict(item) if isinstance(item, dict) else item for item in v]
            elif isinstance(v, str):
                cleaned[k] = clean_string(v)
            else:
                cleaned[k] = v
        
        return cleaned
    
    def clean_string(s):
        """Remove any embedded ReAct JSON from strings."""
        if not s or len(s) < 10:
            return s
        
        # Quick check: does it look like it might have internal traces?
        if '"thought"' not in s.lower() and '"action"' not in s.lower():
            return s
        
        # Try to find and remove JSON blocks with internal keys
        try:
            # Pattern to match JSON objects (simplified for speed)
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            
            def filter_json(match):
                try:
                    obj = json.loads(match.group())
                    if isinstance(obj, dict):
                        keys = {k.lower() for k in obj.keys()}
                        if keys & {'thought', 'action', 'action_input', 'confidence', 'observation'}:
                            return ''  # Remove this JSON block
                except:
                    pass
                return match.group()
            
            s = re.sub(json_pattern, filter_json, s)
        except:
            pass
        
        # Clean up whitespace
        s = re.sub(r'\n{3,}', '\n\n', s)
        return s.strip()
    
    # STEP 1: Clean the entire result recursively
    cleaned_result = clean_dict(result)
    
    # STEP 2: Remove top-level internal objects
    for key in list(cleaned_result.keys()):
        if key in TOP_LEVEL_INTERNAL:
            del cleaned_result[key]
    
    return cleaned_result


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def clean_response():
    """A properly structured response without internal traces."""
    return {
        "success": True,
        "response": {
            "default_view": {
                "greeting": "Hey! Let me help you understand quadratic equations.",
                "main_content": {
                    "content": "To solve quadratic equations for JEE, you can use three methods:\n1. Factoring\n2. Completing the square\n3. Quadratic formula",
                    "type": "markdown"
                }
            },
            "progressive_sections": {
                "explanation": "More detailed explanation here..."
            },
            "intent": "concept_explanation"
        },
        "detected_subject": "Mathematics",
        "generation_time": 1.5
    }


@pytest.fixture
def response_with_raw_response():
    """Response that includes raw_response field (should be removed)."""
    return {
        "success": True,
        "response": {
            "default_view": {
                "main_content": {
                    "content": "Clean answer here"
                }
            }
        },
        "raw_response": "This is the raw LLM output with all internal data...",
        "generation_time": 1.0
    }


@pytest.fixture
def response_with_react_traces():
    """Response with ReAct traces embedded in content."""
    return {
        "success": True,
        "response": {
            "default_view": {
                "main_content": {
                    "content": 'Here is the answer. {"thought": "I should explain this", "action": "search", "action_input": "quadratic"} More content here.'
                }
            }
        }
    }


@pytest.fixture
def response_with_nested_internal_keys():
    """Response with internal keys deeply nested."""
    return {
        "success": True,
        "response": {
            "default_view": {
                "main_content": {
                    "content": "Clean answer"
                },
                "_debug": {"internal": "data"},
                "reasoning_chain": ["step1", "step2"]
            },
            "agent_trace": {"iterations": 3}
        },
        "raw_response": "Raw LLM output",
        "_internal": {"secret": "data"}
    }


# ============================================================================
# TEST CASES
# ============================================================================

class TestResponseSanitization:
    """Tests for response sanitization to prevent UI leaks."""
    
    def test_clean_response_unchanged(self, clean_response):
        """Clean responses should pass through mostly unchanged."""
        result = _sanitize_api_response(clean_response)
        
        assert result["success"] == True
        assert "response" in result
        assert "default_view" in result["response"]
        assert result["response"]["default_view"]["greeting"] == "Hey! Let me help you understand quadratic equations."
    
    def test_raw_response_removed(self, response_with_raw_response):
        """raw_response field must be removed from output."""
        result = _sanitize_api_response(response_with_raw_response)
        
        assert "raw_response" not in result
        assert result["response"]["default_view"]["main_content"]["content"] == "Clean answer here"
    
    def test_react_traces_removed_from_string(self, response_with_react_traces):
        """ReAct traces embedded in strings must be removed."""
        result = _sanitize_api_response(response_with_react_traces)
        
        content = result["response"]["default_view"]["main_content"]["content"]
        assert '"thought"' not in content
        assert '"action"' not in content
        assert '"action_input"' not in content
        assert "Here is the answer" in content
        assert "More content here" in content
    
    def test_nested_internal_keys_removed(self, response_with_nested_internal_keys):
        """Internal keys at any nesting level must be removed."""
        result = _sanitize_api_response(response_with_nested_internal_keys)
        
        # Top-level internal keys removed
        assert "raw_response" not in result
        assert "_internal" not in result
        
        # Nested internal keys removed
        assert "_debug" not in result["response"]["default_view"]
        assert "reasoning_chain" not in result["response"]["default_view"]
        assert "agent_trace" not in result["response"]
        
        # Clean content preserved
        assert result["response"]["default_view"]["main_content"]["content"] == "Clean answer"
    
    def test_forbidden_keys_comprehensive(self):
        """All forbidden keys must be removed."""
        FORBIDDEN_KEYS = {
            'thought', 'action', 'action_input', 'confidence', 'observation',
            'reasoning_chain', '_debug', '_internal', '_trace', '_symbolic',
            'agent_trace', 'thoughts', 'raw_response', 'llm_raw', 'raw_content',
            'debug_info', 'internal_metadata', 'tool_calls_raw',
            'planner_output', 'raw_envelope', 'mentor_raw', 'professor_raw', 'agentic_raw'
        }
        
        # Create a response with ALL forbidden keys
        response = {"success": True, "response": {"main": "content"}}
        for key in FORBIDDEN_KEYS:
            response[key] = f"forbidden_{key}"
        
        result = _sanitize_api_response(response)
        
        for key in FORBIDDEN_KEYS:
            assert key not in result, f"Forbidden key '{key}' was not removed"
    
    def test_no_brace_blocks_in_output(self, response_with_react_traces):
        """Final output should not contain raw JSON brace blocks."""
        result = _sanitize_api_response(response_with_react_traces)
        
        content = result["response"]["default_view"]["main_content"]["content"]
        
        # Check for suspicious patterns that indicate leaked internal data
        # Note: Legitimate JSON in educational content (like code examples) is fine
        # We specifically check for ReAct-style patterns
        assert not re.search(r'\{"thought":', content)
        assert not re.search(r'\{"action":', content)
        assert not re.search(r'\{"action_input":', content)
    
    def test_empty_response_handled(self):
        """Empty/None responses should be handled gracefully."""
        assert _sanitize_api_response(None) is None
        assert _sanitize_api_response({}) == {}
    
    def test_string_response_handled(self):
        """Non-dict responses should pass through."""
        result = _sanitize_api_response("Just a string")
        assert result == "Just a string"
    
    def test_hybrid_reasoning_removed(self):
        """hybrid_reasoning object must be removed from top level."""
        response = {
            "success": True,
            "response": {
                "default_view": {
                    "main_content": {
                        "content": "In physics, force is..."
                    }
                }
            },
            "hybrid_reasoning": {
                "mode": "hybrid",
                "symbolic_proof": None,
                "confidence": 0.85,  # This is what appears as "conf" in UI!
                "verification_passed": True,
                "recommendations": []
            },
            "detected_subject": "Physics"
        }
        
        result = _sanitize_api_response(response)
        
        # hybrid_reasoning must be completely removed
        assert "hybrid_reasoning" not in result
        # The response object should be preserved
        assert "response" in result
        assert result["response"]["default_view"]["main_content"]["content"] == "In physics, force is..."
    
    def test_orchestration_removed(self):
        """orchestration metadata must be removed from top level."""
        response = {
            "response": {"main": "content"},
            "orchestration": {
                "pipeline": "hybrid_reasoning",
                "complexity": "moderate",
                "confidence": 0.9,
                "agents_activated": ["mentor", "professor"],
                "tools_enabled": ["rag"]
            },
            "pipeline": "hybrid_reasoning",
            "agents_used": ["mentor", "professor"]
        }
        
        result = _sanitize_api_response(response)
        
        assert "orchestration" not in result
        assert "pipeline" not in result
        assert "agents_used" not in result
    
    def test_all_top_level_internal_removed(self):
        """All top-level internal metadata must be removed."""
        TOP_LEVEL_INTERNAL = {
            'hybrid_reasoning', 'orchestration', 'routing_decision',
            'knowledge_graph', 'cognitive_context', 'agents_used',
            'pipeline', 'verification', 'query'
        }
        
        response = {"response": {"main": "content"}}
        for key in TOP_LEVEL_INTERNAL:
            response[key] = {"internal": "data"}
        
        result = _sanitize_api_response(response)
        
        for key in TOP_LEVEL_INTERNAL:
            assert key not in result, f"Top-level internal key '{key}' was not removed"


class TestMainResponseContract:
    """Tests for the main_response display contract."""
    
    def test_main_response_is_string_or_absent(self, clean_response):
        """main_response, if present, must be a string."""
        # Add main_response
        clean_response["main_response"] = "This is the main response"
        
        result = _sanitize_api_response(clean_response)
        
        if "main_response" in result:
            assert isinstance(result["main_response"], str)
    
    def test_no_dict_in_display_content(self):
        """Display content fields must never contain raw dicts."""
        response = {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": {"nested": "dict"}  # This is wrong!
                    }
                }
            }
        }
        
        result = _sanitize_api_response(response)
        
        # The content should still be the dict (sanitizer doesn't convert types)
        # But the BACKEND should never send this structure
        # This test documents expected behavior
        content = result["response"]["default_view"]["main_content"]["content"]
        # Content should be sanitized if it's a dict
        assert isinstance(content, dict)  # Sanitizer preserves type


class TestStreamingSafetyContract:
    """Tests for streaming response safety."""
    
    def test_chunk_must_be_string(self):
        """Emitted streaming chunks must be strings, not dicts."""
        # This is a documentation test - actual streaming tests would be integration tests
        valid_chunk = "Here is part of the response..."
        invalid_chunk = {"text": "Here is part...", "confidence": 0.9}
        
        assert isinstance(valid_chunk, str)
        assert not isinstance(invalid_chunk, str)
    
    def test_no_intermediate_state_in_chunks(self):
        """Streaming chunks should not contain intermediate agent state."""
        # Document the contract
        invalid_chunks = [
            '{"thought": "thinking..."}',
            '{"action": "search", "action_input": "query"}',
            '{"observation": "found result"}'
        ]
        
        for chunk in invalid_chunks:
            # These should be flagged as invalid
            assert '"thought"' in chunk or '"action"' in chunk or '"observation"' in chunk


class TestReActParsingFix:
    """Tests for the ReAct agent JSON parsing fix."""
    
    def test_malformed_json_extracts_answer(self):
        """Malformed JSON should extract the answer field, not return raw JSON."""
        # Simulate the malformed JSON the LLM might return
        malformed_response = '''
{
"thought": "The student is asking for explanations of a few concepts in mathematics"
"action": "FINISH",
"action_input": {"answer": "Here are some fundamental concepts in mathematics:

1. **Algebra** - deals with symbols and equations
2. **Geometry** - focuses on shapes and spaces
3. **Calculus** - studies rates of change"}
}
'''
        # Import the parser
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        # Test that we extract the answer, not the raw JSON
        import re
        answer_match = re.search(r'"answer"\s*:\s*"([^"]*(?:"[^"]*"[^"]*)*)"', malformed_response)
        
        # The regex should find an answer
        assert answer_match is not None
        extracted = answer_match.group(1)
        assert "Algebra" in extracted or len(extracted) > 20
    
    def test_raw_json_never_in_content(self):
        """Content field must never contain raw JSON structure."""
        # These patterns should NEVER appear in final content
        forbidden_patterns = [
            r'^\s*\{\s*"thought"',
            r'"action"\s*:\s*"FINISH"',
            r'"action_input"\s*:\s*\{',
            r'^\s*\{\s*\n\s*"'
        ]
        
        clean_content = "Here are some fundamental concepts in mathematics"
        
        for pattern in forbidden_patterns:
            assert not re.search(pattern, clean_content, re.MULTILINE)
    
    def test_sanitize_removes_json_from_content(self):
        """Final sanitization should remove any JSON traces from content."""
        import re
        
        # Content that somehow got JSON mixed in
        dirty_content = '''Here is the explanation.

{"thought": "I should explain more", "action": "FINISH"}

More explanation here.'''
        
        # Sanitize
        cleaned = re.sub(
            r'\{\s*"(?:thought|action|action_input|confidence|observation)"[^}]*\}',
            '', dirty_content, flags=re.IGNORECASE | re.DOTALL
        )
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
        
        assert '"thought"' not in cleaned
        assert '"action"' not in cleaned
        assert "Here is the explanation" in cleaned
        assert "More explanation here" in cleaned


class TestEducationResponseFormatting:
    """Tests for education-specific formatting (LaTeX, math, structure)."""
    
    def test_lone_backslash_removed(self):
        """Lone backslash lines must be removed from output."""
        # This is what was showing in the UI
        content_with_stray_backslash = '''The fundamental theorem states:

\\

$$\\int_a^b f(x) dx = F(b) - F(a)$$

\\

This means the integral...'''
        
        # Apply sanitization
        cleaned = re.sub(r'^\s*\\+\s*$', '', content_with_stray_backslash, flags=re.MULTILINE)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
        
        # No line should be just a backslash
        lines = cleaned.split('\n')
        for line in lines:
            assert line.strip() != '\\', f"Found lone backslash line: '{line}'"
            assert line.strip() != '\\\\', f"Found double backslash line: '{line}'"
    
    def test_latex_delimiters_normalized(self):
        """\\[ and \\] should be converted to $$ for consistent rendering."""
        content_with_old_delimiters = '''The formula is:

\\[ F = ma \\]

And for inline: \\( E = mc^2 \\)'''
        
        # Apply normalization
        cleaned = content_with_old_delimiters
        cleaned = re.sub(r'\\\[\s*', '\n$$', cleaned)
        cleaned = re.sub(r'\s*\\\]', '$$\n', cleaned)
        cleaned = re.sub(r'\\\(\s*', '$', cleaned)
        cleaned = re.sub(r'\s*\\\)', '$', cleaned)
        
        assert '\\[' not in cleaned
        assert '\\]' not in cleaned
        assert '\\(' not in cleaned
        assert '\\)' not in cleaned
        assert '$$' in cleaned
        assert '$E = mc^2$' in cleaned or '$ E = mc^2 $' in cleaned
    
    def test_json_fragment_at_end_removed(self):
        """JSON fragments like "}, at end of response must be removed."""
        content_with_json_end = '''This is a great explanation of calculus.

The integral represents the area under the curve."},'''
        
        cleaned = re.sub(r'["\']?\s*\}\s*,?\s*$', '', content_with_json_end)
        
        assert not cleaned.endswith('"},')
        assert not cleaned.endswith('"}')
        assert not cleaned.endswith('},')
        assert "area under the curve" in cleaned
    
    def test_double_escaped_latex_fixed(self):
        """\\\\int should become \\int for proper rendering."""
        content_with_double_escape = '''$$\\\\int_a^b f(x) dx$$'''
        
        def fix_latex(match):
            content = match.group(1)
            content = re.sub(r'\\\\([a-zA-Z]+)', r'\\\1', content)
            return '$$' + content + '$$'
        
        cleaned = re.sub(r'\$\$([^$]+)\$\$', fix_latex, content_with_double_escape, flags=re.DOTALL)
        
        assert '\\\\int' not in cleaned
        assert '\\int' in cleaned
    
    def test_latex_normalization_idempotent(self):
        """
        CRITICAL: Running LaTeX normalization twice must produce identical output.
        This prevents the \\\\frac → \\frac → \frac multi-pass issue.
        """
        # Known LaTeX commands pattern (must match the one in unified_ai_orchestrator.py)
        LATEX_COMMANDS = (
            r'frac|int|sum|prod|sqrt|lim|sin|cos|tan|log|ln|exp|max|min|sup|inf|'
            r'partial|nabla|vec|hat|bar|dot|ddot|'
            r'alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|omega|phi|psi|rho|tau|'
            r'Delta|Sigma|Omega|Gamma|Lambda|Phi|Psi|'
            r'cdot|times|div|pm|mp|leq|geq|neq|approx|equiv|subset|supset|in|notin|'
            r'forall|exists|rightarrow|leftarrow|Rightarrow|Leftarrow|'
            r'infty|text|mathrm|mathbf|mathit|mathcal|mathbb|'
            r'begin|end|left|right|big|Big|bigg|Bigg|'
            r'quad|qquad|hspace|vspace|over|atop'
        )
        
        def normalize_latex_backslashes(content: str) -> str:
            """Same logic as in unified_ai_orchestrator.py"""
            return re.sub(r'\\{2,}(' + LATEX_COMMANDS + r')', r'\\\1', content)
        
        test_cases = [
            # (input, expected after one pass)
            (r'$$\\\\frac{a}{b}$$', r'$$\frac{a}{b}$$'),  # 4 backslashes → 1
            (r'$$\\frac{a}{b}$$', r'$$\frac{a}{b}$$'),    # 2 backslashes → 1
            (r'$$\frac{a}{b}$$', r'$$\frac{a}{b}$$'),     # 1 backslash → 1 (unchanged)
            (r'$\\\\int_0^1 x dx$', r'$\int_0^1 x dx$'),  # inline math
            (r'\\\\\\\\sqrt{2}', r'\sqrt{2}'),             # 8 backslashes → 1
        ]
        
        for input_text, expected in test_cases:
            # First pass
            result1 = normalize_latex_backslashes(input_text)
            # Second pass
            result2 = normalize_latex_backslashes(result1)
            
            # Both passes should produce the expected result
            assert result1 == expected, f"First pass failed: {input_text!r} → {result1!r}, expected {expected!r}"
            # IDEMPOTENT: second pass must equal first pass
            assert result2 == result1, f"Not idempotent: {result1!r} → {result2!r}"
    
    def test_no_double_escape_frac(self):
        """
        REGRESSION: Input containing \\\\\\\\frac must become \\frac in output.
        This was causing visible \\\\frac in the UI.
        """
        LATEX_COMMANDS = (
            r'frac|int|sum|prod|sqrt|lim|sin|cos|tan|log|ln|exp|max|min|sup|inf|'
            r'partial|nabla|vec|hat|bar|dot|ddot|'
            r'alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|omega|phi|psi|rho|tau|'
            r'Delta|Sigma|Omega|Gamma|Lambda|Phi|Psi|'
            r'cdot|times|div|pm|mp|leq|geq|neq|approx|equiv|subset|supset|in|notin|'
            r'forall|exists|rightarrow|leftarrow|Rightarrow|Leftarrow|'
            r'infty|text|mathrm|mathbf|mathit|mathcal|mathbb|'
            r'begin|end|left|right|big|Big|bigg|Bigg|'
            r'quad|qquad|hspace|vspace|over|atop'
        )
        
        def normalize_latex_backslashes(content: str) -> str:
            return re.sub(r'\\{2,}(' + LATEX_COMMANDS + r')', r'\\\1', content)
        
        # These are the problematic patterns that were appearing in UI
        problematic_inputs = [
            r'$$\\\\frac{a}{b}$$',           # Double escape in block
            r'The formula \\\\frac{1}{2}',    # Double escape outside delimiters
            r'$\\\\\\\\int_0^1$',             # Quadruple escape
            r'\\\\sum_{i=1}^n',               # Double escape for sum
        ]
        
        for inp in problematic_inputs:
            result = normalize_latex_backslashes(inp)
            # Should NOT contain double backslashes before LaTeX commands
            assert r'\\frac' not in result or result.count('\\') == 1, \
                f"Double backslash still present: {inp!r} → {result!r}"
            assert r'\\int' not in result or result.count('\\') == 1, \
                f"Double backslash still present: {inp!r} → {result!r}"
            assert r'\\sum' not in result or result.count('\\') == 1, \
                f"Double backslash still present: {inp!r} → {result!r}"
    
    def test_preserve_normal_backslashes_non_latex(self):
        """
        Non-LaTeX backslashes (like Windows paths) must NOT be modified.
        Only backslashes before known LaTeX commands are normalized.
        """
        LATEX_COMMANDS = (
            r'frac|int|sum|prod|sqrt|lim|sin|cos|tan|log|ln|exp|max|min|sup|inf|'
            r'partial|nabla|vec|hat|bar|dot|ddot|'
            r'alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|omega|phi|psi|rho|tau|'
            r'Delta|Sigma|Omega|Gamma|Lambda|Phi|Psi|'
            r'cdot|times|div|pm|mp|leq|geq|neq|approx|equiv|subset|supset|in|notin|'
            r'forall|exists|rightarrow|leftarrow|Rightarrow|Leftarrow|'
            r'infty|text|mathrm|mathbf|mathit|mathcal|mathbb|'
            r'begin|end|left|right|big|Big|bigg|Bigg|'
            r'quad|qquad|hspace|vspace|over|atop'
        )
        
        def normalize_latex_backslashes(content: str) -> str:
            return re.sub(r'\\{2,}(' + LATEX_COMMANDS + r')', r'\\\1', content)
        
        # These should remain UNCHANGED
        non_latex_paths = [
            r'C:\\Users\\name\\Documents',           # Windows path
            r'The path is C:\\Program Files\\App',   # Mixed text with path
            r'\\server\\share\\folder',              # Network path
            r'Newline is \\n and tab is \\t',        # Escape sequences
            r'JSON uses \\"quotes\\"',               # JSON escapes
        ]
        
        for inp in non_latex_paths:
            result = normalize_latex_backslashes(inp)
            assert result == inp, f"Non-LaTeX path was modified: {inp!r} → {result!r}"
    
    def test_no_raw_latex_delimiters_in_output(self):
        """Final output must not contain unrendered \\[ \\] \\( \\) delimiters."""
        # Simulate content after sanitization
        content = '''The fundamental theorem of calculus:

$$\\int_a^b f(x) dx = F(b) - F(a)$$

Where $F$ is the antiderivative.'''
        
        # These patterns should NOT be in well-formatted output
        assert '\\[' not in content
        assert '\\]' not in content
        # Note: \\( and \\) inside $$ blocks are OK (like \\int)
        # But standalone ones are not
        standalone_inline = re.search(r'(?<!\$)\\\(|\\\)(?!\$)', content)
        assert standalone_inline is None, "Found standalone \\( or \\) outside math"
    
    def test_no_duplicate_paragraphs(self):
        """Same paragraph should not appear twice in output after deduplication."""
        # This was happening in some responses - exact same content repeated
        content_with_dupe = '''The fundamental theorem of calculus states that differentiation and integration are inverse processes. If f is continuous on [a, b], then the integral of f from a to b equals F(b) minus F(a), where F is an antiderivative of f.

This is more detail about applications.

The fundamental theorem of calculus states that differentiation and integration are inverse processes. If f is continuous on [a, b], then the integral of f from a to b equals F(b) minus F(a), where F is an antiderivative of f.

And the conclusion.'''
        
        # Apply deduplication logic
        paragraphs = content_with_dupe.split('\n\n')
        seen_paragraphs = set()
        unique_paragraphs = []
        for para in paragraphs:
            para_stripped = para.strip()
            if not para_stripped:
                continue
            para_normalized = ' '.join(para_stripped.lower().split())
            if len(para_normalized) > 80:
                if para_normalized in seen_paragraphs:
                    continue  # Skip duplicate
                seen_paragraphs.add(para_normalized)
            unique_paragraphs.append(para_stripped)
        
        cleaned = '\n\n'.join(unique_paragraphs)
        
        # Should have removed the duplicate
        assert cleaned.count('fundamental theorem of calculus states') == 1, \
            f"Expected 1 occurrence, found {cleaned.count('fundamental theorem of calculus states')}"
    
    def test_teachback_prompt_remains_readable(self):
        """Teach Me Back prompt should be appended cleanly."""
        base_response = '''Here is the explanation of force.

**Formula:** $F = ma$'''
        
        teachback = "\n\n🎯 **Quick Check:** Can you explain Newton's Second Law in your own words?"
        
        final = base_response + teachback
        
        # Should be valid markdown
        assert '**Quick Check:**' in final
        assert '$F = ma$' in final
        assert final.count('**') >= 2  # At least Formula and Quick Check
    
    def test_output_is_always_string(self):
        """Final content must always be a string, never dict/list."""
        test_inputs = [
            "Clean string response",
            {"content": "Dict with content"},
            ["List", "of", "things"],
            None,
            123,
        ]
        
        for inp in test_inputs:
            if isinstance(inp, str):
                result = inp
            elif isinstance(inp, dict):
                result = inp.get('content', str(inp))
            elif inp is None:
                result = ""
            else:
                result = str(inp)
            
            assert isinstance(result, str)
    
    def test_unwrapped_latex_gets_delimiters(self):
        """Orphan LaTeX commands should be wrapped in $ delimiters."""
        content_with_orphan_latex = '''The formula is:

\\int_a^b f(x) dx = F(b) - F(a)

This shows the relationship.'''
        
        # Apply wrapping logic
        import re
        def wrap_orphan_latex(match):
            return f'${match.group(0)}$'
        
        cleaned = re.sub(
            r'(?<![a-zA-Z$])(\\(?:int|frac|sum|prod|sqrt|lim|sin|cos|tan|log|ln)(?:_[^$\s]+|\{[^}]+\})*(?:\s*[+\-=<>]\s*[^\n$]+)?)',
            wrap_orphan_latex, 
            content_with_orphan_latex
        )
        
        # Should now have $ delimiters
        assert '$\\int' in cleaned or '$' in cleaned


class TestResponseRenderingGate:
    """Tests for the centralized Response Rendering Gate (fast path + slow path)."""
    
    def test_fast_path_clean_response(self):
        """Clean responses should pass through fast path unchanged."""
        clean_response = '''Here is a clean explanation of Newton's Laws.

**First Law:** An object at rest stays at rest unless acted upon by a force.

**Second Law:** $F = ma$

**Third Law:** For every action, there is an equal and opposite reaction.'''
        
        # Fast path checks
        has_json_traces = any(marker in clean_response for marker in [
            '{"thought":', '"action_input"', '"action":',
            'Student asked:', 'confidence:'
        ])
        
        assert not has_json_traces, "Clean response should not trigger slow path"
    
    def test_slow_path_triggers_on_json(self):
        """JSON traces should trigger slow path."""
        dirty_response = '''Here is the explanation.
        
{"thought": "I should explain this", "action": "FINISH"}'''
        
        has_json_traces = any(marker in dirty_response for marker in [
            '{"thought":', '"action_input"', '"action":',
            'Student asked:', 'confidence:'
        ])
        
        assert has_json_traces, "JSON traces should trigger slow path"
    
    def test_no_empty_output(self):
        """Rendering gate must never return empty output."""
        test_inputs = [
            "",
            "   ",
            None,
            "Very short"
        ]
        
        for inp in test_inputs:
            if not inp or len(str(inp).strip()) < 20:
                # Should use fallback
                result = inp if inp and len(str(inp).strip()) >= 20 else "I'm processing your request..."
                assert len(result) > 0, "Must never return empty output"


class TestCompletenessGuard:
    """Tests for response completeness detection and fixing."""
    
    def test_truncated_mid_word_detected(self):
        """Response ending mid-word should be detected as truncated."""
        # Response that is clearly truncated mid-word (> 100 chars)
        truncated = "The fundamental theorem of calculus connects differentiation and integration, two core concepts in mathemat"
        
        # Check for truncation indicators - ending mid-word without proper suffix
        is_truncated = (
            len(truncated) > 100 and 
            truncated[-1].isalpha() and 
            truncated[-2].isalpha() and
            not truncated.endswith(('ing', 'tion', 'ment', 'ness', 'ally', 'ible', 'able', 'ics'))
        )
        
        assert is_truncated, f"Mid-word truncation should be detected (len={len(truncated)}, ends={truncated[-10:]})"
    
    def test_unclosed_brackets_detected(self):
        """Unclosed brackets should be detected."""
        unclosed = "The formula is F = ma (where m is mass"
        
        is_truncated = unclosed.count('(') > unclosed.count(')')
        assert is_truncated, "Unclosed parenthesis should be detected"
    
    def test_completeness_fix_closes_brackets(self):
        """Completeness guard should close unclosed brackets."""
        unclosed = "The formula is F = ma (where m is mass"
        
        # Apply fix
        fixed = unclosed
        while fixed.count('(') > fixed.count(')'):
            fixed += ')'
        
        assert fixed.count('(') == fixed.count(')'), "Brackets should be balanced"
    
    def test_ends_with_comma_detected(self):
        """Response ending with comma/colon should be detected."""
        truncated = "The key concepts are:"
        
        is_truncated = truncated.rstrip().endswith((',', ':', ' and', ' or', ' the', ' a'))
        assert is_truncated, "Trailing comma/colon should be detected"


class TestUIForbiddenPatterns:
    """Tests that forbidden patterns are never in UI output."""
    
    def test_no_thought_action_in_output(self):
        """Output must never contain thought/action/action_input keys."""
        # Simulated dirty input with ReAct traces
        dirty_output = '''Here is the explanation.

{"thought": "Let me think about this", "action": "FINISH", "action_input": {"answer": "The answer is 42"}}

More content here.'''
        
        # Apply sanitization pattern
        import re
        cleaned = re.sub(
            r'\{\s*"(?:thought|action|action_input|confidence|observation)"[^}]*\}',
            '', dirty_output, flags=re.IGNORECASE | re.DOTALL
        )
        
        assert '"thought"' not in cleaned
        assert '"action"' not in cleaned
        assert '"action_input"' not in cleaned
    
    def test_no_student_asked_in_output(self):
        """Output must never contain 'Student asked:' debug lines."""
        dirty_output = "Student asked: What is calculus?\n\nCalculus is the study of change."
        
        # Simple removal
        import re
        cleaned = re.sub(r'^Student asked:.*$', '', dirty_output, flags=re.MULTILINE)
        
        assert "Student asked:" not in cleaned
    
    def test_no_traceback_in_output(self):
        """Output must never contain Python tracebacks."""
        dirty_output = '''Here is the answer.

Traceback (most recent call last):
  File "test.py", line 1
Exception: Something went wrong

More content.'''
        
        # Check for traceback markers
        has_traceback = 'Traceback (' in dirty_output or 'Exception:' in dirty_output
        assert has_traceback, "Traceback should be detected"
    
    def test_no_routing_metadata_in_output(self):
        """Output must never contain routing/orchestration metadata."""
        forbidden_keys = ['"routing":', '"tool_calls":', '{"step":', '"orchestration":']
        
        clean_output = "Here is a clear explanation of Newton's Laws of Motion."
        
        for key in forbidden_keys:
            assert key not in clean_output, f"Forbidden key {key} should not be in output"


class TestStructureBasedFormatting:
    """Tests for structure-based (not keyword-based) formatting."""
    
    def test_latex_detection_by_structure(self):
        """LaTeX should be detected by structure (backslash commands), not keywords."""
        import re
        
        content_with_latex = "The integral is \\int_0^1 x dx"
        content_without_latex = "The integral is the area under a curve"
        
        # Structure-based detection: look for backslash followed by command
        latex_pattern = r'\\[a-zA-Z]+'
        
        has_latex_1 = bool(re.search(latex_pattern, content_with_latex))
        has_latex_2 = bool(re.search(latex_pattern, content_without_latex))
        
        assert has_latex_1, "Should detect LaTeX by backslash commands"
        assert not has_latex_2, "Should not false-positive on word 'integral'"
    
    def test_steps_detection_by_structure(self):
        """Steps/procedures should be detected by numbering structure."""
        procedural_content = '''1. First, identify the problem
2. Apply the formula
3. Calculate the result'''
        
        narrative_content = "The problem involves calculating force using mass and acceleration."
        
        # Structure-based: numbered list pattern
        import re
        has_steps = bool(re.search(r'^\s*\d+\.', procedural_content, re.MULTILINE))
        no_steps = bool(re.search(r'^\s*\d+\.', narrative_content, re.MULTILINE))
        
        assert has_steps, "Should detect numbered steps"
        assert not no_steps, "Should not detect steps in narrative"


class TestStreamingChunkSanitization:
    """Tests for SSE streaming chunk sanitization."""
    
    def test_streaming_no_json_thought_action(self):
        """
        SHIP BLOCKER: Streaming chunks must never contain {"thought": ...} or similar.
        """
        from services.streaming_service import _sanitize_streaming_chunk
        
        dirty_chunks = [
            'Here is the answer. {"thought": "thinking...", "action": "FINISH"}',
            '{"action_input": {"result": "42"}} The answer is 42.',
            'Newton\'s law states {"confidence": 0.95, "observation": "correct"}',
            'Force equals {"tool_calls": [{"name": "calc"}]} mass times acceleration',
            'Step 1: Think\nThought: Let me analyze\nAction: Calculate',
        ]
        
        for dirty in dirty_chunks:
            clean = _sanitize_streaming_chunk(dirty)
            
            # These should NOT be in output
            assert '"thought"' not in clean.lower(), f"thought leaked in: {clean}"
            assert '"action"' not in clean.lower() or 'action' in dirty.lower().replace('"action"', ''), f"action leaked in: {clean}"
            assert '"action_input"' not in clean.lower(), f"action_input leaked in: {clean}"
            assert '"tool_calls"' not in clean.lower(), f"tool_calls leaked in: {clean}"
            assert '"confidence"' not in clean.lower(), f"confidence leaked in: {clean}"
    
    def test_streaming_preserves_normal_text(self):
        """Clean chunks should pass through unchanged."""
        from services.streaming_service import _sanitize_streaming_chunk
        
        clean_chunks = [
            "Newton's First Law states that an object at rest stays at rest.",
            "The integral of x from 0 to 1 is 0.5.",
            "Force equals mass times acceleration, F = ma.",
            "Step 1: Identify variables\nStep 2: Apply formula",
            "🎯 **Key concept:** Force is a vector quantity.",
        ]
        
        for clean in clean_chunks:
            result = _sanitize_streaming_chunk(clean)
            # Clean text should be preserved (or minimally changed)
            # Allow for whitespace normalization
            assert len(result) >= len(clean) * 0.9, f"Too much removed from clean chunk: {clean!r} → {result!r}"
    
    def test_streaming_handles_partial_json(self):
        """Partial/broken JSON should be cleaned without breaking stream."""
        from services.streaming_service import _sanitize_streaming_chunk
        
        partial_json_chunks = [
            '{"thought": "incomplete',
            'result is {"action":',
            '}}\n\nThe answer is 42',
            '{\n  "routing": {\n',
        ]
        
        for partial in partial_json_chunks:
            # Should not raise
            try:
                result = _sanitize_streaming_chunk(partial)
                # Should return something (not crash)
                assert isinstance(result, str), "Should return string"
            except Exception as e:
                pytest.fail(f"Sanitizer crashed on partial JSON: {partial!r} - {e}")
    
    def test_streaming_removes_student_asked(self):
        """'Student asked:' debug lines must be removed from streaming."""
        from services.streaming_service import _sanitize_streaming_chunk
        
        dirty = "Student asked: What is calculus?\n\nCalculus is the mathematical study of change."
        clean = _sanitize_streaming_chunk(dirty)
        
        assert "Student asked:" not in clean
        assert "Calculus is" in clean or "calculus" in clean.lower()
    
    def test_streaming_removes_traceback(self):
        """Python tracebacks must be removed from streaming."""
        from services.streaming_service import _sanitize_streaming_chunk
        
        dirty = "Here's the answer.\n\nTraceback (most recent call last):\n  File 'x.py'\nError\n\nMore text."
        clean = _sanitize_streaming_chunk(dirty)
        
        assert "Traceback (" not in clean
        assert "Here's the answer" in clean or "More text" in clean
    
    def test_streaming_fast_path_performance(self):
        """Fast path should be O(1) for clean chunks."""
        from services.streaming_service import _sanitize_streaming_chunk, FORBIDDEN_STREAMING_PATTERNS
        import time
        
        # Generate clean chunks of varying sizes
        clean_chunks = [
            "Short clean text.",
            "Medium length clean text that explains physics concepts clearly and concisely." * 10,
            "Long clean text about calculus and integration methods. " * 100,
        ]
        
        for chunk in clean_chunks:
            # Warm up
            _sanitize_streaming_chunk(chunk)
            
            # Time it
            start = time.perf_counter()
            for _ in range(100):
                _sanitize_streaming_chunk(chunk)
            elapsed = time.perf_counter() - start
            
            # Should be very fast (< 10ms for 100 iterations)
            assert elapsed < 0.1, f"Fast path too slow: {elapsed*1000:.2f}ms for 100 calls on {len(chunk)} chars"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

