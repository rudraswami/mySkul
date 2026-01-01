"""
🛡️ Guardrails v2 - Content Validation & Safety System
=======================================================

Production-grade guardrails for ensuring:
- Accuracy (no hallucinations when grounding weak)
- Grounding (claims supported by citations)
- Safety (emotional crisis handling)
- Exam Integrity (teach-instead mode for cheating)

ARCHITECTURE:
1. ResponseEnvelope - Internal contract for guardrail processing
2. RetrievalRepair - Auto-retrieve when citations weak
3. GroundingVerifier - Claim-level validation
4. SafetyGuard - Emotional/crisis detection
5. ExamIntegrityChecker - Cheating detection
6. GuardrailsEngine - Central orchestrator

INSERTION POINT: UnifiedAIOrchestrator.process() before return

NO CHANGES TO:
- External API schemas
- Tool names or outputs
- Agent behavior
"""

import logging
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

# Environment flag for debug logging
GUARDRAILS_DEBUG = os.getenv("GUARDRAILS_DEBUG", "false").lower() == "true"


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class GuardrailStatus(Enum):
    """Guardrail decision status"""
    PASS = "pass"
    SOFT_BLOCK = "soft_block"  # Revise to supported-only
    HARD_BLOCK = "hard_block"  # No factual answer, teach basics


class GuardrailAction(Enum):
    """Actions taken by guardrails"""
    NONE = "none"
    REVISE_TO_SUPPORTED = "revise_to_supported"
    ADD_UNCERTAINTY_NOTES = "add_uncertainty_notes"
    ASK_CLARIFY = "ask_clarify"
    TEACH_BASICS = "teach_basics"
    RETRIEVAL_RETRY = "retrieval_retry"
    CRISIS_SUPPORT = "crisis_support"
    TEACH_INSTEAD = "teach_instead"
    SOCRATIC_MODE = "socratic_mode"


class RiskFlag(Enum):
    """Risk flags detected"""
    CHEATING = "cheating"
    SELF_HARM_INSTRUCTION = "self_harm_instruction"  # Method-seeking (HARD_BLOCK)
    SELF_HARM_IDEATION = "self_harm_ideation"  # Hopelessness (crisis_support)
    UNSAFE = "unsafe"
    LOW_GROUNDING = "low_grounding"
    SEVERE_DISTRESS = "severe_distress"
    NORMAL_STRESS = "normal_stress"  # Supportive coaching


class SafetySeverity(Enum):
    """Safety severity tiers"""
    TIER_A_INSTRUCTION = "tier_a_instruction"  # Method-seeking → HARD_BLOCK
    TIER_B_IDEATION = "tier_b_ideation"  # Hopelessness → crisis_support
    TIER_C_STRESS = "tier_c_stress"  # Normal stress → supportive coaching
    NONE = "none"


# Thresholds
GROUNDING_PASS_THRESHOLD = 0.75
GROUNDING_SOFT_BLOCK_THRESHOLD = 0.45
RETRIEVAL_CONFIDENCE_THRESHOLD = 0.55
MAX_RETRIEVAL_RETRIES = 2
MAX_CLAIMS_TO_CHECK = 6  # Reduced from 8 for bounded processing


# =============================================================================
# RESPONSE ENVELOPE (Internal Contract)
# =============================================================================

@dataclass
class RetrievalContext:
    """Single retrieved context with citation info"""
    chunk_id: str
    doc_id: str
    section: str
    text_snippet: str
    score: float
    source_file: Optional[str] = None


@dataclass
class ResponseEnvelope:
    """
    Internal response contract for guardrail processing.
    
    This is NOT exposed to the external API - only used internally
    for guardrail validation and metadata tracking.
    """
    # Input
    user_message: str
    agent_name: str
    route_type: str
    
    # Draft/Final
    draft_answer: str
    final_answer: str = ""
    
    # Retrieval data
    retrieval_contexts: List[RetrievalContext] = field(default_factory=list)
    retrieval_confidence: float = 0.0
    retrieval_method: str = "unknown"
    
    # Grounding
    claims_extracted: List[str] = field(default_factory=list)
    claims_supported: List[str] = field(default_factory=list)
    claims_unsupported: List[str] = field(default_factory=list)
    claim_support_rate: float = 0.0
    
    # Risk assessment
    risk_flags: List[RiskFlag] = field(default_factory=list)
    
    # Guardrail decision
    guardrail_status: GuardrailStatus = GuardrailStatus.PASS
    guardrail_actions: List[GuardrailAction] = field(default_factory=list)
    
    # Metadata
    request_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    retrieval_retries: int = 0
    
    def get_citations(self) -> List[Dict[str, str]]:
        """Get citations in standard format"""
        return [
            {
                "doc_id": ctx.doc_id,
                "chunk_id": ctx.chunk_id,
                "section": ctx.section
            }
            for ctx in self.retrieval_contexts
        ]
    
    def to_log_dict(self) -> Dict[str, Any]:
        """
        Convert to loggable dictionary.
        
        OBSERVABILITY REQUIREMENTS (complete per-request logging):
        - guardrail_status, actions_taken
        - is_self_harm_instruction, is_self_harm_ideation, severity
        - cheating_detected + mode
        - support_rate, citations_count
        - retrieval_method before/after repair
        """
        # Detect safety flags
        is_self_harm_instruction = RiskFlag.SELF_HARM_INSTRUCTION in self.risk_flags
        is_self_harm_ideation = RiskFlag.SELF_HARM_IDEATION in self.risk_flags
        cheating_detected = RiskFlag.CHEATING in self.risk_flags
        
        # Determine severity
        if is_self_harm_instruction:
            severity = "tier_a_instruction"
        elif is_self_harm_ideation:
            severity = "tier_b_ideation"
        elif RiskFlag.SEVERE_DISTRESS in self.risk_flags:
            severity = "tier_b_distress"
        elif RiskFlag.NORMAL_STRESS in self.risk_flags:
            severity = "tier_c_stress"
        else:
            severity = "none"
        
        return {
            "request_id": self.request_id,
            "agent_name": self.agent_name,
            "route_type": self.route_type,
            # Retrieval
            "retrieval_method": self.retrieval_method,
            "citations_count": len(self.retrieval_contexts),
            "retrieval_confidence": round(self.retrieval_confidence, 3),
            "retrieval_retries": self.retrieval_retries,
            # Grounding
            "claim_support_rate": round(self.claim_support_rate, 3),
            "claims_extracted": len(self.claims_extracted),
            "unsupported_claims_count": len(self.claims_unsupported),
            # Guardrail decision
            "guardrail_status": self.guardrail_status.value,
            "guardrail_actions": [a.value for a in self.guardrail_actions],
            # Safety (explicit flags)
            "is_self_harm_instruction": is_self_harm_instruction,
            "is_self_harm_ideation": is_self_harm_ideation,
            "severity": severity,
            # Exam integrity
            "cheating_detected": cheating_detected,
            "cheating_mode": "teach_instead" if cheating_detected else None,
            # Risk summary
            "risk_flags": [f.value for f in self.risk_flags],
        }


