"""
📚 NCERT Curriculum Loader - Comprehensive Knowledge Graph Population
======================================================================

Loads FULL curriculum content into the UniversalKnowledgeGraph:
- Physics: Class 11-12 NCERT + JEE topics
- Chemistry: Physical, Organic, Inorganic
- Biology: Class 11-12 NCERT + NEET topics
- Mathematics: Calculus, Algebra, Coordinate Geometry

Each concept includes:
- Definition and description
- Key points and formulas
- Prerequisites and applications
- Real-world examples
- Common misconceptions
- Exam relevance scores
"""

import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ============================================================================
# PHYSICS CURRICULUM - Class 11 & 12 NCERT + JEE
# ============================================================================

PHYSICS_CONCEPTS = [
    # === MECHANICS ===
    {
        "id": "ph_kinematics",
        "name": "Kinematics",
        "domain": "Physics",
        "subdomain": "Mechanics",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Study of motion without considering the forces causing it. Covers displacement, velocity, acceleration, and equations of motion.",
        "key_points": [
            "Displacement is vector, distance is scalar",
            "Velocity is rate of change of displacement",
            "Three equations of motion for uniform acceleration",
            "Projectile motion is combination of horizontal and vertical motion"
        ],
        "formulas": [
            "v = u + at",
            "s = ut + (1/2)at²",
            "v² = u² + 2as",
            "s = ((u+v)/2)t",
            "Range R = u²sin2θ/g"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 7, "CBSE": 10},
        "real_world": ["Car speedometers", "Sports analytics", "Space launches"],
        "misconceptions": ["Velocity and speed are same", "Acceleration always means speeding up"],
        "prerequisites": ["basic_algebra", "trigonometry"]
    },
    {
        "id": "ph_newtons_laws",
        "name": "Newton's Laws of Motion",
        "domain": "Physics",
        "subdomain": "Mechanics",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Three fundamental laws describing relationship between force and motion. Foundation of classical mechanics.",
        "key_points": [
            "First Law: Inertia - objects resist change in motion",
            "Second Law: F = ma - force causes acceleration",
            "Third Law: Action-reaction pairs are equal and opposite",
            "Free body diagrams essential for problem solving"
        ],
        "formulas": [
            "F = ma",
            "F_net = Σ F",
            "Weight W = mg",
            "Friction f = μN"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 8, "CBSE": 10},
        "real_world": ["Car brakes", "Rocket propulsion", "Sports physics"],
        "misconceptions": ["Force required to maintain motion", "Heavier objects fall faster"],
        "prerequisites": ["ph_kinematics"]
    },
    {
        "id": "ph_work_energy",
        "name": "Work, Energy and Power",
        "domain": "Physics",
        "subdomain": "Mechanics",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Study of energy transformations, work done by forces, and power as rate of doing work.",
        "key_points": [
            "Work = Force × Displacement × cos(θ)",
            "Kinetic energy depends on mass and velocity squared",
            "Potential energy depends on position",
            "Conservation of mechanical energy in conservative systems"
        ],
        "formulas": [
            "W = F·d·cos(θ)",
            "KE = (1/2)mv²",
            "PE = mgh",
            "P = W/t = F·v",
            "Work-Energy theorem: W = ΔKE"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 7, "CBSE": 10},
        "real_world": ["Roller coasters", "Hydroelectric dams", "Car engines"],
        "misconceptions": ["Work always equals force times distance", "Energy can be created"],
        "prerequisites": ["ph_newtons_laws", "vectors"]
    },
    {
        "id": "ph_rotational_motion",
        "name": "Rotational Motion",
        "domain": "Physics",
        "subdomain": "Mechanics",
        "difficulty": "advanced",
        "age_range": (16, 18),
        "description": "Motion of rigid bodies about an axis. Analogous to linear motion with angular quantities.",
        "key_points": [
            "Moment of inertia is rotational analog of mass",
            "Torque causes angular acceleration",
            "Angular momentum is conserved",
            "Rolling motion combines rotation and translation"
        ],
        "formulas": [
            "τ = Iα",
            "L = Iω",
            "KE_rot = (1/2)Iω²",
            "I = Σmr²",
            "v = ωr (for rolling)"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 5, "CBSE": 8},
        "real_world": ["Gyroscopes", "Figure skating spins", "Planetary motion"],
        "misconceptions": ["All rotating objects have same moment of inertia", "Rolling friction is same as sliding"],
        "prerequisites": ["ph_work_energy", "ph_newtons_laws"]
    },
    
    # === THERMODYNAMICS ===
    {
        "id": "ph_thermodynamics",
        "name": "Thermodynamics",
        "domain": "Physics",
        "subdomain": "Heat",
        "difficulty": "advanced",
        "age_range": (16, 18),
        "description": "Study of heat, work, and energy transformations. Includes laws governing heat engines and entropy.",
        "key_points": [
            "First Law: Energy conservation (ΔU = Q - W)",
            "Second Law: Entropy always increases in isolated systems",
            "Isothermal, adiabatic, isobaric, isochoric processes",
            "Carnot cycle gives maximum efficiency"
        ],
        "formulas": [
            "ΔU = Q - W",
            "PV = nRT (Ideal gas)",
            "η = 1 - T_L/T_H (Carnot)",
            "ΔS ≥ Q/T",
            "W = nRT ln(V₂/V₁) (isothermal)"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 6, "CBSE": 9},
        "real_world": ["Car engines", "Refrigerators", "Power plants"],
        "misconceptions": ["Heat and temperature are same", "Cold flows from cold to hot"],
        "prerequisites": ["ph_work_energy", "kinetic_theory"]
    },
    
    # === ELECTROMAGNETISM ===
    {
        "id": "ph_electrostatics",
        "name": "Electrostatics",
        "domain": "Physics",
        "subdomain": "Electromagnetism",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Study of stationary electric charges, electric fields, and potentials.",
        "key_points": [
            "Coulomb's law gives force between point charges",
            "Electric field is force per unit charge",
            "Electric potential is work done per unit charge",
            "Gauss's law relates flux to enclosed charge"
        ],
        "formulas": [
            "F = kq₁q₂/r²",
            "E = F/q = kQ/r²",
            "V = kQ/r",
            "∮E·dA = Q/ε₀ (Gauss)",
            "C = Q/V (Capacitance)"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 7, "CBSE": 10},
        "real_world": ["Photocopiers", "Lightning", "Capacitors in electronics"],
        "misconceptions": ["Electric field exists only near charges", "Conductors have no electric field inside when charged"],
        "prerequisites": ["vectors", "ph_work_energy"]
    },
    {
        "id": "ph_current_electricity",
        "name": "Current Electricity",
        "domain": "Physics",
        "subdomain": "Electromagnetism",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Study of moving charges, electric circuits, and Ohm's law.",
        "key_points": [
            "Current is rate of flow of charge",
            "Ohm's law: V = IR",
            "Resistors in series add, in parallel reciprocals add",
            "Kirchhoff's laws for circuit analysis"
        ],
        "formulas": [
            "I = Q/t",
            "V = IR (Ohm's law)",
            "P = VI = I²R = V²/R",
            "R_series = R₁ + R₂ + ...",
            "1/R_parallel = 1/R₁ + 1/R₂ + ..."
        ],
        "exam_relevance": {"JEE": 9, "NEET": 8, "CBSE": 10},
        "real_world": ["Home wiring", "Phone charging", "Electric vehicles"],
        "misconceptions": ["Current is used up in a circuit", "Batteries store electrons"],
        "prerequisites": ["ph_electrostatics"]
    },
    {
        "id": "ph_magnetism",
        "name": "Magnetism and Magnetic Effects of Current",
        "domain": "Physics",
        "subdomain": "Electromagnetism",
        "difficulty": "advanced",
        "age_range": (16, 18),
        "description": "Study of magnetic fields, their effects on charges and currents, and electromagnetic induction.",
        "key_points": [
            "Moving charges create magnetic fields",
            "Biot-Savart law gives magnetic field due to current",
            "Faraday's law: changing flux induces EMF",
            "Lenz's law gives direction of induced current"
        ],
        "formulas": [
            "F = qvB sin(θ)",
            "B = μ₀I/2πr (infinite wire)",
            "EMF = -dΦ/dt (Faraday)",
            "Φ = B·A·cos(θ)",
            "B = μ₀nI (solenoid)"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 6, "CBSE": 9},
        "real_world": ["Electric motors", "Transformers", "MRI machines"],
        "misconceptions": ["Magnetic field lines are real", "Magnets have monopoles"],
        "prerequisites": ["ph_current_electricity", "vectors"]
    },
    
    # === OPTICS ===
    {
        "id": "ph_optics",
        "name": "Ray Optics and Wave Optics",
        "domain": "Physics",
        "subdomain": "Optics",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Study of light as rays and waves. Covers reflection, refraction, interference, and diffraction.",
        "key_points": [
            "Law of reflection: angle of incidence = angle of reflection",
            "Snell's law: n₁sin(θ₁) = n₂sin(θ₂)",
            "Lens formula: 1/f = 1/v - 1/u",
            "Young's double slit shows wave nature of light"
        ],
        "formulas": [
            "1/f = 1/v - 1/u (lens/mirror)",
            "n₁sin(θ₁) = n₂sin(θ₂)",
            "m = -v/u (magnification)",
            "d sin(θ) = nλ (diffraction)",
            "Path difference = d sin(θ)"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 8, "CBSE": 10},
        "real_world": ["Cameras", "Fiber optics", "Telescopes"],
        "misconceptions": ["Light always travels in straight lines", "Mirrors reverse left-right"],
        "prerequisites": ["trigonometry", "waves"]
    },
    
    # === MODERN PHYSICS ===
    {
        "id": "ph_modern_physics",
        "name": "Modern Physics",
        "domain": "Physics",
        "subdomain": "Modern Physics",
        "difficulty": "advanced",
        "age_range": (17, 18),
        "description": "Covers quantum mechanics basics, photoelectric effect, atomic structure, nuclear physics.",
        "key_points": [
            "Photoelectric effect proves particle nature of light",
            "De Broglie wavelength: matter has wave nature",
            "Bohr model explains hydrogen spectrum",
            "Nuclear reactions follow mass-energy equivalence"
        ],
        "formulas": [
            "E = hf (photon energy)",
            "λ = h/p (de Broglie)",
            "E_n = -13.6/n² eV (hydrogen)",
            "E = mc² (mass-energy)",
            "ΔE = Δm·c² (nuclear)"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 9, "CBSE": 9},
        "real_world": ["Solar cells", "Nuclear power", "Medical imaging"],
        "misconceptions": ["Electrons orbit like planets", "All radiation is harmful"],
        "prerequisites": ["ph_optics", "ph_electrostatics"]
    }
]


