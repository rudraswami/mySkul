"""
📅 Study Planner Tool - In-Chat Quick Planning
===============================================

Generates personalized study schedules based on weak topics, available time, and exam countdown.
Used by MentorAgent when students feel overwhelmed or ask for planning help.

ARCHITECTURE NOTE:
- This TOOL is for quick, in-chat planning (when student says "I'm overwhelmed")
- StudyPlannerAgent (agents/study_planner_agent.py) is for the full dashboard feature
- They are NOT duplicates - they serve different purposes:
  - Tool: Quick response during conversation
  - Agent: Full feature with XP tracking, completion, persistence
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class StudyPlannerTool(BaseTool):
    """
    Study Planner Tool - Generates personalized study schedules.
    
    Replaces the Study Planner Agent functionality.
    Used by MentorAgent when students need help with planning or feel overwhelmed.
    """
    
    @property
    def name(self) -> str:
        return "study_planner"
    
    @property
    def description(self) -> str:
        return (
            "Generates a personalized study timetable based on weak topics, available hours, "
            "and days until exam. Use this tool when students feel overwhelmed, ask 'How do I finish this?', "
            "or need help planning their study schedule. The output is a strict but achievable markdown timetable."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "weak_topics": "List of topics the student struggles with (e.g., ['Rotational Motion', 'Organic Chemistry'])",
            "hours_available": "Daily study hours available (integer, e.g., 6)",
            "days_until_exam": "Days remaining until exam (integer, e.g., 60)"
        }
    
    async def execute(
        self,
        weak_topics: List[str] = None,
        hours_available: int = 6,
        days_until_exam: int = 60,
        context: Dict = None,
        **kwargs
    ) -> ToolResult:
        """
        Generate personalized study timetable.
        
        Args:
            weak_topics: List of topics student struggles with
            hours_available: Daily study hours
            days_until_exam: Days until exam
        
        Returns:
            ToolResult with markdown-formatted timetable
        """
        try:
            # Validate inputs
            if weak_topics is None:
                weak_topics = []
            
            if not isinstance(weak_topics, list):
                weak_topics = [str(weak_topics)]
            
            hours_available = int(hours_available) if hours_available else 6
            days_until_exam = int(days_until_exam) if days_until_exam else 60
            
            # Ensure reasonable bounds
            hours_available = max(2, min(12, hours_available))  # 2-12 hours
            days_until_exam = max(7, min(365, days_until_exam))  # 7-365 days
            
            # Generate timetable
            timetable = self._generate_timetable(
                weak_topics=weak_topics,
                hours_per_day=hours_available,
                days_remaining=days_until_exam
            )
            
            logger.info(f"📅 Study plan generated: {len(weak_topics)} weak topics, {hours_available}h/day, {days_until_exam} days")
            
            return ToolResult.success_result(
                timetable,
                metadata={
                    "weak_topics_count": len(weak_topics),
                    "hours_per_day": hours_available,
                    "days_remaining": days_until_exam
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Study planner error: {e}", exc_info=True)
            return ToolResult.error_result(f"Failed to generate study plan: {str(e)}")
    
    def _generate_timetable(
        self,
        weak_topics: List[str],
        hours_per_day: int,
        days_remaining: int
    ) -> str:
        """
        Generate markdown-formatted study timetable.
        
        Allocates time for:
        - Concept Revision (NCERT)
        - Practice (PYQs)
        - Buffer time
        """
        
        # Calculate time allocation
        total_hours = hours_per_day * days_remaining
        
        # Time allocation strategy
        if days_remaining >= 90:
            # Long-term plan: Balanced approach
            concept_revision_pct = 40
            practice_pct = 40
            buffer_pct = 20
        elif days_remaining >= 30:
            # Medium-term: More practice
            concept_revision_pct = 30
            practice_pct = 50
            buffer_pct = 20
        else:
            # Short-term: Focus on practice and weak areas
            concept_revision_pct = 20
            practice_pct = 60
            buffer_pct = 20
        
        concept_hours = int(total_hours * concept_revision_pct / 100)
        practice_hours = int(total_hours * practice_pct / 100)
        buffer_hours = total_hours - concept_hours - practice_hours
        
        # Build timetable
        parts = [
            "# 📅 Personalized Study Plan\n",
            f"**Generated for:** {days_remaining} days until exam",
            f"**Daily Study Time:** {hours_per_day} hours",
            f"**Total Available Time:** {total_hours} hours\n",
            "---\n",
            "## ⏰ Time Allocation\n",
            f"- **Concept Revision (NCERT)**: {concept_hours} hours ({concept_revision_pct}%)",
            f"- **Practice (PYQs & Mock Tests)**: {practice_hours} hours ({practice_pct}%)",
            f"- **Buffer & Revision**: {buffer_hours} hours ({buffer_pct}%)\n",
            "---\n",
            "## 📚 Weekly Schedule Template\n",
            "### Monday - Friday (Weekdays)\n",
            f"- **Morning ({hours_per_day // 3}h)**: Concept Revision",
            f"  - Focus on NCERT reading + note-making",
            f"  - One weak topic per day",
            f"- **Afternoon ({hours_per_day // 3}h)**: Practice",
            f"  - Solve PYQs from the topic studied",
            f"  - Time yourself (exam simulation)",
            f"- **Evening ({hours_per_day // 3}h)**: Revision",
            f"  - Quick review of what you learned",
            f"  - Solve 2-3 more problems\n",
            "### Saturday - Sunday (Weekends)\n",
            f"- **Extended Study ({hours_per_day + 2}h/day)**:",
            f"  - Mock test (3 hours)",
            f"  - Analysis & weak topic focus",
            f"  - Buffer time for catching up\n",
            "---\n"
        ]
        
        # Add weak topics focus
        if weak_topics:
            parts.extend([
                "## 🎯 Weak Topics Priority Plan\n",
                "Focus on these topics with extra time:\n"
            ])
            
            # Distribute weak topics across available days
            topics_per_week = max(1, len(weak_topics) // (days_remaining // 7))
            
            for i, topic in enumerate(weak_topics[:10], 1):  # Limit to 10 topics
                week_num = (i - 1) // topics_per_week + 1
                parts.append(f"{i}. **{topic}** - Week {week_num}")
                parts.append(f"   - Allocate 2x time compared to other topics")
                parts.append(f"   - Start with NCERT basics, then PYQs")
                parts.append("")
        else:
            parts.append("## 🎯 General Study Strategy\n")
            parts.append("Since no specific weak topics were mentioned:\n")
            parts.append("1. Follow NCERT chapter order")
            parts.append("2. Practice 10 PYQs per topic")
            parts.append("3. Take weekly mock tests")
            parts.append("4. Review mistakes immediately\n")
        
        # Add daily breakdown example
        parts.extend([
            "---\n",
            "## 📋 Sample Daily Schedule\n",
            f"**Example Day (Weekday - {hours_per_day}h available):**\n",
            f"- **6:00 AM - 8:00 AM** ({hours_per_day // 3}h): Concept Revision",
            "  - Read NCERT chapter",
            "  - Make notes",
            "  - Understand fundamentals\n",
            f"- **4:00 PM - 6:00 PM** ({hours_per_day // 3}h): Practice",
            "  - Solve 10 PYQs",
            "  - Time yourself",
            "  - Mark difficult problems\n",
            f"- **8:00 PM - 10:00 PM** ({hours_per_day // 3}h): Revision",
            "  - Review notes",
            "  - Re-attempt marked problems",
            "  - Quick formula revision\n",
            "---\n",
            "## ✅ Success Tips\n",
            "1. **Stick to the schedule** - Consistency beats intensity",
            "2. **Take breaks** - 5 min break every 45 min",
            "3. **Track progress** - Mark completed topics",
            "4. **Adjust weekly** - If falling behind, reduce scope, not quality",
            "5. **Mock tests are mandatory** - Take at least 1 per week",
            "6. **Sleep 7-8 hours** - Don't sacrifice sleep for study\n",
            "---\n",
            "**Remember:** This plan is strict but achievable. Adjust based on your pace, but maintain consistency! 💪"
        ])
        
        return "\n".join(parts)