# =============================================================================
# SAFETY GUARD (Emotional/Crisis Detection) - CORRECT TIERED POLICY
# =============================================================================

@dataclass
class SafetyCheckResult:
    """Result of safety check with explicit flags"""
    risk_flags: List[RiskFlag]
    severity: SafetySeverity
    is_self_harm_instruction: bool  # Method-seeking
    is_self_harm_ideation: bool  # Hopelessness/suicidal thoughts
    recommended_action: Optional[GuardrailAction]
    recommended_status: GuardrailStatus


class SafetyGuard:
    """
    Detects emotional distress and safety concerns.
    
    POLICY TIERS (CRITICAL):
    A) self_harm_instruction (method-seeking) → HARD_BLOCK + refuse instructions
    B) self_harm_ideation (hopelessness) → crisis_support_mode (supportive, NOT refusal)
    C) normal_stress → supportive coaching (PASS or SOFT_BLOCK)
    
    Uses deterministic policy table - NO LLM guessing for safety.
    """
    
    # TIER A: Self-harm INSTRUCTION patterns (method-seeking) → HARD_BLOCK
    # These request HOW to harm - must refuse and redirect
    INSTRUCTION_PATTERNS = [
        r'\b(how\s+to|ways?\s+to|methods?\s+to)\s+(kill|hurt|harm|end)\s+(myself|my\s+life|it\s+all)\b',
        r'\b(best\s+way|easiest\s+way|quickest\s+way)\s+to\s+(die|end\s+it|hurt\s+myself)\b',
        r'\b(tell\s+me\s+how|show\s+me\s+how)\s+to\s+(die|hurt|harm|cut)\b',
        r'\b(where\s+to\s+get|how\s+to\s+get)\s+(pills|drugs|poison)\s+to\s+(die|end)\b',
        r'\b(help\s+me\s+(die|end\s+it|hurt\s+myself))\b',
    ]
    
    # TIER B: Self-harm IDEATION patterns (hopelessness) → crisis_support
    # These express feelings - respond with empathy and encourage reaching out
    IDEATION_PATTERNS = [
        r'\b(want\s+to\s+die|wanna\s+die|wish\s+I\s+was\s+dead)\b',
        r'\b(kill\s+myself|end\s+my\s+life|suicidal|suicide)\b',
        r'\b(no\s+point|no\s+reason\s+to\s+live|better\s+off\s+dead)\b',
        r'\b(give\s+up\s+on\s+life|can\'t\s+go\s+on|ending\s+it\s+all)\b',
        r'\b(want\s+to\s+hurt\s+myself|cut\s+myself|self[-\s]?harm)\b',
        r'\b(don\'t\s+want\s+to\s+be\s+here|don\'t\s+want\s+to\s+exist)\b',
    ]
    
    # TIER B (lower): Severe distress (no explicit self-harm mention) → crisis_support
    DISTRESS_PATTERNS = [
        r'\b(completely\s+)?(hopeless|worthless|useless)\b',
        r'\b(nobody\s+cares|no\s+one\s+cares|all\s+alone|completely\s+alone)\b',
        r'\b(ruined\s+my\s+life|life\s+is\s+over|can\'t\s+cope)\b',
        r'\b(hate\s+myself|disgusted\s+with\s+myself|despise\s+myself)\b',
        r'\b(i\s+give\s+up|giving\s+up\s+on\s+everything)\b',
    ]
    
    # TIER C: Normal stress/anxiety → supportive coaching (PASS with empathy)
    STRESS_PATTERNS = [
        r'\b(stressed|overwhelmed|too\s+much\s+pressure)\b',
        r'\b(can\'t\s+study|can\'t\s+focus|brain\s+fog)\b',
        r'\b(scared\s+of\s+exam|terrified|freaking\s+out)\b',
        r'\b(disappointed|let\s+everyone\s+down|failed)\b',
        r'\b(anxious|nervous|worried)\s+(about|for)\b',
        r'\b(so\s+tired|exhausted|burned\s+out|burnt\s+out)\b',
    ]
    
    def __init__(self):
        self._instruction_re = [re.compile(p, re.IGNORECASE) for p in self.INSTRUCTION_PATTERNS]
        self._ideation_re = [re.compile(p, re.IGNORECASE) for p in self.IDEATION_PATTERNS]
        self._distress_re = [re.compile(p, re.IGNORECASE) for p in self.DISTRESS_PATTERNS]
        self._stress_re = [re.compile(p, re.IGNORECASE) for p in self.STRESS_PATTERNS]
    
    def check(self, message: str, context: Dict = None) -> SafetyCheckResult:
        """
        Check message for safety concerns with explicit tier classification.
        
        Returns:
            SafetyCheckResult with explicit flags and severity
        """
        context = context or {}
        request_id = context.get('request_id', 'unknown')
        
        # === TIER A: Self-harm INSTRUCTION (method-seeking) → HARD_BLOCK ===
        for pattern in self._instruction_re:
            if pattern.search(message):
                logger.warning(f"🚨 SAFETY TIER-A: Self-harm instruction detected | request_id={request_id}")
                return SafetyCheckResult(
                    risk_flags=[RiskFlag.SELF_HARM_INSTRUCTION],
                    severity=SafetySeverity.TIER_A_INSTRUCTION,
                    is_self_harm_instruction=True,
                    is_self_harm_ideation=False,
                    recommended_action=GuardrailAction.CRISIS_SUPPORT,
                    recommended_status=GuardrailStatus.HARD_BLOCK
                )
        
        # === TIER B: Self-harm IDEATION (hopelessness) → crisis_support ===
        for pattern in self._ideation_re:
            if pattern.search(message):
                logger.warning(f"⚠️ SAFETY TIER-B: Self-harm ideation detected | request_id={request_id}")
                return SafetyCheckResult(
                    risk_flags=[RiskFlag.SELF_HARM_IDEATION],
                    severity=SafetySeverity.TIER_B_IDEATION,
                    is_self_harm_instruction=False,
                    is_self_harm_ideation=True,
                    recommended_action=GuardrailAction.CRISIS_SUPPORT,
                    recommended_status=GuardrailStatus.SOFT_BLOCK
                )
        
        # === TIER B (lower): Severe distress → crisis_support ===
        for pattern in self._distress_re:
            if pattern.search(message):
                logger.info(f"⚠️ SAFETY TIER-B: Severe distress detected | request_id={request_id}")
                return SafetyCheckResult(
                    risk_flags=[RiskFlag.SEVERE_DISTRESS],
                    severity=SafetySeverity.TIER_B_IDEATION,
                    is_self_harm_instruction=False,
                    is_self_harm_ideation=True,
                    recommended_action=GuardrailAction.CRISIS_SUPPORT,
                    recommended_status=GuardrailStatus.SOFT_BLOCK
                )
        
        # === TIER C: Normal stress → supportive coaching (PASS) ===
        for pattern in self._stress_re:
            if pattern.search(message):
                logger.info(f"💙 SAFETY TIER-C: Normal stress detected | request_id={request_id}")
                return SafetyCheckResult(
                    risk_flags=[RiskFlag.NORMAL_STRESS],
                    severity=SafetySeverity.TIER_C_STRESS,
                    is_self_harm_instruction=False,
                    is_self_harm_ideation=False,
                    recommended_action=None,  # Let normal flow handle with empathy
                    recommended_status=GuardrailStatus.PASS
                )
        
        # No safety concern detected
        return SafetyCheckResult(
            risk_flags=[],
            severity=SafetySeverity.NONE,
            is_self_harm_instruction=False,
            is_self_harm_ideation=False,
            recommended_action=None,
            recommended_status=GuardrailStatus.PASS
        )
    
    def get_crisis_response(self, safety_result: SafetyCheckResult) -> str:
        """
        Get appropriate response based on safety tier.
        
        CRITICAL:
        - TIER A (instruction): Refuse + redirect to help
        - TIER B (ideation): Supportive + encourage reaching out (NOT refusal tone)
        - TIER C (stress): Supportive coaching
        """
        if safety_result.severity == SafetySeverity.TIER_A_INSTRUCTION:
            # HARD_BLOCK - Refuse instructions, provide crisis resources
            return (
                "I can't help with that, but I really care about you. 💙\n\n"
                "What you're feeling right now matters, and there are people who want to help:\n\n"
                "**Please reach out right now:**\n"
                "📞 Talk to a parent, teacher, or trusted adult\n"
                "📞 Crisis helplines are available 24/7 (search for your country's helpline)\n"
                "📞 Text a crisis line if calling feels too hard\n\n"
                "You don't have to face this alone. Will you reach out to someone?"
            )
        
        elif safety_result.severity == SafetySeverity.TIER_B_IDEATION:
            # crisis_support - Supportive, encourage reaching out (NOT refusal tone)
            return (
                "I hear you, and I want you to know that your feelings matter. 💙\n\n"
                "What you're going through sounds really hard. It takes courage to express how you feel.\n\n"
                "**You don't have to face this alone:**\n"
                "- Please talk to someone you trust - a parent, teacher, friend, or counselor\n"
                "- Crisis helplines are available 24/7 if you need someone to listen\n"
                "- Even texting a friend can help right now\n\n"
                "I'm here for your studies whenever you're ready, but right now, "
                "please reach out to a real person who can support you. 🤝"
            )
        
        elif safety_result.severity == SafetySeverity.TIER_C_STRESS:
            # Supportive coaching - empathy + micro-steps
            return (
                "I can sense you're going through a tough time. That's really hard, "
                "and it's okay to feel this way - especially with exam pressure.\n\n"
                "**Here's what might help:**\n"
                "- Take a short break (even 5 minutes helps)\n"
                "- Talk to someone you trust about how you're feeling\n"
                "- Break your task into tiny, manageable steps\n\n"
                "When you're ready, let's tackle one small thing together. "
                "What's the ONE topic you'd like to start with? 💪"
            )
        
        # Default supportive
        return (
            "I'm here for you. Let me know how I can help with your studies, "
            "or if you just need to talk about what you're going through. 💙"
        )


