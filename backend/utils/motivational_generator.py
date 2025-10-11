"""
Motivational Message Generator for AI Tutor 2.1
Combines real user analytics with adaptive messaging based on sentiment
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class MotivationalGenerator:
    """Generate personalized motivational messages"""
    
    def __init__(self):
        self.templates = {
            'improvement': [
                "📈 You've improved your {subject} accuracy by {improvement}% this week! Keep the momentum going 💪",
                "🚀 Your {subject} performance is trending up {improvement}% — you're on fire!",
                "⭐ Amazing progress! {improvement}% improvement in {subject} shows your dedication is paying off!",
            ],
            'streak': [
                "🔥 {streak} day streak! You're building unstoppable momentum!",
                "💎 {streak} consecutive days of learning — consistency is your superpower!",
                "⚡ {streak} days in a row! Your discipline is inspiring!",
            ],
            'mastery': [
                "🏆 You've mastered {topic}! Ready for the next challenge?",
                "✨ {topic} is now in your skill set — time to level up!",
                "🎯 {mastery}% mastery in {topic} — you're becoming an expert!",
            ],
            'encouragement': [
                "💙 Learning takes time — every question brings you closer to mastery!",
                "🌟 Your curiosity is your strength — keep asking great questions!",
                "💪 Challenges help you grow — you're doing amazing!",
            ],
            'focus': [
                "🎯 Your focus level is strong today — let's tackle a harder topic!",
                "🧠 You're in the zone! This is the perfect time for deep learning.",
                "💫 Great concentration today — make the most of this momentum!",
            ]
        }
    
    def generate(self, analytics_data: Dict[str, Any], sentiment: str, subject: str) -> Dict[str, Any]:
        """
        Generate motivational message based on analytics and sentiment
        
        Args:
            analytics_data: User's analytics (accuracy, streak, mastery, etc.)
            sentiment: Current detected sentiment (confusion, confidence, curiosity, etc.)
            subject: Current subject being studied
        
        Returns:
            Dict with message, icon, and animation type
        """
        import random
        
        message = ""
        animation_type = "celebration"  # Lottie animation type
        
        # Extract analytics
        accuracy = analytics_data.get('accuracy', 0)
        previous_accuracy = analytics_data.get('previous_accuracy', 0)
        streak = analytics_data.get('streak', 0)
        mastery = analytics_data.get('mastery', 0)
        topic = analytics_data.get('current_topic', subject)
        
        # Calculate improvement
        improvement = accuracy - previous_accuracy if previous_accuracy > 0 else 0
        
        # Priority 1: Improvement (if significant)
        if improvement >= 5:
            message = random.choice(self.templates['improvement']).format(
                subject=subject,
                improvement=round(improvement, 1)
            )
            animation_type = "celebration"
        
        # Priority 2: Streak (if active)
        elif streak >= 3:
            message = random.choice(self.templates['streak']).format(
                streak=streak
            )
            animation_type = "fire"
        
        # Priority 3: Mastery (if high)
        elif mastery >= 80:
            message = random.choice(self.templates['mastery']).format(
                topic=topic,
                mastery=round(mastery, 1)
            )
            animation_type = "trophy"
        
        # Priority 4: Sentiment-based
        elif sentiment == 'confusion' or sentiment == 'frustration':
            message = random.choice(self.templates['encouragement'])
            animation_type = "heart"
        
        elif sentiment == 'confidence' or sentiment == 'curiosity':
            message = random.choice(self.templates['focus'])
            animation_type = "rocket"
        
        # Fallback: Generic encouragement
        else:
            message = random.choice(self.templates['encouragement'])
            animation_type = "star"
        
        return {
            'message': message,
            'animation_type': animation_type,
            'stats': {
                'accuracy': accuracy,
                'improvement': improvement,
                'streak': streak,
                'mastery': mastery
            }
        }
    
    def get_lottie_animation_url(self, animation_type: str) -> str:
        """Get Lottie animation URL for animation type"""
        lottie_urls = {
            'celebration': 'https://assets5.lottiefiles.com/packages/lf20_touohxv0.json',
            'fire': 'https://assets9.lottiefiles.com/packages/lf20_yfsxxxdp.json',
            'trophy': 'https://assets10.lottiefiles.com/packages/lf20_jwjvhg3v.json',
            'heart': 'https://assets4.lottiefiles.com/packages/lf20_lk80fpsm.json',
            'rocket': 'https://assets8.lottiefiles.com/packages/lf20_jpcmikjb.json',
            'star': 'https://assets2.lottiefiles.com/packages/lf20_s2lryxtd.json',
        }
        return lottie_urls.get(animation_type, lottie_urls['star'])