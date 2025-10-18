import React from 'react';
import { Sparkles, TrendingUp, Target, BookOpen, ArrowRight } from 'lucide-react';

/**
 * Smart Recommendations Panel
 * AI-driven study suggestions based on user patterns
 */
const SmartRecommendations = ({ userData }) => {
  // In production, these would come from backend AI analysis
  const recommendations = [
    {
      id: 1,
      type: 'weak-topic',
      icon: Target,
      title: 'Focus on Chemical Bonding',
      description: 'Your recent test shows you need more practice in this area',
      action: 'Start Learning',
      priority: 'high',
      color: 'from-red-500 to-pink-500',
      bgColor: 'from-red-50 to-pink-50'
    },
    {
      id: 2,
      type: 'streak',
      icon: TrendingUp,
      title: 'Keep Your 7-Day Streak!',
      description: 'Study for at least 30 minutes today to maintain your streak',
      action: 'Study Now',
      priority: 'medium',
      color: 'from-orange-500 to-yellow-500',
      bgColor: 'from-orange-50 to-yellow-50'
    },
    {
      id: 3,
      type: 'revision',
      icon: BookOpen,
      title: 'Time to Revise Calculus',
      description: 'You learned this 2 weeks ago. Perfect time for revision!',
      action: 'Review Topic',
      priority: 'medium',
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'from-blue-50 to-cyan-50'
    },
    {
      id: 4,
      type: 'practice',
      icon: Sparkles,
      title: 'Take a Mock Test',
      description: 'You haven\'t practiced in 3 days. Let\'s test your knowledge!',
      action: 'Start Test',
      priority: 'low',
      color: 'from-purple-500 to-indigo-500',
      bgColor: 'from-purple-50 to-indigo-50'
    }
  ];

  const handleAction = (rec) => {
    // Handle different recommendation actions
    console.log('Action clicked:', rec);
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-premium glass-card">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl animate-pulse-glow">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">Smart Recommendations</h3>
            <p className="text-sm text-gray-500">AI-powered study suggestions</p>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec) => {
          const Icon = rec.icon;
          return (
            <div
              key={rec.id}
              className={`relative overflow-hidden rounded-xl border-2 transition-all hover:shadow-lg group ${
                rec.priority === 'high' ? 'border-red-200' :
                rec.priority === 'medium' ? 'border-yellow-200' :
                'border-gray-200'
              }`}
            >
              {/* Background gradient */}
              <div className={`absolute inset-0 bg-gradient-to-r ${rec.bgColor} opacity-50`}></div>
              
              {/* Content */}
              <div className="relative p-4 flex items-start space-x-4">
                <div className={`flex-shrink-0 p-2 bg-gradient-to-br ${rec.color} rounded-lg shadow-md group-hover:scale-110 transition-transform`}>
                  <Icon className="h-5 w-5 text-white" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-semibold text-gray-900">{rec.title}</h4>
                    {rec.priority === 'high' && (
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded-full">
                        High Priority
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                  
                  <button
                    onClick={() => handleAction(rec)}
                    className={`inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r ${rec.color} text-white rounded-lg text-sm font-medium hover:shadow-lg transition-all group-hover:translate-x-1`}
                  >
                    <span>{rec.action}</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Priority indicator line */}
              {rec.priority === 'high' && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-red-500 to-pink-500"></div>
              )}
            </div>
          );
        })}
      </div>

      {/* AI Insight Footer */}
      <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-200">
        <div className="flex items-start space-x-3">
          <Sparkles className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-xs font-semibold text-purple-900 mb-1">💡 AI Insight</p>
            <p className="text-xs text-purple-700">
              Based on your learning patterns, we recommend studying in 25-minute focused sessions with 5-minute breaks. This matches your peak concentration time!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmartRecommendations;