# =============================================================================
# EXAM INTEGRITY CHECKER (Cheating Detection)
# =============================================================================

class ExamIntegrityChecker:
    """
    Detects cheating/assessment context and enforces teach-instead policy.
    
    RULES:
    - HARD_BLOCK: Direct answers for assessment submission
    - TEACH_INSTEAD: Method + guided steps + practice (DYNAMIC, not template)
    - ALLOW: "Check my work", "Explain why option B"
    
    DYNAMIC RESPONSE REQUIREMENTS:
    - Give method + 1-2 guided steps
    - Ask for student's attempt
    - Provide 1-2 similar practice questions
    - NEVER give "answers-only / final option only"
    """
    
    # Cheating indicators
    CHEATING_PATTERNS = [
        # Direct answer demands
        r'\b(give me|just give|only give|tell me)\s+(the\s+)?(answers?|solutions?|options?)\b',
        r'\b(answers?\s+only|solutions?\s+only|just\s+the\s+answers?)\b',
        r'\b(solve\s+this|solve\s+these)\s+(whole\s+)?(paper|test|exam|quiz|assignment)\b',
        r'\b(complete\s+my|do\s+my|finish\s+my)\s+(assignment|homework|project|paper)\b',
        
        # MCQ answer demands (CRITICAL: no final options)
        r'\b(give|tell)\s+(me\s+)?(only\s+)?(the\s+)?(correct\s+)?(option|answer)\b',
        r'\b(which\s+option|what\s+option)\s+is\s+(correct|right|the\s+answer)\b',
        r'\b(option\s+[a-d])\s+(is\s+)?(correct|right)\s*\?\s*$',
        
        # Assessment context with urgency
        r'\b(exam|test|quiz)\s+(is\s+)?(now|right now|ongoing|happening)\b',
        r'\b(during\s+exam|in\s+exam|exam\s+time)\b',
        r'\b(urgent|hurry|quick|fast)\b.{0,30}\b(answer|solve)\b',
        
        # Paper/section solving
        r'\b(section\s+[a-d]|part\s+[a-d]|question\s+\d+)\b.{0,20}\b(answer|solve)\b',
        
        # Assignment writing
        r'\b(write\s+my|write\s+this)\s+(essay|assignment|report|paper)\b',
    ]
    
    # Allowed patterns (teaching emphasis) - check FIRST
    TEACHING_PATTERNS = [
        r'\b(check\s+my|verify\s+my|review\s+my)\s+(work|attempt|solution|answer)\b',
        r'\b(explain\s+why|why\s+is)\s+(option\s+[a-d]|this\s+correct|this\s+wrong)\b',
        r'\b(here\s+is\s+my\s+attempt|this\s+is\s+my\s+solution|i\s+tried)\b',
        r'\b(how\s+to\s+solve|method|approach|concept|understand)\b',
        r'\b(practice|example|similar\s+question)\b',
        r'\b(step\s+by\s+step|derivation|proof)\b',
        r'\b(is\s+my\s+answer\s+correct|did\s+i\s+get\s+it\s+right)\b',
    ]
    
    def __init__(self):
        self._cheating_re = [re.compile(p, re.IGNORECASE) for p in self.CHEATING_PATTERNS]
        self._teaching_re = [re.compile(p, re.IGNORECASE) for p in self.TEACHING_PATTERNS]
    
    def check(self, message: str, context: Dict = None) -> Tuple[bool, Optional[GuardrailAction]]:
        """
        Check for cheating/assessment context.
        
        Returns:
            (is_cheating, recommended_action)
        """
        # First check if it's clearly a teaching request (ALLOW)
        for pattern in self._teaching_re:
            if pattern.search(message):
                logger.info(f"🎓 EXAM INTEGRITY: Teaching request detected - ALLOWED")
                return False, None  # Teaching request, allow
        
        # Check for cheating indicators
        for pattern in self._cheating_re:
            if pattern.search(message):
                logger.info(f"🎓 EXAM INTEGRITY: Cheating pattern detected - TEACH_INSTEAD")
                return True, GuardrailAction.TEACH_INSTEAD
        
        return False, None
    
    def get_teach_instead_response(self, original_query: str, subject: str = None) -> str:
        """
        Generate DYNAMIC teach-instead response (NOT template-y).
        
        REQUIREMENTS:
        - Give method + 1-2 guided steps
        - Ask for student's attempt
        - Provide 1-2 similar practice questions
        - NEVER give final answers/options
        """
        # Extract topic hints from query
        query_lower = original_query.lower()
        
        # Detect question type for dynamic response
        is_mcq = any(x in query_lower for x in ['mcq', 'option', 'multiple choice', 'a)', 'b)', 'c)', 'd)'])
        is_numerical = any(x in query_lower for x in ['calculate', 'find', 'solve', 'value'])
        is_conceptual = any(x in query_lower for x in ['explain', 'why', 'how', 'what is'])
        
        # Build dynamic response based on question type
        if is_mcq:
            return self._get_mcq_teach_response(subject)
        elif is_numerical:
            return self._get_numerical_teach_response(subject)
        else:
            return self._get_conceptual_teach_response(subject)
    
    def _get_mcq_teach_response(self, subject: str = None) -> str:
        """Dynamic response for MCQ-type cheating attempts"""
        subject_hint = f" in {subject}" if subject else ""
        return (
            f"I can see you're working on a multiple choice question{subject_hint}! "
            "Let me help you actually understand it 🎯\n\n"
            "**Here's the approach:**\n"
            "1. **Read carefully** - What concept is being tested?\n"
            "2. **Eliminate wrong options** - Which ones don't fit the concept?\n"
            "3. **Verify your choice** - Can you explain WHY it's correct?\n\n"
            "**Your turn:** Look at the question and tell me:\n"
            "- What topic/concept does this relate to?\n"
            "- Which option(s) can you eliminate and why?\n\n"
            "**Practice:** Try solving: *If you understand the concept, create your own MCQ "
            "on the same topic!*\n\n"
            "Share your reasoning, and I'll guide you to the right understanding! 💪"
        )
    
    def _get_numerical_teach_response(self, subject: str = None) -> str:
        """Dynamic response for numerical problem cheating attempts"""
        subject_hint = f" in {subject}" if subject else ""
        return (
            f"I can see you're working on a problem{subject_hint}! "
            "Let's solve it together, step by step 🧮\n\n"
            "**Here's how to approach it:**\n"
            "1. **Identify** - What are the given quantities? What do you need to find?\n"
            "2. **Choose the right formula** - What relationship applies here?\n"
            "3. **Substitute and solve** - Put in the values carefully\n\n"
            "**Your turn:** Start by:\n"
            "- Writing down what's given\n"
            "- Writing what you need to find\n"
            "- Choosing which formula might help\n\n"
            "**Similar practice:** After we solve this, try a similar problem with different numbers!\n\n"
            "Show me your first step, and I'll guide you from there! ✏️"
        )
    
    def _get_conceptual_teach_response(self, subject: str = None) -> str:
        """Dynamic response for conceptual question cheating attempts"""
        subject_hint = f" in {subject}" if subject else ""
        return (
            f"Let me help you understand this{subject_hint}.\n\n"
            "To give you the clearest explanation, tell me:\n"
            "- What do you already know about this?\n"
            "- What specific part is unclear?\n\n"
            "**Practice:** After understanding, try explaining it back to me in your own words!\n\n"
            "This way, you'll really remember it for your exam. What part should we start with? 🎓"
        )


