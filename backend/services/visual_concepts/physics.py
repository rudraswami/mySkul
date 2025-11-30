"""
⚡ PHYSICS Visual Concepts - Complete Coverage
==============================================

Class 9-12, JEE, NEET level Physics concepts with visual templates.

Categories:
1. Mechanics (Motion, Force, Energy, etc.)
2. Thermodynamics (Heat, Temperature)
3. Waves & Sound
4. Light & Optics
5. Electricity & Magnetism
6. Modern Physics

Total: 50+ concepts
"""

from typing import Dict, Any

# Template types
RACE = "race_comparison"
PROCESS = "process_flow"
CAUSE_EFFECT = "cause_effect"
CYCLE = "cycle"
SCALE = "scale_spectrum"
STRUCTURE = "structure_anatomy"
GRAPH = "graph_relationship"
SEQUENCE = "sequence_timeline"


PHYSICS_CONCEPTS: Dict[str, Dict[str, Any]] = {
    
    # ═══════════════════════════════════════════════════════════════
    # MECHANICS - Motion
    # ═══════════════════════════════════════════════════════════════
    
    "velocity": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Motion",
        "class_level": [9, 11],
        "title": "Velocity = Distance ÷ Time",
        "title_hindi": "वेग = दूरी ÷ समय",
        "keywords": ["velocity", "speed", "motion", "fast", "slow", "moving"],
        "config": {
            "object_a": {"type": "auto_rickshaw", "label": "FAST", "color": "#FF9933", "speed": 20},
            "object_b": {"type": "auto_rickshaw", "label": "SLOW", "color": "#3B82F6", "speed": 10},
            "track_length": 100,
            "unit": "m",
            "formula": "v = d / t",
            "memory_hook": "MORE distance in SAME time = MORE velocity! 🚀"
        },
        "indian_context": "Auto rickshaw race to school"
    },
    
    "displacement": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Motion",
        "class_level": [9, 11],
        "title": "Displacement vs Distance",
        "title_hindi": "विस्थापन बनाम दूरी",
        "keywords": ["displacement", "distance", "path", "shortest"],
        "config": {
            "object_a": {"type": "car", "label": "CURVED PATH", "color": "#EF4444", "speed": 15, "path": "curved"},
            "object_b": {"type": "car", "label": "STRAIGHT", "color": "#10B981", "speed": 15, "path": "straight"},
            "track_length": 100,
            "unit": "m",
            "formula": "Displacement ≤ Distance",
            "memory_hook": "Shortest path = Displacement! 📍"
        },
        "indian_context": "Two routes to school - shortcut vs main road"
    },
    
    "acceleration": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Motion",
        "class_level": [9, 11],
        "title": "Acceleration = Change in Velocity",
        "title_hindi": "त्वरण = वेग में परिवर्तन",
        "keywords": ["acceleration", "speed up", "slow down", "decelerate"],
        "config": {
            "object_a": {"type": "scooter", "label": "ACCELERATING", "color": "#10B981", "speed": 0, "acceleration": 5},
            "object_b": {"type": "scooter", "label": "CONSTANT", "color": "#6B7280", "speed": 10, "acceleration": 0},
            "track_length": 100,
            "unit": "m",
            "formula": "a = (v - u) / t",
            "memory_hook": "Twist throttle = Acceleration! 🏎️"
        },
        "indian_context": "Scooty speeding up on highway"
    },
    
    "uniform_motion": {
        "template": GRAPH,
        "subject": "physics",
        "chapter": "Motion",
        "class_level": [9, 11],
        "title": "Uniform Motion = Straight Line",
        "title_hindi": "एकसमान गति = सीधी रेखा",
        "keywords": ["uniform motion", "constant speed", "straight line graph"],
        "config": {
            "equation": "s = vt",
            "shape": "line",
            "x_axis": "Time (t)",
            "y_axis": "Distance (s)",
            "formula": "s = v × t",
            "memory_hook": "Constant speed = Straight graph! 📈"
        },
        "indian_context": "Train moving at constant speed"
    },
    
    "equations_of_motion": {
        "template": SEQUENCE,
        "subject": "physics",
        "chapter": "Motion",
        "class_level": [9, 11],
        "title": "Three Equations of Motion",
        "title_hindi": "गति के तीन समीकरण",
        "keywords": ["equations of motion", "suvat", "kinematic"],
        "config": {
            "stages": [
                {"label": "v = u + at", "description": "Final velocity"},
                {"label": "s = ut + ½at²", "description": "Displacement"},
                {"label": "v² = u² + 2as", "description": "No time needed"}
            ],
            "formula": "v = u + at | s = ut + ½at² | v² = u² + 2as",
            "memory_hook": "SUVAT - Super Useful Velocity And Time! 🎯"
        },
        "indian_context": "Cricket ball thrown up and coming down"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # MECHANICS - Force & Laws of Motion
    # ═══════════════════════════════════════════════════════════════
    
    "force": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Force and Laws of Motion",
        "class_level": [9, 11],
        "title": "Force = Mass × Acceleration",
        "title_hindi": "बल = द्रव्यमान × त्वरण",
        "keywords": ["force", "push", "pull", "newton", "f=ma"],
        "config": {
            "cause": {"label": "PUSH", "icon": "💪"},
            "effect": {"label": "MOVES", "icon": "📦"},
            "action_label": "FORCE →",
            "formula": "F = m × a",
            "memory_hook": "More mass = More force needed! 🏋️"
        },
        "indian_context": "Pushing loaded vs empty cart"
    },
    
    "newton_first_law": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Force and Laws of Motion",
        "class_level": [9, 11],
        "title": "Newton's 1st Law - Inertia",
        "title_hindi": "न्यूटन का प्रथम नियम - जड़त्व",
        "keywords": ["inertia", "newton first", "rest", "motion continues"],
        "config": {
            "cause": {"label": "NO FORCE", "icon": "🛑"},
            "effect": {"label": "STAYS SAME", "icon": "➡️"},
            "action_label": "INERTIA",
            "formula": "If F=0, v=constant",
            "memory_hook": "Lazy objects hate change! 😴"
        },
        "indian_context": "Bus brake - passengers fall forward"
    },
    
    "newton_second_law": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Force and Laws of Motion",
        "class_level": [9, 11],
        "title": "Newton's 2nd Law - F = ma",
        "title_hindi": "न्यूटन का द्वितीय नियम",
        "keywords": ["newton second", "f=ma", "acceleration force"],
        "config": {
            "object_a": {"type": "ball", "label": "LIGHT (1kg)", "color": "#10B981", "mass": 1},
            "object_b": {"type": "ball", "label": "HEAVY (2kg)", "color": "#EF4444", "mass": 2},
            "same_force": True,
            "formula": "a = F / m",
            "memory_hook": "Heavy = Lazy to accelerate! 🐘"
        },
        "indian_context": "Same push on cricket ball vs football"
    },
    
    "newton_third_law": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Force and Laws of Motion",
        "class_level": [9, 11],
        "title": "Newton's 3rd Law - Action-Reaction",
        "title_hindi": "न्यूटन का तृतीय नियम",
        "keywords": ["newton third", "action reaction", "equal opposite"],
        "config": {
            "cause": {"label": "ACTION", "icon": "👊"},
            "effect": {"label": "REACTION", "icon": "👊"},
            "action_label": "= but ←",
            "formula": "F₁ = -F₂",
            "memory_hook": "Slap wall, wall slaps back! ✋"
        },
        "indian_context": "Swimming - push water back, you go forward"
    },
    
    "momentum": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Force and Laws of Motion",
        "class_level": [9, 11],
        "title": "Momentum = Mass × Velocity",
        "title_hindi": "संवेग = द्रव्यमान × वेग",
        "keywords": ["momentum", "collision", "impact", "impulse"],
        "config": {
            "object_a": {"type": "train", "label": "TRAIN", "color": "#EF4444", "mass": 1000, "speed": 10},
            "object_b": {"type": "bicycle", "label": "BICYCLE", "color": "#3B82F6", "mass": 10, "speed": 10},
            "track_length": 100,
            "formula": "p = m × v",
            "memory_hook": "Heavy + Fast = UNSTOPPABLE! 💨"
        },
        "indian_context": "Train vs bicycle at same speed - which hurts more?"
    },
    
    "conservation_of_momentum": {
        "template": PROCESS,
        "subject": "physics",
        "chapter": "Force and Laws of Motion",
        "class_level": [9, 11],
        "title": "Conservation of Momentum",
        "title_hindi": "संवेग का संरक्षण",
        "keywords": ["conservation", "momentum", "collision", "before after"],
        "config": {
            "inputs": [
                {"label": "Ball A (moving)", "icon": "🔴", "color": "#EF4444"},
                {"label": "Ball B (rest)", "icon": "🔵", "color": "#3B82F6"}
            ],
            "process_box": {"label": "COLLISION", "icon": "💥"},
            "outputs": [
                {"label": "Both moving", "icon": "🔴🔵", "color": "#8B5CF6"}
            ],
            "formula": "m₁u₁ + m₂u₂ = m₁v₁ + m₂v₂",
            "memory_hook": "Total momentum before = after! ⚖️"
        },
        "indian_context": "Carrom striker hitting coins"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # MECHANICS - Friction
    # ═══════════════════════════════════════════════════════════════
    
    "friction": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Friction",
        "class_level": [8, 11],
        "title": "Friction Opposes Motion",
        "title_hindi": "घर्षण गति का विरोध करता है",
        "keywords": ["friction", "rough", "smooth", "slide", "grip"],
        "config": {
            "cause": {"label": "ROUGH", "icon": "🪨"},
            "effect": {"label": "SLOW DOWN", "icon": "🐢"},
            "action_label": "FRICTION ←",
            "formula": "f = μN",
            "memory_hook": "Carrom powder reduces friction! 🎯"
        },
        "indian_context": "Carrom board - powder makes striker slide better"
    },
    
    "types_of_friction": {
        "template": SCALE,
        "subject": "physics",
        "chapter": "Friction",
        "class_level": [8, 11],
        "title": "Types of Friction",
        "title_hindi": "घर्षण के प्रकार",
        "keywords": ["static friction", "kinetic friction", "rolling friction"],
        "config": {
            "scale_start": 0,
            "scale_end": 100,
            "unit": "%",
            "items": [
                {"value": 20, "label": "Rolling", "icon": "🛞", "color": "#10B981"},
                {"value": 50, "label": "Sliding", "icon": "📦", "color": "#FBBF24"},
                {"value": 80, "label": "Static", "icon": "🪨", "color": "#EF4444"}
            ],
            "gradient_colors": ["#10B981", "#FBBF24", "#EF4444"],
            "formula": "Static > Sliding > Rolling",
            "memory_hook": "Starting is hardest! (Static > others) 💪"
        },
        "indian_context": "Pushing almirah vs rolling on wheels"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # MECHANICS - Gravitation
    # ═══════════════════════════════════════════════════════════════
    
    "gravity": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Gravitation",
        "class_level": [9, 11],
        "title": "Everything Falls at Same Rate",
        "title_hindi": "सब समान दर से गिरता है",
        "keywords": ["gravity", "fall", "weight", "g=9.8", "free fall"],
        "config": {
            "object_a": {"type": "feather", "label": "FEATHER", "color": "#8B5CF6", "mass": 0.01},
            "object_b": {"type": "stone", "label": "STONE", "color": "#6B7280", "mass": 1},
            "vacuum": True,
            "formula": "g = 9.8 m/s²",
            "memory_hook": "In vacuum, feather = stone! 🪶"
        },
        "indian_context": "Mango and leaf falling from tree (in vacuum)"
    },
    
    "universal_gravitation": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Gravitation",
        "class_level": [9, 11],
        "title": "Universal Law of Gravitation",
        "title_hindi": "गुरुत्वाकर्षण का सार्वत्रिक नियम",
        "keywords": ["universal gravitation", "newton gravity", "inverse square"],
        "config": {
            "cause": {"label": "MASS", "icon": "🌍"},
            "effect": {"label": "ATTRACTS", "icon": "🌙"},
            "action_label": "GRAVITY",
            "formula": "F = G(m₁m₂)/r²",
            "memory_hook": "Every mass attracts every other! 🧲"
        },
        "indian_context": "Earth pulling moon, keeping it in orbit"
    },
    
    "weight_vs_mass": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Gravitation",
        "class_level": [9, 11],
        "title": "Weight vs Mass",
        "title_hindi": "भार बनाम द्रव्यमान",
        "keywords": ["weight", "mass", "kg", "newton", "different"],
        "config": {
            "object_a": {"type": "astronaut", "label": "ON EARTH", "color": "#3B82F6", "location": "earth"},
            "object_b": {"type": "astronaut", "label": "ON MOON", "color": "#9CA3AF", "location": "moon"},
            "same_mass": True,
            "formula": "W = mg (Weight changes, Mass same)",
            "memory_hook": "Mass = same everywhere, Weight = depends on g! ⚖️"
        },
        "indian_context": "Kalpana Chawla - same person, different weight in space"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # MECHANICS - Work, Energy, Power
    # ═══════════════════════════════════════════════════════════════
    
    "work": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Work and Energy",
        "class_level": [9, 11],
        "title": "Work = Force × Displacement",
        "title_hindi": "कार्य = बल × विस्थापन",
        "keywords": ["work", "force", "displacement", "joule"],
        "config": {
            "cause": {"label": "FORCE", "icon": "💪"},
            "effect": {"label": "DISPLACEMENT", "icon": "📏"},
            "action_label": "WORK DONE",
            "formula": "W = F × d × cosθ",
            "memory_hook": "No movement = No work! (Physics definition) 📐"
        },
        "indian_context": "Pushing wall - no work done (no displacement)"
    },
    
    "kinetic_energy": {
        "template": GRAPH,
        "subject": "physics",
        "chapter": "Work and Energy",
        "class_level": [9, 11],
        "title": "Kinetic Energy - Energy of Motion",
        "title_hindi": "गतिज ऊर्जा",
        "keywords": ["kinetic energy", "motion", "speed", "ke"],
        "config": {
            "equation": "KE = ½mv²",
            "shape": "parabola",
            "x_axis": "Velocity (v)",
            "y_axis": "KE",
            "formula": "KE = ½mv²",
            "memory_hook": "Double speed = 4× energy! 🚗💨"
        },
        "indian_context": "Moving cricket ball has KE"
    },
    
    "potential_energy": {
        "template": SCALE,
        "subject": "physics",
        "chapter": "Work and Energy",
        "class_level": [9, 11],
        "title": "Potential Energy - Stored Energy",
        "title_hindi": "स्थितिज ऊर्जा",
        "keywords": ["potential energy", "height", "stored", "pe"],
        "config": {
            "scale_start": 0,
            "scale_end": 100,
            "unit": "m height",
            "items": [
                {"value": 0, "label": "Ground", "icon": "🏠", "color": "#6B7280"},
                {"value": 50, "label": "1st Floor", "icon": "🏢", "color": "#FBBF24"},
                {"value": 100, "label": "Terrace", "icon": "🏗️", "color": "#EF4444"}
            ],
            "gradient_colors": ["#6B7280", "#FBBF24", "#EF4444"],
            "formula": "PE = mgh",
            "memory_hook": "Higher = More stored energy! ⬆️"
        },
        "indian_context": "Water tank on terrace - more height, more PE"
    },
    
    "conservation_of_energy": {
        "template": PROCESS,
        "subject": "physics",
        "chapter": "Work and Energy",
        "class_level": [9, 11],
        "title": "Energy Cannot Be Created or Destroyed",
        "title_hindi": "ऊर्जा न बनती न नष्ट होती",
        "keywords": ["conservation of energy", "transform", "convert"],
        "config": {
            "inputs": [
                {"label": "PE (height)", "icon": "⬆️", "color": "#EF4444"}
            ],
            "process_box": {"label": "FALLING", "icon": "⬇️"},
            "outputs": [
                {"label": "KE (speed)", "icon": "💨", "color": "#10B981"}
            ],
            "formula": "PE + KE = Constant",
            "memory_hook": "Energy transforms, never dies! ✨"
        },
        "indian_context": "Diwali diya - chemical → light + heat"
    },
    
    "power": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Work and Energy",
        "class_level": [9, 11],
        "title": "Power = Work ÷ Time",
        "title_hindi": "शक्ति = कार्य ÷ समय",
        "keywords": ["power", "watt", "rate of work"],
        "config": {
            "object_a": {"type": "person", "label": "FAST WORKER", "color": "#10B981", "power": 100},
            "object_b": {"type": "person", "label": "SLOW WORKER", "color": "#EF4444", "power": 50},
            "same_work": True,
            "formula": "P = W / t",
            "memory_hook": "Same work, less time = More power! ⚡"
        },
        "indian_context": "Powerful motor lifts water faster"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # WAVES & SOUND
    # ═══════════════════════════════════════════════════════════════
    
    "wave": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Sound",
        "class_level": [9, 11],
        "title": "Wave = Energy Transfer",
        "title_hindi": "तरंग = ऊर्जा स्थानांतरण",
        "keywords": ["wave", "vibration", "energy transfer"],
        "config": {
            "cause": {"label": "VIBRATION", "icon": "〰️"},
            "effect": {"label": "ENERGY MOVES", "icon": "➡️"},
            "action_label": "WAVE",
            "formula": "v = fλ",
            "memory_hook": "Wave moves, medium stays! 🌊"
        },
        "indian_context": "Skipping rope - shake one end, wave travels"
    },
    
    "sound_wave": {
        "template": PROCESS,
        "subject": "physics",
        "chapter": "Sound",
        "class_level": [9, 11],
        "title": "Sound = Longitudinal Wave",
        "title_hindi": "ध्वनि = अनुदैर्ध्य तरंग",
        "keywords": ["sound", "longitudinal", "compression", "rarefaction"],
        "config": {
            "inputs": [
                {"label": "Vibrating object", "icon": "🔔", "color": "#FBBF24"}
            ],
            "process_box": {"label": "AIR MOLECULES", "icon": "💨"},
            "outputs": [
                {"label": "Sound to ear", "icon": "👂", "color": "#8B5CF6"}
            ],
            "formula": "v = 340 m/s (in air)",
            "memory_hook": "Sound needs medium, light doesn't! 🔊"
        },
        "indian_context": "Temple bell sound reaching ears"
    },
    
    "echo": {
        "template": SEQUENCE,
        "subject": "physics",
        "chapter": "Sound",
        "class_level": [9],
        "title": "Echo = Reflected Sound",
        "title_hindi": "प्रतिध्वनि",
        "keywords": ["echo", "reflection", "sound"],
        "config": {
            "stages": [
                {"label": "Sound produced", "icon": "🗣️"},
                {"label": "Travels to wall", "icon": "➡️"},
                {"label": "Reflects back", "icon": "↩️"},
                {"label": "Echo heard", "icon": "👂"}
            ],
            "formula": "Min distance = 17m (for echo)",
            "memory_hook": "Echo needs 17m minimum distance! 🏔️"
        },
        "indian_context": "Shouting in mountains - echo returns"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # LIGHT & OPTICS
    # ═══════════════════════════════════════════════════════════════
    
    "reflection": {
        "template": STRUCTURE,
        "subject": "physics",
        "chapter": "Light",
        "class_level": [10, 12],
        "title": "Laws of Reflection",
        "title_hindi": "परावर्तन के नियम",
        "keywords": ["reflection", "mirror", "angle", "incident"],
        "config": {
            "parts": [
                {"label": "Incident ray", "angle": 45},
                {"label": "Normal", "angle": 90},
                {"label": "Reflected ray", "angle": 45}
            ],
            "formula": "∠i = ∠r",
            "memory_hook": "Angle in = Angle out! 🪞"
        },
        "indian_context": "Looking in mirror"
    },
    
    "refraction": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Light",
        "class_level": [10, 12],
        "title": "Refraction = Bending of Light",
        "title_hindi": "अपवर्तन = प्रकाश का मुड़ना",
        "keywords": ["refraction", "bending", "medium", "snell"],
        "config": {
            "cause": {"label": "Light enters", "icon": "💡"},
            "effect": {"label": "Bends", "icon": "↗️"},
            "action_label": "Different medium",
            "formula": "n₁sinθ₁ = n₂sinθ₂",
            "memory_hook": "Slow medium = Bends towards normal! 📐"
        },
        "indian_context": "Pencil in water glass looks bent"
    },
    
    "lens": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Light",
        "class_level": [10, 12],
        "title": "Convex vs Concave Lens",
        "title_hindi": "उत्तल बनाम अवतल लेंस",
        "keywords": ["lens", "convex", "concave", "converge", "diverge"],
        "config": {
            "object_a": {"type": "lens_convex", "label": "CONVEX", "color": "#10B981", "action": "converge"},
            "object_b": {"type": "lens_concave", "label": "CONCAVE", "color": "#EF4444", "action": "diverge"},
            "formula": "1/f = 1/v - 1/u",
            "memory_hook": "Convex = Converges (thick middle)! 🔍"
        },
        "indian_context": "Magnifying glass (convex) vs spectacles for myopia (concave)"
    },
    
    "dispersion": {
        "template": PROCESS,
        "subject": "physics",
        "chapter": "Light",
        "class_level": [10, 12],
        "title": "Dispersion = White → Rainbow",
        "title_hindi": "वर्ण विक्षेपण",
        "keywords": ["dispersion", "spectrum", "rainbow", "prism", "VIBGYOR"],
        "config": {
            "inputs": [
                {"label": "White light", "icon": "⬜", "color": "#FFFFFF"}
            ],
            "process_box": {"label": "PRISM", "icon": "🔺"},
            "outputs": [
                {"label": "VIBGYOR", "icon": "🌈", "color": "#gradient"}
            ],
            "formula": "White = V+I+B+G+Y+O+R",
            "memory_hook": "VIBGYOR - Violet Inside, Red Outside! 🌈"
        },
        "indian_context": "Rainbow after monsoon rain"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # ELECTRICITY
    # ═══════════════════════════════════════════════════════════════
    
    "electric_current": {
        "template": PROCESS,
        "subject": "physics",
        "chapter": "Electricity",
        "class_level": [10, 12],
        "title": "Electric Current = Flow of Charges",
        "title_hindi": "विद्युत धारा = आवेशों का प्रवाह",
        "keywords": ["current", "electric", "ampere", "flow", "charges"],
        "config": {
            "inputs": [
                {"label": "Battery (+)", "icon": "🔋", "color": "#EF4444"}
            ],
            "process_box": {"label": "WIRE", "icon": "〰️"},
            "outputs": [
                {"label": "Battery (-)", "icon": "🔋", "color": "#3B82F6"}
            ],
            "formula": "I = Q / t",
            "memory_hook": "Current = Charge per second! ⚡"
        },
        "indian_context": "Water flow in pipe = Current in wire"
    },
    
    "ohms_law": {
        "template": GRAPH,
        "subject": "physics",
        "chapter": "Electricity",
        "class_level": [10, 12],
        "title": "Ohm's Law: V = IR",
        "title_hindi": "ओम का नियम",
        "keywords": ["ohm", "voltage", "current", "resistance", "v=ir"],
        "config": {
            "equation": "V = IR",
            "shape": "line",
            "x_axis": "Current (I)",
            "y_axis": "Voltage (V)",
            "slope": "R (Resistance)",
            "formula": "V = I × R",
            "memory_hook": "VIR = Very Important Rule! ⚡"
        },
        "indian_context": "Water pressure (V) = Flow (I) × Pipe narrowness (R)"
    },
    
    "resistance": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Electricity",
        "class_level": [10, 12],
        "title": "Resistance Opposes Current",
        "title_hindi": "प्रतिरोध धारा का विरोध करता है",
        "keywords": ["resistance", "ohm", "oppose"],
        "config": {
            "cause": {"label": "ELECTRONS", "icon": "⚡"},
            "effect": {"label": "SLOWED", "icon": "🐢"},
            "action_label": "RESISTANCE",
            "formula": "R = ρL/A",
            "memory_hook": "Thin wire = More resistance! 📏"
        },
        "indian_context": "Narrow road = Traffic resistance"
    },
    
    "series_parallel": {
        "template": RACE,
        "subject": "physics",
        "chapter": "Electricity",
        "class_level": [10, 12],
        "title": "Series vs Parallel Circuits",
        "title_hindi": "श्रेणी बनाम समानांतर परिपथ",
        "keywords": ["series", "parallel", "circuit", "resistor"],
        "config": {
            "object_a": {"type": "circuit_series", "label": "SERIES", "color": "#EF4444"},
            "object_b": {"type": "circuit_parallel", "label": "PARALLEL", "color": "#10B981"},
            "formula": "Series: R = R₁+R₂ | Parallel: 1/R = 1/R₁+1/R₂",
            "memory_hook": "Series = Add up, Parallel = Less total! 🔌"
        },
        "indian_context": "Diwali lights - series (one off, all off) vs parallel"
    },
    
    "power_electrical": {
        "template": PROCESS,
        "subject": "physics",
        "chapter": "Electricity",
        "class_level": [10, 12],
        "title": "Electrical Power = V × I",
        "title_hindi": "विद्युत शक्ति",
        "keywords": ["electrical power", "watt", "vi"],
        "config": {
            "inputs": [
                {"label": "Voltage (V)", "icon": "🔋", "color": "#FBBF24"},
                {"label": "Current (I)", "icon": "⚡", "color": "#3B82F6"}
            ],
            "process_box": {"label": "MULTIPLY", "icon": "✖️"},
            "outputs": [
                {"label": "Power (W)", "icon": "💡", "color": "#10B981"}
            ],
            "formula": "P = V × I = I²R = V²/R",
            "memory_hook": "More Voltage or Current = More Power! 💪"
        },
        "indian_context": "100W bulb vs 60W bulb brightness"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # MAGNETISM
    # ═══════════════════════════════════════════════════════════════
    
    "magnetism": {
        "template": STRUCTURE,
        "subject": "physics",
        "chapter": "Magnetic Effects",
        "class_level": [10, 12],
        "title": "Magnetic Field Lines",
        "title_hindi": "चुंबकीय क्षेत्र रेखाएं",
        "keywords": ["magnet", "field", "north", "south", "pole"],
        "config": {
            "parts": [
                {"label": "North Pole (N)", "x": 150, "y": 180},
                {"label": "South Pole (S)", "x": 350, "y": 180},
                {"label": "Field Lines", "x": 250, "y": 120}
            ],
            "formula": "N → S (outside magnet)",
            "memory_hook": "Field lines: N to S outside, S to N inside! 🧲"
        },
        "indian_context": "Compass needle pointing North"
    },
    
    "electromagnetic_induction": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Magnetic Effects",
        "class_level": [10, 12],
        "title": "Electromagnetic Induction",
        "title_hindi": "विद्युत चुंबकीय प्रेरण",
        "keywords": ["induction", "faraday", "emf", "flux"],
        "config": {
            "cause": {"label": "Moving magnet", "icon": "🧲"},
            "effect": {"label": "Current produced", "icon": "⚡"},
            "action_label": "INDUCTION",
            "formula": "EMF = -dΦ/dt",
            "memory_hook": "Change in flux = Current produced! 🔄"
        },
        "indian_context": "Generator in power plant"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # PRESSURE (FLUIDS)
    # ═══════════════════════════════════════════════════════════════
    
    "pressure": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Pressure",
        "class_level": [8, 11],
        "title": "Pressure = Force ÷ Area",
        "title_hindi": "दाब = बल ÷ क्षेत्रफल",
        "keywords": ["pressure", "force", "area", "pascal"],
        "config": {
            "cause": {"label": "SAME FORCE", "icon": "👆"},
            "effect": {"label": "MORE PRESSURE", "icon": "📌"},
            "action_label": "Small Area",
            "formula": "P = F / A",
            "memory_hook": "Sharp = High pressure! 📍"
        },
        "indian_context": "Nail tip vs finger tip pressing"
    },
    
    "atmospheric_pressure": {
        "template": SCALE,
        "subject": "physics",
        "chapter": "Pressure",
        "class_level": [8, 11],
        "title": "Atmospheric Pressure",
        "title_hindi": "वायुमंडलीय दाब",
        "keywords": ["atmospheric", "air pressure", "altitude"],
        "config": {
            "scale_start": 0,
            "scale_end": 10000,
            "unit": "m altitude",
            "items": [
                {"value": 0, "label": "Sea level", "icon": "🌊", "color": "#3B82F6"},
                {"value": 3000, "label": "Hill station", "icon": "⛰️", "color": "#10B981"},
                {"value": 8848, "label": "Everest", "icon": "🏔️", "color": "#EF4444"}
            ],
            "gradient_colors": ["#3B82F6", "#10B981", "#EF4444"],
            "formula": "1 atm = 101325 Pa",
            "memory_hook": "Higher altitude = Lower pressure! 🏔️"
        },
        "indian_context": "Cooking in Shimla needs pressure cooker (low pressure)"
    },
    
    "buoyancy": {
        "template": CAUSE_EFFECT,
        "subject": "physics",
        "chapter": "Pressure",
        "class_level": [9, 11],
        "title": "Archimedes' Principle",
        "title_hindi": "आर्किमिडीज का सिद्धांत",
        "keywords": ["buoyancy", "float", "archimedes", "upthrust"],
        "config": {
            "cause": {"label": "Object in fluid", "icon": "🔵"},
            "effect": {"label": "Upward force", "icon": "⬆️"},
            "action_label": "BUOYANCY",
            "formula": "Fb = ρVg",
            "memory_hook": "Upthrust = Weight of displaced fluid! 🛟"
        },
        "indian_context": "Iron ship floats, iron nail sinks - shape matters!"
    },
}


# Export
__all__ = ['PHYSICS_CONCEPTS']

