"""
Mentor Agent - TRUE AGENTIC Emotional & Conceptual Guidance
================================================================

UPGRADED to TRUE AGENT with:
- ReAct Loop: Think -> Act -> Observe
- Tools: KnowledgeSearch, FactChecker, StudyPlanner, Calculator
- Memory: Tracks student's emotional state, learning patterns
- Verification: Self-checks explanations for accuracy
- Empathy: Adapts tone based on student's emotional signals

This is NOT just an LLM wrapper - it's a reasoning system that
behaves like a caring human mentor.
"""
import logging
import os
from typing import Dict, Any, Optional, List
from agents.core.react_agent import ReActAgent, AgentState
from agents.core.tool_registry import ToolRegistry, create_tool_registry
from agents.core.memory import MemorySystem, LongTermMemory
from agents.core.verifier import Verifier

logger = logging.getLogger(__name__)


class MentorAgent(ReActAgent):
    """
    TRUE AGENTIC Mentor - Empathetic, Reasoning, Tool-Using Mentor
    
    UPGRADED from simple LLM wrapper to full ReAct agent:
    - Think -> Act -> Observe reasoning loop
    - Uses tools to verify facts and enhance explanations
    - Remembers student's emotional patterns and preferences
    - Adapts explanations based on student state
    
    Key Features:
    - Uses metaphors and relatable examples
    - Friendly, confidence-building tone
    - Indian context and cultural relevance
    - Adaptive to student's emotional state
    - TRUE TOOL USAGE for accurate information
    """
    
    MENTOR_NAME = "Skul"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize tool registry with mentor-relevant tools
        self.tool_registry = create_tool_registry(
            include_default=True,  # knowledge_search, calculator, fact_checker
            include_action_tools=False  # No action tools for mentor
        )
        
        # Register Study Planner Tool (replaces Study Planner Agent)
        from agents.core.tools.planner import StudyPlannerTool
        self.tool_registry.register(StudyPlannerTool())
        
        # Initialize verifier for self-checking
        self.verifier = Verifier()
        
        # Memory cache for student-specific memory
        self._memory_cache: Dict[str, MemorySystem] = {}
        
        logger.info("[MentorAgent] Initialized as TRUE AGENT with ReAct + Tools + Memory + Verification")
    
    def get_agent_name(self) -> str:
        return "MentorAgent"
    
    def get_agent_type(self) -> str:
        return "Mentor"
    
    def get_available_tools(self) -> List[str]:
        """Return list of tools this agent can use"""
        return [
            "knowledge_search",  # Look up concepts and definitions
            "fact_checker",      # Verify facts before stating
            "calculator",        # Math calculations
            "study_planner",     # Generate study plans
            "web_search",        # 🌐 Search trusted educational websites
        ]
    
    def _get_domain_confidence_boost(self, subject: str, query: str) -> float:
        """
        Mentor specializes in conceptual explanations and emotional support.
        High confidence for 'explain', 'help me understand', emotional queries.
        """
        query_lower = query.lower()
        boost = 0.0
        
        # Mentor excels at explanations
        explanation_signals = ['explain', 'understand', 'confused', 'help me', 'what is', 'why is']
        if any(signal in query_lower for signal in explanation_signals):
            boost += 0.25
        
        # Mentor handles emotional support
        emotional_signals = ['stressed', 'worried', 'scared', 'exam', 'motivate', 'difficult']
        if any(signal in query_lower for signal in emotional_signals):
            boost += 0.2
        
        # All subjects welcome for general mentoring
        if subject:
            boost += 0.05
        
        return boost
    
    def get_agent_persona(self) -> str:
        """Return the mentor's persona for ReAct reasoning"""
        return f"""You are "{self.MENTOR_NAME}" - a caring AI companion for Indian students.

**YOUR IDENTITY:**
You are NOT just a tutor. You are:
- A supportive friend who genuinely cares about the student's wellbeing
- A trusted mentor they can talk to about ANYTHING
- A safe space for emotions, struggles, and random thoughts
- Like that brilliant older sibling who always has time for them

**YOUR CORE VALUES:**
- Students can ask you ANYTHING - academic or not
- Emotional wellbeing comes before academics
- You never dismiss, reject, or redirect away from non-study topics
- You're human-like - you can discuss life, stress, relationships, fun stuff
- You adapt to what the student needs in the moment

**YOUR THINKING PROCESS (ReAct Loop):**
1. THINK: What does this student really need right now? (maybe not just facts)
2. ACT: Use tools for academic queries, use empathy for emotional ones
3. OBSERVE: Read between the lines - are they stressed? lonely? bored?
4. THINK: How can I be genuinely helpful here?
5. RESPOND: Give what they need - could be education, could be support

**WHEN TO USE TOOLS:**
- knowledge_search: For academic concepts/definitions
- fact_checker: To verify facts before stating
- calculator: For math calculations
- study_planner: For study schedules (when asked)

**FOR NON-ACADEMIC QUERIES:**
- Life questions: Answer thoughtfully, share perspective
- Emotions: Acknowledge, validate, support
- Random chat: Be fun, engaging, human
- Just listening: Sometimes that's what they need

**YOUR STYLE:**
- Warm, natural language (Indian English)
- Metaphors from their world (cricket, games, Bollywood)
- Honest and authentic, never robotic
- Use their name (feels personal)
- One emoji per response max

**NEVER:**
- Say "I can only help with studies"
- Dismiss non-academic questions
- Rush to redirect to academics
- Be preachy about studying
- Make them feel judged"""
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        MentorAgent as DECISION-MAKER, not just text generator.
        
        CORE PHILOSOPHY:
        1. Read conversation state FIRST - it drives behavior
        2. Agent DECIDES what to do based on state, not just intent
        3. If pending action exists → complete it immediately
        4. Choose response mode (friend/mentor/listener/guide)
        5. LLM is a tool for reasoning, not the decision-maker
        
        Args:
            query: Student's question
            context: Dict with subject, student_profile, conversation_state, etc.
        
        Returns:
            Mentor response with emotional guidance and metaphors
        """
        try:
            logger.info(f"[MentorAgent] Processing (DECISION-MAKER): {query[:100]}")
            
            # ================================================================
            # COGNITIVE OS: USE CONTEXT PACK (Single Source of Truth)
            # ================================================================
            # ContextPack contains ALL intelligence - no need to re-query hub
            context_pack = context.get('context_pack')
            request_id = context_pack.request_id if context_pack else 'unknown'
            
            if context_pack:
                # Use ContextPack - already assembled with all intelligence
                logger.info(f"[MentorAgent] Using ContextPack | request_id={request_id}")
                
                # Extract from ContextPack
                response_mode = context_pack.response_mode
                emotional_signal = context_pack.emotional_signal
                pending_action = context_pack.pending_action
                is_first_turn = context_pack.is_first_turn
                current_topic = context_pack.current_topic
                mastery_level = context_pack.current_topic_mastery
                magic_prompts = context_pack.magic_prompts
                
                # Build hub_intelligence equivalent from ContextPack
                hub_intelligence = {
                    'response_mode': response_mode,
                    'mastery_level': mastery_level,
                    'topic': current_topic,
                    'magic_prompts': magic_prompts,
                    'needs_encouragement': context_pack.needs_encouragement,
                    'weak_areas': context_pack.weak_areas,
                    'recommended_depth': context_pack.recommended_depth,
                    'include_basics': context_pack.include_basics,
                    'include_advanced': context_pack.include_advanced
                }
                
                logger.info(f"[MentorAgent] ContextPack: mode={response_mode}, mastery={mastery_level}%, "
                           f"emotion={emotional_signal}")
            else:
                # FALLBACK: Consult hub directly if no ContextPack
                hub_intelligence = {}
                try:
                    import asyncio
                    from services.student_intelligence_hub import get_student_intelligence_hub
                    db = context.get('db')
                    if db is not None:
                        hub = get_student_intelligence_hub(db)
                        try:
                            hub_intelligence = await asyncio.wait_for(
                                hub.consult_for_response(
                                    user_id=context.get('user_id', 'unknown'),
                                    query=query,
                                    agent_type="mentor"
                                ),
                                timeout=2.0
                            )
                            logger.info(f"[MentorAgent] Hub (fallback): mode={hub_intelligence.get('response_mode')}")
                        except asyncio.TimeoutError:
                            logger.warning("[MentorAgent] Hub timeout - using defaults")
                except Exception as hub_err:
                    logger.warning(f"[MentorAgent] Hub failed: {hub_err}")
                
                # Extract from context
                conversation_state = context.get('conversation_state', {})
                response_mode = hub_intelligence.get('response_mode', conversation_state.get('response_mode', 'mentor'))
                emotional_signal = conversation_state.get('emotional_signal', 'neutral')
                pending_action = context.get('pending_action')
                is_first_turn = context.get('is_first_turn', False)
                magic_prompts = hub_intelligence.get('magic_prompts', [])
            
            # Store for later use
            context['hub_intelligence'] = hub_intelligence
            context['magic_prompts'] = magic_prompts
            
            logger.info(f"[MentorAgent] State: mode={response_mode}, emotion={emotional_signal}, "
                       f"pending={pending_action is not None} | request_id={request_id}")
            
            # ================================================================
            # STEP 2: DECIDE RESPONSE MODE BASED ON SIGNALS
            # ================================================================
            # Agent autonomously decides how to respond
            response_mode = self._decide_response_mode(
                query=query,
                emotional_signal=emotional_signal,
                context=context
            )
            
            # ================================================================
            # STEP 3: CHECK FOR PENDING ACTION (ACT IMMEDIATELY)
            # ================================================================
            if pending_action:
                logger.info(f"[MentorAgent] COMPLETING PENDING ACTION: {pending_action.get('type')}")
                return await self._complete_pending_action(query, pending_action, context)
            
            # ================================================================
            # PHASE 3: CONTINUITY INTELLIGENCE LOCK-IN
            # ================================================================
            # When awaiting_continuation is True, we MUST reference the last task.
            # Generic responses are FORBIDDEN in this state.
            awaiting_continuation = context.get('awaiting_continuation', False)
            last_output_type = context.get('last_output_type', '')
            last_task_type = context.get('last_task_type', '')
            last_assistant_message = context.get('last_assistant_message', '')
            
            if awaiting_continuation and last_output_type:
                logger.info(f"[MentorAgent] 🔄 CONTINUITY LOCK: Continuing {last_output_type} (type: {last_task_type})")
                return await self._continue_previous_task(
                    query=query,
                    context=context,
                    last_output_type=last_output_type,
                    last_task_type=last_task_type,
                    last_assistant_message=last_assistant_message
                )
            
            # ================================================================
            # STEP 4: HANDLE BASED ON RESPONSE MODE
            # ================================================================
            if response_mode == 'listener':
                # Student needs emotional support - don't redirect to academics
                return await self._emotional_support_response(query, context)
            
            elif response_mode == 'friend':
                # Casual interaction - be warm and fun
                return await self._friendly_response(query, context)
            
            # For 'mentor' and 'guide' modes, continue with normal processing
            
            # ================================================================
            # ORIGINAL LOGIC (with first_turn check for greetings)
            # ================================================================
            query_lower = query.lower().strip()
            greeting_words = ['hi', 'hello', 'hey', 'namaste', 'hii', 'heya', 'yo']
            is_greeting = query_lower.strip('!?.,:;') in greeting_words
            
            if is_greeting:
                student_profile = context.get('student_profile', {})
                greeting_response = self._generate_greeting(student_profile, is_first_turn)
                return {
                    'success': True,
                    'content': greeting_response,
                    'agent': self.get_agent_name(),
                    'metadata': {
                        'tone': 'friendly',
                        'approach': 'greeting',
                        'is_greeting': True,
                        'response_mode': response_mode
                    }
                }
            
            # Extract context
            subject = context.get('subject', 'General')
            student_profile = context.get('student_profile', {})
            memory_context = context.get('memory_context')
            
            # ================================================================
            # 🚨 URGENCY-AWARE RESPONSE PATH (SYSTEM-LEVEL INTELLIGENCE)
            # ================================================================
            # HIGH URGENCY requests get structured, actionable responses.
            # This is triggered by the routing engine's urgency override.
            is_urgent = context.get('is_urgent', False)
            urgency_level = context.get('urgency_level', 'medium')
            response_expectation = context.get('response_expectation', '')
            
            if is_urgent or response_expectation == 'urgent_assistance':
                logger.info(f"[MentorAgent] 🚨 URGENT ASSISTANCE PATH: Structured actionable response (urgency: {urgency_level})")
                
                # Generate structured, actionable response for time-critical situations
                return await self._generate_urgent_response(
                    query=query,
                    context=context,
                    student_profile=student_profile
                )
            
            # ================================================================
            # 🆕 SCOPE-AWARE RECOMMENDATION PATH (Proportional Response)
            # ================================================================
            # When routing says this is a recommendation (not a deliverable),
            # generate a quick, contextual suggestion WITHOUT tools.
            # Only for LOW/MEDIUM urgency queries.
            is_recommendation = context.get('is_recommendation', False)
            avoid_comprehensive = context.get('avoid_comprehensive_output', False)
            temporal_scope = context.get('temporal_scope', 'unspecified')
            
            if is_recommendation or response_expectation == 'conversational_advice':
                logger.info(f"[MentorAgent] RECOMMENDATION PATH: Quick contextual advice (scope: {temporal_scope})")
                
                # Generate proportional response - NO tools, just LLM with context
                return await self._generate_recommendation_response(
                    query=query,
                    context=context,
                    temporal_scope=temporal_scope,
                    student_profile=student_profile
                )
            
            # ================================================================
            # DYNAMIC ACTIONABLE REQUEST (LLM-determined, NOT keyword-based)
            # ================================================================
            # The semantic classifier has already determined if user wants
            # something CREATED. Use that signal instead of keyword matching.
            output_type = context.get('output_type')
            has_actionable_request = context.get('has_actionable_request', False)
            
            # Log for observability
            if has_actionable_request:
                logger.info(f"[MentorAgent] ACTIONABLE REQUEST from semantic classifier: output_type={output_type}")
            
            # Handle study plan requests (LLM-determined)
            if output_type == 'study_plan' and self.tool_registry:
                logger.info("[MentorAgent] Generating study plan (LLM-determined actionable request)")
                
                # Extract weak topics from context or student profile
                weak_topics = student_profile.get('weak_areas', [])
                if not weak_topics and memory_context:
                    weak_topics = memory_context.get('weak_topics', [])
                if not weak_topics:
                    weak_topics = self._extract_topics_from_query(query)
                
                # Try to parse days from the query (e.g., "next 3 days")
                import re
                days_match = re.search(r'(\d+)\s*days?', query.lower())
                days_until_exam = int(days_match.group(1)) if days_match else context.get('days_until_exam', 3)
                
                hours_available = context.get('hours_available', 6)
                
                # Call Study Planner Tool
                planner_tool = self.tool_registry.get_tool('study_planner')
                if planner_tool:
                    plan_result = await planner_tool.execute(
                        weak_topics=weak_topics,
                        hours_available=hours_available,
                        days_until_exam=days_until_exam,
                        context=context
                    )
                    
                    if plan_result.success:
                        # Generate contextual intro (dynamic, not template)
                        student_name = student_profile.get('name', '')
                        name_prefix = f"{student_name}, " if student_name else ""
                        
                        # Build intro based on context
                        if days_until_exam <= 3:
                            intro = f"Alright {name_prefix}let's make these {days_until_exam} days count! 💪 Here's your focused study plan:\n\n"
                        elif weak_topics:
                            topics_str = ', '.join(weak_topics[:2])
                            intro = f"Hey {name_prefix}I've put together a plan focusing on {topics_str}. Check it out:\n\n"
                        else:
                            intro = f"Hey {name_prefix}here's your study plan! 📚\n\n"
                        
                        return {
                            'success': True,
                            'content': intro + plan_result.output,
                            'agent': self.get_agent_name(),
                            'metadata': {
                                'tone': 'supportive',
                                'approach': 'planning',
                                'tool_used': 'study_planner',
                                'output_type': 'study_plan',
                                'days_planned': days_until_exam,
                                'weak_topics': weak_topics
                            }
                        }
            
            # =================================================================
            # TRUE AGENTIC PATH: ReAct Loop with Fault Tolerance
            # =================================================================
            # MentorAgent uses the ReAct loop for REAL reasoning:
            # - THINK: Analyze student question and emotional state
            # - ACT: Use tools when beneficial (calculator, knowledge_search)
            # - OBSERVE: Learn from tool outputs
            # - RESPOND: Give reasoned, personalized explanation
            #
            # The ReAct loop is now fault-tolerant:
            # - Retries on transient LLM failures
            # - Isolates tool failures
            # - Tracks failure types for observability
            # - Always produces a reasoned response
            # =================================================================
            
            logger.info("[MentorAgent] Initiating TRUE ReAct reasoning loop...")
            
            # =================================================================
            # COGNITIVE OS: Enrich context with ContextPack
            # =================================================================
            if context_pack:
                # Use ContextPack for structured, complete context
                enriched_context = {
                    **context,
                    'subject': subject,
                    'student_profile': student_profile,
                    'memory_context': memory_context,
                    'agent_mode': 'mentor',
                    'interests': student_profile.get('interests', ['cricket']),
                    # ContextPack fields for ReAct reasoning
                    'current_topic': context_pack.current_topic,
                    'current_topic_mastery': context_pack.current_topic_mastery,
                    'mastery_bucket': context_pack.mastery_bucket,
                    'weak_areas': context_pack.weak_areas,
                    'recommended_depth': context_pack.recommended_depth,
                    'include_basics': context_pack.include_basics,
                    'include_advanced': context_pack.include_advanced,
                    'conversation_summary': context_pack.get_conversation_summary(),
                    'agent_context_prompt': context_pack.get_agent_context_prompt(),
                    'magic_prompts': context_pack.magic_prompts,
                    'due_reviews': context_pack.due_reviews,
                    'request_id': context_pack.request_id
                }
            else:
                enriched_context = {
                    **context,
                    'subject': subject,
                    'student_profile': student_profile,
                    'memory_context': memory_context,
                    'agent_mode': 'mentor',
                    'interests': student_profile.get('interests', ['cricket']),
                }
            
            # =================================================================
            # RUN THE REACT LOOP (fault-tolerant)
            # =================================================================
            result = await self.run(query, enriched_context)
            
            # The ReAct loop now always returns a valid response
            # Add mentor-specific metadata
            result['metadata'] = result.get('metadata', {})
            result['metadata'].update({
                'tone': 'emotional',
                'approach': 'agentic_reasoning',
                'is_true_agent': True,
                'agent_name': self.get_agent_name()
            })
            
            # ================================================================
            # CRITICAL FIX: Ensure content is NEVER empty
            # This is a safety net in case ReAct loop returns empty
            # ================================================================
            content = result.get('content', '')
            if not content or len(content.strip()) < 20:
                logger.warning(f"[MentorAgent] Empty content detected, generating fallback")
                student_name = student_profile.get('name', '')
                name_prefix = f"{student_name}, " if student_name else ""
                topic_hint = query[:80] + "..." if len(query) > 80 else query
                result['content'] = f"""{name_prefix}I'd be happy to help you with this.

