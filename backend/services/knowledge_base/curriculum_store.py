"""
Curriculum Store - Verified Curriculum Content Database
========================================================

Stores and indexes verified curriculum content from:
- NCERT textbooks (Class 9-12)
- JEE Main & Advanced syllabus
- NEET syllabus
- CBSE/State board content

Content is pre-verified and serves as ground truth for RAG.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class CurriculumChunk:
    """A chunk of curriculum content"""
    chunk_id: str
    content: str
    subject: str
    topic: str
    subtopic: str
    class_level: str  # "11", "12", etc.
    source: str  # "NCERT Physics Ch. 5"
    keywords: List[str]
    formulas: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    exam_relevance: Dict[str, int] = field(default_factory=dict)  # {"JEE": 5, "NEET": 3}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "subject": self.subject,
            "topic": self.topic,
            "subtopic": self.subtopic,
            "class_level": self.class_level,
            "source": self.source,
            "keywords": self.keywords,
            "formulas": self.formulas,
            "key_concepts": self.key_concepts,
            "exam_relevance": self.exam_relevance
        }


class CurriculumStore:
    """
    In-Memory Curriculum Content Store
    
    Stores verified curriculum content for RAG retrieval.
    In production, this would be backed by a vector database.
    
    Currently uses keyword-based retrieval for simplicity,
    can be upgraded to embeddings + vector search later.
    """
    
    def __init__(self):
        """Initialize the curriculum store with content"""
        self.chunks: Dict[str, CurriculumChunk] = {}
        self.subject_index: Dict[str, List[str]] = {}  # subject -> chunk_ids
        self.topic_index: Dict[str, List[str]] = {}    # topic -> chunk_ids
        self.keyword_index: Dict[str, List[str]] = {}  # keyword -> chunk_ids
        
        # Load curriculum content
        self._load_curriculum()
        
        logger.info(f"📚 CurriculumStore initialized with {len(self.chunks)} chunks")
    
    def get_chunk(self, chunk_id: str) -> Optional[CurriculumChunk]:
        """Get a specific chunk by ID"""
        return self.chunks.get(chunk_id)
    
    def search_by_keywords(
        self,
        keywords: List[str],
        subject: Optional[str] = None,
        limit: int = 5
    ) -> List[CurriculumChunk]:
        """
        Search chunks by keywords.
        
        Args:
            keywords: List of search keywords
            subject: Optional subject filter
            limit: Maximum results to return
            
        Returns:
            List of matching CurriculumChunks
        """
        chunk_scores: Dict[str, int] = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Direct keyword match
            matching_ids = self.keyword_index.get(keyword_lower, [])
            for chunk_id in matching_ids:
                chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 2
            
            # Partial keyword match
            for indexed_kw, chunk_ids in self.keyword_index.items():
                if keyword_lower in indexed_kw or indexed_kw in keyword_lower:
                    for chunk_id in chunk_ids:
                        chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1
        
        # Filter by subject if specified
        if subject:
            subject_chunks = set(self.subject_index.get(subject.lower(), []))
            chunk_scores = {
                k: v for k, v in chunk_scores.items()
                if k in subject_chunks
            }
        
        # Sort by score and return top results
        sorted_ids = sorted(chunk_scores.keys(), key=lambda x: chunk_scores[x], reverse=True)
        results = [self.chunks[cid] for cid in sorted_ids[:limit] if cid in self.chunks]
        
        return results
    
    def search_by_topic(
        self,
        topic: str,
        subject: Optional[str] = None
    ) -> List[CurriculumChunk]:
        """Search chunks by topic"""
        topic_lower = topic.lower()
        matching_ids = []
        
        for indexed_topic, chunk_ids in self.topic_index.items():
            if topic_lower in indexed_topic or indexed_topic in topic_lower:
                matching_ids.extend(chunk_ids)
        
        results = [self.chunks[cid] for cid in set(matching_ids) if cid in self.chunks]
        
        if subject:
            results = [c for c in results if c.subject.lower() == subject.lower()]
        
        return results
    
    def get_formulas_for_topic(
        self,
        topic: str,
        subject: str
    ) -> List[Dict[str, str]]:
        """Get all formulas related to a topic"""
        chunks = self.search_by_topic(topic, subject)
        formulas = []
        
        for chunk in chunks:
            for formula in chunk.formulas:
                formulas.append({
                    "formula": formula,
                    "topic": chunk.topic,
                    "source": chunk.source
                })
        
        return formulas
    
    def add_chunk(self, chunk: CurriculumChunk) -> None:
        """Add a new chunk to the store"""
        self.chunks[chunk.chunk_id] = chunk
        
        # Update indices
        subject_lower = chunk.subject.lower()
        if subject_lower not in self.subject_index:
            self.subject_index[subject_lower] = []
        self.subject_index[subject_lower].append(chunk.chunk_id)
        
        topic_lower = chunk.topic.lower()
        if topic_lower not in self.topic_index:
            self.topic_index[topic_lower] = []
        self.topic_index[topic_lower].append(chunk.chunk_id)
        
        for keyword in chunk.keywords:
            kw_lower = keyword.lower()
            if kw_lower not in self.keyword_index:
                self.keyword_index[kw_lower] = []
            self.keyword_index[kw_lower].append(chunk.chunk_id)
    
    def _generate_chunk_id(self, content: str, source: str) -> str:
        """Generate unique chunk ID"""
        hash_input = f"{source}:{content[:100]}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _load_curriculum(self) -> None:
        """Load curriculum content into store"""
        # Physics curriculum
        self._load_physics_curriculum()
        
        # Chemistry curriculum
        self._load_chemistry_curriculum()
        
        # Mathematics curriculum
        self._load_mathematics_curriculum()
        
        # Biology curriculum
        self._load_biology_curriculum()
    
    def _load_physics_curriculum(self) -> None:
        """Load Physics curriculum content"""
        physics_content = [
            # Mechanics
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("newton laws", "ncert11-5"),
                content="""Newton's Laws of Motion form the foundation of classical mechanics.
                
