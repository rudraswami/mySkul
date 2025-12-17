"""
Response Section Variety
Varies section titles and structure to avoid repetitive "INTUITIVE UNDERSTANDING" blocks
"""
import random
from typing import Dict, List, Tuple


class SectionTitleVariety:
    """Generates varied section titles instead of fixed ones"""
    
    @staticmethod
    def get_varied_sections(template_style: str, intent: str) -> Dict[str, Dict]:
        """
        Get varied section titles and structure based on template style
        
        Returns dict with section configurations
        """
        # Map template styles to section title variations
        section_variations = {
            "excited_discovery": {
                "main_title": random.choice([
                    "✨ The Cool Part",
                    "🔥 Here's What's Interesting",
                    "💡 The Aha Moment",
                    "⚡ Quick Take"
                ]),
                "expandable_title": random.choice([
                    "🤔 Want More Details?",
                    "🧠 Going Deeper",
                    "📚 The Full Story",
                    "🔬 Under the Hood"
                ]),
                "show_metaphor_separately": False  # Integrate into main content
            },
            
            "calm_walkthrough": {
                "main_title": None,  # Don't force a title - let content speak
                "expandable_title": random.choice([
                    "🔍 Looking Closer",
                    "⚙️ How It Works",
                    "📐 The Mechanics"
                ]),
                "show_metaphor_separately": True
            },
            
            "questioning_socratic": {
                "main_title": random.choice([
                    "❓ Think About This",
                    "🤔 Questions to Consider",
                    "💭 Let's Explore",
                    "🎓 Guided Discovery"
                ]),
                "expandable_title": random.choice([
                    "💡 Answers & Insights",
                    "🔑 The Key Ideas",
                    "✅ Putting It Together",
                    "🧩 Complete Picture"
                ]),
                "show_metaphor_separately": False
            },
            
            "story_narrative": {
                "main_title": random.choice([
                    "📖 The Story",
                    "🎭 Scene by Scene",
                    "🌟 The Journey",
                    "🗺️ The Adventure"
                ]),
                "expandable_title": random.choice([
                    "🔬 The Science Behind It",
                    "📚 Technical Details",
                    "🎓 Academic Perspective",
                    "📊 Formal Explanation"
                ]),
                "show_metaphor_separately": False  # Story IS the metaphor
            },
            
            "relatable_everyday": {
                "main_title": random.choice([
                    "🏠 In Daily Life",
                    "👀 You've Seen This Before",
                    "🌍 All Around You",
                    "🎯 Real World Connection"
                ]),
                "expandable_title": random.choice([
                    "🔬 The Science Part",
                    "📚 Technical Explanation",
                    "🧠 Deeper Understanding",
                    "📖 More Details"
                ]),
                "show_metaphor_separately": False
            },
            
            "exam_panic_mode": {
                "main_title": random.choice([
                    "⚡ Exam Focus",
                    "🎯 What Matters Most",
                    "⏰ Quick Essentials",
                    "📝 Test Strategy"
                ]),
                "expandable_title": random.choice([
                    "📚 Optional Deep Dive",
                    "🔍 If You Have Time",
                    "🧠 Extra Context",
                    "💡 Bonus Insights"
                ]),
                "show_metaphor_separately": False,
                "highlight_formulas": True
            },
            
            "build_on_previous": {
                "main_title": random.choice([
                    "🔗 Building on What You Know",
                    "📈 Next Level",
                    "🪜 One Step Further",
                    "🧩 Adding the Missing Piece"
                ]),
                "expandable_title": random.choice([
                    "🔍 Complete Picture",
                    "📚 Full Context",
                    "🧠 Advanced Details",
                    "💡 Going Further"
                ]),
                "show_metaphor_separately": True
            },
            
            "quick_intuition": {
                "main_title": random.choice([
                    "💡 The Core Idea",
                    "⚡ Quick Grasp",
                    "🎯 Essential Concept",
                    "✨ The Key Insight"
                ]),
                "expandable_title": None,  # No expandable for quick intuition
                "show_metaphor_separately": False,
                "compact": True
            },
            
            "visual_thinker": {
                "main_title": random.choice([
                    "👁️ Mental Picture",
                    "🎨 Visualize This",
                    "🖼️ The Visual",
                    "🌈 Picture It"
                ]),
                "expandable_title": random.choice([
                    "📖 Verbal Explanation",
                    "📚 Text Version",
                    "🔤 In Words",
                    "📝 Description"
                ]),
                "show_metaphor_separately": False,
                "visual_first": True
            },
            
            "playful_curious": {
                "main_title": random.choice([
                    "🎮 Let's Play With This",
                    "🧪 Experimenting",
                    "🎲 What If...",
                    "🔬 Discovery Time"
                ]),
                "expandable_title": random.choice([
                    "📚 The Formal Stuff",
                    "🎓 Academic Version",
                    "📖 Technical Details",
                    "🔍 More Rigorous"
                ]),
                "show_metaphor_separately": False
            }
        }
        
        # Default fallback
        default = {
            "main_title": "📚 Explanation",
            "expandable_title": "🔍 More Details",
            "show_metaphor_separately": True
        }
        
        return section_variations.get(template_style, default)
    
    @staticmethod
    def should_show_key_insight_separately(template_style: str) -> bool:
        """
        Determine if KEY INSIGHT should be shown as separate yellow box
        or integrated into content
        """
        # Only show separate key insight for formal/exam-focused styles
        separate_styles = [
            "exam_panic_mode",
            "calm_walkthrough",
            "build_on_previous"
        ]
        
        return template_style in separate_styles
    
    @staticmethod
    def get_greeting_variation(template_style: str, name: str = "") -> str:
        """Get varied greeting based on template style"""
        greetings = {
            "excited_discovery": random.choice([
                f"Hey {name}! Okay so this is actually pretty cool... 🔥",
                f"Dude! I just realized something about this... 💡",
                f"Alright {name}, here's the interesting part... ✨"
            ]) if name else random.choice([
                "Okay so this is actually pretty cool... 🔥",
                "Dude! I just realized something... 💡",
                "Alright, here's the interesting part... ✨"
            ]),
            
            "calm_walkthrough": random.choice([
                f"Alright {name}, let's take this step by step 🧭",
                f"Okay {name}, let me break this down for you 📖",
                f"Hey {name}, let's walk through this together 🌊"
            ]) if name else random.choice([
                "Alright, let's take this step by step 🧭",
                "Okay, let me break this down 📖",
                "Let's walk through this together 🌊"
            ]),
            
            "questioning_socratic": random.choice([
                f"Hey {name}, let me ask you something first... 🤔",
                f"Okay {name}, think about this... 💭",
                f"{name}, what do you think about... ❓"
            ]) if name else random.choice([
                "Let me ask you something first... 🤔",
                "Okay, think about this... 💭",
                "What do you think about... ❓"
            ]),
            
            "story_narrative": random.choice([
                f"Alright {name}, imagine this scenario... 📖",
                f"Let me tell you a story about this... 🎭",
                f"Picture this, {name}... 🌟"
            ]) if name else random.choice([
                "Alright, imagine this scenario... 📖",
                "Let me tell you a story... 🎭",
                "Picture this... 🌟"
            ]),
            
            "relatable_everyday": random.choice([
                f"You know what {name}, you see this every day... 🏠",
                f"Hey {name}, this is all around you... 👀",
                f"{name}, remember when you... 🌍"
            ]) if name else random.choice([
                "You know what, you see this every day... 🏠",
                "Hey, this is all around you... 👀",
                "Remember when you... 🌍"
            ]),
            
            "exam_panic_mode": random.choice([
                f"Alright {name}, exam mode - here's what matters... ⚡",
                f"{name}, quick focus on this... 🎯",
                f"Okay {name}, test perspective... 📝"
            ]) if name else random.choice([
                "Alright, exam mode - here's what matters... ⚡",
                "Quick focus on this... 🎯",
                "Okay, test perspective... 📝"
            ]),
            
            "quick_intuition": random.choice([
                f"Here's the one-line version, {name}... 💡",
                f"{name}, the core idea is... ⚡",
                f"Quick intuition for you... 🎯"
            ]) if name else random.choice([
                "Here's the one-line version... 💡",
                "The core idea is... ⚡",
                "Quick intuition... 🎯"
            ]),
            
            "visual_thinker": random.choice([
                f"Okay {name}, picture this in your mind... 👁️",
                f"{name}, visualize it like this... 🎨",
                f"Close your eyes and imagine... 🖼️"
            ]) if name else random.choice([
                "Okay, picture this in your mind... 👁️",
                "Visualize it like this... 🎨",
                "Close your eyes and imagine... 🖼️"
            ]),
            
            "playful_curious": random.choice([
                f"Yo {name}, let's mess around with this... 🎮",
                f"{name}, this is kinda interesting actually... 🧪",
                f"What if we tried this {name}... 🎲"
            ]) if name else random.choice([
                "Yo, let's mess around with this... 🎮",
                "This is kinda interesting actually... 🧪",
                "What if we tried this... 🎲"
            ])
        }
        
        return greetings.get(template_style, f"Hey{' ' + name if name else ''}! Let me help you with this 👋")



