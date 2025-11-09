"""
Grammar Visual Templates
Specific animated teaching templates for English grammar concepts
Returns plain dictionaries (not dataclass objects) for JSON serialization
"""

from typing import Dict, List, Any
import uuid


class GrammarVisualTemplates:
    """Pre-built visual templates for common grammar concepts"""

    @staticmethod
    def active_passive_voice() -> Dict[str, Any]:
        """
        Generate animated teaching visual for active vs passive voice
        Uses cooking metaphor for Indian students
        """

        stages = [
            # STAGE 1: Introduction
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 3000,
                "narration": "Let's understand active and passive voice using cooking! Think of it like making chai - who does the action matters!",
                "animations": [
                    {
                        "type": "scene_setup",
                        "elements": ["kitchen", "person", "chai_cup"],
                        "style": "warm_cooking",
                        "colors": {"primary": "#dc2626", "secondary": "#f59e0b"}
                    },
                    {
                        "type": "fade_in",
                        "target": "kitchen_scene",
                        "duration": 1000
                    }
                ],
                "interactions": None,
                "emphasis": "Active voice = WHO does the action is important!"
            },

            # STAGE 2: Active Voice
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 4000,
                "narration": "ACTIVE VOICE: 'Ravi makes chai.' Here, Ravi (the doer) is the HERO of the sentence - he's in the spotlight!",
                "animations": [
                    {"type": "split_screen_enter", "side": "left", "label": "ACTIVE VOICE"},
                    {"type": "character_spotlight", "character": "Ravi", "position": "left", "highlight": True, "duration": 1500},
                    {"type": "action_arrow", "from": "Ravi", "action": "makes", "to": "chai", "style": "bold_red", "duration": 1500},
                    {
                        "type": "sentence_build",
                        "words": ["Ravi", "makes", "chai"],
                        "highlights": {"Ravi": "subject", "makes": "verb", "chai": "object"},
                        "colors": {"subject": "#10b981", "verb": "#f59e0b", "object": "#6366f1"},
                        "duration": 1000
                    }
                ],
                "interactions": [{"type": "tap_to_continue", "prompt": "Tap when you see the doer clearly!"}],
                "emphasis": "Subject (Ravi) + Verb (makes) + Object (chai) = ACTIVE!"
            },

            # STAGE 3: Passive Voice
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 4000,
                "narration": "PASSIVE VOICE: 'Chai is made by Ravi.' Now chai (the object) is in the spotlight - the action happened TO it!",
                "animations": [
                    {"type": "split_screen_enter", "side": "right", "label": "PASSIVE VOICE"},
                    {"type": "object_spotlight", "object": "chai", "position": "right", "highlight": True, "duration": 1500},
                    {"type": "action_arrow_reverse", "from": "chai", "action": "is made by", "to": "Ravi", "style": "dashed_blue", "duration": 1500},
                    {
                        "type": "sentence_build",
                        "words": ["Chai", "is made", "by Ravi"],
                        "highlights": {"Chai": "object_now_subject", "is made": "passive_verb", "by Ravi": "doer_optional"},
                        "colors": {"object_now_subject": "#6366f1", "passive_verb": "#f59e0b", "doer_optional": "#9ca3af"},
                        "duration": 1000
                    }
                ],
                "interactions": [{"type": "tap_to_continue", "prompt": "Notice the chai is now first!"}],
                "emphasis": "Object becomes subject + 'be' verb + past participle + (by doer)"
            },

            # STAGE 4: Comparison + Quiz
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 5000,
                "narration": "See the difference? Active = Doer first. Passive = Action receiver first. Both say the same thing, just different focus!",
                "animations": [
                    {
                        "type": "comparison_arrows",
                        "left_sentence": "Ravi makes chai",
                        "right_sentence": "Chai is made by Ravi",
                        "connection_points": [
                            {"left": "Ravi", "right": "by Ravi", "label": "doer"},
                            {"left": "chai", "right": "Chai", "label": "object→subject"}
                        ],
                        "duration": 2000
                    },
                    {
                        "type": "transformation_morph",
                        "from": "Ravi makes chai",
                        "to": "Chai is made by Ravi",
                        "duration": 2000,
                        "style": "smooth_flow"
                    }
                ],
                "interactions": [
                    {
                        "type": "quiz",
                        "question": "Which voice puts the DOER in the spotlight?",
                        "options": ["Active Voice", "Passive Voice", "Both equally"],
                        "correct": 0,
                        "hint": "Think about which sentence starts with the person doing the action!",
                        "successMessage": "Perfect! Active voice makes the doer the hero!",
                        "errorMessage": "Not quite - in active voice, the DOER comes first!"
                    }
                ],
                "emphasis": "Same meaning, different focus! Choose based on what's more important."
            },

            # STAGE 5: Cricket Example
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 5000,
                "narration": "Let's try with cricket! Active: 'Virat hits a six.' Passive: 'A six is hit by Virat.' See the pattern?",
                "animations": [
                    {"type": "cricket_scene", "elements": ["batsman", "ball", "boundary"], "duration": 1000},
                    {
                        "type": "dual_sentence_build",
                        "active": {"sentence": "Virat hits a six", "animation": "batsman_swings", "focus": "batsman"},
                        "passive": {"sentence": "A six is hit by Virat", "animation": "ball_travels", "focus": "ball"},
                        "duration": 3000
                    }
                ],
                "interactions": [
                    {
                        "type": "drag",
                        "prompt": "Drag the words to form the passive voice!",
                        "items": [
                            {"id": "item1", "label": "A six"},
                            {"id": "item2", "label": "is hit"},
                            {"id": "item3", "label": "by Virat"}
                        ],
                        "targets": [
                            {"id": "pos1", "label": "Position 1"},
                            {"id": "pos2", "label": "Position 2"},
                            {"id": "pos3", "label": "Position 3"}
                        ],
                        "correctMapping": {"item1": "pos1", "item2": "pos2", "item3": "pos3"}
                    }
                ],
                "emphasis": "Pattern: Object + be verb + past participle + by + Subject"
            },

            # STAGE 6: When to Use
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 4000,
                "narration": "Use ACTIVE when the doer is important. Use PASSIVE when the action or receiver matters more, or when the doer is unknown!",
                "animations": [
                    {
                        "type": "decision_tree",
                        "root": "Which voice to use?",
                        "branches": [
                            {"question": "Is WHO did it important?", "yes": "Use ACTIVE VOICE", "no": "Consider PASSIVE"},
                            {"question": "Is WHAT happened important?", "yes": "Use PASSIVE VOICE", "no": "Use ACTIVE"}
                        ],
                        "duration": 3000
                    }
                ],
                "interactions": [
                    {
                        "type": "predict",
                        "prompt": "Which voice would you use for: 'The suspect was arrested last night'?",
                        "options": ["Active Voice", "Passive Voice"],
                        "actual": "Passive Voice - because who arrested is less important than the arrest itself!"
                    }
                ],
                "emphasis": None
            },

            # STAGE 7: Summary
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 3000,
                "narration": "Great! Remember: Active = Doer First, Passive = Receiver First. Both correct, different purposes!",
                "animations": [
                    {
                        "type": "summary_card",
                        "title": "Active vs Passive Voice",
                        "points": [
                            {"icon": "✓", "text": "Active: Subject does action", "color": "#10b981"},
                            {"icon": "✓", "text": "Passive: Action done to object", "color": "#6366f1"},
                            {"icon": "✓", "text": "Choose based on focus!", "color": "#f59e0b"}
                        ],
                        "duration": 2000
                    },
                    {"type": "celebration", "effect": "confetti", "duration": 1000}
                ],
                "interactions": None,
                "emphasis": None
            }
        ]

        total_duration = sum(stage["duration_ms"] for stage in stages)
        interaction_points = [i for i, stage in enumerate(stages) if stage["interactions"]]

        return {
            "visual_id": str(uuid.uuid4()),
            "type": "animated_lesson",
            "stages": stages,
            "total_duration_ms": total_duration,
            "interaction_points": interaction_points,
            "metadata": {
                "subject": "English",
                "topic": "Active and Passive Voice",
                "concept_type": "transformation",
                "visual_pattern": "split_screen",
                "complexity": "medium",
                "cultural_metaphor": "cooking",
                "grade_level": "8-12",
                "ncert_reference": "Class 10 English Grammar"
            }
        }

    @staticmethod
    def subject_verb_agreement() -> Dict[str, Any]:
        """Generate animated teaching for subject-verb agreement"""
        stages = [
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 3000,
                "narration": "Subject-verb agreement is like a cricket team - the number of players (subject) matches the field setup (verb)!",
                "animations": [{"type": "scene_setup", "elements": ["cricket_field", "players"], "style": "cricket_theme"}],
                "interactions": None,
                "emphasis": "Singular subject needs singular verb, plural needs plural!"
            },
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 4000,
                "narration": "Singular: 'The player runs' - ONE player, ONE action. Plural: 'The players run' - MANY players, MANY actions!",
                "animations": [
                    {
                        "type": "split_comparison",
                        "left": {"title": "SINGULAR", "sentence": "The player runs", "visual": "single_player_running"},
                        "right": {"title": "PLURAL", "sentence": "The players run", "visual": "multiple_players_running"}
                    }
                ],
                "interactions": [
                    {
                        "type": "quiz",
                        "question": "Which is correct: 'The team play well' or 'The team plays well'?",
                        "options": ["The team play well", "The team plays well"],
                        "correct": 1,
                        "hint": "Team is ONE unit, even though it has many members!"
                    }
                ],
                "emphasis": None
            }
        ]

        return {
            "visual_id": str(uuid.uuid4()),
            "type": "animated_lesson",
            "stages": stages,
            "total_duration_ms": sum(s["duration_ms"] for s in stages),
            "interaction_points": [i for i, s in enumerate(stages) if s["interactions"]],
            "metadata": {
                "subject": "English",
                "topic": "Subject-Verb Agreement",
                "concept_type": "relationship",
                "visual_pattern": "split_screen",
                "complexity": "simple",
                "cultural_metaphor": "cricket"
            }
        }

    @staticmethod
    def tenses_timeline() -> Dict[str, Any]:
        """Generate animated teaching for tenses using train metaphor"""
        stages = [
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 3500,
                "narration": "Tenses are like train stations! Past is where we came from, Present is where we are, Future is where we're going!",
                "animations": [{"type": "train_timeline", "stations": ["PAST", "PRESENT", "FUTURE"], "train_position": "present"}],
                "interactions": None,
                "emphasis": None
            },
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 4000,
                "narration": "Simple Past: 'I ate biryani yesterday' - train already passed that station!",
                "animations": [{"type": "train_move_to_station", "station": "past", "example": "I ate biryani", "timestamp": "yesterday"}],
                "interactions": [{"type": "tap_to_continue"}],
                "emphasis": None
            },
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 4000,
                "narration": "Present Continuous: 'I am eating biryani' - train is AT the station right now!",
                "animations": [{"type": "train_at_station", "station": "present", "example": "I am eating biryani", "timestamp": "now", "action": "ongoing"}],
                "interactions": None,
                "emphasis": None
            },
            {
                "stage_id": str(uuid.uuid4()),
                "duration_ms": 4000,
                "narration": "Simple Future: 'I will eat biryani tomorrow' - train heading to that station!",
                "animations": [{"type": "train_heading_to_station", "station": "future", "example": "I will eat biryani", "timestamp": "tomorrow"}],
                "interactions": [
                    {
                        "type": "quiz",
                        "question": "Which tense: 'I was eating biryani when he called'?",
                        "options": ["Past Simple", "Past Continuous", "Present Perfect"],
                        "correct": 1,
                        "hint": "The action was ONGOING in the past!"
                    }
                ],
                "emphasis": None
            }
        ]

        return {
            "visual_id": str(uuid.uuid4()),
            "type": "animated_lesson",
            "stages": stages,
            "total_duration_ms": sum(s["duration_ms"] for s in stages),
            "interaction_points": [i for i, s in enumerate(stages) if s["interactions"]],
            "metadata": {
                "subject": "English",
                "topic": "Verb Tenses",
                "concept_type": "timeline",
                "visual_pattern": "timeline",
                "complexity": "medium",
                "cultural_metaphor": "trains"
            }
        }


def get_grammar_visual_template(topic: str) -> Dict[str, Any]:
    """Get pre-built visual template for common grammar topics"""
    templates = {
        "active_passive": GrammarVisualTemplates.active_passive_voice,
        "active_passive_voice": GrammarVisualTemplates.active_passive_voice,
        "subject_verb_agreement": GrammarVisualTemplates.subject_verb_agreement,
        "tenses": GrammarVisualTemplates.tenses_timeline,
        "verb_tenses": GrammarVisualTemplates.tenses_timeline
    }

    topic_key = topic.lower().replace(" ", "_")

    if topic_key in templates:
        return templates[topic_key]()

    return None
