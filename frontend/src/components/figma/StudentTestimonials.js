import { motion } from "framer-motion";
import { Star, Quote } from "lucide-react";
import { ImageWithFallback } from "./ImageWithFallback";

const testimonials = [
    {
        name: "Priya Sharma",
        role: "JEE Advanced Rank 247",
        image: "https://images.unsplash.com/photo-1656236559909-b05a20191727?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjB5b3V0aCUyMGVkdWNhdGlvbnxlbnwxfHx8fDE3NjM3OTExMjZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        quote: "DRON AI's Error Genome™ caught my conceptual gaps in rotational mechanics that I didn't even know existed. The 3D cricket physics module made vector analysis so intuitive!",
        rating: 5,
        exam: "JEE",
        improvement: "+45% in Physics",
    },
    {
        name: "Arjun Patel",
        role: "NEET AIR 156",
        image: "https://images.unsplash.com/photo-1623303366639-0e330d7c3d9f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjBzdHVkZW50JTIwc3R1ZHlpbmd8ZW58MXx8fHwxNzYzNzEyNDI4fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        quote: "The Dual-Layer AI is genius! The Mentor Layer kept me motivated during tough times, while the Professor Layer ensured every biology concept was crystal clear. Zero hallucinations = 100% confidence.",
        rating: 5,
        exam: "NEET",
        improvement: "+38% in Biology",
    },
    {
        name: "Aisha Khan",
        role: "UPSC CSE Rank 42",
        image: "https://images.unsplash.com/photo-1716471081169-cb8528a395d3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjB0ZWVuYWdlciUyMGxhcHRvcHxlbnwxfHx8fDE3NjM3OTExMjZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        quote: "Mock tests that adapt in real-time? Game changer! The Railway Economics module helped me understand network theory for governance questions. Cultural context makes all the difference.",
        rating: 5,
        exam: "UPSC",
        improvement: "Prelims: 175/200",
    },
    {
        name: "Rohan Desai",
        role: "12th Board - 98.2%",
        image: "https://images.unsplash.com/photo-1571260899304-425eee4c7efc?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjBjb2xsZWdlJTIwc3R1ZGVudHN8ZW58MXx8fHwxNzYzNzkxMTI1fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        quote: "Symbolic Verification Engine gives me complete trust in every solution. No more doubting my answers! The temple geometry module made trigonometry my strongest subject.",
        rating: 5,
        exam: "Board Exams",
        improvement: "Math: 85→99",
    },
];

