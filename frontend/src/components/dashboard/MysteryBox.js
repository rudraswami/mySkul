import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Gift, Lock, Sparkles, Zap } from 'lucide-react';

/**
 * Mystery Box Component
 * Variable reward schedule to drive engagement
 */
const MysteryBox = ({ isUnlocked = false, onOpen }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [reward, setReward] = useState(null);

    const handleOpen = () => {
        if (!isUnlocked || isOpen) return;

        setIsOpen(true);

        // Simulate reward calculation
        const rewards = [
            { type: 'xp', amount: 100, label: '100 XP', icon: Zap, color: 'text-yellow-400' },
            { type: 'streak', amount: 1, label: 'Streak Freeze', icon: Sparkles, color: 'text-blue-400' },
            { type: 'xp', amount: 500, label: '500 XP (Jackpot!)', icon: Trophy, color: 'text-purple-400' },
        ];

        const selectedReward = rewards[Math.floor(Math.random() * rewards.length)];
        setReward(selectedReward);

        if (onOpen) onOpen(selectedReward);
    };

    return (
        <div className="glass-panel rounded-2xl p-6 shadow-premium relative overflow-hidden text-center h-full flex flex-col justify-center">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Daily Mystery Box</h3>

            <div className="relative h-40 flex items-center justify-center">
                <AnimatePresence mode='wait'>
                    {!isOpen ? (
                        <motion.div
                            key="box"
                            whileHover={isUnlocked ? { scale: 1.1, rotate: [0, -5, 5, -5, 5, 0] } : {}}
                            whileTap={isUnlocked ? { scale: 0.9 } : {}}
                            onClick={handleOpen}
                            className={`relative cursor-pointer ${!isUnlocked && 'opacity-50 grayscale'}`}
                        >
                            <Gift className={`h-24 w-24 ${isUnlocked ? 'text-purple-500' : 'text-gray-600'}`} />

                            {
                                !isUnlocked && (
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <Lock className="h-8 w-8 text-gray-400" />
                                    </div>
                                )
                            }

                            {
                                isUnlocked && (
                                    <motion.div
                                        animate={{ opacity: [0.5, 1, 0.5] }}
                                        transition={{ duration: 2, repeat: Infinity }}
                                        className="absolute -inset-4 bg-purple-500/20 blur-xl rounded-full -z-10"
                                    />
                                )
                            }
                        </motion.div >
                    ) : (
                        <motion.div
                            key="reward"
                            initial={{ scale: 0, rotate: 180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{ type: "spring", damping: 12 }}
                            className="flex flex-col items-center"
                        >
                            <div className="relative">
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                                    className="absolute -inset-8 bg-gradient-to-r from-yellow-500/20 to-purple-500/20 blur-xl rounded-full -z-10"
                                />
                                {reward && <reward.icon className={`h-16 w-16 ${reward.color}`} />}
                            </div>
                            <motion.h4
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                                className={`text-xl font-bold mt-4 ${reward?.color}`}
                            >
                                {reward?.label}
                            </motion.h4>
                        </motion.div>
                    )}
                </AnimatePresence >
            </div >

            <p className="text-sm text-gray-400 mt-4">
                {isOpen
                    ? "Come back tomorrow for more!"
                    : isUnlocked
                        ? "Tap to open your reward!"
                        : "Complete all Daily Quests to unlock"}
            </p>
        </div >
    );
};

import { Trophy } from 'lucide-react'; // Import missing icon

export default MysteryBox;
