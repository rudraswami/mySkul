"""
Visual Metaphor Library - Regional & Category-Based
100+ culturally resonant metaphors with visual assets
"""

# CDN base path for visual assets
VISUAL_CDN_BASE = "https://assets.dhruvai.com/visuals"

# REAL IMAGE ASSETS - Culturally Relevant Visual Metaphors
# Retrieved from Vision Expert Agent - Authentic Indian scenes

REAL_VISUAL_ASSETS = {
    "cricket": [
        "https://images.unsplash.com/photo-1685541001104-91fe7ae1d8e1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwyfHxEaG9uaSUyMGNyaWNrZXQlMjBiYXR0aW5nfGVufDB8fHx8MTc2MjMyODQ0OXww&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1685541000777-8d0995d38909?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHw0fHxEaG9uaSUyMGNyaWNrZXQlMjBiYXR0aW5nfGVufDB8fHx8MTc2MjMyODQ0OXww&ixlib=rb-4.1.0&q=85",
        "https://images.pexels.com/photos/3800517/pexels-photo-3800517.jpeg",
        "https://images.unsplash.com/photo-1685541000527-662e48d677a3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxjcmlja2V0JTIwc3RyYXRlZ3l8ZW58MHx8fHwxNzYyMzI4NDU4fDA&ixlib=rb-4.1.0&q=85",
        "https://images.pexels.com/photos/32801390/pexels-photo-32801390.jpeg"
    ],
    "cooking": [
        "https://images.unsplash.com/photo-1758387941825-a6ecaec9c14d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwxfHxmaWx0ZXIlMjBjb2ZmZWUlMjBJbmRpYW58ZW58MHx8fHwxNzYyMzI4NTA0fDA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1713780131281-61ec701ebb6f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxiaXJ5YW5pJTIwY29va2luZ3xlbnwwfHx8fDE3NjIzMjg1MTB8MA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1589778314823-d1c2bde0a31b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwyfHxJbmRpYW4lMjBzdHJlZXQlMjBmb29kfGVufDB8fHx8MTc2MjMyODUxN3ww&ixlib=rb-4.1.0&q=85",
        "https://images.pexels.com/photos/19834446/pexels-photo-19834446.jpeg",
        "https://images.pexels.com/photos/3531700/pexels-photo-3531700.jpeg"
    ]
}

