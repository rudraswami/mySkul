import { motion } from "framer-motion";
import { useState } from "react";
import { ImageWithFallback } from "./ImageWithFallback";
import { Play, Sparkles, Zap } from "lucide-react";

const learningModules = [
    {
        id: 1,
        title: "Cricket Physics",
        subtitle: "Projectile Motion & Forces",
        description: "Learn projectile motion, spin dynamics, and forces through the trajectory of a cricket ball - from Dhoni's helicopter shot to Bumrah's yorker",
        color: "from-orange-500 to-red-500",
        image: "https://images.unsplash.com/photo-1571260899304-425eee4c7efc?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjBjb2xsZWdlJTIwc3R1ZGVudHN8ZW58MXx8fHwxNzYzNzkxMTI1fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        topics: ["Parabolic Motion", "Magnus Effect", "Impact Forces"],
    },
    {
        id: 2,
        title: "Temple Geometry",
        subtitle: "Sacred Architecture & Mathematics",
        description: "Discover golden ratios, fractals, and advanced geometry in ancient temple designs - from Konark's precision to Brihadeeswara's symmetry",
        color: "from-purple-500 to-pink-500",
        image: "https://images.unsplash.com/photo-1656236559909-b05a20191727?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjB5b3V0aCUyMGVkdWNhdGlvbnxlbnwxfHx8fDE3NjM3OTExMjZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        topics: ["Golden Ratio", "Mandala Patterns", "3D Symmetry"],
    },
    {
        id: 3,
        title: "Molecular Dance",
        subtitle: "Chemistry Through Motion",
        description: "Visualize molecular interactions through 3D animated models inspired by classical dance mudras and their spatial relationships",
        color: "from-cyan-500 to-blue-500",
        image: "https://images.unsplash.com/photo-1716471081169-cb8528a395d3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjB0ZWVuYWdlciUyMGxhcHRvcHxlbnwxfHx8fDE3NjM3OTExMjZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        topics: ["Bonding Patterns", "Reaction Mechanisms", "Electron Flow"],
    },
    {
        id: 4,
        title: "Railway Economics",
        subtitle: "Network Theory & Optimization",
        description: "Master graph theory, optimization, and logistics through India's vast railway network - the lifeline connecting 1.4 billion people",
        color: "from-green-500 to-emerald-500",
        image: "https://images.unsplash.com/photo-1762438135827-428acc0e8941?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwc3VjY2VzcyUyMGNlbGVicmF0aW9ufGVufDF8fHx8MTc2MzcyMDA3OXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        topics: ["Network Theory", "Resource Allocation", "Dynamic Programming"],
    },
];

export function VisualLearning() {
    const [activeModule, setActiveModule] = useState(0);

    return (
        <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32">
            {/* Coming Soon Overlay */}
            <div className="absolute inset-0 z-20 bg-black/60 backdrop-blur-sm rounded-3xl flex items-center justify-center">
                <div className="text-center">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        whileInView={{ scale: 1, opacity: 1 }}
                        viewport={{ once: true }}
                        className="px-8 py-4 bg-gradient-to-r from-amber-500/30 to-orange-500/30 border-2 border-amber-400/50 rounded-2xl backdrop-blur-md"
                    >
                        <span className="text-amber-300 text-2xl font-bold uppercase tracking-wider">✨ Coming Soon</span>
                    </motion.div>
                    <p className="text-white/70 mt-4 text-lg">3D Visual Learning launching soon!</p>
                </div>
            </div>
            
            <motion.div
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                className="text-center mb-20"
            >
                <motion.div
                    className="inline-block mb-6"
                    animate={{
                        rotate: [0, 5, -5, 0],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                >
                    <div className="px-6 py-3 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 backdrop-blur-xl rounded-full border border-cyan-500/30">
                        <span className="text-cyan-300">🇮🇳 Culturally Rooted Learning</span>
                    </div>
                </motion.div>

                <h2 className="text-5xl lg:text-6xl text-white mb-6">
                    Learn Through{" "}
                    <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                        Indian Context
                    </span>
                </h2>
                <p className="text-white/70 text-xl max-w-3xl mx-auto">
                    Experience complex concepts through familiar, culturally relevant 3D visualizations
                </p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-12 items-center">
                {/* Left: Module List */}
                <div className="space-y-4">
                    {learningModules.map((module, index) => (
                        <motion.div
                            key={module.id}
                            initial={{ opacity: 0, x: -50 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            onClick={() => setActiveModule(index)}
                            className={`relative p-6 rounded-2xl border transition-all cursor-pointer ${activeModule === index
                                    ? "bg-white/10 border-white/30"
                                    : "bg-white/5 border-white/10 hover:bg-white/10"
                                }`}
                        >
                            {activeModule === index && (
                                <motion.div
                                    layoutId="activeGlow"
                                    className={`absolute inset-0 bg-gradient-to-r ${module.color} opacity-10 rounded-2xl`}
                                />
                            )}

                            <div className="flex items-start gap-4 relative z-10">
                                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center shrink-0`}>
                                    <span className="text-white font-bold">{index + 1}</span>
                                </div>
                                <div>
                                    <h3 className="text-xl text-white font-semibold mb-1">{module.title}</h3>
                                    <p className="text-white/60 text-sm">{module.subtitle}</p>
                                </div>
                                {activeModule === index && (
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="ml-auto"
                                    >
                                        <Play className="w-5 h-5 text-white fill-white" />
                                    </motion.div>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Right: Preview Area */}
                <motion.div
                    key={activeModule}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="relative aspect-video rounded-3xl overflow-hidden border border-white/20 group"
                >
                    <ImageWithFallback
                        src={learningModules[activeModule].image}
                        alt={learningModules[activeModule].title}
                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                    />

                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />

                    <div className="absolute bottom-0 left-0 right-0 p-8">
                        <motion.div
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.2 }}
                        >
                            <div className="flex flex-wrap gap-2 mb-4">
                                {learningModules[activeModule].topics.map((topic) => (
                                    <span key={topic} className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs text-white">
                                        {topic}
                                    </span>
                                ))}
                            </div>

                            <h3 className="text-3xl text-white font-bold mb-2">
                                {learningModules[activeModule].title}
                            </h3>
                            <p className="text-white/80 leading-relaxed mb-6">
                                {learningModules[activeModule].description}
                            </p>

                            <button className="px-6 py-3 bg-white text-black rounded-full font-semibold flex items-center gap-2 hover:scale-105 transition-transform">
                                <Play className="w-4 h-4 fill-black" />
                                Start Module
                            </button>
                        </motion.div>
                    </div>

                    {/* Floating 3D Elements */}
                    <motion.div
                        className="absolute top-8 right-8 w-20 h-20 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 flex items-center justify-center"
                        animate={{
                            rotate: [0, 10, -10, 0],
                            y: [0, -10, 0],
                        }}
                        transition={{
                            duration: 4,
                            repeat: Infinity,
                            ease: "easeInOut",
                        }}
                    >
                        <Sparkles className="w-10 h-10 text-white" />
                    </motion.div>
                </motion.div>
            </div>
        </section>
    );
}
