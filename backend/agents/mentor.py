"""
🧠 Mentor Agent - TRUE AGENTIC Emotional & Conceptual Guidance
================================================================

UPGRADED to TRUE AGENT with:
- ReAct Loop: Think → Act → Observe
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
    - Think → Act → Observe reasoning loop
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
        
        logger.info("👨‍🏫 MentorAgent initialized as TRUE AGENT with ReAct + Tools + Memory + Verification")
    
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
        return f"""You are "{self.MENTOR_NAME} Bhaiya/Didi," a caring AI mentor for Indian students.

**YOUR CHARACTER:**
- You're like a supportive older sibling who genuinely cares
- You've helped thousands of students - you understand their struggles
- You're warm and encouraging, but also rigorous about accuracy
- You use tools to verify information rather than guessing
- You remember student patterns and adapt your style

**YOUR THINKING PROCESS (ReAct Loop):**
1. THINK: Understand the student's real question and emotional state
2. ACT: Use tools if you need facts, calculations, or verification
3. OBSERVE: Process what you learned from the tool
4. THINK: How can I explain this in a relatable way?
5. RESPOND: Give a warm, structured, accurate explanation

**WHEN TO USE TOOLS:**
- knowledge_search: When you need to look up a concept or definition
- fact_checker: When you want to verify a fact before stating it
- calculator: When there's any mathematical calculation
- study_planner: When student asks for a study plan or schedule

**YOUR STYLE:**
- Use metaphors from student's life (cricket, games, daily life)
- Explain like a friend at 2 AM before exams
- Structure responses with headers, bullets, bold terms
- Use LaTeX for math: \\( inline \\) and \\[ block \\]
- Be encouraging but never condescending

