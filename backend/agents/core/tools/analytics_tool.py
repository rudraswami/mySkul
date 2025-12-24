"""
Analytics Tool
==============

Performs statistical analysis and generates insights from user data.

Enables agents to:
- Calculate performance metrics
- Identify patterns and trends
- Generate recommendations
- Predict outcomes
"""

import logging
from typing import Dict, Any, List, Optional
from agents.core.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class AnalyticsTool(BaseTool):
    """
    Tool for analyzing data and generating insights.
    
    Provides:
    - Statistical analysis
    - Trend detection
    - Pattern recognition
    - Recommendation generation
    """
    
    def get_name(self) -> str:
        return "analyze_data"
    
    def get_description(self) -> str:
        return """Analyze data and generate insights.
        
        Analysis types:
        - performance_analysis: Calculate metrics and trends
        - pattern_detection: Find patterns in behavior
        - recommendation_generation: Generate actionable recommendations
        - prediction: Predict future outcomes
        """
    
    def get_parameters(self) -> Dict[str, str]:
        return {
            "analysis_type": "Type of analysis to perform",
            "data": "Data to analyze (dict or list)",
            "context": "Additional context for analysis (optional)"
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Perform analysis"""
        try:
            analysis_type = kwargs.get('analysis_type', 'performance_analysis')
            data = kwargs.get('data', {})
            context = kwargs.get('context', {})
            
            logger.info(f"📊 Performing {analysis_type}")
            
            if analysis_type == 'performance_analysis':
                result = self._analyze_performance(data, context)
            elif analysis_type == 'pattern_detection':
                result = self._detect_patterns(data, context)
            elif analysis_type == 'recommendation_generation':
                result = self._generate_recommendations(data, context)
            elif analysis_type == 'prediction':
                result = self._predict_outcomes(data, context)
            else:
                result = self._analyze_performance(data, context)
            
            return ToolResult(
                success=True,
                output=f"Analysis complete: {analysis_type}",
                data=result
            )
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return ToolResult(
                success=False,
                output=f"Analysis failed: {str(e)}",
                error=str(e)
            )
    
    def _analyze_performance(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics"""
        metrics = {}
        
        # Calculate basic metrics
        if 'total_sessions' in data:
            metrics['engagement_level'] = 'high' if data['total_sessions'] > 20 else 'medium' if data['total_sessions'] > 10 else 'low'
        
        if 'subjects' in data:
            # Find most/least studied subjects
            subjects = data['subjects']
            if subjects:
                sorted_subjects = sorted(subjects.items(), key=lambda x: x[1].get('sessions', 0), reverse=True)
                metrics['most_studied'] = sorted_subjects[0][0] if sorted_subjects else None
                metrics['least_studied'] = sorted_subjects[-1][0] if sorted_subjects else None
        
        # Analyze trends
        if 'trend' in data:
            metrics['performance_trend'] = data['trend']
            metrics['trend_confidence'] = 'high' if abs(data.get('improvement_percentage', 0)) > 20 else 'medium'
        
        return {
            'metrics': metrics,
            'summary': self._generate_summary(metrics),
            'insights': self._generate_insights(metrics)
        }
    
    def _detect_patterns(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect patterns in user behavior"""
        patterns = []
        
        # Study time patterns
        if 'peak_study_hour' in data:
            peak_hour = data['peak_study_hour']
            if 6 <= peak_hour <= 11:
                patterns.append({'type': 'morning_learner', 'confidence': 'high'})
            elif 14 <= peak_hour <= 18:
                patterns.append({'type': 'afternoon_learner', 'confidence': 'high'})
            elif 19 <= peak_hour <= 23:
                patterns.append({'type': 'night_learner', 'confidence': 'high'})
        
        # Consistency patterns
        if 'daily_sessions' in data:
            daily_sessions = data['daily_sessions']
            if len(daily_sessions) > 0:
                avg_sessions = sum(daily_sessions.values()) / len(daily_sessions)
                if avg_sessions > 3:
                    patterns.append({'type': 'highly_consistent', 'confidence': 'high'})
                elif avg_sessions > 1:
                    patterns.append({'type': 'moderately_consistent', 'confidence': 'medium'})
                else:
                    patterns.append({'type': 'inconsistent', 'confidence': 'high'})
        
        # Subject preference patterns
        if 'subjects' in data:
            subjects = data['subjects']
            if len(subjects) == 1:
                patterns.append({'type': 'focused_learner', 'confidence': 'high'})
            elif len(subjects) > 5:
                patterns.append({'type': 'diverse_learner', 'confidence': 'high'})
        
        return {
            'patterns': patterns,
            'pattern_count': len(patterns),
            'primary_pattern': patterns[0] if patterns else None
        }
    
    def _generate_recommendations(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on weak areas
        if 'weak_areas' in data:
            weak_areas = data['weak_areas']
            for area in weak_areas[:3]:  # Top 3 weak areas
                recommendations.append({
                    'type': 'focus_area',
                    'priority': 'high',
                    'action': f"Practice more on {area.get('topic', 'this topic')}",
                    'reason': f"Low engagement detected ({area.get('avg_engagement', 0):.1f} avg messages)"
                })
        
        # Based on study patterns
        if 'avg_sessions_per_day' in data:
            avg = data['avg_sessions_per_day']
            if avg < 1:
                recommendations.append({
                    'type': 'consistency',
                    'priority': 'high',
                    'action': "Study daily, even if just 15 minutes",
                    'reason': "Low study frequency detected"
                })
        
        # Based on performance trend
        if 'trend' in data:
            trend = data['trend']
            if trend == 'declining':
                recommendations.append({
                    'type': 'intervention',
                    'priority': 'critical',
                    'action': "Take a break and reassess study strategy",
                    'reason': "Performance declining - possible burnout"
                })
            elif trend == 'improving':
                recommendations.append({
                    'type': 'encouragement',
                    'priority': 'low',
                    'action': "Keep up the great work!",
                    'reason': "Performance improving steadily"
                })
        
        return {
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'priority_actions': [r for r in recommendations if r['priority'] in ['critical', 'high']]
        }
    
    def _predict_outcomes(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future outcomes based on current data"""
        predictions = {}
        
        # Predict exam readiness
        if 'total_sessions' in data and 'trend' in data:
            sessions = data['total_sessions']
            trend = data['trend']
            
            if sessions > 50 and trend == 'improving':
                predictions['exam_readiness'] = 'high'
                predictions['confidence'] = 0.8
            elif sessions > 20 and trend in ['improving', 'stable']:
                predictions['exam_readiness'] = 'medium'
                predictions['confidence'] = 0.6
            else:
                predictions['exam_readiness'] = 'low'
                predictions['confidence'] = 0.5
        
        # Predict dropout risk
        if 'avg_sessions_per_day' in data:
            avg = data['avg_sessions_per_day']
            if avg < 0.5:
                predictions['dropout_risk'] = 'high'
            elif avg < 1:
                predictions['dropout_risk'] = 'medium'
            else:
                predictions['dropout_risk'] = 'low'
        
        return {
            'predictions': predictions,
            'prediction_count': len(predictions),
            'confidence_avg': sum(p.get('confidence', 0.5) for p in [predictions]) / max(len(predictions), 1)
        }
    
    def _generate_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate human-readable summary"""
        summary_parts = []
        
        if 'engagement_level' in metrics:
            summary_parts.append(f"Engagement level: {metrics['engagement_level']}")
        
        if 'performance_trend' in metrics:
            summary_parts.append(f"Performance trend: {metrics['performance_trend']}")
        
        if 'most_studied' in metrics:
            summary_parts.append(f"Most studied: {metrics['most_studied']}")
        
        return ". ".join(summary_parts) if summary_parts else "No significant patterns detected"
    
    def _generate_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        if metrics.get('engagement_level') == 'low':
            insights.append("Consider setting daily study goals to improve engagement")
        
        if metrics.get('performance_trend') == 'declining':
            insights.append("Performance declining - may need intervention or break")
        
        if metrics.get('least_studied'):
            insights.append(f"Subject '{metrics['least_studied']}' needs more attention")
        
        return insights











































































