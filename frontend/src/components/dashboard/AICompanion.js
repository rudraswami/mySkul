import React, { useState, useEffect, useCallback } from 'react';
import { Bot, Sparkles, TrendingUp, BookOpen, Target, Heart, Zap, MessageCircle, RefreshCw } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

/**
 * 🤖 AI Companion Component - Backend-Powered Intelligence
 * 
 * Phase 2 Enhancement:
 * - Fetches personalized messages from backend API
 * - Uses MagicContext + Error Genome™ + Exam Urgency
 * - Falls back to frontend logic if API fails
 * 
 * This is NOT random selection anymore - it's TRUE intelligence!
 */
const AICompanion = ({ dashboardData, userProgress }) => {
    const [currentMessage, setCurrentMessage] = useState(null);
    const [isAnimating, setIsAnimating] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isIntelligent, setIsIntelligent] = useState(false);

    // Get auth token
    const getAuthHeaders = () => {
        const token = localStorage.getItem('dhruv_ai_token');
        return token ? { Authorization: `Bearer ${token}` } : {};
    };

    // Color mapping for backend colors
    const colorMap = {
        purple: 'from-purple-500 to-indigo-500',
        green: 'from-green-500 to-emerald-500',
        orange: 'from-orange-500 to-red-500',
        blue: 'from-blue-500 to-cyan-500',
        pink: 'from-pink-500 to-rose-500',
        yellow: 'from-yellow-500 to-orange-500'
    };

    // Icon mapping for message types
    const iconMap = {
        celebration: Sparkles,
        error_pattern: Target,
        exam_countdown: Zap,
        revision_due: BookOpen,
        weak_topic: Target,
        comeback: Heart,
        focus: BookOpen,
        fallback: Bot
    };

    // 🧠 Fetch intelligent message from backend
    const fetchIntelligentMessage = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await axios.get(`${API_URL}/api/dashboard/companion`, {
                headers: getAuthHeaders(),
                timeout: 6000
            });

            const data = response.data;
            
            if (data && data.title && data.message) {
                setCurrentMessage({
                    type: data.message_type || 'focus',
                    icon: iconMap[data.message_type] || Bot,
                    color: colorMap[data.color] || colorMap.purple,
                    title: data.title,
                    message: data.message,
                    action: data.action_label || 'Start Learning',
                    actionLink: '/ai-tutor',
                    studentContext: data.student_context || {}
                });
                setIsIntelligent(data.intelligent === true);
                setIsAnimating(true);
                setTimeout(() => setIsAnimating(false), 500);
                return true;
            }
        } catch (error) {
            console.log('Companion API unavailable, using fallback:', error.message);
        } finally {
            setIsLoading(false);
        }
        return false;
    }, []);

    // 📝 Fallback: Frontend-only recommendations
    const generateFallbackRecommendation = useCallback(() => {
        const recommendations = [];

        // Check study streak
        if (dashboardData?.current_streak >= 7) {
            recommendations.push({
                type: 'celebration',
                icon: Sparkles,
                color: 'from-orange-500 to-red-500',
                title: '🔥 Amazing Streak!',
                message: `${dashboardData.current_streak} days strong! You're on fire!`,
                action: 'Continue Learning',
                actionLink: '/ai-tutor'
            });
        } else if (dashboardData?.current_streak === 0) {
            recommendations.push({
                type: 'encouragement',
                icon: Heart,
                color: 'from-pink-500 to-rose-500',
                title: '💪 Start Your Streak!',
                message: 'Every expert was once a beginner. Start today!',
                action: 'Begin Session',
                actionLink: '/ai-tutor'
            });
        }

        // Check subject progress
        if (dashboardData?.subjects) {
            const weakSubject = dashboardData.subjects.find(s => s.progress < 40);
            if (weakSubject) {
                recommendations.push({
                    type: 'suggestion',
                    icon: Target,
                    color: 'from-blue-500 to-cyan-500',
                    title: '📚 Focus Suggestion',
                    message: `${weakSubject.name} needs attention. Let's work on it!`,
                    action: `Study ${weakSubject.name}`,
                    actionLink: '/ai-tutor'
                });
            }
        }

        // Check study time
        if (dashboardData?.study_time_today === '0h 0m') {
            recommendations.push({
                type: 'reminder',
                icon: BookOpen,
                color: 'from-purple-500 to-indigo-500',
                title: '👋 Ready to Learn?',
                message: 'Even 15 minutes can make a difference!',
                action: 'Start Learning',
                actionLink: '/ai-tutor'
            });
        }

        // Select from available recommendations
        if (recommendations.length > 0) {
            // Prioritize weak subjects and reminders over celebrations
            const prioritized = recommendations.sort((a, b) => {
                const priority = { suggestion: 3, reminder: 2, encouragement: 1, celebration: 0 };
                return (priority[b.type] || 0) - (priority[a.type] || 0);
            });
            setCurrentMessage(prioritized[0]);
            setIsIntelligent(false);
            setIsAnimating(true);
            setTimeout(() => setIsAnimating(false), 500);
        }
    }, [dashboardData]);

    // 🚀 Main effect: Try backend first, fallback to frontend
    useEffect(() => {
        const loadCompanionMessage = async () => {
            // Try backend API first
            const success = await fetchIntelligentMessage();
            
            // Fallback to frontend logic if API fails
            if (!success) {
                generateFallbackRecommendation();
            }
        };

        loadCompanionMessage();
    }, [fetchIntelligentMessage, generateFallbackRecommendation]);

    // Refresh handler
    const handleRefresh = async () => {
        setIsAnimating(true);
        const success = await fetchIntelligentMessage();
        if (!success) {
            generateFallbackRecommendation();
        }
    };

    // Motivational quotes (shown only when NOT intelligent)
    const motivationalQuotes = [
        "The expert in anything was once a beginner.",
        "Success is the sum of small efforts repeated day in and day out.",
        "Don't watch the clock; do what it does. Keep going.",
        "The only way to learn mathematics is to do mathematics.",
        "Believe you can and you're halfway there."
    ];

    const [quote] = useState(motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)]);

    if (!currentMessage && !isLoading) return null;

    const Icon = currentMessage?.icon || Bot;

    // Loading state
    if (isLoading && !currentMessage) {
        return (
            <div className="glass-card rounded-2xl p-6 shadow-premium relative overflow-hidden">
                <div className="flex items-center justify-center py-8">
                    <RefreshCw className="h-6 w-6 text-purple-500 animate-spin" />
                    <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">Loading your personalized message...</span>
                </div>
            </div>
        );
    }

    if (!currentMessage) return null;

    return (
        <div className={`glass-card rounded-2xl p-6 shadow-premium relative overflow-hidden transition-all duration-500 ${isAnimating ? 'scale-105' : 'scale-100'}`}>
            {/* Animated Background */}
            <div className={`absolute inset-0 bg-gradient-to-br ${currentMessage.color} opacity-5 animate-pulse-slow`}></div>

            <div className="relative z-10">
                {/* AI Avatar */}
                <div className="flex items-start space-x-4 mb-4">
                    <div className={`relative flex-shrink-0 p-3 bg-gradient-to-br ${currentMessage.color} rounded-2xl shadow-lg animate-pulse-glow`}>
                        <Bot className="h-6 w-6 text-white" />
                        {/* Pulse indicator */}
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full"></div>
                    </div>

                    <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                            <h3 className="text-sm font-bold text-gray-900 dark:text-white">Sathi</h3>
                            <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                                isIntelligent 
                                    ? 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300' 
                                    : 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                            }`}>
                                {isIntelligent ? '✨ Personalized' : 'Active'}
                            </span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                            {isIntelligent ? 'Based on your learning patterns' : 'Here to help you succeed!'}
                        </p>
                    </div>

                    {/* Refresh button */}
                    <button
                        onClick={handleRefresh}
                        disabled={isLoading}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="Get new message"
                    >
                        <RefreshCw className={`h-4 w-4 text-gray-400 ${isLoading ? 'animate-spin' : ''}`} />
                    </button>
                </div>

                {/* Message Card */}
                <div className="bg-white/50 dark:bg-gray-800/50 rounded-xl p-4 mb-4 backdrop-blur-sm border border-gray-200 dark:border-gray-700">
                    <div className="flex items-start space-x-3">
                        <Icon className={`h-5 w-5 mt-0.5 bg-gradient-to-br ${currentMessage.color} bg-clip-text text-transparent`} style={{ WebkitTextFillColor: 'transparent' }} />
                        <div className="flex-1">
                            <h4 className="text-base font-bold text-gray-900 dark:text-white mb-2">
                                {currentMessage.title}
                            </h4>
                            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                                {currentMessage.message}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Action Button */}
                <div className="flex items-center justify-between">
                    <button
                        onClick={() => window.location.href = currentMessage.actionLink}
                        className={`flex-1 py-3 px-4 bg-gradient-to-r ${currentMessage.color} text-white font-bold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center justify-center space-x-2`}
                    >
                        <span>{currentMessage.action}</span>
                        <MessageCircle className="h-4 w-4" />
                    </button>
                </div>

                {/* Context indicator for intelligent messages */}
                {isIntelligent && currentMessage.studentContext && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                            {currentMessage.studentContext.streak > 0 && (
                                <span className="flex items-center gap-1">
                                    🔥 {currentMessage.studentContext.streak} days
                                </span>
                            )}
                            {currentMessage.studentContext.days_to_exam && (
                                <span className="flex items-center gap-1">
                                    📅 {currentMessage.studentContext.days_to_exam} days to {currentMessage.studentContext.exam_name}
                                </span>
                            )}
                        </div>
                    </div>
                )}

                {/* Motivational Quote (only for non-intelligent fallback) */}
                {!isIntelligent && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <p className="text-xs text-gray-600 dark:text-gray-400 italic text-center">
                            💭 "{quote}"
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AICompanion;
