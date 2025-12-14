"""
🧠 Unified AI Orchestrator - The Brain of AI Sathi v2.0
========================================================

REPLACES: USE_UNIFIED_FIRST = True (the flawed approach)

This orchestrator intelligently routes ALL queries through the optimal pipeline:
1. TRIVIAL → Fast greeting response
2. SIMPLE → Enhanced ResponseComposer (with refinement)
3. MODERATE → Multi-Agent Supervisor (parallel agents)
4. COMPLEX → Hybrid Reasoning Engine (Neural + Symbolic)
5. DEEP → Full ReAct with Verification

NO MORE bypassing advanced features!
Every educational query gets appropriate intelligence.
"""

import logging
import time
import asyncio
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result from orchestration"""
    success: bool
    response: Dict[str, Any]
    pipeline_used: str
    generation_time: float
    agents_involved: List[str]
    tools_used: List[str]
    verification_status: str
    quality_score: float


class UnifiedAIOrchestrator:
    """
    The Central Intelligence Hub for AI Sathi
    
    This orchestrator:
    1. Analyzes every query for complexity
    2. Routes to the optimal pipeline
    3. Ensures quality through verification
    4. Provides consistent output format
    
    NO fallback logic - every path is intentional.
    """
    
    def __init__(self, db, llm_api_key: str = None):
        """Initialize orchestrator with all components"""
        self.db = db
        self.llm_api_key = llm_api_key or os.environ.get('OPENAI_API_KEY')
        
        # Initialize components lazily
        self._routing_engine = None
        self._enhanced_composer = None
        self._supervisor = None
        self._hybrid_engine = None
        self._negotiator = None
        
        logger.info("🧠 UnifiedAIOrchestrator initialized - Intelligent routing active")
    
    @property
    def routing_engine(self):
        """Lazy load routing engine"""
        if self._routing_engine is None:
            from services.intelligent_routing_engine import get_routing_engine
            self._routing_engine = get_routing_engine(self.db)
        return self._routing_engine
    
    @property
    def enhanced_composer(self):
        """Lazy load enhanced composer"""
        if self._enhanced_composer is None:
            from services.enhanced_response_composer import get_enhanced_composer
            self._enhanced_composer = get_enhanced_composer(self.db, self.llm_api_key)
        return self._enhanced_composer
    
    @property
    def supervisor(self):
        """Lazy load supervisor"""
        if self._supervisor is None:
            from agents.enhanced_supervisor import EnhancedSupervisor
            self._supervisor = EnhancedSupervisor({"emergent_llm_key": self.llm_api_key})
        return self._supervisor
    
    @property
    def hybrid_engine(self):
        """Lazy load hybrid reasoning engine"""
        if self._hybrid_engine is None:
            try:
                from services.hybrid_reasoning_engine import get_hybrid_reasoning_engine
                self._hybrid_engine = get_hybrid_reasoning_engine()
            except ImportError:
                logger.warning("Hybrid reasoning engine not available")
                self._hybrid_engine = None
        return self._hybrid_engine
    
    @property
    def negotiator(self):
        """Lazy load agent negotiator"""
        if self._negotiator is None:
            from services.cognitive_model.agent_negotiation import get_agent_negotiator
            self._negotiator = get_agent_negotiator(self.llm_api_key)
        return self._negotiator
    
    async def process(
        self,
        user_id: str,
        session_id: str,
        message: str,
        subject: str = None,
        exam_mode: str = "General",
        message_history: List[Dict] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for ALL AI requests.
        
        Intelligently routes to the optimal pipeline based on query complexity.
        
        Args:
            user_id: User ID
            session_id: Session ID
            message: User's message/question
            subject: Subject area
            exam_mode: Exam type
            message_history: Previous messages
            context: Additional context
            
        Returns:
            Unified response with metadata
        """
        start_time = time.time()
        context = context or {}
        
        # Merge context
        full_context = {
            "user_id": user_id,
            "session_id": session_id,
            "subject": subject,
            "exam_mode": exam_mode,
            "message_history": message_history,
            **context
        }
        
        logger.info(f"🧠 Orchestrating: {message[:60]}...")
        
        try:
            # === STEP 1: Intelligent Routing Decision ===
            routing_decision = await self.routing_engine.route(message, full_context)
            
            logger.info(f"   Pipeline: {routing_decision.pipeline.value}")
            logger.info(f"   Complexity: {routing_decision.complexity.value}")
            logger.info(f"   Agents: {routing_decision.agents_to_activate}")
            
            # === STEP 2: Execute Appropriate Pipeline ===
            from services.intelligent_routing_engine import RecommendedPipeline
            
            if routing_decision.pipeline == RecommendedPipeline.FAST_RESPONSE:
                result = await self._fast_response(message, full_context, routing_decision)
                
            elif routing_decision.pipeline == RecommendedPipeline.MULTI_AGENT:
                result = await self._multi_agent_response(message, full_context, routing_decision)
                
            elif routing_decision.pipeline == RecommendedPipeline.HYBRID_REASONING:
                result = await self._hybrid_response(message, full_context, routing_decision)
                
            elif routing_decision.pipeline == RecommendedPipeline.REACT_AGENTIC:
                result = await self._react_agentic_response(message, full_context, routing_decision)
                
            elif routing_decision.pipeline == RecommendedPipeline.VISUAL_SYNC:
                result = await self._visual_sync_response(message, full_context, routing_decision)
                
            else:
                # Default to multi-agent
                result = await self._multi_agent_response(message, full_context, routing_decision)
            
            # === STEP 3: Post-Processing ===
            generation_time = time.time() - start_time
            
            # Add orchestration metadata
            result["orchestration"] = {
                "pipeline": routing_decision.pipeline.value,
                "complexity": routing_decision.complexity.value,
                "confidence": routing_decision.confidence,
                "agents_activated": routing_decision.agents_to_activate,
                "tools_enabled": routing_decision.tools_to_enable,
                "generation_time": generation_time,
                "routing_reasoning": routing_decision.reasoning
            }
            
            logger.info(f"✅ Orchestration complete in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Orchestration failed: {e}", exc_info=True)
            return self._error_response(message, str(e), time.time() - start_time)
    
    async def _fast_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Fast response for trivial queries (greetings, gratitude, etc.)"""
        
        msg_lower = message.lower().strip().rstrip('!?.')
        
        # Check for simple greetings
        greetings = ['hi', 'hello', 'hey', 'namaste', 'yo', 'sup']
        if msg_lower in greetings:
            return self._generate_greeting(context)
        
        # Check for gratitude/acknowledgment - respond warmly!
        gratitude_words = [
            'thanks', 'thank you', 'thank you so much', 'thanks a lot',
            'ty', 'tysm', 'thx', 'thnx', 'thnks', 'dhanyawad', 'shukriya',
            'appreciate it', 'much appreciated', 'thanks buddy', 'thanks yaar'
        ]
        acknowledgments = ['ok', 'okay', 'got it', 'understood', 'great', 'nice', 'cool', 'awesome', 'perfect']
        
        if msg_lower in gratitude_words or any(msg_lower.startswith(g) for g in gratitude_words):
            return self._generate_gratitude_response(context)
        
        if msg_lower in acknowledgments:
            return self._generate_acknowledgment_response(context)
        
        # Use enhanced composer with minimal refinement
        result = await self.enhanced_composer.generate_response(
            user_id=context.get("user_id", ""),
            session_id=context.get("session_id", ""),
            question=message,
            subject=context.get("subject"),
            exam_mode=context.get("exam_mode", "General"),
            message_history=context.get("message_history"),
            enable_refinement=False,  # Skip refinement for fast path
            quality_threshold=50  # Lower threshold
        )
        
        result["pipeline"] = "fast_response"
        return result
    
    async def _multi_agent_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Multi-agent response using Supervisor"""
        
        # Prepare context for supervisor
        supervisor_context = {
            "subject": context.get("subject", "General"),
            "session_id": context.get("session_id"),
            "user_id": context.get("user_id"),
            "exam_mode": context.get("exam_mode", "General"),
            "request_visual": routing_decision.enable_visual,
            "use_agent_negotiation": True,  # Enable negotiation
            "student_profile": await self._get_student_profile(context),
            "memory_context": await self._get_memory_context(context)
        }
        
        # Run supervisor with enhanced features
        try:
            result = await self.supervisor.run_enhanced(message, supervisor_context)
        except Exception as e:
            logger.warning(f"Enhanced supervisor failed, using base: {e}")
            result = await self.supervisor.run(message, supervisor_context)
        
        # Convert to standard format
        return self._format_supervisor_result(result, routing_decision)
    
    async def _hybrid_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Hybrid reasoning (Neural + Symbolic + Graph)"""
        
        if not self.hybrid_engine:
            # Fall back to multi-agent
            return await self._multi_agent_response(message, context, routing_decision)
        
        # Run hybrid reasoning
        hybrid_context = {
            "subject": context.get("subject", "General"),
            "domain": context.get("subject", "General"),
            "age": 17,  # Default assumption
            **context
        }
        
        try:
            hybrid_result = await self.hybrid_engine.reason(message, hybrid_context)
            
            # Also run multi-agent for explanation
            supervisor_context = {
                "subject": context.get("subject", "General"),
                "session_id": context.get("session_id"),
                "user_id": context.get("user_id"),
                "request_visual": routing_decision.enable_visual,
                "symbolic_solution": hybrid_result.symbolic_proof,
                "knowledge_graph": {
                    "concepts": [c.name for c in hybrid_result.graph_context.concepts] if hybrid_result.graph_context else []
                } if hybrid_result.graph_context else None
            }
            
            supervisor_result = await self.supervisor.run(message, supervisor_context)
            
            # Merge results
            return self._merge_hybrid_results(supervisor_result, hybrid_result, routing_decision)
            
        except Exception as e:
            logger.error(f"Hybrid reasoning failed: {e}")
            return await self._multi_agent_response(message, context, routing_decision)
    
    async def _react_agentic_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Full ReAct with verification for deep reasoning"""
        
        # Import verified ReAct agent
        from agents.agentic_doubt_resolver import create_agentic_doubt_resolver
        
        agent = create_agentic_doubt_resolver({
            'emergent_llm_key': self.llm_api_key,
            'max_iterations': routing_decision.max_iterations,
            'global_timeout': routing_decision.timeout_seconds,
            'enable_verification': routing_decision.enable_verification,
            'verbose': True
        })
        
        agent_context = {
            "subject": context.get("subject", "General"),
            "user_id": context.get("user_id"),
            "session_id": context.get("session_id"),
            "student_profile": await self._get_student_profile(context)
        }
        
        try:
            result = await agent.run(message, agent_context)
            return self._format_agentic_result(result, routing_decision)
        except Exception as e:
            logger.error(f"ReAct agent failed: {e}")
            return await self._multi_agent_response(message, context, routing_decision)
    
    async def _visual_sync_response(
        self,
        message: str,
        context: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Synchronized visual + text response"""
        
        # Run multi-agent with visual emphasis
        context["request_visual"] = True
        context["visual_priority"] = True
        
        result = await self._multi_agent_response(message, context, routing_decision)
        
        # Ensure visual is included
        if not result.get("visual_data") and not result.get("response", {}).get("visual"):
            # Generate visual separately
            try:
                from services.whiteboard_engine import generate_whiteboard_visual
                visual = generate_whiteboard_visual(
                    message,
                    context.get("subject", "General")
                )
                result["visual_data"] = visual
            except Exception as e:
                logger.warning(f"Visual generation failed: {e}")
        
        return result
    
    async def _get_student_profile(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get student profile from context or DB"""
        profile = {
            "mastery_level": 50,
            "interests": ["cricket", "gaming"],
            "board": "CBSE",
            "exam": context.get("exam_mode", "JEE")
        }
        
        if self.db is not None and context.get("user_id"):
            try:
                user_doc = await self.db.users.find_one({"user_id": context["user_id"]})
                if user_doc:
                    profile["name"] = user_doc.get("full_name", "").split()[0]
                    profile["mastery_level"] = user_doc.get("overall_mastery", 50)
            except Exception:
                pass
        
        return profile
    
    async def _get_memory_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory context for personalization"""
        memory_context = {
            "recent_topics": [],
            "mastery_level": 50,
            "continuity": {}
        }
        
        if self.db is not None and context.get("user_id"):
            try:
                from services.memory_service import MemoryService
                memory_service = MemoryService(self.db)
                
                recent = await memory_service.get_conversation_context(
                    session_id=context.get("session_id", ""),
                    user_id=context["user_id"],
                    window_size=5
                )
                memory_context["recent_context"] = recent
            except Exception as e:
                logger.debug(f"Memory context failed: {e}")
        
        return memory_context
    
    def _generate_greeting(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized greeting"""
        import random
        from datetime import datetime
        
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_greeting = "Good morning"
            emoji = "🌅"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
            emoji = "☀️"
        elif 17 <= hour < 21:
            time_greeting = "Good evening"
            emoji = "🌆"
        else:
            time_greeting = "Hey there"
            emoji = "🌙"
        
        greetings = [
            f"{time_greeting}! {emoji} I'm your AI tutor. What would you like to learn today?",
            f"Hey! 👋 Great to see you! Ask me anything - I'll explain it like a friend!",
            f"{time_greeting}! {emoji} Ready to tackle some concepts together?",
            f"Hi! 🚀 Let's make learning fun. What's on your mind?",
        ]
        
        return {
            "response": {
                "default_view": {
                    "greeting": random.choice(greetings),
                    "main_content": {
                        "content": "I can help with Physics, Chemistry, Biology, Mathematics, and more! 📚",
                        "type": "markdown"
                    }
                },
                "intent": "greeting"
            },
            "detected_subject": "General",
            "generation_time": 0.01,
            "pipeline": "fast_greeting"
        }
    
    def _generate_gratitude_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate warm response for gratitude/thank you messages"""
        import random
        
        # Get student name if available
        name = context.get('student_profile', {}).get('name', '')
        name_suffix = f", {name}" if name else ""
        
        responses = [
            f"You're welcome{name_suffix}! 😊 Happy to help! Is there anything else you'd like to learn?",
            f"Anytime{name_suffix}! 🌟 That's what I'm here for. Feel free to ask more questions!",
            f"Glad I could help{name_suffix}! 💪 Keep up the great learning spirit! What's next?",
            f"My pleasure{name_suffix}! 📚 Learning together is awesome. Ask away anytime!",
            f"Happy to help{name_suffix}! 🚀 Your curiosity is inspiring. What else can I explain?",
            f"No problem at all{name_suffix}! 🎯 Helping you understand is my favorite thing to do!",
        ]
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": random.choice(responses),
                        "type": "markdown"
                    }
                },
                "intent": "gratitude"
            },
            "detected_subject": "General",
            "generation_time": 0.01,
            "pipeline": "fast_gratitude"
        }
    
    def _generate_acknowledgment_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for acknowledgments (ok, got it, cool, etc.)"""
        import random
        
        responses = [
            "Great! 👍 Let me know if you have any more questions!",
            "Perfect! 🎯 Feel free to ask anything else!",
            "Awesome! 💡 I'm here whenever you need me!",
            "Cool! 🌟 Ready to help with your next question!",
            "Got it! 📚 What would you like to explore next?",
        ]
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": random.choice(responses),
                        "type": "markdown"
                    }
                },
                "intent": "acknowledgment"
            },
            "detected_subject": "General",
            "generation_time": 0.01,
            "pipeline": "fast_acknowledgment"
        }
    
    def _format_supervisor_result(
        self,
        result: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Format supervisor result to standard structure"""
        
        # Extract main content
        mentor_content = ""
        if result.get("mentor", {}).get("content"):
            mentor_content = result["mentor"]["content"]
        elif result.get("mentor", {}).get("success"):
            mentor_content = result["mentor"].get("content", "")
        
        professor_content = ""
        if result.get("professor", {}).get("content"):
            professor_content = result["professor"]["content"]
        
        # Combine for main content
        main_content = mentor_content
        if professor_content and professor_content != mentor_content:
            main_content += f"\n\n**Additional Details:**\n{professor_content[:500]}"
        
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": main_content,
                        "type": "markdown"
                    }
                },
                "progressive_sections": {
                    "explanation": main_content,
                    "formal": professor_content
                },
                "intent": result.get("intent", "concept")
            },
            "visual_data": result.get("visual"),
            "detected_subject": result.get("metadata", {}).get("subject"),
            "agents_used": result.get("metadata", {}).get("agents_used", []),
            "pipeline": "multi_agent",
            "verification": result.get("verification"),
            "hybrid_reasoning": result.get("hybrid_reasoning")
        }
    
    def _format_agentic_result(
        self,
        result: Dict[str, Any],
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Format agentic result to standard structure"""
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": result.get("content", ""),
                        "type": "markdown"
                    }
                },
                "intent": "deep_reasoning"
            },
            "detected_subject": result.get("metadata", {}).get("subject"),
            "pipeline": "react_agentic",
            "agentic_info": {
                "tools_used": result.get("tools_used", []),
                "iterations": result.get("iterations", 0),
                "revisions": result.get("revisions", 0),
                "verified": result.get("metadata", {}).get("verified", False)
            },
            "reasoning_chain": result.get("reasoning_chain", [])
        }
    
    def _merge_hybrid_results(
        self,
        supervisor_result: Dict[str, Any],
        hybrid_result: Any,
        routing_decision: Any
    ) -> Dict[str, Any]:
        """Merge hybrid reasoning with supervisor result"""
        base = self._format_supervisor_result(supervisor_result, routing_decision)
        
        # Add hybrid reasoning data
        base["hybrid_reasoning"] = {
            "mode": hybrid_result.reasoning_mode.value if hasattr(hybrid_result, 'reasoning_mode') else "hybrid",
            "symbolic_proof": hybrid_result.symbolic_proof if hasattr(hybrid_result, 'symbolic_proof') else None,
            "confidence": hybrid_result.confidence if hasattr(hybrid_result, 'confidence') else 0.7,
            "verification_passed": hybrid_result.verification_passed if hasattr(hybrid_result, 'verification_passed') else False,
            "recommendations": hybrid_result.recommendations if hasattr(hybrid_result, 'recommendations') else []
        }
        
        # Add knowledge graph context
        if hasattr(hybrid_result, 'graph_context') and hybrid_result.graph_context:
            base["knowledge_graph"] = {
                "concepts": [c.name for c in hybrid_result.graph_context.concepts[:5]],
                "prerequisites": [p.name for p in hybrid_result.graph_context.prerequisites[:3]],
                "applications": [a.name for a in hybrid_result.graph_context.applications[:3]]
            }
        
        base["pipeline"] = "hybrid_reasoning"
        return base
    
    def _error_response(
        self,
        message: str,
        error: str,
        generation_time: float
    ) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": """I encountered an issue processing your question. Let me try a different approach!

Could you:
1. Try rephrasing your question?
2. Ask about a specific part of the topic?

I'm here to help! 🤝""",
                        "type": "markdown"
                    }
                },
                "intent": "error"
            },
            "error": error,
            "generation_time": generation_time,
            "pipeline": "error_fallback",
            "orchestration": {
                "pipeline": "error_fallback",
                "complexity": "unknown",
                "confidence": 0.0,
                "agents_activated": [],
                "tools_enabled": [],
                "generation_time": generation_time,
                "routing_reasoning": f"Error occurred: {error}"
            }
        }


# Factory function
_orchestrator_instance: Optional[UnifiedAIOrchestrator] = None


def get_unified_orchestrator(db, llm_api_key: str = None) -> UnifiedAIOrchestrator:
    """Get or create unified orchestrator"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = UnifiedAIOrchestrator(db, llm_api_key)
    return _orchestrator_instance

