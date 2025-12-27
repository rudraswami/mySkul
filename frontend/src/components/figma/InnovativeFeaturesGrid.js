import { motion, useMotionValue, useTransform } from "framer-motion";
import { Dna, ShieldCheck, FileText, Eye, Box, TrendingUp } from "lucide-react";
import { useState } from "react";

const features = [
    {
        icon: Dna,
        title: "Dual AI System",
        description: "AI Mentor explains like your best friend while AI Professor ensures academic accuracy. Two minds, one goal - your success.",
        details: "Our dual-layer approach combines emotional intelligence with rigorous academic verification for trustworthy, relatable learning.",
        color: "from-purple-500 to-purple-600",
        bgColor: "bg-purple-500/10",
        borderColor: "border-purple-500/30",
        iconColor: "text-purple-400",
        stats: "100% verified responses",
    },
    {
        icon: ShieldCheck,
        title: "Teach Me Back",
        description: "Explain concepts back to the AI and get instant feedback. The best way to learn is to teach - we make it possible.",
        details: "Research shows teaching others improves retention by 90%. Our AI listens to your explanations and helps you identify gaps.",
        color: "from-pink-500 to-pink-600",
        bgColor: "bg-pink-500/10",
        borderColor: "border-pink-500/30",
        iconColor: "text-pink-400",
        stats: "90% better retention",
    },
    {
        icon: FileText,
        title: "Hinglish Support",
        description: "Ask questions in Hindi, English, or mix both! Our AI understands how you naturally communicate and responds accordingly.",
        details: "No more struggling with English-only tutors. Learn in your comfortable language while building English vocabulary naturally.",
        color: "from-blue-500 to-blue-600",
        bgColor: "bg-blue-500/10",
        borderColor: "border-blue-500/30",
        iconColor: "text-blue-400",
        stats: "Hindi + English support",
    },
    {
        icon: TrendingUp,
        title: "Adaptive Learning",
        description: "AI remembers your strengths and weaknesses, adjusting difficulty and explanations to match your learning pace.",
        details: "No more one-size-fits-all education. Get personalized attention that adapts to how you learn best.",
        color: "from-cyan-500 to-cyan-600",
        bgColor: "bg-cyan-500/10",
        borderColor: "border-cyan-500/30",
        iconColor: "text-cyan-400",
        stats: "2x faster progress",
    },
    {
        icon: Eye,
        title: "Visual Explanations",
        description: "Complex diagrams, step-by-step solutions, and concept maps generated instantly to help you visualize and understand.",
        details: "From chemical structures to physics diagrams - see concepts come alive with AI-generated visual explanations.",
        color: "from-violet-500 to-violet-600",
        bgColor: "bg-violet-500/10",
        borderColor: "border-violet-500/30",
        iconColor: "text-violet-400",
        comingSoon: true,
        stats: "Coming Soon",
    },
    {
        icon: Box,
        title: "Mock Tests",
        description: "Generate unlimited practice tests tailored to your exam - JEE, NEET, UPSC, Banking, SSC and more.",
        details: "AI-powered test generation with detailed solutions and performance analytics to track your preparation.",
        color: "from-fuchsia-500 to-fuchsia-600",
        bgColor: "bg-fuchsia-500/10",
        borderColor: "border-fuchsia-500/30",
        iconColor: "text-fuchsia-400",
        comingSoon: true,
        stats: "Coming Soon",
    },
];