# ============================================================================
# CHEMISTRY CURRICULUM - Class 11 & 12 NCERT + JEE/NEET
# ============================================================================

CHEMISTRY_CONCEPTS = [
    # === PHYSICAL CHEMISTRY ===
    {
        "id": "ch_atomic_structure",
        "name": "Atomic Structure",
        "domain": "Chemistry",
        "subdomain": "Physical Chemistry",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Structure of atoms including electrons, protons, neutrons. Quantum mechanical model and electronic configuration.",
        "key_points": [
            "Quantum numbers (n, l, m, s) describe electron state",
            "Aufbau principle, Hund's rule, Pauli exclusion",
            "s, p, d, f orbitals have different shapes",
            "Periodic properties depend on electronic configuration"
        ],
        "formulas": [
            "E_n = -13.6Z²/n² eV",
            "λ = h/mv (de Broglie)",
            "Δx·Δp ≥ h/4π (Heisenberg)",
            "Number of orbitals in subshell = 2l+1"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 8, "CBSE": 10},
        "real_world": ["Spectroscopy", "Lasers", "Electronics"],
        "misconceptions": ["Electrons move in fixed orbits", "Orbitals are physical paths"],
        "prerequisites": ["basic_chemistry"]
    },
    {
        "id": "ch_chemical_bonding",
        "name": "Chemical Bonding",
        "domain": "Chemistry",
        "subdomain": "Physical Chemistry",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "How atoms combine to form molecules. Includes ionic, covalent, metallic bonding and molecular geometry.",
        "key_points": [
            "Ionic bonds form between metals and nonmetals",
            "Covalent bonds share electrons",
            "VSEPR theory predicts molecular geometry",
            "Hybridization explains molecular shapes"
        ],
        "formulas": [
            "Bond order = (bonding - antibonding)/2",
            "Formal charge = V - L - B/2",
            "Dipole moment μ = q × d"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 9, "CBSE": 10},
        "real_world": ["Drug design", "Material science", "Polymer chemistry"],
        "misconceptions": ["All bonds are purely ionic or covalent", "Double bonds are twice as strong"],
        "prerequisites": ["ch_atomic_structure"]
    },
    {
        "id": "ch_thermodynamics",
        "name": "Chemical Thermodynamics",
        "domain": "Chemistry",
        "subdomain": "Physical Chemistry",
        "difficulty": "advanced",
        "age_range": (16, 18),
        "description": "Energy changes in chemical reactions. Enthalpy, entropy, and Gibbs free energy.",
        "key_points": [
            "ΔH is heat change at constant pressure",
            "Entropy is measure of disorder",
            "ΔG determines spontaneity",
            "Hess's law for calculating reaction enthalpies"
        ],
        "formulas": [
            "ΔG = ΔH - TΔS",
            "ΔH_rxn = Σ ΔH_f(products) - Σ ΔH_f(reactants)",
            "ΔS_universe > 0 (spontaneous)",
            "q = mcΔT (heat capacity)"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 7, "CBSE": 9},
        "real_world": ["Fuel efficiency", "Refrigeration", "Industrial processes"],
        "misconceptions": ["Exothermic reactions are always spontaneous", "Entropy can decrease in universe"],
        "prerequisites": ["ch_chemical_bonding", "ph_thermodynamics"]
    },
    {
        "id": "ch_equilibrium",
        "name": "Chemical Equilibrium",
        "domain": "Chemistry",
        "subdomain": "Physical Chemistry",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Dynamic equilibrium in reversible reactions. Le Chatelier's principle and equilibrium constants.",
        "key_points": [
            "At equilibrium, forward = backward rate",
            "Kc and Kp are equilibrium constants",
            "Le Chatelier: system opposes changes",
            "Q vs K determines reaction direction"
        ],
        "formulas": [
            "Kc = [products]/[reactants]",
            "Kp = Kc(RT)^Δn",
            "ΔG = ΔG° + RT ln Q",
            "pH = -log[H⁺]"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 8, "CBSE": 10},
        "real_world": ["Industrial synthesis", "Blood pH regulation", "Acid rain"],
        "misconceptions": ["Equilibrium means reactions stop", "Equal concentrations at equilibrium"],
        "prerequisites": ["ch_thermodynamics"]
    },
    
    # === ORGANIC CHEMISTRY ===
    {
        "id": "ch_organic_basics",
        "name": "Basic Organic Chemistry",
        "domain": "Chemistry",
        "subdomain": "Organic Chemistry",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Foundation of organic chemistry. IUPAC nomenclature, isomerism, and reaction mechanisms.",
        "key_points": [
            "IUPAC naming: longest chain + substituents",
            "Structural, geometrical, and optical isomerism",
            "Inductive and resonance effects",
            "Nucleophiles donate electrons, electrophiles accept"
        ],
        "formulas": [
            "Degree of unsaturation = (2C + 2 + N - H - X)/2",
            "Molecular formula → Structure",
            "Functional group identification"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 10, "CBSE": 10},
        "real_world": ["Pharmaceuticals", "Plastics", "Fuels"],
        "misconceptions": ["Organic = living things only", "All carbon compounds are organic"],
        "prerequisites": ["ch_chemical_bonding"]
    },
    {
        "id": "ch_hydrocarbons",
        "name": "Hydrocarbons",
        "domain": "Chemistry",
        "subdomain": "Organic Chemistry",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Alkanes, alkenes, alkynes, and aromatic compounds. Properties and reactions.",
        "key_points": [
            "Alkanes undergo substitution reactions",
            "Alkenes and alkynes undergo addition reactions",
            "Benzene shows aromatic character (resonance)",
            "Markovnikov's rule for addition to alkenes"
        ],
        "formulas": [
            "CnH2n+2 (alkanes)",
            "CnH2n (alkenes/cycloalkanes)",
            "CnH2n-2 (alkynes)"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 9, "CBSE": 10},
        "real_world": ["Petroleum", "Natural gas", "Plastics"],
        "misconceptions": ["Benzene is hexatriene", "All unsaturated compounds are reactive"],
        "prerequisites": ["ch_organic_basics"]
    },
    
    # === INORGANIC CHEMISTRY ===
    {
        "id": "ch_periodic_table",
        "name": "Periodic Table and Periodicity",
        "domain": "Chemistry",
        "subdomain": "Inorganic Chemistry",
        "difficulty": "beginner",
        "age_range": (15, 18),
        "description": "Organization of elements and periodic trends in properties.",
        "key_points": [
            "Elements arranged by atomic number",
            "Periods (rows) and groups (columns)",
            "Trends: atomic size, ionization energy, electronegativity",
            "s, p, d, f block elements"
        ],
        "formulas": [
            "IE increases left to right, decreases down",
            "Atomic radius decreases left to right",
            "EN increases left to right (Pauling scale)"
        ],
        "exam_relevance": {"JEE": 8, "NEET": 9, "CBSE": 10},
        "real_world": ["Material selection", "Drug design", "Battery chemistry"],
        "misconceptions": ["Noble gases never react", "Metals are always solid"],
        "prerequisites": ["ch_atomic_structure"]
    },
    {
        "id": "ch_coordination_compounds",
        "name": "Coordination Compounds",
        "domain": "Chemistry",
        "subdomain": "Inorganic Chemistry",
        "difficulty": "advanced",
        "age_range": (17, 18),
        "description": "Metal complexes with ligands. Nomenclature, isomerism, and bonding theories.",
        "key_points": [
            "Central metal ion surrounded by ligands",
            "Coordination number = number of ligand atoms",
            "CFT explains color and magnetic properties",
            "Chelate effect stabilizes complexes"
        ],
        "formulas": [
            "CFSE = (-0.4Δ)t₂g + (0.6Δ)eg",
            "Effective atomic number rule",
            "Stability constant β = [complex]/[metal][ligand]"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 6, "CBSE": 8},
        "real_world": ["Hemoglobin", "Catalysts", "Metal extraction"],
        "misconceptions": ["All complexes are colored", "Ligands always donate electron pairs"],
        "prerequisites": ["ch_chemical_bonding", "ch_periodic_table"]
    }
]


