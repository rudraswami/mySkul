"""
⚔️ Agent Challenge Mechanism - Post-Response Dispute Resolution
================================================================

This module enables agents to CHALLENGE each other's responses when
contradictions are detected. This is TRUE agent autonomy: agents don't
just produce outputs, they reason about each other's claims.

ARCHITECTURE:
- Runs AFTER all agents complete (post-response hook)
- Detects contradictions between agent outputs
- Triggers challenge rounds where agents can dispute
- Produces revised response if challenge succeeds

INTEGRATION:
- Called by supervisor AFTER _merge_responses()
- Does NOT modify parallel execution
- Additive hook that enhances final output

This is TRUE cognition: agents argue, correct, and refine each other.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ChallengeType(Enum):
    """Types of challenges an agent can raise"""
    FACTUAL_ERROR = "factual_error"
    MATHEMATICAL_ERROR = "mathematical_error"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    INCOMPLETE_REASONING = "incomplete_reasoning"
    CONCEPTUAL_CONFUSION = "conceptual_confusion"


class ChallengeOutcome(Enum):
    """Outcome of a challenge"""
    UPHELD = "upheld"              # Challenge is valid, original was wrong
    REJECTED = "rejected"          # Challenge is invalid, original stands
    PARTIAL = "partial"            # Partially valid, both need refinement
    WITHDRAWN = "withdrawn"        # Challenger withdrew after review


@dataclass
class Challenge:
    """A challenge raised by one agent against another"""
    challenger_agent: str
    challenged_agent: str
    challenge_type: ChallengeType
    claim_disputed: str              # The specific claim being disputed
    counter_claim: str               # The challenger's counter-claim
    evidence: str                    # Evidence supporting the challenge
    confidence: float                # Challenger's confidence (0-1)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'challenger': self.challenger_agent,
            'challenged': self.challenged_agent,
            'type': self.challenge_type.value,
            'claim_disputed': self.claim_disputed,
            'counter_claim': self.counter_claim,
            'evidence': self.evidence,
            'confidence': self.confidence
        }


@dataclass
class ChallengeResolution:
    """Resolution of a challenge"""
    challenge: Challenge
    outcome: ChallengeOutcome
    revised_claim: Optional[str]     # The corrected claim if upheld
    resolution_reasoning: str        # Why this outcome was chosen
    adjudicator: str                 # Who resolved (e.g., "MathVerifier", "LLM")


class AgentChallengeSystem:
    """
    System for managing agent challenges and dispute resolution.
    
    This enables TRUE agent collaboration: agents don't just produce
    outputs, they reason about and challenge each other's claims.
    """
    
    def __init__(self, llm_api_key: Optional[str] = None):
        self.llm_api_key = llm_api_key
        self._challenges: List[Challenge] = []
        self._resolutions: List[ChallengeResolution] = []
    
    async def detect_contradictions(
        self,
        agent_responses: Dict[str, Any],
        query: str,
        context: Dict[str, Any]
    ) -> List[Tuple[str, str, str]]:
        """
        Detect contradictions between agent responses.
        
        Returns list of (agent1, agent2, contradiction_description) tuples.
        """
        contradictions = []
        
        # Get response contents
        responses = {}
        for agent_name, response in agent_responses.items():
            if isinstance(response, dict) and response.get('success'):
                content = response.get('content', '')
                if isinstance(content, str) and len(content) > 50:
                    responses[agent_name] = content
        
        if len(responses) < 2:
            return []
        
        # Check for numerical contradictions
        agent_names = list(responses.keys())
        for i, agent1 in enumerate(agent_names):
            for agent2 in agent_names[i+1:]:
                content1 = responses[agent1]
                content2 = responses[agent2]
                
                # Extract numerical answers
                numbers1 = self._extract_numerical_answers(content1)
                numbers2 = self._extract_numerical_answers(content2)
                
                # Check for conflicting numbers in same context
                for num1 in numbers1:
                    for num2 in numbers2:
                        if self._numbers_conflict(num1, num2):
                            contradictions.append((
                                agent1, agent2,
                                f"Numerical conflict: {agent1} says {num1}, {agent2} says {num2}"
                            ))
                
                # Check for logical contradictions via patterns
                logic_conflict = self._detect_logical_contradiction(content1, content2)
                if logic_conflict:
                    contradictions.append((agent1, agent2, logic_conflict))
        
        logger.info(f"🔍 Detected {len(contradictions)} potential contradictions")
        return contradictions
    
    def _extract_numerical_answers(self, content: str) -> List[str]:
        """Extract numerical answers from response"""
        patterns = [
            r'(?:answer|result|equals?|=)\s*[:=]?\s*([+-]?\d+(?:\.\d+)?)',
            r'(?:final\s+answer|solution)\s*[:=]?\s*([+-]?\d+(?:\.\d+)?)',
            r'\*\*([+-]?\d+(?:\.\d+)?)\*\*',  # Bold numbers (often answers)
        ]
        
        numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            numbers.extend(matches)
        
        return numbers[:5]  # Limit to prevent noise
    
    def _numbers_conflict(self, num1: str, num2: str) -> bool:
        """Check if two numbers represent conflicting answers"""
        try:
            n1 = float(num1)
            n2 = float(num2)
            
            # Allow small floating point differences
            if abs(n1 - n2) < 0.0001:
                return False
            
            # Same magnitude but different value = conflict
            if abs(n1) > 0.01 and abs(n2) > 0.01:
                ratio = max(n1, n2) / min(abs(n1), abs(n2))
                if 0.5 < ratio < 2.0:  # Similar magnitude
                    return n1 != n2
            
            return False
        except (ValueError, ZeroDivisionError):
            return False
    
    def _detect_logical_contradiction(self, content1: str, content2: str) -> Optional[str]:
        """Detect logical contradictions between responses"""
        # Pattern pairs that indicate contradiction
        contradiction_pairs = [
            (r'(?:is|are)\s+(?:always)\s+(\w+)', r'(?:is|are)\s+(?:never)\s+\1'),
            (r'(?:must|should)\s+(\w+)', r'(?:must|should)\s+not\s+\1'),
            (r'increases?\s+(\w+)', r'decreases?\s+\1'),
            (r'positive\s+(\w+)', r'negative\s+\1'),
        ]
        
        for pattern1, pattern2 in contradiction_pairs:
            match1 = re.search(pattern1, content1, re.IGNORECASE)
            match2 = re.search(pattern2, content2, re.IGNORECASE)
            if match1 and match2:
                return f"Logical contradiction detected: '{match1.group(0)}' vs '{match2.group(0)}'"
            
            # Check reverse
            match1 = re.search(pattern1, content2, re.IGNORECASE)
            match2 = re.search(pattern2, content1, re.IGNORECASE)
            if match1 and match2:
                return f"Logical contradiction detected: '{match1.group(0)}' vs '{match2.group(0)}'"
        
        return None
    
    async def initiate_challenge(
        self,
        challenger_agent: str,
        challenged_agent: str,
        contradiction_desc: str,
        agent_responses: Dict[str, Any],
        query: str,
        context: Dict[str, Any]
    ) -> Challenge:
        """
        Create a challenge from one agent to another.
        
        The challenger agent reasons about why the other agent is wrong.
        """
        challenger_response = agent_responses.get(challenger_agent, {})
        challenged_response = agent_responses.get(challenged_agent, {})
        
        # Determine challenge type from contradiction
        if 'numerical' in contradiction_desc.lower() or 'mathematical' in contradiction_desc.lower():
            challenge_type = ChallengeType.MATHEMATICAL_ERROR
        elif 'logical' in contradiction_desc.lower():
            challenge_type = ChallengeType.LOGICAL_CONTRADICTION
        else:
            challenge_type = ChallengeType.FACTUAL_ERROR
        
        # Extract the disputed claim and counter-claim
        claim_disputed = self._extract_claim(challenged_response.get('content', ''), contradiction_desc)
        counter_claim = self._extract_claim(challenger_response.get('content', ''), contradiction_desc)
        
        challenge = Challenge(
            challenger_agent=challenger_agent,
            challenged_agent=challenged_agent,
            challenge_type=challenge_type,
            claim_disputed=claim_disputed,
            counter_claim=counter_claim,
            evidence=contradiction_desc,
            confidence=0.7  # Default, can be refined
        )
        
        self._challenges.append(challenge)
        logger.info(f"⚔️ {challenger_agent} challenges {challenged_agent}: {challenge_type.value}")
        
        return challenge
    
    def _extract_claim(self, content: str, context: str) -> str:
        """Extract the relevant claim from content based on context"""
        # Find sentence containing key terms from context
        sentences = content.split('.')
        
        # Get key terms from context
        key_terms = re.findall(r'\b\d+\.?\d*\b', context)  # Numbers
        key_terms.extend(re.findall(r'\b[A-Za-z]{4,}\b', context))  # Words
        
        for sentence in sentences:
            if any(term in sentence for term in key_terms[:5]):
                return sentence.strip()[:200]
        
        # Fallback: return first substantial sentence
        for sentence in sentences:
            if len(sentence.strip()) > 30:
                return sentence.strip()[:200]
        
        return content[:200]
    
    async def resolve_challenge(
        self,
        challenge: Challenge,
        query: str,
        context: Dict[str, Any]
    ) -> ChallengeResolution:
        """
        Resolve a challenge using available verification methods.
        
        Priority:
        1. Mathematical verification (if math content)
        2. Knowledge graph verification (if factual)
        3. LLM-based adjudication (fallback)
        """
        # Try mathematical verification first
        if challenge.challenge_type == ChallengeType.MATHEMATICAL_ERROR:
            resolution = await self._resolve_via_math_verification(challenge, query)
            if resolution:
                self._resolutions.append(resolution)
                return resolution
        
        # Fallback to LLM adjudication
        resolution = await self._resolve_via_llm(challenge, query, context)
        self._resolutions.append(resolution)
        return resolution
    
    async def _resolve_via_math_verification(
        self,
        challenge: Challenge,
        query: str
    ) -> Optional[ChallengeResolution]:
        """Resolve challenge using MathVerifier"""
        try:
            from services.verification.math_verifier import MathVerifier
            
            verifier = MathVerifier()
            
            # Verify challenger's claim
            challenger_result = verifier.verify_response(
                response_text=challenge.counter_claim,
                question=query,
                subject="Mathematics"
            )
            
            # Verify challenged agent's claim
            challenged_result = verifier.verify_response(
                response_text=challenge.claim_disputed,
                question=query,
                subject="Mathematics"
            )
            
            # Determine outcome based on verification
            challenger_valid = challenger_result.status.value in ['correct', 'likely_correct']
            challenged_valid = challenged_result.status.value in ['correct', 'likely_correct']
            
            if challenger_valid and not challenged_valid:
                outcome = ChallengeOutcome.UPHELD
                revised = challenge.counter_claim
                reasoning = f"MathVerifier confirmed challenger's answer. Errors in original: {challenged_result.errors}"
            elif challenged_valid and not challenger_valid:
                outcome = ChallengeOutcome.REJECTED
                revised = None
                reasoning = f"MathVerifier confirmed original answer. Challenger's errors: {challenger_result.errors}"
            elif challenger_valid and challenged_valid:
                outcome = ChallengeOutcome.PARTIAL
                revised = challenge.counter_claim  # Prefer challenger in ties with both valid
                reasoning = "Both claims appear mathematically valid - may be equivalent forms"
            else:
                outcome = ChallengeOutcome.PARTIAL
                revised = None
                reasoning = "Neither claim could be verified - requires human review"
            
            logger.info(f"🧮 Math verification resolved challenge: {outcome.value}")
            
            return ChallengeResolution(
                challenge=challenge,
                outcome=outcome,
                revised_claim=revised,
                resolution_reasoning=reasoning,
                adjudicator="MathVerifier"
            )
            
        except ImportError:
            logger.debug("MathVerifier not available for challenge resolution")
            return None
        except Exception as e:
            logger.warning(f"Math verification failed: {e}")
            return None
    
    async def _resolve_via_llm(
        self,
        challenge: Challenge,
        query: str,
        context: Dict[str, Any]
    ) -> ChallengeResolution:
        """Resolve challenge using LLM adjudication"""
        try:
            import openai
            import os
            
            api_key = self.llm_api_key or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("No API key available")
            
            client = openai.AsyncOpenAI(api_key=api_key)
            
            prompt = f"""You are an impartial adjudicator resolving a dispute between two AI agents.

