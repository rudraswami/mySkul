import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Atom, Calculator, FlaskConical, ChevronRight, Star, Zap } from 'lucide-react';

const SkillTree = ({ subjects }) => {
    // Map subject names to icons and colors
    const getSubjectConfig = (name) => {
        const lowerName = name.toLowerCase();
        if (lowerName.includes('math')) return {
            icon: Calculator,
            color: 'text-blue-500',
            gradient: 'from-blue-500 to-cyan-400',
            bg: 'bg-blue-500/10',
            border: 'border-blue-500/20',
            shadow: 'shadow-blue-500/20'
        };
        if (lowerName.includes('phys')) return {
            icon: Atom,
            color: 'text-purple-500',
            gradient: 'from-purple-500 to-pink-400',
            bg: 'bg-purple-500/10',
            border: 'border-purple-500/20',
            shadow: 'shadow-purple-500/20'
        };
        if (lowerName.includes('chem')) return {
            icon: FlaskConical,
            color: 'text-emerald-500',
            gradient: 'from-emerald-500 to-teal-400',
            bg: 'bg-emerald-500/10',
            border: 'border-emerald-500/20',
            shadow: 'shadow-emerald-500/20'
        };
        return {
            icon: BookOpen,
            color: 'text-gray-500',
            gradient: 'from-gray-500 to-gray-400',
            bg: 'bg-gray-500/10',
            border: 'border-gray-500/20',
            shadow: 'shadow-gray-500/20'
        };
    };

    return (
        <div className="relative py-4">
            <div className="flex items-center justify-between mb-6 px-2">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-500" />
                    Knowledge Neural Network
                </h3>
                <button className="text-xs font-medium text-purple-600 dark:text-purple-400 hover:underline">
                    View Full Map
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {subjects.map((subject, index) => {
                    const config = getSubjectConfig(subject.name);
                    const Icon = config.icon;
                    const progress = subject.progress || 0;
                    const level = Math.floor(progress / 10) + 1;

                    return (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            whileHover={{ y: -5 }}
                            className={`relative group rounded-2xl p-1 bg-gradient-to-br ${config.gradient} p-[1px]`}
                        >
                            <div className="bg-white dark:bg-gray-900 rounded-2xl p-5 h-full relative overflow-hidden">
                                {/* Background Decor */}
                                <div className={`absolute top-0 right-0 w-32 h-32 ${config.bg} rounded-full blur-3xl -mr-16 -mt-16 opacity-50 transition-opacity group-hover:opacity-80`}></div>

                                {/* Header: Icon & Level */}
                                <div className="flex items-start justify-between mb-4 relative z-10">
                                    <div className={`p-3 rounded-xl ${config.bg} border ${config.border} group-hover:scale-110 transition-transform duration-300`}>
                                        <Icon className={`w-6 h-6 ${config.color}`} />
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Level</span>
                                        <span className={`text-xl font-black ${config.color}`}>{level}</span>
                                    </div>
                                </div>

                                {/* Title & Topic */}
                                <div className="mb-6 relative z-10">
                                    <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-1 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-gray-900 group-hover:to-gray-600 dark:group-hover:from-white dark:group-hover:to-gray-300 transition-all">
                                        {subject.name}
                                    </h4>
                                    <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                        <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                                        Current: {subject.recent_topic || "Foundations"}
                                    </div>
                                </div>

                                {/* Progress Bar */}
                                <div className="relative z-10 mb-6">
                                    <div className="flex justify-between text-xs mb-1.5">
                                        <span className="font-medium text-gray-500">Mastery</span>
                                        <span className={`font-bold ${config.color}`}>{progress}%</span>
                                    </div>
                                    <div className="h-2 w-full bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${progress}%` }}
                                            transition={{ duration: 1, delay: 0.5 }}
                                            className={`h-full bg-gradient-to-r ${config.gradient}`}
                                        />
                                    </div>
                                </div>

                                {/* Action Button */}
                                <button className={`w-full py-2.5 rounded-xl border ${config.border} ${config.bg} ${config.color} font-bold text-sm flex items-center justify-center gap-2 group-hover:bg-gradient-to-r group-hover:${config.gradient} group-hover:text-white transition-all duration-300`}>
                                    <span>Continue Journey</span>
                                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </button>
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
};

export default SkillTree;
