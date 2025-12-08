"""
Database Query Tool
===================

Allows agents to query MongoDB for user data, performance metrics,
and learning analytics.

This enables WeakAreaDetectiveAgent to analyze REAL data.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from agents.core.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class DatabaseQueryTool(BaseTool):
    """
    Tool for querying user data and analytics from MongoDB.
    
    Enables agents to:
    - Get user performance history
    - Analyze topic-wise accuracy
    - Track time spent per subject
    - Identify weak areas from data
    """
    
    def __init__(self, db_client=None):
        super().__init__()
        self.db = db_client
    
    def get_name(self) -> str:
        return "query_user_data"
    
    def get_description(self) -> str:
        return """Query user performance data and analytics.
        
        Queries:
        - user_performance: Get accuracy, time spent per topic
        - weak_areas: Identify topics with low accuracy
        - study_patterns: Analyze study time patterns
        - progress_over_time: Track improvement trends
        """
    
    def get_parameters(self) -> Dict[str, str]:
        return {
            "user_id": "User ID to query data for",
            "query_type": "Type of query (user_performance, weak_areas, study_patterns, progress_over_time)",
            "subject": "Subject to filter by (optional)",
            "time_range": "Time range in days (default: 30)"
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute database query"""
        try:
            if not self.db:
                return ToolResult(
                    success=False,
                    output="Database not available",
                    error="No database connection"
                )
            
            user_id = kwargs.get('user_id')
            query_type = kwargs.get('query_type', 'user_performance')
            subject = kwargs.get('subject')
            time_range = int(kwargs.get('time_range', 30))
            
            logger.info(f"📊 Querying {query_type} for user {user_id}")
            
            # Execute based on query type
            if query_type == 'user_performance':
                data = await self._get_user_performance(user_id, subject, time_range)
            elif query_type == 'weak_areas':
                data = await self._get_weak_areas(user_id, subject, time_range)
            elif query_type == 'study_patterns':
                data = await self._get_study_patterns(user_id, time_range)
            elif query_type == 'progress_over_time':
                data = await self._get_progress_over_time(user_id, subject, time_range)
            else:
                data = await self._get_user_performance(user_id, subject, time_range)
            
            return ToolResult(
                success=True,
                output=f"Retrieved {query_type} data",
                data=data
            )
            
        except Exception as e:
            logger.error(f"❌ Database query failed: {e}")
            return ToolResult(
                success=False,
                output=f"Query failed: {str(e)}",
                error=str(e)
            )
    
    async def _get_user_performance(self, user_id: str, subject: Optional[str], days: int) -> Dict[str, Any]:
        """Get user performance metrics"""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Query chat sessions
        query = {
            "user_id": user_id,
            "created_at": {"$gte": cutoff_date}
        }
        if subject:
            query["subject"] = subject
        
        sessions = await self.db.chat_sessions.find(query).to_list(length=1000)
        
        # Calculate metrics
        total_sessions = len(sessions)
        total_messages = sum(len(s.get('messages', [])) for s in sessions)
        subjects = {}
        
        for session in sessions:
            subj = session.get('subject', 'Unknown')
            if subj not in subjects:
                subjects[subj] = {'sessions': 0, 'messages': 0}
            subjects[subj]['sessions'] += 1
            subjects[subj]['messages'] += len(session.get('messages', []))
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'subjects': subjects,
            'time_range_days': days
        }
    
    async def _get_weak_areas(self, user_id: str, subject: Optional[str], days: int) -> Dict[str, Any]:
        """Identify weak areas based on session data"""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get sessions with low engagement (few messages = struggled)
        query = {
            "user_id": user_id,
            "created_at": {"$gte": cutoff_date}
        }
        if subject:
            query["subject"] = subject
        
        sessions = await self.db.chat_sessions.find(query).to_list(length=1000)
        
        # Analyze topics
        topic_analysis = {}
        for session in sessions:
            topic = session.get('topic', 'Unknown')
            msg_count = len(session.get('messages', []))
            
            if topic not in topic_analysis:
                topic_analysis[topic] = {
                    'sessions': 0,
                    'avg_messages': 0,
                    'total_messages': 0
                }
            
            topic_analysis[topic]['sessions'] += 1
            topic_analysis[topic]['total_messages'] += msg_count
        
        # Calculate averages and identify weak areas
        weak_areas = []
        for topic, data in topic_analysis.items():
            data['avg_messages'] = data['total_messages'] / data['sessions']
            
            # Low message count = struggled with topic
            if data['avg_messages'] < 3:
                weak_areas.append({
                    'topic': topic,
                    'sessions': data['sessions'],
                    'avg_engagement': data['avg_messages'],
                    'confidence': 'low'
                })
        
        return {
            'weak_areas': weak_areas,
            'total_topics_analyzed': len(topic_analysis),
            'time_range_days': days
        }
    
    async def _get_study_patterns(self, user_id: str, days: int) -> Dict[str, Any]:
        """Analyze study time patterns"""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        sessions = await self.db.chat_sessions.find({
            "user_id": user_id,
            "created_at": {"$gte": cutoff_date}
        }).to_list(length=1000)
        
        # Analyze patterns
        daily_sessions = {}
        hourly_distribution = [0] * 24
        
        for session in sessions:
            created_at = session.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_key = dt.date().isoformat()
                    hour = dt.hour
                    
                    daily_sessions[date_key] = daily_sessions.get(date_key, 0) + 1
                    hourly_distribution[hour] += 1
                except:
                    pass
        
        # Find peak study hour
        peak_hour = hourly_distribution.index(max(hourly_distribution)) if hourly_distribution else 0
        
        return {
            'daily_sessions': daily_sessions,
            'hourly_distribution': hourly_distribution,
            'peak_study_hour': peak_hour,
            'total_days_active': len(daily_sessions),
            'avg_sessions_per_day': len(sessions) / max(len(daily_sessions), 1)
        }
    
    async def _get_progress_over_time(self, user_id: str, subject: Optional[str], days: int) -> Dict[str, Any]:
        """Track progress/improvement over time"""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        query = {
            "user_id": user_id,
            "created_at": {"$gte": cutoff_date}
        }
        if subject:
            query["subject"] = subject
        
        sessions = await self.db.chat_sessions.find(query).sort("created_at", 1).to_list(length=1000)
        
        # Split into time periods
        mid_point = len(sessions) // 2
        first_half = sessions[:mid_point]
        second_half = sessions[mid_point:]
        
        # Calculate engagement metrics
        first_avg = sum(len(s.get('messages', [])) for s in first_half) / max(len(first_half), 1)
        second_avg = sum(len(s.get('messages', [])) for s in second_half) / max(len(second_half), 1)
        
        # Determine trend
        if second_avg > first_avg * 1.2:
            trend = "improving"
        elif second_avg < first_avg * 0.8:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            'trend': trend,
            'first_period_avg': first_avg,
            'second_period_avg': second_avg,
            'improvement_percentage': ((second_avg - first_avg) / max(first_avg, 1)) * 100,
            'total_sessions': len(sessions)
        }
















