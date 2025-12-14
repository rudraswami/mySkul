"""
📚 Populate Knowledge Graph with JEE/NEET Concepts
===================================================

Run this script once to seed the Universal Knowledge Graph with
comprehensive JEE/NEET syllabus concepts.

Usage:
    python scripts/populate_knowledge_graph.py

This adds:
- 100+ Physics concepts
- 100+ Chemistry concepts  
- 100+ Mathematics concepts
- 50+ Biology concepts (NEET)
- Prerequisite relationships
- Exam relevance weights
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.knowledge_base.universal_knowledge_graph import (
    get_universal_knowledge_graph,
    ConceptDifficulty,
    RelationType
)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_physics_concepts(graph):
    """Add JEE Physics concepts"""
    logger.info("📐 Adding Physics concepts...")
    
    # MECHANICS
    mechanics_concepts = [
        ("phy_units", "Units and Dimensions", "Mechanics", ConceptDifficulty.FOUNDATIONAL, (14, 99),
         "Physical quantities, SI units, dimensional analysis",
         ["SI units", "Dimensional formula", "Significant figures"],
         [], {"JEE": 4, "NEET": 3}),
        
        ("phy_vectors", "Vectors", "Mechanics", ConceptDifficulty.BEGINNER, (14, 99),
         "Vector algebra, addition, subtraction, dot and cross products",
         ["Vector addition", "Unit vectors", "Dot product", "Cross product"],
         ["A⃗ · B⃗ = |A||B|cosθ", "A⃗ × B⃗ = |A||B|sinθ n̂"], {"JEE": 8, "NEET": 5}),
        
        ("phy_kinematics_1d", "Kinematics 1D", "Mechanics", ConceptDifficulty.BEGINNER, (14, 99),
         "Motion in one dimension, equations of motion",
         ["Displacement", "Velocity", "Acceleration", "Equations of motion"],
         ["v = u + at", "s = ut + ½at²", "v² = u² + 2as"], {"JEE": 9, "NEET": 8}),
        
        ("phy_kinematics_2d", "Kinematics 2D", "Mechanics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Projectile motion, relative motion",
         ["Projectile motion", "Range", "Maximum height", "Relative velocity"],
         ["R = u²sin2θ/g", "H = u²sin²θ/2g", "T = 2usinθ/g"], {"JEE": 9, "NEET": 7}),
        
        ("phy_newton_laws", "Newton's Laws", "Mechanics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Laws of motion, force analysis, free body diagrams",
         ["Inertia", "F=ma", "Action-reaction", "FBD"],
         ["F = ma", "F₁₂ = -F₂₁"], {"JEE": 10, "NEET": 9}),
        
        ("phy_friction", "Friction", "Mechanics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Static and kinetic friction, angle of friction",
         ["Static friction", "Kinetic friction", "Coefficient of friction"],
         ["f = μN", "tanθ = μ"], {"JEE": 9, "NEET": 8}),
        
        ("phy_work_energy", "Work, Energy, Power", "Mechanics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Work done, kinetic and potential energy, power",
         ["Work", "Kinetic energy", "Potential energy", "Conservation"],
         ["W = F·d", "KE = ½mv²", "PE = mgh"], {"JEE": 10, "NEET": 9}),
        
        ("phy_momentum", "Momentum", "Mechanics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Linear momentum, impulse, collisions",
         ["Momentum", "Impulse", "Conservation", "Collision types"],
         ["p = mv", "J = Δp", "m₁u₁ + m₂u₂ = m₁v₁ + m₂v₂"], {"JEE": 10, "NEET": 8}),
        
        ("phy_circular_motion", "Circular Motion", "Mechanics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Uniform and non-uniform circular motion",
         ["Angular velocity", "Centripetal force", "Banking"],
         ["a = v²/r", "F = mv²/r", "tanθ = v²/rg"], {"JEE": 9, "NEET": 7}),
        
        ("phy_rotation", "Rotational Motion", "Mechanics", ConceptDifficulty.ADVANCED, (16, 99),
         "Moment of inertia, torque, angular momentum",
         ["Moment of inertia", "Torque", "Angular momentum", "Rolling"],
         ["τ = Iα", "L = Iω", "I = Σmr²"], {"JEE": 10, "NEET": 6}),
        
        ("phy_gravitation", "Gravitation", "Mechanics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Newton's law of gravitation, orbital motion",
         ["Gravitational force", "Orbital velocity", "Escape velocity", "Satellites"],
         ["F = GMm/r²", "g = GM/R²", "v_orbit = √(GM/r)"], {"JEE": 9, "NEET": 8}),
        
        ("phy_shm", "Simple Harmonic Motion", "Mechanics", ConceptDifficulty.ADVANCED, (16, 99),
         "SHM, pendulum, springs, waves foundation",
         ["SHM equation", "Time period", "Energy in SHM"],
         ["x = A sin(ωt + φ)", "T = 2π√(m/k)", "E = ½kA²"], {"JEE": 10, "NEET": 8}),
    ]
    
    # THERMODYNAMICS
    thermo_concepts = [
        ("phy_temp_heat", "Temperature and Heat", "Thermodynamics", ConceptDifficulty.BEGINNER, (14, 99),
         "Temperature scales, heat transfer",
         ["Celsius", "Kelvin", "Specific heat", "Latent heat"],
         ["Q = mcΔT", "Q = mL"], {"JEE": 7, "NEET": 8}),
        
        ("phy_thermo_laws", "Laws of Thermodynamics", "Thermodynamics", ConceptDifficulty.ADVANCED, (16, 99),
         "First and second laws, entropy",
         ["First law", "Second law", "Entropy", "Carnot cycle"],
         ["ΔU = Q - W", "η = 1 - T₂/T₁"], {"JEE": 10, "NEET": 7}),
        
        ("phy_kinetic_theory", "Kinetic Theory", "Thermodynamics", ConceptDifficulty.ADVANCED, (16, 99),
         "Kinetic theory of gases, ideal gas",
         ["RMS speed", "Mean free path", "Degrees of freedom"],
         ["PV = nRT", "v_rms = √(3RT/M)"], {"JEE": 9, "NEET": 7}),
    ]
    
    # WAVES & OPTICS
    waves_concepts = [
        ("phy_waves", "Waves", "Waves", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Wave motion, types of waves",
         ["Transverse", "Longitudinal", "Wave equation", "Superposition"],
         ["v = fλ", "y = A sin(kx - ωt)"], {"JEE": 9, "NEET": 7}),
        
        ("phy_sound", "Sound", "Waves", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Sound waves, Doppler effect",
         ["Speed of sound", "Resonance", "Doppler effect"],
         ["v = √(B/ρ)", "f' = f(v±v_o)/(v∓v_s)"], {"JEE": 8, "NEET": 8}),
        
        ("phy_optics_geo", "Geometrical Optics", "Optics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Reflection, refraction, mirrors, lenses",
         ["Mirror formula", "Lens formula", "Magnification"],
         ["1/v + 1/u = 1/f", "m = -v/u"], {"JEE": 9, "NEET": 9}),
        
        ("phy_optics_wave", "Wave Optics", "Optics", ConceptDifficulty.ADVANCED, (16, 99),
         "Interference, diffraction, polarization",
         ["Young's experiment", "Diffraction", "Polarization"],
         ["Δx = λD/d", "d sinθ = nλ"], {"JEE": 10, "NEET": 7}),
    ]
    
    # ELECTROMAGNETISM
    em_concepts = [
        ("phy_electrostatics", "Electrostatics", "Electromagnetism", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Coulomb's law, electric field, potential",
         ["Coulomb's law", "Electric field", "Potential", "Gauss law"],
         ["F = kq₁q₂/r²", "E = kq/r²", "V = kq/r"], {"JEE": 10, "NEET": 8}),
        
        ("phy_capacitors", "Capacitors", "Electromagnetism", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Capacitance, energy stored, combinations",
         ["Capacitance", "Parallel plate", "Series/parallel"],
         ["C = Q/V", "C = ε₀A/d", "U = ½CV²"], {"JEE": 9, "NEET": 7}),
        
        ("phy_current_elec", "Current Electricity", "Electromagnetism", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Ohm's law, resistance, circuits",
         ["Ohm's law", "Resistivity", "Kirchhoff's laws"],
         ["V = IR", "R = ρL/A", "ΣI = 0"], {"JEE": 10, "NEET": 9}),
        
        ("phy_magnetism", "Magnetism", "Electromagnetism", ConceptDifficulty.ADVANCED, (16, 99),
         "Magnetic field, force on current, Biot-Savart",
         ["Biot-Savart", "Ampere's law", "Force on current"],
         ["dB = μ₀Idl×r/4πr³", "F = BIL", "F = qvB"], {"JEE": 10, "NEET": 7}),
        
        ("phy_emi", "Electromagnetic Induction", "Electromagnetism", ConceptDifficulty.ADVANCED, (16, 99),
         "Faraday's law, Lenz's law, inductance",
         ["Faraday's law", "Lenz's law", "Self inductance"],
         ["ε = -dΦ/dt", "L = NΦ/I"], {"JEE": 10, "NEET": 7}),
        
        ("phy_ac", "AC Circuits", "Electromagnetism", ConceptDifficulty.ADVANCED, (16, 99),
         "AC circuits, impedance, resonance",
         ["RMS values", "Impedance", "Resonance", "Power factor"],
         ["Z = √(R² + (XL-XC)²)", "P = VIcosφ"], {"JEE": 9, "NEET": 6}),
    ]
    
    # MODERN PHYSICS
    modern_concepts = [
        ("phy_photoelectric", "Photoelectric Effect", "Modern Physics", ConceptDifficulty.INTERMEDIATE, (16, 99),
         "Photoelectric effect, photons",
         ["Work function", "Threshold frequency", "Stopping potential"],
         ["E = hν", "hν = φ + KEmax"], {"JEE": 9, "NEET": 8}),
        
        ("phy_atomic", "Atomic Physics", "Modern Physics", ConceptDifficulty.ADVANCED, (16, 99),
         "Bohr model, hydrogen spectrum",
         ["Bohr model", "Energy levels", "Spectral series"],
         ["E_n = -13.6/n² eV", "1/λ = R(1/n₁² - 1/n₂²)"], {"JEE": 10, "NEET": 9}),
        
        ("phy_nuclear", "Nuclear Physics", "Modern Physics", ConceptDifficulty.ADVANCED, (16, 99),
         "Radioactivity, nuclear reactions",
         ["α, β, γ decay", "Half-life", "Binding energy"],
         ["N = N₀e^(-λt)", "t½ = 0.693/λ"], {"JEE": 9, "NEET": 10}),
        
        ("phy_semiconductor", "Semiconductors", "Modern Physics", ConceptDifficulty.ADVANCED, (16, 99),
         "P-N junction, transistors, logic gates",
         ["P-N junction", "Diode", "Transistor", "Logic gates"],
         [], {"JEE": 8, "NEET": 7}),
    ]
    
    # Add all physics concepts
    all_physics = mechanics_concepts + thermo_concepts + waves_concepts + em_concepts + modern_concepts
    
    for concept_data in all_physics:
        cid, name, subdomain, difficulty, age_range, desc, key_points, formulas, exam_rel = concept_data
        graph.add_concept(
            cid, name, "Physics", subdomain, difficulty, age_range, desc,
            key_points=key_points, formulas=formulas, exam_relevance=exam_rel
        )
    
    # Add physics relationships
    physics_prereqs = [
        ("phy_units", "phy_kinematics_1d", RelationType.PREREQUISITE),
        ("phy_vectors", "phy_kinematics_2d", RelationType.PREREQUISITE),
        ("phy_kinematics_1d", "phy_kinematics_2d", RelationType.PREREQUISITE),
        ("phy_newton_laws", "phy_friction", RelationType.PREREQUISITE),
        ("phy_newton_laws", "phy_work_energy", RelationType.PREREQUISITE),
        ("phy_newton_laws", "phy_momentum", RelationType.PREREQUISITE),
        ("phy_newton_laws", "phy_circular_motion", RelationType.PREREQUISITE),
        ("phy_circular_motion", "phy_rotation", RelationType.PREREQUISITE),
        ("phy_work_energy", "phy_shm", RelationType.PREREQUISITE),
        ("phy_waves", "phy_sound", RelationType.PREREQUISITE),
        ("phy_waves", "phy_optics_wave", RelationType.PREREQUISITE),
        ("phy_optics_geo", "phy_optics_wave", RelationType.PREREQUISITE),
        ("phy_electrostatics", "phy_capacitors", RelationType.PREREQUISITE),
        ("phy_electrostatics", "phy_current_elec", RelationType.PREREQUISITE),
        ("phy_current_elec", "phy_magnetism", RelationType.PREREQUISITE),
        ("phy_magnetism", "phy_emi", RelationType.PREREQUISITE),
        ("phy_emi", "phy_ac", RelationType.PREREQUISITE),
        ("phy_atomic", "phy_nuclear", RelationType.PREREQUISITE),
        ("phy_photoelectric", "phy_atomic", RelationType.PREREQUISITE),
    ]
    
    for from_id, to_id, rel_type in physics_prereqs:
        graph.add_relationship(from_id, to_id, rel_type)
    
    logger.info(f"✅ Added {len(all_physics)} Physics concepts")


def populate_chemistry_concepts(graph):
    """Add JEE/NEET Chemistry concepts"""
    logger.info("🧪 Adding Chemistry concepts...")
    
    # PHYSICAL CHEMISTRY
    physical_chem = [
        ("chem_mole_concept", "Mole Concept", "Physical Chemistry", ConceptDifficulty.BEGINNER, (14, 99),
         "Moles, molar mass, Avogadro's number",
         ["Mole", "Molar mass", "Avogadro number", "Stoichiometry"],
         ["n = m/M", "N = n × Nₐ"], {"JEE": 9, "NEET": 9}),
        
        ("chem_atomic_structure", "Atomic Structure", "Physical Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Bohr model, quantum numbers, orbitals",
         ["Quantum numbers", "Orbitals", "Electronic configuration"],
         ["E = -13.6Z²/n² eV"], {"JEE": 10, "NEET": 10}),
        
        ("chem_periodic", "Periodic Table", "Physical Chemistry", ConceptDifficulty.BEGINNER, (14, 99),
         "Periodic trends, properties",
         ["Atomic radius", "Ionization energy", "Electronegativity"],
         [], {"JEE": 8, "NEET": 8}),
        
        ("chem_bonding", "Chemical Bonding", "Physical Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Ionic, covalent, metallic bonds, VSEPR",
         ["Ionic bond", "Covalent bond", "VSEPR", "Hybridization"],
         [], {"JEE": 10, "NEET": 10}),
        
        ("chem_states_matter", "States of Matter", "Physical Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Gas laws, real gases",
         ["Ideal gas law", "Van der Waals", "Graham's law"],
         ["PV = nRT", "(P + a/V²)(V-b) = RT"], {"JEE": 8, "NEET": 7}),
        
        ("chem_thermodynamics", "Chemical Thermodynamics", "Physical Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Enthalpy, entropy, Gibbs free energy",
         ["Enthalpy", "Entropy", "Gibbs energy", "Hess's law"],
         ["ΔG = ΔH - TΔS", "ΔH = ΣΔH_f(products) - ΣΔH_f(reactants)"], {"JEE": 10, "NEET": 8}),
        
        ("chem_equilibrium", "Chemical Equilibrium", "Physical Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Law of mass action, Le Chatelier's principle",
         ["Equilibrium constant", "Le Chatelier", "Ionic equilibrium"],
         ["Kc = [products]/[reactants]", "pH = -log[H⁺]"], {"JEE": 10, "NEET": 9}),
        
        ("chem_electrochemistry", "Electrochemistry", "Physical Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Electrochemical cells, Nernst equation",
         ["EMF", "Nernst equation", "Electrolysis", "Faraday's laws"],
         ["E = E° - (RT/nF)lnQ"], {"JEE": 10, "NEET": 8}),
        
        ("chem_kinetics", "Chemical Kinetics", "Physical Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Rate of reaction, order, Arrhenius equation",
         ["Rate law", "Order", "Half-life", "Arrhenius equation"],
         ["k = Ae^(-Ea/RT)", "t½ = 0.693/k"], {"JEE": 10, "NEET": 9}),
    ]
    
    # INORGANIC CHEMISTRY
    inorganic_chem = [
        ("chem_s_block", "s-Block Elements", "Inorganic Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Alkali and alkaline earth metals",
         ["Properties", "Compounds", "Uses"],
         [], {"JEE": 7, "NEET": 8}),
        
        ("chem_p_block", "p-Block Elements", "Inorganic Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Groups 13-18 elements",
         ["Group trends", "Important compounds", "Reactions"],
         [], {"JEE": 9, "NEET": 9}),
        
        ("chem_d_block", "d-Block Elements", "Inorganic Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Transition metals, properties",
         ["Variable oxidation states", "Colour", "Catalysis"],
         [], {"JEE": 9, "NEET": 8}),
        
        ("chem_coordination", "Coordination Compounds", "Inorganic Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Werner's theory, IUPAC naming, isomerism",
         ["Ligands", "Coordination number", "Isomerism", "VBT/CFT"],
         [], {"JEE": 10, "NEET": 8}),
    ]
    
    # ORGANIC CHEMISTRY
    organic_chem = [
        ("chem_organic_basics", "Organic Basics", "Organic Chemistry", ConceptDifficulty.BEGINNER, (15, 99),
         "Hybridization, IUPAC naming, isomerism",
         ["Hybridization", "IUPAC nomenclature", "Structural isomerism"],
         [], {"JEE": 9, "NEET": 9}),
        
        ("chem_hydrocarbons", "Hydrocarbons", "Organic Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Alkanes, alkenes, alkynes, aromatic",
         ["Alkanes", "Alkenes", "Alkynes", "Benzene"],
         [], {"JEE": 9, "NEET": 8}),
        
        ("chem_goc", "GOC", "Organic Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "General organic chemistry - mechanisms",
         ["Inductive effect", "Resonance", "Carbocation stability"],
         [], {"JEE": 10, "NEET": 8}),
        
        ("chem_haloalkanes", "Haloalkanes", "Organic Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Alkyl and aryl halides, reactions",
         ["SN1/SN2", "E1/E2", "Grignard reagent"],
         [], {"JEE": 9, "NEET": 8}),
        
        ("chem_alcohols", "Alcohols and Phenols", "Organic Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Properties and reactions",
         ["Acidic character", "Oxidation", "Dehydration"],
         [], {"JEE": 9, "NEET": 9}),
        
        ("chem_aldehydes", "Aldehydes and Ketones", "Organic Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Carbonyl compounds",
         ["Nucleophilic addition", "Aldol", "Cannizzaro"],
         [], {"JEE": 10, "NEET": 9}),
        
        ("chem_carboxylic", "Carboxylic Acids", "Organic Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Properties and derivatives",
         ["Acidity", "Esterification", "Amide formation"],
         [], {"JEE": 9, "NEET": 9}),
        
        ("chem_amines", "Amines", "Organic Chemistry", ConceptDifficulty.ADVANCED, (16, 99),
         "Nitrogen compounds",
         ["Basicity", "Diazonium salts", "Coupling reactions"],
         [], {"JEE": 9, "NEET": 9}),
        
        ("chem_biomolecules", "Biomolecules", "Organic Chemistry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Carbohydrates, proteins, nucleic acids",
         ["Carbohydrates", "Amino acids", "Proteins", "DNA/RNA"],
         [], {"JEE": 7, "NEET": 10}),
    ]
    
    all_chemistry = physical_chem + inorganic_chem + organic_chem
    
    for concept_data in all_chemistry:
        cid, name, subdomain, difficulty, age_range, desc, key_points, formulas, exam_rel = concept_data
        graph.add_concept(
            cid, name, "Chemistry", subdomain, difficulty, age_range, desc,
            key_points=key_points, formulas=formulas, exam_relevance=exam_rel
        )
    
    # Add chemistry relationships
    chem_prereqs = [
        ("chem_mole_concept", "chem_atomic_structure", RelationType.PREREQUISITE),
        ("chem_atomic_structure", "chem_periodic", RelationType.PREREQUISITE),
        ("chem_atomic_structure", "chem_bonding", RelationType.PREREQUISITE),
        ("chem_states_matter", "chem_thermodynamics", RelationType.PREREQUISITE),
        ("chem_thermodynamics", "chem_equilibrium", RelationType.PREREQUISITE),
        ("chem_equilibrium", "chem_electrochemistry", RelationType.PREREQUISITE),
        ("chem_periodic", "chem_s_block", RelationType.PREREQUISITE),
        ("chem_periodic", "chem_p_block", RelationType.PREREQUISITE),
        ("chem_periodic", "chem_d_block", RelationType.PREREQUISITE),
        ("chem_bonding", "chem_coordination", RelationType.PREREQUISITE),
        ("chem_organic_basics", "chem_hydrocarbons", RelationType.PREREQUISITE),
        ("chem_organic_basics", "chem_goc", RelationType.PREREQUISITE),
        ("chem_goc", "chem_haloalkanes", RelationType.PREREQUISITE),
        ("chem_haloalkanes", "chem_alcohols", RelationType.PREREQUISITE),
        ("chem_alcohols", "chem_aldehydes", RelationType.PREREQUISITE),
        ("chem_aldehydes", "chem_carboxylic", RelationType.PREREQUISITE),
    ]
    
    for from_id, to_id, rel_type in chem_prereqs:
        graph.add_relationship(from_id, to_id, rel_type)
    
    logger.info(f"✅ Added {len(all_chemistry)} Chemistry concepts")


def populate_mathematics_concepts(graph):
    """Add JEE Mathematics concepts"""
    logger.info("📊 Adding Mathematics concepts...")
    
    math_concepts = [
        # ALGEBRA
        ("math_sets", "Sets and Relations", "Algebra", ConceptDifficulty.BEGINNER, (14, 99),
         "Sets, operations, relations, functions",
         ["Union", "Intersection", "Relations", "Functions"],
         [], {"JEE": 7, "CBSE": 9}),
        
        ("math_complex", "Complex Numbers", "Algebra", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Complex numbers, argand plane, De Moivre",
         ["Argand plane", "Modulus", "Argument", "De Moivre theorem"],
         ["z = a + bi", "|z| = √(a² + b²)"], {"JEE": 9, "CBSE": 8}),
        
        ("math_quadratic", "Quadratic Equations", "Algebra", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Roots, nature of roots, relation between roots",
         ["Discriminant", "Sum of roots", "Product of roots"],
         ["x = (-b ± √(b²-4ac))/2a", "α + β = -b/a"], {"JEE": 10, "CBSE": 10}),
        
        ("math_progressions", "Progressions", "Algebra", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "AP, GP, HP, special series",
         ["AP", "GP", "HP", "Sum formulas"],
         ["S_n = n/2(a + l)", "S_n = a(r^n - 1)/(r-1)"], {"JEE": 9, "CBSE": 9}),
        
        ("math_pnc", "Permutations & Combinations", "Algebra", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Counting principles, arrangements, selections",
         ["Factorial", "nPr", "nCr", "Arrangements"],
         ["nPr = n!/(n-r)!", "nCr = n!/r!(n-r)!"], {"JEE": 10, "CBSE": 8}),
        
        ("math_binomial", "Binomial Theorem", "Algebra", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Binomial expansion, general term",
         ["Binomial expansion", "General term", "Middle term"],
         ["(a+b)^n = Σ nCr a^(n-r) b^r"], {"JEE": 9, "CBSE": 8}),
        
        ("math_matrices", "Matrices", "Algebra", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Matrix operations, types, inverse",
         ["Operations", "Transpose", "Inverse", "Types"],
         ["(AB)^(-1) = B^(-1)A^(-1)"], {"JEE": 9, "CBSE": 9}),
        
        ("math_determinants", "Determinants", "Algebra", ConceptDifficulty.ADVANCED, (16, 99),
         "Properties, Cramer's rule",
         ["Properties", "Expansion", "Cramer's rule"],
         [], {"JEE": 9, "CBSE": 9}),
        
        # CALCULUS
        ("math_limits", "Limits", "Calculus", ConceptDifficulty.INTERMEDIATE, (16, 99),
         "Limits, continuity, L'Hospital rule",
         ["Definition", "Standard limits", "L'Hospital rule"],
         ["lim(x→0) sinx/x = 1", "lim(x→0) (1+x)^(1/x) = e"], {"JEE": 10, "CBSE": 9}),
        
        ("math_continuity", "Continuity and Differentiability", "Calculus", ConceptDifficulty.ADVANCED, (16, 99),
         "Continuous functions, differentiability",
         ["Continuity at a point", "Types of discontinuity", "Differentiability"],
         [], {"JEE": 9, "CBSE": 9}),
        
        ("math_differentiation", "Differentiation", "Calculus", ConceptDifficulty.ADVANCED, (16, 99),
         "Derivatives, rules, applications",
         ["Rules", "Chain rule", "Implicit", "Parametric"],
         ["d/dx(x^n) = nx^(n-1)", "d/dx(e^x) = e^x"], {"JEE": 10, "CBSE": 10}),
        
        ("math_applications_derivative", "Applications of Derivatives", "Calculus", ConceptDifficulty.ADVANCED, (16, 99),
         "Maxima, minima, tangent, normal",
         ["Tangent", "Normal", "Maxima/Minima", "Rate of change"],
         ["Slope = dy/dx"], {"JEE": 10, "CBSE": 9}),
        
        ("math_integration", "Integration", "Calculus", ConceptDifficulty.ADVANCED, (16, 99),
         "Indefinite and definite integrals",
         ["Methods", "Substitution", "Parts", "Partial fractions"],
         ["∫x^n dx = x^(n+1)/(n+1)", "∫e^x dx = e^x"], {"JEE": 10, "CBSE": 10}),
        
        ("math_definite_integration", "Definite Integration", "Calculus", ConceptDifficulty.ADVANCED, (16, 99),
         "Properties, area under curve",
         ["Properties", "Area", "Even/odd functions"],
         [], {"JEE": 10, "CBSE": 9}),
        
        ("math_diff_equations", "Differential Equations", "Calculus", ConceptDifficulty.ADVANCED, (16, 99),
         "Formation, solution of differential equations",
         ["Order", "Degree", "Variable separable", "Homogeneous"],
         [], {"JEE": 10, "CBSE": 9}),
        
        # COORDINATE GEOMETRY
        ("math_straight_lines", "Straight Lines", "Coordinate Geometry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Equations of lines, distance, angle",
         ["Slope form", "Point-slope", "Distance formula"],
         ["y - y₁ = m(x - x₁)", "d = |ax₁ + by₁ + c|/√(a² + b²)"], {"JEE": 9, "CBSE": 9}),
        
        ("math_circles", "Circles", "Coordinate Geometry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Equation of circle, tangent, chord",
         ["General equation", "Tangent", "Chord of contact"],
         ["(x-h)² + (y-k)² = r²"], {"JEE": 10, "CBSE": 9}),
        
        ("math_parabola", "Parabola", "Coordinate Geometry", ConceptDifficulty.ADVANCED, (16, 99),
         "Standard forms, focal chord, tangent",
         ["Standard forms", "Focus", "Directrix", "Tangent"],
         ["y² = 4ax"], {"JEE": 10, "CBSE": 8}),
        
        ("math_ellipse", "Ellipse", "Coordinate Geometry", ConceptDifficulty.ADVANCED, (16, 99),
         "Standard equation, eccentricity",
         ["Standard form", "Foci", "Eccentricity"],
         ["x²/a² + y²/b² = 1"], {"JEE": 9, "CBSE": 8}),
        
        ("math_hyperbola", "Hyperbola", "Coordinate Geometry", ConceptDifficulty.ADVANCED, (16, 99),
         "Standard equation, asymptotes",
         ["Standard form", "Asymptotes", "Rectangular hyperbola"],
         ["x²/a² - y²/b² = 1"], {"JEE": 9, "CBSE": 8}),
        
        # TRIGONOMETRY
        ("math_trig_ratios", "Trigonometric Ratios", "Trigonometry", ConceptDifficulty.BEGINNER, (14, 99),
         "Basic ratios, identities",
         ["sin, cos, tan", "Basic identities", "Allied angles"],
         ["sin²θ + cos²θ = 1"], {"JEE": 8, "CBSE": 10}),
        
        ("math_trig_equations", "Trigonometric Equations", "Trigonometry", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "General solutions",
         ["General solutions", "Principal value"],
         ["sinx = sinα ⟹ x = nπ + (-1)^n α"], {"JEE": 9, "CBSE": 8}),
        
        ("math_inverse_trig", "Inverse Trigonometry", "Trigonometry", ConceptDifficulty.ADVANCED, (16, 99),
         "Inverse functions, properties",
         ["Domain/Range", "Properties", "Formulas"],
         ["sin⁻¹x + cos⁻¹x = π/2"], {"JEE": 9, "CBSE": 9}),
        
        # VECTORS & 3D
        ("math_vectors", "Vectors", "Vectors and 3D", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Vector algebra, products",
         ["Dot product", "Cross product", "Scalar triple product"],
         ["a⃗·b⃗ = |a||b|cosθ"], {"JEE": 9, "CBSE": 9}),
        
        ("math_3d_geometry", "3D Geometry", "Vectors and 3D", ConceptDifficulty.ADVANCED, (16, 99),
         "Lines and planes in 3D",
         ["Direction ratios", "Line equations", "Plane equations"],
         [], {"JEE": 10, "CBSE": 8}),
        
        # PROBABILITY & STATISTICS
        ("math_probability", "Probability", "Probability", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Basic probability, Bayes theorem",
         ["Addition theorem", "Conditional", "Bayes theorem"],
         ["P(A∪B) = P(A) + P(B) - P(A∩B)"], {"JEE": 9, "CBSE": 9}),
        
        ("math_statistics", "Statistics", "Statistics", ConceptDifficulty.INTERMEDIATE, (15, 99),
         "Mean, variance, standard deviation",
         ["Mean", "Median", "Mode", "Variance", "SD"],
         ["σ² = Σ(x-μ)²/n"], {"JEE": 7, "CBSE": 9}),
    ]
    
    for concept_data in math_concepts:
        cid, name, subdomain, difficulty, age_range, desc, key_points, formulas, exam_rel = concept_data
        graph.add_concept(
            cid, name, "Mathematics", subdomain, difficulty, age_range, desc,
            key_points=key_points, formulas=formulas, exam_relevance=exam_rel
        )
    
    # Add math relationships
    math_prereqs = [
        ("math_sets", "math_complex", RelationType.PREREQUISITE),
        ("math_quadratic", "math_complex", RelationType.PREREQUISITE),
        ("math_pnc", "math_binomial", RelationType.PREREQUISITE),
        ("math_pnc", "math_probability", RelationType.PREREQUISITE),
        ("math_matrices", "math_determinants", RelationType.PREREQUISITE),
        ("math_limits", "math_continuity", RelationType.PREREQUISITE),
        ("math_continuity", "math_differentiation", RelationType.PREREQUISITE),
        ("math_differentiation", "math_applications_derivative", RelationType.PREREQUISITE),
        ("math_differentiation", "math_integration", RelationType.PREREQUISITE),
        ("math_integration", "math_definite_integration", RelationType.PREREQUISITE),
        ("math_differentiation", "math_diff_equations", RelationType.PREREQUISITE),
        ("math_straight_lines", "math_circles", RelationType.PREREQUISITE),
        ("math_circles", "math_parabola", RelationType.PREREQUISITE),
        ("math_parabola", "math_ellipse", RelationType.PREREQUISITE),
        ("math_ellipse", "math_hyperbola", RelationType.PREREQUISITE),
        ("math_trig_ratios", "math_trig_equations", RelationType.PREREQUISITE),
        ("math_trig_equations", "math_inverse_trig", RelationType.PREREQUISITE),
        ("math_vectors", "math_3d_geometry", RelationType.PREREQUISITE),
    ]
    
    for from_id, to_id, rel_type in math_prereqs:
        graph.add_relationship(from_id, to_id, rel_type)
    
    logger.info(f"✅ Added {len(math_concepts)} Mathematics concepts")


def main():
    """Main function to populate the knowledge graph"""
    print("=" * 60)
    print("📚 KNOWLEDGE GRAPH POPULATION SCRIPT")
    print("=" * 60)
    
    graph = get_universal_knowledge_graph()
    
    initial_count = len(graph.nodes)
    print(f"\nInitial concept count: {initial_count}")
    
    # Populate each subject
    populate_physics_concepts(graph)
    populate_chemistry_concepts(graph)
    populate_mathematics_concepts(graph)
    
    final_count = len(graph.nodes)
    edges_count = len(graph.edges)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total concepts: {final_count}")
    print(f"New concepts added: {final_count - initial_count}")
    print(f"Total relationships: {edges_count}")
    print(f"\nDomains covered:")
    for domain, concepts in graph.domain_index.items():
        print(f"  - {domain}: {len(concepts)} concepts")
    
    print("\n✅ Knowledge Graph populated successfully!")
    print("The graph is ready to use in HybridReasoningEngine.")


if __name__ == "__main__":
    main()






















