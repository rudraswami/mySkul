/**
 * Simplified AI Tutor 2.0 Component for Testing
 * Basic implementation to test feature toggle functionality
 */
import React from 'react';
import { Button } from './ui/button';
import { ArrowLeft, Sparkles } from 'lucide-react';

const SimpleAITutor20 = ({ onBackToV1, className = '' }) => {
  return (
    <div className={`flex flex-col h-full bg-gray-50 p-6 ${className}`}>
      {/* Header */}
      <div className="mb-6 bg-white rounded-xl p-6 shadow-sm border border-purple-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              onClick={onBackToV1}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Classic</span>
            </Button>
            <div className="h-4 w-px bg-gray-300" />
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <span className="text-lg font-semibold text-gray-800">AI Tutor 2.0 Beta</span>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-4 rounded-lg text-white">
          <h2 className="text-xl font-bold mb-2">🎉 Welcome to AI Tutor 2.0!</h2>
          <p className="opacity-90">
            Enhanced with visual-first learning, emotion-aware responses, and progressive disclosure.
          </p>
        </div>
      </div>

      {/* Welcome Content */}
      <div className="flex-1 bg-white rounded-xl p-8 shadow-sm">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full mx-auto mb-4 flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          
          <h3 className="text-2xl font-bold text-gray-800 mb-4">
            AI Tutor 2.0 is Active!
          </h3>
          
          <div className="space-y-4 max-w-md mx-auto text-gray-600">
            <p>✨ Visual-first concept learning</p>
            <p>🧠 Emotion-aware persona adaptation</p>
            <p>📚 Progressive disclosure explanations</p>
            <p>⚡ Enhanced micro-interactions</p>
          </div>
          
          <div className="mt-8 space-y-3">
            <p className="text-sm text-gray-500">Test the new features:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                Professor Mode (Blue)
              </span>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                Mentor Mode (Green)
              </span>
              <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                Hybrid Mode (Purple)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Message Input Test Area */}
      <div className="mt-4 bg-white rounded-xl p-4 shadow-sm">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            placeholder="Try asking: 'Explain quadratic equations' to test persona adaptation..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
          <Button className="bg-purple-600 hover:bg-purple-700">
            <span>Send</span>
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          AI Tutor 2.0 Beta - Enhanced visual and emotion-aware learning experience
        </p>
      </div>
    </div>
  );
};

export default SimpleAITutor20;