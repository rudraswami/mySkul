import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
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
  Zap,
  Heart
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import LatexRenderer from './microlesson/LatexRenderer';
import { applyGlobalModalBehavior } from '../utils/modalBehavior';

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
  const modalRef = useRef(null);

  // Apply global modal behavior (replaces manual scroll lock)
  useEffect(() => {
    if (modalRef.current) {
      return applyGlobalModalBehavior(modalRef.current, {
        trapFocus: true,
        outsideClick: false, // Prevent closing on outside click (exam results)
        onClose,
        scrollLock: true,
        closeOnEsc: false // Don't allow ESC to close exam results
      });
    }
  }, [onClose]);

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

  const resultsContent = (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 z-[9999] overflow-y-auto">
      <div className="min-h-screen py-8 px-4">
        <div className="max-w-6xl mx-auto">
          {/* Close Button - Top Right */}
          <button
            onClick={onClose}
            className="fixed top-4 right-4 z-10 p-3 rounded-full bg-white shadow-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>

          <div className="space-y-6">
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

            {/* Subject-wise Performance Chart - Enhanced */}
            {subjectData.length > 0 && (
              <Card className="bg-white shadow-xl border-2 border-purple-200 mb-8">
                <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 border-b border-purple-100 pb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-purple-500 rounded-full">
                      <Target className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-xl font-bold text-gray-900">
                        Subject-wise Performance Analysis
                      </CardTitle>
                      <p className="text-sm text-gray-600 mt-1">Your accuracy across different subjects</p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="w-full overflow-x-auto">
                    <div style={{ minWidth: '600px', minHeight: '300px' }}>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={subjectData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                          <XAxis 
                            dataKey="name" 
                            tick={{ fontSize: 14, fontWeight: 500 }} 
                            angle={-15}
                            textAnchor="end"
                            height={60}
                          />
                          <YAxis 
                            tick={{ fontSize: 14 }} 
                            label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft', style: { fontSize: 14, fontWeight: 600 } }}
                            domain={[0, 100]}
                          />
                          <Tooltip 
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                const data = payload[0].payload;
                                return (
                                  <div className="bg-white px-5 py-3 rounded-xl shadow-2xl border-2 border-purple-200">
                                    <p className="font-bold text-gray-900 text-base mb-1">{data.name}</p>
                                    <p className="text-lg font-semibold text-purple-600">Accuracy: {data.accuracy}%</p>
                                    <p className="text-sm text-gray-600 mt-1">{data.correct}/{data.total} questions correct</p>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Bar dataKey="accuracy" radius={[8, 8, 0, 0]} maxBarSize={80}>
                            {subjectData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={getBarColor(entry.accuracy)} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  {/* Legend */}
                  <div className="flex flex-wrap justify-center gap-4 mt-6 pt-4 border-t border-gray-200">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-green-500"></div>
                      <span className="text-sm text-gray-700">Excellent (≥80%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-blue-500"></div>
                      <span className="text-sm text-gray-700">Good (60-79%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-orange-500"></div>
                      <span className="text-sm text-gray-700">Fair (40-59%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded bg-red-500"></div>
                      <span className="text-sm text-gray-700">Needs Practice (&lt;40%)</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
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

            {/* AI Feedback Section - Enhanced with AI Tutor Style */}
            {results.dual_feedback && (
              <div className="mb-8 space-y-6">
                {/* Professor's Deep Analysis - Matches AI Tutor Design */}
                <Card className="bg-white shadow-xl border-2 border-blue-200 hover:shadow-2xl transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100 pb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-blue-500 rounded-full">
                        <GraduationCap className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-xl font-bold text-gray-900">
                          Professor's Deep Analysis
                        </CardTitle>
                        <p className="text-sm text-gray-600 mt-1">Detailed performance breakdown & improvement areas</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="prose prose-sm max-w-none text-gray-800 leading-relaxed space-y-3">
                      <LatexRenderer text={sanitizeText(results.dual_feedback.professor_analysis || 'Analysis not available')} />
                    </div>
                  </CardContent>
                </Card>

                {/* Mentor's Strategic Encouragement - Matches AI Tutor Design */}
                <Card className="bg-white shadow-xl border-2 border-green-200 hover:shadow-2xl transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-green-50 to-teal-50 border-b border-green-100 pb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-gradient-to-br from-green-500 to-teal-500 rounded-full">
                        <Heart className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-xl font-bold text-gray-900">
                          Mentor's Strategic Guidance
                        </CardTitle>
                        <p className="text-sm text-gray-600 mt-1">Motivational insights & next steps for success</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="prose prose-sm max-w-none text-gray-800 leading-relaxed space-y-3">
                      <LatexRenderer text={sanitizeText(results.dual_feedback.mentor_feedback || 'Great effort! Keep practicing and you\'ll achieve your goals.')} />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Action Buttons - Enhanced Design */}
            <Card className="bg-white shadow-lg">
              <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button
                    onClick={onReview}
                    className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
                  >
                    <BookOpen className="w-5 h-5" />
                    Review Answers
                  </Button>
                  
                  <Button
                    onClick={onRetake}
                    variant="outline"
                    className="flex-1 flex items-center justify-center gap-2 border-2 border-orange-500 text-orange-600 hover:bg-orange-50 py-6 text-lg font-semibold transition-all"
                  >
                    <RefreshCw className="w-5 h-5" />
                    Retake Test
                  </Button>

                  {onBackToLibrary && (
                    <Button
                      onClick={onBackToLibrary}
                      variant="outline"
                      className="flex-1 flex items-center justify-center gap-2 border-2 border-purple-500 text-purple-600 hover:bg-purple-50 py-6 text-lg font-semibold transition-all"
                    >
                      <Trophy className="w-5 h-5" />
                      Test Library
                    </Button>
                  )}
                </div>
                <p className="text-center text-sm text-gray-600 mt-4">
                  Review your performance, retake the test, or explore more challenges
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );

  // Use React Portal to render at document body level for full-screen display
  return ReactDOM.createPortal(resultsContent, document.body);
}
