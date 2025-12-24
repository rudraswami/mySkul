import { motion } from "framer-motion";
import { Zap, Check, ArrowRight, Star } from "lucide-react";
import { Link } from "react-router-dom";

export function CTASection() {
    // Pricing data matching backend planConfig_ai_tutor.json
    const plans = [
        {
            name: "Free",
            price: "₹0",
            period: "forever",
            tagline: "Perfect for trying out",
            features: [
                "10 AI sessions per month",
                "1 mock test per week",
                "1 note upload per day",
                "Basic analytics"
            ],
            highlight: false,
            cta: "Start Free",
            ctaLink: "/auth"
        },
        {
            name: "Student",
            price: "₹199",
            period: "per month",
            tagline: "Most popular for daily AI help",
            features: [
                "Unlimited AI sessions",
                "3 mock tests per week",
                "Unlimited note uploads",
                "Advanced analytics",
                "Hinglish support",
                "Image uploads"
            ],
            highlight: true,
            badge: "Most Popular",
            cta: "Get Student Plan",
            ctaLink: "/auth"
        },
        {
            name: "Pro",
            price: "₹299",
            period: "per month",
            tagline: "Best for JEE, NEET, CBSE",
            features: [
                "Everything in Student",
                "Unlimited mock tests",
                "Emotion-aware AI",
                "Priority support",
                "Parent dashboard",
                "Offline mode"
            ],
            highlight: false,
            cta: "Get Pro Plan",
            ctaLink: "/auth"
        }
    ];

    return (
        <section id="pricing" className="relative z-10 max-w-7xl mx-auto px-6 py-32">
            <div className="relative">
                {/* Background Glow */}
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 via-pink-500/20 to-purple-500/20 rounded-3xl blur-3xl" />

                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8 }}
                    className="relative bg-gradient-to-br from-purple-500/10 to-pink-500/10 backdrop-blur-xl rounded-3xl border border-white/20 overflow-hidden"
                >
                    {/* Animated Background Pattern */}
                    <div className="absolute inset-0 opacity-10">
                        <div className="absolute inset-0" style={{
                            backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)",
                            backgroundSize: "40px 40px",
                        }} />
                    </div>

                    <div className="relative p-12 lg:p-16">
                        <div className="grid lg:grid-cols-2 gap-12 items-center">
                            {/* Left Content */}
                            <div>
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    whileInView={{ opacity: 1, scale: 1 }}
                                    viewport={{ once: true }}
                                    transition={{ duration: 0.6 }}
                                    className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/20 border border-purple-500/30 rounded-full mb-6"
                                >
                                    <Zap className="w-4 h-4 text-purple-400" />
                                    <span className="text-purple-300 text-sm">Launch Offer - 50% Off</span>
                                </motion.div>

                                <h2 className="text-5xl text-white mb-6 leading-tight">
                                    Start Your{" "}
                                    <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                                        Learning Revolution
                                    </span>
                                </h2>

                                <p className="text-white/70 text-xl mb-8 leading-relaxed">
                                    Join thousands of students who are already learning smarter with DRON AI's
                                    revolutionary Dual-Layer AI system.
                                </p>

                                <div className="space-y-4 mb-8">
                                    {[
                                        "Unlimited AI mentor sessions",
                                        "Personal AI professor & mentor",
                                        "Mock tests with detailed analysis",
                                        "Visual learning with diagrams",
                                        "Progress tracking & analytics",
                                    ].map((feature, index) => (
                                        <motion.div
                                            key={feature}
                                            initial={{ opacity: 0, x: -20 }}
                                            whileInView={{ opacity: 1, x: 0 }}
                                            viewport={{ once: true }}
                                            transition={{ duration: 0.4, delay: index * 0.1 }}
                                            className="flex items-center gap-3"
                                        >
                                            <div className="w-6 h-6 bg-purple-500/20 rounded-full flex items-center justify-center border border-purple-500/30">
                                                <Check className="w-4 h-4 text-purple-400" />
                                            </div>
                                            <span className="text-white">{feature}</span>
                                        </motion.div>
                                    ))}
                                </div>

                                <div className="flex flex-wrap gap-4">
                                    <Link to="/auth">
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full hover:shadow-2xl hover:shadow-purple-500/50 transition-all flex items-center gap-2"
                                        >
                                            Start Free Trial
                                            <ArrowRight className="w-5 h-5" />
                                        </motion.button>
                                    </Link>

                                    <motion.a
                                        href="#pricing-cards"
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        className="px-8 py-4 bg-white/10 backdrop-blur-sm text-white rounded-full border border-white/20 hover:bg-white/20 transition-all"
                                    >
                                        Compare Plans
                                    </motion.a>
                                </div>
                            </div>

                            {/* Right Pricing Cards */}
                            <div id="pricing-cards" className="space-y-4">
                                {plans.map((plan, index) => (
                                    <motion.div
                                        key={plan.name}
                                        initial={{ opacity: 0, x: 50 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        viewport={{ once: true }}
                                        transition={{ duration: 0.6, delay: index * 0.1 }}
                                        whileHover={{ scale: 1.02, x: -10 }}
                                        className={`relative backdrop-blur-xl rounded-2xl p-6 ${
                                            plan.highlight 
                                                ? 'bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30' 
                                                : 'bg-white/5 border border-white/10'
                                        }`}
                                    >
                                        {plan.badge && (
                                            <div className="absolute -top-3 -right-3">
                                                <div className="px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs rounded-full flex items-center gap-1">
                                                    <Star className="w-3 h-3" />
                                                    {plan.badge}
                                                </div>
                                            </div>
                                        )}
                                        <div className="flex items-center justify-between mb-4">
                                            <div>
                                                <h3 className="text-xl text-white mb-1">{plan.name} Plan</h3>
                                                <p className="text-white/60 text-sm">{plan.tagline}</p>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-3xl text-white font-bold">{plan.price}</div>
                                                <div className="text-white/60 text-sm">{plan.period}</div>
                                            </div>
                                        </div>
                                        <div className="space-y-2 text-sm text-white/70 mb-4">
                                            {plan.features.slice(0, 4).map((feature, i) => (
                                                <div key={i} className="flex items-center gap-2">
                                                    <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />
                                                    <span>{feature}</span>
                                                </div>
                                            ))}
                                        </div>
                                        <Link to={plan.ctaLink}>
                                            <button className={`w-full py-2.5 rounded-lg text-sm font-medium transition-all ${
                                                plan.highlight
                                                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg'
                                                    : 'bg-white/10 text-white hover:bg-white/20'
                                            }`}>
                                                {plan.cta}
                                            </button>
                                        </Link>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Animated Corner Elements */}
                    <motion.div
                        className="absolute -bottom-20 -left-20 w-64 h-64 bg-purple-500/30 rounded-full blur-3xl"
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
                    <motion.div
                        className="absolute -top-20 -right-20 w-64 h-64 bg-pink-500/30 rounded-full blur-3xl"
                        animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.3, 0.5, 0.3],
                        }}
                        transition={{
                            duration: 5,
                            repeat: Infinity,
                            ease: "easeInOut",
                            delay: 1,
                        }}
                    />
                </motion.div>
            </div>
        </section>
    );
}