First Law (Law of Inertia): A body at rest stays at rest, and a body in motion continues in motion with the same speed and in the same direction unless acted upon by an external force.

Second Law: The rate of change of momentum of a body is directly proportional to the applied force and takes place in the direction in which the force acts. Mathematically, F = ma, where F is force, m is mass, and a is acceleration.

Third Law: For every action, there is an equal and opposite reaction. When one body exerts a force on another body, the second body simultaneously exerts a force equal in magnitude and opposite in direction on the first body.""",
                subject="Physics",
                topic="Newton's Laws of Motion",
                subtopic="Laws of Motion",
                class_level="11",
                source="NCERT Class 11 Physics Ch. 5",
                keywords=["newton", "laws", "motion", "force", "inertia", "momentum", "action", "reaction", "F=ma"],
                formulas=["F = ma", "p = mv", "F = dp/dt"],
                key_concepts=["inertia", "momentum", "force", "acceleration"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("work energy", "ncert11-6"),
                content="""Work, Energy and Power are fundamental concepts in mechanics.

Work: Work done by a force is defined as the product of the force and the displacement in the direction of the force. W = F·d·cos(θ), where θ is the angle between force and displacement.

Kinetic Energy: Energy possessed by a body due to its motion. KE = ½mv², where m is mass and v is velocity.

Potential Energy: Energy stored in a body due to its position or configuration. Gravitational PE = mgh, where h is height above reference.

Power: Rate of doing work. P = W/t = F·v

Work-Energy Theorem: Net work done on a body equals the change in its kinetic energy.""",
                subject="Physics",
                topic="Work, Energy and Power",
                subtopic="Energy",
                class_level="11",
                source="NCERT Class 11 Physics Ch. 6",
                keywords=["work", "energy", "power", "kinetic", "potential", "conservation", "joule"],
                formulas=["W = Fd cos θ", "KE = ½mv²", "PE = mgh", "P = W/t", "P = Fv"],
                key_concepts=["work-energy theorem", "conservation of energy", "power"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            # Electrostatics
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("coulomb law", "ncert12-1"),
                content="""Coulomb's Law describes the force between electric charges.