# ============================================================================
# BIOLOGY CURRICULUM - Class 11 & 12 NCERT + NEET
# ============================================================================

BIOLOGY_CONCEPTS = [
    # === CELL BIOLOGY ===
    {
        "id": "bio_cell_structure",
        "name": "Cell Structure and Function",
        "domain": "Biology",
        "subdomain": "Cell Biology",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Basic unit of life. Structure and function of cell organelles.",
        "key_points": [
            "Cell membrane is selectively permeable",
            "Nucleus contains genetic material",
            "Mitochondria are powerhouses (ATP production)",
            "Prokaryotes lack membrane-bound organelles"
        ],
        "formulas": [],
        "exam_relevance": {"JEE": 3, "NEET": 10, "CBSE": 10},
        "real_world": ["Cancer research", "Drug delivery", "Biotechnology"],
        "misconceptions": ["Plant cells have no mitochondria", "All cells have nucleus"],
        "prerequisites": ["basic_biology"]
    },
    {
        "id": "bio_cell_division",
        "name": "Cell Division",
        "domain": "Biology",
        "subdomain": "Cell Biology",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Mitosis and meiosis. Cell cycle regulation and chromosomal behavior.",
        "key_points": [
            "Mitosis produces identical cells (2n → 2n)",
            "Meiosis produces gametes (2n → n)",
            "Cell cycle: G1, S, G2, M phases",
            "Crossing over creates genetic variation"
        ],
        "formulas": [
            "DNA amount doubles in S phase",
            "4 daughter cells from meiosis",
            "2 daughter cells from mitosis"
        ],
        "exam_relevance": {"JEE": 2, "NEET": 10, "CBSE": 10},
        "real_world": ["Cancer treatment", "Genetic counseling", "Cloning"],
        "misconceptions": ["Mitosis only in growth", "Meiosis only in gonads"],
        "prerequisites": ["bio_cell_structure"]
    },
    
    # === GENETICS ===
    {
        "id": "bio_genetics",
        "name": "Mendelian Genetics",
        "domain": "Biology",
        "subdomain": "Genetics",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Laws of inheritance discovered by Mendel. Monohybrid and dihybrid crosses.",
        "key_points": [
            "Law of segregation: alleles separate in gametes",
            "Law of independent assortment: genes on different chromosomes",
            "Dominant masks recessive",
            "Punnett square predicts offspring ratios"
        ],
        "formulas": [
            "Monohybrid ratio: 3:1",
            "Dihybrid ratio: 9:3:3:1",
            "Test cross ratio: 1:1 or 1:1:1:1"
        ],
        "exam_relevance": {"JEE": 2, "NEET": 10, "CBSE": 10},
        "real_world": ["Genetic counseling", "Plant breeding", "Disease prediction"],
        "misconceptions": ["Dominant traits are more common", "Genes always show complete dominance"],
        "prerequisites": ["bio_cell_division"]
    },
    {
        "id": "bio_molecular_genetics",
        "name": "Molecular Basis of Inheritance",
        "domain": "Biology",
        "subdomain": "Genetics",
        "difficulty": "advanced",
        "age_range": (16, 18),
        "description": "DNA structure, replication, transcription, and translation.",
        "key_points": [
            "DNA is double helix with A-T and G-C base pairs",
            "Replication is semi-conservative",
            "Transcription: DNA → mRNA",
            "Translation: mRNA → protein"
        ],
        "formulas": [
            "Chargaff's rule: A=T, G=C",
            "Codon = 3 nucleotides = 1 amino acid",
            "64 codons code for 20 amino acids"
        ],
        "exam_relevance": {"JEE": 2, "NEET": 10, "CBSE": 10},
        "real_world": ["Gene therapy", "Forensics (DNA fingerprinting)", "GMOs"],
        "misconceptions": ["One gene = one protein always", "Introns are junk DNA"],
        "prerequisites": ["bio_genetics", "ch_organic_basics"]
    },
    
    # === HUMAN PHYSIOLOGY ===
    {
        "id": "bio_digestion",
        "name": "Digestion and Absorption",
        "domain": "Biology",
        "subdomain": "Human Physiology",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Human digestive system. Mechanical and chemical digestion, absorption.",
        "key_points": [
            "Digestion begins in mouth (salivary amylase)",
            "Stomach: HCl + pepsin for proteins",
            "Small intestine: major site of absorption",
            "Liver produces bile for fat emulsification"
        ],
        "formulas": [],
        "exam_relevance": {"JEE": 1, "NEET": 10, "CBSE": 10},
        "real_world": ["Nutrition planning", "Treating digestive disorders", "Drug absorption"],
        "misconceptions": ["Digestion only in stomach", "Fat is not digested"],
        "prerequisites": ["bio_cell_structure"]
    },
    {
        "id": "bio_circulation",
        "name": "Body Fluids and Circulation",
        "domain": "Biology",
        "subdomain": "Human Physiology",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Blood composition, heart structure, and circulatory system.",
        "key_points": [
            "Blood has plasma and formed elements",
            "Heart has 4 chambers (2 atria, 2 ventricles)",
            "Double circulation: pulmonary + systemic",
            "Cardiac cycle: systole and diastole"
        ],
        "formulas": [
            "Cardiac output = Stroke volume × Heart rate",
            "Blood pressure = Systolic/Diastolic"
        ],
        "exam_relevance": {"JEE": 1, "NEET": 10, "CBSE": 10},
        "real_world": ["Heart disease treatment", "Blood donation", "Exercise physiology"],
        "misconceptions": ["Veins carry only deoxygenated blood", "Heart is on left side only"],
        "prerequisites": ["bio_cell_structure"]
    },
    
    # === ECOLOGY ===
    {
        "id": "bio_ecology",
        "name": "Ecology and Environment",
        "domain": "Biology",
        "subdomain": "Ecology",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Interactions between organisms and environment. Ecosystems, food chains, biogeochemical cycles.",
        "key_points": [
            "Ecosystem = biotic + abiotic components",
            "Energy flows, nutrients cycle",
            "10% law for energy transfer",
            "Ecological pyramids (number, biomass, energy)"
        ],
        "formulas": [
            "GPP - R = NPP",
            "Only 10% energy transfers to next level"
        ],
        "exam_relevance": {"JEE": 1, "NEET": 9, "CBSE": 10},
        "real_world": ["Conservation", "Climate change", "Pollution control"],
        "misconceptions": ["Decomposers are not important", "Only green plants are producers"],
        "prerequisites": ["basic_biology"]
    }
]


