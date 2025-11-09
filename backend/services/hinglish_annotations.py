"""
Hinglish Annotation Generator
Generates emotionally resonant exam annotations in Hinglish
Implements the "friend explaining at 2 AM" emotional mandate
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional

# Regional slang and teaching styles
REGIONAL_SLANG = {
    "North": {
        "attention": ["Dhyan se dekho", "Yeh important hai", "Arre bhai", "Suno yaar"],
        "warning": [
            "Sharma sir yaha cut maarte hain",
            "Yaha galti mat karna",
            "Yaha number jayenge",
            "Ye step miss mat karna"
        ],
        "encouragement": [
            "Simple hai yaar",
            "Bas yeh samajh le",
            "Ekdum easy hai",
            "Tu kar lega bhai"
        ],
        "teachers": ["Sharma sir", "Khan ma'am", "Gupta sir", "Verma ma'am", "Singh sir"]
    },
    "South": {
        "attention": [
            "See this carefully da",
            "This is important pa",
            "Note this point",
            "Focus here ra"
        ],
        "warning": [
            "Sir will deduct marks here",
            "Don't skip this step da",
            "Examiner will check this pa",
            "This mistake is common ra"
        ],
        "encouragement": [
            "Simple only",
            "Just understand this",
            "Easy concept da",
            "You can do it pa"
        ],
        "teachers": ["Kumar sir", "Lakshmi ma'am", "Reddy sir", "Iyer ma'am", "Rao sir"]
    },
    "West": {
        "attention": ["Aata, yeh dekh", "Focus kar yaha", "Hya kade baagh", "Lakshyat thev"],
        "warning": [
            "Madam points kaapti hai",
            "Aamcha galti yaha",
            "Marks jayenge yaha",
            "Careful rahna yaha"
        ],
        "encouragement": [
            "Simple aahe",
            "Samjun ghya",
            "Easy aahe na",
            "Tension nahi gheu"
        ],
        "teachers": ["Patil sir", "Desai ma'am", "Joshi sir", "Kulkarni ma'am", "Pawar sir"]
    },
    "East": {
        "attention": ["Ektu dekho", "Important hoiche", "Dhyan dao", "Suno toh"],
        "warning": [
            "Sir ekhane number katbe",
            "Mistake korbe na",
            "Marks harabe yaha",
            "Careful thakbe"
        ],
        "encouragement": ["Simple", "Bujhe nao", "Easy aahe", "Parbe tumi"],
        "teachers": ["Das sir", "Sen ma'am", "Chatterjee sir", "Mukherjee ma'am", "Bose sir"]
    }
}

# Exam fear templates with emotional resonance
EXAM_FEAR_TEMPLATES = [
    "Kal exam hai, yeh yaad rakhna! 📝",
    "90% yaha marks lose karte hain ⚠️",
    "Yeh step skip kiya toh {marks} marks gaye 💔",
    "Examiner yaha pakka check karega 👀",
    "{teacher} specifically iske baare mein bole the 🎓",
    "Boards mein yahi question aata hai! 🔥",
    "Paper mein yeh compulsory hai 📌",
    "Concept clear nahi toh full marks gaye 😰"
]

# Common mistake warnings
COMMON_MISTAKES = {
    "recursion": [
        "90% log base case bhool jaate hain",
        "Recursive call ke baad return likhna bhoolte hain",
        "Base case pehle nahi likhte"
    ],
    "binary_search": [
        "Mid calculation galat hota hai",
        "Array sorted hai ya nahi check nahi karte",
        "Left <= right condition miss ho jata hai"
    ],
    "sorting": [
        "Time complexity galat likh dete hain",
        "Stable vs unstable difference nahi jaante",
        "Best/worst case confuse ho jata hai"
    ],
    "stack": [
        "Underflow condition check nahi karte",
        "Push ke baad top increment bhoolte hain",
        "Stack full condition miss hoti hai"
    ],
    "tree": [
        "Null check nahi karte - segfault!",
        "Left/right confuse ho jata hai",
        "Base case recursion mein nahi hai"
    ],
    "default": [
        "Yeh step 90% students bhool jaate hain",
        "Formula yaad hai but application galat",
        "Definition toh sahi hai but example galat"
    ]
}


def generate_annotation(
    concept: str,
    annotation_type: str,  # "attention", "warning", "encouragement", "teacher_tip", "exam_fear"
    region: str = "North",
    marks: int = 2,
    teacher_name: Optional[str] = None
) -> str:
    """
    Generate context-aware Hinglish annotation

    Args:
        concept: The concept being explained (e.g., "recursion", "binary search")
        annotation_type: Type of annotation to generate
        region: Geographic region for language style (North/South/East/West)
        marks: Number of marks at stake
        teacher_name: Optional specific teacher name

    Returns:
        Hinglish annotation string with emoji
    """
    # Normalize region
    region = region if region in REGIONAL_SLANG else "North"
    templates = REGIONAL_SLANG[region]

    if annotation_type == "warning":
        base = random.choice(templates["warning"])
        return f"{base} ⚠️ ({marks} marks risk)"

    elif annotation_type == "teacher_tip":
        teacher = teacher_name or random.choice(templates["teachers"])
        return f"{teacher} ne bola: Yeh exam mein zaroori hai! 🎓"

    elif annotation_type == "exam_fear":
        template = random.choice(EXAM_FEAR_TEMPLATES)
        teacher = teacher_name or random.choice(templates["teachers"])
        return template.format(marks=marks, teacher=teacher)

    elif annotation_type == "encouragement":
        return f"{random.choice(templates['encouragement'])} 💪"

    elif annotation_type == "attention":
        return f"{random.choice(templates['attention'])} 👀"

    # Default: attention
    return random.choice(templates.get("attention", ["Important point"]))


def get_common_mistake(concept: str, region: str = "North") -> str:
    """
    Get common mistake warning for a concept

    Args:
        concept: The concept (e.g., "recursion")
        region: Region for language localization

    Returns:
        Common mistake annotation in Hinglish
    """
    # Extract key concept words
    concept_lower = concept.lower()

    # Find matching mistake category
    for key, mistakes in COMMON_MISTAKES.items():
        if key in concept_lower:
            mistake = random.choice(mistakes)
            return f"❌ Common mistake: {mistake}"

    # Default fallback
    mistake = random.choice(COMMON_MISTAKES["default"])
    return f"❌ {mistake}"


def generate_marks_annotation(
    total_marks: int,
    parts: List[int],
    region: str = "North"
) -> str:
    """
    Generate marks breakdown annotation

    Args:
        total_marks: Total marks for the question
        parts: List of marks per part
        region: Region for language style

    Returns:
        Marks breakdown string
    """
    if len(parts) > 1:
        parts_str = " + ".join(str(p) for p in parts)
        return f"💯 Marks: {total_marks} ({parts_str})"
    else:
        return f"💯 Total: {total_marks} marks"


def generate_exam_context(
    board: Optional[str] = None,
    exam: Optional[str] = None,
    region: str = "North"
) -> str:
    """
    Generate exam-specific context annotation

    Args:
        board: Education board (CBSE, ICSE, etc.)
        exam: Exam name (JEE, NEET, etc.)
        region: Region for language style

    Returns:
        Exam context string
    """
    contexts = []

    if board:
        contexts.append(f"📚 {board} pattern")

    if exam:
        contexts.append(f"🎯 {exam} important")

    if not contexts:
        contexts.append("📝 Exam important")

    return " | ".join(contexts)


def get_regional_metaphor_label(metaphor_name: str, region: str = "North") -> str:
    """
    Get region-appropriate label for metaphor

    Args:
        metaphor_name: Metaphor category (family, food, cricket, etc.)
        region: Region for language style

    Returns:
        Localized metaphor label
    """
    labels = {
        "North": {
            "family": "Ghar ka example",
            "food": "Khana banane jaise",
            "cricket": "Cricket jaise samjho",
            "bollywood": "Film ki kahani jaise",
            "gaming": "Game jaise khelo"
        },
        "South": {
            "family": "Home example da",
            "food": "Cooking like this",
            "cricket": "Cricket match like",
            "bollywood": "Movie story like",
            "gaming": "Game mechanics"
        },
        "West": {
            "family": "Gharcha udaharan",
            "food": "Swayampak jaise",
            "cricket": "Cricket sarkha",
            "bollywood": "Chitra katha",
            "gaming": "Khel jaise"
        },
        "East": {
            "family": "Ghorer udaharan",
            "food": "Ranna korar moto",
            "cricket": "Cricket match",
            "bollywood": "Cinema kahini",
            "gaming": "Game khela"
        }
    }

    region = region if region in labels else "North"
    return labels[region].get(metaphor_name, metaphor_name.title())


# Quick access functions for common use cases
def fear_annotation(marks: int = 2, region: str = "North") -> str:
    """Quick exam fear annotation"""
    return generate_annotation("concept", "exam_fear", region, marks)


def mistake_warning(concept: str, region: str = "North") -> str:
    """Quick common mistake warning"""
    return get_common_mistake(concept, region)


def topper_tip(region: str = "North") -> str:
    """Quick topper tip annotation"""
    tips = {
        "North": [
            "🏆 Topper trick: Steps ko number karo",
            "🏆 AIR holder: Diagram zaroori hai",
            "🏆 90+ scorer: Keywords bold karo"
        ],
        "South": [
            "🏆 Topper tip: Number the steps",
            "🏆 State rank: Diagram is must",
            "🏆 High scorer: Bold keywords"
        ],
        "West": [
            "🏆 Topper tip: Steps number kara",
            "🏆 Rank holder: Diagram aavashyak",
            "🏆 High marks: Keywords bold"
        ],
        "East": [
            "🏆 Topper tip: Steps number koro",
            "🏆 Rank holder: Diagram lagbe",
            "🏆 High marks: Keywords bold"
        ]
    }

    region = region if region in tips else "North"
    return random.choice(tips[region])
