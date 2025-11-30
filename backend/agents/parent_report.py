"""
👨‍👩‍👧 PARENT REPORT AGENT - Guardian Communication System

Philosophy: "Informed parents = supported students."

PURPOSE:
- Keep parents/guardians informed about student progress
- Generate meaningful, actionable reports
- Celebrate achievements (not just problems)
- Alert only when necessary (not spam)
- Build trust between student-AI-parent triangle

REPORT TYPES:
1. Weekly Summary - Regular progress update
2. Achievement Alert - Instant celebration of wins
3. Concern Alert - Only for genuine issues
4. Exam Preparation Status - Pre-exam updates
5. Monthly Deep Dive - Comprehensive analysis

TONE:
- Always positive-first (celebrate before concerns)
- Actionable suggestions (what parents can do)
- Student-friendly (not surveillance)
- Encouraging (never punitive)

INTEGRATION:
- Scheduled reports (weekly/monthly)
- Event-triggered alerts (achievements, concerns)
- On-demand generation
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ParentReportAgent(BaseAgent):
    """
    Parent Report Agent - Keeps guardians informed
    
    Generates reports that:
    - Celebrate wins first
    - Provide actionable insights
    - Respect student privacy
    - Build supportive environment
    """
    
    # Report configurations
    REPORT_TYPES = {
        'weekly': {
            'sections': ['greeting', 'achievements', 'progress', 'areas_to_watch', 'suggestions', 'encouragement'],
            'frequency': 'sunday_evening',
            'tone': 'positive_first',
            'length': 'medium'
        },
        'achievement': {
            'sections': ['celebration', 'achievement_details', 'impact', 'suggestion'],
            'trigger': ['streak_milestone', 'concept_mastered', 'level_up', 'test_improvement'],
            'tone': 'celebratory',
            'length': 'short'
        },
        'concern': {
            'sections': ['greeting', 'observation', 'context', 'suggestion', 'reassurance'],
            'trigger': ['no_activity_7_days', 'significant_performance_drop', 'repeated_struggles'],
            'tone': 'supportive_not_alarming',
            'length': 'short'
        },
        'exam_prep': {
            'sections': ['greeting', 'readiness_score', 'strengths', 'focus_areas', 'study_plan', 'parent_tips'],
            'trigger': ['exam_in_30_days', 'exam_in_7_days'],
            'tone': 'informative',
            'length': 'long'
        },
        'monthly': {
            'sections': ['greeting', 'monthly_summary', 'achievements', 'progress_graph', 'comparisons', 
                        'detailed_analysis', 'recommendations', 'next_month_goals'],
            'frequency': 'last_sunday_of_month',
            'tone': 'comprehensive',
            'length': 'long'
        }
    }
    
    # Achievement messages for parents
    ACHIEVEMENT_MESSAGES = {
        'streak_3': {
            'title': '🔥 3-Day Learning Streak!',
            'message': '{student_name} has studied consistently for 3 days straight. This habit-building is excellent!',
            'parent_tip': 'A simple "I noticed you\'ve been consistent, proud of you!" goes a long way.'
        },
        'streak_7': {
            'title': '🌟 Week-Long Streak Achievement!',
            'message': '{student_name} maintained a full week of daily learning. This shows great commitment!',
            'parent_tip': 'Consider a small reward - maybe their favorite snack or extra screen time.'
        },
        'streak_30': {
            'title': '🏆 INCREDIBLE! 30-Day Streak!',
            'message': '{student_name} has achieved a remarkable 30-day learning streak. This level of discipline is rare!',
            'parent_tip': 'This calls for a proper celebration! Your child has shown exceptional dedication.'
        },
        'concept_mastered': {
            'title': '✅ Concept Mastered!',
            'message': '{student_name} has fully mastered {concept_name}. Their understanding is now exam-ready.',
            'parent_tip': 'Ask them to explain the concept to you - teaching reinforces learning!'
        },
        'level_up': {
            'title': '⬆️ Level Up!',
            'message': '{student_name} has leveled up to {new_level}! Their consistent effort is paying off.',
            'parent_tip': 'Acknowledge their progress verbally - recognition motivates more than rewards.'
        },
        'test_improvement': {
            'title': '📈 Score Improvement!',
            'message': '{student_name} improved their test score from {old_score}% to {new_score}%!',
            'parent_tip': 'Praise the effort, not just the result. "I can see how hard you\'ve been working!"'
        }
    }
    
    # Concern templates (careful, supportive tone)
    CONCERN_TEMPLATES = {
        'no_activity': {
            'title': 'Checking In',
            'message': 'We noticed {student_name} hasn\'t logged in for {days} days. Everything okay?',
            'context': 'Sometimes students take breaks, which is healthy. But if they\'re feeling stuck or unmotivated, early support helps.',
            'suggestion': 'A casual conversation about their studies (not interrogation) might help: "How\'s studying going? Need any help?"',
            'reassurance': 'This is just a heads-up, not an alarm. Many top students have taken breaks too.'
        },
        'performance_drop': {
            'title': 'Progress Update',
            'message': '{student_name}\'s recent test scores show a dip in {subject}.',
            'context': 'Temporary dips are normal and can happen due to many reasons - difficult topic, tiredness, or just a bad day.',
            'suggestion': 'Avoid pressure. Instead, ask: "Is there something specific that\'s challenging? Want to talk about it?"',
            'reassurance': 'With the right support, students typically bounce back quickly. Our AI tutor is working on targeted practice.'
        },
        'repeated_struggles': {
            'title': 'Learning Update',
            'message': '{student_name} seems to be finding {topic} challenging.',
            'context': 'Some topics are genuinely harder and need more time. This is where patience and support matter most.',
            'suggestion': 'Encourage them: "Take your time with this. Shall we find a tutor for extra help?"',
            'reassurance': 'Our system has identified this and is providing extra practice and alternative explanations.'
        }
    }
    
    # Parent tips by situation
    PARENT_TIPS = {
        'general': [
            'Create a dedicated study space free from distractions',
            'Ensure 7-8 hours of sleep - tired brains don\'t learn well',
            'Ask open-ended questions: "What did you learn today?" not "Did you study?"',
            'Celebrate effort, not just results',
            'Avoid comparing with siblings or other students'
        ],
        'exam_time': [
            'Ensure good sleep - no all-nighters',
            'Light, nutritious meals before exams',
            'Create calm environment - avoid last-minute pressure',
            'Your confidence in them matters more than you think',
            'Post-exam, avoid "How did it go?" immediately - give them space'
        ],
        'struggling': [
            'Show empathy: "I can see this is tough"',
            'Focus on progress, not perfection',
            'Reduce other pressures if possible',
            'Consider if extra help (tutor) is needed',
            'Remind them of past successes: "Remember when you mastered X?"'
        ],
        'doing_well': [
            'Don\'t increase pressure because they\'re doing well',
            'Let them maintain their own rhythm',
            'Praise specific efforts, not just intelligence',
            'Encourage helping classmates - teaching strengthens learning',
            'Balance studies with breaks and hobbies'
        ]
    }
    
    def get_agent_type(self) -> str:
        return "ParentReport"
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate parent report based on query/context
        """
        try:
            logger.info(f"👨‍👩‍👧 ParentReport generating report...")
            
            # Determine report type
            report_type = self._determine_report_type(query, context)
            logger.info(f"   Report type: {report_type}")
            
            # Get student data
            student_data = await self._get_student_data(context)
            
            # Generate report
            report = await self._generate_report(
                report_type=report_type,
                student_data=student_data,
                context=context
            )
            
            return self._format_response(
                content=report['content'],
                metadata={
                    'report_type': report_type,
                    'student_name': student_data.get('name'),
                    'generated_at': datetime.now().isoformat(),
                    'sections_included': report.get('sections', [])
                }
            )
            
        except Exception as e:
            logger.error(f"❌ ParentReport error: {e}", exc_info=True)
            return self._format_error(f"Report generation failed: {str(e)}")
    
    def _determine_report_type(self, query: str, context: Dict[str, Any]) -> str:
        """Determine which type of report to generate"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['weekly', 'week', 'this week']):
            return 'weekly'
        
        if any(word in query_lower for word in ['monthly', 'month', 'this month']):
            return 'monthly'
        
        if any(word in query_lower for word in ['exam', 'test coming', 'preparation']):
            return 'exam_prep'
        
        # Check triggers in context
        session_data = context.get('session_data', {})
        
        if session_data.get('just_achieved_milestone'):
            return 'achievement'
        
        if session_data.get('days_inactive', 0) > 7:
            return 'concern'
        
        return 'weekly'  # Default
    
    async def _get_student_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get student's data for report"""
        student_profile = context.get('student_profile', {})
        session_data = context.get('session_data', {})
        
        return {
            'name': student_profile.get('user_name', student_profile.get('name', 'Your child')),
            'grade': student_profile.get('grade', 'Class 12'),
            'exam': student_profile.get('exam', 'JEE'),
            'current_streak': session_data.get('current_streak', 0),
            'weekly_study_hours': session_data.get('weekly_hours', 0),
            'topics_covered': session_data.get('topics_this_week', []),
            'achievements': session_data.get('recent_achievements', []),
            'weak_areas': session_data.get('weak_areas', []),
            'strong_areas': session_data.get('strong_areas', []),
            'test_scores': session_data.get('recent_scores', []),
            'questions_asked': session_data.get('questions_count', 0),
            'days_active': session_data.get('days_active_this_week', 0),
            'mastery_progress': session_data.get('mastery_progress', {})
        }
    
    async def _generate_report(
        self,
        report_type: str,
        student_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate the actual report content"""
        
        config = self.REPORT_TYPES.get(report_type, self.REPORT_TYPES['weekly'])
        student_name = student_data.get('name', 'Your child')
        
        if report_type == 'weekly':
            content = self._generate_weekly_report(student_data, config)
        elif report_type == 'achievement':
            content = self._generate_achievement_report(student_data, context)
        elif report_type == 'concern':
            content = self._generate_concern_report(student_data, context)
        elif report_type == 'exam_prep':
            content = self._generate_exam_prep_report(student_data, context)
        elif report_type == 'monthly':
            content = self._generate_monthly_report(student_data, config)
        else:
            content = self._generate_weekly_report(student_data, config)
        
        return {
            'content': content,
            'sections': config.get('sections', [])
        }
    
    def _generate_weekly_report(self, student_data: Dict, config: Dict) -> str:
        """Generate weekly progress report"""
        name = student_data['name']
        streak = student_data.get('current_streak', 0)
        hours = student_data.get('weekly_study_hours', 0)
        topics = student_data.get('topics_covered', [])
        achievements = student_data.get('achievements', [])
        weak_areas = student_data.get('weak_areas', [])
        days_active = student_data.get('days_active', 0)
        
        report = f"""# 📊 Weekly Progress Report for {name}

## 👋 Hello, Parents!

Here's how {name} did this week on Druv AI.

---

## 🎉 This Week's Achievements

"""
        # Achievements section (always positive first!)
        if achievements:
            for achievement in achievements[:3]:
                report += f"- ✅ {achievement}\n"
        elif streak > 0:
            report += f"- 🔥 Maintained a {streak}-day learning streak!\n"
        elif days_active > 0:
            report += f"- ✅ Stayed active for {days_active} days this week\n"
        else:
            report += "- 📚 Exploring learning at their own pace\n"
        
        report += f"""
---

## 📈 Progress Overview

| Metric | This Week |
|--------|-----------|
| Study Time | {hours} hours |
| Days Active | {days_active}/7 |
| Current Streak | {streak} days |
| Topics Covered | {len(topics)} |

"""
        
        # Topics covered
        if topics:
            report += "### Topics Studied\n"
            for topic in topics[:5]:
                report += f"- {topic}\n"
            report += "\n"
        
        # Areas to focus (reframed positively)
        if weak_areas:
            report += """## 🎯 Areas to Focus

These topics need a bit more practice:
"""
            for area in weak_areas[:3]:
                report += f"- {area}\n"
            report += "\n*Our AI tutor is providing extra practice in these areas.*\n\n"
        
        # Parent tips
        if hours > 10:
            tip_category = 'doing_well'
        elif weak_areas:
            tip_category = 'struggling'
        else:
            tip_category = 'general'
        
        tips = self.PARENT_TIPS[tip_category][:2]
        
        report += """## 💡 Tips for Parents

"""
        for tip in tips:
            report += f"- {tip}\n"
        
        report += f"""
---

## 💬 A Note from Druv AI

{name} is on a learning journey, and every step counts! Remember, consistency matters more than perfection. Keep encouraging them!

*This report was auto-generated by Druv AI. For questions, reach out to support.*

---
*Report generated: {datetime.now().strftime('%B %d, %Y')}*
"""
        
        return report
    
    def _generate_achievement_report(self, student_data: Dict, context: Dict) -> str:
        """Generate achievement celebration report"""
        name = student_data['name']
        session_data = context.get('session_data', {})
        
        # Get achievement details
        achievement_type = session_data.get('achievement_type', 'level_up')
        achievement_info = self.ACHIEVEMENT_MESSAGES.get(
            achievement_type, 
            self.ACHIEVEMENT_MESSAGES['level_up']
        )
        
        title = achievement_info['title']
        message = achievement_info['message'].format(
            student_name=name,
            concept_name=session_data.get('concept_name', 'a key concept'),
            new_level=session_data.get('new_level', 'a higher level'),
            old_score=session_data.get('old_score', 60),
            new_score=session_data.get('new_score', 75)
        )
        parent_tip = achievement_info['parent_tip']
        
        report = f"""# {title}

## Great News! 🎊

{message}

---

## 💡 How You Can Help

{parent_tip}

---

*Shared with love from Druv AI 💙*
*{datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
"""
        
        return report
    
    def _generate_concern_report(self, student_data: Dict, context: Dict) -> str:
        """Generate concern/check-in report (careful tone)"""
        name = student_data['name']
        session_data = context.get('session_data', {})
        
        # Determine concern type
        days_inactive = session_data.get('days_inactive', 0)
        
        if days_inactive > 0:
            concern_type = 'no_activity'
            concern_info = self.CONCERN_TEMPLATES['no_activity']
        elif session_data.get('performance_drop'):
            concern_type = 'performance_drop'
            concern_info = self.CONCERN_TEMPLATES['performance_drop']
        else:
            concern_type = 'repeated_struggles'
            concern_info = self.CONCERN_TEMPLATES['repeated_struggles']
        
        report = f"""# 💬 {concern_info['title']}

## Hi, Parents 👋

{concern_info['message'].format(
    student_name=name,
    days=days_inactive,
    subject=session_data.get('struggling_subject', 'a subject'),
    topic=session_data.get('struggling_topic', 'a topic')
)}

### Some Context

{concern_info['context']}

### What You Could Do

{concern_info['suggestion']}

### Important Note

{concern_info['reassurance']}

---

*We're here to support {name}'s learning journey. This is a gentle heads-up, not an alarm.*

*Druv AI Care Team*
*{datetime.now().strftime('%B %d, %Y')}*
"""
        
        return report
    
    def _generate_exam_prep_report(self, student_data: Dict, context: Dict) -> str:
        """Generate exam preparation status report"""
        name = student_data['name']
        exam = student_data.get('exam', 'the upcoming exam')
        strong_areas = student_data.get('strong_areas', [])
        weak_areas = student_data.get('weak_areas', [])
        
        session_data = context.get('session_data', {})
        days_to_exam = session_data.get('days_to_exam', 30)
        readiness_score = session_data.get('readiness_score', 65)
        
        report = f"""# 📝 Exam Preparation Report for {name}

## Exam: {exam} (in {days_to_exam} days)

---

## 📊 Readiness Score: {readiness_score}%

{"🟢 On Track!" if readiness_score >= 70 else "🟡 Needs Focus" if readiness_score >= 50 else "🔴 Needs Attention"}

---

## 💪 Strong Areas

"""
        if strong_areas:
            for area in strong_areas[:4]:
                report += f"- ✅ {area}\n"
        else:
            report += "- Building foundation across topics\n"
        
        report += """
## 🎯 Focus Areas

"""
        if weak_areas:
            for area in weak_areas[:4]:
                report += f"- ⚠️ {area}\n"
        else:
            report += "- Continue current preparation\n"
        
        report += f"""
---

## 💡 Tips for Parents During Exam Time

"""
        for tip in self.PARENT_TIPS['exam_time'][:4]:
            report += f"- {tip}\n"
        
        report += f"""
---

## 📅 What's Happening

Our AI tutor is:
- Providing targeted practice for weak areas
- Revising strong topics to maintain confidence  
- Generating mock tests similar to {exam} pattern

---

*Wishing {name} all the best! 🍀*

*Druv AI*
*{datetime.now().strftime('%B %d, %Y')}*
"""
        
        return report
    
    def _generate_monthly_report(self, student_data: Dict, config: Dict) -> str:
        """Generate comprehensive monthly report"""
        name = student_data['name']
        
        report = f"""# 📊 Monthly Progress Report for {name}

## {datetime.now().strftime('%B %Y')}

---

## 📈 Month at a Glance

[Detailed monthly statistics would go here]

---

## 🏆 Key Achievements This Month

[List of achievements]

---

## 📚 Topics Mastered

[List of mastered topics]

---

## 🎯 Recommended Focus for Next Month

[Recommendations based on analysis]

---

## 💡 Parent Insights

[Personalized tips for parents]

---

*Thank you for trusting Druv AI with {name}'s learning journey!*

*{datetime.now().strftime('%B %d, %Y')}*
"""
        
        return report
    
    @staticmethod
    def is_parent_report_query(query: str) -> bool:
        """
        Static method to detect if query is for parent report
        Used by Supervisor to route to this agent
        """
        query_lower = query.lower()
        
        parent_signals = [
            'parent report', 'progress report', 'weekly report',
            'send to parent', 'guardian', 'parent update',
            'how is my child', 'my kid', 'my son', 'my daughter'
        ]
        
        for signal in parent_signals:
            if signal in query_lower:
                return True
        
        return False