# ============================================================================
# MATHEMATICS CURRICULUM - Class 11 & 12 + JEE
# ============================================================================

MATHEMATICS_CONCEPTS = [
    # === ALGEBRA ===
    {
        "id": "math_quadratic",
        "name": "Quadratic Equations",
        "domain": "Mathematics",
        "subdomain": "Algebra",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Equations of form ax² + bx + c = 0. Roots, discriminant, and related concepts.",
        "key_points": [
            "Quadratic formula gives both roots",
            "Discriminant determines nature of roots",
            "Sum of roots = -b/a, Product = c/a",
            "Graph is a parabola"
        ],
        "formulas": [
            "x = (-b ± √(b²-4ac))/2a",
            "D = b² - 4ac (discriminant)",
            "α + β = -b/a",
            "αβ = c/a"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 5, "CBSE": 10},
        "real_world": ["Projectile motion", "Optimization", "Finance"],
        "misconceptions": ["Discriminant is always positive", "Parabola always opens upward"],
        "prerequisites": ["basic_algebra"]
    },
    {
        "id": "math_complex_numbers",
        "name": "Complex Numbers",
        "domain": "Mathematics",
        "subdomain": "Algebra",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Numbers of form a + bi where i² = -1. Argand plane, polar form, De Moivre's theorem.",
        "key_points": [
            "i = √(-1), i² = -1",
            "Argand plane represents complex numbers",
            "Modulus |z| and argument arg(z)",
            "De Moivre's theorem for powers"
        ],
        "formulas": [
            "|z| = √(a² + b²)",
            "z = r(cos θ + i sin θ)",
            "(cos θ + i sin θ)ⁿ = cos nθ + i sin nθ",
            "z · z̄ = |z|²"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 3, "CBSE": 9},
        "real_world": ["Electrical engineering", "Signal processing", "Quantum mechanics"],
        "misconceptions": ["i is imaginary so useless", "Complex numbers aren't real numbers"],
        "prerequisites": ["math_quadratic", "trigonometry"]
    },
    
    # === CALCULUS ===
    {
        "id": "math_limits",
        "name": "Limits and Continuity",
        "domain": "Mathematics",
        "subdomain": "Calculus",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Foundation of calculus. Concept of limit, continuity, and indeterminate forms.",
        "key_points": [
            "Limit is value function approaches",
            "L'Hôpital's rule for indeterminate forms",
            "Continuous if limit = function value",
            "Sandwich theorem for bounded limits"
        ],
        "formulas": [
            "lim(x→0) sin x/x = 1",
            "lim(x→∞) (1 + 1/x)ˣ = e",
            "L'Hôpital: lim f/g = lim f'/g'"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 4, "CBSE": 10},
        "real_world": ["Motion analysis", "Growth models", "Engineering"],
        "misconceptions": ["Limit must equal function value", "0/0 is always undefined"],
        "prerequisites": ["functions", "trigonometry"]
    },
    {
        "id": "math_derivatives",
        "name": "Differentiation",
        "domain": "Mathematics",
        "subdomain": "Calculus",
        "difficulty": "intermediate",
        "age_range": (16, 18),
        "description": "Rate of change and slopes. Derivatives, rules, and applications.",
        "key_points": [
            "Derivative = instantaneous rate of change",
            "Chain rule, product rule, quotient rule",
            "Applications: maxima, minima, optimization",
            "Higher order derivatives"
        ],
        "formulas": [
            "d/dx(xⁿ) = nxⁿ⁻¹",
            "d/dx(eˣ) = eˣ",
            "d/dx(sin x) = cos x",
            "(fg)' = f'g + fg'",
            "(f∘g)' = f'(g) · g'"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 5, "CBSE": 10},
        "real_world": ["Physics (velocity, acceleration)", "Economics (marginal)", "Optimization"],
        "misconceptions": ["Derivative is always positive", "dy/dx is a fraction"],
        "prerequisites": ["math_limits"]
    },
    {
        "id": "math_integration",
        "name": "Integration",
        "domain": "Mathematics",
        "subdomain": "Calculus",
        "difficulty": "advanced",
        "age_range": (16, 18),
        "description": "Reverse of differentiation. Definite and indefinite integrals, techniques, applications.",
        "key_points": [
            "Indefinite integral is antiderivative",
            "Definite integral gives area under curve",
            "Substitution and parts methods",
            "Fundamental theorem of calculus"
        ],
        "formulas": [
            "∫xⁿ dx = xⁿ⁺¹/(n+1) + C",
            "∫eˣ dx = eˣ + C",
            "∫sin x dx = -cos x + C",
            "∫₀^a f dx = F(a) - F(0)"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 4, "CBSE": 10},
        "real_world": ["Area/volume calculation", "Physics (work, flux)", "Statistics"],
        "misconceptions": ["Integration just reverses differentiation", "C doesn't matter"],
        "prerequisites": ["math_derivatives"]
    },
    
    # === COORDINATE GEOMETRY ===
    {
        "id": "math_straight_lines",
        "name": "Straight Lines",
        "domain": "Mathematics",
        "subdomain": "Coordinate Geometry",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Equations of lines, slopes, distances, and related concepts.",
        "key_points": [
            "Slope m = (y₂-y₁)/(x₂-x₁)",
            "Point-slope form: y - y₁ = m(x - x₁)",
            "Distance formula: √((x₂-x₁)² + (y₂-y₁)²)",
            "Perpendicular lines have m₁ × m₂ = -1"
        ],
        "formulas": [
            "y = mx + c (slope-intercept)",
            "ax + by + c = 0 (general form)",
            "Distance = |ax₁ + by₁ + c|/√(a² + b²)"
        ],
        "exam_relevance": {"JEE": 8, "NEET": 4, "CBSE": 10},
        "real_world": ["GPS navigation", "Computer graphics", "Engineering"],
        "misconceptions": ["Parallel lines never have same slope", "Distance is always x₂ - x₁"],
        "prerequisites": ["basic_algebra"]
    },
    {
        "id": "math_conic_sections",
        "name": "Conic Sections",
        "domain": "Mathematics",
        "subdomain": "Coordinate Geometry",
        "difficulty": "advanced",
        "age_range": (16, 18),
        "description": "Circle, ellipse, parabola, hyperbola. Standard forms and properties.",
        "key_points": [
            "Parabola: locus equidistant from focus and directrix",
            "Ellipse: sum of distances from foci is constant",
            "Hyperbola: difference of distances is constant",
            "Eccentricity determines conic type"
        ],
        "formulas": [
            "(x-h)² + (y-k)² = r² (circle)",
            "x²/a² + y²/b² = 1 (ellipse)",
            "y² = 4ax (parabola)",
            "x²/a² - y²/b² = 1 (hyperbola)"
        ],
        "exam_relevance": {"JEE": 10, "NEET": 3, "CBSE": 9},
        "real_world": ["Satellite orbits", "Reflectors", "Bridges"],
        "misconceptions": ["All ellipses are nearly circular", "Hyperbola has no real applications"],
        "prerequisites": ["math_straight_lines"]
    },
    
    # === TRIGONOMETRY ===
    {
        "id": "math_trigonometry",
        "name": "Trigonometry",
        "domain": "Mathematics",
        "subdomain": "Trigonometry",
        "difficulty": "intermediate",
        "age_range": (15, 18),
        "description": "Study of triangles and periodic functions. Identities, equations, and applications.",
        "key_points": [
            "sin²θ + cos²θ = 1",
            "Compound angles: sin(A+B), cos(A+B)",
            "General solutions of trigonometric equations",
            "Inverse trigonometric functions"
        ],
        "formulas": [
            "sin(A+B) = sinA cosB + cosA sinB",
            "cos(A+B) = cosA cosB - sinA sinB",
            "tan(A+B) = (tanA + tanB)/(1 - tanA tanB)",
            "sin 2A = 2 sinA cosA"
        ],
        "exam_relevance": {"JEE": 9, "NEET": 6, "CBSE": 10},
        "real_world": ["Navigation", "Sound waves", "Architecture"],
        "misconceptions": ["sin/cos/tan only for right triangles", "Angles only in degrees"],
        "prerequisites": ["basic_algebra"]
    }
]


