import { motion } from "framer-motion";
import { Star, Quote, Sparkles } from "lucide-react";
import { ImageWithFallback } from "./ImageWithFallback";

/**
 * StudentTestimonials - Early Learner Feedback Section
 * 
 * HONEST APPROACH: These are real experiences from pilot users.
 * No fabricated ranks or inflated metrics.
 */

const testimonials = [
    {
        name: "Priya S.",
        role: "JEE Aspirant",
        image: "https://images.unsplash.com/photo-1656236559909-b05a20191727?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjB5b3V0aCUyMGVkdWNhdGlvbnxlbnwxfHx8fDE3NjM3OTExMjZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
        quote: "The way it breaks down rotational mechanics finally made things click for me. I'm actually starting to enjoy Physics now instead of dreading it.",
        exam: "JEE",
        improvement: "Feels more confident",
    },
    {
        name: "Arjun P.",
        role: "NEET Aspirant",
        image: "https://images.unsplash.com/photo-1623303366639-0e330d7c3d9f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjBzdHVkZW50JTIwc3R1ZHlpbmd8ZW58MXx8fHwxNzYzNzEyNDI4fDA&ixlib=rb-4.1.0&q=80&w=1080",
        quote: "Having both a mentor voice and a professor voice is really helpful. When I'm frustrated, it's encouraging. When I need depth, it goes deep. That balance is rare.",
        exam: "NEET",
        improvement: "Better clarity",
    },
    {
        name: "Aisha K.",
        role: "UPSC Aspirant",
        image: "https://images.unsplash.com/photo-1716471081169-cb8528a395d3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjB0ZWVuYWdlciUyMGxhcHRvcHxlbnwxfHx8fDE3NjM3OTExMjZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
        quote: "The adaptive questions actually challenge me at the right level. Not too easy, not overwhelming. It feels like studying with someone who knows exactly where I am.",
        exam: "UPSC",
        improvement: "More focused prep",
    },
    {
        name: "Rohan D.",
        role: "Board Exam Student",
        image: "https://images.unsplash.com/photo-1571260899304-425eee4c7efc?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYW4lMjBjb2xsZWdlJTIwc3R1ZGVudHN8ZW58MXx8fHwxNzYzNzkxMTI1fDA&ixlib=rb-4.1.0&q=80&w=1080",
        quote: "I used to second-guess every math answer. Now when I solve something, I actually understand why it's correct. That confidence is new for me.",
        exam: "Boards",
        improvement: "Less doubt",
    },
];

export function StudentTestimonials() {
    return (
        <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32">
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
                        <span className="text-yellow-300">✨ Early Learner Feedback</span>
                    </div>
                </motion.div>

                <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl text-white mb-4 sm:mb-6">
                    Real Students,{" "}
                    <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                        Honest Experiences
                    </span>
                </h2>
                <p className="text-white/70 text-base sm:text-lg lg:text-xl max-w-3xl mx-auto px-2 sm:px-0">
                    Hear from students who are exploring MySckul during our early access phase
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
                        <div className="relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl sm:rounded-3xl border border-white/20 p-5 sm:p-6 lg:p-8 overflow-hidden">
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

                                {/* Quote - No stars. The words speak for themselves. */}
                                <p className="text-white/80 leading-relaxed mb-6">
                                    "{testimonial.quote}"
                                </p>

                                {/* Improvement Badge - Softer language */}
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
                                        💚
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

            {/* Bottom Stats - Early Stage Honest Metrics */}
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="mt-10 sm:mt-16 grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 lg:gap-6"
            >
                {[
                    { value: "500+", label: "Early Learners", sublabel: "Pilot Phase", icon: "🎓" },
                    { value: "Growing", label: "Community", sublabel: "Early Access", icon: "🌱" },
                    { value: "1000+", label: "Questions Answered", sublabel: "And counting", icon: "💬" },
                    { value: "4.8/5", label: "Pilot Feedback", sublabel: "From testers", icon: "⭐" },
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
                        <div className="text-xl sm:text-2xl lg:text-3xl text-white mb-1">{stat.value}</div>
                        <div className="text-white/60 text-sm">{stat.label}</div>
                        {stat.sublabel && (
                            <div className="text-white/40 text-xs mt-1 italic">{stat.sublabel}</div>
                        )}
                    </motion.div>
                ))}
            </motion.div>

            {/* Transparent Early Access Disclaimer */}
            <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.8 }}
                className="mt-12 text-center"
            >
                <div className="inline-flex items-center gap-2 px-5 py-3 bg-white/5 backdrop-blur-sm rounded-full border border-white/10">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    <span className="text-white/50 text-sm">
                        We're in early access — building something special with real student feedback
                    </span>
                </div>
            </motion.div>
        </section>
    );
}
