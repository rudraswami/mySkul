"""
📚 Corpus Ingestion - Offline Content Pipeline
===============================================

Implements offline ingestion of educational content:
1. SourceRegistry: Defines controlled sources (NCERT PDFs, formulas, exam data)
2. IngestionJob: Downloads/processes content with metadata
3. ChunkProcessor: Text extraction, cleaning, chunking with hierarchy

IMPORTANT: Internet access is ONLY allowed in offline ingestion jobs.
Runtime tools query the local indexed corpus.

Content Types:
- NCERT textbooks (PDF/HTML)
- Formula databases (structured JSON)
- Exam strategy data (structured JSON)
- Previous year questions (structured JSON)
"""

import logging
import json
import hashlib
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


# =============================================================================
# DATA DIRECTORY - Store all ingested content here
# =============================================================================
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "corpus"
FORMULAS_FILE = DATA_DIR / "formulas.json"
EXAM_STRATEGY_FILE = DATA_DIR / "exam_strategy.json"
CURRICULUM_FILE = DATA_DIR / "curriculum_chunks.json"
SOURCES_FILE = DATA_DIR / "sources_registry.json"
INGESTION_LOG_FILE = DATA_DIR / "ingestion_log.json"


class SourceType(Enum):
    """Types of content sources"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    STRUCTURED = "structured"


class ContentDomain(Enum):
    """Educational content domains"""
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    MATHEMATICS = "mathematics"
    BIOLOGY = "biology"
    GENERAL = "general"


@dataclass
class ContentSource:
    """
    Definition of a controlled content source.
    
    All content must be from registered sources with proper attribution.
    """
    source_id: str
    name: str
    source_type: SourceType
    domain: ContentDomain
    urls: List[str]  # URLs/paths to fetch from (offline job)
    attribution: str  # License/attribution notes
    version: str = "1.0"
    last_updated: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "name": self.name,
            "source_type": self.source_type.value,
            "domain": self.domain.value,
            "urls": self.urls,
            "attribution": self.attribution,
            "version": self.version,
            "last_updated": self.last_updated,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ContentSource':
        return cls(
            source_id=data["source_id"],
            name=data["name"],
            source_type=SourceType(data["source_type"]),
            domain=ContentDomain(data["domain"]),
            urls=data.get("urls", []),
            attribution=data.get("attribution", ""),
            version=data.get("version", "1.0"),
            last_updated=data.get("last_updated", ""),
            metadata=data.get("metadata", {})
        )


@dataclass
class Formula:
    """
    Structured formula entry with full metadata.
    
    This replaces the hardcoded FORMULAS dict with a queryable structure.
    """
    formula_id: str
    name: str
    formula: str
    subject: str
    topic: str
    variables: str
    units: str = ""
    constraints: str = ""
    common_mistakes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    source_id: str = ""
    exam_relevance: Dict[str, int] = field(default_factory=dict)  # {"JEE": 5, "NEET": 3}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Formula':
        return cls(**data)


@dataclass
class ExamTopicStrategy:
    """
    Exam strategy data for a specific topic.
    
    This replaces the hardcoded EXAM_STRATEGY_DATA.
    """
    strategy_id: str
    exam_type: str  # JEE, NEET, CBSE
    topic: str
    subject: str
    weightage_percent: float
    common_traps: List[str]
    shortcut_technique: str
    ncert_relevance: str
    pyq_pattern: str
    source_id: str = ""
    syllabus_reference: str = ""
    recommended_time_percent: float = 0.0
    difficulty_rating: int = 3  # 1-5
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExamTopicStrategy':
        return cls(**data)


# =============================================================================
# SOURCE REGISTRY
# =============================================================================

class SourceRegistry:
    """
    Central registry of all controlled content sources.
    
    All content must be from registered sources.
    Sources must have proper attribution and license notes.
    """
    
    # Default sources (can be extended)
    DEFAULT_SOURCES = [
        ContentSource(
            source_id="ncert_physics_11",
            name="NCERT Physics Class 11",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.PHYSICS,
            urls=["local://curriculum/ncert_physics_11.json"],
            attribution="NCERT, Govt. of India. Educational use only.",
            version="2023-24"
        ),
        ContentSource(
            source_id="ncert_physics_12",
            name="NCERT Physics Class 12",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.PHYSICS,
            urls=["local://curriculum/ncert_physics_12.json"],
            attribution="NCERT, Govt. of India. Educational use only.",
            version="2023-24"
        ),
        ContentSource(
            source_id="ncert_chemistry_11",
            name="NCERT Chemistry Class 11",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.CHEMISTRY,
            urls=["local://curriculum/ncert_chemistry_11.json"],
            attribution="NCERT, Govt. of India. Educational use only.",
            version="2023-24"
        ),
        ContentSource(
            source_id="ncert_chemistry_12",
            name="NCERT Chemistry Class 12",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.CHEMISTRY,
            urls=["local://curriculum/ncert_chemistry_12.json"],
            attribution="NCERT, Govt. of India. Educational use only.",
            version="2023-24"
        ),
        ContentSource(
            source_id="ncert_math_11",
            name="NCERT Mathematics Class 11",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.MATHEMATICS,
            urls=["local://curriculum/ncert_math_11.json"],
            attribution="NCERT, Govt. of India. Educational use only.",
            version="2023-24"
        ),
        ContentSource(
            source_id="ncert_math_12",
            name="NCERT Mathematics Class 12",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.MATHEMATICS,
            urls=["local://curriculum/ncert_math_12.json"],
            attribution="NCERT, Govt. of India. Educational use only.",
            version="2023-24"
        ),
        ContentSource(
            source_id="ncert_biology_11",
            name="NCERT Biology Class 11",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.BIOLOGY,
            urls=["local://curriculum/ncert_biology_11.json"],
            attribution="NCERT, Govt. of India. Educational use only.",
            version="2023-24"
        ),
        ContentSource(
            source_id="ncert_biology_12",
            name="NCERT Biology Class 12",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.BIOLOGY,
            urls=["local://curriculum/ncert_biology_12.json"],
            attribution="NCERT, Govt. of India. Educational use only.",
            version="2023-24"
        ),
        ContentSource(
            source_id="jee_syllabus",
            name="JEE Main & Advanced Syllabus",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.GENERAL,
            urls=["local://exam/jee_syllabus.json"],
            attribution="NTA, Govt. of India. Public syllabus document.",
            version="2024"
        ),
        ContentSource(
            source_id="neet_syllabus",
            name="NEET Syllabus",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.GENERAL,
            urls=["local://exam/neet_syllabus.json"],
            attribution="NTA, Govt. of India. Public syllabus document.",
            version="2024"
        ),
        ContentSource(
            source_id="formula_bank",
            name="Educational Formula Bank",
            source_type=SourceType.STRUCTURED,
            domain=ContentDomain.GENERAL,
            urls=["local://formulas/formula_bank.json"],
            attribution="Compiled from NCERT and standard textbooks. Educational use.",
            version="1.0"
        ),
    ]
    
    def __init__(self):
        self.sources: Dict[str, ContentSource] = {}
        self._load_sources()
    
    def _load_sources(self):
        """Load sources from file or use defaults"""
        if SOURCES_FILE.exists():
            try:
                with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for source_data in data.get("sources", []):
                        source = ContentSource.from_dict(source_data)
                        self.sources[source.source_id] = source
                logger.info(f"📚 Loaded {len(self.sources)} sources from registry")
            except Exception as e:
                logger.warning(f"Failed to load sources file: {e}, using defaults")
                self._init_default_sources()
        else:
            self._init_default_sources()
    
    def _init_default_sources(self):
        """Initialize with default sources"""
        for source in self.DEFAULT_SOURCES:
            self.sources[source.source_id] = source
        self.save()
        logger.info(f"📚 Initialized {len(self.sources)} default sources")
    
    def save(self):
        """Persist sources to file"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(SOURCES_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "sources": [s.to_dict() for s in self.sources.values()],
                "updated_at": datetime.utcnow().isoformat()
            }, f, indent=2)
    
    def get_source(self, source_id: str) -> Optional[ContentSource]:
        return self.sources.get(source_id)
    
    def add_source(self, source: ContentSource):
        self.sources[source.source_id] = source
        self.save()
    
    def list_sources(self) -> List[ContentSource]:
        return list(self.sources.values())