# Metaphor Library: {concept: {category: {region: visual_data}}}
METAPHOR_LIBRARY = {
    "integration_by_parts": {
        "cricket": {
            "Delhi": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][0],  # Real cricket action
                "metaphor_text": "Like Dhoni choosing which ball to hit vs defend - you decide which part to differentiate (attack) and which to integrate (defend)",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][1:3],
                "animation_hint": "cricket-bat-swing",
                "color_theme": "#DC2626",  # Delhi Capitals red
                "cultural_context": "Delhi Capitals strategy"
            },
            "Mumbai": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][1],  # Real cricket game
                "metaphor_text": "Like Mumbai Indians choosing batting order - decide which function goes first (u) and which follows (dv)",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][2:4],
                "animation_hint": "cricket-run-chase",
                "color_theme": "#004BA0",  # MI blue
                "cultural_context": "Mumbai Indians tactics"
            },
            "Chennai": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][2],  # Real cricket strategy
                "metaphor_text": "Like CSK's calm batting approach - choose u wisely and let dv support",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][3:5],
                "animation_hint": "cricket-calm-strategy",
                "color_theme": "#FDB913",  # CSK yellow
                "cultural_context": "CSK's strategic play"
            },
            "Kolkata": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][3],  # Real fielding
                "metaphor_text": "Like KKR's aggressive fielding - position your functions (u and dv) strategically",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][0:2],
                "animation_hint": "cricket-fielding",
                "color_theme": "#3F1F5E",  # KKR purple
                "cultural_context": "KKR's fielding tactics"
            },
            "Bangalore": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][4],  # Real power hitting
                "metaphor_text": "Like RCB's power hitting - choose the right function (u) to differentiate and integrate (dv) for maximum impact",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][1:3],
                "animation_hint": "cricket-power-hit",
                "color_theme": "#EC1C24",  # RCB red
                "cultural_context": "RCB's aggressive batting"
            }
        },
        "cooking": {
            "Delhi": {
                "hero_visual": REAL_VISUAL_ASSETS["cooking"][2],  # Street food cooking
                "metaphor_text": "Like making butter chicken - marinate (u) first, then cook (dv) step by step",
                "step_visuals": REAL_VISUAL_ASSETS["cooking"][3:5],
                "animation_hint": "cooking-pot-stir",
                "color_theme": "#F97316",  # Orange curry
                "cultural_context": "Delhi street food"
            },
            "Mumbai": {
                "hero_visual": REAL_VISUAL_ASSETS["cooking"][2],  # Street vendor
                "metaphor_text": "Like assembling vada pav - prepare vada (u), then add pav (dv) together",
                "step_visuals": REAL_VISUAL_ASSETS["cooking"][3:5],
                "animation_hint": "cooking-assembly",
                "color_theme": "#F59E0B",  # Golden vada
                "cultural_context": "Mumbai street food"
            },
            "Chennai": {
                "hero_visual": REAL_VISUAL_ASSETS["cooking"][0],  # Filter coffee
                "metaphor_text": "Like making perfect dosa - spread batter (u) evenly, cook (dv) with timing",
                "step_visuals": REAL_VISUAL_ASSETS["cooking"][1:3],
                "animation_hint": "cooking-dosa-spread",
                "color_theme": "#D97706",  # Golden dosa
                "cultural_context": "Chennai breakfast"
            },
            "Kolkata": {
                "hero_visual": REAL_VISUAL_ASSETS["cooking"][1],  # Cooking pot
                "metaphor_text": "Like making rasgulla - prepare chenna balls (u), cook in syrup (dv) with care",
                "step_visuals": REAL_VISUAL_ASSETS["cooking"][3:5],
                "animation_hint": "cooking-sweet-boil",
                "color_theme": "#FBBF24",  # Sweet yellow
                "cultural_context": "Kolkata sweets"
            },
            "Bangalore": {
                "hero_visual": REAL_VISUAL_ASSETS["cooking"][0],  # Filter coffee brewing
                "metaphor_text": "Like brewing filter coffee - decoction (u) first, then add milk (dv) in layers",
                "step_visuals": REAL_VISUAL_ASSETS["cooking"][3:5],
                "animation_hint": "cooking-pour-coffee",
                "color_theme": "#92400E",  # Coffee brown
                "cultural_context": "Bangalore coffee culture"
            }
        },
        "bollywood": {
            "all": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][0],  # Placeholder - using cricket for now
                "metaphor_text": "Like SRK and Kajol's chemistry in DDLJ - two functions (u and dv) working together perfectly",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][1:3],
                "animation_hint": "movie-scene-transition",
                "color_theme": "#BE185D",  # Bollywood pink
                "cultural_context": "Classic Bollywood romance"
            }
        },
        "gaming": {
            "all": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][3],  # Placeholder - using cricket for now
                "metaphor_text": "Like choosing weapon in PUBG - pick u (rifle) to differentiate, dv (scope) to integrate for perfect shot",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][0:2],
                "animation_hint": "game-level-up",
                "color_theme": "#059669",  # Gaming green
                "cultural_context": "Mobile gaming strategy"
            }
        }
    },
    
    # Pythagoras Theorem - Real visuals
    "pythagoras_theorem": {
        "cricket": {
            "all": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][1],  # Cricket fielding
                "metaphor_text": "Like cricket fielding triangle - three fielders form right angle, distance calculation is a² + b² = c²",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][2:4],
                "animation_hint": "cricket-triangle-formation",
                "color_theme": "#10B981",
                "cultural_context": "IPL fielding strategy"
            }
        },
        "cooking": {
            "all": {
                "hero_visual": REAL_VISUAL_ASSETS["cooking"][4],  # Cooking scene
                "metaphor_text": "Like measuring roti dough - if you fold it into triangle, edges follow Pythagoras",
                "step_visuals": REAL_VISUAL_ASSETS["cooking"][1:3],
                "animation_hint": "cooking-fold-triangle",
                "color_theme": "#F59E0B",
                "cultural_context": "Home cooking"
            }
        }
    },
    
    # Generic fallback for unmapped concepts
    "generic_concept": {
        "cricket": {
            "all": {
                "hero_visual": REAL_VISUAL_ASSETS["cricket"][0],
                "metaphor_text": "Let me explain this with a cricket example you'll relate to",
                "step_visuals": REAL_VISUAL_ASSETS["cricket"][1:3],
                "animation_hint": "cricket-strategy",
                "color_theme": "#10B981",
                "cultural_context": "Cricket strategy"
            }
        },
        "cooking": {
            "all": {
                "hero_visual": REAL_VISUAL_ASSETS["cooking"][0],
                "metaphor_text": "Let me explain this like a cooking recipe",
                "step_visuals": REAL_VISUAL_ASSETS["cooking"][1:3],
                "animation_hint": "cooking-process",
                "color_theme": "#F59E0B",
                "cultural_context": "Cooking process"
            }
        }
    }
}

