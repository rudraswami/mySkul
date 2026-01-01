import { motion } from "framer-motion";
import { Heart, Lightbulb, Calculator, Atom, Sparkles } from "lucide-react";
import { useState } from "react";

export function DualLayerSystem() {
    const [hoveredLayer, setHoveredLayer] = useState(null);

    return (
        <section id="how-it-works" className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
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
                        y: [0, -8, 0],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                >
                    <div className="px-6 py-3 bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-xl rounded-full border border-purple-500/30">
                        <span className="text-purple-300">🧠 Dual Intelligence System</span>
                    </div>
                </motion.div>

                <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl text-white mb-4 sm:mb-6">
                    The Power of{" "}
                    <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Dual-Layer AI
                    </span>
                </h2>
                <p className="text-white/70 text-base sm:text-lg lg:text-xl max-w-3xl mx-auto px-2 sm:px-0">
                    Two specialized AI systems working in perfect harmony to deliver the most comprehensive learning experience
                </p>
            </motion.div>

            <div className="relative">
                {/* Connection Line with animated pulse */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1 h-32 overflow-hidden hidden lg:block">
                    <motion.div
                        className="w-full h-full bg-gradient-to-b from-purple-500 to-pink-500"
                        animate={{
                            opacity: [0.5, 1, 0.5],
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                        }}
                    />
                    <motion.div
                        className="absolute top-0 left-0 right-0 h-8 bg-gradient-to-b from-white to-transparent"
                        animate={{
                            y: ["0%", "400%"],
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "linear",
                        }}
                    />
                </div>

                <div className="grid lg:grid-cols-2 gap-8 lg:gap-16">
                    {/* Mentor Layer */}
                    <motion.div
                        initial={{ opacity: 0, x: -50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        onHoverStart={() => setHoveredLayer("mentor")}
                        onHoverEnd={() => setHoveredLayer(null)}
                        className="relative group"
                    >
                        <motion.div
                            className="relative bg-gradient-to-br from-purple-500/10 to-purple-600/5 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-purple-500/30 p-5 sm:p-6 lg:p-8 overflow-hidden"
                            animate={{
                                scale: hoveredLayer === "mentor" ? 1.02 : 1,
                                borderColor: hoveredLayer === "mentor" ? "rgba(168, 85, 247, 0.5)" : "rgba(168, 85, 247, 0.3)",
                            }}
                            transition={{ duration: 0.3 }}
                        >
                            {/* 3D Floating Icon */}
                            <motion.div
                                className="absolute -top-6 -right-6 w-32 h-32 bg-purple-500/20 rounded-3xl flex items-center justify-center"
                                animate={{
                                    rotateY: hoveredLayer === "mentor" ? 360 : 0,
                                    rotateX: [0, 10, 0],
                                }}
                                transition={{
                                    rotateY: { duration: 1 },
                                    rotateX: { duration: 4, repeat: Infinity, ease: "easeInOut" },
                                }}
                                style={{ transformStyle: "preserve-3d" }}
                            >
                                <Heart className="w-16 h-16 text-purple-400" />
                            </motion.div>

                            <div className="relative z-10">
                                <motion.div
                                    className="w-16 h-16 bg-purple-500/20 rounded-2xl flex items-center justify-center mb-6 border border-purple-500/30"
                                    whileHover={{ rotate: 360, scale: 1.1 }}
                                    transition={{ duration: 0.6 }}
                                >
                                    <Heart className="w-8 h-8 text-purple-400" />
                                </motion.div>

                                <h3 className="text-2xl sm:text-3xl text-white mb-3 sm:mb-4">Mentor Layer</h3>
                                <p className="text-white/70 mb-4 sm:mb-6 text-base sm:text-lg leading-relaxed">
                                    Your emotional companion that understands your learning journey, provides encouragement,
                                    and guides you through conceptual understanding with empathy.
                                </p>

                                <div className="space-y-4">
                                    {[
                                        { title: "Emotional Intelligence", desc: "Adapts to your mood and motivation levels", icon: "💝" },
                                        { title: "Conceptual Clarity", desc: "Explains \"why\" behind every concept", icon: "💡" },
                                        { title: "Personalized Guidance", desc: "Tailored learning paths for your goals", icon: "🎯" },
                                    ].map((item, index) => (
                                        <motion.div
                                            key={item.title}
                                            initial={{ opacity: 0, x: -20 }}
                                            whileInView={{ opacity: 1, x: 0 }}
                                            viewport={{ once: true }}
                                            transition={{ delay: index * 0.1 }}
                                            whileHover={{ x: 10 }}
                                            className="flex items-start gap-3 p-3 rounded-xl bg-purple-500/5 hover:bg-purple-500/10 transition-colors"
                                        >
                                            <motion.div
                                                className="text-2xl"
                                                animate={{
                                                    rotate: [0, 10, -10, 0],
                                                }}
                                                transition={{
                                                    duration: 3,
                                                    repeat: Infinity,
                                                    delay: index * 0.3,
                                                }}
                                            >
                                                {item.icon}
                                            </motion.div>
                                            <div>
                                                <div className="text-white">{item.title}</div>
                                                <div className="text-white/60 text-sm">{item.desc}</div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>

                            {/* Animated Background Elements */}
                            <motion.div
                                className="absolute bottom-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl"
                                animate={{
                                    scale: [1, 1.2, 1],
                                    opacity: [0.3, 0.5, 0.3],
                                }}
                                transition={{
                                    duration: 5,
                                    repeat: Infinity,
                                    ease: "easeInOut",
                                }}
                            />

                            {/* Particles */}
                            {[...Array(5)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    className="absolute w-1 h-1 bg-purple-400 rounded-full"
                                    style={{
                                        left: `${20 + i * 15}%`,
                                        top: `${30 + i * 10}%`,
                                    }}
                                    animate={{
                                        y: [0, -20, 0],
                                        opacity: [0, 1, 0],
                                    }}
                                    transition={{
                                        duration: 3,
                                        repeat: Infinity,
                                        delay: i * 0.4,
                                    }}
                                />
                            ))}
                        </motion.div>
                    </motion.div>

                    {/* Professor Layer */}
                    <motion.div
                        initial={{ opacity: 0, x: 50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        onHoverStart={() => setHoveredLayer("professor")}
                        onHoverEnd={() => setHoveredLayer(null)}
                        className="relative group"
                    >
                        <motion.div
                            className="relative bg-gradient-to-br from-pink-500/10 to-pink-600/5 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-pink-500/30 p-5 sm:p-6 lg:p-8 overflow-hidden"
                            animate={{
                                scale: hoveredLayer === "professor" ? 1.02 : 1,
                                borderColor: hoveredLayer === "professor" ? "rgba(236, 72, 153, 0.5)" : "rgba(236, 72, 153, 0.3)",
                            }}
                            transition={{ duration: 0.3 }}
                        >
                            {/* 3D Floating Icon */}
                            <motion.div
                                className="absolute -top-6 -right-6 w-32 h-32 bg-pink-500/20 rounded-3xl flex items-center justify-center"
                                animate={{
                                    rotateY: hoveredLayer === "professor" ? 360 : 0,
                                    rotateX: [0, -10, 0],
                                }}
                                transition={{
                                    rotateY: { duration: 1 },
                                    rotateX: { duration: 4, repeat: Infinity, ease: "easeInOut" },
                                }}
                                style={{ transformStyle: "preserve-3d" }}
                            >
                                <Atom className="w-16 h-16 text-pink-400" />
                            </motion.div>

                            <div className="relative z-10">
                                <motion.div
                                    className="w-16 h-16 bg-pink-500/20 rounded-2xl flex items-center justify-center mb-6 border border-pink-500/30"
                                    whileHover={{ rotate: 360, scale: 1.1 }}
                                    transition={{ duration: 0.6 }}
                                >
                                    <Atom className="w-8 h-8 text-pink-400" />
                                </motion.div>

                                <h3 className="text-2xl sm:text-3xl text-white mb-3 sm:mb-4">Professor Layer</h3>
                                <p className="text-white/70 mb-4 sm:mb-6 text-base sm:text-lg leading-relaxed">
                                    Your analytical powerhouse that delivers deep reasoning, symbolic verification,
                                    and zero-hallucination solutions backed by rigorous logic.
                                </p>

                                <div className="space-y-4">
                                    {[
                                        { title: "Symbolic Reasoning", desc: "Step-by-step logical verification", icon: "🔬" },
                                        { title: "Zero Hallucination", desc: "Every answer is mathematically verified", icon: "✅" },
                                        { title: "Deep Analysis", desc: "Advanced problem-solving techniques", icon: "🧮" },
                                    ].map((item, index) => (
                                        <motion.div
                                            key={item.title}
                                            initial={{ opacity: 0, x: -20 }}
                                            whileInView={{ opacity: 1, x: 0 }}
                                            viewport={{ once: true }}
                                            transition={{ delay: index * 0.1 }}
                                            whileHover={{ x: 10 }}
                                            className="flex items-start gap-3 p-3 rounded-xl bg-pink-500/5 hover:bg-pink-500/10 transition-colors"
                                        >
                                            <motion.div
                                                className="text-2xl"
                                                animate={{
                                                    rotate: [0, -10, 10, 0],
                                                }}
                                                transition={{
                                                    duration: 3,
                                                    repeat: Infinity,
                                                    delay: index * 0.3,
                                                }}
                                            >
                                                {item.icon}
                                            </motion.div>
                                            <div>
                                                <div className="text-white">{item.title}</div>
                                                <div className="text-white/60 text-sm">{item.desc}</div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>

                            {/* Animated Background Elements */}
                            <motion.div
                                className="absolute bottom-0 right-0 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl"
                                animate={{
                                    scale: [1, 1.2, 1],
                                    opacity: [0.3, 0.5, 0.3],
                                }}
                                transition={{
                                    duration: 5,
                                    repeat: Infinity,
                                    ease: "easeInOut",
                                    delay: 0.5,
                                }}
                            />

                            {/* Particles */}
                            {[...Array(5)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    className="absolute w-1 h-1 bg-pink-400 rounded-full"
                                    style={{
                                        left: `${20 + i * 15}%`,
                                        top: `${30 + i * 10}%`,
                                    }}
                                    animate={{
                                        y: [0, -20, 0],
                                        opacity: [0, 1, 0],
                                    }}
                                    transition={{
                                        duration: 3,
                                        repeat: Infinity,
                                        delay: i * 0.4,
                                    }}
                                />
                            ))}
                        </motion.div>
                    </motion.div>
                </div>

                {/* Center Connection Badge */}
                <motion.div
                    initial={{ opacity: 0, scale: 0 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 hidden lg:block"
                >
                    <motion.div
                        className="relative w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/50"
                        animate={{
                            rotate: 360,
                        }}
                        transition={{
                            duration: 20,
                            repeat: Infinity,
                            ease: "linear",
                        }}
                    >
                        <Lightbulb className="w-12 h-12 text-white" />

                        {/* Pulsing ring */}
                        <motion.div
                            className="absolute inset-0 rounded-2xl border-2 border-white"
                            animate={{
                                scale: [1, 1.3, 1],
                                opacity: [1, 0, 1],
                            }}
                            transition={{
                                duration: 2,
                                repeat: Infinity,
                            }}
                        />

                        {/* Sparkles around */}
                        {[...Array(4)].map((_, i) => (
                            <motion.div
                                key={i}
                                className="absolute"
                                style={{
                                    top: "50%",
                                    left: "50%",
                                }}
                                animate={{
                                    rotate: i * 90,
                                    x: [0, 40, 0],
                                    y: [0, 40, 0],
                                }}
                                transition={{
                                    duration: 3,
                                    repeat: Infinity,
                                    delay: i * 0.2,
                                }}
                            >
                                <Sparkles className="w-4 h-4 text-yellow-400" />
                            </motion.div>
                        ))}
                    </motion.div>
                </motion.div>
            </div>
        </section>
    );
}