export function StudentTestimonials() {
    return (
        <section className="relative z-10 max-w-7xl mx-auto px-6 py-32">
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
                        scale: [1, 1.05, 1],
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                >
                    <div className="px-6 py-3 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 backdrop-blur-xl rounded-full border border-yellow-500/30">
                        <span className="text-yellow-300">⭐ Student Success Stories</span>
                    </div>
                </motion.div>

                <h2 className="text-5xl lg:text-6xl text-white mb-6">
                    Real Students,{" "}
                    <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                        Real Results
                    </span>
                </h2>
                <p className="text-white/70 text-xl max-w-3xl mx-auto">
                    Join thousands of Indian students who are achieving their dreams with DRON AI's revolutionary learning platform
                </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
                {testimonials.map((testimonial, index) => (
                    <motion.div
                        key={testimonial.name}
                        initial={{ opacity: 0, y: 50 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                        whileHover={{ y: -10, scale: 1.02 }}
                        className="relative group"
                    >
                        <div className="relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-3xl border border-white/20 p-8 overflow-hidden">
                            {/* Animated background glow */}
                            <motion.div
                                className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-pink-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                                animate={{
                                    backgroundPosition: ["0% 0%", "100% 100%"],
                                }}
                                transition={{
                                    duration: 10,
                                    repeat: Infinity,
                                    ease: "linear",
                                }}
                            />

                            <div className="relative z-10">
                                {/* Quote Icon */}
                                <motion.div
                                    className="absolute -top-4 -right-4 w-16 h-16 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl flex items-center justify-center border border-purple-500/30"
                                    animate={{
                                        rotate: [0, 10, -10, 0],
                                    }}
                                    transition={{
                                        duration: 5,
                                        repeat: Infinity,
                                        ease: "easeInOut",
                                    }}
                                >
                                    <Quote className="w-8 h-8 text-purple-400" />
                                </motion.div>

                                {/* Student Info */}
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="relative">
                                        <motion.div
                                            className="w-16 h-16 rounded-full overflow-hidden border-2 border-purple-500/50"
                                            whileHover={{ scale: 1.1, rotate: 5 }}
                                        >
                                            <ImageWithFallback
                                                src={testimonial.image}
                                                alt={testimonial.name}
                                                className="w-full h-full object-cover"
                                            />
                                        </motion.div>

                                        {/* Success badge */}
                                        <motion.div
                                            className="absolute -bottom-1 -right-1 w-6 h-6 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-full flex items-center justify-center border-2 border-slate-950"
                                            animate={{
                                                scale: [1, 1.2, 1],
                                            }}
                                            transition={{
                                                duration: 2,
                                                repeat: Infinity,
                                            }}
                                        >
                                            <Star className="w-3 h-3 text-white fill-white" />
                                        </motion.div>
                                    </div>

                                    <div className="flex-1">
                                        <h4 className="text-white text-lg">{testimonial.name}</h4>
                                        <p className="text-purple-400 text-sm">{testimonial.role}</p>
                                    </div>

                                    {/* Exam Badge */}
                                    <div className="px-3 py-1.5 bg-purple-500/20 backdrop-blur-sm rounded-full border border-purple-500/30">
                                        <span className="text-purple-300 text-xs">{testimonial.exam}</span>
                                    </div>
                                </div>

                                {/* Rating */}
                                <div className="flex items-center gap-1 mb-4">
                                    {[...Array(testimonial.rating)].map((_, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, scale: 0 }}
                                            whileInView={{ opacity: 1, scale: 1 }}
                                            viewport={{ once: true }}
                                            transition={{ delay: index * 0.1 + i * 0.1 }}
                                        >
                                            <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                                        </motion.div>
                                    ))}
                                </div>

                                {/* Quote */}
                                <p className="text-white/80 leading-relaxed mb-6">
                                    "{testimonial.quote}"
                                </p>

                                {/* Improvement Badge */}
                                <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500/20 to-emerald-500/20 backdrop-blur-sm rounded-full border border-green-500/30">
                                    <motion.div
                                        animate={{
                                            y: [0, -3, 0],
                                        }}
                                        transition={{
                                            duration: 2,
                                            repeat: Infinity,
                                        }}
                                    >
                                        📈
                                    </motion.div>
                                    <span className="text-green-300 text-sm">{testimonial.improvement}</span>
                                </div>
                            </div>

                            {/* Decorative elements */}
                            <motion.div
                                className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-2xl"
                                animate={{
                                    scale: [1, 1.2, 1],
                                    opacity: [0.3, 0.5, 0.3],
                                }}
                                transition={{
                                    duration: 4,
                                    repeat: Infinity,
                                    ease: "easeInOut",
                                    delay: index * 0.2,
                                }}
                            />
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Bottom Stats */}
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6"
            >
                {[
                    { value: "50K+", label: "Students Learning", icon: "👨‍🎓" },
                    { value: "98.4%", label: "Success Rate", icon: "🎯" },
                    { value: "100K+", label: "Tests Completed", icon: "📝" },
                    { value: "4.9/5", label: "Average Rating", icon: "⭐" },
                ].map((stat, index) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, scale: 0.8 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.5 + index * 0.1 }}
                        whileHover={{ scale: 1.05, y: -5 }}
                        className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl border border-white/20 p-6 text-center"
                    >
                        <motion.div
                            className="text-4xl mb-2"
                            animate={{
                                rotate: [0, 10, -10, 0],
                            }}
                            transition={{
                                duration: 4,
                                repeat: Infinity,
                                ease: "easeInOut",
                                delay: index * 0.2,
                            }}
                        >
                            {stat.icon}
                        </motion.div>
                        <div className="text-3xl text-white mb-1">{stat.value}</div>
                        <div className="text-white/60 text-sm">{stat.label}</div>
                    </motion.div>
                ))}
            </motion.div>
        </section>
    );
}
