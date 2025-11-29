"""
Logic Validator - Step-by-Step Reasoning Verification
======================================================

Validates the logical structure and reasoning flow:
- Checks if conclusions follow from premises
- Validates step-by-step problem-solving logic
- Detects logical fallacies and gaps
- Ensures reasoning consistency

Part of Layer 2: Symbolic Reasoning Layer.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LogicStatus(Enum):
    """Status of logic validation"""
    VALID = "valid"
    INVALID = "invalid"
    INCOMPLETE = "incomplete"
    UNCERTAIN = "uncertain"


@dataclass
class ReasoningStep:
    """A single step in the reasoning chain"""
    step_number: int
    content: str
    step_type: str  # premise, inference, conclusion
    depends_on: List[int]  # Previous steps this depends on
    is_valid: bool
    issues: List[str]


@dataclass
class LogicValidationResult:
    """Result of logic validation"""
    status: LogicStatus
    is_valid: bool
    confidence: float
    reasoning_chain: List[ReasoningStep]
    logical_gaps: List[Dict[str, Any]]
    fallacies_detected: List[str]
    completeness_score: float
    explanation: str


class LogicValidator:
    """
    Logic Validation Engine for Reasoning Verification
    
    Validates:
    - Premise-to-conclusion flow
    - Step-by-step reasoning integrity
    - Logical consistency
    - Completeness of explanations
    """
    
    # Common logical patterns
    STEP_INDICATORS = [
        r'step\s*\d+',
        r'first(ly)?[,:]',
        r'second(ly)?[,:]',
        r'third(ly)?[,:]',
        r'next[,:]',
        r'then[,:]',
        r'therefore[,:]',
        r'hence[,:]',
        r'thus[,:]',
        r'finally[,:]',
        r'so[,:]',
        r'because[,:]',
        r'since[,:]',
        r'given\s+that',
        r'it\s+follows\s+that',
        r'we\s+can\s+conclude',
    ]
    
    CONCLUSION_INDICATORS = [
        r'therefore',
        r'hence',
        r'thus',
        r'so\s+the\s+answer',
        r'the\s+result\s+is',
        r'we\s+get',
        r'finally',
        r'in\s+conclusion',
        r'the\s+solution\s+is',
        r'answer\s*[:=]',
    ]
    
    FALLACY_PATTERNS = {
        "circular_reasoning": [
            r'because\s+it\s+is',
            r'true\s+because\s+.*\s+true',
        ],
        "non_sequitur": [
            # Detected through step analysis
        ],
        "false_dichotomy": [
            r'either\s+.*\s+or\s+.*\s+only\s+two',
            r'only\s+option',
        ],
        "appeal_to_authority": [
            r'must\s+be\s+true\s+because\s+.*\s+said',
        ],
    }
    
    def __init__(self):
        """Initialize the Logic Validator"""
        logger.info("🧠 LogicValidator initialized - Reasoning validation active")
    
    def validate_reasoning(
        self,
        response_text: str,
        question: str,
        subject: str
    ) -> LogicValidationResult:
        """
        Validate the logical reasoning in a response.
        
        Args:
            response_text: The AI response to validate
            question: Original question for context
            subject: Subject area
            
        Returns:
            LogicValidationResult with detailed analysis
        """
        try:
            logger.info(f"🔍 Validating reasoning logic for: {question[:50]}...")
            
            # Step 1: Extract reasoning steps
            reasoning_chain = self._extract_reasoning_chain(response_text)
            
            if not reasoning_chain:
                return LogicValidationResult(
                    status=LogicStatus.UNCERTAIN,
                    is_valid=True,
                    confidence=0.5,
                    reasoning_chain=[],
                    logical_gaps=[],
                    fallacies_detected=[],
                    completeness_score=0.5,
                    explanation="No clear step-by-step reasoning detected."
                )
            
            # Step 2: Validate each step
            for step in reasoning_chain:
                self._validate_step(step, reasoning_chain)
            
            # Step 3: Check for logical gaps
            logical_gaps = self._detect_logical_gaps(reasoning_chain)
            
            # Step 4: Detect fallacies
            fallacies = self._detect_fallacies(response_text)
            
            # Step 5: Calculate completeness
            completeness = self._calculate_completeness(
                reasoning_chain, question, subject
            )
            
            # Step 6: Determine overall status
            valid_steps = sum(1 for s in reasoning_chain if s.is_valid)
            total_steps = len(reasoning_chain)
            
            if total_steps == 0:
                confidence = 0.5
            else:
                confidence = valid_steps / total_steps
            
            if len(fallacies) > 0:
                status = LogicStatus.INVALID
                is_valid = False
            elif len(logical_gaps) > 2:
                status = LogicStatus.INCOMPLETE
                is_valid = False
            elif confidence >= 0.8:
                status = LogicStatus.VALID
                is_valid = True
            else:
                status = LogicStatus.UNCERTAIN
                is_valid = True
            
            return LogicValidationResult(
                status=status,
                is_valid=is_valid,
                confidence=confidence,
                reasoning_chain=reasoning_chain,
                logical_gaps=logical_gaps,
                fallacies_detected=fallacies,
                completeness_score=completeness,
                explanation=self._generate_explanation(
                    status, logical_gaps, fallacies, completeness
                )
            )
            
        except Exception as e:
            logger.error(f"❌ Logic validation error: {e}", exc_info=True)
            return LogicValidationResult(
                status=LogicStatus.UNCERTAIN,
                is_valid=True,
                confidence=0.5,
                reasoning_chain=[],
                logical_gaps=[],
                fallacies_detected=[],
                completeness_score=0.5,
                explanation=f"Validation error: {str(e)}"
            )
    
    def validate_problem_solution(
        self,
        problem: str,
        solution_steps: List[str],
        final_answer: str,
        subject: str
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate a problem's solution steps lead to the answer.
        
        Args:
            problem: The problem statement
            solution_steps: List of solution steps
            final_answer: The claimed answer
            subject: Subject area
            
        Returns:
            Tuple of (is_valid, issues_list)
        """
        issues = []
        
        if not solution_steps:
            issues.append({
                "type": "missing_steps",
                "message": "No solution steps provided"
            })
            return False, issues
        
        # Check for minimum steps based on subject
        min_steps = {
            "mathematics": 2,
            "physics": 3,
            "chemistry": 2,
        }
        
        required_steps = min_steps.get(subject.lower(), 2)
        if len(solution_steps) < required_steps:
            issues.append({
                "type": "insufficient_steps",
                "message": f"Solution seems too brief. Expected at least {required_steps} steps for {subject}."
            })
        
        # Check that answer appears in final step
        if final_answer and final_answer.lower() not in solution_steps[-1].lower():
            issues.append({
                "type": "disconnected_answer",
                "message": "Final answer doesn't appear to follow from the last step"
            })
        
        return len(issues) == 0, issues
    
    def _extract_reasoning_chain(self, text: str) -> List[ReasoningStep]:
        """Extract the chain of reasoning steps from text"""
        steps = []
        
        # Split by common step patterns
        lines = text.split('\n')
        current_step = 0
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Check if this is a step
            is_step = False
            step_type = "inference"
            
            for pattern in self.STEP_INDICATORS:
                if re.search(pattern, line, re.IGNORECASE):
                    is_step = True
                    break
            
            # Check step type
            if re.search(r'(given|let|assume|consider)', line, re.IGNORECASE):
                step_type = "premise"
            elif any(re.search(p, line, re.IGNORECASE) for p in self.CONCLUSION_INDICATORS):
                step_type = "conclusion"
            
            if is_step or step_type == "conclusion":
                current_step += 1
                
                # Determine dependencies
                depends_on = []
                if current_step > 1:
                    # Simple heuristic: each step depends on previous
                    depends_on = [current_step - 1]
                    
                    # Check for explicit references
                    refs = re.findall(r'step\s*(\d+)', line, re.IGNORECASE)
                    if refs:
                        depends_on = [int(r) for r in refs if int(r) < current_step]
                
                steps.append(ReasoningStep(
                    step_number=current_step,
                    content=line,
                    step_type=step_type,
                    depends_on=depends_on,
                    is_valid=True,  # Will be updated by validation
                    issues=[]
                ))
        
        return steps
    
    def _validate_step(
        self,
        step: ReasoningStep,
        all_steps: List[ReasoningStep]
    ) -> None:
        """Validate a single reasoning step in context"""
        # Check if dependencies exist
        for dep in step.depends_on:
            if dep > len(all_steps) or dep < 1:
                step.is_valid = False
                step.issues.append(f"References non-existent step {dep}")
        
        # Check for logical connectors in inferences
        if step.step_type == "inference":
            has_connector = any(
                re.search(p, step.content, re.IGNORECASE)
                for p in [r'therefore', r'so', r'thus', r'because', r'since', r'hence']
            )
            if not has_connector and step.step_number > 1:
                step.issues.append("Inference lacks logical connector")
        
        # Check conclusion has support
        if step.step_type == "conclusion":
            if not step.depends_on:
                step.issues.append("Conclusion lacks supporting premises")
    
    def _detect_logical_gaps(
        self,
        reasoning_chain: List[ReasoningStep]
    ) -> List[Dict[str, Any]]:
        """Detect gaps in the logical chain"""
        gaps = []
        
        for i, step in enumerate(reasoning_chain[1:], 1):
            # Check if there's a large conceptual jump
            prev_step = reasoning_chain[i - 1]
            
            # Simple heuristic: if step content doesn't reference previous concepts
            prev_keywords = set(re.findall(r'\b\w{4,}\b', prev_step.content.lower()))
            curr_keywords = set(re.findall(r'\b\w{4,}\b', step.content.lower()))
            
            common_words = {'this', 'that', 'which', 'where', 'when', 'what', 'have', 'been', 'from', 'with'}
            prev_keywords -= common_words
            curr_keywords -= common_words
            
            overlap = len(prev_keywords & curr_keywords)
            
            if overlap < 1 and step.step_type != "conclusion":
                gaps.append({
                    "between_steps": [i, i + 1],
                    "type": "conceptual_jump",
                    "message": f"Possible missing step between step {i} and step {i+1}"
                })
        
        return gaps
    
    def _detect_fallacies(self, text: str) -> List[str]:
        """Detect logical fallacies in the text"""
        fallacies = []
        
        for fallacy_name, patterns in self.FALLACY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    fallacies.append(fallacy_name.replace('_', ' ').title())
                    break
        
        return fallacies
    
    def _calculate_completeness(
        self,
        reasoning_chain: List[ReasoningStep],
        question: str,
        subject: str
    ) -> float:
        """Calculate how complete the reasoning is"""
        if not reasoning_chain:
            return 0.0
        
        score = 0.0
        
        # Has premise?
        has_premise = any(s.step_type == "premise" for s in reasoning_chain)
        if has_premise:
            score += 0.25
        
        # Has conclusion?
        has_conclusion = any(s.step_type == "conclusion" for s in reasoning_chain)
        if has_conclusion:
            score += 0.25
        
        # Has intermediate steps?
        inference_count = sum(1 for s in reasoning_chain if s.step_type == "inference")
        if inference_count >= 1:
            score += 0.25
        if inference_count >= 2:
            score += 0.15
        
        # All steps valid?
        valid_ratio = sum(1 for s in reasoning_chain if s.is_valid) / len(reasoning_chain)
        score += 0.1 * valid_ratio
        
        return min(1.0, score)
    
    def _generate_explanation(
        self,
        status: LogicStatus,
        gaps: List[Dict],
        fallacies: List[str],
        completeness: float
    ) -> str:
        """Generate explanation of validation result"""
        if status == LogicStatus.VALID:
            return f"✅ Reasoning is logically valid with {completeness:.0%} completeness."
        elif status == LogicStatus.INCOMPLETE:
            return f"⚠️ Reasoning has {len(gaps)} logical gaps. Completeness: {completeness:.0%}"
        elif status == LogicStatus.INVALID:
            issues = []
            if fallacies:
                issues.append(f"Fallacies: {', '.join(fallacies)}")
            if gaps:
                issues.append(f"{len(gaps)} logical gaps")
            return f"❌ Reasoning issues detected: {'; '.join(issues)}"
        else:
            return f"❓ Unable to fully validate reasoning. Completeness: {completeness:.0%}"

