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
    
    MENTOR_NAME = "Druv"
    
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
        ]
    
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
                    if db:
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
            
            # Check if this is a planning request
            planning_keywords = [
                'plan', 'schedule', 'timetable', 'how do i finish', 
                'overwhelmed', 'no time', 'too much', "can't finish",
                'study plan', 'what to study', 'where to start'
            ]
            
            is_planning_request = any(keyword in query_lower for keyword in planning_keywords)
            
            if is_planning_request and self.tool_registry:
                # Use Study Planner Tool
                logger.info("[MentorAgent] Detected planning request - using StudyPlannerTool")
                
                # Extract weak topics from context or student profile
                weak_topics = student_profile.get('weak_areas', [])
                if not weak_topics:
                    # Try to extract from query or context
                    weak_topics = self._extract_topics_from_query(query)
                
                # Get available hours and days until exam
                hours_available = context.get('hours_available', 6)  # Default 6 hours
                days_until_exam = context.get('days_until_exam', 60)  # Default 60 days
                
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
                        # Combine planning response with mentor's warm introduction
                        mentor_intro = "Hey! I can see you're feeling overwhelmed. No worries, yaar - let's turn this into a concrete plan! Here's your personalized study schedule:\n\n"
                        full_response = mentor_intro + plan_result.output
                        
                        return {
                            'success': True,
                            'content': full_response,
                            'agent': self.get_agent_name(),
                            'metadata': {
                                'tone': 'supportive',
                                'approach': 'planning',
                                'tool_used': 'study_planner',
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
        emotional_words = ['feeling', 'sad', 'happy', 'stressed', 'worried', 'scared', 'tired', 
                          'frustrated', 'bored', 'lonely', 'help me', 'need support']
        if any(word in query_lower for word in emotional_words):
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
            
            prompt = f"""You are Druv - a caring friend and mentor. The student shared something emotional.

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
            
            prompt = f"""You are Druv - a fun, friendly AI companion. This is casual chat.

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
                f"Hey{name_suffix}! 👋 I'm Druv, your study buddy. I can help with any subject, explain tough concepts, or just chat. What's on your mind?",
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
            mentor_system = """You are "Druv Bhaiya/Didi," an expert mentor for Indian students.

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
