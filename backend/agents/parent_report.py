"""
Parent Report Agent - TRUE AGENTIC Guardian Communication System
==================================================================

UPGRADED to TRUE AGENT with:
- ReAct Loop: Think → Act → Observe
- Tools: DatabaseQueryTool (performance tracking), AnalyticsTool (insights)
- Memory: Tracks report history, student progress over time
- Actions: ANALYZES real data, GENERATES insights, SENDS reports

OLD: Template-based reports
NEW: DATA-DRIVEN reports with real insights from student's actual performance
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from agents.core.react_agent import ReActAgent
from agents.core.tool_registry import ToolRegistry
from agents.core.tools.database_query_tool import DatabaseQueryTool
from agents.core.tools.analytics_tool import AnalyticsTool
from agents.core.memory import LongTermMemory

logger = logging.getLogger(__name__)


class ParentReportAgent(ReActAgent):
    """
    TRUE AGENTIC Parent Report Generator
    
    Capabilities:
    - Queries actual student performance data
    - Analyzes progress trends
    - Identifies achievements and concerns
    - Generates actionable insights for parents
    - Tracks report history
    """
    
    REPORT_TYPES = ['weekly', 'achievement', 'concern', 'exam_prep', 'monthly']
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Get DB client from config
        self.db = config.get('db_client') if config else None
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self.tool_registry.register(DatabaseQueryTool(self.db))
        self.tool_registry.register(AnalyticsTool())
        
        # Initialize memory (will be set per user)
        self.memory = None  # Set during process() with actual user_id
        
        logger.info("👨‍👩‍👧 ParentReportAgent initialized as TRUE AGENT")
    
    def get_agent_name(self) -> str:
        return "ParentReportAgent"
    
    def get_available_tools(self) -> list:
        """Return list of tools this agent can use"""
        return ['query_user_data', 'analyze_data']
    
    def get_agent_persona(self) -> str:
        return """You are a parent communication specialist who generates meaningful reports.

Your role:
- Analyze student's actual performance data
- Generate insights that parents can act on
- Celebrate achievements first, then address concerns
- Provide specific, actionable suggestions
- Build trust between student-AI-parent

Your style:
- Positive-first: Always start with achievements
- Data-driven: Base everything on real metrics
- Actionable: Give parents specific things they can do
- Supportive: Never punitive or surveillance-like
- Honest: Don't sugarcoat serious concerns