Coulomb's Law: The force between two point charges is directly proportional to the product of their magnitudes and inversely proportional to the square of the distance between them.

F = k(q₁q₂)/r²

where:
- k = 9 × 10⁹ N·m²/C² (Coulomb's constant)
- q₁, q₂ are the charges
- r is the distance between charges

Electric Field: E = F/q = kQ/r²
Electric Potential: V = kQ/r

The force is attractive for unlike charges and repulsive for like charges.""",
                subject="Physics",
                topic="Electrostatics",
                subtopic="Coulomb's Law",
                class_level="12",
                source="NCERT Class 12 Physics Ch. 1",
                keywords=["coulomb", "charge", "electric", "force", "field", "potential", "electrostatic"],
                formulas=["F = kq₁q₂/r²", "E = kQ/r²", "V = kQ/r", "k = 9×10⁹ N·m²/C²"],
                key_concepts=["electric charge", "electric field", "electric potential", "superposition"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            # Modern Physics
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("photoelectric effect", "ncert12-11"),
                content="""Photoelectric Effect is the emission of electrons from a metal surface when light of sufficient frequency falls on it.

Einstein's Photoelectric Equation:
hν = φ + ½mv²max

where:
- h = Planck's constant (6.626 × 10⁻³⁴ J·s)
- ν = frequency of incident light
- φ = work function (minimum energy to eject electron)
- ½mv²max = maximum kinetic energy of emitted electrons

Key observations:
1. Threshold frequency: Below this, no emission occurs regardless of intensity
2. Instantaneous emission: No time delay
3. Maximum KE depends on frequency, not intensity
4. Number of electrons depends on intensity""",
                subject="Physics",
                topic="Photoelectric Effect",
                subtopic="Dual Nature of Matter",
                class_level="12",
                source="NCERT Class 12 Physics Ch. 11",
                keywords=["photoelectric", "photon", "planck", "einstein", "threshold", "work function", "electron"],
                formulas=["E = hν", "hν = φ + KEmax", "λ = h/p", "h = 6.626×10⁻³⁴ J·s"],
                key_concepts=["quantization", "photon", "wave-particle duality", "threshold frequency"],
                exam_relevance={"JEE": 5, "NEET": 5}
            ),
        ]
        
        for chunk in physics_content:
            self.add_chunk(chunk)
    
    def _load_chemistry_curriculum(self) -> None:
        """Load Chemistry curriculum content"""
        chemistry_content = [
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("mole concept", "ncert11-1"),
                content="""The Mole Concept is fundamental to quantitative chemistry.

Mole: One mole contains exactly 6.022 × 10²³ entities (atoms, molecules, ions). This number is Avogadro's number (NA).

Key Relationships:
- Number of moles (n) = Given mass / Molar mass = N / NA
- Molar mass = Mass of 1 mole of substance (g/mol)
- At STP, 1 mole of any gas occupies 22.4 L

For compounds:
- Molecular formula gives actual ratio of atoms
- Empirical formula gives simplest whole number ratio
- Molecular formula = n × Empirical formula""",
                subject="Chemistry",
                topic="Mole Concept",
                subtopic="Basic Concepts",
                class_level="11",
                source="NCERT Class 11 Chemistry Ch. 1",
                keywords=["mole", "avogadro", "molecular mass", "molar mass", "stoichiometry"],
                formulas=["n = m/M", "n = N/NA", "NA = 6.022×10²³", "V = 22.4 L at STP"],
                key_concepts=["mole", "Avogadro's number", "molar mass", "stoichiometry"],
                exam_relevance={"JEE": 5, "NEET": 5}
            ),
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("chemical equilibrium", "ncert11-7"),
                content="""Chemical Equilibrium is a dynamic state where forward and reverse reaction rates are equal.

Law of Mass Action:
For reaction aA + bB ⇌ cC + dD
Equilibrium constant Kc = [C]^c[D]^d / [A]^a[B]^b

Le Chatelier's Principle:
When a system at equilibrium is disturbed, it shifts to minimize the disturbance.

Factors affecting equilibrium:
1. Concentration: Adding reactant shifts equilibrium forward
2. Pressure: Increasing pressure favors side with fewer moles of gas
3. Temperature: Increasing T favors endothermic direction
4. Catalyst: Does NOT shift equilibrium, only speeds up attainment""",
                subject="Chemistry",
                topic="Chemical Equilibrium",
                subtopic="Equilibrium",
                class_level="11",
                source="NCERT Class 11 Chemistry Ch. 7",
                keywords=["equilibrium", "le chatelier", "Kc", "Kp", "reversible", "dynamic"],
                formulas=["Kc = [products]/[reactants]", "Kp = Kc(RT)^Δn", "ΔG = -RT ln K"],
                key_concepts=["dynamic equilibrium", "Le Chatelier's principle", "equilibrium constant"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("ionic equilibrium", "ncert11-7b"),
                content="""Ionic Equilibrium deals with equilibria involving ions in solution.

pH Scale:
- pH = -log[H⁺]
- pOH = -log[OH⁻]
- pH + pOH = 14 (at 25°C)
- Neutral solution: pH = 7

Acids and Bases:
- Strong acids/bases: Complete dissociation
- Weak acids/bases: Partial dissociation, Ka/Kb applies

Buffer Solutions:
- Resist change in pH when small amounts of acid/base added
- Henderson-Hasselbalch: pH = pKa + log([A⁻]/[HA])""",
                subject="Chemistry",
                topic="Ionic Equilibrium",
                subtopic="Acids and Bases",
                class_level="11",
                source="NCERT Class 11 Chemistry Ch. 7",
                keywords=["pH", "pOH", "acid", "base", "buffer", "Henderson", "Ka", "Kb", "ionic"],
                formulas=["pH = -log[H⁺]", "pH + pOH = 14", "pH = pKa + log([A⁻]/[HA])"],
                key_concepts=["pH scale", "buffer solutions", "acid-base equilibrium"],
                exam_relevance={"JEE": 5, "NEET": 5}
            ),
        ]
        
        for chunk in chemistry_content:
            self.add_chunk(chunk)
    
    def _load_mathematics_curriculum(self) -> None:
        """Load Mathematics curriculum content"""
        math_content = [
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("permutations combinations", "ncert11-7"),
                content="""Permutations and Combinations are fundamental counting principles.

Permutation (nPr): Arrangement of objects where ORDER MATTERS.
nPr = n!/(n-r)!

Examples of permutations:
- Arranging books on a shelf
- Forming a queue
- Assigning positions in a race

Combination (nCr): Selection of objects where ORDER DOES NOT MATTER.
nCr = n!/[r!(n-r)!]

Examples of combinations:
- Choosing a committee
- Selecting cards from a deck
- Picking team members

Key relationship: nPr = nCr × r!

Special cases:
- nC0 = nCn = 1
- nC1 = n
- nCr = nC(n-r)""",
                subject="Mathematics",
                topic="Permutations and Combinations",
                subtopic="Counting Principles",
                class_level="11",
                source="NCERT Class 11 Mathematics Ch. 7",
                keywords=["permutation", "combination", "nPr", "nCr", "factorial", "arrangement", "selection", "counting"],
                formulas=["nPr = n!/(n-r)!", "nCr = n!/[r!(n-r)!]", "nPr = nCr × r!"],
                key_concepts=["permutation", "combination", "factorial", "fundamental counting principle"],
                exam_relevance={"JEE": 5, "NEET": 3}
            ),
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("calculus derivatives", "ncert12-5"),
                content="""Derivatives measure the rate of change of a function.

Definition: f'(x) = lim[h→0] [f(x+h) - f(x)]/h

Standard Derivatives:
- d/dx(xⁿ) = nxⁿ⁻¹
- d/dx(eˣ) = eˣ
- d/dx(ln x) = 1/x
- d/dx(sin x) = cos x
- d/dx(cos x) = -sin x
- d/dx(tan x) = sec²x

Rules:
1. Sum Rule: (f + g)' = f' + g'
2. Product Rule: (fg)' = f'g + fg'
3. Quotient Rule: (f/g)' = (f'g - fg')/g²
4. Chain Rule: d/dx[f(g(x))] = f'(g(x)) · g'(x)

Applications: Finding maxima/minima, rate of change, tangent/normal lines.""",
                subject="Mathematics",
                topic="Derivatives",
                subtopic="Calculus",
                class_level="12",
                source="NCERT Class 12 Mathematics Ch. 5",
                keywords=["derivative", "differentiation", "calculus", "rate of change", "chain rule", "product rule"],
                formulas=["d/dx(xⁿ) = nxⁿ⁻¹", "d/dx(eˣ) = eˣ", "d/dx(sin x) = cos x", "(fg)' = f'g + fg'"],
                key_concepts=["derivative", "chain rule", "product rule", "maxima and minima"],
                exam_relevance={"JEE": 5, "NEET": 3}
            ),
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("calculus integration", "ncert12-7"),
                content="""Integration is the reverse process of differentiation.

Indefinite Integral: ∫f(x)dx = F(x) + C, where F'(x) = f(x)

Standard Integrals:
- ∫xⁿ dx = xⁿ⁺¹/(n+1) + C (n ≠ -1)
- ∫1/x dx = ln|x| + C
- ∫eˣ dx = eˣ + C
- ∫sin x dx = -cos x + C
- ∫cos x dx = sin x + C

Integration Techniques:
1. Substitution: Use when integrand contains composite function
2. By Parts: ∫u dv = uv - ∫v du (ILATE rule for choosing u)
3. Partial Fractions: For rational functions

Definite Integral: ∫[a to b] f(x)dx = F(b) - F(a)
Represents area under curve from a to b.""",
                subject="Mathematics",
                topic="Integration",
                subtopic="Calculus",
                class_level="12",
                source="NCERT Class 12 Mathematics Ch. 7",
                keywords=["integration", "integral", "antiderivative", "by parts", "substitution", "definite", "area"],
                formulas=["∫xⁿ dx = xⁿ⁺¹/(n+1) + C", "∫eˣ dx = eˣ + C", "∫u dv = uv - ∫v du"],
                key_concepts=["integration by parts", "substitution", "definite integral", "area under curve"],
                exam_relevance={"JEE": 5, "NEET": 2}
            ),
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("quadratic equations", "ncert10-4"),
                content="""Quadratic Equations are polynomials of degree 2.

Standard form: ax² + bx + c = 0, where a ≠ 0

Quadratic Formula:
x = (-b ± √(b² - 4ac)) / 2a

Discriminant D = b² - 4ac:
- D > 0: Two distinct real roots
- D = 0: Two equal real roots (one repeated root)
- D < 0: No real roots (two complex conjugate roots)

Sum of roots: α + β = -b/a
Product of roots: αβ = c/a

Nature of roots also depends on sign of a:
- If a > 0: Parabola opens upward
- If a < 0: Parabola opens downward""",
                subject="Mathematics",
                topic="Quadratic Equations",
                subtopic="Algebra",
                class_level="10",
                source="NCERT Class 10 Mathematics Ch. 4",
                keywords=["quadratic", "roots", "discriminant", "formula", "parabola", "polynomial"],
                formulas=["x = (-b ± √(b²-4ac))/2a", "D = b² - 4ac", "α + β = -b/a", "αβ = c/a"],
                key_concepts=["discriminant", "nature of roots", "sum and product of roots"],
                exam_relevance={"JEE": 4, "NEET": 2}
            ),
        ]
        
        for chunk in math_content:
            self.add_chunk(chunk)
    
    def _load_biology_curriculum(self) -> None:
        """Load Biology curriculum content"""
        biology_content = [
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("cell structure", "ncert11-8"),
                content="""The Cell is the basic structural and functional unit of life.

Cell Theory:
1. All living organisms are made of cells
2. Cell is the basic unit of life
3. All cells arise from pre-existing cells

Cell Types:
1. Prokaryotic: No true nucleus, no membrane-bound organelles (bacteria)
2. Eukaryotic: True nucleus, membrane-bound organelles (plants, animals, fungi)

Key Organelles:
- Nucleus: Contains DNA, controls cell activities
- Mitochondria: Powerhouse, ATP production (cellular respiration)
- Chloroplast: Photosynthesis (plants only)
- Endoplasmic Reticulum: Protein synthesis (rough), lipid synthesis (smooth)
- Golgi Apparatus: Packaging and secretion
- Lysosomes: Digestion, "suicide bags"
- Ribosomes: Protein synthesis""",
                subject="Biology",
                topic="Cell Structure",
                subtopic="Cell Biology",
                class_level="11",
                source="NCERT Class 11 Biology Ch. 8",
                keywords=["cell", "nucleus", "mitochondria", "organelle", "prokaryotic", "eukaryotic", "membrane"],
                formulas=[],
                key_concepts=["cell theory", "prokaryotes vs eukaryotes", "cell organelles"],
                exam_relevance={"JEE": 2, "NEET": 5}
            ),
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("photosynthesis", "ncert11-13"),
                content="""Photosynthesis is the process by which plants convert light energy to chemical energy.

Overall Equation:
6CO₂ + 6H₂O + Light Energy → C₆H₁₂O₆ + 6O₂

Two Stages:
1. Light Reactions (in thylakoids):
   - Photolysis of water
   - ATP and NADPH production
   - O₂ released

2. Dark Reactions/Calvin Cycle (in stroma):
   - CO₂ fixation by RuBisCO
   - Uses ATP and NADPH
   - Produces glucose

Factors affecting photosynthesis:
- Light intensity
- CO₂ concentration
- Temperature
- Water availability

C3 vs C4 Plants:
- C3: First product is 3-carbon compound (3-PGA)
- C4: First product is 4-carbon compound (OAA), Kranz anatomy""",
                subject="Biology",
                topic="Photosynthesis",
                subtopic="Plant Physiology",
                class_level="11",
                source="NCERT Class 11 Biology Ch. 13",
                keywords=["photosynthesis", "chlorophyll", "calvin cycle", "light reaction", "CO2", "glucose", "ATP"],
                formulas=["6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂"],
                key_concepts=["light reactions", "Calvin cycle", "C3 and C4 plants", "factors affecting photosynthesis"],
                exam_relevance={"JEE": 1, "NEET": 5}
            ),
            CurriculumChunk(
                chunk_id=self._generate_chunk_id("human circulation", "ncert11-18"),
                content="""The Human Circulatory System transports blood throughout the body.

Heart Structure:
- 4 chambers: 2 atria (upper), 2 ventricles (lower)
- Right side: Deoxygenated blood
- Left side: Oxygenated blood
- Septum separates left and right sides

Blood Circulation:
1. Pulmonary Circulation: Heart → Lungs → Heart
   Right ventricle → Pulmonary artery → Lungs → Pulmonary vein → Left atrium

2. Systemic Circulation: Heart → Body → Heart
   Left ventricle → Aorta → Body → Vena cava → Right atrium

Cardiac Cycle:
- Systole: Contraction phase (blood pumped out)
- Diastole: Relaxation phase (chambers fill)
- Heart rate: ~72 beats/min
- Cardiac output = Stroke volume × Heart rate

ECG (Electrocardiogram):
- P wave: Atrial depolarization
- QRS complex: Ventricular depolarization
- T wave: Ventricular repolarization""",
                subject="Biology",
                topic="Human Circulation",
                subtopic="Body Fluids and Circulation",
                class_level="11",
                source="NCERT Class 11 Biology Ch. 18",
                keywords=["heart", "circulation", "blood", "atrium", "ventricle", "cardiac", "ECG", "systole", "diastole"],
                formulas=["Cardiac Output = Stroke Volume × Heart Rate"],
                key_concepts=["double circulation", "cardiac cycle", "ECG", "heart chambers"],
                exam_relevance={"JEE": 1, "NEET": 5}
            ),
        ]
        
        for chunk in biology_content:
            self.add_chunk(chunk)


# Singleton instance
_store_instance: Optional[CurriculumStore] = None


def get_curriculum_store() -> CurriculumStore:
    """Get or create the global curriculum store instance"""
    global _store_instance
    if _store_instance is None:
        _store_instance = CurriculumStore()
    return _store_instance