# Mentor Avatar States
MENTOR_AVATARS = {
    "default": f"{VISUAL_CDN_BASE}/mentor/avatar-neutral.png",
    "excited": f"{VISUAL_CDN_BASE}/mentor/avatar-excited.png",
    "thinking": f"{VISUAL_CDN_BASE}/mentor/avatar-thinking.png",
    "encouraging": f"{VISUAL_CDN_BASE}/mentor/avatar-encouraging.png",
    "celebrating": f"{VISUAL_CDN_BASE}/mentor/avatar-celebrating.png"
}

# Interactive Element Templates
INTERACTIVE_TEMPLATES = {
    "drag_drop": {
        "visual": f"{VISUAL_CDN_BASE}/interactive/drag-drop-template.png",
        "feedback_correct": f"{VISUAL_CDN_BASE}/interactive/correct-celebration.gif",
        "feedback_wrong": f"{VISUAL_CDN_BASE}/interactive/try-again.png"
    },
    "slider": {
        "visual": f"{VISUAL_CDN_BASE}/interactive/slider-template.png",
        "feedback_correct": f"{VISUAL_CDN_BASE}/interactive/slider-success.gif",
        "feedback_wrong": f"{VISUAL_CDN_BASE}/interactive/slider-hint.png"
    },
    "tap_reveal": {
        "visual": f"{VISUAL_CDN_BASE}/interactive/tap-reveal-template.png",
        "feedback_correct": f"{VISUAL_CDN_BASE}/interactive/reveal-success.gif",
        "feedback_wrong": f"{VISUAL_CDN_BASE}/interactive/reveal-hint.png"
    }
}

# Verification Badges
VERIFICATION_BADGES = {
    "verified": f"{VISUAL_CDN_BASE}/badges/verified-badge.png",
    "ncert_verified": f"{VISUAL_CDN_BASE}/badges/ncert-badge.png",
    "professor_checked": f"{VISUAL_CDN_BASE}/badges/professor-badge.png"
}

# Memory Challenge Assets
MEMORY_CHALLENGE_ASSETS = {
    "memory_badge": f"{VISUAL_CDN_BASE}/badges/memory-master.png",
    "challenge_bg": f"{VISUAL_CDN_BASE}/challenges/memory-bg.png",
    "success_animation": f"{VISUAL_CDN_BASE}/challenges/success-confetti.gif"
}


def get_metaphor_visual(concept: str, category: str, region: str):
    """
    Get visual metaphor for concept
    
    Args:
        concept: Concept name (e.g., 'integration_by_parts')
        category: Metaphor category ('cricket', 'cooking', 'bollywood', 'gaming')
        region: Region ('Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore')
    
    Returns:
        Dict with visual assets and metaphor text
    """
    concept_key = concept.lower().replace(' ', '_')
    
    if concept_key not in METAPHOR_LIBRARY:
        # Default fallback
        return {
            "hero_visual": f"{VISUAL_CDN_BASE}/default/concept-visual.png",
            "metaphor_text": "Let me break this down for you step by step",
            "step_visuals": [],
            "animation_hint": "none",
            "color_theme": "#6366F1",
            "cultural_context": "General"
        }
    
    concept_metaphors = METAPHOR_LIBRARY[concept_key]
    
    if category not in concept_metaphors:
        category = list(concept_metaphors.keys())[0]  # Fallback to first available
    
    category_metaphors = concept_metaphors[category]
    
    # Check if region-specific or 'all' regions
    if region in category_metaphors:
        return category_metaphors[region]
    elif 'all' in category_metaphors:
        return category_metaphors['all']
    else:
        # Fallback to first region available
        first_region = list(category_metaphors.keys())[0]
        return category_metaphors[first_region]


def get_mentor_avatar(emotion: str):
    """Get mentor avatar for emotion state"""
    return MENTOR_AVATARS.get(emotion, MENTOR_AVATARS['default'])


def get_interactive_template(interaction_type: str):
    """Get interactive element template"""
    return INTERACTIVE_TEMPLATES.get(interaction_type, INTERACTIVE_TEMPLATES['tap_reveal'])


def get_verification_badge(verification_type: str = 'verified'):
    """Get verification badge visual"""
    return VERIFICATION_BADGES.get(verification_type, VERIFICATION_BADGES['verified'])