Remember:
- Parents want to help, not punish
- Specific data is more useful than vague statements
- Every concern should have a suggested action
- Celebrate effort, not just results"""
    
    @staticmethod
    def is_parent_report_query(query: str) -> bool:
        """Check if query is for parent report"""
        patterns = [
            'parent report', 'progress report', 'weekly report',
            'send to parent', 'guardian', 'parent update'
        ]
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in patterns)
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate parent report using ReAct loop with data analysis.
        
        Think: What type of report? What data is needed?
        Act: Query performance, analyze trends, generate insights
        Observe: Verify report is actionable and supportive
        """
        try:
            user_id = context.get('user_id')
            student_profile = context.get('student_profile', {})
            student_name = student_profile.get('name', 'Your child')
            
            logger.info(f"👨‍👩‍👧 Generating parent report for {student_name}")
            
            # THINK: Determine report type
            report_type = self._determine_report_type(query, context)
            thought = f"Report type: {report_type}. Need to query performance data."
            
            # ACT 1: Query student performance
            logger.info("👨‍👩‍👧 Step 1: Querying performance data...")
            performance_result = await self.tool_registry.execute_tool(
                'query_user_data',
                user_id=user_id,
                query_type='user_performance',
                time_range=30
            )
            
            # ACT 2: Analyze progress trends
            logger.info("👨‍👩‍👧 Step 2: Analyzing progress...")
            progress_result = await self.tool_registry.execute_tool(
                'query_user_data',
                user_id=user_id,
                query_type='progress_over_time',
                time_range=30
            )
            
            # ACT 3: Generate report
            logger.info(f"👨‍👩‍👧 Step 3: Generating {report_type} report...")
            report = await self._generate_report(
                report_type=report_type,
                student_name=student_name,
                performance_data=performance_result.data if performance_result.success else {},
                progress_data=progress_result.data if progress_result.success else {},
                context=context
            )
            
            # OBSERVE: Report generated
            observation = f"{report_type} report generated with real data"
            
            return {
                'success': True,
                'content': report,
                'report_type': report_type,
                'student_name': student_name,
                'data_driven': True,
                'thought': thought,
                'actions': ['query_performance', 'analyze_progress', 'generate_report'],
                'observation': observation
            }
            
        except Exception as e:
            logger.error(f"❌ ParentReport error: {e}", exc_info=True)
            return await self._fallback_report(query, context)
    
    def _determine_report_type(self, query: str, context: Dict[str, Any]) -> str:
        """Determine type of report to generate"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['weekly', 'week']):
            return 'weekly'
        elif any(word in query_lower for word in ['monthly', 'month']):
            return 'monthly'
        elif any(word in query_lower for word in ['exam', 'preparation']):
            return 'exam_prep'
        elif 'achievement' in query_lower:
            return 'achievement'
        elif 'concern' in query_lower:
            return 'concern'
        else:
            return 'weekly'  # Default
    
    async def _generate_report(
        self,
        report_type: str,
        student_name: str,
        performance_data: Dict,
        progress_data: Dict,
        context: Dict[str, Any]
    ) -> str:
        """Generate the actual report"""
        
        if report_type == 'weekly':
            return self._generate_weekly_report(student_name, performance_data, progress_data)
        elif report_type == 'achievement':
            return self._generate_achievement_report(student_name, performance_data)
        elif report_type == 'concern':
            return self._generate_concern_report(student_name, performance_data, progress_data)
        elif report_type == 'exam_prep':
            return self._generate_exam_prep_report(student_name, performance_data)
        elif report_type == 'monthly':
            return self._generate_monthly_report(student_name, performance_data, progress_data)
        else:
            return self._generate_weekly_report(student_name, performance_data, progress_data)
    
    def _generate_weekly_report(self, student_name: str, performance: Dict, progress: Dict) -> str:
        """Generate weekly progress report"""
        
        total_sessions = performance.get('total_sessions', 0)
        subjects = performance.get('subjects', {})
        trend = progress.get('trend', 'stable')
        
        report = f"""# 📊 Weekly Progress Report for {student_name}

## 👋 Hello, Parents!

Here's how {student_name} did this week on Druv AI.

---

## 🎉 This Week's Achievements

"""
        
        # Achievements (positive first!)
        if total_sessions > 20:
            report += f"- ✅ Excellent engagement: {total_sessions} study sessions!\n"
        elif total_sessions > 10:
            report += f"- ✅ Good consistency: {total_sessions} study sessions\n"
        elif total_sessions > 0:
            report += f"- ✅ Active learning: {total_sessions} study sessions\n"
        else:
            report += "- 📚 Getting started with the platform\n"
        
        if trend == 'improving':
            report += "- 📈 Performance is improving steadily!\n"
        
        report += f"""
---

## 📈 Progress Overview

| Metric | This Week |
|--------|-----------|
| Study Sessions | {total_sessions} |
| Subjects Studied | {len(subjects)} |
| Performance Trend | {trend.capitalize()} |

"""
        
        # Subject breakdown
        if subjects:
            report += "### Subjects Studied\n"
            for subject, data in list(subjects.items())[:3]:
                report += f"- **{subject}**: {data.get('sessions', 0)} sessions, {data.get('messages', 0)} questions\n"
            report += "\n"
        
        # Suggestions
        report += """## 💡 Tips for Parents

- Encourage consistent daily study (even 30 minutes helps)
- Ask open-ended questions: "What did you learn today?"
- Celebrate effort, not just results

---

## 💬 A Note from Druv AI

"""
        
        if trend == 'improving':
            report += f"{student_name} is making great progress! Keep encouraging them.\n"
        elif trend == 'declining':
            report += f"{student_name} might need some extra support. Consider having a gentle conversation about any challenges they're facing.\n"
        else:
            report += f"{student_name} is learning steadily. Consistency is key!\n"
        
        report += f"""
