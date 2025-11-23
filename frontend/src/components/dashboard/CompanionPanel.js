import React from 'react';
import { motion } from 'framer-motion';
import AchievementBadges from './AchievementBadges';
import LiveLeaderboard from './LiveLeaderboard';
import UsageMeter from '../UsageMeter';
import PlanBadge from '../PlanBadge';
import { Sparkles, Shield, Activity } from 'lucide-react';

const CompanionPanel = ({ user, userXP, userLevel, subscriptionInfo, usageData }) => {
    return (
        <div className="space-y-6 md:space-y-8">

            {/* AI Companion Header / Status */}
            <div className="glass-panel rounded-2xl p-6 shadow-premium relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Sparkles className="h-24 w-24 text-purple-500" />
                </div>

                <div className="relative z-10">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                        <Shield className="h-5 w-5 text-purple-500" />
                        Companion Status
                    </h3>
                    <div className="flex items-center gap-3 mb-4">
                        <div className="h-2 flex-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-purple-500 to-blue-500 w-[75%] animate-pulse"></div>
                        </div>
                        <span className="text-xs text-purple-600 dark:text-purple-300 font-mono font-bold">ONLINE</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        "I'm analyzing your learning patterns. You're doing great on Physics today!"
                    </p>
                </div>
            </div>

            {/* Achievement Badges */}
            <AchievementBadges userXP={userXP} userLevel={userLevel} />

            {/* Live Leaderboard */}
            <LiveLeaderboard />

            {/* Usage Meters - Subscription Limits */}
            <div className="glass-panel rounded-2xl p-6 shadow-premium animate-fade-in">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <Activity className="h-5 w-5 text-blue-500" />
                        System Usage
                    </h2>
                    <PlanBadge tier={subscriptionInfo?.subscription_tier || user?.subscription_type || 'free'} />
                </div>

                <div className="space-y-4">
                    {/* AI Questions Usage */}
                    <UsageMeter
                        feature="AI Questions"
                        used={usageData?.usage?.ai_mentor?.used || 0}
                        limit={usageData?.usage?.ai_mentor?.limit || 10}
                        resetPeriod="daily"
                        icon="🤖"
                    />

                    {/* Mock Tests Usage */}
                    <UsageMeter
                        feature="Mock Tests"
                        used={usageData?.usage?.mock_tests?.used || 0}
                        limit={usageData?.usage?.mock_tests?.limit || 2}
                        resetPeriod="monthly"
                        icon="📝"
                    />

                    {/* Auto Notes Usage */}
                    <UsageMeter
                        feature="Auto Notes"
                        used={usageData?.usage?.auto_notes?.used || 0}
                        limit={usageData?.usage?.auto_notes?.limit || 5}
                        resetPeriod="monthly"
                        icon="📔"
                    />
                </div>
            </div>

        </div>
    );
};

export default CompanionPanel;
