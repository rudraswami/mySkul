import React from 'react';
import { motion } from 'framer-motion';
import { Flame, MessageCircle, Sun, Moon, Zap, Bell } from 'lucide-react';

const HeroHUD = ({
    user,
    userLevel,
    userXP,
    currentStreak,
    greeting,
    onOpenMentor,
    onToggleFocus,
    onToggleTheme,
    isDarkMode
}) => {

    // XP progress calculation
    const progress = userXP % 100;

    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel-hero rounded-3xl p-1 shadow-premium-lg relative overflow-hidden"
        >
            {/* --- Background Glow Layer --- */}
            <div className="bg-white/40 dark:bg-gray-900/40 backdrop-blur-xl rounded-[22px] p-2 md:p-3 relative overflow-hidden">

                <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl -mr-32 -mt-32 animate-pulse-slow" />
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -ml-20 -mb-20" />
            </div>

            {/* --- Foreground Content --- */}
            <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-4 items-center -mt-4">


                {/* LEFT SIDE */}
                <div className="lg:col-span-7 flex items-center gap-4">
                    {/* Avatar & Level Ring */}
                    <div className="relative group cursor-pointer shrink-0">
                        <svg className="w-16 h-16 md:w-20 md:h-20 transform -rotate-90 drop-shadow-lg">
                            <circle
                                cx="50%"
                                cy="50%"
                                r="46%"
                                className="stroke-gray-200 dark:stroke-gray-700 fill-none"
                                strokeWidth="3"
                            />
                            <circle
                                cx="50%"
                                cy="50%"
                                r="46%"
                                className="stroke-purple-500 fill-none transition-all duration-1000 ease-out"
                                strokeWidth="3"
                                strokeDasharray="283"
                                strokeDashoffset={283 - (283 * progress) / 100}
                                strokeLinecap="round"
                            />
                        </svg>

                        <div className="absolute inset-1.5 rounded-full overflow-hidden border-2 border-white dark:border-gray-800 bg-gray-100 dark:bg-gray-900 flex items-center justify-center shadow-inner">
                            {user?.avatar_url ? (
                                <img src={user.avatar_url} alt="Profile" className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full bg-gradient-to-br from-purple-600 to-indigo-700 flex items-center justify-center">
                                    <span className="text-xl font-bold text-white">
                                        {user?.full_name?.charAt(0) || 'S'}
                                    </span>
                                </div>
                            )}
                        </div>

                        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-2 py-0.5 rounded-full text-[9px] font-black tracking-wider shadow-lg border border-white/20 dark:border-gray-900/20">
                            LVL {userLevel}
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center gap-2 mb-0.5">
                            <h1 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">
                                {greeting?.greeting?.split(',')[0] || "Hey Learner"}
                            </h1>
                            <span className="text-xl animate-wave">👋</span>
                        </div>

                        <p className="text-gray-600 dark:text-gray-300 text-sm font-medium flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                            {greeting?.message || "Ready to learn?"}
                        </p>

                        {/* Mini XP Bar */}
                        <div className="mt-2 flex items-center gap-2 text-[10px] font-medium text-gray-500 dark:text-gray-400">
                            <div className="w-20 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                            <span>{userXP} XP</span>
                        </div>
                    </div>
                </div>

                {/* RIGHT SIDE ACTIONS */}
                <div className="lg:col-span-5 flex items-center justify-end gap-4">

                    {/* Streak Badge */}
                    <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-orange-500/10 border border-orange-500/20 rounded-full">
                        <Flame className={`w-4 h-4 ${currentStreak > 0 ? 'text-orange-500' : 'text-gray-400'}`} />
                        <span className="text-sm font-bold text-orange-600 dark:text-orange-400">{currentStreak} Day Streak</span>
                    </div>

                    {/* Quick Action Buttons */}
                    <div className="flex items-center gap-2">
                        <button className="relative p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors mr-1">
                            <Bell className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-gray-900" />
                        </button>

                        <div className="h-8 w-px bg-gray-200 dark:bg-gray-700 mx-1"></div>

                        <button
                            onClick={onOpenMentor}
                            className="group p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:scale-105 hover:shadow-lg transition-all">
                            <MessageCircle className="w-4 h-4 text-blue-500 opacity-80 group-hover:opacity-100" />
                        </button>

                        <button
                            onClick={onToggleFocus}
                            className="group p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:scale-105 hover:shadow-lg transition-all">
                            <Zap className="w-4 h-4 text-yellow-500 opacity-80 group-hover:opacity-100" />
                        </button>

                        <button
                            onClick={onToggleTheme}
                            className="group p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:scale-105 hover:shadow-lg transition-all">
                            {isDarkMode ? (
                                <Sun className="w-4 h-4 text-orange-400 opacity-80 group-hover:opacity-100" />
                            ) : (
                                <Moon className="w-4 h-4 text-indigo-400 opacity-80 group-hover:opacity-100" />
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default HeroHUD;