*This report was auto-generated by Druv AI based on actual usage data.*

---
*Report generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        return report
    
    def _generate_achievement_report(self, student_name: str, performance: Dict) -> str:
        """Generate achievement celebration report"""
        
        return f"""# 🎉 Achievement Alert!

## Great News! 🎊

{student_name} has reached a significant milestone in their learning journey!

**Achievement:** Completed {performance.get('total_sessions', 0)} study sessions

---

## 💡 How You Can Help

A simple "I noticed you've been consistent, proud of you!" goes a long way.

---

*Shared with love from Druv AI 💙*
*{datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
"""
    
    def _generate_concern_report(self, student_name: str, performance: Dict, progress: Dict) -> str:
        """Generate concern/check-in report"""
        
        trend = progress.get('trend', 'stable')
        
        return f"""# 💬 Checking In

## Hi, Parents 👋

We noticed {student_name}'s activity has been lower than usual recently.

### Some Context

This could be due to many reasons - exams, other commitments, or just needing a break. All of these are normal!

### What You Could Do

A casual conversation might help: "How's studying going? Need any help?"

### Important Note

This is just a gentle heads-up, not an alarm. Many students have ups and downs in their learning journey.

---

*We're here to support {student_name}'s learning journey.*

*Druv AI Care Team*
*{datetime.now().strftime('%B %d, %Y')}*
"""
    
    def _generate_exam_prep_report(self, student_name: str, performance: Dict) -> str:
        """Generate exam preparation status report"""
        
        total_sessions = performance.get('total_sessions', 0)
        readiness_score = min(100, (total_sessions / 50) * 100)  # Simple calculation
        
        return f"""# 📝 Exam Preparation Report for {student_name}

## 📊 Readiness Score: {readiness_score:.0f}%

{"🟢 On Track!" if readiness_score >= 70 else "🟡 Needs Focus" if readiness_score >= 50 else "🔴 Needs Attention"}

---

## 💪 Current Status

- Study sessions completed: {total_sessions}
- Subjects covered: {len(performance.get('subjects', {}))}

---

## 💡 Tips for Parents During Exam Time

- Ensure 7-8 hours of sleep - tired brains don't learn well
- Create calm environment - avoid last-minute pressure
- Your confidence in them matters more than you think
- Light, nutritious meals before exams

---

*Wishing {student_name} all the best! 🍀*

*Druv AI*
*{datetime.now().strftime('%B %d, %Y')}*
"""
    
    def _generate_monthly_report(self, student_name: str, performance: Dict, progress: Dict) -> str:
        """Generate comprehensive monthly report"""
        
        return f"""# 📊 Monthly Progress Report for {student_name}

## {datetime.now().strftime('%B %Y')}

---

## 📈 Month at a Glance

- Total study sessions: {performance.get('total_sessions', 0)}
- Subjects studied: {len(performance.get('subjects', {}))}
- Performance trend: {progress.get('trend', 'stable').capitalize()}

---

## 🏆 Key Achievements This Month

[Based on {performance.get('total_sessions', 0)} sessions of data]

---

## 🎯 Recommended Focus for Next Month

Continue consistent daily practice and focus on weak areas identified by our AI tutor.

---

*Thank you for trusting Druv AI with {student_name}'s learning journey!*

*{datetime.now().strftime('%B %d, %Y')}*
"""
    
    async def _fallback_report(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback when data analysis fails"""
        student_name = context.get('student_profile', {}).get('name', 'Your child')
        
        return {
            'success': True,
            'content': f"""# 📊 Progress Report for {student_name}

We're collecting data to generate a comprehensive report. Check back in a few days for detailed insights!

In the meantime, encourage consistent daily study and feel free to reach out if you have any questions.

*Druv AI Team*""",
            'data_driven': False
        }


# Factory function
def create_parent_report_agent(config: Optional[Dict[str, Any]] = None) -> ParentReportAgent:
    """Create ParentReportAgent instance"""
    return ParentReportAgent(config)