# =============================================================================
# FORMULA BANK (Structured, replaces hardcoded FORMULAS dict)
# =============================================================================

class FormulaBank:
    """
    Structured formula database with search capabilities.
    
    Replaces the hardcoded FORMULAS dict in formula_lookup.py
    """
    
    def __init__(self):
        self.formulas: Dict[str, Formula] = {}
        self._subject_index: Dict[str, List[str]] = {}
        self._topic_index: Dict[str, List[str]] = {}
        self._tag_index: Dict[str, List[str]] = {}
        self._load_formulas()
    
    def _load_formulas(self):
        """Load formulas from file or initialize defaults"""
        if FORMULAS_FILE.exists():
            try:
                with open(FORMULAS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for formula_data in data.get("formulas", []):
                        formula = Formula.from_dict(formula_data)
                        self._add_formula_to_index(formula)
                logger.info(f"📐 Loaded {len(self.formulas)} formulas from bank")
            except Exception as e:
                logger.warning(f"Failed to load formulas file: {e}, initializing defaults")
                self._init_default_formulas()
        else:
            self._init_default_formulas()
    
    def _init_default_formulas(self):
        """Initialize with comprehensive formula set"""
        default_formulas = self._get_default_formulas()
        for formula in default_formulas:
            self._add_formula_to_index(formula)
        self.save()
        logger.info(f"📐 Initialized {len(self.formulas)} default formulas")
    
    def _add_formula_to_index(self, formula: Formula):
        """Add formula to all indices"""
        self.formulas[formula.formula_id] = formula
        
        # Subject index
        subj = formula.subject.lower()
        if subj not in self._subject_index:
            self._subject_index[subj] = []
        self._subject_index[subj].append(formula.formula_id)
        
        # Topic index
        topic = formula.topic.lower()
        if topic not in self._topic_index:
            self._topic_index[topic] = []
        self._topic_index[topic].append(formula.formula_id)
        
        # Tag index
        for tag in formula.tags:
            tag_lower = tag.lower()
            if tag_lower not in self._tag_index:
                self._tag_index[tag_lower] = []
            self._tag_index[tag_lower].append(formula.formula_id)
    
    def save(self):
        """Persist formulas to file"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(FORMULAS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "formulas": [f.to_dict() for f in self.formulas.values()],
                "count": len(self.formulas),
                "updated_at": datetime.utcnow().isoformat()
            }, f, indent=2)
    
    def search(
        self,
        query: str,
        subject: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[Formula, float]]:
        """
        Search formulas with relevance scoring.
        
        Returns list of (Formula, score) tuples.
        """
        query_lower = query.lower()
        scores: Dict[str, float] = {}
        
        # Search by topic
        for topic, formula_ids in self._topic_index.items():
            if query_lower in topic or topic in query_lower:
                for fid in formula_ids:
                    scores[fid] = scores.get(fid, 0) + 2.0
        
        # Search by tags
        for tag, formula_ids in self._tag_index.items():
            if query_lower in tag or tag in query_lower:
                for fid in formula_ids:
                    scores[fid] = scores.get(fid, 0) + 1.5
        
        # Search by formula name
        for fid, formula in self.formulas.items():
            if query_lower in formula.name.lower():
                scores[fid] = scores.get(fid, 0) + 2.5
            # Search in variables
            if query_lower in formula.variables.lower():
                scores[fid] = scores.get(fid, 0) + 0.5
        
        # Filter by subject if specified
        if subject:
            subject_lower = subject.lower()
            subject_formulas = set(self._subject_index.get(subject_lower, []))
            scores = {k: v for k, v in scores.items() if k in subject_formulas}
        
        # Sort by score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        results = [(self.formulas[fid], scores[fid]) for fid in sorted_ids[:limit]]
        
        return results
    
    def get_by_topic(self, topic: str, subject: Optional[str] = None) -> List[Formula]:
        """Get all formulas for a topic"""
        topic_lower = topic.lower()
        matching_ids = []
        
        for indexed_topic, formula_ids in self._topic_index.items():
            if topic_lower in indexed_topic or indexed_topic in topic_lower:
                matching_ids.extend(formula_ids)
        
        results = [self.formulas[fid] for fid in set(matching_ids)]
        
        if subject:
            results = [f for f in results if f.subject.lower() == subject.lower()]
        
        return results
    
    def _get_default_formulas(self) -> List[Formula]:
        """Generate comprehensive default formula set"""
        formulas = []
        
        # Physics - Mechanics
        mechanics_formulas = [
            Formula(
                formula_id="phys_mech_001",
                name="Newton's Second Law",
                formula="F = ma",
                subject="Physics",
                topic="Mechanics",
                variables="F: force (N), m: mass (kg), a: acceleration (m/s²)",
                units="SI: Newton (N) = kg·m/s²",
                constraints="Valid for constant mass systems",
                common_mistakes=["Forgetting to use vector form", "Mixing up mass and weight"],
                tags=["newton", "force", "motion", "dynamics"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mech_002",
                name="Kinematic Equation (velocity-time)",
                formula="v = u + at",
                subject="Physics",
                topic="Mechanics",
                variables="v: final velocity, u: initial velocity, a: acceleration, t: time",
                units="SI: m/s",
                constraints="Valid for constant acceleration only",
                common_mistakes=["Using for non-uniform acceleration", "Sign errors with direction"],
                tags=["kinematics", "velocity", "motion", "SUVAT"],
                exam_relevance={"JEE": 4, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mech_003",
                name="Kinematic Equation (displacement-time)",
                formula="s = ut + ½at²",
                subject="Physics",
                topic="Mechanics",
                variables="s: displacement, u: initial velocity, a: acceleration, t: time",
                units="SI: meters (m)",
                constraints="Valid for constant acceleration only",
                common_mistakes=["Confusing displacement with distance", "Forgetting ½ factor"],
                tags=["kinematics", "displacement", "motion", "SUVAT"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mech_004",
                name="Kinematic Equation (velocity-displacement)",
                formula="v² = u² + 2as",
                subject="Physics",
                topic="Mechanics",
                variables="v: final velocity, u: initial velocity, a: acceleration, s: displacement",
                units="SI: m²/s²",
                constraints="Valid for constant acceleration only",
                common_mistakes=["Forgetting to square velocities", "Sign errors"],
                tags=["kinematics", "velocity", "displacement", "SUVAT"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mech_005",
                name="Kinetic Energy",
                formula="KE = ½mv²",
                subject="Physics",
                topic="Mechanics",
                variables="KE: kinetic energy (J), m: mass (kg), v: velocity (m/s)",
                units="SI: Joule (J) = kg·m²/s²",
                constraints="v must be measured relative to reference frame",
                common_mistakes=["Forgetting ½ factor", "Using speed instead of velocity magnitude"],
                tags=["energy", "kinetic", "motion", "work-energy"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mech_006",
                name="Gravitational Potential Energy",
                formula="PE = mgh",
                subject="Physics",
                topic="Mechanics",
                variables="PE: potential energy (J), m: mass (kg), g: gravity (9.8 m/s²), h: height (m)",
                units="SI: Joule (J)",
                constraints="Valid near Earth's surface where g is constant",
                common_mistakes=["Wrong reference height", "Using varying g for large heights"],
                tags=["energy", "potential", "gravity", "work-energy"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mech_007",
                name="Work Done",
                formula="W = Fd cos θ",
                subject="Physics",
                topic="Mechanics",
                variables="W: work (J), F: force (N), d: displacement (m), θ: angle between F and d",
                units="SI: Joule (J)",
                constraints="θ must be angle between force and displacement vectors",
                common_mistakes=["Forgetting cos θ", "Using distance instead of displacement"],
                tags=["work", "force", "energy"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mech_008",
                name="Power",
                formula="P = W/t = Fv",
                subject="Physics",
                topic="Mechanics",
                variables="P: power (W), W: work (J), t: time (s), F: force (N), v: velocity (m/s)",
                units="SI: Watt (W) = J/s",
                constraints="Fv form valid when F and v are parallel",
                common_mistakes=["Confusing average and instantaneous power"],
                tags=["power", "energy", "work"],
                exam_relevance={"JEE": 4, "NEET": 3}
            ),
            Formula(
                formula_id="phys_mech_009",
                name="Momentum",
                formula="p = mv",
                subject="Physics",
                topic="Mechanics",
                variables="p: momentum (kg·m/s), m: mass (kg), v: velocity (m/s)",
                units="SI: kg·m/s",
                constraints="Vector quantity - direction matters",
                common_mistakes=["Treating as scalar", "Confusing with impulse"],
                tags=["momentum", "motion", "collision"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mech_010",
                name="Friction Force",
                formula="f = μN",
                subject="Physics",
                topic="Mechanics",
                variables="f: friction force (N), μ: coefficient of friction, N: normal force (N)",
                units="SI: Newton (N)",
                constraints="μs for static (max), μk for kinetic friction",
                common_mistakes=["Using wrong μ value", "Forgetting N depends on orientation"],
                tags=["friction", "force", "contact"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
        ]
        formulas.extend(mechanics_formulas)
        
        # Physics - Electricity
        electricity_formulas = [
            Formula(
                formula_id="phys_elec_001",
                name="Coulomb's Law",
                formula="F = kq₁q₂/r²",
                subject="Physics",
                topic="Electrostatics",
                variables="F: force (N), k: 9×10⁹ N·m²/C², q: charges (C), r: distance (m)",
                units="SI: Newton (N)",
                constraints="Point charges, medium is vacuum/air",
                common_mistakes=["Forgetting inverse square", "Wrong sign for unlike charges"],
                tags=["coulomb", "charge", "electric", "force", "electrostatic"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_elec_002",
                name="Ohm's Law",
                formula="V = IR",
                subject="Physics",
                topic="Current Electricity",
                variables="V: voltage (V), I: current (A), R: resistance (Ω)",
                units="SI: Volt, Ampere, Ohm",
                constraints="Valid for ohmic conductors at constant temperature",
                common_mistakes=["Applying to non-ohmic materials", "Temperature dependence of R"],
                tags=["ohm", "voltage", "current", "resistance", "circuit"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_elec_003",
                name="Electric Field (point charge)",
                formula="E = kQ/r²",
                subject="Physics",
                topic="Electrostatics",
                variables="E: electric field (N/C), k: 9×10⁹, Q: source charge (C), r: distance (m)",
                units="SI: N/C or V/m",
                constraints="Point charge in vacuum",
                common_mistakes=["Confusing with force formula", "Direction errors"],
                tags=["electric", "field", "charge", "electrostatic"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="phys_elec_004",
                name="Electrical Power",
                formula="P = VI = I²R = V²/R",
                subject="Physics",
                topic="Current Electricity",
                variables="P: power (W), V: voltage (V), I: current (A), R: resistance (Ω)",
                units="SI: Watt (W)",
                constraints="All forms equivalent for DC circuits",
                common_mistakes=["Using wrong form for given data", "AC vs DC"],
                tags=["power", "electrical", "circuit", "energy"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
        ]
        formulas.extend(electricity_formulas)
        
        # Physics - Modern Physics
        modern_formulas = [
            Formula(
                formula_id="phys_mod_001",
                name="Einstein's Mass-Energy",
                formula="E = mc²",
                subject="Physics",
                topic="Modern Physics",
                variables="E: energy (J), m: mass (kg), c: speed of light (3×10⁸ m/s)",
                units="SI: Joule (J)",
                constraints="Mass-energy equivalence",
                common_mistakes=["Confusing rest mass with relativistic mass"],
                tags=["einstein", "relativity", "energy", "mass"],
                exam_relevance={"JEE": 4, "NEET": 4}
            ),
            Formula(
                formula_id="phys_mod_002",
                name="Photoelectric Effect",
                formula="hν = φ + KEmax",
                subject="Physics",
                topic="Modern Physics",
                variables="h: Planck constant (6.626×10⁻³⁴ J·s), ν: frequency (Hz), φ: work function (J), KE: kinetic energy (J)",
                units="SI: Joule (J)",
                constraints="ν must exceed threshold frequency",
                common_mistakes=["Confusing threshold and incident frequency", "Sign errors"],
                tags=["photoelectric", "photon", "planck", "einstein", "quantum"],
                exam_relevance={"JEE": 5, "NEET": 5}
            ),
            Formula(
                formula_id="phys_mod_003",
                name="de Broglie Wavelength",
                formula="λ = h/p = h/mv",
                subject="Physics",
                topic="Modern Physics",
                variables="λ: wavelength (m), h: Planck constant, p: momentum (kg·m/s), m: mass (kg), v: velocity (m/s)",
                units="SI: meters (m)",
                constraints="Wave-particle duality",
                common_mistakes=["Using relativistic momentum for high speeds"],
                tags=["de broglie", "wavelength", "matter wave", "quantum"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
        ]
        formulas.extend(modern_formulas)
        
        # Chemistry Formulas
        chemistry_formulas = [
            Formula(
                formula_id="chem_gen_001",
                name="Ideal Gas Law",
                formula="PV = nRT",
                subject="Chemistry",
                topic="States of Matter",
                variables="P: pressure (Pa), V: volume (m³), n: moles, R: 8.314 J/(mol·K), T: temperature (K)",
                units="SI: Pa, m³, mol, K",
                constraints="Ideal gas behavior (low P, high T)",
                common_mistakes=["Wrong units for R", "Using Celsius instead of Kelvin"],
                tags=["gas", "ideal", "mole", "PV=nRT"],
                exam_relevance={"JEE": 5, "NEET": 5}
            ),
            Formula(
                formula_id="chem_gen_002",
                name="Molarity",
                formula="M = n/V = moles of solute / volume of solution (L)",
                subject="Chemistry",
                topic="Solutions",
                variables="M: molarity (mol/L), n: moles of solute, V: volume in liters",
                units="mol/L or M",
                constraints="Volume is of solution, not solvent",
                common_mistakes=["Using solvent volume", "Unit conversion errors"],
                tags=["molarity", "concentration", "solution", "mole"],
                exam_relevance={"JEE": 5, "NEET": 5}
            ),
            Formula(
                formula_id="chem_gen_003",
                name="Gibbs Free Energy",
                formula="ΔG = ΔH - TΔS",
                subject="Chemistry",
                topic="Thermodynamics",
                variables="ΔG: Gibbs energy (J), ΔH: enthalpy (J), T: temperature (K), ΔS: entropy (J/K)",
                units="SI: Joule (J)",
                constraints="At constant T and P",
                common_mistakes=["Using °C instead of K", "Sign convention errors"],
                tags=["gibbs", "thermodynamics", "spontaneity", "entropy"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
            Formula(
                formula_id="chem_gen_004",
                name="pH Definition",
                formula="pH = -log[H⁺]",
                subject="Chemistry",
                topic="Ionic Equilibrium",
                variables="pH: acidity measure, [H⁺]: hydrogen ion concentration (mol/L)",
                units="Dimensionless (log scale)",
                constraints="Valid for aqueous solutions",
                common_mistakes=["Forgetting negative sign", "Logarithm base errors"],
                tags=["pH", "acid", "base", "ionic", "equilibrium"],
                exam_relevance={"JEE": 5, "NEET": 5}
            ),
            Formula(
                formula_id="chem_gen_005",
                name="Nernst Equation",
                formula="E = E° - (RT/nF)lnQ",
                subject="Chemistry",
                topic="Electrochemistry",
                variables="E: cell potential (V), E°: standard potential, R: gas constant, T: temp (K), n: electrons, F: Faraday constant, Q: reaction quotient",
                units="SI: Volt (V)",
                constraints="At equilibrium, E = 0",
                common_mistakes=["Wrong n value", "Confusing Q and K"],
                tags=["nernst", "electrochemistry", "cell", "potential"],
                exam_relevance={"JEE": 5, "NEET": 4}
            ),
        ]
        formulas.extend(chemistry_formulas)
        
        # Mathematics Formulas
        math_formulas = [
            Formula(
                formula_id="math_alg_001",
                name="Quadratic Formula",
                formula="x = (-b ± √(b²-4ac))/2a",
                subject="Mathematics",
                topic="Algebra",
                variables="For ax² + bx + c = 0: a, b, c are coefficients, x is the root",
                units="N/A",
                constraints="a ≠ 0",
                common_mistakes=["Sign errors in -b", "Forgetting 2a in denominator"],
                tags=["quadratic", "roots", "polynomial", "algebra"],
                exam_relevance={"JEE": 5, "NEET": 3}
            ),
            Formula(
                formula_id="math_alg_002",
                name="Discriminant",
                formula="D = b² - 4ac",
                subject="Mathematics",
                topic="Algebra",
                variables="D: discriminant, a, b, c: quadratic coefficients",
                units="N/A",
                constraints="D>0: 2 real roots, D=0: 1 root, D<0: complex roots",
                common_mistakes=["Forgetting to check sign", "Wrong coefficient identification"],
                tags=["discriminant", "quadratic", "roots", "nature of roots"],
                exam_relevance={"JEE": 5, "NEET": 3}
            ),
            Formula(
                formula_id="math_calc_001",
                name="Power Rule (Derivative)",
                formula="d/dx(xⁿ) = nxⁿ⁻¹",
                subject="Mathematics",
                topic="Calculus",
                variables="n: power (any real number), x: variable",
                units="N/A",
                constraints="Valid for all real n",
                common_mistakes=["Forgetting to subtract 1 from power", "Wrong coefficient"],
                tags=["derivative", "differentiation", "power rule", "calculus"],
                exam_relevance={"JEE": 5, "NEET": 3}
            ),
            Formula(
                formula_id="math_calc_002",
                name="Chain Rule",
                formula="d/dx[f(g(x))] = f'(g(x)) · g'(x)",
                subject="Mathematics",
                topic="Calculus",
                variables="f, g: functions, f': derivative of outer, g': derivative of inner",
                units="N/A",
                constraints="Both f and g must be differentiable",
                common_mistakes=["Forgetting inner derivative", "Wrong order of application"],
                tags=["chain rule", "derivative", "composite", "calculus"],
                exam_relevance={"JEE": 5, "NEET": 2}
            ),
            Formula(
                formula_id="math_calc_003",
                name="Integration Power Rule",
                formula="∫xⁿdx = xⁿ⁺¹/(n+1) + C",
                subject="Mathematics",
                topic="Calculus",
                variables="n: power (n ≠ -1), C: constant of integration",
                units="N/A",
                constraints="n ≠ -1 (use ln|x| for n=-1)",
                common_mistakes=["Forgetting +C", "Using for n=-1"],
                tags=["integration", "integral", "power rule", "calculus"],
                exam_relevance={"JEE": 5, "NEET": 2}
            ),
            Formula(
                formula_id="math_trig_001",
                name="Pythagorean Identity",
                formula="sin²θ + cos²θ = 1",
                subject="Mathematics",
                topic="Trigonometry",
                variables="θ: angle (any real number)",
                units="N/A (dimensionless)",
                constraints="Valid for all angles",
                common_mistakes=["Forgetting to square", "Sign errors in manipulation"],
                tags=["trigonometry", "identity", "sine", "cosine", "pythagorean"],
                exam_relevance={"JEE": 4, "NEET": 3}
            ),
            Formula(
                formula_id="math_comb_001",
                name="Permutation",
                formula="ⁿPᵣ = n!/(n-r)!",
                subject="Mathematics",
                topic="Permutations and Combinations",
                variables="n: total items, r: items to arrange",
                units="N/A (count)",
                constraints="0 ≤ r ≤ n",
                common_mistakes=["Confusing with combination", "Wrong factorial calculation"],
                tags=["permutation", "factorial", "arrangement", "counting"],
                exam_relevance={"JEE": 5, "NEET": 3}
            ),
            Formula(
                formula_id="math_comb_002",
                name="Combination",
                formula="ⁿCᵣ = n!/[r!(n-r)!]",
                subject="Mathematics",
                topic="Permutations and Combinations",
                variables="n: total items, r: items to select",
                units="N/A (count)",
                constraints="0 ≤ r ≤ n, order doesn't matter",
                common_mistakes=["Confusing with permutation", "Forgetting denominator r!"],
                tags=["combination", "factorial", "selection", "counting", "choose"],
                exam_relevance={"JEE": 5, "NEET": 3}
            ),
        ]
        formulas.extend(math_formulas)
        
        return formulas


# =============================================================================
# EXAM STRATEGY BANK (Structured, replaces hardcoded EXAM_STRATEGY_DATA dict)
# =============================================================================

class ExamStrategyBank:
    """
    Structured exam strategy database.
    
    Replaces the hardcoded EXAM_STRATEGY_DATA dict in exam_strategy.py
    """
    
    def __init__(self):
        self.strategies: Dict[str, ExamTopicStrategy] = {}
        self._exam_index: Dict[str, List[str]] = {}  # exam -> strategy_ids
        self._topic_index: Dict[str, List[str]] = {}  # topic -> strategy_ids
        self._subject_index: Dict[str, List[str]] = {}  # subject -> strategy_ids
        self._load_strategies()
    
    def _load_strategies(self):
        """Load strategies from file or initialize defaults"""
        if EXAM_STRATEGY_FILE.exists():
            try:
                with open(EXAM_STRATEGY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for strategy_data in data.get("strategies", []):
                        strategy = ExamTopicStrategy.from_dict(strategy_data)
                        self._add_strategy_to_index(strategy)
                logger.info(f"🎯 Loaded {len(self.strategies)} exam strategies from bank")
            except Exception as e:
                logger.warning(f"Failed to load strategies file: {e}, initializing defaults")
                self._init_default_strategies()
        else:
            self._init_default_strategies()
    
    def _init_default_strategies(self):
        """Initialize with comprehensive strategy set"""
        default_strategies = self._get_default_strategies()
        for strategy in default_strategies:
            self._add_strategy_to_index(strategy)
        self.save()
        logger.info(f"🎯 Initialized {len(self.strategies)} default strategies")
    
    def _add_strategy_to_index(self, strategy: ExamTopicStrategy):
        """Add strategy to all indices"""
        self.strategies[strategy.strategy_id] = strategy
        
        # Exam index
        exam = strategy.exam_type.upper()
        if exam not in self._exam_index:
            self._exam_index[exam] = []
        self._exam_index[exam].append(strategy.strategy_id)
        
        # Topic index
        topic = strategy.topic.lower()
        if topic not in self._topic_index:
            self._topic_index[topic] = []
        self._topic_index[topic].append(strategy.strategy_id)
        
        # Subject index
        subject = strategy.subject.lower()
        if subject not in self._subject_index:
            self._subject_index[subject] = []
        self._subject_index[subject].append(strategy.strategy_id)
    
    def save(self):
        """Persist strategies to file"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(EXAM_STRATEGY_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "strategies": [s.to_dict() for s in self.strategies.values()],
                "count": len(self.strategies),
                "updated_at": datetime.utcnow().isoformat()
            }, f, indent=2)
    
    def search(
        self,
        topic: str,
        exam_type: str,
        subject: Optional[str] = None
    ) -> Optional[ExamTopicStrategy]:
        """
        Search for strategy by topic and exam type.
        
        Returns best matching strategy or None.
        """
        exam_upper = exam_type.upper()
        topic_lower = topic.lower()
        
        # Get strategies for this exam
        exam_strategy_ids = set(self._exam_index.get(exam_upper, []))
        if not exam_strategy_ids:
            return None
        
        # Find matching topic
        best_match = None
        best_score = 0
        
        for sid in exam_strategy_ids:
            strategy = self.strategies[sid]
            strategy_topic_lower = strategy.topic.lower()
            
            # Exact match
            if topic_lower == strategy_topic_lower:
                return strategy
            
            # Partial match
            if topic_lower in strategy_topic_lower or strategy_topic_lower in topic_lower:
                score = len(set(topic_lower.split()) & set(strategy_topic_lower.split()))
                if score > best_score:
                    best_score = score
                    best_match = strategy
        
        return best_match
    
    def get_all_for_exam(self, exam_type: str) -> List[ExamTopicStrategy]:
        """Get all strategies for an exam"""
        exam_upper = exam_type.upper()
        strategy_ids = self._exam_index.get(exam_upper, [])
        return [self.strategies[sid] for sid in strategy_ids]
    
    def _get_default_strategies(self) -> List[ExamTopicStrategy]:
        """Generate comprehensive default strategy set"""
        strategies = []
        
        # JEE Strategies
        jee_strategies = [
            ExamTopicStrategy(
                strategy_id="jee_phys_mechanics",
                exam_type="JEE",
                topic="Mechanics",
                subject="Physics",
                weightage_percent=25.0,
                common_traps=[
                    "Confusing reference frames in relative motion",
                    "Sign errors in projectile motion",
                    "Forgetting pseudo forces in non-inertial frames",
                    "Wrong application of conservation laws"
                ],
                shortcut_technique="**Energy Method**: When forces are complex, use energy conservation. Work-energy theorem is often faster than Newton's laws for problems involving variable forces.",
                ncert_relevance="NCERT Class 11 Chapters 3-7 cover mechanics. JEE expects deeper problem-solving skills beyond NCERT.",
                pyq_pattern="5-7 questions per paper. Often combined with calculus. NLM + circular motion is common.",
                difficulty_rating=4,
                recommended_time_percent=15.0
            ),
            ExamTopicStrategy(
                strategy_id="jee_phys_electro",
                exam_type="JEE",
                topic="Electrostatics and Current Electricity",
                subject="Physics",
                weightage_percent=15.0,
                common_traps=[
                    "Confusing electric field and potential formulas",
                    "Sign errors in work done by electric field",
                    "Wrong application of Kirchhoff's laws",
                    "Forgetting internal resistance"
                ],
                shortcut_technique="**Potential Method**: For complex charge configurations, calculate potential first (scalar), then field if needed. This avoids vector addition.",
                ncert_relevance="NCERT Class 12 Chapters 1-3. JEE tests circuit analysis skills heavily.",
                pyq_pattern="4-6 questions. RC circuits and Gauss's law are favorites.",
                difficulty_rating=4,
                recommended_time_percent=12.0
            ),
            ExamTopicStrategy(
                strategy_id="jee_phys_modern",
                exam_type="JEE",
                topic="Modern Physics",
                subject="Physics",
                weightage_percent=10.0,
                common_traps=[
                    "Confusing binding energy per nucleon trends",
                    "Wrong threshold frequency calculation",
                    "Confusing activity with number of atoms",
                    "Sign errors in decay equations"
                ],
                shortcut_technique="**Ratio Method**: For radioactivity problems, always work with ratios (N/N₀, A/A₀). Avoid absolute calculations when possible.",
                ncert_relevance="NCERT Class 12 Chapters 11-13. JEE tests numerical applications.",
                pyq_pattern="3-4 questions. Photoelectric effect and nuclear physics common.",
                difficulty_rating=3,
                recommended_time_percent=8.0
            ),
            ExamTopicStrategy(
                strategy_id="jee_chem_organic",
                exam_type="JEE",
                topic="Organic Chemistry",
                subject="Chemistry",
                weightage_percent=35.0,
                common_traps=[
                    "Confusing SN1 vs SN2 mechanisms",
                    "Wrong stability order of carbocations",
                    "Missing stereochemistry in reactions",
                    "Ignoring electronic effects (resonance, inductive)"
                ],
                shortcut_technique="**Mechanism First**: Always draw the mechanism. Identify: (1) nucleophile, (2) electrophile, (3) leaving group. This predicts products accurately.",
                ncert_relevance="NCERT Class 12 Chapters 10-16. JEE expects mechanism understanding.",
                pyq_pattern="10-12 questions. Reaction mechanisms and named reactions dominate.",
                difficulty_rating=4,
                recommended_time_percent=18.0
            ),
            ExamTopicStrategy(
                strategy_id="jee_chem_physical",
                exam_type="JEE",
                topic="Physical Chemistry",
                subject="Chemistry",
                weightage_percent=35.0,
                common_traps=[
                    "Unit conversion errors (especially in gas laws)",
                    "Sign convention in thermodynamics",
                    "Confusing molarity and molality",
                    "Wrong equilibrium constant expressions"
                ],
                shortcut_technique="**Dimensional Analysis**: Always check units. If answer has wrong units, the method is wrong. This catches 90% of calculation errors.",
                ncert_relevance="NCERT Class 11 Chapters 1-7, Class 12 Chapters 1-5. JEE needs numerical proficiency.",
                pyq_pattern="10-12 questions. Electrochemistry and equilibrium are high-weightage.",
                difficulty_rating=4,
                recommended_time_percent=18.0
            ),
            ExamTopicStrategy(
                strategy_id="jee_math_calculus",
                exam_type="JEE",
                topic="Calculus",
                subject="Mathematics",
                weightage_percent=35.0,
                common_traps=[
                    "Forgetting constant of integration",
                    "Wrong limits in definite integrals",
                    "Confusing maxima/minima conditions",
                    "Chain rule errors in differentiation"
                ],
                shortcut_technique="**Substitution Strategy**: For integration, always check if u-substitution works first. 70% of JEE integrals can be solved by substitution alone.",
                ncert_relevance="NCERT Class 12 Chapters 5-8. JEE expects mastery of all techniques.",
                pyq_pattern="10-12 questions. Definite integrals and application of derivatives common.",
                difficulty_rating=5,
                recommended_time_percent=20.0
            ),
            ExamTopicStrategy(
                strategy_id="jee_math_algebra",
                exam_type="JEE",
                topic="Algebra",
                subject="Mathematics",
                weightage_percent=25.0,
                common_traps=[
                    "Wrong binomial coefficient calculation",
                    "Missing terms in sequence sums",
                    "Complex number argument errors",
                    "Matrix multiplication order"
                ],
                shortcut_technique="**Pattern Recognition**: In sequences, always check if it's AP, GP, or AGP. For matrices, check if special properties apply (symmetric, orthogonal).",
                ncert_relevance="NCERT Class 11 Chapters 4-9, Class 12 Chapters 3-4. JEE adds complexity.",
                pyq_pattern="8-10 questions. Matrices and quadratics are favorites.",
                difficulty_rating=4,
                recommended_time_percent=15.0
            ),
        ]
        strategies.extend(jee_strategies)
        
        # NEET Strategies
        neet_strategies = [
            ExamTopicStrategy(
                strategy_id="neet_bio_physiology",
                exam_type="NEET",
                topic="Human Physiology",
                subject="Biology",
                weightage_percent=20.0,
                common_traps=[
                    "Confusing different types of blood cells",
                    "Mixing up hormone sources and targets",
                    "Wrong cardiac cycle phases",
                    "Nephron structure confusion"
                ],
                shortcut_technique="**System-by-System**: Study each body system completely before moving to next. Use flowcharts for processes like digestion, respiration.",
                ncert_relevance="NCERT Class 11 Chapters 17-22, Class 12 Chapters 16-19. NEET directly tests NCERT content.",
                pyq_pattern="15-20 questions. Diagrams are crucial. Focus on NCERT figures.",
                difficulty_rating=3,
                recommended_time_percent=15.0
            ),
            ExamTopicStrategy(
                strategy_id="neet_bio_genetics",
                exam_type="NEET",
                topic="Genetics and Evolution",
                subject="Biology",
                weightage_percent=18.0,
                common_traps=[
                    "Confusing genotype vs phenotype ratios",
                    "Wrong pedigree analysis",
                    "Missing sex-linked inheritance patterns",
                    "Confusing DNA replication vs transcription"
                ],
                shortcut_technique="**Punnett Square Practice**: Do 10 pedigree problems daily. For molecular biology, memorize the enzymes and their functions.",
                ncert_relevance="NCERT Class 12 Chapters 5-7. NEET expects application skills.",
                pyq_pattern="12-15 questions. Pedigree analysis and molecular biology common.",
                difficulty_rating=4,
                recommended_time_percent=12.0
            ),
            ExamTopicStrategy(
                strategy_id="neet_bio_botany",
                exam_type="NEET",
                topic="Plant Biology",
                subject="Biology",
                weightage_percent=25.0,
                common_traps=[
                    "Confusing C3 vs C4 vs CAM plants",
                    "Wrong plant hormone effects",
                    "Mixing up tissue types",
                    "Life cycle stage confusion"
                ],
                shortcut_technique="**Diagram-First Approach**: For plant anatomy, always start by drawing the diagram. Label all parts. This helps in MCQ elimination.",
                ncert_relevance="NCERT Class 11 Chapters 5-15, Class 12 Chapters 2-3, 13-15. NCERT figures are gold.",
                pyq_pattern="20-25 questions. Photosynthesis and plant anatomy are high-weightage.",
                difficulty_rating=3,
                recommended_time_percent=18.0
            ),
            ExamTopicStrategy(
                strategy_id="neet_phys_mechanics",
                exam_type="NEET",
                topic="Mechanics",
                subject="Physics",
                weightage_percent=20.0,
                common_traps=[
                    "Unit conversion errors",
                    "Wrong sign in projectile problems",
                    "Confusing work and energy signs",
                    "Forgetting to resolve components"
                ],
                shortcut_technique="**NCERT Numerical Focus**: NEET physics is formula-based. Memorize formulas and practice NCERT back-of-chapter numericals.",
                ncert_relevance="NCERT Class 11 Chapters 3-7. NEET tests direct NCERT content.",
                pyq_pattern="8-10 questions. Direct formula application is common.",
                difficulty_rating=3,
                recommended_time_percent=12.0
            ),
            ExamTopicStrategy(
                strategy_id="neet_chem_organic",
                exam_type="NEET",
                topic="Organic Chemistry",
                subject="Chemistry",
                weightage_percent=30.0,
                common_traps=[
                    "Confusing functional group reactions",
                    "Wrong IUPAC naming",
                    "Missing isomer counts",
                    "Reaction condition errors"
                ],
                shortcut_technique="**Functional Group Mastery**: Learn reactions grouped by functional group. Make a table: Functional Group → Reagent → Product.",
                ncert_relevance="NCERT Class 12 Chapters 10-16. NEET directly tests NCERT reactions.",
                pyq_pattern="15-18 questions. Named reactions and conversions are favorites.",
                difficulty_rating=3,
                recommended_time_percent=15.0
            ),
        ]
        strategies.extend(neet_strategies)
        
        # CBSE Strategies
        cbse_strategies = [
            ExamTopicStrategy(
                strategy_id="cbse_phys_electricity",
                exam_type="CBSE",
                topic="Electricity and Magnetism",
                subject="Physics",
                weightage_percent=18.0,
                common_traps=[
                    "Series vs parallel resistance formulas",
                    "Kirchhoff's laws sign errors",
                    "Magnetic field direction mistakes",
                    "Unit conversion errors"
                ],
                shortcut_technique="**Circuit Simplification**: Always simplify circuits to series-parallel combinations. Redraw complex circuits step by step.",
                ncert_relevance="NCERT Class 10 Chapter 12, Class 12 Chapters 3-5. CBSE follows NCERT exactly.",
                pyq_pattern="10-12 marks. Circuit numericals and magnetic effect of current common.",
                difficulty_rating=3,
                recommended_time_percent=12.0
            ),
            ExamTopicStrategy(
                strategy_id="cbse_chem_reactions",
                exam_type="CBSE",
                topic="Chemical Reactions",
                subject="Chemistry",
                weightage_percent=15.0,
                common_traps=[
                    "Unbalanced equations",
                    "Wrong oxidation states",
                    "Missing reaction conditions",
                    "Confusing reaction types"
                ],
                shortcut_technique="**Balance First**: Always balance equations before answering. Check: atoms balanced, charges balanced (for ionic), conditions written.",
                ncert_relevance="NCERT Class 10 Chapters 1-4, Class 12 Chapters 1-8. Direct NCERT testing.",
                pyq_pattern="8-10 marks. Balancing and identifying reaction types common.",
                difficulty_rating=2,
                recommended_time_percent=10.0
            ),
        ]
        strategies.extend(cbse_strategies)
        
        return strategies


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

