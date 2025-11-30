"""
📐 MATHEMATICS Visual Concepts - Complete Coverage
==================================================

Class 9-12, JEE level Mathematics concepts with visual templates.

Categories:
1. Number Systems
2. Algebra
3. Geometry
4. Trigonometry
5. Coordinate Geometry
6. Statistics & Probability
7. Calculus (Basic)

Total: 35+ concepts
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


MATHEMATICS_CONCEPTS: Dict[str, Dict[str, Any]] = {
    
    # ═══════════════════════════════════════════════════════════════
    # NUMBER SYSTEMS
    # ═══════════════════════════════════════════════════════════════
    
    "number_line": {
        "template": SCALE,
        "subject": "mathematics",
        "chapter": "Number Systems",
        "class_level": [9],
        "title": "Number Line - Visualizing Numbers",
        "title_hindi": "संख्या रेखा",
        "keywords": ["number line", "integer", "positive", "negative"],
        "config": {
            "scale_start": -10,
            "scale_end": 10,
            "unit": "",
            "items": [
                {"value": -5, "label": "Negative", "icon": "➖", "color": "#EF4444"},
                {"value": 0, "label": "Zero", "icon": "⭕", "color": "#6B7280"},
                {"value": 5, "label": "Positive", "icon": "➕", "color": "#10B981"}
            ],
            "gradient_colors": ["#EF4444", "#6B7280", "#10B981"],
            "formula": "Left = Negative | Right = Positive",
            "memory_hook": "Number line = Temperature scale! 🌡️"
        },
        "indian_context": "Like floors in building - basement (-1), ground (0), first (1)"
    },
    
    "real_numbers": {
        "template": STRUCTURE,
        "subject": "mathematics",
        "chapter": "Number Systems",
        "class_level": [9, 10],
        "title": "Real Numbers Classification",
        "title_hindi": "वास्तविक संख्याएं",
        "keywords": ["real numbers", "rational", "irrational", "integer"],
        "config": {
            "parts": [
                {"label": "Real Numbers (ℝ)", "x": 250, "y": 100},
                {"label": "Rational (p/q)", "x": 150, "y": 180},
                {"label": "Irrational (√2, π)", "x": 350, "y": 180},
                {"label": "Integers (...-1,0,1...)", "x": 150, "y": 250},
                {"label": "Natural (1,2,3...)", "x": 150, "y": 300}
            ],
            "formula": "Real = Rational + Irrational",
            "memory_hook": "Real numbers = Everything on number line! 📏"
        },
        "indian_context": "Like family tree of numbers"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # ALGEBRA
    # ═══════════════════════════════════════════════════════════════
    
    "linear_equation": {
        "template": GRAPH,
        "subject": "mathematics",
        "chapter": "Linear Equations",
        "class_level": [9, 10],
        "title": "Linear Equation = Straight Line",
        "title_hindi": "रैखिक समीकरण",
        "keywords": ["linear", "equation", "straight line", "y=mx+c"],
        "config": {
            "equation": "y = mx + c",
            "shape": "line",
            "x_axis": "x",
            "y_axis": "y",
            "key_points": [
                {"label": "y-intercept (c)", "description": "Where line crosses y-axis"},
                {"label": "slope (m)", "description": "Steepness of line"}
            ],
            "formula": "y = mx + c",
            "memory_hook": "m = Mountain slope, c = Cut point on y-axis! 🏔️"
        },
        "indian_context": "Railway track = Straight line"
    },
    
    "quadratic_equation": {
        "template": GRAPH,
        "subject": "mathematics",
        "chapter": "Quadratic Equations",
        "class_level": [10, 11],
        "title": "Quadratic = Parabola (U-shape)",
        "title_hindi": "द्विघात समीकरण",
        "keywords": ["quadratic", "parabola", "ax2", "roots", "discriminant"],
        "config": {
            "equation": "ax² + bx + c = 0",
            "shape": "parabola",
            "x_axis": "x",
            "y_axis": "y",
            "key_points": [
                {"label": "Vertex (turning point)", "x": 250, "y": 100},
                {"label": "Root 1", "x": 150, "y": 250},
                {"label": "Root 2", "x": 350, "y": 250}
            ],
            "formula": "x = (-b ± √(b²-4ac)) / 2a",
            "memory_hook": "Diwali rocket path = Parabola! 🎆"
        },
        "indian_context": "Fountain water arc, rocket trajectory"
    },
    
    "polynomials": {
        "template": SCALE,
        "subject": "mathematics",
        "chapter": "Polynomials",
        "class_level": [9, 10],
        "title": "Types of Polynomials",
        "title_hindi": "बहुपद के प्रकार",
        "keywords": ["polynomial", "degree", "monomial", "binomial", "trinomial"],
        "config": {
            "scale_start": 0,
            "scale_end": 3,
            "unit": "terms",
            "items": [
                {"value": 1, "label": "Monomial (1 term)", "icon": "1️⃣", "color": "#10B981", "example": "5x²"},
                {"value": 2, "label": "Binomial (2 terms)", "icon": "2️⃣", "color": "#3B82F6", "example": "x + 5"},
                {"value": 3, "label": "Trinomial (3 terms)", "icon": "3️⃣", "color": "#8B5CF6", "example": "x² + x + 1"}
            ],
            "gradient_colors": ["#10B981", "#3B82F6", "#8B5CF6"],
            "formula": "Mono = 1, Bi = 2, Tri = 3 terms",
            "memory_hook": "Mono/Bi/Tri = 1/2/3 (like bicycle, tricycle)! 🚲"
        },
        "indian_context": "Mono = Unicycle, Bi = Bicycle, Tri = Tricycle"
    },
    
    "factorization": {
        "template": PROCESS,
        "subject": "mathematics",
        "chapter": "Polynomials",
        "class_level": [9, 10],
        "title": "Factorization - Breaking Into Factors",
        "title_hindi": "गुणनखंड",
        "keywords": ["factorization", "factor", "common", "splitting"],
        "config": {
            "inputs": [
                {"label": "x² + 5x + 6", "icon": "📝", "color": "#3B82F6"}
            ],
            "process_box": {"label": "FACTORIZE", "icon": "✂️"},
            "outputs": [
                {"label": "(x + 2)(x + 3)", "icon": "✅", "color": "#10B981"}
            ],
            "formula": "Find numbers that multiply to c and add to b",
            "memory_hook": "Factorize = Find the building blocks! 🧱"
        },
        "indian_context": "Breaking 12 into 3 × 4 or 2 × 6"
    },
    
    "algebraic_identities": {
        "template": SEQUENCE,
        "subject": "mathematics",
        "chapter": "Polynomials",
        "class_level": [9, 10],
        "title": "Algebraic Identities",
        "title_hindi": "बीजगणितीय सर्वसमिकाएं",
        "keywords": ["identity", "a+b squared", "a-b squared", "formula"],
        "config": {
            "stages": [
                {"label": "(a+b)² = a² + 2ab + b²", "formula": "Square of sum"},
                {"label": "(a-b)² = a² - 2ab + b²", "formula": "Square of difference"},
                {"label": "(a+b)(a-b) = a² - b²", "formula": "Difference of squares"},
                {"label": "(a+b+c)² = a² + b² + c² + 2ab + 2bc + 2ca", "formula": "Three terms"}
            ],
            "formula": "(a±b)² = a² ± 2ab + b²",
            "memory_hook": "First², Last², 2×First×Last in middle! 🎯"
        },
        "indian_context": "Shortcut to calculate 99² = (100-1)² = 9801"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # GEOMETRY
    # ═══════════════════════════════════════════════════════════════
    
    "pythagoras_theorem": {
        "template": STRUCTURE,
        "subject": "mathematics",
        "chapter": "Triangles",
        "class_level": [9, 10],
        "title": "Pythagoras Theorem",
        "title_hindi": "पाइथागोरस प्रमेय",
        "keywords": ["pythagoras", "right triangle", "hypotenuse", "a2+b2=c2"],
        "config": {
            "parts": [
                {"label": "Base (a)", "x": 150, "y": 280, "labelX": 200, "labelY": 300},
                {"label": "Height (b)", "x": 350, "y": 180, "labelX": 370, "labelY": 230},
                {"label": "Hypotenuse (c)", "x": 250, "y": 180, "labelX": 200, "labelY": 200}
            ],
            "formula": "a² + b² = c²",
            "memory_hook": "Square dance: a² + b² = c²! 💃"
        },
        "indian_context": "Checking if corner is 90° using 3-4-5 triangle"
    },
    
    "triangle_properties": {
        "template": SEQUENCE,
        "subject": "mathematics",
        "chapter": "Triangles",
        "class_level": [9, 10],
        "title": "Types of Triangles",
        "title_hindi": "त्रिभुज के प्रकार",
        "keywords": ["triangle", "equilateral", "isosceles", "scalene", "acute", "obtuse"],
        "config": {
            "stages": [
                {"label": "Equilateral", "icon": "🔺", "property": "All sides equal"},
                {"label": "Isosceles", "icon": "📐", "property": "Two sides equal"},
                {"label": "Scalene", "icon": "📏", "property": "No sides equal"},
                {"label": "Right angle", "icon": "⊾", "property": "One 90° angle"}
            ],
            "formula": "Sum of angles = 180°",
            "memory_hook": "Equi = Equal (3 sides), Iso = 2 sides, Scale = All different! 📐"
        },
        "indian_context": "Rangoli patterns use triangles"
    },
    
    "circle_properties": {
        "template": STRUCTURE,
        "subject": "mathematics",
        "chapter": "Circles",
        "class_level": [9, 10],
        "title": "Circle - Parts and Properties",
        "title_hindi": "वृत्त",
        "keywords": ["circle", "radius", "diameter", "circumference", "chord"],
        "config": {
            "parts": [
                {"label": "Center (O)", "x": 250, "y": 180},
                {"label": "Radius (r)", "x": 300, "y": 180},
                {"label": "Diameter (d = 2r)", "x": 250, "y": 180},
                {"label": "Circumference (2πr)", "x": 250, "y": 100},
                {"label": "Chord", "x": 200, "y": 220}
            ],
            "formula": "Circumference = 2πr | Area = πr²",
            "memory_hook": "Diameter = 2 × Radius (twice the radius)! ⭕"
        },
        "indian_context": "Bangle = Circle, measuring its size"
    },
    
    "area_formulas": {
        "template": SCALE,
        "subject": "mathematics",
        "chapter": "Areas",
        "class_level": [9, 10],
        "title": "Area Formulas",
        "title_hindi": "क्षेत्रफल सूत्र",
        "keywords": ["area", "square", "rectangle", "triangle", "circle"],
        "config": {
            "scale_start": 0,
            "scale_end": 4,
            "unit": "",
            "items": [
                {"value": 0, "label": "Square = s²", "icon": "⬛", "color": "#EF4444"},
                {"value": 1, "label": "Rectangle = l×b", "icon": "📏", "color": "#F97316"},
                {"value": 2, "label": "Triangle = ½×b×h", "icon": "🔺", "color": "#FBBF24"},
                {"value": 3, "label": "Circle = πr²", "icon": "⭕", "color": "#10B981"}
            ],
            "gradient_colors": ["#EF4444", "#F97316", "#FBBF24", "#10B981"],
            "formula": "Square = s² | Rectangle = l×b | Triangle = ½bh | Circle = πr²",
            "memory_hook": "Triangle = Half of rectangle (cut diagonally)! ✂️"
        },
        "indian_context": "Measuring land area for farming"
    },
    
    "surface_area_volume": {
        "template": RACE,
        "subject": "mathematics",
        "chapter": "Surface Areas and Volumes",
        "class_level": [9, 10],
        "title": "Surface Area vs Volume",
        "title_hindi": "पृष्ठीय क्षेत्रफल बनाम आयतन",
        "keywords": ["surface area", "volume", "3d", "cube", "cylinder"],
        "config": {
            "object_a": {"type": "measurement", "label": "SURFACE AREA", "color": "#3B82F6", "unit": "sq units"},
            "object_b": {"type": "measurement", "label": "VOLUME", "color": "#10B981", "unit": "cubic units"},
            "formula": "Surface = Paint needed | Volume = Space inside",
            "memory_hook": "Surface = Gift wrap, Volume = Space for gift! 🎁"
        },
        "indian_context": "Surface area = Paint for room walls, Volume = Room AC capacity"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # TRIGONOMETRY
    # ═══════════════════════════════════════════════════════════════
    
    "trigonometric_ratios": {
        "template": STRUCTURE,
        "subject": "mathematics",
        "chapter": "Trigonometry",
        "class_level": [10, 11],
        "title": "Trigonometric Ratios",
        "title_hindi": "त्रिकोणमितीय अनुपात",
        "keywords": ["sin", "cos", "tan", "trigonometry", "ratio"],
        "config": {
            "parts": [
                {"label": "Opposite (O)", "x": 350, "y": 200},
                {"label": "Adjacent (A)", "x": 200, "y": 280},
                {"label": "Hypotenuse (H)", "x": 250, "y": 180},
                {"label": "Angle θ", "x": 150, "y": 250}
            ],
            "formula": "sin = O/H | cos = A/H | tan = O/A",
            "memory_hook": "SOH-CAH-TOA: Some Old Horses Can Always Hear Their Owners Approach! 🐴"
        },
        "indian_context": "Finding height of temple using shadow and angle"
    },
    
    "trig_values": {
        "template": SCALE,
        "subject": "mathematics",
        "chapter": "Trigonometry",
        "class_level": [10, 11],
        "title": "Standard Trigonometric Values",
        "title_hindi": "मानक त्रिकोणमितीय मान",
        "keywords": ["sin 30", "cos 45", "tan 60", "standard values"],
        "config": {
            "scale_start": 0,
            "scale_end": 90,
            "unit": "°",
            "items": [
                {"value": 0, "label": "0°: sin=0", "icon": "0️⃣", "color": "#6B7280"},
                {"value": 30, "label": "30°: sin=½", "icon": "🔹", "color": "#3B82F6"},
                {"value": 45, "label": "45°: sin=1/√2", "icon": "🔸", "color": "#FBBF24"},
                {"value": 60, "label": "60°: sin=√3/2", "icon": "🔶", "color": "#F97316"},
                {"value": 90, "label": "90°: sin=1", "icon": "🔴", "color": "#EF4444"}
            ],
            "gradient_colors": ["#6B7280", "#3B82F6", "#FBBF24", "#F97316", "#EF4444"],
            "formula": "sin: 0, ½, 1/√2, √3/2, 1 | cos: reverse",
            "memory_hook": "sin 0,30,45,60,90 = √(0,1,2,3,4)/2 🎯"
        },
        "indian_context": "Values to memorize for exams"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # COORDINATE GEOMETRY
    # ═══════════════════════════════════════════════════════════════
    
    "coordinate_system": {
        "template": STRUCTURE,
        "subject": "mathematics",
        "chapter": "Coordinate Geometry",
        "class_level": [9, 10],
        "title": "Cartesian Coordinate System",
        "title_hindi": "कार्तीय निर्देशांक पद्धति",
        "keywords": ["coordinate", "x-axis", "y-axis", "quadrant", "origin"],
        "config": {
            "parts": [
                {"label": "Origin (0,0)", "x": 250, "y": 200},
                {"label": "x-axis (horizontal)", "x": 400, "y": 200},
                {"label": "y-axis (vertical)", "x": 250, "y": 80},
                {"label": "Quadrant I (+,+)", "x": 350, "y": 120},
                {"label": "Quadrant II (-,+)", "x": 150, "y": 120}
            ],
            "formula": "Point = (x, y) where x = horizontal, y = vertical",
            "memory_hook": "X comes before Y (alphabetically) → (x, y)! 📍"
        },
        "indian_context": "Like finding location on map using coordinates"
    },
    
    "distance_formula": {
        "template": CAUSE_EFFECT,
        "subject": "mathematics",
        "chapter": "Coordinate Geometry",
        "class_level": [10],
        "title": "Distance Formula",
        "title_hindi": "दूरी सूत्र",
        "keywords": ["distance", "formula", "two points", "coordinate"],
        "config": {
            "cause": {"label": "Point A(x₁,y₁)", "icon": "📍"},
            "effect": {"label": "Point B(x₂,y₂)", "icon": "📍"},
            "action_label": "DISTANCE",
            "formula": "d = √[(x₂-x₁)² + (y₂-y₁)²]",
            "memory_hook": "Pythagoras in disguise! a² + b² = c² 📐"
        },
        "indian_context": "Finding distance between two cities on map"
    },
    
    "section_formula": {
        "template": PROCESS,
        "subject": "mathematics",
        "chapter": "Coordinate Geometry",
        "class_level": [10],
        "title": "Section Formula",
        "title_hindi": "विभाजन सूत्र",
        "keywords": ["section", "divide", "ratio", "midpoint"],
        "config": {
            "inputs": [
                {"label": "Point A(x₁,y₁)", "icon": "📍", "color": "#3B82F6"},
                {"label": "Point B(x₂,y₂)", "icon": "📍", "color": "#EF4444"}
            ],
            "process_box": {"label": "DIVIDE m:n", "icon": "✂️"},
            "outputs": [
                {"label": "Point P dividing AB", "icon": "📍", "color": "#10B981"}
            ],
            "formula": "P = ((mx₂+nx₁)/(m+n), (my₂+ny₁)/(m+n))",
            "memory_hook": "Cross multiply and add, divide by sum! ✖️"
        },
        "indian_context": "Finding point that divides road in given ratio"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # STATISTICS & PROBABILITY
    # ═══════════════════════════════════════════════════════════════
    
    "mean_median_mode": {
        "template": RACE,
        "subject": "mathematics",
        "chapter": "Statistics",
        "class_level": [9, 10],
        "title": "Mean, Median, Mode",
        "title_hindi": "माध्य, माध्यिका, बहुलक",
        "keywords": ["mean", "median", "mode", "average", "central tendency"],
        "config": {
            "object_a": {"type": "measure", "label": "MEAN", "color": "#3B82F6", "description": "Average"},
            "object_b": {"type": "measure", "label": "MEDIAN", "color": "#10B981", "description": "Middle value"},
            "object_c": {"type": "measure", "label": "MODE", "color": "#F97316", "description": "Most frequent"},
            "formula": "Mean = Sum/Count | Median = Middle | Mode = Most frequent",
            "memory_hook": "Mean = Average, Median = Middle man, Mode = Most popular! 🏆"
        },
        "indian_context": "Class average marks (mean), middle ranker (median), most common score (mode)"
    },
    
    "probability_basics": {
        "template": SCALE,
        "subject": "mathematics",
        "chapter": "Probability",
        "class_level": [9, 10],
        "title": "Probability - 0 to 1",
        "title_hindi": "प्रायिकता",
        "keywords": ["probability", "chance", "likelihood", "event"],
        "config": {
            "scale_start": 0,
            "scale_end": 1,
            "unit": "",
            "items": [
                {"value": 0, "label": "Impossible", "icon": "❌", "color": "#EF4444"},
                {"value": 0.5, "label": "Equal chance", "icon": "🎲", "color": "#FBBF24"},
                {"value": 1, "label": "Certain", "icon": "✅", "color": "#10B981"}
            ],
            "gradient_colors": ["#EF4444", "#FBBF24", "#10B981"],
            "formula": "P(E) = Favorable outcomes / Total outcomes",
            "memory_hook": "Probability = Chances out of total! 🎲"
        },
        "indian_context": "Coin toss = 50% head, 50% tail"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # CALCULUS (BASIC)
    # ═══════════════════════════════════════════════════════════════
    
    "limits": {
        "template": GRAPH,
        "subject": "mathematics",
        "chapter": "Limits",
        "class_level": [11, 12],
        "title": "Limits - Approaching a Value",
        "title_hindi": "सीमा",
        "keywords": ["limit", "approaching", "tends to", "continuous"],
        "config": {
            "equation": "lim(x→a) f(x) = L",
            "shape": "approaching",
            "x_axis": "x",
            "y_axis": "f(x)",
            "formula": "lim(x→a) f(x) = L",
            "memory_hook": "Limit = Where you're heading, not where you are! 🎯"
        },
        "indian_context": "Like approaching temple but stopping just before"
    },
    
    "differentiation": {
        "template": CAUSE_EFFECT,
        "subject": "mathematics",
        "chapter": "Differentiation",
        "class_level": [11, 12],
        "title": "Differentiation - Rate of Change",
        "title_hindi": "अवकलन",
        "keywords": ["differentiation", "derivative", "rate", "slope"],
        "config": {
            "cause": {"label": "Function f(x)", "icon": "📈"},
            "effect": {"label": "Derivative f'(x)", "icon": "📉"},
            "action_label": "d/dx",
            "formula": "f'(x) = lim(h→0) [f(x+h) - f(x)] / h",
            "memory_hook": "Derivative = Speedometer of function! 🚗"
        },
        "indian_context": "Car speedometer shows rate of change of distance"
    },
    
    "integration": {
        "template": CAUSE_EFFECT,
        "subject": "mathematics",
        "chapter": "Integration",
        "class_level": [11, 12],
        "title": "Integration - Area Under Curve",
        "title_hindi": "समाकलन",
        "keywords": ["integration", "integral", "area", "antiderivative"],
        "config": {
            "cause": {"label": "Function f(x)", "icon": "📈"},
            "effect": {"label": "Integral ∫f(x)dx", "icon": "📊"},
            "action_label": "∫ dx",
            "formula": "∫f(x)dx = F(x) + C",
            "memory_hook": "Integration = Reverse of differentiation! ↩️"
        },
        "indian_context": "Finding area of irregular land"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # ARITHMETIC PROGRESSIONS
    # ═══════════════════════════════════════════════════════════════
    
    "arithmetic_progression": {
        "template": SEQUENCE,
        "subject": "mathematics",
        "chapter": "Arithmetic Progressions",
        "class_level": [10],
        "title": "Arithmetic Progression (AP)",
        "title_hindi": "समांतर श्रेणी",
        "keywords": ["ap", "arithmetic", "progression", "common difference"],
        "config": {
            "stages": [
                {"label": "a (first term)", "value": 2},
                {"label": "a + d", "value": 5},
                {"label": "a + 2d", "value": 8},
                {"label": "a + 3d", "value": 11},
                {"label": "a + (n-1)d", "value": "..."}
            ],
            "formula": "aₙ = a + (n-1)d | Sₙ = n/2[2a + (n-1)d]",
            "memory_hook": "AP = Add same number each time! ➕"
        },
        "indian_context": "Salary increment: 10000, 12000, 14000, 16000... (d = 2000)"
    },
    
    "geometric_progression": {
        "template": SEQUENCE,
        "subject": "mathematics",
        "chapter": "Sequences",
        "class_level": [11],
        "title": "Geometric Progression (GP)",
        "title_hindi": "गुणोत्तर श्रेणी",
        "keywords": ["gp", "geometric", "progression", "common ratio"],
        "config": {
            "stages": [
                {"label": "a (first term)", "value": 2},
                {"label": "ar", "value": 6},
                {"label": "ar²", "value": 18},
                {"label": "ar³", "value": 54},
                {"label": "arⁿ⁻¹", "value": "..."}
            ],
            "formula": "aₙ = arⁿ⁻¹ | Sₙ = a(rⁿ-1)/(r-1)",
            "memory_hook": "GP = Multiply same number each time! ✖️"
        },
        "indian_context": "Bacteria doubling: 1, 2, 4, 8, 16... (r = 2)"
    },
}


# Export
__all__ = ['MATHEMATICS_CONCEPTS']