function FlipCard({ feature, index }) {
    const [isFlipped, setIsFlipped] = useState(false);
    const Icon = feature.icon;

    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="h-[400px] cursor-pointer"
            style={{ perspective: "1000px" }}
            onHoverStart={() => setIsFlipped(true)}
            onHoverEnd={() => setIsFlipped(false)}
        >
            <motion.div
                className="relative w-full h-full"
                animate={{ rotateY: isFlipped ? 180 : 0 }}
                transition={{ duration: 0.6, type: "spring" }}
                style={{ transformStyle: "preserve-3d" }}
            >
                {/* Front Side */}
                <div
                    className={`absolute inset-0 ${feature.bgColor} backdrop-blur-xl rounded-3xl border ${feature.borderColor} p-8 overflow-hidden`}
                    style={{ backfaceVisibility: "hidden" }}
                >
                    {/* Coming Soon Badge */}
                    {feature.comingSoon && (
                        <div className="absolute top-4 right-4 px-3 py-1 bg-amber-500/20 border border-amber-500/50 rounded-full">
                            <span className="text-amber-300 text-xs font-bold uppercase tracking-wider">Coming Soon</span>
                        </div>
                    )}
                    
                    {/* Animated Icon */}
                    <motion.div
                        className={`w-20 h-20 ${feature.bgColor} rounded-2xl flex items-center justify-center mb-6 border ${feature.borderColor} relative`}
                        animate={{
                            rotateZ: [0, 5, -5, 0],
                        }}
                        transition={{
                            duration: 4,
                            repeat: Infinity,
                            ease: "easeInOut",
                        }}
                    >
                        <Icon className={`w-10 h-10 ${feature.iconColor}`} />

                        {/* Pulsing glow */}
                        <motion.div
                            className={`absolute inset-0 bg-gradient-to-br ${feature.color} rounded-2xl opacity-0 blur-xl`}
                            animate={{
                                opacity: [0, 0.4, 0],
                                scale: [1, 1.2, 1],
                            }}
                            transition={{
                                duration: 2,
                                repeat: Infinity,
                                ease: "easeInOut",
                            }}
                        />
                    </motion.div>

                    <h3 className="text-2xl text-white mb-4">{feature.title}</h3>
                    <p className="text-white/70 leading-relaxed mb-6">{feature.description}</p>

                    {/* Hover hint */}
                    <div className="absolute bottom-8 left-8 right-8">
                        <div className={`flex items-center justify-between px-4 py-2 bg-gradient-to-r ${feature.color} rounded-full`}>
                            <span className="text-white text-sm">Hover to learn more</span>
                            <motion.div
                                animate={{ x: [0, 5, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            >
                                →
                            </motion.div>
                        </div>
                    </div>

                    {/* Floating particles */}
                    {[...Array(3)].map((_, i) => (
                        <motion.div
                            key={i}
                            className={`absolute w-1 h-1 bg-gradient-to-br ${feature.color} rounded-full`}
                            style={{
                                left: `${20 + i * 30}%`,
                                top: `${20 + i * 20}%`,
                            }}
                            animate={{
                                y: [0, -20, 0],
                                opacity: [0, 1, 0],
                            }}
                            transition={{
                                duration: 3,
                                repeat: Infinity,
                                delay: i * 0.5,
                            }}
                        />
                    ))}
                </div>

                {/* Back Side */}
                <div
                    className={`absolute inset-0 bg-gradient-to-br ${feature.color} backdrop-blur-xl rounded-3xl border ${feature.borderColor} p-8 overflow-hidden`}
                    style={{
                        backfaceVisibility: "hidden",
                        transform: "rotateY(180deg)",
                    }}
                >
                    <div className="h-full flex flex-col justify-between">
                        <div>
                            <div className={`w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mb-6`}>
                                <Icon className="w-8 h-8 text-white" />
                            </div>

                            <h3 className="text-2xl text-white mb-4">{feature.title}</h3>
                            <p className="text-white/90 leading-relaxed mb-6">{feature.details}</p>
                        </div>

                        <div>
                            <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-4 border border-white/30">
                                <div className="text-white/80 text-sm mb-1">Performance</div>
                                <div className="text-white text-xl">{feature.stats}</div>
                            </div>
                        </div>
                    </div>

                    {/* Animated background pattern */}
                    <motion.div
                        className="absolute inset-0 opacity-10"
                        animate={{
                            backgroundPosition: ["0% 0%", "100% 100%"],
                        }}
                        transition={{
                            duration: 20,
                            repeat: Infinity,
                            ease: "linear",
                        }}
                        style={{
                            backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)",
                            backgroundSize: "30px 30px",
                        }}
                    />
                </div>
            </motion.div>
        </motion.div>
    );
}

export function InnovativeFeaturesGrid() {
    return (
        <section id="features" className="relative z-10 max-w-7xl mx-auto px-6 py-16">
            <motion.div
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                className="text-center mb-12"
            >
                <motion.div
                    className="inline-block mb-6"
                    animate={{
                        y: [0, -10, 0],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                >
                    <div className="px-6 py-3 bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-xl rounded-full border border-purple-500/30">
                        <span className="text-purple-300">✨ Revolutionary Features</span>
                    </div>
                </motion.div>

                <h2 className="text-5xl lg:text-6xl text-white mb-6">
                    Experience Learning{" "}
                    <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Reimagined
                    </span>
                </h2>
                <p className="text-white/70 text-xl max-w-3xl mx-auto">
                    Hover over each card to discover how our cutting-edge AI features transform your learning journey
                </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {features.map((feature, index) => (
                    <FlipCard key={feature.title} feature={feature} index={index} />
                ))}
            </div>

            {/* Bottom CTA */}
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.5 }}
                className="mt-16 text-center"
            >
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-10 py-5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full hover:shadow-2xl hover:shadow-purple-500/50 transition-all text-lg"
                >
                    Explore All Features →
                </motion.button>
            </motion.div>
        </section>
    );
}
