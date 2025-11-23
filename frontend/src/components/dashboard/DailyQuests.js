import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Circle, Gift, Clock, Zap, Trophy } from 'lucide-react';

/**
 * Daily Quests Component
 * Displays 3 daily tasks to drive user engagement
 */
const DailyQuests = ({ onQuestComplete, onAllQuestsComplete }) => {
    const [quests, setQuests] = useState([]);
    const [timeRemaining, setTimeRemaining] = useState('');
    const [allCompleted, setAllCompleted] = useState(false);
    const [loading, setLoading] = useState(true);

    // Fetch Quests from Backend
    useEffect(() => {
        const fetchQuests = async () => {
            try {
                const token = localStorage.getItem('dhruv_ai_token');
                const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/gamification/daily-quests`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    setQuests(data.quests);

                    // Check if all already completed
                    if (data.quests.length > 0 && data.quests.every(q => q.completed)) {
                        setAllCompleted(true);
                        if (onAllQuestsComplete) onAllQuestsComplete();
                    }
                }
            } catch (error) {
                console.error('Failed to fetch daily quests:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchQuests();
    }, []);

    // Countdown Timer
    useEffect(() => {
        const updateTimer = () => {
            const now = new Date();
            const midnight = new Date();
            midnight.setHours(24, 0, 0, 0);
            const diff = midnight - now;

            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

            setTimeRemaining(`${hours}h ${minutes}m`);
        };

        updateTimer();
        const timer = setInterval(updateTimer, 60000);
        return () => clearInterval(timer);
    }, []);

    const handleComplete = async (id) => {
        // Optimistic update
        const updatedQuests = quests.map(q =>
            q.id === id ? { ...q, completed: true } : q
        );
        setQuests(updatedQuests);

        try {
            const token = localStorage.getItem('dhruv_ai_token');
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/gamification/daily-quests/${id}/complete`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                if (onQuestComplete) onQuestComplete(data.xp_awarded);
            }
        } catch (error) {
            console.error('Failed to complete quest:', error);
            // Revert on error (optional, but good practice)
        }

        // Check if all completed
        if (updatedQuests.every(q => q.completed)) {
            setAllCompleted(true);
            if (onAllQuestsComplete) onAllQuestsComplete();
        }
    };

    const getIcon = (iconName) => {
        switch (iconName) {
            case 'Zap': return <Zap className="h-5 w-5" />;
            case 'Trophy': return <Trophy className="h-5 w-5" />;
            case 'Clock': return <Clock className="h-5 w-5" />;
            case 'CheckCircle': return <CheckCircle className="h-5 w-5" />;
            default: return <Circle className="h-5 w-5" />;
        }
    };

    return (
        <div className="glass-panel rounded-2xl p-6 shadow-premium relative overflow-hidden h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl shadow-lg animate-pulse-slow">
                        <Gift className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">Daily Quests</h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                            <Clock className="h-3 w-3 mr-1" /> Resets in {timeRemaining}
                        </p>
                    </div>
                </div>

                {allCompleted && (
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg"
                    >
                        ALL COMPLETE!
                    </motion.div>
                )}
            </div>

            {/* Quest List */}
            <div className="space-y-3 flex-1">
                {loading ? (
                    <div className="space-y-3">
                        {[1, 2, 3].map(i => <div key={i} className="h-16 bg-gray-200 dark:bg-gray-800/50 rounded-xl animate-pulse"></div>)}
                    </div>
                ) : (
                    <AnimatePresence>
                        {quests.map((quest, index) => (
                            <motion.div
                                key={quest.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className={`relative p-4 rounded-xl border transition-all duration-300 ${quest.completed
                                    ? 'bg-green-500/10 border-green-500/30'
                                    : 'bg-white/50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 hover:bg-white dark:hover:bg-gray-800'
                                    }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <button
                                            onClick={() => !quest.completed && handleComplete(quest.id)}
                                            className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${quest.completed
                                                ? 'bg-green-500 text-white scale-110'
                                                : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 hover:bg-gray-300 dark:hover:bg-gray-600'
                                                }`}
                                        >
                                            {quest.completed ? <CheckCircle className="h-5 w-5" /> : <Circle className="h-5 w-5" />}
                                        </button>

                                        <div>
                                            <h4 className={`font-semibold text-sm ${quest.completed ? 'text-green-600 dark:text-green-400 line-through' : 'text-gray-800 dark:text-gray-200'}`}>
                                                {quest.title}
                                            </h4>
                                            <div className="flex items-center space-x-2 mt-1">
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${quest.type === 'easy' ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400' :
                                                    quest.type === 'medium' ? 'bg-yellow-100 dark:bg-yellow-500/20 text-yellow-600 dark:text-yellow-400' :
                                                        'bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400'
                                                    }`}>
                                                    {quest.type.toUpperCase()}
                                                </span>
                                                <span className="text-xs text-yellow-600 dark:text-yellow-500 font-bold">+{quest.xp} XP</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Completion Shine Effect */}
                                {quest.completed && (
                                    <motion.div
                                        initial={{ x: '-100%' }}
                                        animate={{ x: '100%' }}
                                        transition={{ duration: 0.8 }}
                                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12 pointer-events-none"
                                    />
                                )}
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}
            </div>
        </div>
    );
};

export default DailyQuests;