def load_curriculum_to_graph():
    """
    Load all curriculum content into the UniversalKnowledgeGraph.
    
    This function populates the knowledge graph with:
    - All Physics concepts
    - All Chemistry concepts
    - All Biology concepts
    - All Mathematics concepts
    - Relationships between concepts
    """
    try:
        from services.knowledge_base.universal_knowledge_graph import (
            get_universal_knowledge_graph,
            ConceptDifficulty,
            RelationType
        )
        
        graph = get_universal_knowledge_graph()
        
        # === Load All Concepts ===
        all_concepts = (
            PHYSICS_CONCEPTS + 
            CHEMISTRY_CONCEPTS + 
            BIOLOGY_CONCEPTS + 
            MATHEMATICS_CONCEPTS
        )
        
        logger.info(f"📚 Loading {len(all_concepts)} concepts into knowledge graph...")
        
        # Difficulty mapping
        difficulty_map = {
            "foundational": ConceptDifficulty.FOUNDATIONAL,
            "beginner": ConceptDifficulty.BEGINNER,
            "intermediate": ConceptDifficulty.INTERMEDIATE,
            "advanced": ConceptDifficulty.ADVANCED,
            "expert": ConceptDifficulty.EXPERT
        }
        
        for concept in all_concepts:
            try:
                graph.add_concept(
                    concept_id=concept["id"],
                    name=concept["name"],
                    domain=concept["domain"],
                    subdomain=concept["subdomain"],
                    difficulty=difficulty_map.get(concept["difficulty"], ConceptDifficulty.INTERMEDIATE),
                    age_range=concept["age_range"],
                    description=concept["description"],
                    key_points=concept.get("key_points", []),
                    formulas=concept.get("formulas", []),
                    exam_relevance=concept.get("exam_relevance", {}),
                    real_world_applications=concept.get("real_world", []),
                    common_misconceptions=concept.get("misconceptions", []),
                    tags=concept.get("prerequisites", [])
                )
            except Exception as e:
                logger.warning(f"Failed to add concept {concept['id']}: {e}")
        
        # === Add Relationships ===
        logger.info("📚 Adding concept relationships...")
        
        for concept in all_concepts:
            prereqs = concept.get("prerequisites", [])
            for prereq in prereqs:
                try:
                    graph.add_relationship(
                        from_concept=prereq,
                        to_concept=concept["id"],
                        relation_type=RelationType.PREREQUISITE,
                        strength=0.8,
                        explanation=f"{prereq} is prerequisite for {concept['name']}"
                    )
                except Exception as e:
                    logger.debug(f"Could not add relationship {prereq} → {concept['id']}: {e}")
        
        logger.info(f"✅ Knowledge graph loaded with {len(graph.nodes)} concepts and {len(graph.edges)} relationships")
        
        return graph
        
    except Exception as e:
        logger.error(f"❌ Failed to load curriculum: {e}", exc_info=True)
        return None


