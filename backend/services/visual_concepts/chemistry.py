"""
🧪 CHEMISTRY Visual Concepts - Complete Coverage
================================================

Class 9-12, JEE, NEET level Chemistry concepts with visual templates.

Categories:
1. Atomic Structure
2. Periodic Table
3. Chemical Bonding
4. Acids, Bases & Salts
5. Chemical Reactions
6. Carbon & Organic Chemistry
7. Metals & Non-metals

Total: 40+ concepts
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


CHEMISTRY_CONCEPTS: Dict[str, Dict[str, Any]] = {
    
    # ═══════════════════════════════════════════════════════════════
    # ATOMIC STRUCTURE
    # ═══════════════════════════════════════════════════════════════
    
    "atom": {
        "template": STRUCTURE,
        "subject": "chemistry",
        "chapter": "Atomic Structure",
        "class_level": [9, 11],
        "title": "Atom - The Basic Unit",
        "title_hindi": "परमाणु - मूल इकाई",
        "keywords": ["atom", "electron", "proton", "neutron", "nucleus"],
        "config": {
            "parts": [
                {"label": "Nucleus", "x": 250, "y": 180, "labelX": 350, "labelY": 150, "color": "#EF4444"},
                {"label": "Proton (+)", "x": 240, "y": 175, "labelX": 140, "labelY": 140, "color": "#EF4444"},
                {"label": "Neutron (0)", "x": 260, "y": 185, "labelX": 360, "labelY": 200, "color": "#6B7280"},
                {"label": "Electron (-)", "x": 180, "y": 180, "labelX": 80, "labelY": 180, "color": "#3B82F6"}
            ],
            "formula": "Atom = Protons + Neutrons + Electrons",
            "memory_hook": "Atom is like a joint family - nucleus is home! 👨‍👩‍👧‍👦"
        },
        "indian_context": "Joint family - parents (nucleus) with kids (electrons)"
    },
    
    "atomic_number": {
        "template": CAUSE_EFFECT,
        "subject": "chemistry",
        "chapter": "Atomic Structure",
        "class_level": [9, 11],
        "title": "Atomic Number = Number of Protons",
        "title_hindi": "परमाणु क्रमांक",
        "keywords": ["atomic number", "proton", "z number"],
        "config": {
            "cause": {"label": "PROTONS", "icon": "🔴"},
            "effect": {"label": "IDENTITY", "icon": "🎫"},
            "action_label": "= Atomic Number (Z)",
            "formula": "Z = Number of Protons",
            "memory_hook": "Protons = Identity card of element! 🎫"
        },
        "indian_context": "Aadhaar number - unique identifier"
    },
    
    "mass_number": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Atomic Structure",
        "class_level": [9, 11],
        "title": "Mass Number = Protons + Neutrons",
        "title_hindi": "द्रव्यमान संख्या",
        "keywords": ["mass number", "proton", "neutron", "a number"],
        "config": {
            "inputs": [
                {"label": "Protons", "icon": "🔴", "color": "#EF4444"},
                {"label": "Neutrons", "icon": "⚪", "color": "#6B7280"}
            ],
            "process_box": {"label": "ADD", "icon": "➕"},
            "outputs": [
                {"label": "Mass Number (A)", "icon": "⚖️", "color": "#8B5CF6"}
            ],
            "formula": "A = Z + N",
            "memory_hook": "Mass = Protons + Neutrons (electrons too light!) ⚖️"
        },
        "indian_context": "Weight of family = adults only (kids too light)"
    },
    
    "isotopes": {
        "template": RACE,
        "subject": "chemistry",
        "chapter": "Atomic Structure",
        "class_level": [9, 11],
        "title": "Isotopes - Same Element, Different Mass",
        "title_hindi": "समस्थानिक",
        "keywords": ["isotope", "same proton", "different neutron"],
        "config": {
            "object_a": {"type": "atom", "label": "C-12", "color": "#10B981", "protons": 6, "neutrons": 6},
            "object_b": {"type": "atom", "label": "C-14", "color": "#3B82F6", "protons": 6, "neutrons": 8},
            "same_protons": True,
            "formula": "Same Z, Different A",
            "memory_hook": "Brothers - same father (protons), different weight! 👬"
        },
        "indian_context": "Brothers in family - same parents, different weights"
    },
    
    "electron_configuration": {
        "template": SEQUENCE,
        "subject": "chemistry",
        "chapter": "Atomic Structure",
        "class_level": [9, 11],
        "title": "Electron Shells - K, L, M, N",
        "title_hindi": "इलेक्ट्रॉन कोश",
        "keywords": ["shell", "orbit", "electron configuration", "2n squared"],
        "config": {
            "stages": [
                {"label": "K shell", "max": 2, "formula": "2×1² = 2"},
                {"label": "L shell", "max": 8, "formula": "2×2² = 8"},
                {"label": "M shell", "max": 18, "formula": "2×3² = 18"},
                {"label": "N shell", "max": 32, "formula": "2×4² = 32"}
            ],
            "formula": "Max electrons = 2n²",
            "memory_hook": "2n² = 2, 8, 18, 32 - Memorize this pattern! 🎯"
        },
        "indian_context": "Like seats in cinema - front rows have fewer seats"
    },
    
    "valency": {
        "template": SCALE,
        "subject": "chemistry",
        "chapter": "Atomic Structure",
        "class_level": [9, 11],
        "title": "Valency - Combining Capacity",
        "title_hindi": "संयोजकता",
        "keywords": ["valency", "valence", "combining", "outermost"],
        "config": {
            "scale_start": 0,
            "scale_end": 4,
            "unit": "",
            "items": [
                {"value": 0, "label": "Noble gas", "icon": "💎", "color": "#6B7280"},
                {"value": 1, "label": "Na, K", "icon": "🧂", "color": "#FBBF24"},
                {"value": 2, "label": "Mg, Ca", "icon": "🔵", "color": "#10B981"},
                {"value": 3, "label": "Al", "icon": "🔺", "color": "#3B82F6"},
                {"value": 4, "label": "C, Si", "icon": "⬛", "color": "#8B5CF6"}
            ],
            "gradient_colors": ["#6B7280", "#FBBF24", "#10B981", "#3B82F6", "#8B5CF6"],
            "formula": "Valency = 8 - valence electrons (if > 4)",
            "memory_hook": "Valency = How many hands to hold! 🤝"
        },
        "indian_context": "How many friends can you hold hands with?"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # PERIODIC TABLE
    # ═══════════════════════════════════════════════════════════════
    
    "periodic_table": {
        "template": STRUCTURE,
        "subject": "chemistry",
        "chapter": "Periodic Classification",
        "class_level": [10, 11],
        "title": "Periodic Table Organization",
        "title_hindi": "आवर्त सारणी",
        "keywords": ["periodic table", "groups", "periods", "mendeleev"],
        "config": {
            "parts": [
                {"label": "Period (row) = Shells", "x": 100, "y": 150},
                {"label": "Group (column) = Valence e⁻", "x": 400, "y": 150},
                {"label": "Metals (left)", "x": 150, "y": 250},
                {"label": "Non-metals (right)", "x": 350, "y": 250}
            ],
            "formula": "Period = n, Group = Valence electrons",
            "memory_hook": "Rows = Shells, Columns = Valence electrons! 📊"
        },
        "indian_context": "Seating arrangement in class - rows and columns"
    },
    
    "periodic_trends_size": {
        "template": SCALE,
        "subject": "chemistry",
        "chapter": "Periodic Classification",
        "class_level": [10, 11],
        "title": "Atomic Size Trends",
        "title_hindi": "परमाणु आकार प्रवृत्ति",
        "keywords": ["atomic size", "radius", "trend"],
        "config": {
            "scale_start": 0,
            "scale_end": 100,
            "unit": "pm",
            "items": [
                {"value": 25, "label": "F", "icon": "🔵", "color": "#3B82F6"},
                {"value": 50, "label": "Cl", "icon": "🟢", "color": "#10B981"},
                {"value": 75, "label": "Br", "icon": "🟠", "color": "#F97316"},
                {"value": 100, "label": "I", "icon": "🟣", "color": "#8B5CF6"}
            ],
            "gradient_colors": ["#3B82F6", "#10B981", "#F97316", "#8B5CF6"],
            "formula": "Size: ↓ down group, ← across period",
            "memory_hook": "Down = Bigger (more shells), Right = Smaller (more pull)! 📏"
        },
        "indian_context": "Younger siblings in bigger clothes down generations"
    },
    
    "metals_nonmetals": {
        "template": RACE,
        "subject": "chemistry",
        "chapter": "Periodic Classification",
        "class_level": [8, 10],
        "title": "Metals vs Non-metals",
        "title_hindi": "धातु बनाम अधातु",
        "keywords": ["metal", "non-metal", "properties"],
        "config": {
            "object_a": {"type": "element", "label": "METAL", "color": "#FBBF24", "properties": ["shiny", "conductor", "malleable"]},
            "object_b": {"type": "element", "label": "NON-METAL", "color": "#6B7280", "properties": ["dull", "insulator", "brittle"]},
            "formula": "Metals = Left side, Non-metals = Right side",
            "memory_hook": "Metals = Good conductors (like copper wire)! ⚡"
        },
        "indian_context": "Gold jewelry (metal) vs coal (non-metal)"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # CHEMICAL BONDING
    # ═══════════════════════════════════════════════════════════════
    
    "ionic_bond": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Chemical Bonding",
        "class_level": [10, 11],
        "title": "Ionic Bond - Transfer of Electrons",
        "title_hindi": "आयनिक बंधन",
        "keywords": ["ionic", "bond", "transfer", "nacl", "electrovalent"],
        "config": {
            "inputs": [
                {"label": "Na (loses e⁻)", "icon": "🔵", "color": "#3B82F6"},
                {"label": "Cl (gains e⁻)", "icon": "🟢", "color": "#10B981"}
            ],
            "process_box": {"label": "TRANSFER", "icon": "➡️"},
            "outputs": [
                {"label": "Na⁺ Cl⁻ (NaCl)", "icon": "🧂", "color": "#FBBF24"}
            ],
            "formula": "Na → Na⁺ + e⁻ | Cl + e⁻ → Cl⁻",
            "memory_hook": "Give and Take = Ionic bond! 🤝"
        },
        "indian_context": "Marriage - family gives daughter, other family receives"
    },
    
    "covalent_bond": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Chemical Bonding",
        "class_level": [10, 11],
        "title": "Covalent Bond - Sharing of Electrons",
        "title_hindi": "सहसंयोजक बंधन",
        "keywords": ["covalent", "bond", "sharing", "molecule"],
        "config": {
            "inputs": [
                {"label": "H (1 e⁻)", "icon": "🔴", "color": "#EF4444"},
                {"label": "H (1 e⁻)", "icon": "🔴", "color": "#EF4444"}
            ],
            "process_box": {"label": "SHARE", "icon": "🤝"},
            "outputs": [
                {"label": "H₂ molecule", "icon": "⚛️", "color": "#8B5CF6"}
            ],
            "formula": "H· + ·H → H:H (H₂)",
            "memory_hook": "Sharing is caring = Covalent! 💕"
        },
        "indian_context": "Friends sharing lunch - both benefit"
    },
    
    "metallic_bond": {
        "template": STRUCTURE,
        "subject": "chemistry",
        "chapter": "Chemical Bonding",
        "class_level": [11, 12],
        "title": "Metallic Bond - Sea of Electrons",
        "title_hindi": "धात्विक बंधन",
        "keywords": ["metallic", "bond", "sea of electrons", "delocalized"],
        "config": {
            "parts": [
                {"label": "Metal ions (+)", "x": 200, "y": 180},
                {"label": "Free electrons", "x": 300, "y": 180},
                {"label": "Sea of e⁻", "x": 250, "y": 250}
            ],
            "formula": "Metal = Positive ions in electron sea",
            "memory_hook": "Metals = Positive islands in electron ocean! 🌊"
        },
        "indian_context": "Coins in a jar - electrons moving freely"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # ACIDS, BASES & SALTS
    # ═══════════════════════════════════════════════════════════════
    
    "acids": {
        "template": SCALE,
        "subject": "chemistry",
        "chapter": "Acids Bases Salts",
        "class_level": [10],
        "title": "Acids - pH < 7",
        "title_hindi": "अम्ल",
        "keywords": ["acid", "sour", "ph", "hydrogen ion", "h+"],
        "config": {
            "scale_start": 0,
            "scale_end": 7,
            "unit": "pH",
            "items": [
                {"value": 1, "label": "HCl", "icon": "🧪", "color": "#EF4444"},
                {"value": 2, "label": "Lemon", "icon": "🍋", "color": "#FBBF24"},
                {"value": 3, "label": "Vinegar", "icon": "🫗", "color": "#F97316"},
                {"value": 6, "label": "Milk", "icon": "🥛", "color": "#F3F4F6"}
            ],
            "gradient_colors": ["#EF4444", "#FBBF24", "#F97316", "#F3F4F6"],
            "formula": "Acid → H⁺ ions in water",
            "memory_hook": "Sour = Acidic! (Nimbu paani) 🍋"
        },
        "indian_context": "Nimbu paani, imli, dahi - all sour (acidic)"
    },
    
    "bases": {
        "template": SCALE,
        "subject": "chemistry",
        "chapter": "Acids Bases Salts",
        "class_level": [10],
        "title": "Bases - pH > 7",
        "title_hindi": "क्षार",
        "keywords": ["base", "bitter", "soapy", "hydroxide", "oh-"],
        "config": {
            "scale_start": 7,
            "scale_end": 14,
            "unit": "pH",
            "items": [
                {"value": 8, "label": "Baking soda", "icon": "🧁", "color": "#93C5FD"},
                {"value": 10, "label": "Soap", "icon": "🧼", "color": "#60A5FA"},
                {"value": 12, "label": "Bleach", "icon": "🫧", "color": "#3B82F6"},
                {"value": 14, "label": "NaOH", "icon": "⚗️", "color": "#1D4ED8"}
            ],
            "gradient_colors": ["#93C5FD", "#60A5FA", "#3B82F6", "#1D4ED8"],
            "formula": "Base → OH⁻ ions in water",
            "memory_hook": "Soapy/bitter = Basic! 🧼"
        },
        "indian_context": "Soap water feels slippery - basic"
    },
    
    "ph_scale": {
        "template": SCALE,
        "subject": "chemistry",
        "chapter": "Acids Bases Salts",
        "class_level": [10],
        "title": "pH Scale - 0 to 14",
        "title_hindi": "pH स्केल",
        "keywords": ["ph scale", "acid base", "neutral"],
        "config": {
            "scale_start": 0,
            "scale_end": 14,
            "unit": "",
            "items": [
                {"value": 0, "label": "Strong Acid", "icon": "🔴", "color": "#EF4444"},
                {"value": 7, "label": "Neutral", "icon": "💧", "color": "#10B981"},
                {"value": 14, "label": "Strong Base", "icon": "🔵", "color": "#3B82F6"}
            ],
            "gradient_colors": ["#EF4444", "#FBBF24", "#10B981", "#60A5FA", "#3B82F6"],
            "formula": "pH = -log[H⁺]",
            "memory_hook": "7 = Neutral (like pure water)! 💧"
        },
        "indian_context": "0-14 scale like temperature"
    },
    
    "neutralization": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Acids Bases Salts",
        "class_level": [10],
        "title": "Acid + Base = Salt + Water",
        "title_hindi": "उदासीनीकरण",
        "keywords": ["neutralization", "acid base", "salt water"],
        "config": {
            "inputs": [
                {"label": "Acid (HCl)", "icon": "🔴", "color": "#EF4444"},
                {"label": "Base (NaOH)", "icon": "🔵", "color": "#3B82F6"}
            ],
            "process_box": {"label": "REACT", "icon": "⚡"},
            "outputs": [
                {"label": "Salt (NaCl)", "icon": "🧂", "color": "#FBBF24"},
                {"label": "Water", "icon": "💧", "color": "#60A5FA"}
            ],
            "formula": "HCl + NaOH → NaCl + H₂O",
            "memory_hook": "Acid + Base = Salt + Water (Always!) 🧂"
        },
        "indian_context": "Antacid (base) neutralizes stomach acid"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # CHEMICAL REACTIONS
    # ═══════════════════════════════════════════════════════════════
    
    "chemical_equation": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Chemical Reactions",
        "class_level": [10],
        "title": "Chemical Equation - Balanced",
        "title_hindi": "रासायनिक समीकरण",
        "keywords": ["chemical equation", "reactant", "product", "balanced"],
        "config": {
            "inputs": [
                {"label": "Reactants", "icon": "⬅️", "color": "#EF4444"}
            ],
            "process_box": {"label": "ARROW →", "icon": "➡️"},
            "outputs": [
                {"label": "Products", "icon": "➡️", "color": "#10B981"}
            ],
            "formula": "Reactants → Products",
            "memory_hook": "Left side = Reactants, Right = Products! 📝"
        },
        "indian_context": "Recipe - ingredients → dish"
    },
    
    "combination_reaction": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Chemical Reactions",
        "class_level": [10],
        "title": "Combination - A + B → AB",
        "title_hindi": "संयोजन अभिक्रिया",
        "keywords": ["combination", "synthesis", "a+b"],
        "config": {
            "inputs": [
                {"label": "A", "icon": "🔵", "color": "#3B82F6"},
                {"label": "B", "icon": "🔴", "color": "#EF4444"}
            ],
            "process_box": {"label": "COMBINE", "icon": "🤝"},
            "outputs": [
                {"label": "AB", "icon": "🟣", "color": "#8B5CF6"}
            ],
            "formula": "A + B → AB",
            "memory_hook": "Two become one! (Marriage) 💒"
        },
        "indian_context": "Iron + Oxygen = Rust"
    },
    
    "decomposition_reaction": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Chemical Reactions",
        "class_level": [10],
        "title": "Decomposition - AB → A + B",
        "title_hindi": "अपघटन अभिक्रिया",
        "keywords": ["decomposition", "break down", "thermal"],
        "config": {
            "inputs": [
                {"label": "AB", "icon": "🟣", "color": "#8B5CF6"}
            ],
            "process_box": {"label": "HEAT/LIGHT", "icon": "🔥"},
            "outputs": [
                {"label": "A", "icon": "🔵", "color": "#3B82F6"},
                {"label": "B", "icon": "🔴", "color": "#EF4444"}
            ],
            "formula": "AB → A + B",
            "memory_hook": "One breaks into many! (Divorce) 💔"
        },
        "indian_context": "CaCO₃ → Cite lime (chuna) + CO₂ when heated"
    },
    
    "displacement_reaction": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Chemical Reactions",
        "class_level": [10],
        "title": "Displacement - More Reactive Wins",
        "title_hindi": "विस्थापन अभिक्रिया",
        "keywords": ["displacement", "reactive", "replace"],
        "config": {
            "inputs": [
                {"label": "Zn (more reactive)", "icon": "⚪", "color": "#6B7280"},
                {"label": "CuSO₄ (blue)", "icon": "🔵", "color": "#3B82F6"}
            ],
            "process_box": {"label": "DISPLACE", "icon": "🔄"},
            "outputs": [
                {"label": "ZnSO₄ (colorless)", "icon": "⚪", "color": "#F3F4F6"},
                {"label": "Cu (brown)", "icon": "🟤", "color": "#B45309"}
            ],
            "formula": "Zn + CuSO₄ → ZnSO₄ + Cu",
            "memory_hook": "Stronger player replaces weaker! 💪"
        },
        "indian_context": "Like cricket - better player replaces weak one"
    },
    
    "oxidation_reduction": {
        "template": RACE,
        "subject": "chemistry",
        "chapter": "Chemical Reactions",
        "class_level": [10, 12],
        "title": "Oxidation vs Reduction",
        "title_hindi": "ऑक्सीकरण व अपचयन",
        "keywords": ["oxidation", "reduction", "redox", "electron"],
        "config": {
            "object_a": {"type": "process", "label": "OXIDATION", "color": "#EF4444", "action": "Loses e⁻"},
            "object_b": {"type": "process", "label": "REDUCTION", "color": "#3B82F6", "action": "Gains e⁻"},
            "formula": "OIL RIG: Oxidation Is Loss, Reduction Is Gain",
            "memory_hook": "OIL RIG - Oxidation Is Loss, Reduction Is Gain! 🛢️"
        },
        "indian_context": "Rusting = Oxidation, Extracting metal = Reduction"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # CARBON & ORGANIC CHEMISTRY
    # ═══════════════════════════════════════════════════════════════
    
    "carbon_bonding": {
        "template": STRUCTURE,
        "subject": "chemistry",
        "chapter": "Carbon Compounds",
        "class_level": [10],
        "title": "Carbon - Tetravalent Element",
        "title_hindi": "कार्बन - चतुर्संयोजी",
        "keywords": ["carbon", "tetravalent", "catenation", "four bonds"],
        "config": {
            "parts": [
                {"label": "4 bonds possible", "x": 250, "y": 150},
                {"label": "Can form chains", "x": 150, "y": 220},
                {"label": "Can form rings", "x": 350, "y": 220}
            ],
            "formula": "Carbon has 4 valence electrons",
            "memory_hook": "Carbon = 4 hands to hold friends! ✋"
        },
        "indian_context": "Carbon is the backbone of life - in all living things"
    },
    
    "hydrocarbons": {
        "template": SEQUENCE,
        "subject": "chemistry",
        "chapter": "Carbon Compounds",
        "class_level": [10],
        "title": "Hydrocarbons - C and H only",
        "title_hindi": "हाइड्रोकार्बन",
        "keywords": ["hydrocarbon", "alkane", "alkene", "alkyne"],
        "config": {
            "stages": [
                {"label": "Alkane (-ane)", "formula": "C-C single bond", "example": "Methane CH₄"},
                {"label": "Alkene (-ene)", "formula": "C=C double bond", "example": "Ethene C₂H₄"},
                {"label": "Alkyne (-yne)", "formula": "C≡C triple bond", "example": "Ethyne C₂H₂"}
            ],
            "formula": "CₙH₂ₙ₊₂ (alkane) | CₙH₂ₙ (alkene) | CₙH₂ₙ₋₂ (alkyne)",
            "memory_hook": "ANE, ENE, YNE = Single, Double, Triple! 123"
        },
        "indian_context": "LPG (propane, butane) = Alkanes"
    },
    
    "functional_groups": {
        "template": SCALE,
        "subject": "chemistry",
        "chapter": "Carbon Compounds",
        "class_level": [10, 12],
        "title": "Functional Groups in Organic Chemistry",
        "title_hindi": "क्रियात्मक समूह",
        "keywords": ["functional group", "alcohol", "aldehyde", "ketone", "carboxylic"],
        "config": {
            "scale_start": 0,
            "scale_end": 4,
            "unit": "",
            "items": [
                {"value": 0, "label": "Alcohol -OH", "icon": "🍺", "color": "#10B981"},
                {"value": 1, "label": "Aldehyde -CHO", "icon": "🧪", "color": "#FBBF24"},
                {"value": 2, "label": "Ketone -CO-", "icon": "⚗️", "color": "#F97316"},
                {"value": 3, "label": "Acid -COOH", "icon": "🍋", "color": "#EF4444"}
            ],
            "gradient_colors": ["#10B981", "#FBBF24", "#F97316", "#EF4444"],
            "formula": "-OH, -CHO, -CO-, -COOH",
            "memory_hook": "OH! A CHO told CO to eat COOH! 🤣"
        },
        "indian_context": "Ethanol (alcohol), Acetic acid (vinegar)"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # METALS AND NON-METALS
    # ═══════════════════════════════════════════════════════════════
    
    "reactivity_series": {
        "template": SCALE,
        "subject": "chemistry",
        "chapter": "Metals and Non-metals",
        "class_level": [10],
        "title": "Reactivity Series of Metals",
        "title_hindi": "धातुओं की क्रियाशीलता श्रेणी",
        "keywords": ["reactivity", "series", "active", "metal"],
        "config": {
            "scale_start": 0,
            "scale_end": 100,
            "unit": "",
            "items": [
                {"value": 95, "label": "K, Na", "icon": "💥", "color": "#EF4444"},
                {"value": 70, "label": "Mg, Al", "icon": "🔥", "color": "#F97316"},
                {"value": 50, "label": "Zn, Fe", "icon": "⚡", "color": "#FBBF24"},
                {"value": 20, "label": "Cu, Ag", "icon": "✨", "color": "#10B981"},
                {"value": 5, "label": "Au, Pt", "icon": "👑", "color": "#8B5CF6"}
            ],
            "gradient_colors": ["#EF4444", "#F97316", "#FBBF24", "#10B981", "#8B5CF6"],
            "formula": "K Na Ca Mg Al Zn Fe Ni Sn Pb H Cu Hg Ag Pt Au",
            "memory_hook": "King Nathan Can Make A Zoo In Nice Sunny Place Having Cute Happy Silver Platypus And Unicorn! 👑"
        },
        "indian_context": "Gold (Au) doesn't rust - least reactive"
    },
    
    "extraction_of_metals": {
        "template": SEQUENCE,
        "subject": "chemistry",
        "chapter": "Metals and Non-metals",
        "class_level": [10, 12],
        "title": "Extraction of Metals",
        "title_hindi": "धातुओं का निष्कर्षण",
        "keywords": ["extraction", "ore", "reduction", "refining"],
        "config": {
            "stages": [
                {"label": "Mining ore", "icon": "⛏️"},
                {"label": "Concentration", "icon": "🔄"},
                {"label": "Reduction", "icon": "🔥"},
                {"label": "Refining", "icon": "✨"}
            ],
            "formula": "Ore → Concentration → Reduction → Pure Metal",
            "memory_hook": "Dig → Clean → Heat → Shine! ⛏️→✨"
        },
        "indian_context": "Iron extraction from iron ore in Jamshedpur"
    },
    
    "corrosion": {
        "template": PROCESS,
        "subject": "chemistry",
        "chapter": "Metals and Non-metals",
        "class_level": [10],
        "title": "Corrosion - Slow Oxidation",
        "title_hindi": "संक्षारण",
        "keywords": ["corrosion", "rust", "oxidation"],
        "config": {
            "inputs": [
                {"label": "Iron (Fe)", "icon": "🔩", "color": "#6B7280"},
                {"label": "O₂ + H₂O", "icon": "💧", "color": "#3B82F6"}
            ],
            "process_box": {"label": "TIME", "icon": "⏰"},
            "outputs": [
                {"label": "Rust (Fe₂O₃)", "icon": "🟤", "color": "#B45309"}
            ],
            "formula": "4Fe + 3O₂ + 6H₂O → 4Fe(OH)₃ → 2Fe₂O₃·3H₂O",
            "memory_hook": "Iron + Air + Water = Rust (enemy of gates!) 🚪"
        },
        "indian_context": "Old iron gate rusting in monsoon"
    },
}


# Export
__all__ = ['CHEMISTRY_CONCEPTS']

