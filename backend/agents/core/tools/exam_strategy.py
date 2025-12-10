"""
🎯 Exam Strategy Tool - Replaces Exam Coach Agent
==================================================

Provides exam-specific insights: weightage, trap questions, shortcuts.
Used by ProfessorAgent when students ask for exam tips or strategies.
"""

import logging
from typing import Dict, Any, Optional, List
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


# High-quality mock data for exam strategies
# In production, this would come from a database
EXAM_STRATEGY_DATA = {
    "JEE": {
        "Rotational Motion": {
            "weightage_percent": 4.2,
            "common_traps": [
                "Confusing moment of inertia (I) with angular momentum (L)",
                "Forgetting to convert angular velocity to rad/s",
                "Mixing up parallel axis theorem and perpendicular axis theorem",
                "Not considering rolling without slipping condition properly"
            ],
            "shortcut_technique": "**Parallel Axis Theorem Shortcut**: For any object, I = I_cm + Md². Remember: 'cm' means center of mass. This saves time in JEE Main where they often ask about moment of inertia about different axes.",
            "ncert_relevance": "NCERT Class 11 Chapter 7 covers basics. JEE expects deeper application.",
            "pyq_pattern": "Usually 1-2 questions per paper. Often combined with energy conservation."
        },
        "Thermodynamics": {
            "weightage_percent": 5.8,
            "common_traps": [
                "Sign convention errors in ΔU = Q - W (remember: work done BY system is positive)",
                "Confusing isothermal vs adiabatic processes",
                "Not distinguishing between heat capacity at constant volume (Cv) vs constant pressure (Cp)",
                "Forgetting that ΔH = ΔU + PΔV only for constant pressure"
            ],
            "shortcut_technique": "**First Law Memory Trick**: ΔU = Q - W. Think: 'You (U) get energy (Q) but lose it doing work (W)'. For ideal gas, remember: Cv = 3R/2 (monoatomic), Cp = Cv + R. This helps solve 80% of thermodynamics problems quickly.",
            "ncert_relevance": "NCERT Class 11 Chapter 12. JEE requires deeper understanding of cyclic processes and efficiency.",
            "pyq_pattern": "2-3 questions per paper. Often involves PV diagrams and efficiency calculations."
        },
        "Organic Chemistry": {
            "weightage_percent": 12.5,
            "common_traps": [
                "Confusing SN1 vs SN2 mechanisms (SN1 = carbocation stability, SN2 = steric hindrance)",
                "Not recognizing resonance structures correctly",
                "Mixing up E1 vs E2 elimination conditions",
                "Forgetting about stereochemistry in reactions"
            ],
            "shortcut_technique": "**Reaction Mechanism Pattern**: SN2 = 'backside attack' (inversion), SN1 = 'racemization'. For JEE, focus on: (1) Carbocation stability order, (2) Leaving group ability (I > Br > Cl), (3) Nucleophile strength. This pattern solves most mechanism questions.",
            "ncert_relevance": "NCERT Class 12 Chapters 10-13. JEE expects mechanism understanding, not just memorization.",
            "pyq_pattern": "4-5 questions per paper. Often involves reaction mechanisms and product prediction."
        }
    },
    "NEET": {
        "Human Physiology": {
            "weightage_percent": 15.2,
            "common_traps": [
                "Confusing different types of blood cells and their functions",
                "Mixing up hormones and their target organs",
                "Not understanding the difference between systole and diastole",
                "Confusing nephron structure and function"
            ],
            "shortcut_technique": "**System-by-System Approach**: For NEET, memorize: (1) Heart = 4 chambers, (2) Lungs = gas exchange, (3) Kidneys = filtration. Focus on 'what happens where' rather than deep biochemistry. NCERT diagrams are gold - study them carefully.",
            "ncert_relevance": "NCERT Class 11 Chapter 17-18, Class 12 Chapter 16-18. NEET directly tests NCERT content.",
            "pyq_pattern": "6-8 questions per paper. Often involves diagram-based questions."
        },
        "Genetics": {
            "weightage_percent": 8.5,
            "common_traps": [
                "Confusing genotype vs phenotype",
                "Not understanding linkage and crossing over",
                "Mixing up Mendelian vs non-Mendelian inheritance",
                "Forgetting about sex-linked inheritance patterns"
            ],
            "shortcut_technique": "**Punnett Square Shortcut**: For monohybrid cross, always 3:1 ratio (dominant:recessive). For dihybrid, 9:3:3:1. For NEET, focus on: (1) Blood group inheritance, (2) Sex-linked traits (color blindness, hemophilia), (3) Pedigree analysis. Practice 10 pedigree problems daily.",
            "ncert_relevance": "NCERT Class 12 Chapter 5. NEET expects application, not just theory.",
            "pyq_pattern": "3-4 questions per paper. Often involves pedigree analysis and probability calculations."
        }
    },
    "CBSE": {
        "Electricity": {
            "weightage_percent": 8.0,
            "common_traps": [
                "Confusing series vs parallel resistance formulas",
                "Not understanding Kirchhoff's laws properly",
                "Mixing up AC vs DC concepts",
                "Forgetting about power dissipation in resistors"
            ],
            "shortcut_technique": "**Resistance Formula Memory**: Series = R1 + R2 (add them), Parallel = (R1×R2)/(R1+R2) for two resistors. For CBSE boards, focus on: (1) Ohm's law applications, (2) Power calculations (P = VI = I²R), (3) Circuit diagrams. NCERT numericals are important.",
            "ncert_relevance": "NCERT Class 10 Chapter 12, Class 12 Chapter 3. CBSE directly follows NCERT.",
            "pyq_pattern": "2-3 questions per paper. Often involves numerical problems."
        }
    }
}


