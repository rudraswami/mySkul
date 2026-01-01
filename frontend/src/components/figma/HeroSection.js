import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { Sparkles, Zap, ShieldCheck, BookOpen, MessageCircle, CheckCircle } from "lucide-react";

/**
 * HeroSection - Production-Grade with Premium Animation
 * 
 * "The Clarity Engine" - Visual metaphor for understanding
 * Multi-layered, sophisticated, responsive across all devices
 */

// --- Premium Learning Animation ---
// Represents the transformation: confusion → clarity → mastery

const ClarityEngineAnimation = () => {
    return (
        <div className="relative w-full h-full min-h-[400px] flex items-center justify-center">
            {/* === LAYER 1: Deep Background Glow === */}
            <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                    className="absolute w-[600px] h-[600px] md:w-[700px] md:h-[700px] rounded-full opacity-30"
                    style={{
                        background: 'radial-gradient(circle, rgba(139,92,246,0.4) 0%, rgba(6,182,212,0.2) 40%, transparent 70%)',
                    }}
                    animate={{ 
                        scale: [1, 1.15, 1],
                        rotate: [0, 180, 360],
                    }}
                    transition={{ 
                        scale: { duration: 8, repeat: Infinity, ease: "easeInOut" },
                        rotate: { duration: 60, repeat: Infinity, ease: "linear" }
                    }}
                />
            </div>

            {/* === LAYER 2: Flowing Light Streams === */}
            <svg className="absolute w-[500px] h-[500px] md:w-[600px] md:h-[600px]" viewBox="0 0 600 600">
                <defs>
                    <linearGradient id="stream1" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0" />
                        <stop offset="50%" stopColor="#8B5CF6" stopOpacity="0.6" />
                        <stop offset="100%" stopColor="#06B6D4" stopOpacity="0" />
                    </linearGradient>
                    <linearGradient id="stream2" x1="100%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#06B6D4" stopOpacity="0" />
                        <stop offset="50%" stopColor="#06B6D4" stopOpacity="0.5" />
                        <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
                    </linearGradient>
                    <linearGradient id="stream3" x1="0%" y1="100%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#10B981" stopOpacity="0" />
                        <stop offset="50%" stopColor="#8B5CF6" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>

                {/* Flowing curves - knowledge streams */}
                <motion.path
                    d="M 100,300 Q 200,200 300,300 T 500,300"
                    fill="none"
                    stroke="url(#stream1)"
                    strokeWidth="2"
                    filter="url(#glow)"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ 
                        pathLength: [0, 1, 1, 0],
                        opacity: [0, 0.8, 0.8, 0]
                    }}
                    transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.path
                    d="M 300,100 Q 400,200 300,300 T 300,500"
                    fill="none"
                    stroke="url(#stream2)"
                    strokeWidth="2"
                    filter="url(#glow)"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ 
                        pathLength: [0, 1, 1, 0],
                        opacity: [0, 0.7, 0.7, 0]
                    }}
                    transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 2 }}
                />
                <motion.path
                    d="M 150,450 Q 250,350 350,400 T 500,200"
                    fill="none"
                    stroke="url(#stream3)"
                    strokeWidth="2"
                    filter="url(#glow)"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ 
                        pathLength: [0, 1, 1, 0],
                        opacity: [0, 0.6, 0.6, 0]
                    }}
                    transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 4 }}
                />
            </svg>
            
            {/* === LAYER 3: Floating Geometric Elements === */}
            
            <div className="absolute inset-0 pointer-events-none">
                {/* Hexagon 1 */}
                <motion.div
                    className="absolute top-[15%] left-[20%] w-12 h-12 md:w-16 md:h-16"
                    animate={{ 
                        y: [0, -20, 0],
                        rotate: [0, 90, 0],
                        opacity: [0.3, 0.6, 0.3]
                    }}
                    transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
                >
                    <svg viewBox="0 0 100 100" className="w-full h-full">
                        <polygon 
                            points="50,5 95,27.5 95,72.5 50,95 5,72.5 5,27.5" 
                            fill="none" 
                            stroke="rgba(139,92,246,0.4)" 
                            strokeWidth="2"
                        />
                    </svg>
                </motion.div>

                {/* Circle 1 */}
                <motion.div
                    className="absolute top-[25%] right-[15%] w-8 h-8 md:w-12 md:h-12 rounded-full border-2 border-cyan-400/30"
                    animate={{ 
                        y: [0, 15, 0],
                        scale: [1, 1.2, 1],
                        opacity: [0.4, 0.7, 0.4]
                    }}
                    transition={{ duration: 6, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                />

                {/* Triangle */}
                <motion.div
                    className="absolute bottom-[20%] left-[15%] w-10 h-10 md:w-14 md:h-14"
                    animate={{ 
                        y: [0, -15, 0],
                        rotate: [0, -60, 0],
                        opacity: [0.3, 0.5, 0.3]
                    }}
                    transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 2 }}
                >
                    <svg viewBox="0 0 100 100" className="w-full h-full">
                        <polygon 
                            points="50,10 90,90 10,90" 
                            fill="none" 
                            stroke="rgba(16,185,129,0.4)" 
                            strokeWidth="2"
                        />
                    </svg>
                </motion.div>

                {/* Small dots - knowledge particles */}
                {[...Array(6)].map((_, i) => (
                    <motion.div
                        key={i}
                        className="absolute w-2 h-2 rounded-full bg-violet-400/40"
                        style={{
                            top: `${20 + Math.random() * 60}%`,
                            left: `${15 + Math.random() * 70}%`,
                        }}
                        animate={{
                            opacity: [0, 0.6, 0],
                            scale: [0.5, 1, 0.5],
                            y: [0, -30, 0],
                        }}
                        transition={{
                            duration: 4 + Math.random() * 3,
                            repeat: Infinity,
                            delay: i * 0.8,
                            ease: "easeInOut"
                        }}
                    />
                ))}
            </div>

            {/* === LAYER 4: Central Clarity Lens === */}
            <div className="relative z-10">
                {/* Outer rotating ring */}
                <motion.div
                    className="absolute -inset-8 md:-inset-12 rounded-full border border-violet-400/20"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
                >
                    {/* Ring markers */}
                    {[0, 90, 180, 270].map((angle) => (
                        <motion.div
                            key={angle}
                            className="absolute w-2 h-2 md:w-3 md:h-3 bg-violet-400/40 rounded-full"
                            style={{
                                top: '50%',
                                left: '50%',
                                transform: `rotate(${angle}deg) translateX(calc(50% + 60px)) translateY(-50%)`,
                            }}
                        />
                    ))}
                </motion.div>

                {/* Second rotating ring - opposite direction */}
                <motion.div
                    className="absolute -inset-4 md:-inset-6 rounded-full border border-cyan-400/15"
                    animate={{ rotate: -360 }}
                    transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                />

                {/* Main lens container */}
                <motion.div
                    className="relative w-32 h-32 md:w-44 md:h-44 rounded-full"
                    animate={{ 
                        boxShadow: [
                            '0 0 60px rgba(139,92,246,0.3), 0 0 120px rgba(6,182,212,0.2)',
                            '0 0 80px rgba(139,92,246,0.5), 0 0 160px rgba(6,182,212,0.3)',
                            '0 0 60px rgba(139,92,246,0.3), 0 0 120px rgba(6,182,212,0.2)',
                        ]
                    }}
                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                >
                    {/* Glass effect outer */}
                    <div className="absolute inset-0 rounded-full bg-gradient-to-br from-violet-500/20 via-transparent to-cyan-500/20 backdrop-blur-xl border border-white/10" />
                    
                    {/* Inner glow ring */}
                    <motion.div
                        className="absolute inset-3 md:inset-4 rounded-full border-2 border-violet-400/30"
                        animate={{ 
                            borderColor: [
                                'rgba(139,92,246,0.3)',
                                'rgba(6,182,212,0.4)',
                                'rgba(139,92,246,0.3)',
                            ]
                        }}
                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    />

                    {/* Core gradient */}
                    <motion.div
                        className="absolute inset-6 md:inset-8 rounded-full bg-gradient-to-br from-violet-600 via-purple-500 to-cyan-500"
                        animate={{ 
                            scale: [1, 1.05, 1],
                        }}
                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    >
                        {/* Inner shine */}
                        <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-white/20 via-transparent to-transparent" />
                        
                        {/* Center icon - abstract clarity symbol */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <motion.svg
                                className="w-12 h-12 md:w-16 md:h-16"
                                viewBox="0 0 64 64"
                                animate={{ rotate: [0, 5, -5, 0] }}
                                transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                            >
                                {/* Abstract lens/prism shape */}
                                <motion.path
                                    d="M32 8 L52 24 L52 40 L32 56 L12 40 L12 24 Z"
                                    fill="none"
                                    stroke="white"
                                    strokeWidth="2"
                                    strokeLinejoin="round"
                                    initial={{ pathLength: 0 }}
                                    animate={{ pathLength: 1 }}
                                    transition={{ duration: 2, ease: "easeOut" }}
                                />
                                {/* Inner diamond */}
                                <motion.path
                                    d="M32 18 L42 28 L42 36 L32 46 L22 36 L22 28 Z"
                                    fill="rgba(255,255,255,0.3)"
                                    stroke="white"
                                    strokeWidth="1.5"
                                    initial={{ scale: 0, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    transition={{ delay: 0.5, duration: 0.8 }}
                                />
                                {/* Center point - moment of clarity */}
                                <motion.circle
                                    cx="32"
                                    cy="32"
                                    r="4"
                                    fill="white"
                                    initial={{ scale: 0 }}
                                    animate={{ 
                                        scale: [1, 1.3, 1],
                                        opacity: [0.8, 1, 0.8]
                                    }}
                                    transition={{ 
                                        scale: { duration: 2, repeat: Infinity, ease: "easeInOut" },
                                        opacity: { duration: 2, repeat: Infinity, ease: "easeInOut" }
                                    }}
                                />
                            </motion.svg>
                        </div>
                    </motion.div>
                </motion.div>

                {/* Pulse ripples */}
                <motion.div
                    className="absolute inset-0 rounded-full border border-violet-400/30"
                    animate={{
                        scale: [1, 2],
                        opacity: [0.5, 0],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeOut",
                    }}
                />
                <motion.div
                    className="absolute inset-0 rounded-full border border-cyan-400/20"
                    animate={{
                        scale: [1, 2.5],
                        opacity: [0.4, 0],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeOut",
                        delay: 1.5
                    }}
                />
            </div>

            {/* === LAYER 5: Floating State Labels === */}
            <motion.div
                className="absolute top-[12%] right-[10%] md:top-[18%] md:right-[18%]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1, duration: 0.8 }}
            >
                <motion.div
                    className="px-4 py-2 bg-violet-500/10 backdrop-blur-md rounded-xl border border-violet-400/20 shadow-lg shadow-violet-500/10"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                >
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
                        <span className="text-violet-200 text-sm font-medium">Concepts clicking</span>
                    </div>
                </motion.div>
            </motion.div>

            <motion.div
                className="absolute bottom-[15%] left-[8%] md:bottom-[20%] md:left-[15%]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.5, duration: 0.8 }}
            >
                <motion.div
                    className="px-4 py-2 bg-cyan-500/10 backdrop-blur-md rounded-xl border border-cyan-400/20 shadow-lg shadow-cyan-500/10"
                    animate={{ y: [0, 8, 0] }}
                    transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                >
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                        <span className="text-cyan-200 text-sm font-medium">Understanding clear</span>
                    </div>
                </motion.div>
            </motion.div>

            <motion.div
                className="absolute top-[55%] right-[5%] md:top-[50%] md:right-[10%]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 2, duration: 0.8 }}
            >
                <motion.div
                    className="px-4 py-2 bg-emerald-500/10 backdrop-blur-md rounded-xl border border-emerald-400/20 shadow-lg shadow-emerald-500/10"
                    animate={{ y: [0, -6, 0] }}
                    transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut", delay: 2 }}
                >
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="text-emerald-200 text-sm font-medium">Answers verified</span>
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
};

// Outcome-focused feature card
const OutcomeCard = ({ icon: Icon, title, description, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay }}
        className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-4 md:p-5 hover:bg-white/10 transition-colors group cursor-pointer"
    >
        <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 md:w-10 md:h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform border border-white/5">
                <Icon className="w-4 h-4 md:w-5 md:h-5 text-cyan-300" />
            </div>
            <span className="text-white font-semibold text-sm md:text-base">{title}</span>
        </div>
        <p className="text-white/60 text-xs md:text-sm leading-relaxed">{description}</p>
    </motion.div>
);

// --- Main Component ---

export function HeroSection() {
    return (
        <section className="relative z-10 w-full max-w-[1400px] mx-auto px-4 sm:px-6 pt-16 sm:pt-20 md:pt-24 pb-12 md:pb-16 min-h-[90vh] flex items-center overflow-hidden">

            {/* Deep Space Background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] md:w-[1400px] h-[800px] md:h-[1400px] bg-purple-900/20 blur-[150px] md:blur-[180px] rounded-full mix-blend-screen" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] md:w-[900px] h-[500px] md:h-[900px] bg-cyan-900/20 blur-[100px] md:blur-[120px] rounded-full mix-blend-screen" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 md:gap-12 lg:gap-16 items-center w-full relative z-10">

                {/* --- Left Content (6 Columns on lg+) --- */}
                <motion.div
                    className="lg:col-span-5 xl:col-span-5 flex flex-col justify-center relative z-40 text-center lg:text-left"
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    {/* Badge */}
                    <motion.div
                        className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/50 rounded-full mb-6 md:mb-8 w-fit mx-auto lg:mx-0 backdrop-blur-md shadow-[0_0_20px_rgba(6,214,160,0.3)]"
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <Sparkles className="w-4 h-4 text-cyan-400" />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-purple-300 text-xs sm:text-sm font-bold tracking-wide">
                            Your 24/7 STUDY COMPANION
                        </span>
                    </motion.div>

                    {/* Headline */}
                    <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-white mb-6 md:mb-8 leading-[1.1] tracking-tight drop-shadow-2xl">
                        Learn Smarter, <br />
                        <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-blue-500 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(6,214,160,0.5)]">
                            Not Harder
                        </span>
                    </h1>

                    {/* Subtext */}
                    <p className="text-base sm:text-lg text-white/80 mb-6 md:mb-8 leading-relaxed max-w-xl mx-auto lg:mx-0">
                        Your personal AI tutor that explains concepts like a friend, checks your understanding, and adapts to how you learn best.
                    </p>

                    {/* CTAs */}
                    <div className="flex flex-wrap gap-4 md:gap-5 mb-8 md:mb-10 justify-center lg:justify-start">
                        <a href="/register">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-cyan-600 to-purple-600 text-white font-bold rounded-xl shadow-[0_0_40px_rgba(6,214,160,0.4)] hover:shadow-[0_0_60px_rgba(168,85,247,0.6)] transition-all flex items-center gap-2 sm:gap-3 border border-white/20 text-base sm:text-lg"
                            >
                                Start Learning Free
                                <Zap className="w-4 h-4 sm:w-5 sm:h-5 fill-white" />
                            </motion.button>
                        </a>
                    </div>
                    
                    {/* Trust Signals */}
                    <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4 md:gap-6 text-xs sm:text-sm text-white/70 mb-10 md:mb-12">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 md:w-5 md:h-5 bg-green-500 rounded-full flex items-center justify-center">
                                <ShieldCheck className="w-2.5 h-2.5 md:w-3 md:h-3 text-white" />
                            </div>
                            <span>Free to start</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 md:w-5 md:h-5 bg-green-500 rounded-full flex items-center justify-center">
                                <ShieldCheck className="w-2.5 h-2.5 md:w-3 md:h-3 text-white" />
                            </div>
                            <span>No credit card</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 md:w-5 md:h-5 bg-green-500 rounded-full flex items-center justify-center">
                                <ShieldCheck className="w-2.5 h-2.5 md:w-3 md:h-3 text-white" />
                            </div>
                            <span>Works for all exams</span>
                        </div>
                    </div>

                    {/* Outcome Cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4 w-full border-t border-white/10 pt-8 md:pt-10">
                        <OutcomeCard 
                            icon={MessageCircle} 
                            title="Explains clearly" 
                            description="Breaks down hard topics until they click"
                            delay={0.4} 
                        />
                        <OutcomeCard 
                            icon={CheckCircle} 
                            title="Catches mistakes" 
                            description="Spots where you went wrong and why"
                            delay={0.5} 
                        />
                        <OutcomeCard 
                            icon={BookOpen} 
                            title="Adapts to you" 
                            description="Learns your pace and adjusts"
                            delay={0.6} 
                        />
                    </div>
                </motion.div>

                {/* --- Right Content (7 Columns on lg+) - Premium Animation --- */}
                <motion.div
                    className="lg:col-span-7 xl:col-span-7 relative h-[400px] sm:h-[450px] md:h-[500px] lg:h-[600px] xl:h-[650px] flex items-center justify-center order-first lg:order-last"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1.2, ease: "easeOut" }}
                >
                    <ClarityEngineAnimation />
                </motion.div>
            </div>
        </section>
    );
}