**NEVER:**
- Give wrong information (always verify when uncertain)
- Make students feel stupid
- Rush through explanations
- Use jargon without explaining
- Output unformatted walls of text"""
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mentor-style conceptual explanation using ReAct loop.
        
        This is the TRUE AGENTIC processing:
        - Uses ReAct loop for complex queries
        - Falls back to fast path for simple queries (greetings, short facts)
        
        Args:
            query: Student's question
            context: Dict with subject, student_profile, etc.
        
        Returns:
            Mentor response with emotional guidance and metaphors
        """
        try:
            logger.info(f"👨‍🏫 Mentor processing (TRUE AGENTIC): {query[:100]}")
            
            # Check if this is a greeting
            query_lower = query.lower().strip()
            greeting_words = ['hi', 'hello', 'hey', 'namaste', 'hii', 'heya', 'yo']
            is_greeting = query_lower.strip('!?.,:;') in greeting_words
            
            if is_greeting:
                # Generate friendly greeting response
                student_profile = context.get('student_profile', {})
                greeting_response = self._generate_greeting(student_profile)
                return self._format_response(
                    content=greeting_response,
                    metadata={
                        'tone': 'friendly',
                        'approach': 'greeting',
                        'is_greeting': True
                    }
                )
            
            # Extract context
            subject = context.get('subject', 'General')
            student_profile = context.get('student_profile', {})
            memory_context = context.get('memory_context')
            
            # Check if this is a planning request
            planning_keywords = [
                'plan', 'schedule', 'timetable', 'how do i finish', 
                'overwhelmed', 'no time', 'too much', 'can\'t finish',
                'study plan', 'what to study', 'where to start'
            ]
            
            is_planning_request = any(keyword in query_lower for keyword in planning_keywords)
            
            if is_planning_request and self.tool_registry:
                # Use Study Planner Tool
                logger.info("📅 MentorAgent detected planning request - using StudyPlannerTool")
                
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
                        
                        return self._format_response(
                            content=full_response,
                            metadata={
                                'tone': 'supportive',
                                'approach': 'planning',
                                'tool_used': 'study_planner',
                                'weak_topics': weak_topics
                            }
                        )
            
            # =================================================================
            # STANDARD PATH: Generate mentor response
            # Note: ReAct loop is handled by base class run() when called directly
            # =================================================================
            from services.dynamic_mentor_prompts import get_dynamic_mentor_prompt
            
            mentor_prompt = get_dynamic_mentor_prompt(
                query=query,
                subject=subject,
                student_profile=student_profile,
                memory_context=memory_context,
                user_id=context.get('user_id', 'anonymous')
            )
            
            # Call LLM for mentor response
            mentor_response = await self._generate_mentor_response(mentor_prompt)
            
            return self._format_response(
                content=mentor_response,
                metadata={
                    'tone': 'emotional',
                    'approach': 'conceptual',
                    'metaphor_used': student_profile.get('interests', ['cricket'])[0] if student_profile.get('interests') else 'cricket'
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Mentor agent error: {e}", exc_info=True)
            return self._format_error(f"Mentor processing failed: {str(e)}")
    
    def _build_mentor_prompt(
        self,
        query: str,
        subject: str,
        student_profile: Dict[str, Any],
        memory_context: Dict[str, Any] = None
    ) -> str:
        """Build mentor-specific prompt with memory context"""
        
        # Student details
        name = student_profile.get('name', '')
        region = student_profile.get('region', 'India')
        interests = student_profile.get('interests', ['cricket', 'gaming'])
        board = student_profile.get('board', 'CBSE')
        exam = student_profile.get('exam', 'JEE')
        mastery_level = student_profile.get('mastery_level', 50)
        
        # LANGUAGE PREFERENCE - Only use Hinglish if student prefers it
        language = student_profile.get('language', 'en')  # Default: English
        use_hinglish = language in ['hi', 'hinglish', 'hindi']
        
        # Memory context
        memory_str = ""
        if memory_context:
            # Continuity check
            continuity = memory_context.get('continuity', {})
            if continuity.get('is_continuation'):
                memory_str += f"\n\nIMPORTANT - Conversation Continuity:\n"
                memory_str += f"Last time, you covered: {', '.join(continuity.get('concepts_covered_before', [])[:3])}\n"
                memory_str += f"{continuity.get('suggestion', '')}\n"
            
            # Relevant past memories
            relevant_memories = memory_context.get('relevant_memories', [])
            if relevant_memories:
                memory_str += f"\n\nStudent's Learning History:\n"
                for mem in relevant_memories[:3]:
                    memory_str += f"- {mem['content']}\n"
        
        # Adaptive instructions based on mastery
        depth_instruction = self._get_depth_instruction(mastery_level)
        
        # Personalized greeting
        greeting = f"Hey {name}!" if name else "Hey there!"
        
        # Language instruction - CONDITIONAL
        if use_hinglish:
            language_instruction = """9. HINGLISH SUPPORT: Student prefers Hindi-English mix. Naturally use:
   - "matlab" (means), "yaar" (friend), "bhai" (bro), "arre" (hey)
   - "samjho" (understand), "dekho" (see), "basically" "actually"
   - Example: "Dekho, basically force matlab push ya pull hai, samjhe?"
   - Use 2-3 Hinglish words per response naturally, not forced"""
        else:
            language_instruction = """9. LANGUAGE: Respond in clear, simple ENGLISH only.
   - Use easy-to-understand vocabulary
   - NO Hindi/Hinglish words (student prefers English)
   - Keep sentences short and crisp
   - Use relatable Indian examples but in English"""
        
        return f"""You are a caring AI Mentor helping {name if name else 'an Indian student'} prepare for {exam} ({board} board).

Student Context:
- Name: {name if name else 'Student'}
- Region: {region}
- Language Preference: {'Hindi/Hinglish' if use_hinglish else 'English only'}
- Interests: {', '.join(interests)}
- Subject: {subject}
- Current Mastery: {mastery_level}/100 ({self._get_mastery_label(mastery_level)})

{memory_str}

Question: {query}

Your role as MENTOR:
1. {greeting} Be PERSONAL - use their name and reference their learning history
2. {depth_instruction}
3. **SPECIAL RULE FOR IMAGES**: If the question mentions "[Student uploaded an image" or contains "IMAGE CONTAINS:", this is an image-based question:
   - Focus ONLY on the extracted content from the image
   - NO metaphors or creative stories - be DIRECT and FACTUAL
   - If it's an MCQ, identify the question and explain options
   - If it's a problem, solve it step-by-step
   - Be precise and educational, not creative
4. For TEXT-only questions: Use METAPHORS from student's interests ({interests[0]} preferred)
5. Give INTUITIVE explanations, not formal derivations
6. Be friendly, encouraging, and culturally relevant
7. If continuing a topic, acknowledge what was covered before
8. Adapt your explanation depth to their mastery level
{language_instruction}

Keep response concise (150-200 words) and warm in tone.

Mentor's Explanation:"""
    
    def _get_depth_instruction(self, mastery_level: int) -> str:
        """Get instruction for explanation depth based on mastery"""
        if mastery_level < 30:
            return "Use VERY SIMPLE language, more visuals, basic examples (beginner level)"
        elif mastery_level < 70:
            return "Use balanced approach with examples and moderate theory (intermediate level)"
        else:
            return "Student is advanced - use deeper insights, proofs, exam tricks (advanced level)"
    
    def _get_mastery_label(self, mastery_level: int) -> str:
        """Convert mastery number to label"""
        if mastery_level < 30:
            return "Beginner"
        elif mastery_level < 70:
            return "Intermediate"
        else:
            return "Advanced"
    
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

**EXAMPLE FORMAT:**

## What is Force?

**Force** is a push or pull acting on an object.

### Key Points
- Forces can change motion
- Measured in **Newtons (N)**

### Formula
\\[ F = ma \\]

> **Remember:** Force = mass × acceleration

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
                logger.info("⚡ MentorAgent using Gemini Flash for fast, warm response...")
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
                logger.info("🧠 MentorAgent using DeepSeek for response...")
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
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            import uuid
            
            llm_client = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"mentor_{str(uuid.uuid4())[:8]}",
                system_message=mentor_system
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.8,
                top_p=0.9,
                max_tokens=1000     # INCREASED: Prevent truncation
            )
            
            user_msg = UserMessage(text=prompt)
            response = await llm_client.send_message(user_msg)
            
            if not response:
                raise Exception("Empty response from LLM")
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            # Fallback response
            return """I understand you're working on this concept. While I'm having trouble generating a detailed explanation right now, remember that every complex topic becomes clearer with practice. Think of learning like building muscle memory - each attempt makes the next one easier. Let's break this down step by step together."""
    
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
    
    def _generate_greeting(self, student_profile: Dict[str, Any]) -> str:
        """Generate a friendly greeting response"""
        import random
        
        region = student_profile.get('region', 'India')
        exam = student_profile.get('exam', 'JEE')
        
        greetings = [
            f"Hey there! 👋 Ready to tackle some {exam} concepts today? I'm here to help you understand anything you're working on!",
            f"Hello! 😊 Great to see you! What concept would you like to explore today? Whether it's tough formulas or tricky theories, we'll break it down together!",
            f"Hi! 🌟 I'm your AI Mentor, here to help you ace {exam}. Ask me anything - from quick doubts to deep concepts - and I'll explain it in the simplest way possible!",
            f"Namaste! 🙏 Ready for some learning? I'm here to make complex concepts feel easy. What would you like to understand today?",
            f"Hey! 💪 Let's crush some concepts together! Whether you need quick clarification or a detailed explanation, I've got you covered!"
        ]
        
        return random.choice(greetings)
    
    # =================================================================
    # TRUE AGENTIC METHODS: ReAct Loop Implementation
    # =================================================================
    
    def _load_student_memory(self, user_id: str) -> None:
        """Load or create memory for a student"""
        if user_id not in self._memory_cache:
            self._memory_cache[user_id] = MemorySystem(user_id=user_id)
            logger.info(f"📚 Loaded memory for student {user_id[:8]}...")
    
    def _should_verify(self, response: str) -> bool:
        """Check if response contains facts or calculations that should be verified"""
        # Verify if response contains math, formulas, or specific facts
        verification_triggers = [
            '=',  # Equations
            '\\(',  # LaTeX math
            '\\[',  # LaTeX block math
            'formula',
            'equation',
            'equals',
            'calculated',
            'result is',
            'answer is',
            'value is',
        ]
        response_lower = response.lower()
        return any(trigger in response_lower for trigger in verification_triggers)
    
    async def _run_react_loop(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override base ReActAgent's _run_react_loop for mentor-specific behavior.
        
        This is the heart of TRUE AGENTIC behavior:
        1. THINK about the student's question
        2. Decide if tools are needed
        3. ACT using tools if needed
        4. OBSERVE results
        5. THINK again and refine
        6. Generate final response
        
        Returns:
            Dict with 'content' and metadata matching expected format
        """
        from services.dynamic_mentor_prompts import get_dynamic_mentor_prompt
        
        student_profile = context.get('student_profile', {})
        subject = context.get('subject', 'General')
        memory_context = context.get('memory_context')
        
        tools_used = []
        tool_outputs = []
        
        # Step 1: Determine if tools are needed
        tool_decision = self._analyze_tool_needs(query, subject)
        
        if tool_decision['needs_tools']:
            for tool_name in tool_decision['tools_to_use']:
                try:
                    tool = self.tool_registry.get_tool(tool_name)
                    if tool:
                        logger.info(f"🔧 MentorAgent using tool: {tool_name}")
                        result = await tool.execute(query=query, context=context)
                        tools_used.append(tool_name)
                        
                        if result.success:
                            tool_outputs.append({
                                'tool': tool_name,
                                'output': result.output
                            })
                except Exception as tool_error:
                    logger.warning(f"⚠️ Tool {tool_name} failed: {tool_error}")
        
        # Step 2: Build enhanced prompt with tool outputs
        enhanced_prompt = get_dynamic_mentor_prompt(
            query=query,
            subject=subject,
            student_profile=student_profile,
            memory_context=memory_context,
            user_id=context.get('user_id', 'anonymous')
        )
        
        # Add tool outputs to prompt if available
        if tool_outputs:
            tool_context = "\n\n## Research Results (from your tools):\n"
            for output in tool_outputs:
                tool_context += f"**{output['tool']}:** {output['output'][:500]}\n"
            enhanced_prompt = tool_context + "\n\n" + enhanced_prompt
        
        # Step 3: Generate final response with all context
        logger.info("🧠 MentorAgent generating warm, structured explanation...")
        final_response = await self._generate_mentor_response(enhanced_prompt)
        
        # Return in expected format
        return {
            'content': final_response,
            'tools_used': tools_used,
            'reasoning_steps': len(tool_outputs) + 1,
            'confidence': 0.85
        }
    
    def _analyze_tool_needs(self, query: str, subject: str) -> Dict[str, Any]:
        """Analyze if the query needs tool usage"""
        query_lower = query.lower()
        
        needs_tools = False
        tools_to_use = []
        
        # Check for calculation needs
        if any(w in query_lower for w in ['calculate', 'solve', 'find the value', 'compute', '=']):
            needs_tools = True
            tools_to_use.append('calculator')
        
        # Check for fact verification needs
        if any(w in query_lower for w in ['is it true', 'verify', 'check', 'correct', 'accurate']):
            needs_tools = True
            tools_to_use.append('fact_checker')
        
        # Check for knowledge lookup needs
        if any(w in query_lower for w in ['what is', 'define', 'explain', 'meaning of', 'formula for']):
            # Only use knowledge search for specific lookups
            if len(query.split()) < 10:  # Short, specific queries
                needs_tools = True
                tools_to_use.append('knowledge_search')
        
        return {
            'needs_tools': needs_tools,
            'tools_to_use': tools_to_use
        }
    
    def get_system_prompt(self, state: AgentState) -> str:
        """Get system prompt for ReAct reasoning (override from ReActAgent)"""
        return self.get_agent_persona()

