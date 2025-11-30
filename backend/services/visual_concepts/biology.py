"""
🌿 BIOLOGY Visual Concepts - Complete Coverage
==============================================

Class 9-12, NEET level Biology concepts with visual templates.

Categories:
1. Cell Biology
2. Life Processes (Nutrition, Respiration, Transport, Excretion)
3. Control & Coordination
4. Reproduction
5. Genetics & Evolution
6. Ecology & Environment

Total: 45+ concepts
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


BIOLOGY_CONCEPTS: Dict[str, Dict[str, Any]] = {
    
    # ═══════════════════════════════════════════════════════════════
    # CELL BIOLOGY
    # ═══════════════════════════════════════════════════════════════
    
    "cell": {
        "template": STRUCTURE,
        "subject": "biology",
        "chapter": "The Fundamental Unit of Life",
        "class_level": [9, 11],
        "title": "Cell - The Basic Unit of Life",
        "title_hindi": "कोशिका - जीवन की मूल इकाई",
        "keywords": ["cell", "nucleus", "cytoplasm", "organelle"],
        "config": {
            "parts": [
                {"label": "Cell membrane", "x": 250, "y": 100, "labelX": 360, "labelY": 80},
                {"label": "Nucleus (brain)", "x": 250, "y": 180, "labelX": 360, "labelY": 160},
                {"label": "Mitochondria (powerhouse)", "x": 180, "y": 220, "labelX": 70, "labelY": 220},
                {"label": "Ribosome (protein factory)", "x": 300, "y": 240, "labelX": 410, "labelY": 240},
                {"label": "Cytoplasm (jelly)", "x": 200, "y": 160, "labelX": 90, "labelY": 140}
            ],
            "formula": "Cell = Membrane + Cytoplasm + Nucleus + Organelles",
            "memory_hook": "Cell is a mini city with departments! 🏙️"
        },
        "indian_context": "Cell = Mumbai city with different areas doing different jobs"
    },
    
    "cell_membrane": {
        "template": PROCESS,
        "subject": "biology",
        "chapter": "The Fundamental Unit of Life",
        "class_level": [9, 11],
        "title": "Cell Membrane - Selective Barrier",
        "title_hindi": "कोशिका झिल्ली",
        "keywords": ["cell membrane", "plasma membrane", "selective", "permeable"],
        "config": {
            "inputs": [
                {"label": "Nutrients (in)", "icon": "🍎", "color": "#10B981"},
                {"label": "Waste (out)", "icon": "🗑️", "color": "#EF4444"}
            ],
            "process_box": {"label": "CELL MEMBRANE", "icon": "🚧"},
            "outputs": [
                {"label": "Selective entry", "icon": "✅", "color": "#3B82F6"}
            ],
            "formula": "Selectively permeable = Allows some, blocks others",
            "memory_hook": "Cell membrane = Security guard at gate! 🚔"
        },
        "indian_context": "Like security guard at society gate - checks who enters"
    },
    
    "plant_vs_animal_cell": {
        "template": RACE,
        "subject": "biology",
        "chapter": "The Fundamental Unit of Life",
        "class_level": [9, 11],
        "title": "Plant Cell vs Animal Cell",
        "title_hindi": "पादप कोशिका बनाम जंतु कोशिका",
        "keywords": ["plant cell", "animal cell", "cell wall", "chloroplast", "vacuole"],
        "config": {
            "object_a": {"type": "cell", "label": "PLANT CELL", "color": "#10B981", "extras": ["cell wall", "chloroplast", "large vacuole"]},
            "object_b": {"type": "cell", "label": "ANIMAL CELL", "color": "#EF4444", "extras": ["no cell wall", "no chloroplast", "small vacuoles"]},
            "formula": "Plant = Cell wall + Chloroplast + Large vacuole",
            "memory_hook": "Plants have WALL (protection) + GREEN (chloroplast)! 🌿"
        },
        "indian_context": "Plant cell = House with boundary wall, Animal cell = Tent"
    },
    
    "mitosis": {
        "template": SEQUENCE,
        "subject": "biology",
        "chapter": "Cell Division",
        "class_level": [10, 11],
        "title": "Mitosis - Identical Cell Division",
        "title_hindi": "समसूत्री विभाजन",
        "keywords": ["mitosis", "cell division", "pmat", "identical"],
        "config": {
            "stages": [
                {"label": "Prophase", "icon": "🧬", "description": "Chromosomes condense"},
                {"label": "Metaphase", "icon": "➖", "description": "Line up at center"},
                {"label": "Anaphase", "icon": "↔️", "description": "Pull apart"},
                {"label": "Telophase", "icon": "⭕⭕", "description": "Two nuclei form"}
            ],
            "formula": "1 cell → 2 identical cells (2n → 2n)",
            "memory_hook": "PMAT = Pizza Makes A Treat! 🍕"
        },
        "indian_context": "Xerox copy - exact duplicate"
    },
    
    "meiosis": {
        "template": SEQUENCE,
        "subject": "biology",
        "chapter": "Cell Division",
        "class_level": [10, 11],
        "title": "Meiosis - Half the Chromosomes",
        "title_hindi": "अर्धसूत्री विभाजन",
        "keywords": ["meiosis", "gametes", "haploid", "crossing over"],
        "config": {
            "stages": [
                {"label": "Meiosis I", "icon": "1️⃣", "description": "2n → n (halving)"},
                {"label": "Crossing over", "icon": "🔀", "description": "Gene mixing"},
                {"label": "Meiosis II", "icon": "2️⃣", "description": "Like mitosis"},
                {"label": "4 gametes", "icon": "🎲", "description": "All different"}
            ],
            "formula": "1 cell (2n) → 4 gametes (n)",
            "memory_hook": "Meiosis = Making Eggs and Sperm (different each time)! 🎲"
        },
        "indian_context": "Making unique lottery tickets - no two same"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # LIFE PROCESSES - NUTRITION
    # ═══════════════════════════════════════════════════════════════
    
    "photosynthesis": {
        "template": PROCESS,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Photosynthesis - Plants Making Food",
        "title_hindi": "प्रकाश संश्लेषण",
        "keywords": ["photosynthesis", "chlorophyll", "glucose", "oxygen"],
        "config": {
            "inputs": [
                {"label": "CO₂ (from air)", "icon": "💨", "color": "#6B7280"},
                {"label": "H₂O (from soil)", "icon": "💧", "color": "#3B82F6"},
                {"label": "Sunlight", "icon": "☀️", "color": "#FBBF24"}
            ],
            "process_box": {"label": "CHLOROPLAST", "icon": "🌿"},
            "outputs": [
                {"label": "Glucose (food)", "icon": "🍬", "color": "#F59E0B"},
                {"label": "O₂ (released)", "icon": "💨", "color": "#10B981"}
            ],
            "formula": "6CO₂ + 6H₂O + Light → C₆H₁₂O₆ + 6O₂",
            "memory_hook": "Plants are tiny FOOD FACTORIES! 🏭"
        },
        "indian_context": "Tulsi plant on balcony making food using sunlight"
    },
    
    "nutrition_types": {
        "template": RACE,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10],
        "title": "Autotrophs vs Heterotrophs",
        "title_hindi": "स्वपोषी बनाम परपोषी",
        "keywords": ["autotroph", "heterotroph", "producer", "consumer"],
        "config": {
            "object_a": {"type": "organism", "label": "AUTOTROPH", "color": "#10B981", "example": "Plants"},
            "object_b": {"type": "organism", "label": "HETEROTROPH", "color": "#EF4444", "example": "Animals"},
            "formula": "Auto = Self-feeder | Hetero = Other-feeder",
            "memory_hook": "AUTO = Automatic food maker (plants)! 🌱"
        },
        "indian_context": "Plants = Cook at home, Animals = Order from outside"
    },
    
    "human_digestion": {
        "template": SEQUENCE,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Human Digestive System",
        "title_hindi": "मानव पाचन तंत्र",
        "keywords": ["digestion", "stomach", "intestine", "enzyme"],
        "config": {
            "stages": [
                {"label": "Mouth", "icon": "👄", "action": "Chew + Saliva (starch → maltose)"},
                {"label": "Stomach", "icon": "🫃", "action": "HCl + Pepsin (protein → peptides)"},
                {"label": "Small intestine", "icon": "🌀", "action": "Absorption of nutrients"},
                {"label": "Large intestine", "icon": "📦", "action": "Water absorption"},
                {"label": "Exit", "icon": "🚪", "action": "Waste removal"}
            ],
            "formula": "Food → Mouth → Stomach → Small intestine → Large intestine",
            "memory_hook": "Food's 24-hour journey through body! 🚂"
        },
        "indian_context": "Roti's journey from mouth to energy"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # LIFE PROCESSES - RESPIRATION
    # ═══════════════════════════════════════════════════════════════
    
    "respiration": {
        "template": PROCESS,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Cellular Respiration - Energy Release",
        "title_hindi": "कोशिकीय श्वसन",
        "keywords": ["respiration", "atp", "glucose", "oxygen", "energy"],
        "config": {
            "inputs": [
                {"label": "Glucose (C₆H₁₂O₆)", "icon": "🍬", "color": "#F59E0B"},
                {"label": "Oxygen (O₂)", "icon": "💨", "color": "#3B82F6"}
            ],
            "process_box": {"label": "MITOCHONDRIA", "icon": "🔥"},
            "outputs": [
                {"label": "ATP (energy)", "icon": "⚡", "color": "#10B981"},
                {"label": "CO₂ + H₂O", "icon": "💨", "color": "#6B7280"}
            ],
            "formula": "C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + ATP",
            "memory_hook": "Mitochondria = Cell's Power Plant! ⚡"
        },
        "indian_context": "Like burning LPG gas for cooking energy"
    },
    
    "aerobic_vs_anaerobic": {
        "template": RACE,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Aerobic vs Anaerobic Respiration",
        "title_hindi": "वायवीय बनाम अवायवीय श्वसन",
        "keywords": ["aerobic", "anaerobic", "oxygen", "fermentation"],
        "config": {
            "object_a": {"type": "process", "label": "AEROBIC", "color": "#10B981", "requires": "O₂", "atp": 38},
            "object_b": {"type": "process", "label": "ANAEROBIC", "color": "#EF4444", "requires": "No O₂", "atp": 2},
            "formula": "Aerobic = 38 ATP | Anaerobic = 2 ATP",
            "memory_hook": "With oxygen = More energy (38 ATP)! 💪"
        },
        "indian_context": "Marathon runner (aerobic) vs sprinter muscles cramping (anaerobic)"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # LIFE PROCESSES - TRANSPORT
    # ═══════════════════════════════════════════════════════════════
    
    "circulatory_system": {
        "template": CYCLE,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Blood Circulation - Double Circulation",
        "title_hindi": "रक्त परिसंचरण",
        "keywords": ["circulation", "heart", "blood", "artery", "vein"],
        "config": {
            "stages": [
                {"label": "Heart (pump)", "icon": "❤️", "color": "#EF4444"},
                {"label": "Lungs (O₂)", "icon": "🫁", "color": "#3B82F6"},
                {"label": "Body (deliver)", "icon": "🏃", "color": "#10B981"},
                {"label": "Back to heart", "icon": "↩️", "color": "#8B5CF6"}
            ],
            "formula": "Heart → Lungs → Heart → Body → Heart",
            "memory_hook": "Double circulation = Two loops (lungs + body)! 🔄🔄"
        },
        "indian_context": "Blood = Delivery boy, Heart = Distribution center"
    },
    
    "heart_structure": {
        "template": STRUCTURE,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Human Heart - 4 Chambers",
        "title_hindi": "मानव हृदय",
        "keywords": ["heart", "atrium", "ventricle", "valve"],
        "config": {
            "parts": [
                {"label": "Right Atrium", "x": 180, "y": 150},
                {"label": "Left Atrium", "x": 320, "y": 150},
                {"label": "Right Ventricle", "x": 180, "y": 220},
                {"label": "Left Ventricle", "x": 320, "y": 220},
                {"label": "Septum", "x": 250, "y": 185}
            ],
            "formula": "4 chambers: 2 Atria (receiving) + 2 Ventricles (pumping)",
            "memory_hook": "A = Arrival (atria), V = Dispatch (ventricle)! 📬"
        },
        "indian_context": "Heart = Post office with 4 rooms"
    },
    
    "blood_components": {
        "template": SCALE,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Blood Components",
        "title_hindi": "रक्त के घटक",
        "keywords": ["blood", "rbc", "wbc", "platelet", "plasma"],
        "config": {
            "scale_start": 0,
            "scale_end": 100,
            "unit": "%",
            "items": [
                {"value": 55, "label": "Plasma", "icon": "💛", "color": "#FCD34D"},
                {"value": 40, "label": "RBC", "icon": "🔴", "color": "#EF4444"},
                {"value": 4, "label": "WBC", "icon": "⚪", "color": "#F3F4F6"},
                {"value": 1, "label": "Platelets", "icon": "🩹", "color": "#3B82F6"}
            ],
            "gradient_colors": ["#FCD34D", "#EF4444", "#F3F4F6", "#3B82F6"],
            "formula": "Blood = Plasma (55%) + RBC + WBC + Platelets",
            "memory_hook": "RBC = Red taxi carrying O₂! 🚕"
        },
        "indian_context": "Blood = Army with soldiers (WBC), trucks (RBC), and medics (platelets)"
    },
    
    "transpiration": {
        "template": PROCESS,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Transpiration - Water Loss in Plants",
        "title_hindi": "वाष्पोत्सर्जन",
        "keywords": ["transpiration", "stomata", "water", "evaporation"],
        "config": {
            "inputs": [
                {"label": "Water (from roots)", "icon": "💧", "color": "#3B82F6"}
            ],
            "process_box": {"label": "STOMATA", "icon": "🌿"},
            "outputs": [
                {"label": "Water vapor (to air)", "icon": "💨", "color": "#93C5FD"}
            ],
            "formula": "Water from roots → Stem → Leaves → Air",
            "memory_hook": "Plants sweat through leaves! 💦"
        },
        "indian_context": "Like sweating on hot day - plants cool themselves"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # LIFE PROCESSES - EXCRETION
    # ═══════════════════════════════════════════════════════════════
    
    "excretion": {
        "template": PROCESS,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Human Excretory System",
        "title_hindi": "मानव उत्सर्जन तंत्र",
        "keywords": ["excretion", "kidney", "urine", "nephron"],
        "config": {
            "inputs": [
                {"label": "Blood with waste", "icon": "🩸", "color": "#EF4444"}
            ],
            "process_box": {"label": "KIDNEYS", "icon": "🫘"},
            "outputs": [
                {"label": "Clean blood", "icon": "💉", "color": "#10B981"},
                {"label": "Urine (waste)", "icon": "💧", "color": "#FBBF24"}
            ],
            "formula": "Blood → Kidney → Urine + Clean blood",
            "memory_hook": "Kidneys = Blood filters! 🧹"
        },
        "indian_context": "Kidneys = Water purifier for blood"
    },
    
    "nephron": {
        "template": STRUCTURE,
        "subject": "biology",
        "chapter": "Life Processes",
        "class_level": [10, 11],
        "title": "Nephron - Kidney's Filtering Unit",
        "title_hindi": "नेफ्रॉन",
        "keywords": ["nephron", "bowman", "glomerulus", "tubule"],
        "config": {
            "parts": [
                {"label": "Bowman's capsule", "x": 150, "y": 150},
                {"label": "Glomerulus", "x": 170, "y": 170},
                {"label": "Proximal tubule", "x": 250, "y": 200},
                {"label": "Loop of Henle", "x": 300, "y": 250},
                {"label": "Collecting duct", "x": 350, "y": 200}
            ],
            "formula": "Filtration → Reabsorption → Secretion → Urine",
            "memory_hook": "1 million nephrons per kidney filtering blood! 🏭"
        },
        "indian_context": "Each nephron = Tiny water treatment plant"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # CONTROL AND COORDINATION
    # ═══════════════════════════════════════════════════════════════
    
    "nervous_system": {
        "template": PROCESS,
        "subject": "biology",
        "chapter": "Control and Coordination",
        "class_level": [10, 11],
        "title": "Nervous System - Electrical Signals",
        "title_hindi": "तंत्रिका तंत्र",
        "keywords": ["nervous", "neuron", "brain", "reflex"],
        "config": {
            "inputs": [
                {"label": "Stimulus", "icon": "👆", "color": "#FBBF24"}
            ],
            "process_box": {"label": "BRAIN/SPINAL", "icon": "🧠"},
            "outputs": [
                {"label": "Response", "icon": "🏃", "color": "#10B981"}
            ],
            "formula": "Stimulus → Receptor → Nerve → Brain → Nerve → Effector → Response",
            "memory_hook": "Nervous system = Body's internet (fast signals)! ⚡"
        },
        "indian_context": "Like WhatsApp - instant messaging in body"
    },
    
    "reflex_arc": {
        "template": SEQUENCE,
        "subject": "biology",
        "chapter": "Control and Coordination",
        "class_level": [10, 11],
        "title": "Reflex Arc - Automatic Response",
        "title_hindi": "प्रतिवर्त चाप",
        "keywords": ["reflex", "arc", "automatic", "knee jerk"],
        "config": {
            "stages": [
                {"label": "Receptor (sense)", "icon": "👁️"},
                {"label": "Sensory neuron", "icon": "➡️"},
                {"label": "Spinal cord", "icon": "🧠"},
                {"label": "Motor neuron", "icon": "➡️"},
                {"label": "Effector (act)", "icon": "💪"}
            ],
            "formula": "Stimulus → Receptor → CNS → Effector → Response",
            "memory_hook": "Hot pan → Hand pulls back (no thinking needed)! 🔥"
        },
        "indian_context": "Touching hot tawa - instant hand withdrawal"
    },
    
    "hormones": {
        "template": CAUSE_EFFECT,
        "subject": "biology",
        "chapter": "Control and Coordination",
        "class_level": [10, 11],
        "title": "Hormones - Chemical Messengers",
        "title_hindi": "हार्मोन",
        "keywords": ["hormone", "endocrine", "gland", "chemical messenger"],
        "config": {
            "cause": {"label": "GLAND", "icon": "🏭"},
            "effect": {"label": "TARGET ORGAN", "icon": "🎯"},
            "action_label": "HORMONE (via blood)",
            "formula": "Gland → Hormone → Blood → Target organ",
            "memory_hook": "Hormones = WhatsApp messages through blood! 📱"
        },
        "indian_context": "Like postal letters - slow but effective"
    },
    
    "plant_hormones": {
        "template": SCALE,
        "subject": "biology",
        "chapter": "Control and Coordination",
        "class_level": [10],
        "title": "Plant Hormones",
        "title_hindi": "पादप हार्मोन",
        "keywords": ["auxin", "gibberellin", "cytokinin", "abscisic"],
        "config": {
            "scale_start": 0,
            "scale_end": 4,
            "unit": "",
            "items": [
                {"value": 0, "label": "Auxin (growth)", "icon": "🌱", "color": "#10B981"},
                {"value": 1, "label": "Gibberellin (height)", "icon": "📏", "color": "#3B82F6"},
                {"value": 2, "label": "Cytokinin (division)", "icon": "🔄", "color": "#8B5CF6"},
                {"value": 3, "label": "Abscisic (stress)", "icon": "🛑", "color": "#EF4444"}
            ],
            "gradient_colors": ["#10B981", "#3B82F6", "#8B5CF6", "#EF4444"],
            "formula": "Auxin = Tip growth | Gibberellin = Stem height",
            "memory_hook": "Auxin makes plants bend towards light! ☀️"
        },
        "indian_context": "Money plant growing towards window light"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # REPRODUCTION
    # ═══════════════════════════════════════════════════════════════
    
    "asexual_reproduction": {
        "template": SEQUENCE,
        "subject": "biology",
        "chapter": "Reproduction",
        "class_level": [10],
        "title": "Asexual Reproduction - One Parent",
        "title_hindi": "अलैंगिक प्रजनन",
        "keywords": ["asexual", "binary fission", "budding", "fragmentation"],
        "config": {
            "stages": [
                {"label": "Binary fission", "example": "Amoeba", "icon": "🔵"},
                {"label": "Budding", "example": "Hydra", "icon": "🌿"},
                {"label": "Spore formation", "example": "Fungi", "icon": "🍄"},
                {"label": "Vegetative", "example": "Potato", "icon": "🥔"}
            ],
            "formula": "1 parent → Identical offspring",
            "memory_hook": "Asexual = Making clones (Xerox)! 📋"
        },
        "indian_context": "Potato eyes growing new plants"
    },
    
    "sexual_reproduction": {
        "template": PROCESS,
        "subject": "biology",
        "chapter": "Reproduction",
        "class_level": [10, 12],
        "title": "Sexual Reproduction - Two Parents",
        "title_hindi": "लैंगिक प्रजनन",
        "keywords": ["sexual", "gamete", "fertilization", "zygote"],
        "config": {
            "inputs": [
                {"label": "Sperm (male)", "icon": "🔵", "color": "#3B82F6"},
                {"label": "Egg (female)", "icon": "🔴", "color": "#EF4444"}
            ],
            "process_box": {"label": "FERTILIZATION", "icon": "💫"},
            "outputs": [
                {"label": "Zygote (new life)", "icon": "👶", "color": "#8B5CF6"}
            ],
            "formula": "Sperm (n) + Egg (n) → Zygote (2n)",
            "memory_hook": "Half from mom + Half from dad = Unique YOU! 🎲"
        },
        "indian_context": "Taking traits from both parents - like your nose from dad!"
    },
    
    "flower_parts": {
        "template": STRUCTURE,
        "subject": "biology",
        "chapter": "Reproduction",
        "class_level": [10, 12],
        "title": "Flower - Reproductive Organ of Plants",
        "title_hindi": "पुष्प संरचना",
        "keywords": ["flower", "stamen", "pistil", "pollen", "ovule"],
        "config": {
            "parts": [
                {"label": "Petal (attracts)", "x": 250, "y": 120},
                {"label": "Stamen (male)", "x": 180, "y": 180},
                {"label": "Pistil (female)", "x": 320, "y": 180},
                {"label": "Ovary (eggs)", "x": 280, "y": 240},
                {"label": "Sepal (protection)", "x": 250, "y": 280}
            ],
            "formula": "Flower = Sepals + Petals + Stamens + Pistil",
            "memory_hook": "Stamen = Male (S like Sperm), Pistil = Female! 🌸"
        },
        "indian_context": "Marigold flower structure"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # GENETICS & EVOLUTION
    # ═══════════════════════════════════════════════════════════════
    
    "dna": {
        "template": STRUCTURE,
        "subject": "biology",
        "chapter": "Heredity and Evolution",
        "class_level": [10, 12],
        "title": "DNA - Blueprint of Life",
        "title_hindi": "डीएनए - जीवन का नक्शा",
        "keywords": ["dna", "gene", "chromosome", "double helix"],
        "config": {
            "parts": [
                {"label": "Double helix", "x": 250, "y": 140},
                {"label": "Base pairs (A-T, G-C)", "x": 180, "y": 200},
                {"label": "Sugar-phosphate backbone", "x": 320, "y": 200},
                {"label": "Gene (instruction)", "x": 250, "y": 260}
            ],
            "formula": "DNA → RNA → Protein",
            "memory_hook": "DNA = Life's recipe book with 4 letters (A, T, G, C)! 📖"
        },
        "indian_context": "Like grandmother's secret recipe passed down"
    },
    
    "mendel_laws": {
        "template": PROCESS,
        "subject": "biology",
        "chapter": "Heredity and Evolution",
        "class_level": [10, 12],
        "title": "Mendel's Laws of Inheritance",
        "title_hindi": "मेंडल के आनुवंशिकता नियम",
        "keywords": ["mendel", "dominant", "recessive", "inheritance", "pea"],
        "config": {
            "inputs": [
                {"label": "Tall (TT)", "icon": "🌱", "color": "#10B981"},
                {"label": "Short (tt)", "icon": "🌿", "color": "#FBBF24"}
            ],
            "process_box": {"label": "CROSS", "icon": "✖️"},
            "outputs": [
                {"label": "F1: All Tall (Tt)", "icon": "🌱🌱", "color": "#10B981"}
            ],
            "formula": "Dominant masks Recessive (T > t)",
            "memory_hook": "Capital letter (T) = Dominant = Boss! 👔"
        },
        "indian_context": "Why you look like your parents - Mendel's pea experiments"
    },
    
    "evolution": {
        "template": SEQUENCE,
        "subject": "biology",
        "chapter": "Heredity and Evolution",
        "class_level": [10, 12],
        "title": "Evolution - Change Over Time",
        "title_hindi": "जैव विकास",
        "keywords": ["evolution", "darwin", "natural selection", "adaptation"],
        "config": {
            "stages": [
                {"label": "Variation exists", "icon": "🎲"},
                {"label": "Natural selection", "icon": "⚔️"},
                {"label": "Survival of fittest", "icon": "💪"},
                {"label": "Inheritance", "icon": "👶"},
                {"label": "Species change", "icon": "🦕→🐦"}
            ],
            "formula": "Variation + Selection + Time = New Species",
            "memory_hook": "Darwin: Best fit survives, others die out! 🏆"
        },
        "indian_context": "Peppered moth - dark ones survived in polluted cities"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # ECOLOGY & ENVIRONMENT
    # ═══════════════════════════════════════════════════════════════
    
    "ecosystem": {
        "template": CYCLE,
        "subject": "biology",
        "chapter": "Our Environment",
        "class_level": [10],
        "title": "Ecosystem - Living + Non-living",
        "title_hindi": "पारितंत्र",
        "keywords": ["ecosystem", "biotic", "abiotic", "environment"],
        "config": {
            "stages": [
                {"label": "Producers (plants)", "icon": "🌿", "color": "#10B981"},
                {"label": "Consumers (animals)", "icon": "🐄", "color": "#FBBF24"},
                {"label": "Decomposers", "icon": "🍄", "color": "#8B5CF6"},
                {"label": "Back to soil", "icon": "🌍", "color": "#6B7280"}
            ],
            "formula": "Sun → Producers → Consumers → Decomposers → Nutrients",
            "memory_hook": "Circle of life - nothing wasted! 🔄"
        },
        "indian_context": "Forest ecosystem with all living things connected"
    },
    
    "food_chain": {
        "template": SEQUENCE,
        "subject": "biology",
        "chapter": "Our Environment",
        "class_level": [10],
        "title": "Food Chain - Who Eats Whom",
        "title_hindi": "खाद्य श्रृंखला",
        "keywords": ["food chain", "producer", "consumer", "trophic"],
        "config": {
            "stages": [
                {"label": "Grass (Producer)", "icon": "🌿"},
                {"label": "Grasshopper", "icon": "🦗"},
                {"label": "Frog", "icon": "🐸"},
                {"label": "Snake", "icon": "🐍"},
                {"label": "Eagle", "icon": "🦅"}
            ],
            "formula": "10% energy transfers to next level",
            "memory_hook": "10% rule - Energy reduces at each step! 📉"
        },
        "indian_context": "Grass → Deer → Tiger chain in Indian forest"
    },
    
    "water_cycle": {
        "template": CYCLE,
        "subject": "biology",
        "chapter": "Our Environment",
        "class_level": [10],
        "title": "Water Cycle",
        "title_hindi": "जल चक्र",
        "keywords": ["water cycle", "evaporation", "condensation", "precipitation"],
        "config": {
            "stages": [
                {"label": "Evaporation", "icon": "☀️", "color": "#FBBF24"},
                {"label": "Condensation", "icon": "☁️", "color": "#9CA3AF"},
                {"label": "Precipitation", "icon": "🌧️", "color": "#3B82F6"},
                {"label": "Collection", "icon": "🌊", "color": "#0EA5E9"}
            ],
            "formula": "Water: Ocean → Cloud → Rain → River → Ocean",
            "memory_hook": "Water travels in circles, never stops! 🔄"
        },
        "indian_context": "Monsoon cycle in India"
    },
    
    "carbon_cycle": {
        "template": CYCLE,
        "subject": "biology",
        "chapter": "Our Environment",
        "class_level": [10],
        "title": "Carbon Cycle",
        "title_hindi": "कार्बन चक्र",
        "keywords": ["carbon cycle", "co2", "photosynthesis", "respiration"],
        "config": {
            "stages": [
                {"label": "CO₂ in air", "icon": "💨", "color": "#6B7280"},
                {"label": "Photosynthesis (plants absorb)", "icon": "🌿", "color": "#10B981"},
                {"label": "Food chain", "icon": "🔗", "color": "#FBBF24"},
                {"label": "Respiration/Decay (release)", "icon": "🔥", "color": "#EF4444"}
            ],
            "formula": "CO₂ → Plants → Animals → CO₂ (back to air)",
            "memory_hook": "Carbon = Nature's recycling program! ♻️"
        },
        "indian_context": "Breathing out CO₂, plants using it - perfect balance"
    },
    
    "ozone_depletion": {
        "template": CAUSE_EFFECT,
        "subject": "biology",
        "chapter": "Our Environment",
        "class_level": [10],
        "title": "Ozone Layer Depletion",
        "title_hindi": "ओजोन परत का क्षय",
        "keywords": ["ozone", "cfc", "uv", "depletion"],
        "config": {
            "cause": {"label": "CFCs", "icon": "🧴"},
            "effect": {"label": "Ozone hole", "icon": "🕳️"},
            "action_label": "DESTROY O₃",
            "formula": "CFCs + O₃ → O₂ (ozone destroyed)",
            "memory_hook": "CFCs eat ozone - bad for Earth's sunscreen! ☀️🛡️"
        },
        "indian_context": "AC and refrigerator gases harming ozone layer"
    },
}


# Export
__all__ = ['BIOLOGY_CONCEPTS']