class ExamStrategyTool(BaseTool):
    """
    Exam Strategy Tool - Provides exam-specific insights.
    
    Replaces the Exam Coach Agent functionality.
    Used by ProfessorAgent when students ask for exam tips, weightage, or strategies.
    """
    
    @property
    def name(self) -> str:
        return "exam_strategy"
    
    @property
    def description(self) -> str:
        return (
            "Provides exam-specific strategy information for JEE, NEET, or CBSE. "
            "Use this tool when students ask about: exam weightage, common trap questions, "
            "shortcut techniques, or exam-specific tips. DO NOT hallucinate exam data - "
            "always use this tool to get accurate information."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "topic": "The topic name (e.g., 'Rotational Motion', 'Thermodynamics', 'Organic Chemistry')",
            "exam_type": "Exam type: 'JEE' | 'NEET' | 'CBSE'"
        }
    
    async def execute(
        self,
        topic: str = "",
        exam_type: str = "JEE",
        context: Dict = None,
        **kwargs
    ) -> ToolResult:
        """
        Get exam strategy information for a topic.
        
        Args:
            topic: Topic name
            exam_type: JEE, NEET, or CBSE
        
        Returns:
            ToolResult with structured strategy information
        """
        if not topic:
            return ToolResult.error_result("Topic is required")
        
        exam_type = exam_type.upper()
        if exam_type not in ["JEE", "NEET", "CBSE"]:
            exam_type = "JEE"  # Default to JEE
            logger.warning(f"Invalid exam_type, defaulting to JEE")
        
        topic_normalized = topic.strip()
        
        # Search for topic in strategy data
        strategy_data = None
        exam_data = EXAM_STRATEGY_DATA.get(exam_type, {})
        
        # Try exact match first
        if topic_normalized in exam_data:
            strategy_data = exam_data[topic_normalized]
        else:
            # Try partial match (case-insensitive)
            topic_lower = topic_normalized.lower()
            for key, value in exam_data.items():
                if topic_lower in key.lower() or key.lower() in topic_lower:
                    strategy_data = value
                    topic_normalized = key  # Use the canonical name
                    break
        
        if not strategy_data:
            # Graceful degradation - return general advice
            logger.info(f"⚠️ No strategy data found for '{topic}' in {exam_type}. Returning general advice.")
            return ToolResult.success_result(
                f"**Exam Strategy for {topic} ({exam_type})**:\n\n"
                f"While I don't have specific data for '{topic}' in my database right now, here's general advice:\n\n"
                f"1. **Focus on NCERT**: {exam_type} questions are often based on NCERT concepts.\n"
                f"2. **Practice PYQs**: Previous year questions help identify patterns.\n"
                f"3. **Time Management**: Allocate time based on topic difficulty.\n"
                f"4. **Common Mistakes**: Always double-check units and sign conventions.\n\n"
                f"_Note: For specific weightage and trap questions, please check official exam analysis or ask your teacher._",
                metadata={"found": False, "topic": topic, "exam_type": exam_type}
            )
        
        # Format structured response
        output_parts = [
            f"**📊 Exam Strategy: {topic_normalized} ({exam_type})**\n",
            f"### Weightage",
            f"**{strategy_data['weightage_percent']}%** of {exam_type} questions come from this topic.\n",
            f"### Common Trap Questions",
        ]
        
        for i, trap in enumerate(strategy_data['common_traps'], 1):
            output_parts.append(f"{i}. {trap}")
        
        output_parts.extend([
            f"\n### 🎯 Shortcut Technique",
            strategy_data['shortcut_technique'],
            f"\n### 📚 NCERT Relevance",
            strategy_data['ncert_relevance'],
            f"\n### 📈 PYQ Pattern",
            strategy_data['pyq_pattern']
        ])
        
        output = "\n".join(output_parts)
        
        logger.info(f"🎯 Exam strategy retrieved: {topic_normalized} ({exam_type})")
        
        return ToolResult.success_result(
            output,
            metadata={
                "found": True,
                "topic": topic_normalized,
                "exam_type": exam_type,
                "weightage": strategy_data['weightage_percent']
            }
        )

