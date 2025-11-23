"""
Dynamic Response Template System
Creates varied, engaging response structures based on intent, student profile, and context
Prevents repetitive templates that make students feel disconnected
"""
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseTemplateVariety:
    """Manages variety in response presentation to keep students engaged"""
    
    # Track which templates were used recently (per user)
    _recent_templates: Dict[str, List[str]] = {}
    
    @staticmethod
    def get_template_style(
        user_id: str,
        intent: str,
        student_profile: Optional[Dict[str, Any]] = None,
        question_complexity: str = "medium"
    ) -> str:
        """
        Select a template style that:
        1. Matches the intent
        2. Avoids recent repetition
        3. Considers student preferences
        4. Varies presentation
        """
        # Get available styles for this intent
        available_styles = ResponseTemplateVariety._get_available_styles(intent)
        
        # Get recent templates for this user (last 5)
        recent = ResponseTemplateVariety._recent_templates.get(user_id, [])
        
        # Filter out recently used styles
        fresh_styles = [s for s in available_styles if s not in recent[-3:]]
        
        # If all styles were used recently, allow reuse but prefer less recent ones
        if not fresh_styles:
            fresh_styles = available_styles
        
        # Consider student preferences
        preferred_style = None
        if student_profile:
            preferred_style = student_profile.get('preferences', {}).get('response_style')
            if preferred_style and preferred_style in fresh_styles:
                selected = preferred_style
            else:
                selected = random.choice(fresh_styles)
        else:
            selected = random.choice(fresh_styles)
        
        # Track usage
        if user_id not in ResponseTemplateVariety._recent_templates:
            ResponseTemplateVariety._recent_templates[user_id] = []
        ResponseTemplateVariety._recent_templates[user_id].append(selected)
        if len(ResponseTemplateVariety._recent_templates[user_id]) > 10:
            ResponseTemplateVariety._recent_templates[user_id].pop(0)
        
        logger.info(f"🎨 Selected template style '{selected}' for intent '{intent}' (user: {user_id})")
        return selected
    
    @staticmethod
    def _get_available_styles(intent: str) -> List[str]:
        """Get available template styles for each intent type"""
        style_map = {
            "definition_query": [
                "quick_card",      # Compact definition card
                "expanded_definition",  # Full definition with examples
                "visual_first",    # Visual with definition below
                "story_definition"  # Definition wrapped in story
            ],
            "concept_explanation": [
                "layered_reveal",   # Progressive disclosure (current)
                "story_journey",    # Concept as a story
                "visual_anchor",    # Visual-first with text support
                "conversational",   # Chat-like, less structured
                "exam_focused",     # Exam tips prominently featured
                "analogy_heavy"     # Multiple analogies
            ],
            "compare_query": [
                "side_by_side",     # Comparison table
                "before_after",     # Sequential comparison
                "visual_comparison", # Visual comparison grid
                "narrative_compare"  # Story-based comparison
            ],
            "deep_dive": [
                "step_by_step",     # Detailed steps
                "reasoning_path",   # Logical reasoning flow
                "visual_sequence",  # Visual step sequence
                "interactive_proof"  # Interactive derivation
            ],
            "application_request": [
                "real_world_story",  # Real-world scenario
                "hands_on",          # Practical steps
                "visual_scenario",   # Visual scenario
                "case_study"         # Case study format
            ],
            "clarification_follow_up": [
                "fresh_angle",      # Different perspective
                "simplified",       # Simplified version
                "visual_clarify",   # Visual clarification
                "quick_recap"       # Quick recap format
            ]
        }
        
        return style_map.get(intent, ["layered_reveal"])  # Default fallback


