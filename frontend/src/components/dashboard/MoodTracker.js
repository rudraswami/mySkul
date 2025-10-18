import React, { useState } from 'react';
import { Smile, Meh, Frown, Heart, Coffee, Zap, X } from 'lucide-react';

/**
 * Mood AI Chip Component
 * Tracks user mood and adapts dashboard accordingly
 */
const MoodTracker = ({ onMoodChange }) => {
  const [selectedMood, setSelectedMood] = useState(null);
  const [showMoodPicker, setShowMoodPicker] = useState(false);

  const moods = [
    {
      id: 'energized',
      label: 'Energized',
      icon: Zap,
      emoji: '⚡',
      color: 'from-yellow-400 to-orange-500',
      bgColor: 'bg-yellow-50',
      message: 'Great! Let\'s tackle your toughest topics today! 💪'
    },
    {
      id: 'happy',
      label: 'Happy',
      icon: Smile,
      emoji: '😊',
      color: 'from-green-400 to-emerald-500',
      bgColor: 'bg-green-50',
      message: 'Wonderful! Your positive energy will help you learn better! 🌟'
    },
    {
      id: 'neutral',
      label: 'Okay',
      icon: Meh,
      emoji: '😐',
      color: 'from-blue-400 to-cyan-500',
      bgColor: 'bg-blue-50',
      message: 'That\'s fine! Let\'s start with something interesting. 📚'
    },
    {
      id: 'tired',
      label: 'Tired',
      icon: Coffee,
      emoji: '😴',
      color: 'from-purple-400 to-pink-500',
      bgColor: 'bg-purple-50',
      message: 'Take it easy! We\'ll focus on lighter revision today. ☕'
    },
    {
      id: 'stressed',
      label: 'Stressed',
      icon: Frown,
      emoji: '😰',
      color: 'from-red-400 to-pink-500',
      bgColor: 'bg-red-50',
      message: 'It\'s okay to feel this way. Let\'s take small steps today. 💙'
    }
  ];

  const handleMoodSelect = (mood) => {
    setSelectedMood(mood);
    setShowMoodPicker(false);
    onMoodChange(mood);
    
    // Apply mood-based changes to dashboard
    if (mood.id === 'tired' || mood.id === 'stressed') {
      // Dim dashboard slightly
      document.body.classList.add('mood-relaxed');
    } else {
      document.body.classList.remove('mood-relaxed');
    }
  };

  return (
    <>
      {/* Mood Chip Button */}
      <div className="fixed top-20 right-6 z-40">
        {!showMoodPicker && (
          <button
            onClick={() => setShowMoodPicker(true)}
            className={`group flex items-center space-x-2 px-4 py-2 ${selectedMood ? `bg-gradient-to-r ${selectedMood.color}` : 'bg-white'} rounded-full shadow-lg hover:shadow-xl transition-all animate-float-gentle`}
          >
            {selectedMood ? (
              <>
                <span className="text-lg">{selectedMood.emoji}</span>
                <span className="text-white font-medium text-sm">{selectedMood.label}</span>
              </>
            ) : (
              <>
                <Heart className="h-5 w-5 text-purple-600" />
                <span className="text-gray-700 font-medium text-sm">How are you feeling?</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Mood Picker Modal */}
      {showMoodPicker && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm animate-scale-in">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900">How are you feeling today?</h3>
                <p className="text-sm text-gray-500 mt-1">Your mood helps us personalize your experience</p>
              </div>
              <button
                onClick={() => setShowMoodPicker(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-gray-600" />
              </button>
            </div>

            {/* Mood Options */}
            <div className="space-y-3">
              {moods.map((mood) => {
                const Icon = mood.icon;
                return (
                  <button
                    key={mood.id}
                    onClick={() => handleMoodSelect(mood)}
                    className={`w-full flex items-center space-x-4 p-4 rounded-xl border-2 transition-all hover:scale-105 ${
                      selectedMood?.id === mood.id
                        ? `border-purple-500 ${mood.bgColor}`
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <div className={`flex-shrink-0 p-3 bg-gradient-to-br ${mood.color} rounded-xl shadow-md`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="flex items-center space-x-2">
                        <span className="text-2xl">{mood.emoji}</span>
                        <h4 className="font-semibold text-gray-900">{mood.label}</h4>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{mood.message}</p>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Footer */}
            <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200">
              <p className="text-xs text-purple-700">
                <strong>💡 Did you know?</strong> Your mood affects your learning capacity. We'll adjust recommendations based on how you feel!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Mood-based Tip Banner */}
      {selectedMood && (
        <div className={`fixed bottom-6 left-1/2 transform -translate-x-1/2 max-w-lg w-full mx-4 p-4 ${selectedMood.bgColor} rounded-xl shadow-lg border-2 border-current animate-slide-up`}
             style={{ borderColor: `var(--${selectedMood.id}-color)` }}>
          <div className="flex items-start space-x-3">
            {React.createElement(selectedMood.icon, { className: "h-5 w-5 flex-shrink-0 mt-0.5" })}
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">
                {selectedMood.message}
              </p>
            </div>
            <button
              onClick={() => setSelectedMood(null)}
              className="flex-shrink-0 p-1 hover:bg-white hover:bg-opacity-50 rounded transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default MoodTracker;