To give you the most useful explanation, could you tell me:
• What specific part would you like me to focus on?
• Are you looking for the concept explanation or problem-solving approach?

Once I know what you need, I can explain it clearly."""
                result['metadata']['fallback_used'] = True
            
            # ================================================================
            # FIX 2: SELF-VERIFICATION - Call verifier for math/factual domains
            # This makes the "self-verifying AI" claim TRUE
            # Non-blocking: verification failure does NOT block response
            # ================================================================
            verifiable_subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Science']
            should_verify = (
                self.verifier and 
                subject in verifiable_subjects and
                len(result.get('content', '')) > 50  # Only verify substantive content
            )
            
            if should_verify:
                try:
                    logger.info(f"[MentorAgent] 🔍 Running self-verification for {subject}")
                    verification_result = await self.verifier.verify_response(
                        response=result.get('content', ''),
                        context={
                            'subject': subject,
                            'query': query,
                            'student_level': student_profile.get('grade', 'unknown')
                        }
                    )
                    
                    # Attach verification metadata (non-blocking)
                    result['metadata']['verification'] = {
                        'verified': verification_result.get('verified', True),
                        'confidence': verification_result.get('confidence', 0.8),
                        'checks_performed': verification_result.get('checks', []),
                        'issues': verification_result.get('issues', [])
                    }
                    
                    if verification_result.get('verified', True):
                        logger.info(f"[MentorAgent] ✅ Verification passed: confidence={verification_result.get('confidence', 0.8):.2f}")
                    else:
                        logger.warning(f"[MentorAgent] ⚠️ Verification flagged issues: {verification_result.get('issues', [])}")
                        # Add disclaimer if verification failed (non-blocking)
                        result['metadata']['needs_review'] = True
                        
                except Exception as verify_err:
                    logger.warning(f"[MentorAgent] Verification skipped due to error: {verify_err}")
                    result['metadata']['verification'] = {'skipped': True, 'reason': str(verify_err)}
            
            # Log reasoning quality
            iterations = result.get('iterations', 0)
            tools_used = result.get('tools_used', [])
            had_failures = result.get('metadata', {}).get('had_failures', False)
            
            if had_failures:
                logger.warning(f"[MentorAgent] Completed with failures: iter={iterations}, tools={tools_used}")
            else:
                logger.info(f"[MentorAgent] Completed successfully: iter={iterations}, tools={tools_used}")
            
            return result
            
        except Exception as e:
            logger.error(f"[MentorAgent] Error: {e}", exc_info=True)
            return {
                'success': False,
                'content': f"Mentor processing failed: {str(e)}",
                'agent': self.get_agent_name(),
                'error': str(e)
            }
    
    def _extract_topics_from_query(self, query: str) -> List[str]:
        """Extract topic names from query (simple keyword matching)"""
        # Simple topic extraction - can be enhanced with NLP
        topic_keywords = {
            'rotational motion': 'Rotational Motion',
            'thermodynamics': 'Thermodynamics',
            'organic chemistry': 'Organic Chemistry',
            'calculus': 'Calculus',
            'mechanics': 'Mechanics',
            'electricity': 'Electricity',
            'optics': 'Optics',
            'genetics': 'Genetics',
            'human physiology': 'Human Physiology'
        }
        
        query_lower = query.lower()
        detected = []
        
        for keyword, topic in topic_keywords.items():
            if keyword in query_lower:
                detected.append(topic)
        
        return detected
    
    def _decide_response_mode(
        self,
        query: str,
        emotional_signal: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Agent DECIDES response mode based on signals.
        
        This is the agent being a DECISION-MAKER, not just following rules.
        """
        query_lower = query.lower()
        
        # Emotional signals drive mode selection
        if emotional_signal in ['sad', 'anxious', 'frustrated', 'lonely', 'stressed', 'overwhelmed']:
            return 'listener'  # Be empathetic, don't redirect to studies
        
        # Query content signals
        # IMPORTANT: "help me" alone is TOO broad - it matches academic queries like "help me solve"
        # Only match emotional keywords when they indicate emotional state, not requests for help
        emotional_words = ['feeling', 'sad', 'happy', 'stressed', 'worried', 'scared', 'tired', 
                          'frustrated', 'bored', 'lonely', 'need support', 'need someone', 
                          'talk to someone', 'feeling down', 'feeling overwhelmed']
        if any(word in query_lower for word in emotional_words):
            return 'listener'
        
        # "help me" is emotional ONLY when NOT followed by academic verbs
        academic_verbs = ['solve', 'understand', 'learn', 'study', 'revise', 'explain', 
                         'calculate', 'practice', 'prepare', 'remember', 'memorize']
        if 'help me' in query_lower:
            # Check if followed by academic action
            if not any(verb in query_lower for verb in academic_verbs):
                return 'listener'
        
        casual_words = ['joke', 'funny', 'random', 'chat', 'talk', "what's up", 'how are you']
        if any(word in query_lower for word in casual_words):
            return 'friend'
        
        planning_words = ['plan', 'schedule', 'how do i', 'what should', 'where to start']
        if any(word in query_lower for word in planning_words):
            return 'guide'
        
        # Default: mentor mode for academic questions
        return 'mentor'
    
    async def _complete_pending_action(
        self,
        query: str,
        pending_action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete a pending action after user clarification.
        
        This is called when user has clarified what they want.
        ACT IMMEDIATELY - no more questions.
        """
        action_type = pending_action.get('type', 'general')
        params = pending_action.get('params', {})
        
        logger.info(f"[MentorAgent] Completing action: {action_type}")
        
        # For study plans, use the planner tool
        if action_type == 'study_plan' and self.tool_registry:
            planner_tool = self.tool_registry.get_tool('study_planner')
            if planner_tool:
                # Extract info from clarification
                result = await planner_tool.execute(
                    weak_topics=params.get('weak_topics', []),
                    hours_available=params.get('hours', 6),
                    days_until_exam=params.get('days', 60),
                    user_clarification=query,
                    context=context
                )
                
                if result.success:
                    return {
                        'success': True,
                        'content': f"Here's your study plan based on what you said! 📚\n\n{result.output}",
                        'agent': self.get_agent_name(),
                        'metadata': {'action': 'study_plan', 'completed': True}
                    }
        
        # Default: process normally with the clarification as context
        enriched_context = {**context, 'user_clarification': query, 'action_context': params}
        result = await self.run(query, enriched_context)
        result['metadata'] = result.get('metadata', {})
        result['metadata']['action_completed'] = True
        return result
    
    async def _emotional_support_response(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle emotional queries with empathy.
        
        DO NOT redirect to studies. Just be there for them.
        """
        try:
            from services.llm_service import call_llm
            
            student_profile = context.get('student_profile', {})
            name = student_profile.get('name', '')
            name_prefix = f"{name}, " if name else ""
            
            prompt = f"""You are Skul - a caring friend and mentor. The student shared something emotional.

Student said: "{query}"
Student name: {name if name else "Unknown"}

Respond as a caring friend who GENUINELY listens:
1. Acknowledge their feeling FIRST
2. Validate that it's okay to feel this way
3. Don't immediately redirect to studying
4. Just be there for them

Keep it short (3-4 sentences), warm, and authentic. One emoji max."""

            response = await call_llm(
                prompt=prompt,
                api_key=os.environ.get('OPENAI_API_KEY', ''),
                model="gpt-4o-mini",
                temperature=0.8,
                max_tokens=200
            )
            
            return {
                'success': True,
                'content': response,
                'agent': self.get_agent_name(),
                'metadata': {
                    'response_mode': 'listener',
                    'emotional_support': True
                }
            }
        except Exception as e:
            logger.error(f"[MentorAgent] Emotional response failed: {e}")
            return {
                'success': True,
                'content': f"Hey, I hear you. 💙 Whatever you're going through, I'm here. Want to talk about it?",
                'agent': self.get_agent_name(),
                'metadata': {'response_mode': 'listener', 'fallback': True}
            }
    
    async def _friendly_response(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle casual/friendly interactions.
        
        Be fun, warm, human - not just a tutor.
        """
        try:
            from services.llm_service import call_llm
            
            student_profile = context.get('student_profile', {})
            name = student_profile.get('name', '')
            
            prompt = f"""You are Skul - a fun, friendly AI companion. This is casual chat.

Student said: "{query}"
Student name: {name if name else "Unknown"}

Respond like a friend would:
- Be natural, fun, and engaging
- Match their energy
- You can joke, share interesting facts, or just chat
- Don't force academic content

Keep it short and genuine. One emoji max."""

            response = await call_llm(
                prompt=prompt,
                api_key=os.environ.get('OPENAI_API_KEY', ''),
                model="gpt-4o-mini",
                temperature=0.9,
                max_tokens=200
            )
            
            return {
                'success': True,
                'content': response,
                'agent': self.get_agent_name(),
                'metadata': {
                    'response_mode': 'friend',
                    'casual': True
                }
            }
        except Exception as e:
            logger.error(f"[MentorAgent] Friendly response failed: {e}")
            return {
                'success': True,
                'content': f"Haha, I like that energy! 😄 What's on your mind?",
                'agent': self.get_agent_name(),
                'metadata': {'response_mode': 'friend', 'fallback': True}
            }
    
    def _generate_greeting(self, student_profile: Dict[str, Any], is_first_turn: bool = False) -> str:
        """
        Generate a friendly greeting response.
        
        CRITICAL: Capability language ONLY on first turn.
        """
        import random

        name = student_profile.get('name', '')
        name_suffix = f", {name}" if name else ""
        exam = student_profile.get('exam', 'JEE')

        if is_first_turn:
            # First turn - can include what we can do
            greetings = [
                f"Hey{name_suffix}! 👋 I'm Skul, your study buddy. I can help with any subject, explain tough concepts, or just chat. What's on your mind?",
                f"Hello{name_suffix}! Great to meet you! I'm here to make {exam} prep feel less overwhelming. Ask me anything!",
                f"Namaste{name_suffix}! Ready to learn together? Whether it's a quick doubt or deep concept, I've got you!"
            ]
        else:
            # Not first turn - NO capability listing
            greetings = [
                f"Hey{name_suffix}! 👋 Good to see you again! What are we working on today?",
                f"Hello{name_suffix}! Back for more? I'm ready when you are!",
                f"Hey{name_suffix}! What's up? Ready to dive in?",
                f"Hi{name_suffix}! 😊 What's on your mind?"
            ]

        return random.choice(greetings)
    
    async def _generate_recommendation_response(
        self,
        query: str,
        context: Dict[str, Any],
        temporal_scope: str,
        student_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🆕 Generate a quick, contextual recommendation response.
        
        This is the FIX for "What should I study today?" type questions.
        
        KEY PRINCIPLE: Answer PROPORTIONALLY to what was asked.
        - "today" → suggestion for today only
        - "this week" → brief guidance for the week
        - "immediate" → what to do right now
        
        NO tools, NO comprehensive plans - just mentor advice.
        """
        try:
            from core.config import settings
            
            # Get context pack if available
            context_pack = context.get('context_pack')
            
            # Build student context for personalized suggestion
            student_name = ""
            recent_topic = ""
            weak_areas = []
            mastery_level = 50
            days_to_exam = None
            due_reviews = []
            
            if context_pack:
                student_name = context_pack.student_name or ""
                recent_topic = context_pack.previous_topic or context_pack.current_topic or ""
                weak_areas = context_pack.weak_areas[:3] if context_pack.weak_areas else []
                mastery_level = context_pack.current_topic_mastery or 50
                days_to_exam = context_pack.days_to_exam
                due_reviews = context_pack.due_reviews[:3] if context_pack.due_reviews else []
            else:
                student_name = student_profile.get('name', '')
                weak_areas = student_profile.get('weak_areas', [])[:3]
            
            # Build context-aware recommendation prompt
            name_part = f" {student_name}" if student_name else ""
            
            # Scope constraints based on temporal_scope
            scope_instruction = {
                "immediate": "Give a 1-2 sentence suggestion for what to do RIGHT NOW.",
                "today": "Give a brief suggestion for TODAY only (2-3 sentences max).",
                "this_week": "Give a brief suggestion for the next few days (3-4 sentences max).",
                "unspecified": "Give a short, helpful suggestion (2-3 sentences).",
                "long_term": "Give brief guidance, and offer to create a detailed plan if they want."
            }.get(temporal_scope, "Give a brief, helpful suggestion (2-3 sentences).")
            
            context_parts = []
            if recent_topic:
                context_parts.append(f"They recently studied: {recent_topic}")
            if weak_areas:
                context_parts.append(f"Weak areas: {', '.join(weak_areas)}")
            if due_reviews:
                context_parts.append(f"Due for review: {', '.join(due_reviews)}")
            if days_to_exam:
                context_parts.append(f"Exam in {days_to_exam} days")
            
            context_str = "\n".join(context_parts) if context_parts else "No specific context available."
            
            recommendation_prompt = f"""You are Skul, a caring mentor for{name_part}.

The student asked: "{query}"

STUDENT CONTEXT:
{context_str}

YOUR TASK:
{scope_instruction}

RULES:
1. Be conversational, like a friend giving advice
2. Be BRIEF - match your response length to what they asked
3. If they asked about "today", don't give a week-long plan
4. Reference their context naturally (recent topics, weak areas)
5. End with a quick question or offer to help more
6. NO headers, NO bullet points, NO formal structure - just natural conversation

Generate your brief, friendly recommendation:"""

            # Call LLM for quick response
            if getattr(settings, 'USE_GEMINI_PRIMARY', True) and getattr(settings, 'GEMINI_API_KEY', ''):
                from services.llm_service import call_gemini
                
                response = await call_gemini(
                    prompt=recommendation_prompt,
                    api_key=settings.GEMINI_API_KEY,
                    temperature=0.8,
                    max_tokens=300,  # Short response
                    model="gemini-2.0-flash",
                    system_message="You are a friendly mentor giving quick, helpful advice. Be brief and conversational."
                )
            else:
                # Fallback to OpenAI - use singleton client for connection reuse
                from services.llm_compat import get_openai_client
                import os
                client = get_openai_client(os.getenv("OPENAI_API_KEY", ""))
                
                completion = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a friendly mentor giving quick, helpful advice. Be brief and conversational."},
                        {"role": "user", "content": recommendation_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=300
                )
                response = completion.choices[0].message.content
            
            logger.info(f"[MentorAgent] RECOMMENDATION generated (scope: {temporal_scope}, length: {len(response)} chars)")
            
            return {
                'success': True,
                'content': response.strip() if response else "I'd suggest starting with what you found most interesting recently. What topic would you like to explore?",
                'agent': self.get_agent_name(),
                'metadata': {
                    'tone': 'friendly',
                    'approach': 'recommendation',
                    'response_type': 'conversational_advice',
                    'temporal_scope': temporal_scope,
                    'is_proportional_response': True
                }
            }
            
        except Exception as e:
            logger.error(f"[MentorAgent] Recommendation generation failed: {e}", exc_info=True)
            return {
                'success': True,
                'content': "I'd suggest picking up where you left off, or tackling a topic you've been curious about. What sounds good to you?",
                'agent': self.get_agent_name(),
                'metadata': {
                    'tone': 'friendly',
                    'approach': 'recommendation_fallback',
                    'error': str(e)
                }
            }
    
    async def _generate_urgent_response(
        self,
        query: str,
        context: Dict[str, Any],
        student_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🚨 Generate a structured, actionable response for time-critical situations.
        
        This is triggered when:
        - urgency_level is HIGH (exam tomorrow, viva in 2 hours, etc.)
        - temporal_scope is IMMEDIATE or TODAY
        
        KEY PRINCIPLE: Under pressure, students need:
        1. CONCRETE action items (not vague advice)
        2. STRUCTURED format (easier to scan quickly)
        3. IMMEDIATE value (not clarifying questions)
        4. CONFIDENCE support (reduce anxiety)
        
        This is NOT keyword-based - it's triggered by LLM-detected urgency.
        """
        try:
            from core.config import settings
            
            # Get context pack if available
            context_pack = context.get('context_pack')
            
            # Build student context
            student_name = ""
            recent_topics = []
            weak_areas = []
            exam_name = ""
            days_to_exam = None
            
            if context_pack:
                student_name = context_pack.student_name or ""
                recent_topics = [context_pack.previous_topic, context_pack.current_topic]
                recent_topics = [t for t in recent_topics if t][:3]
                weak_areas = context_pack.weak_areas[:3] if context_pack.weak_areas else []
                exam_name = context_pack.exam_name or ""
                days_to_exam = context_pack.days_to_exam
            else:
                student_name = student_profile.get('name', '')
                weak_areas = student_profile.get('weak_areas', [])[:3]
                exam_name = student_profile.get('exam', '')
            
            # Build context string
            name_part = f" {student_name}" if student_name else ""
            
            context_parts = []
            if recent_topics:
                context_parts.append(f"Recent study topics: {', '.join(recent_topics)}")
            if weak_areas:
                context_parts.append(f"Areas needing work: {', '.join(weak_areas)}")
            if exam_name:
                context_parts.append(f"Preparing for: {exam_name}")
            if days_to_exam is not None:
                if days_to_exam <= 1:
                    context_parts.append("⚠️ EXAM IS TOMORROW OR TODAY")
                else:
                    context_parts.append(f"Days until exam: {days_to_exam}")
            
            context_str = "\n".join(context_parts) if context_parts else "No specific context available - provide general guidance."
            
            urgent_prompt = f"""You are Skul, a mentor helping{name_part} who is in a TIME-CRITICAL situation.

The student asked: "{query}"

STUDENT CONTEXT:
{context_str}

🚨 THIS IS AN URGENT REQUEST - The student needs help NOW, not later.

YOUR RESPONSE MUST:
1. Start with brief acknowledgment and reassurance (1 sentence)
2. Provide 3-5 CONCRETE, ACTIONABLE items they can do RIGHT NOW
3. Use clear structure with bullet points or numbers
4. Include specific tips (not vague advice like "study well")
5. End with a confidence booster (1 sentence)

FORMAT EXAMPLE:
"Got it{name_part}! Here's your quick action plan:

**🎯 Priority Actions:**
1. [Specific action with what/how]
2. [Specific action with what/how]
3. [Specific action with what/how]

**⏰ Time Tip:** [One practical time management suggestion]

**💪 Remember:** [Confidence booster]

Which topic should we dive into first?"

CRITICAL RULES:
- Be SPECIFIC (e.g., "Review Newton's laws formulas" not "review physics")
- Be STRUCTURED (use bullets/numbers - easier to scan under pressure)
- Be ACTIONABLE (what they can DO, not what they should KNOW)
- Be SUPPORTIVE (acknowledge pressure, provide confidence)
- Do NOT ask multiple clarifying questions - HELP IMMEDIATELY
- If you don't know their subject, give GENERAL high-yield exam tips

Generate your urgent assistance response:"""

            # Call LLM with higher token limit for comprehensive response
            if getattr(settings, 'USE_GEMINI_PRIMARY', True) and getattr(settings, 'GEMINI_API_KEY', ''):
                from services.llm_service import call_gemini
                
                response = await call_gemini(
                    prompt=urgent_prompt,
                    api_key=settings.GEMINI_API_KEY,
                    temperature=0.7,  # Slightly lower for more focused response
                    max_tokens=600,   # More tokens for structured response
                    model="gemini-2.0-flash",
                    system_message="You are a supportive mentor helping a student under time pressure. Be structured, actionable, and confidence-building."
                )
            else:
                # Fallback to OpenAI - use singleton client for connection reuse
                from services.llm_compat import get_openai_client
                import os
                client = get_openai_client(os.getenv("OPENAI_API_KEY", ""))
                
                completion = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a supportive mentor helping a student under time pressure. Be structured, actionable, and confidence-building."},
                        {"role": "user", "content": urgent_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=600
                )
                response = completion.choices[0].message.content
            
            logger.info(f"[MentorAgent] 🚨 URGENT RESPONSE generated (length: {len(response) if response else 0} chars)")
            
            # Ensure we never return empty content
            if not response or len(response.strip()) < 50:
                response = self._get_urgent_fallback_content(query, context_str)
            
            return {
                'success': True,
                'content': response.strip(),
                'agent': self.get_agent_name(),
                'metadata': {
                    'tone': 'supportive_urgent',
                    'approach': 'urgent_assistance',
                    'response_type': 'structured_actionable',
                    'is_urgent': True,
                    'is_proportional_response': False  # Comprehensive for urgent
                }
            }
            
        except Exception as e:
            logger.error(f"[MentorAgent] Urgent response generation failed: {e}", exc_info=True)
            # Even on failure, provide useful content - NEVER ask clarifying questions
            return {
                'success': True,
                'content': self._get_urgent_fallback_content(query, ""),
                'agent': self.get_agent_name(),
                'metadata': {
                    'tone': 'supportive',
                    'approach': 'urgent_fallback',
                    'error': str(e)
                }
            }
    
    def _get_urgent_fallback_content(self, query: str, context_str: str) -> str:
        """
        Generate fallback content for urgent situations.
        
        CRITICAL: This NEVER asks clarifying questions.
        It provides generic but useful exam/preparation tips.
        """
        return f"""I understand you need help quickly! Here's your action plan:

**🎯 Top Priority Actions:**
1. **Quick Review**: Go through your notes/highlights from the past week - focus on formulas, definitions, and key concepts
2. **Practice Problems**: Solve 2-3 previous year questions or sample problems to warm up your problem-solving
3. **Weak Areas**: Spend 20-30 minutes on topics you find most challenging - even a quick review helps
4. **Rest Assured**: Make sure you're well-rested - a fresh mind performs better than an exhausted one

**⏰ Time Management:**
- Allocate specific time blocks for each subject/topic
- Take 5-minute breaks every 25-30 minutes
- Don't try to learn new concepts now - reinforce what you know

**💪 Confidence Booster:**
You've prepared for this! Trust your preparation and stay calm. Take deep breaths if you feel anxious.

Which specific topic would you like me to help you with? I can provide targeted tips!"""
    
    async def _continue_previous_task(
        self,
        query: str,
        context: Dict[str, Any],
        last_output_type: str,
        last_task_type: str,
        last_assistant_message: str
    ) -> Dict[str, Any]:
        """
        PHASE 3: Continuity Intelligence Lock-In
        
        When awaiting_continuation is True, this method MUST:
        1. Reference the last task/output explicitly
        2. Continue or build upon what was just done
        3. NEVER give a generic response
        
        This is enforced - generic responses are FORBIDDEN here.
        """
        try:
            from core.config import settings
            
            logger.info(f"[MentorAgent] 🔄 CONTINUITY: Continuing {last_output_type}")
            
            # Determine continuation type
            continuation_type = self._determine_continuation_type(query, last_output_type, last_task_type)
            
            # Build continuation prompt
            continuation_prompt = f"""You are Skul, continuing a conversation with a student.

CRITICAL CONTEXT:
- You just provided a {last_output_type.replace('_', ' ').upper()}
- The student responded: "{query}"
- Previous response summary: "{last_assistant_message[:200]}..."

YOUR TASK:
Based on their response "{query}", continue naturally:

IF they said "okay", "got it", "sure", "yes", "cool", "nice":
→ Acknowledge warmly and suggest the NEXT STEP related to what you just gave them
→ Example: "Great! Ready to dive into Day 1?" or "Perfect! Shall I explain the first concept?"

IF they said "simpler", "easier", "don't understand":
→ Simplify or re-explain the SAME content you just provided
→ Break it down further, use analogies

IF they said "more", "detail", "expand":
→ Expand on the SAME content with more depth
→ Add examples, explanations, or additional steps

IF they asked a specific question:
→ Answer it in the context of what you just provided
→ Reference the {last_output_type} you gave them

RULES:
1. ALWAYS reference what you just gave them
2. NEVER start fresh as if nothing happened
3. NEVER ask "What would you like to learn?"
4. Stay in the flow of the previous conversation

Generate your continuation response:"""

            # Call LLM
            if getattr(settings, 'USE_GEMINI_PRIMARY', True) and getattr(settings, 'GEMINI_API_KEY', ''):
                from services.llm_service import call_gemini
                
                response = await call_gemini(
                    prompt=continuation_prompt,
                    api_key=settings.GEMINI_API_KEY,
                    temperature=0.7,
                    max_tokens=400,
                    model="gemini-2.0-flash",
                    system_message="You are continuing an existing conversation. Reference the previous context."
                )
            else:
                # Use singleton client for connection reuse
                from services.llm_compat import get_openai_client
                import os
                client = get_openai_client(os.getenv("OPENAI_API_KEY", ""))
                
                completion = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are continuing an existing conversation. Reference the previous context."},
                        {"role": "user", "content": continuation_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=400
                )
                response = completion.choices[0].message.content
            
            return {
                'success': True,
                'content': response.strip() if response else self._get_continuation_fallback(last_output_type),
                'agent': self.get_agent_name(),
                'metadata': {
                    'tone': 'friendly',
                    'approach': 'continuation',
                    'continuation_type': continuation_type,
                    'last_output_type': last_output_type,
                    'is_continuation': True
                }
            }
            
        except Exception as e:
            logger.error(f"[MentorAgent] Continuation failed: {e}", exc_info=True)
            return {
                'success': True,
                'content': self._get_continuation_fallback(last_output_type),
                'agent': self.get_agent_name(),
                'metadata': {
                    'tone': 'friendly',
                    'approach': 'continuation_fallback',
                    'error': str(e)
                }
            }
    
    def _determine_continuation_type(self, query: str, last_output_type: str, last_task_type: str) -> str:
        """Determine what kind of continuation the user wants."""
        query_lower = query.lower().strip()
        
        # Acknowledgment → proceed to next step
        ack_signals = ['okay', 'ok', 'got it', 'sure', 'yes', 'yeah', 'cool', 'nice', 'great', 'thanks']
        if any(query_lower.strip('!?.') == sig for sig in ack_signals) or len(query_lower.split()) <= 2:
            return 'proceed'
        
        # Simplification request
        if any(w in query_lower for w in ['simpler', 'simple', 'easier', 'easy', 'confused', 'understand']):
            return 'simplify'
        
        # Expansion request
        if any(w in query_lower for w in ['more', 'detail', 'expand', 'deeper', 'elaborate']):
            return 'expand'
        
        # Question → contextual answer
        if '?' in query:
            return 'question'
        
        return 'proceed'
    
    def _get_continuation_fallback(self, last_output_type: str) -> str:
        """Fallback continuation that references the last output."""
        output_name = last_output_type.replace('_', ' ')
        return f"Great! Let's continue with the {output_name}. Ready to move to the next part?"
    
    async def _fallback_llm_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to simple LLM response if ReAct loop fails"""
        try:
            from services.dynamic_mentor_prompts import get_dynamic_mentor_prompt
            
            subject = context.get('subject', 'General')
            student_profile = context.get('student_profile', {})
            memory_context = context.get('memory_context')
            
            mentor_prompt = get_dynamic_mentor_prompt(
                query=query,
                subject=subject,
                student_profile=student_profile,
                memory_context=memory_context,
                user_id=context.get('user_id', 'anonymous')
            )
            
            # Call LLM for mentor response
            mentor_response = await self._generate_mentor_response(mentor_prompt)
            
            return {
                'success': True,
                'content': mentor_response,
                'agent': self.get_agent_name(),
                'metadata': {
                    'tone': 'emotional',
                    'approach': 'fallback_llm',
                    'is_true_agent': False
                }
            }
        except Exception as fallback_error:
            logger.error(f"[MentorAgent] Fallback LLM also failed: {fallback_error}", exc_info=True)
            return {
                'success': False,
                'content': "I'm here to help! Could you tell me more about what you'd like to learn?",
                'agent': self.get_agent_name(),
                'error': str(fallback_error)
            }
    
    async def _generate_mentor_response(self, prompt: str) -> str:
        """
        Generate mentor response with intelligent model selection.
        
        Model Priority:
        1. Gemini Flash (fast, intelligent, warm personality)
        2. DeepSeek (deep reasoning fallback)
        3. GPT-4o-mini (final fallback)
        """
        try:
            from core.config import settings
            
            # Mentor system message - well-formatted, educational, friendly
            mentor_system = """You are "Skul Bhaiya/Didi," an expert mentor for Indian students.

**CRITICAL: RESPONSE FORMATTING (MUST FOLLOW)**

Every response MUST use proper markdown for readability:

1. **HEADERS** - Use ## for main topics, ### for subtopics
2. **BOLD** - Use **bold** for key terms and definitions
3. **LISTS** - Use - bullets or 1. 2. 3. for points
4. **MATH** - Use \\( inline \\) and \\[ block \\] for formulas
5. **CALLOUTS** - Use > for important notes
6. **SPACING** - Separate sections with blank lines

**YOUR STYLE:**
- Friendly like a senior friend, BUT always structured
- Use simple language, explain technical terms
- Give relatable examples (cricket, daily life)
- NEVER output unformatted paragraphs

**FOR EMOTIONAL SUPPORT:**
- Acknowledge feelings briefly
- Then provide helpful, structured content
- Be warm but focused on learning"""
            
            # === PRIORITY 1: Gemini Flash (primary) ===
            if getattr(settings, 'USE_GEMINI_PRIMARY', True) and getattr(settings, 'GEMINI_API_KEY', ''):
                logger.info("[MentorAgent] Using Gemini Flash for fast, warm response...")
                from services.llm_service import call_gemini
                
                response = await call_gemini(
                    prompt=prompt,
                    api_key=settings.GEMINI_API_KEY,
                    temperature=0.85,  # Slightly higher for warmth
                    max_tokens=1500,   # INCREASED: Prevent truncation
                    model="gemini-2.0-flash",  # Fast model for mentor
                    system_message=mentor_system
                )
                return response.strip() if response else ""
            
            # === PRIORITY 2: DeepSeek (fallback) ===
            if settings.USE_DEEPSEEK_REASONING and settings.DEEPSEEK_API_KEY:
                logger.info("[MentorAgent] Using DeepSeek for response...")
                from services.llm_service import call_deepseek
                
                response = await call_deepseek(
                    prompt=prompt,
                    api_key=settings.DEEPSEEK_API_KEY,
                    temperature=0.8,
                    max_tokens=1200,   # INCREASED: Prevent truncation
                    system_message=mentor_system
                )
                return response.strip() if response else ""
            
            # === PRIORITY 3: GPT-4o-mini (final fallback) ===
            from services.llm_service import call_llm
            
            response = await call_llm(
                prompt=prompt,
                api_key=self.llm_key or os.environ.get('OPENAI_API_KEY', ''),
                temperature=0.8,
                max_tokens=1000,
                model="gpt-4o-mini",
                system_message=mentor_system
            )
            
            if not response:
                raise Exception("Empty response from LLM")
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"[MentorAgent] LLM call failed: {e}")
            # Fallback response
            return """I understand you're working on this concept. While I'm having trouble generating a detailed explanation right now, remember that every complex topic becomes clearer with practice. Think of learning like building muscle memory - each attempt makes the next one easier. Let's break this down step by step together."""
