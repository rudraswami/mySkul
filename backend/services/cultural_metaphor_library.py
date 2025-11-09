"""
Cultural Metaphor Library for Indian Students
Provides culturally relevant metaphors and visual patterns
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import random

class MetaphorCategory(Enum):
    CRICKET = "cricket"
    BOLLYWOOD = "bollywood"
    COOKING = "cooking"
    TRAINS = "trains"
    FESTIVALS = "festivals"
    GAMING = "gaming"
    FAMILY = "family"
    SCHOOL = "school"
    TRAFFIC = "traffic"
    STREET_FOOD = "street_food"

class CulturalMetaphorLibrary:
    """Library of Indian cultural metaphors for teaching concepts"""

    def __init__(self):
        self.metaphors = self._load_metaphors()
        self.visual_elements = self._load_visual_elements()

    def _load_metaphors(self) -> Dict[str, Dict[str, Any]]:
        """Load cultural metaphor templates"""
        return {
            # CRICKET METAPHORS
            "process_flow": {
                "cricket": {
                    "template": "Think of {concept} like a cricket match - {stage1} is the powerplay, {stage2} is building the innings, and {stage3} is the final slog overs",
                    "visual_elements": ["cricket_pitch", "batsman", "bowler", "fielders"],
                    "animations": ["ball_trajectory", "run_between_wickets", "boundary_hit"],
                    "examples": {
                        "photosynthesis": "Sunlight is the bowler, chlorophyll is the batsman, and glucose is the runs scored",
                        "water_cycle": "Water evaporating is like the ball being hit, clouds are fielders catching it, rain is throwing it back"
                    }
                }
            },

            # COOKING METAPHORS
            "transformation": {
                "cooking": {
                    "template": "Just like making {dish}, {input} needs {process} to become {output}",
                    "visual_elements": ["kadhai", "spices", "flame", "ingredients"],
                    "animations": ["stirring", "sizzling", "steam_rising", "spice_adding"],
                    "examples": {
                        "chemical_reaction": "Like making chai - water + tea leaves + heat = perfect chai",
                        "active_passive": "Like dosa batter fermenting - the batter (subject) ferments (verb) overnight"
                    }
                }
            },

            # TRAIN METAPHORS
            "sequence": {
                "trains": {
                    "template": "Imagine {concept} as a train journey from {start} to {end}, with stops at {stages}",
                    "visual_elements": ["train", "stations", "tracks", "signals"],
                    "animations": ["train_moving", "passengers_boarding", "signal_changing"],
                    "examples": {
                        "digestion": "Food travels like a train through stations - mouth (Mumbai), stomach (Pune), intestines (Bangalore)",
                        "electron_flow": "Electrons are passengers moving through circuit stations"
                    }
                }
            },

            # BOLLYWOOD METAPHORS
            "drama": {
                "bollywood": {
                    "template": "This is like a Bollywood movie where {hero} must {action} to {result}",
                    "visual_elements": ["hero", "villain", "stage", "spotlight"],
                    "animations": ["dramatic_entry", "dance_move", "fight_sequence"],
                    "examples": {
                        "immune_system": "White blood cells are the heroes fighting villain bacteria",
                        "oxidation": "Oxygen is the villain stealing electrons from the hero metal"
                    }
                }
            },

            # FESTIVAL METAPHORS
            "cycles": {
                "festivals": {
                    "template": "Like how {festival} comes every year, {concept} repeats in a cycle",
                    "visual_elements": ["diya", "rangoli", "fireworks", "decorations"],
                    "animations": ["lighting_diya", "creating_rangoli", "bursting_crackers"],
                    "examples": {
                        "seasons": "Like Diwali marks winter's arrival, Earth's tilt creates seasonal festivals",
                        "cell_division": "Cells celebrate division like we celebrate Holi - colorful and multiplying"
                    }
                }
            },

            # GAMING METAPHORS
            "levels": {
                "gaming": {
                    "template": "{concept} is like leveling up in a game - {stage1} is tutorial, {stage2} is main quest, {stage3} is boss battle",
                    "visual_elements": ["avatar", "health_bar", "power_ups", "obstacles"],
                    "animations": ["jumping", "collecting_coins", "power_up_effect"],
                    "examples": {
                        "energy_levels": "Electrons jump energy levels like Mario jumping platforms",
                        "food_chain": "Each level up is eating to gain XP - grass→deer→tiger"
                    }
                }
            },

            # TRAFFIC METAPHORS
            "flow": {
                "traffic": {
                    "template": "Think of {concept} like traffic at {location} - {element1} are vehicles, {element2} are signals",
                    "visual_elements": ["auto_rickshaw", "traffic_light", "flyover", "zebra_crossing"],
                    "animations": ["vehicles_moving", "signal_change", "traffic_jam", "smooth_flow"],
                    "examples": {
                        "blood_circulation": "Blood cells are autos in Mumbai traffic, heart is the main signal",
                        "data_flow": "Internet packets navigate like vehicles through Bangalore traffic"
                    }
                }
            },

            # FAMILY METAPHORS
            "hierarchy": {
                "family": {
                    "template": "{concept} is organized like a joint family - {top} is like grandparents, {middle} like parents, {bottom} like children",
                    "visual_elements": ["family_tree", "elders", "siblings", "cousins"],
                    "animations": ["gathering", "blessing", "celebration"],
                    "examples": {
                        "taxonomy": "Kingdom is the grandfather, Species is the youngest grandchild",
                        "corporate_structure": "CEO is family head, managers are uncles, employees are cousins"
                    }
                }
            },

            # STREET FOOD METAPHORS
            "combination": {
                "street_food": {
                    "template": "Like making {dish}, you need to combine {ingredients} in the right {proportion}",
                    "visual_elements": ["pani_puri", "chaat_plate", "vendor_cart", "chutneys"],
                    "animations": ["assembling_puri", "adding_chutney", "mixing_ingredients"],
                    "examples": {
                        "chemical_formula": "H₂O is like the perfect pani puri - 2 parts pani, 1 part puri",
                        "color_mixing": "Primary colors mix like chutneys - green + red = brown tamarind"
                    }
                }
            },

            # SCHOOL METAPHORS
            "learning": {
                "school": {
                    "template": "{concept} is like school assembly - {part1} is prayer, {part2} is announcement, {part3} is dispersal",
                    "visual_elements": ["classroom", "blackboard", "students", "teacher"],
                    "animations": ["writing_on_board", "raising_hand", "bell_ringing"],
                    "examples": {
                        "algorithm": "Step-by-step like morning assembly routine",
                        "essay_structure": "Introduction is assembly, body is classes, conclusion is final bell"
                    }
                }
            }
        }

    def _load_visual_elements(self) -> Dict[str, Dict[str, Any]]:
        """Load visual element specifications for each metaphor category"""
        return {
            "cricket": {
                "colors": {
                    "primary": "#1e40af",  # Blue (Indian jersey)
                    "secondary": "#ea580c",  # Orange
                    "accent": "#16a34a",  # Green (field)
                },
                "icons": {
                    "bat": "🏏",
                    "ball": "⚪",
                    "wicket": "🥅",
                    "trophy": "🏆"
                },
                "shapes": {
                    "pitch": "rectangle",
                    "boundary": "oval",
                    "crease": "line"
                }
            },

            "cooking": {
                "colors": {
                    "primary": "#dc2626",  # Red (spice/heat)
                    "secondary": "#f59e0b",  # Yellow (turmeric)
                    "accent": "#84cc16",  # Green (coriander)
                },
                "icons": {
                    "pot": "🍲",
                    "spice": "🌶️",
                    "fire": "🔥",
                    "dish": "🍛"
                },
                "shapes": {
                    "kadhai": "arc",
                    "flame": "triangle",
                    "steam": "wavy_lines"
                }
            },

            "trains": {
                "colors": {
                    "primary": "#0891b2",  # Cyan (Indian Railways)
                    "secondary": "#f97316",  # Orange
                    "accent": "#6b7280",  # Gray (tracks)
                },
                "icons": {
                    "train": "🚂",
                    "station": "🚉",
                    "ticket": "🎫",
                    "signal": "🚦"
                },
                "shapes": {
                    "track": "parallel_lines",
                    "carriage": "rectangle",
                    "platform": "rectangle"
                }
            },

            "bollywood": {
                "colors": {
                    "primary": "#c026d3",  # Fuchsia
                    "secondary": "#facc15",  # Yellow (spotlight)
                    "accent": "#ec4899",  # Pink
                },
                "icons": {
                    "star": "⭐",
                    "camera": "🎬",
                    "music": "🎵",
                    "dance": "💃"
                },
                "shapes": {
                    "spotlight": "cone",
                    "stage": "rectangle",
                    "curtain": "wavy_rectangle"
                }
            },

            "festivals": {
                "colors": {
                    "primary": "#f59e0b",  # Amber (Diwali)
                    "secondary": "#a855f7",  # Purple (Holi)
                    "accent": "#ef4444",  # Red
                },
                "icons": {
                    "diya": "🪔",
                    "firework": "🎆",
                    "sweet": "🍬",
                    "rangoli": "🎨"
                },
                "shapes": {
                    "rangoli": "mandala",
                    "diya": "teardrop",
                    "firework": "starburst"
                }
            }
        }

    def get_metaphor(self, concept: str, category: Optional[MetaphorCategory] = None) -> Dict[str, Any]:
        """Get appropriate metaphor for a concept"""

        # Map concepts to metaphor patterns
        concept_mapping = {
            "process": ["cricket", "cooking", "trains"],
            "transformation": ["cooking", "bollywood", "festivals"],
            "flow": ["traffic", "trains", "cricket"],
            "hierarchy": ["family", "school", "gaming"],
            "cycle": ["festivals", "trains", "traffic"],
            "combination": ["street_food", "cooking", "festivals"]
        }

        # Detect concept type from keywords
        concept_lower = concept.lower()

        if any(word in concept_lower for word in ["process", "steps", "stages", "sequence"]):
            suitable_categories = concept_mapping["process"]
        elif any(word in concept_lower for word in ["change", "transform", "convert", "reaction"]):
            suitable_categories = concept_mapping["transformation"]
        elif any(word in concept_lower for word in ["flow", "current", "stream", "movement"]):
            suitable_categories = concept_mapping["flow"]
        elif any(word in concept_lower for word in ["hierarchy", "levels", "structure", "organization"]):
            suitable_categories = concept_mapping["hierarchy"]
        elif any(word in concept_lower for word in ["cycle", "repeat", "circular", "recurring"]):
            suitable_categories = concept_mapping["cycle"]
        elif any(word in concept_lower for word in ["mix", "combine", "blend", "formula"]):
            suitable_categories = concept_mapping["combination"]
        else:
            suitable_categories = ["cricket", "cooking", "trains"]  # Default fallback

        # Select category
        if category:
            selected_category = category.value
        else:
            selected_category = random.choice(suitable_categories)

        # Find appropriate metaphor pattern
        for pattern_type, patterns in self.metaphors.items():
            if selected_category in patterns:
                metaphor = patterns[selected_category].copy()
                metaphor["category"] = selected_category
                metaphor["visual_style"] = self.visual_elements.get(selected_category, {})
                return metaphor

        # Fallback to cricket (most universal)
        return {
            "category": "cricket",
            "template": f"{concept} is like a cricket match",
            "visual_elements": ["cricket_pitch", "players"],
            "animations": ["ball_movement"],
            "visual_style": self.visual_elements["cricket"]
        }

    def get_visual_style(self, category: str) -> Dict[str, Any]:
        """Get visual styling for a metaphor category"""
        return self.visual_elements.get(category, self.visual_elements["cricket"])

    def get_animation_sequence(self, concept: str, metaphor_category: str) -> List[Dict[str, Any]]:
        """Generate animation sequence based on concept and metaphor"""

        sequences = {
            "cricket": [
                {"type": "scene_setup", "elements": ["pitch", "players"], "duration": 1000},
                {"type": "ball_bowl", "from": "bowler", "to": "batsman", "duration": 800},
                {"type": "bat_swing", "power": 0.8, "duration": 400},
                {"type": "ball_travel", "trajectory": "parabola", "duration": 1200},
                {"type": "celebration", "elements": ["crowd_cheer"], "duration": 800}
            ],

            "cooking": [
                {"type": "ingredient_add", "items": ["base"], "duration": 600},
                {"type": "heat_apply", "intensity": "medium", "duration": 800},
                {"type": "stir", "speed": "moderate", "duration": 1000},
                {"type": "spice_add", "items": ["masala"], "duration": 600},
                {"type": "steam_rise", "density": 0.6, "duration": 800},
                {"type": "serve", "presentation": "plate", "duration": 600}
            ],

            "trains": [
                {"type": "station_arrive", "platform": 1, "duration": 1000},
                {"type": "door_open", "duration": 400},
                {"type": "passenger_board", "count": "many", "duration": 800},
                {"type": "signal_green", "duration": 400},
                {"type": "train_depart", "speed": "gradual", "duration": 1200},
                {"type": "journey", "landscape": "varied", "duration": 1600}
            ]
        }

        return sequences.get(metaphor_category, sequences["cricket"])

    def get_micro_interactions(self, category: str) -> List[Dict[str, Any]]:
        """Get micro-interaction points for engagement"""

        interactions = {
            "cricket": [
                {"type": "tap", "prompt": "Tap when the bowler should release!", "timing": 2000},
                {"type": "swipe", "prompt": "Swipe to hit a six!", "timing": 3000},
                {"type": "hold", "prompt": "Hold to build power!", "timing": 4000}
            ],

            "cooking": [
                {"type": "drag", "prompt": "Drag spices into the pot!", "timing": 1500},
                {"type": "circular", "prompt": "Stir the mixture!", "timing": 2500},
                {"type": "tap", "prompt": "Add the final ingredient!", "timing": 3500}
            ],

            "trains": [
                {"type": "tap", "prompt": "Ring the bell to depart!", "timing": 2000},
                {"type": "slide", "prompt": "Pull the chain to stop!", "timing": 4000},
                {"type": "tap", "prompt": "Punch your ticket!", "timing": 1000}
            ]
        }

        return interactions.get(category, [])

    def adapt_to_subject(self, metaphor: Dict[str, Any], subject: str) -> Dict[str, Any]:
        """Adapt metaphor to specific subject context"""

        subject_adaptations = {
            "physics": {
                "cricket": "forces and motion like cricket ball physics",
                "cooking": "heat transfer like cooking on a stove",
                "trains": "momentum and acceleration like train movement"
            },
            "chemistry": {
                "cricket": "reactions like team coordination",
                "cooking": "chemical changes like cooking transformations",
                "trains": "reaction rates like train schedules"
            },
            "biology": {
                "cricket": "systems working like a cricket team",
                "cooking": "digestion like food preparation",
                "trains": "circulation like train routes"
            },
            "mathematics": {
                "cricket": "statistics and probability in cricket",
                "cooking": "proportions and ratios in recipes",
                "trains": "distance, speed, and time calculations"
            },
            "english": {
                "cricket": "commentary and communication",
                "cooking": "recipe instructions as grammar",
                "trains": "journey narratives and timetables"
            }
        }

        if subject in subject_adaptations and metaphor.get("category") in subject_adaptations[subject]:
            metaphor["subject_context"] = subject_adaptations[subject][metaphor["category"]]

        return metaphor


# Global instance
cultural_library = CulturalMetaphorLibrary()


def get_culturally_relevant_metaphor(concept: str, subject: Optional[str] = None,
                                     preferred_category: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a culturally relevant metaphor for teaching a concept

    Args:
        concept: The concept to teach
        subject: The subject area (physics, chemistry, etc.)
        preferred_category: Preferred metaphor category (cricket, cooking, etc.)

    Returns:
        Complete metaphor with visual elements and animations
    """

    category = MetaphorCategory(preferred_category) if preferred_category else None
    metaphor = cultural_library.get_metaphor(concept, category)

    if subject:
        metaphor = cultural_library.adapt_to_subject(metaphor, subject)

    # Add animation sequence
    metaphor["animation_sequence"] = cultural_library.get_animation_sequence(
        concept, metaphor["category"]
    )

    # Add micro-interactions
    metaphor["interactions"] = cultural_library.get_micro_interactions(
        metaphor["category"]
    )

    return metaphor