_source_registry: Optional[SourceRegistry] = None
_formula_bank: Optional[FormulaBank] = None
_exam_strategy_bank: Optional[ExamStrategyBank] = None


def get_source_registry() -> SourceRegistry:
    """Get or create the global source registry"""
    global _source_registry
    if _source_registry is None:
        _source_registry = SourceRegistry()
    return _source_registry


def get_formula_bank() -> FormulaBank:
    """Get or create the global formula bank"""
    global _formula_bank
    if _formula_bank is None:
        _formula_bank = FormulaBank()
    return _formula_bank


def get_exam_strategy_bank() -> ExamStrategyBank:
    """Get or create the global exam strategy bank"""
    global _exam_strategy_bank
    if _exam_strategy_bank is None:
        _exam_strategy_bank = ExamStrategyBank()
    return _exam_strategy_bank


# =============================================================================
# INGESTION LOG
# =============================================================================

class IngestionLog:
    """
    Tracks ingestion job runs for observability.
    """
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self._load_logs()
    
    def _load_logs(self):
        """Load existing logs"""
        if INGESTION_LOG_FILE.exists():
            try:
                with open(INGESTION_LOG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logs = data.get("logs", [])
            except:
                self.logs = []
    
    def add_entry(
        self,
        source_id: str,
        status: str,
        items_processed: int,
        errors: List[str] = None
    ):
        """Add a log entry"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "source_id": source_id,
            "status": status,
            "items_processed": items_processed,
            "errors": errors or []
        }
        self.logs.append(entry)
        self._save()
        
        logger.info(f"📋 Ingestion log: {source_id} - {status} - {items_processed} items")
    
    def _save(self):
        """Persist logs"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(INGESTION_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"logs": self.logs[-100:]}, f, indent=2)  # Keep last 100 entries


def get_ingestion_log() -> IngestionLog:
    """Get ingestion log instance"""
    return IngestionLog()
