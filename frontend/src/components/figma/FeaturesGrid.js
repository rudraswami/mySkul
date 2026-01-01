import { motion } from "framer-motion";
import { Dna, ShieldCheck, FileText, Eye, Box, TrendingUp } from "lucide-react";

const features = [
    {
        icon: Dna,
        title: "Error Genome™",
        description: "Detects microscopic errors at the root level, just like a top-performing student would identify conceptual gaps.",
        color: "from-purple-500 to-purple-600",
        bgColor: "bg-purple-500/10",
        borderColor: "border-purple-500/30",
        iconColor: "text-purple-400",
    },
    {
        icon: ShieldCheck,
        title: "Symbolic Verification Engine",
        description: "Every generated answer is logically verified through symbolic reasoning, ensuring zero hallucination in solutions.",
        color: "from-pink-500 to-pink-600",
        bgColor: "bg-pink-500/10",
        borderColor: "border-pink-500/30",
        iconColor: "text-pink-400",
    },
    {
        icon: FileText,
        title: "Mock Test Engine",
        description: "Generate high-quality JEE/NEET/UPSC mock tests instantly with adaptive difficulty tailored to your performance.",
        color: "from-blue-500 to-blue-600",
        bgColor: "bg-blue-500/10",
        borderColor: "border-blue-500/30",
        iconColor: "text-blue-400",
    },
    {
        icon: Eye,
        title: "Visual Reasoning Engine",
        description: "Complex concepts transformed into animated visual reasoning steps that make learning intuitive and memorable.",
        color: "from-cyan-500 to-cyan-600",
        bgColor: "bg-cyan-500/10",
        borderColor: "border-cyan-500/30",
        iconColor: "text-cyan-400",
    },
    {
        icon: Box,
        title: "3D Visual Learning",
        description: "Experience concepts through culturally relevant 3D metaphors - from cricket physics to temple geometry.",
        color: "from-violet-500 to-violet-600",
        bgColor: "bg-violet-500/10",
        borderColor: "border-violet-500/30",
        iconColor: "text-violet-400",
    },
    {
        icon: TrendingUp,
        title: "Adaptive Learning Path",
        description: "AI analyzes your strengths and weaknesses to create a personalized learning journey that accelerates growth.",
        color: "from-fuchsia-500 to-fuchsia-600",
        bgColor: "bg-fuchsia-500/10",
        borderColor: "border-fuchsia-500/30",
        iconColor: "text-fuchsia-400",
    },
];

export function FeaturesGrid() {
    return (
        <section id="features" className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32">
            <motion.div
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                className="text-center mb-20"
            >
                <h2 className="text-3xl sm:text-4xl lg:text-5xl text-white mb-4 sm:mb-6">
                    Revolutionary{" "}
                    <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Learning Features
                    </span>
                </h2>
                <p className="text-white/70 text-base sm:text-lg lg:text-xl max-w-3xl mx-auto px-2 sm:px-0">
                    Scientifically designed features that transform how you learn, practice, and master concepts
                </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
                {features.map((feature, index) => {
                    const Icon = feature.icon;
                    return (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 50 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            whileHover={{ scale: 1.05, y: -10 }}
                            className="group"
                        >
                            <div
                                className={`relative h-full ${feature.bgColor} backdrop-blur-xl rounded-2xl sm:rounded-3xl border ${feature.borderColor} p-5 sm:p-6 lg:p-8 overflow-hidden transition-all`}
                            >
                                {/* 3D Icon Container */}
                                <motion.div
                                    className={`w-16 h-16 ${feature.bgColor} rounded-2xl flex items-center justify-center mb-6 border ${feature.borderColor} relative`}
                                    whileHover={{
                                        rotateY: 180,
                                    }}
                                    transition={{ duration: 0.6 }}
                                    style={{ transformStyle: "preserve-3d" }}
                                >
                                    <Icon className={`w-8 h-8 ${feature.iconColor}`} />

                                    {/* Glow effect */}
                                    <motion.div
                                        className={`absolute inset-0 bg-gradient-to-br ${feature.color} rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity blur-xl`}
                                    />
                                </motion.div>

                                <h3 className="text-xl sm:text-2xl text-white mb-3 sm:mb-4">{feature.title}</h3>
                                <p className="text-white/70 leading-relaxed">{feature.description}</p>

                                {/* Floating particle effect on hover */}
                                <motion.div
                                    className={`absolute -bottom-10 -right-10 w-40 h-40 bg-gradient-to-br ${feature.color} rounded-full opacity-0 group-hover:opacity-20 blur-3xl transition-all duration-500`}
                                />
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </section>
    );
}