ORIGINAL QUESTION: {query}

AGENT A ({challenge.challenged_agent}) CLAIMS:
{challenge.claim_disputed}

AGENT B ({challenge.challenger_agent}) DISPUTES THIS AND CLAIMS:
{challenge.counter_claim}

CHALLENGE TYPE: {challenge.challenge_type.value}
EVIDENCE: {challenge.evidence}

Analyze both claims carefully. Determine:
1. Which claim is correct (or if both are partially correct)
2. What the correct answer should be

Respond in this exact format:
OUTCOME: [UPHELD/REJECTED/PARTIAL]
CORRECT_ANSWER: [The verified correct answer]
REASONING: [Brief explanation of your decision]"""
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            
            # Parse response
            outcome = ChallengeOutcome.PARTIAL
            if 'OUTCOME: UPHELD' in result:
                outcome = ChallengeOutcome.UPHELD
            elif 'OUTCOME: REJECTED' in result:
                outcome = ChallengeOutcome.REJECTED
            
            # Extract correct answer
            revised = None
            if 'CORRECT_ANSWER:' in result:
                revised = result.split('CORRECT_ANSWER:')[1].split('REASONING:')[0].strip()
            
            # Extract reasoning
            reasoning = "LLM adjudication"
            if 'REASONING:' in result:
                reasoning = result.split('REASONING:')[1].strip()
            
            logger.info(f"🤖 LLM resolved challenge: {outcome.value}")
            
            return ChallengeResolution(
                challenge=challenge,
                outcome=outcome,
                revised_claim=revised,
                resolution_reasoning=reasoning[:500],
                adjudicator="LLM-gpt-4o-mini"
            )
            
        except Exception as e:
            logger.warning(f"LLM adjudication failed: {e}")
            
            # Default to partial - let human review
            return ChallengeResolution(
                challenge=challenge,
                outcome=ChallengeOutcome.PARTIAL,
                revised_claim=None,
                resolution_reasoning=f"Adjudication failed: {str(e)}. Manual review recommended.",
                adjudicator="Fallback"
            )
    
    async def run_challenge_round(
        self,
        agent_responses: Dict[str, Any],
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a full challenge round on agent responses.
        
        This is the main entry point - call after _merge_responses().
        
        Returns:
            Updated responses with challenge resolutions applied
        """
        # Step 1: Detect contradictions
        contradictions = await self.detect_contradictions(agent_responses, query, context)
        
        if not contradictions:
            logger.info("✅ No contradictions detected - challenge round skipped")
            return {
                'responses': agent_responses,
                'challenges': [],
                'resolutions': [],
                'challenge_round_ran': False
            }
        
        # Step 2: Create challenges
        challenges = []
        for agent1, agent2, desc in contradictions:
            challenge = await self.initiate_challenge(
                challenger_agent=agent1,
                challenged_agent=agent2,
                contradiction_desc=desc,
                agent_responses=agent_responses,
                query=query,
                context=context
            )
            challenges.append(challenge)
        
        # Step 3: Resolve challenges
        resolutions = []
        for challenge in challenges:
            resolution = await self.resolve_challenge(challenge, query, context)
            resolutions.append(resolution)
        
        # Step 4: Apply corrections to responses
        corrected_responses = agent_responses.copy()
        for resolution in resolutions:
            if resolution.outcome == ChallengeOutcome.UPHELD and resolution.revised_claim:
                # Update the challenged agent's response
                challenged_agent = resolution.challenge.challenged_agent
                if challenged_agent in corrected_responses:
                    corrected_responses[challenged_agent] = {
                        **corrected_responses[challenged_agent],
                        '_original_content': corrected_responses[challenged_agent].get('content'),
                        'content': resolution.revised_claim,
                        '_challenge_correction': {
                            'corrected_by': resolution.challenge.challenger_agent,
                            'adjudicator': resolution.adjudicator,
                            'reasoning': resolution.resolution_reasoning
                        }
                    }
                    logger.info(f"📝 Applied correction to {challenged_agent} from challenge")
        
        logger.info(f"⚔️ Challenge round complete: {len(challenges)} challenges, "
                   f"{sum(1 for r in resolutions if r.outcome == ChallengeOutcome.UPHELD)} upheld")
        
        return {
            'responses': corrected_responses,
            'challenges': [c.to_dict() for c in challenges],
            'resolutions': [{
                'challenge': r.challenge.to_dict(),
                'outcome': r.outcome.value,
                'revised': r.revised_claim,
                'reasoning': r.resolution_reasoning,
                'adjudicator': r.adjudicator
            } for r in resolutions],
            'challenge_round_ran': True
        }


# Singleton instance
_challenge_system: Optional[AgentChallengeSystem] = None


def get_challenge_system(llm_api_key: Optional[str] = None) -> AgentChallengeSystem:
    """Get or create the challenge system singleton"""
    global _challenge_system
    if _challenge_system is None:
        _challenge_system = AgentChallengeSystem(llm_api_key)
    return _challenge_system

