import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { Sparkles, Zap, Target, ShieldCheck, Cpu, GraduationCap, HeartHandshake, Eye } from "lucide-react";

// --- Custom Hooks ---

const useMousePosition = () => {
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const updateMousePosition = (e) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
        };
        window.addEventListener("mousemove", updateMousePosition);
        return () => window.removeEventListener("mousemove", updateMousePosition);
    }, []);

    return mousePosition;
};

// --- Sub-components ---

const CognitiveSymbol = () => (
    <div className="relative w-48 h-48">
        {/* Outer Glow */}
        <motion.div
            className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-400/40 via-purple-500/40 to-blue-500/40 blur-[40px]"
            animate={{ scale: [1, 1.2, 1], opacity: [0.4, 0.7, 0.4] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* Main Symbol Container */}
        <div className="relative w-full h-full rounded-full bg-gradient-to-br from-cyan-400 via-purple-500 to-blue-600 p-1 shadow-[0_0_80px_rgba(6,214,160,0.6)]">
            <div className="w-full h-full rounded-full bg-black/40 backdrop-blur-xl flex items-center justify-center overflow-hidden border-2 border-white/20">

                {/* SVG Hybrid Symbol */}
                <svg width="140" height="140" viewBox="0 0 140 140" className="relative z-10">
                    {/* Neural Network Base */}
                    <g opacity="0.8">
                        {/* Central Node */}
                        <motion.circle
                            cx="70" cy="70" r="12"
                            fill="url(#neuralGradient)"
                            animate={{ scale: [1, 1.1, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />

                        {/* Surrounding Nodes */}
                        {[0, 60, 120, 180, 240, 300].map((angle, i) => {
                            const x = 70 + 35 * Math.cos((angle * Math.PI) / 180);
                            const y = 70 + 35 * Math.sin((angle * Math.PI) / 180);
                            return (
                                <motion.g key={i}>
                                    <line
                                        x1="70" y1="70" x2={x} y2={y}
                                        stroke="url(#lineGradient)"
                                        strokeWidth="2"
                                        opacity="0.6"
                                    />
                                    <motion.circle
                                        cx={x} cy={y} r="6"
                                        fill="url(#nodeGradient)"
                                        animate={{ scale: [1, 1.2, 1] }}
                                        transition={{ duration: 2, repeat: Infinity, delay: i * 0.2 }}
                                    />
                                </motion.g>
                            );
                        })}
                    </g>

                    {/* Graduation Cap Overlay */}
                    <g transform="translate(70, 50)">
                        <motion.path
                            d="M -20,-10 L 0,-20 L 20,-10 L 20,0 L -20,0 Z"
                            fill="url(#capGradient)"
                            stroke="#06D6A0"
                            strokeWidth="2"
                            animate={{ y: [0, -3, 0] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />
                        <rect x="-2" y="0" width="4" height="15" fill="#A855F7" opacity="0.8" />
                    </g>

                    {/* Infinity Loop */}
                    <motion.path
                        d="M 40,90 Q 50,80 60,90 T 80,90 Q 90,80 100,90 T 80,90 Q 70,100 60,90 T 40,90"
                        fill="none"
                        stroke="url(#infinityGradient)"
                        strokeWidth="3"
                        strokeLinecap="round"
                        animate={{ pathLength: [0, 1], opacity: [0.3, 0.8, 0.3] }}
                        transition={{ duration: 3, repeat: Infinity }}
                    />

                    {/* Spark of Discovery */}
                    <motion.g transform="translate(100, 30)">
                        <motion.path
                            d="M 0,-8 L 2,0 L 8,2 L 2,4 L 0,12 L -2,4 L -8,2 L -2,0 Z"
                            fill="#FCD34D"
                            animate={{ scale: [1, 1.3, 1], rotate: [0, 180, 360] }}
                            transition={{ duration: 4, repeat: Infinity }}
                        />
                    </motion.g>

                    {/* Gradients */}
                    <defs>
                        <linearGradient id="neuralGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#06D6A0" />
                            <stop offset="100%" stopColor="#3B82F6" />
                        </linearGradient>
                        <linearGradient id="nodeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#A855F7" />
                            <stop offset="100%" stopColor="#3B82F6" />
                        </linearGradient>
                        <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#06D6A0" stopOpacity="0.3" />
                            <stop offset="100%" stopColor="#A855F7" stopOpacity="0.6" />
                        </linearGradient>
                        <linearGradient id="capGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#06D6A0" />
                            <stop offset="100%" stopColor="#A855F7" />
                        </linearGradient>
                        <linearGradient id="infinityGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#3B82F6" />
                            <stop offset="50%" stopColor="#A855F7" />
                            <stop offset="100%" stopColor="#06D6A0" />
                        </linearGradient>
                    </defs>
                </svg>

                {/* Internal Energy Swirl */}
                <motion.div
                    className="absolute inset-0 bg-gradient-to-tr from-transparent via-cyan-500/20 to-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                />
            </div>
        </div>
    </div>
);

const NeonRing = ({ size, duration, delay, reverse = false, gradient, opacity = 0.6 }) => (
    <motion.div
        className="absolute top-1/2 left-1/2 rounded-full border-2"
        style={{
            width: size,
            height: size,
            x: "-50%",
            y: "-50%",
            borderImage: `linear-gradient(${gradient}) 1`,
            opacity
        }}
        animate={{ rotate: reverse ? -360 : 360 }}
        transition={{ duration, repeat: Infinity, ease: "linear", delay: -delay }}
    />
);

const StaticNode = ({ icon: Icon, x, y, color, label }) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <motion.div
            className="absolute z-40 cursor-pointer group"
            style={{ left: x, top: y, x: "-50%", y: "-50%" }}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, type: "spring", bounce: 0.4 }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
        >
            {/* Node Container */}
            <motion.div
                className={`relative w-32 h-32 ${color} backdrop-blur-xl rounded-3xl border-2 border-white/70 flex flex-col items-center justify-center shadow-[0_0_70px_rgba(6,214,160,0.9)]`}
                animate={{
                    scale: isHovered ? 1.1 : 1,
                    boxShadow: isHovered
                        ? "0 0 100px rgba(6,214,160,1)"
                        : "0 0 70px rgba(6,214,160,0.9)",
                    rotateY: isHovered ? 10 : 0
                }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
                <Icon className="w-16 h-16 text-white drop-shadow-[0_0_25px_rgba(255,255,255,1)]" strokeWidth={2.5} />

                {/* Pulsing Glow */}
                <motion.div
                    className={`absolute inset-0 rounded-3xl ${color} blur-2xl`}
                    animate={{
                        opacity: isHovered ? [0.7, 1, 0.7] : [0.5, 0.8, 0.5]
                    }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                />

                {/* Floating Particles around node */}
                {[...Array(3)].map((_, i) => (
                    <motion.div
                        key={i}
                        className="absolute w-2 h-2 rounded-full bg-white/80"
                        animate={{
                            x: [0, 20 * Math.cos((i * 120) * Math.PI / 180), 0],
                            y: [0, 20 * Math.sin((i * 120) * Math.PI / 180), 0],
                            opacity: [0, 1, 0]
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            delay: i * 0.4,
                            ease: "easeInOut"
                        }}
                    />
                ))}
            </motion.div>

            {/* Label */}
            <div className="absolute top-full mt-6 left-1/2 -translate-x-1/2 whitespace-nowrap pointer-events-none">
                <motion.div
                    className="px-5 py-2.5 bg-black/95 backdrop-blur-md border-2 border-cyan-400/60 rounded-xl text-base font-bold text-white shadow-[0_0_30px_rgba(6,214,160,0.5)]"
                    animate={{
                        borderColor: isHovered ? "rgba(6,214,160,1)" : "rgba(6,214,160,0.6)",
                        boxShadow: isHovered
                            ? "0 0 40px rgba(6,214,160,0.7)"
                            : "0 0 30px rgba(6,214,160,0.5)",
                        scale: isHovered ? 1.05 : 1
                    }}
                >
                    {label}
                </motion.div>
            </div>
        </motion.div>
    );
};

const StatCard = ({ value, label, icon: Icon, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay }}
        className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 hover:bg-white/10 transition-colors group cursor-pointer"
    >
        <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform border border-white/5">
                <Icon className="w-5 h-5 text-cyan-300" />
            </div>
            <span className="text-white/50 text-xs font-bold uppercase tracking-widest">{label}</span>
        </div>
        <div className="text-3xl font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-cyan-400 group-hover:to-purple-400 transition-all">{value}</div>
    </motion.div>
);

// --- Main Component ---

export function HeroSection() {
    // Calculate perfect triangle positions - responsive scaling
    // Base values for larger screens, will be scaled down via CSS transform
    const centerX = 450;
    const centerY = 450;
    const radius = 320;

    const mentorPos = {
        x: centerX + radius * Math.cos((0 - 90) * Math.PI / 180),
        y: centerY + radius * Math.sin((0 - 90) * Math.PI / 180)
    };

    const professorPos = {
        x: centerX + radius * Math.cos((120 - 90) * Math.PI / 180),
        y: centerY + radius * Math.sin((120 - 90) * Math.PI / 180)
    };

    const supervisorPos = {
        x: centerX + radius * Math.cos((240 - 90) * Math.PI / 180),
        y: centerY + radius * Math.sin((240 - 90) * Math.PI / 180)
    };

    return (
        <section className="relative z-10 w-full max-w-[1400px] mx-auto px-6 pt-24 pb-16 min-h-[90vh] flex items-center overflow-visible">

            {/* Deep Space Background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1400px] h-[1400px] bg-purple-900/30 blur-[180px] rounded-full mix-blend-screen" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[900px] bg-cyan-900/30 blur-[120px] rounded-full mix-blend-screen" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center w-full relative z-10">

                {/* --- Left Content (5 Columns) --- */}
                <motion.div
                    className="lg:col-span-5 flex flex-col justify-center relative z-40"
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    {/* Badge */}
                    <motion.div
                        className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/50 rounded-full mb-8 w-fit backdrop-blur-md shadow-[0_0_20px_rgba(6,214,160,0.3)]"
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <Cpu className="w-4 h-4 text-cyan-400" />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-purple-300 text-sm font-bold tracking-wide uppercase">
                            Your 24/7 Study Companion
                        </span>
                    </motion.div>

                    {/* Headline */}
                    <h1 className="text-5xl lg:text-7xl font-bold text-white mb-8 leading-[1.1] tracking-tight drop-shadow-2xl">
                        Learn Smarter, <br />
                        <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-blue-500 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(6,214,160,0.5)]">
                            Not Harder
                        </span>
                    </h1>

                    {/* Subtext */}
                    <p className="text-lg text-white/80 mb-6 leading-relaxed max-w-xl">
                        Your personal AI tutor that explains concepts like a friend, verifies answers like a professor, and adapts to your learning style.
                    </p>
                    
                    <p className="text-base text-white/70 mb-12 leading-relaxed max-w-xl">
                        🤝 AI Mentor explains intuitively • 🎓 AI Professor verifies academically • 
                        🏏 Hinglish support • ✨ Free to start
                    </p>

                    {/* CTAs */}
                    <div className="flex flex-wrap gap-5 mb-12">
                        <a href="/register">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-8 py-4 bg-gradient-to-r from-cyan-600 to-purple-600 text-white font-bold rounded-xl shadow-[0_0_40px_rgba(6,214,160,0.4)] hover:shadow-[0_0_60px_rgba(168,85,247,0.6)] transition-all flex items-center gap-3 border border-white/20 text-lg"
                            >
                                Start Learning Free
                                <Zap className="w-5 h-5 fill-white" />
                            </motion.button>
                        </a>
                    </div>
                    
                    {/* Trust Signals */}
                    <div className="flex flex-wrap items-center gap-6 text-sm text-white/70 mb-16">
                        <div className="flex items-center gap-2">
                            <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                                <ShieldCheck className="w-3 h-3 text-white" />
                            </div>
                            <span>100% Free to Start</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                                <ShieldCheck className="w-3 h-3 text-white" />
                            </div>
                            <span>No Credit Card Required</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                                <ShieldCheck className="w-3 h-3 text-white" />
                            </div>
                            <span>Cancel Anytime</span>
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-5 w-full border-t border-white/10 pt-10">
                        <StatCard value="10K+" label="Active Learners" icon={GraduationCap} delay={0.4} />
                        <StatCard value="4.8/5" label="Student Rating" icon={Target} delay={0.5} />
                        <StatCard value="All Exams" label="JEE • NEET • UPSC & More" icon={Sparkles} delay={0.6} />
                    </div>
                </motion.div>

                {/* --- Right Content (7 Columns) - Premium Cognitive Engine --- */}
                <motion.div
                    id="orbit-container"
                    className="lg:col-span-7 relative h-[600px] lg:h-[800px] xl:h-[900px] flex items-center justify-center perspective-1000 scale-[0.6] sm:scale-[0.7] lg:scale-[0.85] xl:scale-100 origin-center"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 1.2, ease: "easeOut" }}
                >
                    {/* Layered Neon Rings */}
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <NeonRing size={300} duration={20} gradient="90deg, #06D6A0, #A855F7" opacity={0.8} />
                        <NeonRing size={340} duration={25} reverse gradient="90deg, #A855F7, #3B82F6" opacity={0.6} />
                        <NeonRing size={700} duration={40} gradient="90deg, #3B82F6, #06D6A0" opacity={0.4} />
                        <NeonRing size={750} duration={50} reverse gradient="90deg, #06D6A0, #A855F7" opacity={0.3} />
                    </div>

                    {/* Animated Connection Lines & Energy Flow */}
                    <svg className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none" width="900" height="900" style={{ zIndex: 15 }}>
                        {/* Triangle Connection Lines with Gradient */}
                        <motion.line
                            x1={mentorPos.x} y1={mentorPos.y}
                            x2={professorPos.x} y2={professorPos.y}
                            stroke="url(#energyGradient1)"
                            strokeWidth="3"
                            opacity="0.7"
                            animate={{ strokeDashoffset: [0, -40] }}
                            strokeDasharray="10 10"
                            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                        />

                        <motion.line
                            x1={professorPos.x} y1={professorPos.y}
                            x2={supervisorPos.x} y2={supervisorPos.y}
                            stroke="url(#energyGradient2)"
                            strokeWidth="3"
                            opacity="0.7"
                            animate={{ strokeDashoffset: [0, -40] }}
                            strokeDasharray="10 10"
                            transition={{ duration: 3, repeat: Infinity, ease: "linear", delay: 1 }}
                        />

                        <motion.line
                            x1={supervisorPos.x} y1={supervisorPos.y}
                            x2={mentorPos.x} y2={mentorPos.y}
                            stroke="url(#energyGradient3)"
                            strokeWidth="3"
                            opacity="0.7"
                            animate={{ strokeDashoffset: [0, -40] }}
                            strokeDasharray="10 10"
                            transition={{ duration: 3, repeat: Infinity, ease: "linear", delay: 2 }}
                        />

                        {/* Energy Orbs flowing through connections */}
                        {[0, 1, 2].map((i) => (
                            <motion.circle
                                key={`orb-${i}`}
                                r="6"
                                fill={i === 0 ? "#A855F7" : i === 1 ? "#06D6A0" : "#F59E0B"}
                                filter="url(#glow)"
                                animate={{
                                    cx: i === 0
                                        ? [mentorPos.x, professorPos.x, mentorPos.x]
                                        : i === 1
                                            ? [professorPos.x, supervisorPos.x, professorPos.x]
                                            : [supervisorPos.x, mentorPos.x, supervisorPos.x],
                                    cy: i === 0
                                        ? [mentorPos.y, professorPos.y, mentorPos.y]
                                        : i === 1
                                            ? [professorPos.y, supervisorPos.y, professorPos.y]
                                            : [supervisorPos.y, mentorPos.y, supervisorPos.y],
                                    opacity: [0, 1, 1, 1, 0]
                                }}
                                transition={{
                                    duration: 4,
                                    repeat: Infinity,
                                    ease: "easeInOut",
                                    delay: i * 1.33
                                }}
                            />
                        ))}

                        {/* Gradients */}
                        <defs>
                            <linearGradient id="energyGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#A855F7" />
                                <stop offset="50%" stopColor="#06D6A0" />
                                <stop offset="100%" stopColor="#A855F7" />
                            </linearGradient>
                            <linearGradient id="energyGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#06D6A0" />
                                <stop offset="50%" stopColor="#F59E0B" />
                                <stop offset="100%" stopColor="#06D6A0" />
                            </linearGradient>
                            <linearGradient id="energyGradient3" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#F59E0B" />
                                <stop offset="50%" stopColor="#A855F7" />
                                <stop offset="100%" stopColor="#F59E0B" />
                            </linearGradient>
                            <filter id="glow">
                                <feGaussianBlur stdDeviation="4" result="coloredBlur" />
                                <feMerge>
                                    <feMergeNode in="coloredBlur" />
                                    <feMergeNode in="SourceGraphic" />
                                </feMerge>
                            </filter>
                        </defs>
                    </svg>

                    {/* Central Cognitive Symbol */}
                    <motion.div
                        className="relative z-20"
                        initial={{ opacity: 0, scale: 0, rotate: -180 }}
                        animate={{ opacity: 1, scale: 1, rotate: 0 }}
                        transition={{ duration: 1.5, type: "spring", bounce: 0.3 }}
                    >
                        <CognitiveSymbol />
                    </motion.div>

                    {/* Static Triangle Nodes - NO ROTATION */}
                    <StaticNode
                        icon={HeartHandshake}
                        label="AI Mentor"
                        x={mentorPos.x}
                        y={mentorPos.y}
                        color="bg-gradient-to-br from-purple-500/50 to-pink-500/50"
                    />

                    <StaticNode
                        icon={GraduationCap}
                        label="AI Professor"
                        x={professorPos.x}
                        y={professorPos.y}
                        color="bg-gradient-to-br from-cyan-500/50 to-teal-500/50"
                    />

                    <StaticNode
                        icon={Eye}
                        label="AI Supervisor"
                        x={supervisorPos.x}
                        y={supervisorPos.y}
                        color="bg-gradient-to-br from-amber-500/50 to-orange-500/50"
                    />

                </motion.div>
            </div>
        </section>
    );
}