class DynamicResponseBuilder:
    """Builds dynamic response structures based on template style and intent"""
    
    @staticmethod
    def build_response_structure(
        template_style: str,
        intent: str,
        mentor_content: str,
        professor_content: str,
        metaphor_used: str,
        student_profile: Optional[Dict[str, Any]] = None,
        question: str = "",
        concept_name: str = ""
    ) -> Dict[str, Any]:
        """
        Build response structure based on template style
        
        Returns:
            Dict with default_view, progressive_sections, and render_directives
        """
        builder_map = {
            "quick_card": DynamicResponseBuilder._build_quick_card,
            "expanded_definition": DynamicResponseBuilder._build_expanded_definition,
            "visual_first": DynamicResponseBuilder._build_visual_first,
            "story_definition": DynamicResponseBuilder._build_story_definition,
            "layered_reveal": DynamicResponseBuilder._build_layered_reveal,
            "story_journey": DynamicResponseBuilder._build_story_journey,
            "visual_anchor": DynamicResponseBuilder._build_visual_anchor,
            "conversational": DynamicResponseBuilder._build_conversational,
            "exam_focused": DynamicResponseBuilder._build_exam_focused,
            "analogy_heavy": DynamicResponseBuilder._build_analogy_heavy,
            "side_by_side": DynamicResponseBuilder._build_side_by_side,
            "before_after": DynamicResponseBuilder._build_before_after,
            "visual_comparison": DynamicResponseBuilder._build_visual_comparison,
            "narrative_compare": DynamicResponseBuilder._build_narrative_compare,
            "step_by_step": DynamicResponseBuilder._build_step_by_step,
            "reasoning_path": DynamicResponseBuilder._build_reasoning_path,
            "visual_sequence": DynamicResponseBuilder._build_visual_sequence,
            "interactive_proof": DynamicResponseBuilder._build_interactive_proof,
            "real_world_story": DynamicResponseBuilder._build_real_world_story,
            "hands_on": DynamicResponseBuilder._build_hands_on,
            "visual_scenario": DynamicResponseBuilder._build_visual_scenario,
            "case_study": DynamicResponseBuilder._build_case_study,
            "fresh_angle": DynamicResponseBuilder._build_fresh_angle,
            "simplified": DynamicResponseBuilder._build_simplified,
            "visual_clarify": DynamicResponseBuilder._build_visual_clarify,
            "quick_recap": DynamicResponseBuilder._build_quick_recap
        }
        
        builder = builder_map.get(template_style, DynamicResponseBuilder._build_layered_reveal)
        
        return builder(
            mentor_content=mentor_content,
            professor_content=professor_content,
            metaphor_used=metaphor_used,
            student_profile=student_profile,
            question=question,
            concept_name=concept_name
        )
    
    # ========== DEFINITION TEMPLATES ==========
    
    @staticmethod
    def _build_quick_card(**kwargs) -> Dict[str, Any]:
        """Compact definition card - minimal, focused"""
        mentor_content = kwargs.get('mentor_content', '')
        concept_name = kwargs.get('concept_name', 'Concept')
        
        return {
            'default_view': {
                'greeting': f"Quick definition of {concept_name} 📖",
                'quick_summary': mentor_content[:200] + '...' if len(mentor_content) > 200 else mentor_content,
                'key_insight': mentor_content.split('.')[0] + '.' if '.' in mentor_content else mentor_content[:100],
                'main_content': None,  # Suppress main content for quick card
                'metaphor': None
            },
            'progressive_sections': {
                'full_definition': {
                    'title': '📚 Complete Definition',
                    'content': mentor_content,
                    'expandable': True
                }
            },
            'render_directives': {
                'suppress_main_content': True,
                'suppress_metaphor': True,
                'compact_mode': True
            }
        }
    
    @staticmethod
    def _build_expanded_definition(**kwargs) -> Dict[str, Any]:
        """Full definition with examples"""
        mentor_content = kwargs.get('mentor_content', '')
        professor_content = kwargs.get('professor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Here\'s a complete definition with examples 🎯',
                'quick_summary': mentor_content[:150],
                'key_insight': professor_content.split('.')[0] + '.' if '.' in professor_content else professor_content[:100],
                'main_content': {
                    'title': 'Definition & Examples',
                    'content': mentor_content,
                    'key_insight': professor_content[:200]
                },
                'metaphor': {
                    'text': mentor_content[:200],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {
                'examples': {
                    'title': '💡 Real Examples',
                    'content': professor_content,
                    'expandable': True
                }
            },
            'render_directives': {}
        }
    
    @staticmethod
    def _build_visual_first(**kwargs) -> Dict[str, Any]:
        """Visual prominently displayed, text below"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Visual explanation first! 👀',
                'quick_summary': '',
                'key_insight': mentor_content[:150],
                'main_content': {
                    'title': 'Explanation',
                    'content': mentor_content,
                    'key_insight': None
                },
                'metaphor': {
                    'text': mentor_content[:200],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {},
            'render_directives': {
                'prefer_visual_first': True,
                'suppress_metaphor': False
            }
        }
    
    @staticmethod
    def _build_story_definition(**kwargs) -> Dict[str, Any]:
        """Definition wrapped in a story"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Let me tell you a story about this concept 📖',
                'quick_summary': mentor_content,
                'key_insight': None,
                'main_content': {
                    'title': 'The Story',
                    'content': mentor_content,
                    'key_insight': None
                },
                'metaphor': {
                    'text': mentor_content[:250],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {
                'formal_definition': {
                    'title': '📚 Formal Definition',
                    'content': kwargs.get('professor_content', ''),
                    'expandable': True
                }
            },
            'render_directives': {
                'story_mode': True
            }
        }
    
    # ========== CONCEPT EXPLANATION TEMPLATES ==========
    
    @staticmethod
    def _build_layered_reveal(**kwargs) -> Dict[str, Any]:
        """Progressive disclosure (current default)"""
        mentor_content = kwargs.get('mentor_content', '')
        professor_content = kwargs.get('professor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Hey! Let me help you understand this concept. 👋',
                'quick_summary': mentor_content[:150],
                'key_insight': professor_content.split('.')[0] + '.' if '.' in professor_content else professor_content[:100],
                'main_content': {
                    'title': '📚 Detailed Explanation',
                    'content': mentor_content,
                    'key_insight': professor_content[:200]
                },
                'metaphor': {
                    'text': mentor_content[:200],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {
                'intuition': {
                    'title': '🎯 Intuitive Understanding',
                    'content': mentor_content,
                    'metaphor': kwargs.get('metaphor_used', 'general'),
                    'expandable': True
                },
                'formal_explanation': {
                    'title': '📚 Formal Explanation',
                    'content': professor_content,
                    'structure': 'step_by_step',
                    'expandable': True
                }
            },
            'render_directives': {}
        }
    
    @staticmethod
    def _build_story_journey(**kwargs) -> Dict[str, Any]:
        """Concept explained as a journey/story"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Let\'s go on a learning journey together! 🚀',
                'quick_summary': mentor_content[:200],
                'key_insight': None,
                'main_content': {
                    'title': 'The Journey',
                    'content': mentor_content,
                    'key_insight': None
                },
                'metaphor': {
                    'text': mentor_content[:250],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {
                'next_stop': {
                    'title': '📍 Next Stop',
                    'content': kwargs.get('professor_content', ''),
                    'expandable': True
                }
            },
            'render_directives': {
                'story_mode': True,
                'journey_metaphor': True
            }
        }
    
    @staticmethod
    def _build_visual_anchor(**kwargs) -> Dict[str, Any]:
        """Visual is the anchor, text supports it"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Visual learning mode activated! 🎨',
                'quick_summary': '',
                'key_insight': mentor_content[:150],
                'main_content': {
                    'title': 'Explanation',
                    'content': mentor_content,
                    'key_insight': None
                },
                'metaphor': {
                    'text': mentor_content[:200],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {},
            'render_directives': {
                'visual_anchor_mode': True,
                'prefer_visual_first': True
            }
        }
    
    @staticmethod
    def _build_conversational(**kwargs) -> Dict[str, Any]:
        """Chat-like, less structured, more natural"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Sure! Here\'s how I think about it 💭',
                'quick_summary': mentor_content,
                'key_insight': None,
                'main_content': None,
                'metaphor': None
            },
            'progressive_sections': {
                'more_details': {
                    'title': 'Want more details?',
                    'content': kwargs.get('professor_content', ''),
                    'expandable': True
                }
            },
            'render_directives': {
                'conversational_mode': True,
                'suppress_main_content': True,
                'suppress_metaphor': True,
                'minimal_structure': True
            }
        }
    
    @staticmethod
    def _build_exam_focused(**kwargs) -> Dict[str, Any]:
        """Exam tips and strategies prominently featured"""
        mentor_content = kwargs.get('mentor_content', '')
        professor_content = kwargs.get('professor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Exam-focused explanation! 📝',
                'quick_summary': mentor_content[:150],
                'key_insight': '💡 Exam Tip: ' + (professor_content[:150] if professor_content else mentor_content[:150]),
                'main_content': {
                    'title': '📚 Concept Explanation',
                    'content': mentor_content,
                    'key_insight': None
                },
                'metaphor': {
                    'text': mentor_content[:200],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {
                'exam_strategies': {
                    'title': '🎯 Exam Strategies',
                    'content': professor_content,
                    'expandable': True
                },
                'common_mistakes': {
                    'title': '⚠️ Common Mistakes',
                    'content': 'Students often confuse this with...',
                    'expandable': True
                }
            },
            'render_directives': {
                'exam_mode': True,
                'highlight_exam_tips': True
            }
        }
    
    @staticmethod
    def _build_analogy_heavy(**kwargs) -> Dict[str, Any]:
        """Multiple analogies and comparisons"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Let me explain this with multiple analogies! 🎭',
                'quick_summary': mentor_content[:200],
                'key_insight': None,
                'main_content': {
                    'title': 'Analogies & Comparisons',
                    'content': mentor_content,
                    'key_insight': None
                },
                'metaphor': {
                    'text': mentor_content[:250],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {
                'more_analogies': {
                    'title': '🔄 More Analogies',
                    'content': kwargs.get('professor_content', ''),
                    'expandable': True
                }
            },
            'render_directives': {
                'analogy_mode': True
            }
        }
    
    # ========== COMPARISON TEMPLATES ==========
    
    @staticmethod
    def _build_side_by_side(**kwargs) -> Dict[str, Any]:
        """Side-by-side comparison table"""
        return {
            'default_view': {
                'greeting': 'Let\'s compare side by side! ⚖️',
                'quick_summary': kwargs.get('mentor_content', '')[:150],
                'key_insight': None,
                'main_content': {
                    'title': 'Comparison',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'prefer_compare_layout': True,
                'compare_mode': True
            }
        }
    
    @staticmethod
    def _build_before_after(**kwargs) -> Dict[str, Any]:
        """Sequential before/after comparison"""
        return {
            'default_view': {
                'greeting': 'Before vs After comparison! 🔄',
                'quick_summary': kwargs.get('mentor_content', '')[:150],
                'key_insight': None,
                'main_content': {
                    'title': 'Before → After',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'before_after_mode': True
            }
        }
    
    @staticmethod
    def _build_visual_comparison(**kwargs) -> Dict[str, Any]:
        """Visual comparison grid"""
        return {
            'default_view': {
                'greeting': 'Visual comparison! 👀',
                'quick_summary': '',
                'key_insight': None,
                'main_content': {
                    'title': 'Visual Comparison',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'visual_comparison_mode': True,
                'prefer_visual_first': True
            }
        }
    
    @staticmethod
    def _build_narrative_compare(**kwargs) -> Dict[str, Any]:
        """Story-based comparison"""
        return {
            'default_view': {
                'greeting': 'Let me tell you a comparison story! 📖',
                'quick_summary': kwargs.get('mentor_content', '')[:200],
                'key_insight': None,
                'main_content': {
                    'title': 'The Comparison Story',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': {
                    'text': kwargs.get('mentor_content', '')[:250],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {},
            'render_directives': {
                'story_mode': True,
                'narrative_compare': True
            }
        }
    
    # ========== DEEP DIVE TEMPLATES ==========
    
    @staticmethod
    def _build_step_by_step(**kwargs) -> Dict[str, Any]:
        """Detailed step-by-step"""
        professor_content = kwargs.get('professor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Deep dive: Step by step! 🔬',
                'quick_summary': kwargs.get('mentor_content', '')[:150],
                'key_insight': None,
                'main_content': {
                    'title': 'Step-by-Step Deep Dive',
                    'content': professor_content,
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {
                'detailed_steps': {
                    'title': '📋 Detailed Steps',
                    'content': professor_content,
                    'expandable': False  # Always visible for deep dive
                }
            },
            'render_directives': {
                'deep_dive_mode': True,
                'step_by_step_mode': True
            }
        }
    
    @staticmethod
    def _build_reasoning_path(**kwargs) -> Dict[str, Any]:
        """Logical reasoning flow"""
        professor_content = kwargs.get('professor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Let\'s trace the reasoning path! 🧭',
                'quick_summary': kwargs.get('mentor_content', '')[:150],
                'key_insight': None,
                'main_content': {
                    'title': 'Reasoning Path',
                    'content': professor_content,
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'reasoning_path_mode': True
            }
        }
    
    @staticmethod
    def _build_visual_sequence(**kwargs) -> Dict[str, Any]:
        """Visual step sequence"""
        return {
            'default_view': {
                'greeting': 'Visual step sequence! 🎬',
                'quick_summary': '',
                'key_insight': None,
                'main_content': {
                    'title': 'Visual Sequence',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'visual_sequence_mode': True,
                'prefer_visual_first': True
            }
        }
    
    @staticmethod
    def _build_interactive_proof(**kwargs) -> Dict[str, Any]:
        """Interactive derivation"""
        return {
            'default_view': {
                'greeting': 'Interactive proof mode! 🧮',
                'quick_summary': kwargs.get('mentor_content', '')[:150],
                'key_insight': None,
                'main_content': {
                    'title': 'Interactive Proof',
                    'content': kwargs.get('professor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'interactive_mode': True
            }
        }
    
    # ========== APPLICATION TEMPLATES ==========
    
    @staticmethod
    def _build_real_world_story(**kwargs) -> Dict[str, Any]:
        """Real-world scenario story"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Real-world story time! 🌍',
                'quick_summary': mentor_content[:200],
                'key_insight': None,
                'main_content': {
                    'title': 'Real-World Story',
                    'content': mentor_content,
                    'key_insight': None
                },
                'metaphor': {
                    'text': mentor_content[:250],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {},
            'render_directives': {
                'real_world_mode': True,
                'story_mode': True
            }
        }
    
    @staticmethod
    def _build_hands_on(**kwargs) -> Dict[str, Any]:
        """Practical hands-on steps"""
        return {
            'default_view': {
                'greeting': 'Hands-on practical guide! ✋',
                'quick_summary': kwargs.get('mentor_content', '')[:150],
                'key_insight': None,
                'main_content': {
                    'title': 'Practical Steps',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {
                'action_steps': {
                    'title': '🎯 Action Steps',
                    'content': kwargs.get('professor_content', ''),
                    'expandable': True
                }
            },
            'render_directives': {
                'hands_on_mode': True
            }
        }
    
    @staticmethod
    def _build_visual_scenario(**kwargs) -> Dict[str, Any]:
        """Visual scenario"""
        return {
            'default_view': {
                'greeting': 'Visual scenario! 🎨',
                'quick_summary': '',
                'key_insight': None,
                'main_content': {
                    'title': 'Scenario',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'visual_scenario_mode': True,
                'prefer_visual_first': True
            }
        }
    
    @staticmethod
    def _build_case_study(**kwargs) -> Dict[str, Any]:
        """Case study format"""
        return {
            'default_view': {
                'greeting': 'Case study format! 📊',
                'quick_summary': kwargs.get('mentor_content', '')[:150],
                'key_insight': None,
                'main_content': {
                    'title': 'Case Study',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {
                'analysis': {
                    'title': '📊 Analysis',
                    'content': kwargs.get('professor_content', ''),
                    'expandable': True
                }
            },
            'render_directives': {
                'case_study_mode': True
            }
        }
    
    # ========== CLARIFICATION TEMPLATES ==========
    
    @staticmethod
    def _build_fresh_angle(**kwargs) -> Dict[str, Any]:
        """Different perspective"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Let me explain from a fresh angle! 🔄',
                'quick_summary': mentor_content[:200],
                'key_insight': None,
                'main_content': {
                    'title': 'Fresh Perspective',
                    'content': mentor_content,
                    'key_insight': None
                },
                'metaphor': {
                    'text': mentor_content[:250],
                    'category': kwargs.get('metaphor_used', 'general')
                }
            },
            'progressive_sections': {},
            'render_directives': {
                'fresh_angle_mode': True
            }
        }
    
    @staticmethod
    def _build_simplified(**kwargs) -> Dict[str, Any]:
        """Simplified version"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Simplified explanation! ✨',
                'quick_summary': mentor_content,
                'key_insight': None,
                'main_content': None,
                'metaphor': None
            },
            'progressive_sections': {
                'detailed_version': {
                    'title': 'Want more detail?',
                    'content': kwargs.get('professor_content', ''),
                    'expandable': True
                }
            },
            'render_directives': {
                'simplified_mode': True,
                'suppress_main_content': True
            }
        }
    
    @staticmethod
    def _build_visual_clarify(**kwargs) -> Dict[str, Any]:
        """Visual clarification"""
        return {
            'default_view': {
                'greeting': 'Visual clarification! 👀',
                'quick_summary': '',
                'key_insight': kwargs.get('mentor_content', '')[:150],
                'main_content': {
                    'title': 'Clarification',
                    'content': kwargs.get('mentor_content', ''),
                    'key_insight': None
                },
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'visual_clarify_mode': True,
                'prefer_visual_first': True
            }
        }
    
    @staticmethod
    def _build_quick_recap(**kwargs) -> Dict[str, Any]:
        """Quick recap format"""
        mentor_content = kwargs.get('mentor_content', '')
        
        return {
            'default_view': {
                'greeting': 'Quick recap! ⚡',
                'quick_summary': mentor_content,
                'key_insight': None,
                'main_content': None,
                'metaphor': None
            },
            'progressive_sections': {},
            'render_directives': {
                'recap_mode': True,
                'suppress_main_content': True,
                'suppress_metaphor': True,
                'compact_mode': True
            }
        }



