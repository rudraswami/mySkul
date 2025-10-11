import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Trophy, 
  Target, 
  CheckCircle, 
  XCircle, 
  Circle,
  TrendingUp,
  RefreshCw,
  BookOpen,
  Award,
  Sparkles,
  Brain,
  GraduationCap,
  X,
  Star,
  Zap
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import LatexRenderer from './microlesson/LatexRenderer';

export default function EnhancedResultsModal({ 
  results, 
  onClose, 
  onRetake, 
  onReview, 
  onBackToLibrary,
  gamificationRewards = null // { xp_earned, badges_earned, new_level, streak }
}) {
  const [animationStep, setAnimationStep] = useState(0);
  const [displayScore, setDisplayScore] = useState(0);

  // Sanitize AI feedback text
  const sanitizeText = (text) => {
    if (!text) return '';
    
    // Remove ALL emojis
    const emojiPattern = /[\u{1F1E0}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{231A}-\u{23FF}\u{FE0F}\u{1F600}-\u{1F64F}]/gu;
    let cleaned = text.replace(emojiPattern, '');
    
    // Remove specific problematic emojis
    cleaned = cleaned.replace(/✅|❌|☑|💡|🔎|📔|💙|👇|📚|🧮|🧠|1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|6️⃣|7️⃣|8️⃣|9️⃣|🔟/g, '');
    
    // Remove markdown
    cleaned = cleaned.replace(/\*\*(.+?)\*\*/g, '$1'); // **bold**
    cleaned = cleaned.replace(/\*(.+?)\*/g, '$1');     // *italic*
    cleaned = cleaned.replace(/__(.+?)__/g, '$1');     // __underline__
    cleaned = cleaned.replace(/_(.+?)_/g, '$1');       // _italic_
    
    // Remove special characters
    cleaned = cleaned.replace(/###/g, '');
    
    return cleaned.trim();
  };

  // Animated score counter
  useEffect(() => {
    const timer = setTimeout(() => {
      if (animationStep < 3) {
        setAnimationStep(prev => prev + 1);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [animationStep]);

  useEffect(() => {
    if (animationStep >= 1 && displayScore < results.percentage) {
      const increment = Math.ceil(results.percentage / 20);
      const timer = setTimeout(() => {
        setDisplayScore(prev => Math.min(prev + increment, results.percentage));
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [animationStep, displayScore, results.percentage]);

  const getPerformanceMessage = (score) => {
    if (score >= 90) return { text: 'Outstanding! 🎉', color: 'text-green-600', emoji: '🎉' };
    if (score >= 75) return { text: 'Great Job! 👏', color: 'text-blue-600', emoji: '👏' };
    if (score >= 60) return { text: 'Good Effort! 💪', color: 'text-yellow-600', emoji: '💪' };
    if (score >= 40) return { text: 'Keep Practicing! 📚', color: 'text-orange-600', emoji: '📚' };
    return { text: 'Need More Practice 💡', color: 'text-red-600', emoji: '💡' };
  };

  const performance = getPerformanceMessage(results.percentage);

  // Prepare subject-wise data for chart
  const subjectData = Object.entries(results.subject_wise_analysis || {}).map(([subject, data]) => ({
    name: subject.length > 12 ? subject.substring(0, 12) + '...' : subject,
    accuracy: data.total > 0 ? Math.round((data.correct / data.total) * 100) : 0,
    correct: data.correct,
    total: data.total
  }));

  const getBarColor = (accuracy) => {
    if (accuracy >= 80) return '#10b981'; // green
    if (accuracy >= 60) return '#3b82f6'; // blue
    if (accuracy >= 40) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[70] p-4 overflow-y-auto">
      <div className="max-w-4xl w-full my-8">
        <Card className="shadow-2xl border-0 relative overflow-hidden">
          {/* Animated Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 opacity-50"></div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 rounded-full bg-white shadow-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>

          <CardContent className="p-8 relative z-10">
            {/* Hero Score Display */}
            <div className="text-center mb-8">
              <div className={`transform transition-all duration-500 ${animationStep >= 1 ? 'scale-100 opacity-100' : 'scale-50 opacity-0'}`}>
                <Trophy className={`w-20 h-20 mx-auto mb-4 ${performance.color}`} />
                <h2 className={`text-4xl font-bold mb-2 ${performance.color}`}>
                  {performance.text}
                </h2>
                
                {/* Circular Score */}
                <div className="relative inline-block mt-6">
                  <svg className="w-48 h-48">
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      fill="none"
                      stroke="#e5e7eb"
                      strokeWidth="12"
                    />
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      fill="none"
                      stroke="url(#gradient)"
                      strokeWidth="12"
                      strokeLinecap="round"
                      strokeDasharray={`${(displayScore / 100) * 553} 553`}
                      transform="rotate(-90 96 96)"
                      className="transition-all duration-500"
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#8b5cf6" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-5xl font-bold text-gray-800">{Math.round(displayScore)}%</span>
                    <span className="text-sm text-gray-600">Accuracy</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className={`grid grid-cols-3 gap-4 mb-8 transform transition-all duration-500 delay-300 ${
              animationStep >= 2 ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
            }`}>
              <Card className="bg-green-50 border-green-200">
                <CardContent className="p-4 text-center">
                  <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-green-600">{results.correct_answers}</p>
                  <p className="text-sm text-gray-600">Correct</p>
                </CardContent>
              </Card>

              <Card className="bg-red-50 border-red-200">
                <CardContent className="p-4 text-center">
                  <XCircle className="w-8 h-8 text-red-600 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-red-600">{results.wrong_answers}</p>
                  <p className="text-sm text-gray-600">Wrong</p>
                </CardContent>
              </Card>

              <Card className="bg-gray-50 border-gray-200">
                <CardContent className="p-4 text-center">
                  <Circle className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-gray-600">{results.unanswered}</p>
                  <p className="text-sm text-gray-600">Skipped</p>
                </CardContent>
              </Card>
            </div>

            {/* Subject-wise Performance Chart */}
            {subjectData.length > 0 && (
              <div className={`mb-8 transform transition-all duration-500 delay-500 ${
                animationStep >= 3 ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
              }`}>
                <Card className="bg-white overflow-visible">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-sm font-bold text-gray-800">
                      <Target className="w-5 h-5 text-purple-600" />
                      Subject-wise Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="overflow-x-auto">
                    <div style={{ minWidth: '500px' }}>
                      <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={subjectData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip 
                          content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                              return (
                                <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
                                  <p className="font-semibold text-gray-800">{payload[0].payload.name}</p>
                                  <p className="text-sm text-gray-600">
                                    {payload[0].payload.correct}/{payload[0].payload.total} correct
                                  </p>
                                  <p className="text-sm font-bold text-blue-600">
                                    {payload[0].value}% accuracy
                                  </p>
                                </div>
                              );
                            }
                            return null;
                          }}
                        />
                        <Bar dataKey="accuracy" radius={[8, 8, 0, 0]}>
                          {subjectData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={getBarColor(entry.accuracy)} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Gamification Rewards */}
            {gamificationRewards && (
              <div className="mb-8">
                <Card className="bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <Sparkles className="w-8 h-8 text-yellow-500" />
                      <h3 className="text-xl font-bold text-gray-800">Rewards Earned! 🎉</h3>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {/* XP Earned */}
                      <div className="text-center p-3 bg-white rounded-lg">
                        <Zap className="w-6 h-6 text-yellow-500 mx-auto mb-1" />
                        <p className="text-2xl font-bold text-yellow-600">+{gamificationRewards.xp_earned}</p>
                        <p className="text-xs text-gray-600">XP Earned</p>
                      </div>

                      {/* New Level */}
                      {gamificationRewards.new_level && (
                        <div className="text-center p-3 bg-white rounded-lg">
                          <Star className="w-6 h-6 text-purple-500 mx-auto mb-1" />
                          <p className="text-2xl font-bold text-purple-600">Level {gamificationRewards.new_level}</p>
                          <p className="text-xs text-gray-600">Level Up!</p>
                        </div>
                      )}

                      {/* Streak */}
                      {gamificationRewards.streak > 0 && (
                        <div className="text-center p-3 bg-white rounded-lg">
                          <TrendingUp className="w-6 h-6 text-orange-500 mx-auto mb-1" />
                          <p className="text-2xl font-bold text-orange-600">{gamificationRewards.streak} 🔥</p>
                          <p className="text-xs text-gray-600">Day Streak</p>
                        </div>
                      )}

                      {/* Badges */}
                      {gamificationRewards.badges_earned > 0 && (
                        <div className="text-center p-3 bg-white rounded-lg">
                          <Award className="w-6 h-6 text-blue-500 mx-auto mb-1" />
                          <p className="text-2xl font-bold text-blue-600">+{gamificationRewards.badges_earned}</p>
                          <p className="text-xs text-gray-600">New Badges</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* AI Feedback Section */}
            {results.dual_feedback && (
              <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Professor Analysis */}
                <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 shadow-lg">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base font-bold text-blue-900">
                      <Brain className="w-5 h-5 text-blue-600" />
                      Professor's Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="max-h-64 overflow-y-auto">
                    <div className="text-sm text-gray-800 leading-loose space-y-2" style={{ lineHeight: '1.8' }}>
                      <LatexRenderer text={sanitizeText(results.dual_feedback.professor_analysis || 'Analysis not available')} />
                    </div>
                  </CardContent>
                </Card>

                {/* Mentor Feedback */}
                <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 shadow-lg">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base font-bold text-green-900">
                      <GraduationCap className="w-5 h-5 text-green-600" />
                      Mentor's Encouragement
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="max-h-64 overflow-y-auto">
                    <div className="text-sm text-gray-800 leading-loose space-y-2" style={{ lineHeight: '1.8' }}>
                      <LatexRenderer text={sanitizeText(results.dual_feedback.mentor_feedback || 'Keep practicing!')} />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col md:flex-row gap-3">
              <Button
                onClick={onReview}
                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700"
              >
                <BookOpen className="w-4 h-4" />
                Review Answers
              </Button>
              
              <Button
                onClick={onRetake}
                variant="outline"
                className="flex-1 flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Retake Test
              </Button>

              {onBackToLibrary && (
                <Button
                  onClick={onBackToLibrary}
                  variant="outline"
                  className="flex-1 flex items-center justify-center gap-2"
                >
                  <Trophy className="w-4 h-4" />
                  Test Library
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
