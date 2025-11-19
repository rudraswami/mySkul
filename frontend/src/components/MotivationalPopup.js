import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { X, TrendingUp, Zap, Target, Award } from 'lucide-react';
import GlobalModal from './modals/GlobalModal';

const MOTIVATIONAL_MESSAGES = {
  excellent: {
    title: "Outstanding Performance! 🎉",
    messages: [
      "You're absolutely crushing it! Keep this momentum going!",
      "Wow! You're in the top tier of performers. Incredible work!",
      "This is the mark of a champion. You're destined for greatness!",
      "Phenomenal score! Your dedication is truly paying off!"
    ],
    emoji: "🏆",
    color: "from-green-400 to-emerald-600"
  },
  great: {
    title: "Great Job! 👏",
    messages: [
      "You're making excellent progress. Keep pushing forward!",
      "Solid performance! You're on the right track to success!",
      "Well done! Your hard work is clearly showing results!",
      "Strong work! You're building great momentum!"
    ],
    emoji: "⭐",
    color: "from-blue-400 to-indigo-600"
  },
  good: {
    title: "Good Progress! 💪",
    messages: [
      "You're improving with every test. Don't stop now!",
      "Nice work! Consistency is key to mastery!",
      "You're on your way up! Keep practicing!",
      "Good effort! Every test makes you stronger!"
    ],
    emoji: "📈",
    color: "from-yellow-400 to-orange-600"
  },
  improving: {
    title: "Keep Going! 🚀",
    messages: [
      "Every expert was once a beginner. You're getting there!",
      "Don't give up! Each attempt brings you closer to success!",
      "Remember: Progress, not perfection. You're doing great!",
      "The journey of mastery starts with a single test. Keep going!"
    ],
    emoji: "💡",
    color: "from-purple-400 to-pink-600"
  }
};

export default function MotivationalPopup({ performance, onClose, stats = {} }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Fade in animation
    setTimeout(() => setIsVisible(true), 100);
  }, []);
  
  const getMotivationalContent = () => {
    const score = performance?.percentage || 0;
    if (score >= 85) return MOTIVATIONAL_MESSAGES.excellent;
    if (score >= 70) return MOTIVATIONAL_MESSAGES.great;
    if (score >= 50) return MOTIVATIONAL_MESSAGES.good;
    return MOTIVATIONAL_MESSAGES.improving;
  };

  const content = getMotivationalContent();
  const randomMessage = content.messages[Math.floor(Math.random() * content.messages.length)];

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  return (
    <GlobalModal isOpen onClose={handleClose} maxWidth="32rem">
      <Card
        className={`w-full bg-gradient-to-br ${content.color} border-0 shadow-2xl transition-all duration-300 ${
          isVisible ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 rounded-full bg-white/20 backdrop-blur-sm hover:bg-white/30 transition-colors"
        >
          <X className="w-5 h-5 text-white" />
        </button>

        <CardContent className="p-8 text-white text-center">
          {/* Animated emoji */}
          <div className="text-8xl mb-4 animate-bounce">
            {content.emoji}
          </div>

          {/* Title */}
          <h2 className="text-3xl font-bold mb-4">
            {content.title}
          </h2>

          {/* Message */}
          <p className="text-xl mb-6 leading-relaxed">
            {randomMessage}
          </p>

          {/* Stats highlights */}
          {stats && (
            <div className="grid grid-cols-3 gap-4 mb-6">
              {stats.improvement && (
                <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                  <TrendingUp className="w-6 h-6 mx-auto mb-1" />
                  <p className="text-sm font-semibold">+{stats.improvement}%</p>
                  <p className="text-xs opacity-80">Improvement</p>
                </div>
              )}
              
              {stats.xp_earned && (
                <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                  <Zap className="w-6 h-6 mx-auto mb-1" />
                  <p className="text-sm font-semibold">+{stats.xp_earned}</p>
                  <p className="text-xs opacity-80">XP Earned</p>
                </div>
              )}
              
              {stats.streak && (
                <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                  <Award className="w-6 h-6 mx-auto mb-1" />
                  <p className="text-sm font-semibold">{stats.streak} Days</p>
                  <p className="text-xs opacity-80">Streak</p>
                </div>
              )}
            </div>
          )}

          {/* Call to action */}
          <div className="space-y-3">
            <Button
              onClick={handleClose}
              className="w-full bg-white text-gray-800 hover:bg-gray-100 font-semibold py-6 text-lg"
            >
              Continue Learning →
            </Button>
            <p className="text-sm opacity-80">
              {performance?.percentage >= 85 
                ? "Share your achievement with friends!" 
                : "Take another test to improve even more!"}
            </p>
          </div>
        </CardContent>
      </Card>
    </GlobalModal>
  );
}
