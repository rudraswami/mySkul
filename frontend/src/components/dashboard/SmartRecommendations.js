import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, TrendingUp, Target, BookOpen, ArrowRight } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Smart Recommendations Panel with Dynamic API Data
 * AI-driven study suggestions based on user patterns
 */
const SmartRecommendations = ({ userData }) => {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      
      const response = await fetch(`${BACKEND_URL}/api/user/recommendations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (type) => {
    switch(type) {
      case 'focus': return Target;
      case 'streak': return TrendingUp;
      case 'review': return BookOpen;
      case 'test': return Sparkles;
      default: return Sparkles;
    }
  };

  const getColor = (priority) => {
    switch(priority) {
      case 'high': return 'from-red-500 to-pink-500';
      case 'medium': return 'from-orange-500 to-yellow-500';
      case 'low': return 'from-blue-500 to-cyan-500';
      default: return 'from-purple-500 to-indigo-500';
    }
  };

  const getBgColor = (priority) => {
    switch(priority) {
      case 'high': return 'from-red-50 to-pink-50';
      case 'medium': return 'from-orange-50 to-yellow-50';
      case 'low': return 'from-blue-50 to-cyan-50';
      default: return 'from-purple-50 to-indigo-50';
    }
  };

  const handleAction = (rec) => {
    if (rec.route) {
      navigate(rec.route);
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-premium glass-card">
        <div className="animate-shimmer h-48 rounded-xl"></div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-premium glass-card">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl animate-pulse-glow">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Smart Recommendations</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">AI-powered study suggestions</p>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.length > 0 ? (
          recommendations.map((rec) => {
            const Icon = getIcon(rec.type);
            return (
              <div
                key={rec.id}
                className={`relative overflow-hidden rounded-xl border-2 transition-all hover:shadow-lg group ${
                  rec.priority === 'high' ? 'border-red-200 dark:border-red-800' :
                  rec.priority === 'medium' ? 'border-yellow-200 dark:border-yellow-800' :
                  'border-gray-200 dark:border-gray-700'
                }`}
              >
                {/* Background gradient */}
                <div className={`absolute inset-0 bg-gradient-to-r ${getBgColor(rec.priority)} dark:opacity-20 opacity-50`}></div>
                
                {/* Content */}
                <div className="relative p-4 flex items-start space-x-4">
                  <div className={`flex-shrink-0 p-2 bg-gradient-to-br ${getColor(rec.priority)} rounded-lg shadow-md group-hover:scale-110 transition-transform`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900 dark:text-white">{rec.title}</h4>
                      {rec.priority === 'high' && (
                        <span className="px-2 py-0.5 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 text-xs font-medium rounded-full">
                          High Priority
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">{rec.description}</p>
                    
                    {/* Progress Bar */}
                    {rec.progress !== undefined && rec.progress > 0 && (
                      <div className="mb-3">
                        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                          <span>Progress</span>
                          <span>{Math.round(rec.progress)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className={`bg-gradient-to-r ${getColor(rec.priority)} h-2 rounded-full transition-all duration-500`}
                            style={{ width: `${rec.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                    
                    <button
                      onClick={() => handleAction(rec)}
                      className={`inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r ${getColor(rec.priority)} text-white rounded-lg text-sm font-medium hover:shadow-lg transition-all group-hover:translate-x-1`}
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
          })
        ) : (
          <div className="text-center py-8 text-gray-400 dark:text-gray-500">
            <Sparkles className="h-12 w-12 mx-auto mb-2 opacity-30" />
            <p className="text-sm">Keep learning! Recommendations will appear based on your progress.</p>
          </div>
        )}
      </div>

      {/* AI Insight Footer */}
      <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900 dark:to-indigo-900 rounded-xl border border-purple-200 dark:border-purple-700">
        <div className="flex items-start space-x-3">
          <Sparkles className="h-4 w-4 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-xs font-semibold text-purple-900 dark:text-purple-100 mb-1">💡 AI Insight</p>
            <p className="text-xs text-purple-700 dark:text-purple-200">
              Based on your learning patterns, we recommend studying in 25-minute focused sessions with 5-minute breaks. This matches your peak concentration time!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmartRecommendations;