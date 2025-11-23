import React, { useState, useEffect } from 'react';
import { Bot, Sparkles, TrendingUp, BookOpen, Target, Heart, Zap, MessageCircle } from 'lucide-react';

/**
 * AI Companion Component
 * Provides proactive recommendations and encouragement to students
 */
const AICompanion = ({ dashboardData, userProgress }) => {
    const [currentMessage, setCurrentMessage] = useState(null);
    const [isAnimating, setIsAnimating] = useState(false);

    useEffect(() => {
        generateSmartRecommendation();
    }, [dashboardData, userProgress]);

    // Generate contextual recommendations based on student behavior
    const generateSmartRecommendation = () => {
        const recommendations = [];

        // Check study streak
        if (dashboardData?.current_streak >= 7) {
            recommendations.push({
                type: 'celebration',
                icon: Sparkles,
                color: 'from-orange-500 to-red-500',
                title: '🔥 Amazing Streak!',
                message: `${dashboardData.current_streak} days strong! You're on fire! Keep this momentum going!`,
                action: 'Continue Learning',
                actionLink: '/ai-tutor'
            });
        } else if (dashboardData?.current_streak === 0) {
            recommendations.push({
                type: 'encouragement',
                icon: Heart,
                color: 'from-pink-500 to-rose-500',
                title: '💪 Start Your Streak!',
                message: 'Every expert was once a beginner. Start your learning streak today!',
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
                    message: `I noticed ${weakSubject.name} needs attention. Let's work on "${weakSubject.recent_topic}" together!`,
                    action: `Study ${weakSubject.name}`,
                    actionLink: '/ai-tutor'
                });
            }

            const strongSubject = dashboardData.subjects.find(s => s.progress >= 75);
            if (strongSubject) {
                recommendations.push({
                    type: 'celebration',
                    icon: TrendingUp,
                    color: 'from-green-500 to-emerald-500',
                    title: '🌟 Excellent Progress!',
                    message: `You're crushing ${strongSubject.name}! ${strongSubject.progress}% complete. Keep up the great work!`,
                    action: 'Take Mock Test',
                    actionLink: '/mock-tests'
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
                message: 'You haven\'t studied today yet. Even 15 minutes can make a difference!',
                action: 'Start Learning',
                actionLink: '/ai-tutor'
            });
        }

        // Motivational quotes for high performers
        if (userProgress?.xp_progress >= 80) {
            recommendations.push({
                type: 'motivation',
                icon: Zap,
                color: 'from-yellow-500 to-orange-500',
                title: '⚡ Almost There!',
                message: `Just ${100 - userProgress.xp_progress}% away from leveling up! You've got this!`,
                action: 'Earn More XP',
                actionLink: '/ai-tutor'
            });
        }

        // Select a random recommendation
        if (recommendations.length > 0) {
            const selected = recommendations[Math.floor(Math.random() * recommendations.length)];
            setCurrentMessage(selected);
            setIsAnimating(true);
            setTimeout(() => setIsAnimating(false), 500);
        }
    };

    // Motivational quotes
    const motivationalQuotes = [
        "The expert in anything was once a beginner.",
        "Success is the sum of small efforts repeated day in and day out.",
        "Don't watch the clock; do what it does. Keep going.",
        "The only way to learn mathematics is to do mathematics.",
        "Believe you can and you're halfway there."
    ];

    const [quote] = useState(motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)]);

    if (!currentMessage) return null;

    const Icon = currentMessage.icon;

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
                            <h3 className="text-sm font-bold text-gray-900 dark:text-white">AI Learning Buddy</h3>
                            <span className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full font-semibold">
                                Active
                            </span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Here to help you succeed!</p>
                    </div>
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

                {/* Motivational Quote */}
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-xs text-gray-600 dark:text-gray-400 italic text-center">
                        💭 "{quote}"
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AICompanion;