# =============================================================================
# GROUNDING VERIFIER (Claim-Level Validation)
# =============================================================================

class GroundingVerifier:
    """
    Verifies that factual claims are supported by retrieved contexts.
    
    BOUNDED & DETERMINISTIC:
    - Max claims: 6 (enforced)
    - Support scoring: lexical overlap + embedding similarity (primary)
    - NO LLM judge (cost + latency)
    - NEVER invent citations: must be from corpus store
    
    THRESHOLDS (ENFORCED):
    - support_rate >= 0.75 → PASS
    - 0.45-0.75 → SOFT_BLOCK (revise + uncertainty notes)
    - < 0.45 → HARD_BLOCK (ask clarify / teach basics, NO factual claims)
    """
    
    def __init__(self):
        self._embedding_service = None
    
    async def _get_embedding_service(self):
        """Lazy load embedding service for similarity checks"""
        if self._embedding_service is None:
            try:
                from lightweight_embeddings import get_embedding_service
                self._embedding_service = await get_embedding_service()
            except Exception as e:
                logger.warning(f"Embedding service not available for grounding: {e}")
        return self._embedding_service
    
    def extract_claims(self, text: str) -> List[str]:
        """
        Extract atomic factual claims from text.
        
        BOUNDED: Max 6 claims (enforced by MAX_CLAIMS_TO_CHECK)
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        claims = []
        factual_indicators = [
            r'\b(is|are|was|were|has|have|had)\b',
            r'\b(equals?|equal to)\b',
            r'\b(defined as|known as|called)\b',
            r'\b(formula|equation|law|principle|theorem)\b',
            r'\b(\d+(?:\.\d+)?)\s*(kg|m|s|N|J|W|V|A|Hz|mol|°C|K)\b',  # Units
            r'\b(always|never|must|cannot|causes?|results?\s+in)\b',
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10 or len(sentence) > 300:  # Skip too short/long
                continue
            
            # Skip non-factual sentences (questions, commands, etc.)
            if sentence.endswith('?') or sentence.startswith(('Let', 'Try', 'Would', 'Could')):
                continue
            
            # Check if sentence contains factual indicators
            for pattern in factual_indicators:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence)
                    break
            
            # ENFORCED CAP
            if len(claims) >= MAX_CLAIMS_TO_CHECK:
                break
        
        return claims[:MAX_CLAIMS_TO_CHECK]  # Double-ensure cap
    
    async def verify_claims(
        self, 
        claims: List[str], 
        contexts: List[RetrievalContext]
    ) -> Tuple[List[str], List[str], float]:
        """
        Verify claims against retrieved contexts.
        
        DETERMINISTIC SCORING:
        1. Lexical overlap (word match)
        2. Key term presence
        3. Optional: embedding similarity (if service available)
        
        CRITICAL: Citations MUST be from contexts (doc_id + chunk_id + section).
        NEVER invent or fabricate citations.
        
        Returns:
            (supported_claims, unsupported_claims, support_rate)
        """
        if not claims:
            return [], [], 1.0  # No claims = fully supported
        
        if not contexts:
            return [], claims, 0.0  # No contexts = nothing supported
        
        # Validate contexts have required fields (no fake citations)
        valid_contexts = [
            ctx for ctx in contexts 
            if ctx.chunk_id and ctx.doc_id and ctx.text_snippet
        ]
        
        if not valid_contexts:
            logger.warning("⚠️ No valid contexts with chunk_id/doc_id - cannot verify claims")
            return [], claims, 0.0
        
        # Combine context texts for matching
        context_text = " ".join([ctx.text_snippet for ctx in valid_contexts]).lower()
        context_words = set(re.findall(r'\b\w{4,}\b', context_text))
        
        supported = []
        unsupported = []
        
        for claim in claims[:MAX_CLAIMS_TO_CHECK]:  # Enforce cap
            claim_lower = claim.lower()
            
            # Extract substantive words from claim
            claim_words = set(re.findall(r'\b\w{4,}\b', claim_lower))
            
            if not claim_words:
                supported.append(claim)  # No substantial words to check
                continue
            
            # === LEXICAL OVERLAP ===
            word_overlap = len(claim_words & context_words) / len(claim_words)
            
            # === KEY TERM PRESENCE ===
            # Check for important terms (numbers, proper nouns, technical terms)
            key_terms = set(re.findall(r'\b[A-Z][a-z]+|\b\d+(?:\.\d+)?', claim))
            key_terms_lower = {t.lower() for t in key_terms}
            key_match = sum(1 for t in key_terms_lower if t in context_text)
            key_ratio = key_match / len(key_terms) if key_terms else 1.0
            
            # === COMBINED SCORE (deterministic) ===
            # Weight: 60% lexical overlap, 40% key terms
            support_score = 0.6 * word_overlap + 0.4 * key_ratio
            
            # Threshold for support: 0.4 (must match at least 40% of claim)
            if support_score >= 0.4:
                supported.append(claim)
            else:
                unsupported.append(claim)
        
        support_rate = len(supported) / len(claims) if claims else 1.0
        
        logger.debug(f"📊 Grounding: {len(supported)}/{len(claims)} claims supported "
                    f"(rate={support_rate:.2f})")
        
        return supported, unsupported, support_rate
    
    def get_grounding_decision(self, support_rate: float) -> GuardrailStatus:
        """
        Get guardrail decision based on support rate.
        
        THRESHOLDS (ENFORCED):
        - >= 0.75 → PASS
        - 0.45-0.75 → SOFT_BLOCK
        - < 0.45 → HARD_BLOCK
        """
        if support_rate >= GROUNDING_PASS_THRESHOLD:
            return GuardrailStatus.PASS
        elif support_rate >= GROUNDING_SOFT_BLOCK_THRESHOLD:
            return GuardrailStatus.SOFT_BLOCK
        else:
            return GuardrailStatus.HARD_BLOCK
    
    def get_valid_citations(self, contexts: List[RetrievalContext]) -> List[Dict[str, str]]:
        """
        Get citations ONLY from valid contexts.
        
        CRITICAL: Never invent citations. Must have:
        - doc_id (from corpus)
        - chunk_id (from corpus)
        - section (from corpus)
        """
        return [
            {
                "doc_id": ctx.doc_id,
                "chunk_id": ctx.chunk_id,
                "section": ctx.section
            }
            for ctx in contexts
            if ctx.doc_id and ctx.chunk_id  # Must have valid IDs
        ]


# =============================================================================
# RETRIEVAL REPAIR (Auto-Retrieve on Fail)
# =============================================================================

class RetrievalRepair:
    """
    Attempts to improve retrieval when initial results are weak.
    
    TRIGGERS:
    - citations_count == 0 for factual queries
    - retrieval_confidence < threshold
    - draft contains factual assertions but lacks support
    """
    
    def __init__(self):
        self._retriever = None
    
    def _get_retriever(self):
        """Lazy load retriever"""
        if self._retriever is None:
            try:
                from services.knowledge_base.retriever_v2 import get_retriever_v2
                self._retriever = get_retriever_v2()
            except Exception as e:
                logger.error(f"Failed to load retriever for repair: {e}")
        return self._retriever
    
    def should_repair(self, envelope: ResponseEnvelope) -> bool:
        """Check if retrieval repair is needed"""
        # Already retried enough
        if envelope.retrieval_retries >= MAX_RETRIEVAL_RETRIES:
            return False
        
        # No citations for what looks like a factual query
        if not envelope.retrieval_contexts and self._is_factual_query(envelope.user_message):
            return True
        
        # Low confidence
        if envelope.retrieval_confidence < RETRIEVAL_CONFIDENCE_THRESHOLD:
            return True
        
        # Low grounding
        if envelope.claim_support_rate < GROUNDING_SOFT_BLOCK_THRESHOLD:
            return True
        
        return False
    
    def _is_factual_query(self, message: str) -> bool:
        """Check if query expects factual information"""
        factual_patterns = [
            r'\b(what is|what are|define|explain|describe)\b',
            r'\b(formula|equation|law|theorem|principle)\b',
            r'\b(how does|why does|when did)\b',
            r'\b(calculate|find|solve|derive)\b',
        ]
        
        for pattern in factual_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    def generate_repair_queries(self, original_query: str, subject: str = None) -> List[str]:
        """
        Generate alternative queries for retry.
        
        Strategies:
        - Add subject context
        - Add synonyms
        - Simplify query
        """
        queries = []
        
        # Add subject if known
        if subject and subject.lower() != "general":
            queries.append(f"{subject} {original_query}")
        
        # Extract key terms
        key_terms = re.findall(r'\b\w{4,}\b', original_query.lower())
        if key_terms:
            # Try just key terms
            queries.append(" ".join(key_terms[:3]))
        
        # Add educational context
        queries.append(f"explain concept {original_query}")
        
        return queries[:3]  # Max 3 queries
    
    async def repair(self, envelope: ResponseEnvelope, subject: str = None) -> List[RetrievalContext]:
        """
        Attempt retrieval repair with alternative queries.
        
        Returns improved contexts (or empty if failed).
        """
        retriever = self._get_retriever()
        if retriever is None:
            return []
        
        repair_queries = self.generate_repair_queries(envelope.user_message, subject)
        
        all_contexts = []
        
        for query in repair_queries:
            try:
                result = retriever.retrieve_knowledge(query, subject, max_results=3)
                
                for r in result.results:
                    ctx = RetrievalContext(
                        chunk_id=r.get("chunk_id", ""),
                        doc_id=r.get("doc_id", ""),
                        section=r.get("section", ""),
                        text_snippet=r.get("content", "")[:500],
                        score=r.get("score", 0.0),
                        source_file=r.get("raw_file")
                    )
                    all_contexts.append(ctx)
            except Exception as e:
                logger.warning(f"Repair query failed: {query} - {e}")
        
        # Deduplicate by chunk_id
        seen = set()
        unique_contexts = []
        for ctx in all_contexts:
            if ctx.chunk_id not in seen:
                seen.add(ctx.chunk_id)
                unique_contexts.append(ctx)
        
        # Sort by score and return top results
        unique_contexts.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"🔄 Retrieval repair: {len(repair_queries)} queries → {len(unique_contexts)} contexts")
        
        return unique_contexts[:5]


# =============================================================================
# GUARDRAILS ENGINE (Central Orchestrator)
# =============================================================================

class GuardrailsEngine:
    """
    Central guardrails orchestrator.
    
    CORRECT FLOW:
    1. Safety check (tiered: instruction vs ideation vs stress)
    2. Exam integrity check (dynamic teach-instead)
    3. Retrieval repair (if needed)
    4. Grounding verification (ALWAYS after repair)
    5. Final decision
    
    CRITICAL: Retrieval repair MUST re-verify grounding after repair.
    """
    
    def __init__(self):
        self.safety_guard = SafetyGuard()
        self.exam_checker = ExamIntegrityChecker()
        self.grounding_verifier = GroundingVerifier()
        self.retrieval_repair = RetrievalRepair()
        
        logger.info("🛡️ GuardrailsEngine initialized")
    
    async def process(
        self,
        envelope: ResponseEnvelope,
        context: Dict[str, Any] = None
    ) -> ResponseEnvelope:
        """
        Process response through all guardrails.
        
        FLOW:
        1. Safety (tiered)
        2. Exam integrity
        3. Retrieval repair → RE-VERIFY grounding
        4. Grounding decision
        5. Final answer
        
        Returns updated envelope with guardrail decisions.
        """
        context = context or {}
        
        if GUARDRAILS_DEBUG:
            logger.info(f"🛡️ Guardrails processing: {envelope.user_message[:50]}...")
        
        # === STEP 1: SAFETY CHECK (Tiered - Highest Priority) ===
        safety_result = self.safety_guard.check(envelope.user_message, context)
        
        if safety_result.risk_flags:
            envelope.risk_flags.extend(safety_result.risk_flags)
            
            # TIER A: Self-harm INSTRUCTION → HARD_BLOCK
            if safety_result.is_self_harm_instruction:
                envelope.guardrail_status = GuardrailStatus.HARD_BLOCK
                envelope.guardrail_actions.append(GuardrailAction.CRISIS_SUPPORT)
                envelope.final_answer = self.safety_guard.get_crisis_response(safety_result)
                self._log_guardrail_decision(envelope, "safety_tier_a_instruction")
                return envelope
            
            # TIER B: Self-harm IDEATION → crisis_support (supportive, not refusal)
            if safety_result.is_self_harm_ideation:
                envelope.guardrail_status = GuardrailStatus.SOFT_BLOCK
                envelope.guardrail_actions.append(GuardrailAction.CRISIS_SUPPORT)
                envelope.final_answer = self.safety_guard.get_crisis_response(safety_result)
                self._log_guardrail_decision(envelope, "safety_tier_b_ideation")
                return envelope
            
            # TIER C: Normal stress → Continue with supportive context (PASS)
            if safety_result.severity == SafetySeverity.TIER_C_STRESS:
                # Add supportive context but continue normal flow
                envelope.guardrail_actions.append(GuardrailAction.NONE)
                # Don't block - let the normal response flow with empathy
        
        # === STEP 2: EXAM INTEGRITY CHECK ===
        is_cheating, exam_action = self.exam_checker.check(envelope.user_message, context)
        
        if is_cheating:
            envelope.risk_flags.append(RiskFlag.CHEATING)
            envelope.guardrail_status = GuardrailStatus.HARD_BLOCK
            envelope.guardrail_actions.append(GuardrailAction.TEACH_INSTEAD)
            
            # Dynamic teach-instead response (NOT template)
            envelope.final_answer = self.exam_checker.get_teach_instead_response(
                envelope.user_message,
                context.get("subject")
            )
            
            self._log_guardrail_decision(envelope, "exam_integrity_teach_instead")
            return envelope
        
        # === STEP 3: GROUNDING VERIFICATION (First Pass) ===
        # 🎯 TRI-LANE RESPONSE ENGINE: Skip grounding for Conversation Lane
        # 
        # LANE A (Conversation): emotional, chitchat, proactive, fast, clarification
        #   → These are dialogue/memory-based, NOT factual claims
        #   → Bypass grounding entirely (but keep safety + exam integrity)
        #
        # LANE B (Education): multi_agent, hybrid, react_agentic, visual_sync
        #   → These make factual claims that need grounding
        #   → Full guardrails apply
        #
        # LANE C (Action): Handled by agentic router before reaching here
        #
        # This is ROUTE-DRIVEN, not keyword-driven.
        
        # Educational routes that REQUIRE grounding verification
        FACTUAL_ROUTES = {
            'multi_agent',     # Educational explanations
            'hybrid',          # Hybrid reasoning (factual)
            'react_agentic',   # ReAct with tools (factual)
            'visual_sync',     # Visual explanations (factual)
        }
        
        route_type_lower = envelope.route_type.lower() if envelope.route_type else ""
        
        # Only apply grounding to factual/educational routes
        requires_grounding = route_type_lower in FACTUAL_ROUTES
        
        if not requires_grounding:
            # CONVERSATION LANE: Pass through without grounding
            logger.info(f"🎯 Conversation Lane: route='{envelope.route_type}' → bypass grounding")
            envelope.guardrail_status = GuardrailStatus.PASS
            envelope.guardrail_actions.append(GuardrailAction.NONE)
            envelope.final_answer = envelope.draft_answer
            self._log_guardrail_decision(envelope, "conversation_lane_pass")
            return envelope
        
        # EDUCATION LANE: Apply grounding verification
        logger.info(f"📚 Education Lane: route='{envelope.route_type}' → grounding check")
        envelope.claims_extracted = self.grounding_verifier.extract_claims(envelope.draft_answer)
        
        if envelope.claims_extracted:
            supported, unsupported, support_rate = await self.grounding_verifier.verify_claims(
                envelope.claims_extracted,
                envelope.retrieval_contexts
            )
            
            envelope.claims_supported = supported
            envelope.claims_unsupported = unsupported
            envelope.claim_support_rate = support_rate
        
        # === STEP 4: RETRIEVAL REPAIR (If Needed) + RE-VERIFY ===
        if self.retrieval_repair.should_repair(envelope):
            envelope.retrieval_retries += 1
            envelope.guardrail_actions.append(GuardrailAction.RETRIEVAL_RETRY)
            
            new_contexts = await self.retrieval_repair.repair(
                envelope,
                context.get("subject")
            )
            
            if new_contexts:
                # Merge with existing
                existing_ids = {c.chunk_id for c in envelope.retrieval_contexts}
                for ctx in new_contexts:
                    if ctx.chunk_id not in existing_ids:
                        envelope.retrieval_contexts.append(ctx)
                
                # Recalculate confidence
                if envelope.retrieval_contexts:
                    envelope.retrieval_confidence = sum(
                        c.score for c in envelope.retrieval_contexts
                    ) / len(envelope.retrieval_contexts)
                
                # === CRITICAL: RE-VERIFY GROUNDING AFTER REPAIR ===
                if envelope.claims_extracted:
                    supported, unsupported, support_rate = await self.grounding_verifier.verify_claims(
                        envelope.claims_extracted,
                        envelope.retrieval_contexts
                    )
                    
                    envelope.claims_supported = supported
                    envelope.claims_unsupported = unsupported
                    envelope.claim_support_rate = support_rate
                    
                    logger.info(f"🔄 Re-verified after repair: support_rate={support_rate:.2f}")
        
        # === STEP 5: GROUNDING DECISION ===
        if envelope.claims_extracted:
            grounding_status = self.grounding_verifier.get_grounding_decision(envelope.claim_support_rate)
            
            if grounding_status == GuardrailStatus.HARD_BLOCK:
                envelope.guardrail_status = GuardrailStatus.HARD_BLOCK
                envelope.risk_flags.append(RiskFlag.LOW_GROUNDING)
                envelope.guardrail_actions.append(GuardrailAction.ASK_CLARIFY)
                
                # Generate response that does NOT hallucinate
                envelope.final_answer = self._generate_no_hallucinate_response(envelope)
                
                self._log_guardrail_decision(envelope, "low_grounding_hard_block")
                return envelope
            
            elif grounding_status == GuardrailStatus.SOFT_BLOCK:
                envelope.guardrail_status = GuardrailStatus.SOFT_BLOCK
                envelope.risk_flags.append(RiskFlag.LOW_GROUNDING)
                envelope.guardrail_actions.append(GuardrailAction.ADD_UNCERTAINTY_NOTES)
                
                # Revise to supported content only + uncertainty notes
                envelope.final_answer = self._revise_to_supported(envelope)
                
                self._log_guardrail_decision(envelope, "low_grounding_soft_block")
                return envelope
        
        # === STEP 6: PASS - Use draft as final ===
        envelope.guardrail_status = GuardrailStatus.PASS
        envelope.final_answer = envelope.draft_answer
        
        # Add valid citations if available
        if envelope.retrieval_contexts:
            valid_citations = self.grounding_verifier.get_valid_citations(envelope.retrieval_contexts)
            if valid_citations and GUARDRAILS_DEBUG:
                logger.debug(f"📚 Valid citations: {len(valid_citations)}")
        
        self._log_guardrail_decision(envelope, "pass")
        return envelope
    
    def _generate_no_hallucinate_response(self, envelope: ResponseEnvelope) -> str:
        """
        Generate response when grounding is too low.
        
        🎯 STUDENT-FIRST: Never leave student hanging with "KB not found".
        Instead: Acknowledge → What we CAN help with → Clarifying question → Options
        
        CRITICAL: Must NOT hallucinate factual claims. But CAN:
        - Acknowledge the question
        - Offer to help in different ways
        - Ask clarifying questions
        - Suggest next steps
        """
        # Check what we can offer
        has_any_context = len(envelope.retrieval_contexts) > 0
        
        if has_any_context:
            # We have some context but not enough - teach from what we have
            sections = list(set(c.section for c in envelope.retrieval_contexts[:2]))
            section_hint = f" about {', '.join(sections)}" if sections else ""
            
            return (
                f"I can help with this{section_hint}.\n\n"
                "To give you the best explanation:\n"
                "- What specific aspect would you like to focus on?\n"
                "- Is this for exam prep or concept understanding?\n\n"
                "Let me know and I'll explain it clearly."
            )
        else:
            # No context at all - STILL help, just differently
            # Extract topic hint from user message if possible
            topic_hint = envelope.user_message[:50] if envelope.user_message else "this topic"
            
            return (
                f"I'd love to help you with that! 🎯\n\n"
                "Let me understand your question better:\n"
                "- Which subject is this for (Physics, Chemistry, Bio, Math)?\n"
                "- What do you already know about it?\n\n"
                "**Here's how I can help:**\n"
                "• Explain the concept from basics\n"
                "• Walk through an example problem\n"
                "• Create a quick visual explanation\n\n"
                "Just tell me a bit more, and I'll jump right in! 💪"
            )
    
    def _revise_to_supported(self, envelope: ResponseEnvelope) -> str:
        """
        Revise response to include only supported content + uncertainty notes.
        
        MUST include valid citations (doc_id + chunk_id + section).
        """
        # Get valid citations ONLY
        valid_citations = self.grounding_verifier.get_valid_citations(envelope.retrieval_contexts)
        
        # Build citation note
        citation_note = ""
        if valid_citations:
            sections = list(set(c["section"] for c in valid_citations[:3] if c.get("section")))
            if sections:
                citation_note = f"\n\n📚 *Sources: {', '.join(sections)}*"
        
        # Add uncertainty note for unsupported claims
        uncertainty_note = ""
        if envelope.claims_unsupported:
            uncertainty_note = (
                "\n\n⚠️ *Note: Some details may need verification from your textbook. "
                "I've marked what I'm confident about based on your syllabus.*"
            )
        
        return envelope.draft_answer + citation_note + uncertainty_note
    
    def _log_guardrail_decision(self, envelope: ResponseEnvelope, decision_type: str):
        """Log guardrail decision for observability"""
        log_data = envelope.to_log_dict()
        log_data["decision_type"] = decision_type
        
        if GUARDRAILS_DEBUG:
            logger.info(f"🛡️ GUARDRAIL: {decision_type} | {log_data}")
        else:
            logger.info(f"🛡️ Guardrail: {decision_type} | status={envelope.guardrail_status.value} | "
                       f"citations={len(envelope.retrieval_contexts)} | support_rate={envelope.claim_support_rate:.2f}")


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_guardrails_engine: Optional[GuardrailsEngine] = None


def get_guardrails_engine() -> GuardrailsEngine:
    """Get or create the global guardrails engine"""
    global _guardrails_engine
    if _guardrails_engine is None:
        _guardrails_engine = GuardrailsEngine()
    return _guardrails_engine


# =============================================================================
# HELPER: Create Envelope from Orchestrator Result
# =============================================================================

def create_envelope_from_result(
    user_message: str,
    result: Dict[str, Any],
    routing_decision: Any = None,
    context: Dict[str, Any] = None
) -> ResponseEnvelope:
    """
    Create ResponseEnvelope from orchestrator result.
    
    This captures metadata from the orchestrator pipeline.
    """
    context = context or {}
    
    # Extract agent and route info
    agent_name = "unknown"
    route_type = "unknown"
    
    if routing_decision:
        agent_name = routing_decision.agents_to_activate[0] if routing_decision.agents_to_activate else "unknown"
        route_type = routing_decision.pipeline.value if hasattr(routing_decision.pipeline, 'value') else str(routing_decision.pipeline)
    
    # Extract draft answer
    draft_answer = result.get("main_response", "")
    if not draft_answer:
        draft_answer = result.get("response", {}).get("default_view", {}).get("main_content", {}).get("content", "")
    
    # Extract retrieval info from orchestration metadata
    orchestration = result.get("orchestration", {})
    retrieval_confidence = orchestration.get("confidence", 0.0)
    
    # Extract contexts from tool results if available
    contexts = []
    if "retrieval_contexts" in result:
        for ctx in result["retrieval_contexts"]:
            contexts.append(RetrievalContext(
                chunk_id=ctx.get("chunk_id", ""),
                doc_id=ctx.get("doc_id", ""),
                section=ctx.get("section", ""),
                text_snippet=ctx.get("content", "")[:500],
                score=ctx.get("score", 0.0),
                source_file=ctx.get("raw_file")
            ))
    
    return ResponseEnvelope(
        user_message=user_message,
        agent_name=agent_name,
        route_type=route_type,
        draft_answer=draft_answer,
        retrieval_contexts=contexts,
        retrieval_confidence=retrieval_confidence,
        retrieval_method=orchestration.get("retrieval_method", "unknown"),
        request_id=context.get("request_id", "")
    )


def apply_envelope_to_result(envelope: ResponseEnvelope, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply envelope decisions back to orchestrator result.
    
    This updates the result with guardrail decisions WITHOUT changing the external schema.
    """
    # Update main response if guardrails modified it
    if envelope.final_answer and envelope.final_answer != envelope.draft_answer:
        result["main_response"] = envelope.final_answer
        
        # Update nested response structure too
        if "response" in result and "default_view" in result["response"]:
            if "main_content" in result["response"]["default_view"]:
                result["response"]["default_view"]["main_content"]["content"] = envelope.final_answer
    
    # Add guardrail metadata (internal, not exposed to UI)
    result["_guardrails"] = envelope.to_log_dict()
    
    # Add citations if available
    if envelope.retrieval_contexts:
        result["_citations"] = envelope.get_citations()
    
    return result