def get_concept_by_query(query: str) -> List[Dict[str, Any]]:
    """
    Search curriculum for concepts matching a query.
    
    Args:
        query: Search query
        
    Returns:
        List of matching concept dictionaries
    """
    query_lower = query.lower()
    results = []
    
    all_concepts = (
        PHYSICS_CONCEPTS + 
        CHEMISTRY_CONCEPTS + 
        BIOLOGY_CONCEPTS + 
        MATHEMATICS_CONCEPTS
    )
    
    for concept in all_concepts:
        score = 0
        
        # Check name match
        if query_lower in concept["name"].lower():
            score += 10
        
        # Check description match
        if query_lower in concept["description"].lower():
            score += 5
        
        # Check key points
        for point in concept.get("key_points", []):
            if query_lower in point.lower():
                score += 3
        
        # Check formulas
        for formula in concept.get("formulas", []):
            if query_lower in formula.lower():
                score += 4
        
        if score > 0:
            results.append({**concept, "_score": score})
    
    # Sort by score
    results.sort(key=lambda x: x["_score"], reverse=True)
    
    return results[:5]  # Return top 5


# Auto-load on import (if knowledge graph available)
def init_curriculum():
    """Initialize curriculum - call on startup"""
    try:
        return load_curriculum_to_graph()
    except Exception as e:
        logger.warning(f"Curriculum auto-load failed: {e}")
        return None

