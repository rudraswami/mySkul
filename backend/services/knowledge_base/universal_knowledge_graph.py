"""
Universal Knowledge Graph - Global Education OS
================================================

NOT limited to JEE/NEET - covers ALL education domains:
- Sciences: Physics, Chemistry, Biology, Computer Science, Environmental Science
- Mathematics: Arithmetic → Calculus → Statistics → Discrete Math
- Humanities: History, Geography, Economics, Political Science, Sociology
- Languages: English, Hindi, Sanskrit, Regional languages, Foreign languages
- Life Skills: Critical thinking, Financial literacy, Health, Communication
- Arts: Music theory, Visual arts, Literature, Drama
- Professional: Career guidance, Industry skills, Research methods

Graph Structure:
- Nodes: Concepts with metadata (difficulty, age_range, real_world_use)
- Edges: Relationships (prerequisite, application, analogy, contrast, extends)
- Multi-domain: Concepts can belong to multiple domains
- Learning Paths: From beginner → expert in any domain
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ConceptDifficulty(Enum):
    """Difficulty levels for concepts"""
    FOUNDATIONAL = "foundational"  # Basic building blocks
    BEGINNER = "beginner"          # Entry level
    INTERMEDIATE = "intermediate"  # Requires prerequisites
    ADVANCED = "advanced"          # Complex understanding
    EXPERT = "expert"              # Research/professional level


class RelationType(Enum):
    """Types of relationships between concepts"""
    PREREQUISITE = "prerequisite"  # Must learn A before B
    APPLICATION = "application"    # A is applied in B
    ANALOGY = "analogy"           # A is similar to B
    CONTRAST = "contrast"         # A is opposite to B
    EXTENDS = "extends"           # B extends/builds on A
    RELATED = "related"           # General relationship
    EXAMPLE = "example"           # B is an example of A
    PART_OF = "part_of"          # A is part of B


@dataclass
class ConceptNode:
    """
    Represents a single concept in the knowledge graph
    """
    concept_id: str
    name: str
    domain: str  # e.g., "Physics", "Mathematics", "History"
    subdomain: str  # e.g., "Mechanics", "Calculus", "Ancient History"
    difficulty: ConceptDifficulty
    age_range: Tuple[int, int]  # (min_age, max_age)
    description: str
    key_points: List[str] = field(default_factory=list)
    formulas: List[str] = field(default_factory=list)
    exam_relevance: Dict[str, int] = field(default_factory=dict)  # {"JEE": 8, "NEET": 3, "CBSE": 10}
    real_world_applications: List[str] = field(default_factory=list)
    common_misconceptions: List[str] = field(default_factory=list)
    learning_resources: List[Dict[str, str]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "name": self.name,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "difficulty": self.difficulty.value,
            "age_range": self.age_range,
            "description": self.description,
            "key_points": self.key_points,
            "formulas": self.formulas,
            "exam_relevance": self.exam_relevance,
            "real_world_applications": self.real_world_applications,
            "common_misconceptions": self.common_misconceptions,
            "tags": self.tags
        }


@dataclass
class ConceptEdge:
    """Represents a relationship between two concepts"""
    from_concept: str
    to_concept: str
    relation_type: RelationType
    strength: float = 1.0  # 0.0 to 1.0
    explanation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_concept,
            "to": self.to_concept,
            "type": self.relation_type.value,
            "strength": self.strength,
            "explanation": self.explanation
        }


class UniversalKnowledgeGraph:
    """
    Universal Education Knowledge Graph
    
    Features:
    - Multi-domain coverage (not exam-limited)
    - Hierarchical concept organization
    - Rich relationships between concepts
    - Learning path generation
    - Query by domain, difficulty, age
    - Real-world application mapping
    """
    
    def __init__(self):
        """Initialize empty knowledge graph"""
        self.nodes: Dict[str, ConceptNode] = {}
        self.edges: List[ConceptEdge] = []
        
        # Indices for fast lookup
        self.domain_index: Dict[str, List[str]] = {}  # domain -> concept_ids
        self.difficulty_index: Dict[ConceptDifficulty, List[str]] = {}
        self.tag_index: Dict[str, List[str]] = {}
        
        # Adjacency lists for graph traversal
        self.prerequisites: Dict[str, List[str]] = {}  # concept -> prerequisite concepts
        self.applications: Dict[str, List[str]] = {}   # concept -> application concepts
        
        # Initialize with seed concepts
        self._initialize_seed_concepts()
        
        logger.info(f"🌍 UniversalKnowledgeGraph initialized with {len(self.nodes)} concepts")
    
    def add_concept(
        self,
        concept_id: str,
        name: str,
        domain: str,
        subdomain: str,
        difficulty: ConceptDifficulty,
        age_range: Tuple[int, int],
        description: str,
        **kwargs
    ) -> ConceptNode:
        """Add a new concept to the graph"""
        concept = ConceptNode(
            concept_id=concept_id,
            name=name,
            domain=domain,
            subdomain=subdomain,
            difficulty=difficulty,
            age_range=age_range,
            description=description,
            **kwargs
        )
        
        self.nodes[concept_id] = concept
        
        # Update indices
        if domain not in self.domain_index:
            self.domain_index[domain] = []
        self.domain_index[domain].append(concept_id)
        
        if difficulty not in self.difficulty_index:
            self.difficulty_index[difficulty] = []
        self.difficulty_index[difficulty].append(concept_id)
        
        for tag in concept.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(concept_id)
        
        logger.debug(f"Added concept: {name} ({domain}/{subdomain})")
        return concept
    
    def add_relationship(
        self,
        from_concept: str,
        to_concept: str,
        relation_type: RelationType,
        strength: float = 1.0,
        explanation: str = ""
    ) -> ConceptEdge:
        """Add a relationship between two concepts"""
        if from_concept not in self.nodes:
            logger.warning(f"Source concept {from_concept} not found")
            return None
        
        if to_concept not in self.nodes:
            logger.warning(f"Target concept {to_concept} not found")
            return None
        
        edge = ConceptEdge(
            from_concept=from_concept,
            to_concept=to_concept,
            relation_type=relation_type,
            strength=strength,
            explanation=explanation
        )
        
        self.edges.append(edge)
        
        # Update adjacency lists
        if relation_type == RelationType.PREREQUISITE:
            if to_concept not in self.prerequisites:
                self.prerequisites[to_concept] = []
            self.prerequisites[to_concept].append(from_concept)
        
        if relation_type == RelationType.APPLICATION:
            if from_concept not in self.applications:
                self.applications[from_concept] = []
            self.applications[from_concept].append(to_concept)
        
        return edge
    
    def get_concept(self, concept_id: str) -> Optional[ConceptNode]:
        """Get a concept by ID"""
        return self.nodes.get(concept_id)
    
    def get_prerequisites(self, concept_id: str) -> List[ConceptNode]:
        """Get all prerequisite concepts for a given concept"""
        prereq_ids = self.prerequisites.get(concept_id, [])
        return [self.nodes[cid] for cid in prereq_ids if cid in self.nodes]
    
    def get_applications(self, concept_id: str) -> List[ConceptNode]:
        """Get all application concepts for a given concept"""
        app_ids = self.applications.get(concept_id, [])
        return [self.nodes[cid] for cid in app_ids if cid in self.nodes]
    
    def get_related_concepts(
        self,
        concept_id: str,
        relation_type: Optional[RelationType] = None
    ) -> List[Tuple[ConceptNode, RelationType, float]]:
        """Get all concepts related to a given concept"""
        related = []
        
        for edge in self.edges:
            if edge.from_concept == concept_id:
                if relation_type is None or edge.relation_type == relation_type:
                    target = self.nodes.get(edge.to_concept)
                    if target:
                        related.append((target, edge.relation_type, edge.strength))
            elif edge.to_concept == concept_id:
                if relation_type is None or edge.relation_type == relation_type:
                    source = self.nodes.get(edge.from_concept)
                    if source:
                        related.append((source, edge.relation_type, edge.strength))
        
        return related
    
    def query_by_domain(
        self,
        domain: str,
        subdomain: Optional[str] = None,
        difficulty: Optional[ConceptDifficulty] = None,
        age_range: Optional[Tuple[int, int]] = None
    ) -> List[ConceptNode]:
        """Query concepts by domain and filters"""
        concept_ids = self.domain_index.get(domain, [])
        concepts = [self.nodes[cid] for cid in concept_ids]
        
        # Filter by subdomain
        if subdomain:
            concepts = [c for c in concepts if c.subdomain == subdomain]
        
        # Filter by difficulty
        if difficulty:
            concepts = [c for c in concepts if c.difficulty == difficulty]
        
        # Filter by age range
        if age_range:
            min_age, max_age = age_range
            concepts = [c for c in concepts if c.age_range[0] <= max_age and c.age_range[1] >= min_age]
        
        return concepts
    
    def find_learning_path(
        self,
        start_concept: str,
        end_concept: str
    ) -> List[ConceptNode]:
        """
        Find a learning path from start to end concept using BFS
        Returns ordered list of concepts to learn
        """
        if start_concept not in self.nodes or end_concept not in self.nodes:
            return []
        
        # BFS to find shortest path
        from collections import deque
        
        queue = deque([(start_concept, [start_concept])])
        visited = {start_concept}
        
        while queue:
            current, path = queue.popleft()
            
            if current == end_concept:
                return [self.nodes[cid] for cid in path]
            
            # Explore related concepts (prerequisites and extensions)
            for edge in self.edges:
                if edge.from_concept == current:
                    next_concept = edge.to_concept
                    if next_concept not in visited:
                        visited.add(next_concept)
                        queue.append((next_concept, path + [next_concept]))
        
        return []  # No path found
    
    def get_foundational_concepts(self, domain: str) -> List[ConceptNode]:
        """Get all foundational concepts in a domain"""
        return self.query_by_domain(domain, difficulty=ConceptDifficulty.FOUNDATIONAL)
    
    def search_concepts(self, query: str) -> List[ConceptNode]:
        """Search concepts by name or description"""
        query_lower = query.lower()
        results = []
        
        for concept in self.nodes.values():
            if (query_lower in concept.name.lower() or 
                query_lower in concept.description.lower() or
                any(query_lower in kp.lower() for kp in concept.key_points)):
                results.append(concept)
        
        return results
    
    def get_concept_by_name(self, name: str, domain: Optional[str] = None) -> Optional[ConceptNode]:
        """Find concept by name (case-insensitive)"""
        name_lower = name.lower()
        
        for concept in self.nodes.values():
            if concept.name.lower() == name_lower:
                if domain is None or concept.domain == domain:
                    return concept
        
        return None
    
    def _initialize_seed_concepts(self):
        """Initialize with seed concepts across all domains"""
        
        # ========== MATHEMATICS ==========
        
        # Arithmetic (Foundational)
        self.add_concept(
            "math_numbers", "Numbers", "Mathematics", "Arithmetic",
            ConceptDifficulty.FOUNDATIONAL, (6, 99),
            "Understanding numbers, counting, and basic operations",
            key_points=["Natural numbers", "Integers", "Real numbers", "Number properties"],
            tags=["fundamental", "arithmetic", "numbers"]
        )
        
        self.add_concept(
            "math_operations", "Basic Operations", "Mathematics", "Arithmetic",
            ConceptDifficulty.FOUNDATIONAL, (6, 99),
            "Addition, subtraction, multiplication, division",
            key_points=["Addition", "Subtraction", "Multiplication", "Division", "Order of operations"],
            tags=["fundamental", "arithmetic", "operations"],
            real_world_applications=["Counting money", "Measuring", "Shopping calculations"]
        )
        
        # Algebra (Beginner → Advanced)
        self.add_concept(
            "math_variables", "Variables and Expressions", "Mathematics", "Algebra",
            ConceptDifficulty.BEGINNER, (12, 99),
            "Using symbols to represent numbers and relationships",
            key_points=["Variables", "Constants", "Algebraic expressions", "Simplification"],
            tags=["algebra", "variables"],
            exam_relevance={"CBSE": 10, "JEE": 8, "SAT": 7}
        )
        
        self.add_concept(
            "math_equations", "Equations and Inequalities", "Mathematics", "Algebra",
            ConceptDifficulty.INTERMEDIATE, (13, 99),
            "Solving for unknown values using equations",
            key_points=["Linear equations", "Quadratic equations", "Systems of equations", "Inequalities"],
            formulas=["ax + b = 0", "ax² + bx + c = 0", "x = (-b ± √(b² - 4ac)) / 2a"],
            tags=["algebra", "equations"],
            exam_relevance={"CBSE": 10, "JEE": 10, "NEET": 6}
        )
        
        # Calculus
        self.add_concept(
            "math_limits", "Limits", "Mathematics", "Calculus",
            ConceptDifficulty.ADVANCED, (16, 99),
            "Understanding behavior of functions as they approach values",
            key_points=["Definition of limit", "One-sided limits", "Continuity", "L'Hôpital's rule"],
            formulas=["lim(x→a) f(x)", "lim(x→∞) f(x)"],
            tags=["calculus", "limits"],
            exam_relevance={"JEE": 10, "CBSE": 9}
        )
        
        self.add_concept(
            "math_derivatives", "Derivatives", "Mathematics", "Calculus",
            ConceptDifficulty.ADVANCED, (16, 99),
            "Rate of change of functions",
            key_points=["Definition", "Power rule", "Product rule", "Quotient rule", "Chain rule"],
            formulas=["f'(x) = lim(h→0) [f(x+h) - f(x)]/h", "d/dx(xⁿ) = nxⁿ⁻¹"],
            tags=["calculus", "derivatives"],
            exam_relevance={"JEE": 10, "CBSE": 10}
        )
        
        # ========== PHYSICS ==========
        
        self.add_concept(
            "physics_motion", "Motion", "Physics", "Mechanics",
            ConceptDifficulty.BEGINNER, (13, 99),
            "Study of how objects move",
            key_points=["Distance", "Displacement", "Speed", "Velocity", "Acceleration"],
            formulas=["v = u + at", "s = ut + ½at²", "v² = u² + 2as"],
            tags=["mechanics", "kinematics"],
            exam_relevance={"JEE": 10, "NEET": 8, "CBSE": 10},
            real_world_applications=["Car acceleration", "Sports physics", "Space travel"]
        )
        
        self.add_concept(
            "physics_force", "Force and Newton's Laws", "Physics", "Mechanics",
            ConceptDifficulty.INTERMEDIATE, (14, 99),
            "Understanding forces and their effects on motion",
            key_points=["Newton's First Law", "Newton's Second Law", "Newton's Third Law", "Friction"],
            formulas=["F = ma", "F₁₂ = -F₂₁"],
            tags=["mechanics", "force", "newton"],
            exam_relevance={"JEE": 10, "NEET": 9, "CBSE": 10}
        )
        
        # ========== CHEMISTRY ==========
        
        self.add_concept(
            "chem_atoms", "Atomic Structure", "Chemistry", "Physical Chemistry",
            ConceptDifficulty.BEGINNER, (13, 99),
            "Structure and properties of atoms",
            key_points=["Protons", "Neutrons", "Electrons", "Atomic number", "Mass number", "Isotopes"],
            tags=["atoms", "structure"],
            exam_relevance={"JEE": 9, "NEET": 10, "CBSE": 10}
        )
        
        self.add_concept(
            "chem_bonding", "Chemical Bonding", "Chemistry", "Physical Chemistry",
            ConceptDifficulty.INTERMEDIATE, (14, 99),
            "How atoms combine to form molecules",
            key_points=["Ionic bonds", "Covalent bonds", "Metallic bonds", "Lewis structures", "VSEPR theory"],
            tags=["bonding", "molecules"],
            exam_relevance={"JEE": 10, "NEET": 10, "CBSE": 10}
        )
        
        # ========== BIOLOGY ==========
        
        self.add_concept(
            "bio_cells", "Cell Structure", "Biology", "Cell Biology",
            ConceptDifficulty.BEGINNER, (12, 99),
            "Basic unit of life and its components",
            key_points=["Cell membrane", "Cytoplasm", "Nucleus", "Organelles", "Prokaryotic vs Eukaryotic"],
            tags=["cell", "structure"],
            exam_relevance={"NEET": 10, "CBSE": 10}
        )
        
        # ========== HUMANITIES ==========
        
        self.add_concept(
            "history_independence", "Indian Independence Movement", "History", "Modern India",
            ConceptDifficulty.INTERMEDIATE, (14, 99),
            "India's struggle for freedom from British rule",
            key_points=["1857 Revolt", "Gandhi's movement", "Non-cooperation", "Quit India", "1947 Independence"],
            tags=["history", "independence", "india"],
            exam_relevance={"CBSE": 10, "UPSC": 10}
        )
        
        self.add_concept(
            "eco_demand_supply", "Demand and Supply", "Economics", "Microeconomics",
            ConceptDifficulty.INTERMEDIATE, (15, 99),
            "Market forces that determine prices",
            key_points=["Law of demand", "Law of supply", "Equilibrium", "Elasticity", "Market structures"],
            tags=["economics", "market"],
            exam_relevance={"CBSE": 10, "UPSC": 9},
            real_world_applications=["Price determination", "Business strategy", "Policy making"]
        )
        
        # ========== LIFE SKILLS ==========
        
        self.add_concept(
            "skill_critical_thinking", "Critical Thinking", "Life Skills", "Cognitive Skills",
            ConceptDifficulty.INTERMEDIATE, (14, 99),
            "Analyzing and evaluating information objectively",
            key_points=["Logical reasoning", "Problem analysis", "Decision making", "Bias recognition"],
            tags=["thinking", "reasoning", "analysis"],
            real_world_applications=["Problem solving", "Decision making", "Career success"]
        )
        
        self.add_concept(
            "skill_financial_literacy", "Financial Literacy", "Life Skills", "Practical Skills",
            ConceptDifficulty.BEGINNER, (16, 99),
            "Understanding money management and personal finance",
            key_points=["Budgeting", "Saving", "Investing", "Credit", "Taxes", "Insurance"],
            tags=["finance", "money", "practical"],
            real_world_applications=["Personal budgeting", "Investment decisions", "Financial planning"]
        )
        
        # ========== LANGUAGES ==========
        
        self.add_concept(
            "lang_grammar", "English Grammar", "Languages", "English",
            ConceptDifficulty.FOUNDATIONAL, (8, 99),
            "Rules and structure of English language",
            key_points=["Parts of speech", "Tenses", "Sentence structure", "Punctuation"],
            tags=["english", "grammar", "language"],
            exam_relevance={"CBSE": 10}
        )
        
        # ========== ADD RELATIONSHIPS ==========
        
        # Math progression
        self.add_relationship("math_numbers", "math_operations", RelationType.PREREQUISITE, 1.0, "Need to understand numbers before operations")
        self.add_relationship("math_operations", "math_variables", RelationType.PREREQUISITE, 1.0, "Operations are used in algebraic expressions")
        self.add_relationship("math_variables", "math_equations", RelationType.PREREQUISITE, 1.0, "Equations use variables and expressions")
        self.add_relationship("math_equations", "math_limits", RelationType.PREREQUISITE, 0.7, "Algebra helps understand limits")
        self.add_relationship("math_limits", "math_derivatives", RelationType.PREREQUISITE, 1.0, "Derivatives are defined using limits")
        
        # Physics progression
        self.add_relationship("math_variables", "physics_motion", RelationType.PREREQUISITE, 0.8, "Algebra needed for kinematics equations")
        self.add_relationship("physics_motion", "physics_force", RelationType.PREREQUISITE, 1.0, "Force affects motion")
        self.add_relationship("math_derivatives", "physics_motion", RelationType.APPLICATION, 0.9, "Derivatives describe velocity and acceleration")
        
        # Chemistry progression
        self.add_relationship("chem_atoms", "chem_bonding", RelationType.PREREQUISITE, 1.0, "Must understand atoms before bonding")
        
        # Cross-domain
        self.add_relationship("math_operations", "skill_financial_literacy", RelationType.APPLICATION, 0.8, "Math operations used in finance")
        self.add_relationship("skill_critical_thinking", "eco_demand_supply", RelationType.APPLICATION, 0.7, "Critical thinking helps analyze economics")
        
        logger.info("✅ Seed concepts and relationships initialized")


# Singleton instance
_graph_instance: Optional[UniversalKnowledgeGraph] = None


def get_universal_knowledge_graph() -> UniversalKnowledgeGraph:
    """Get or create the global knowledge graph instance"""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = UniversalKnowledgeGraph()
    return _graph_instance




