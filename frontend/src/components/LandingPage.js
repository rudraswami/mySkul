import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Brain, Heart, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { HeroSection } from "./figma/HeroSection";
import { DualLayerSystem } from "./figma/DualLayerSystem";
import { InnovativeFeaturesGrid } from "./figma/InnovativeFeaturesGrid";
import { StudentTestimonials } from "./figma/StudentTestimonials";
import { VisualLearning } from "./figma/VisualLearning";
import { CTASection } from "./figma/CTASection";
import { FloatingOrbs } from "./figma/FloatingOrbs";

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isFeaturesOpen, setIsFeaturesOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const features = [
    { name: 'AI Tutor', desc: 'Personalized learning companion', icon: '🎓' },
    { name: 'Mock Tests', desc: 'Adaptive practice engine', icon: '📝' },
    { name: 'Error Genome', desc: 'Pattern recognition system', icon: '🧬' },
    { name: 'Visual Professor', desc: 'Concept visualization', icon: '👨‍🏫' }
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${isScrolled ? 'bg-[#000005]/95 backdrop-blur-2xl border-b border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.4)] py-3' : 'bg-transparent py-5'}`}>
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="relative w-9 h-9">
            <motion.div
              className="absolute inset-0 bg-gradient-to-br from-cyan-400 via-purple-500 to-blue-600 rounded-xl blur-md opacity-70"
              animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0.8, 0.5] }}
              transition={{ duration: 3, repeat: Infinity }}
            />
            <div className="relative w-full h-full bg-gradient-to-br from-[#000010] to-[#000020] rounded-xl border border-white/20 flex items-center justify-center shadow-lg">
              <Brain className="h-5 w-5 text-cyan-400" />
            </div>
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
            Druv<span className="text-cyan-400">.AI</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {/* Features Dropdown */}
          <div
            className="relative"
            onMouseEnter={() => setIsFeaturesOpen(true)}
            onMouseLeave={() => setIsFeaturesOpen(false)}
          >
            <button className="text-sm font-semibold text-gray-300 hover:text-cyan-400 transition-colors uppercase tracking-wider flex items-center gap-1 group">
              Features
              <motion.svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                animate={{ rotate: isFeaturesOpen ? 180 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </motion.svg>
            </button>

            <AnimatePresence>
              {isFeaturesOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ duration: 0.2 }}
                  className="absolute top-full left-0 mt-2 w-72 bg-[#000010]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-[0_20px_60px_rgba(0,0,0,0.5)] overflow-hidden"
                >
                  {features.map((feature, index) => (
                    <motion.a
                      key={feature.name}
                      href="#features"
                      className="flex items-start gap-4 p-4 hover:bg-white/5 transition-colors group border-b border-white/5 last:border-0"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <div className="text-2xl mt-0.5">{feature.icon}</div>
                      <div className="flex-1">
                        <div className="text-sm font-bold text-white group-hover:text-cyan-400 transition-colors">
                          {feature.name}
                        </div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {feature.desc}
                        </div>
                      </div>
                      <svg className="w-4 h-4 text-gray-600 group-hover:text-cyan-400 transition-all group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </motion.a>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <a href="#how-it-works" className="text-sm font-semibold text-gray-300 hover:text-cyan-400 transition-colors uppercase tracking-wider">
            How It Works
          </a>
          <a href="#pricing" className="text-sm font-semibold text-gray-300 hover:text-cyan-400 transition-colors uppercase tracking-wider">
            Pricing
          </a>
        </div>

        {/* CTA Buttons */}
        <div className="flex items-center gap-3">
          <Link to="/login" className="hidden sm:block text-sm font-bold text-gray-300 hover:text-white transition-colors uppercase tracking-wider">
            Login
          </Link>
          <Link
            to="/register"
            className="px-6 py-2.5 bg-gradient-to-r from-cyan-600 to-purple-600 text-white font-bold text-sm rounded-full hover:shadow-[0_0_30px_rgba(6,214,160,0.5)] transition-all uppercase tracking-wider border border-white/20"
          >
            Get Started
          </Link>
          <button className="md:hidden text-white" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            {isMobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#000010]/95 backdrop-blur-2xl border-b border-white/10"
          >
            <div className="flex flex-col p-6 gap-4">
              {/* Mobile Features */}
              <div className="space-y-2">
                <div className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">Features</div>
                {features.map((feature) => (
                  <a
                    key={feature.name}
                    href="#features"
                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <span className="text-xl">{feature.icon}</span>
                    <div>
                      <div className="text-sm font-semibold text-white">{feature.name}</div>
                      <div className="text-xs text-gray-500">{feature.desc}</div>
                    </div>
                  </a>
                ))}
              </div>

              <div className="border-t border-white/10 pt-4 space-y-3">
                <a href="#how-it-works" className="block text-sm font-semibold text-gray-300 hover:text-cyan-400 transition-colors uppercase tracking-wider">
                  How It Works
                </a>
                <a href="#pricing" className="block text-sm font-semibold text-gray-300 hover:text-cyan-400 transition-colors uppercase tracking-wider">
                  Pricing
                </a>
                <Link to="/login" className="block text-sm font-bold text-gray-300 hover:text-white transition-colors uppercase tracking-wider">
                  Login
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

const Footer = () => (
  <footer className="relative bg-gradient-to-b from-[#000005] to-[#000010] py-16 border-t border-white/10 overflow-hidden">
    {/* Background Effects */}
    <div className="absolute inset-0 pointer-events-none">
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-[120px]" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-[120px]" />
    </div>

    <div className="max-w-7xl mx-auto px-6 relative z-10">
      {/* Top Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-12">
        {/* Brand Column */}
        <div className="lg:col-span-2">
          <Link to="/" className="flex items-center gap-2 mb-4 group">
            <div className="relative w-10 h-10">
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-cyan-400 via-purple-500 to-blue-600 rounded-xl blur-md opacity-70"
                animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0.8, 0.5] }}
                transition={{ duration: 3, repeat: Infinity }}
              />
              <div className="relative w-full h-full bg-gradient-to-br from-[#000010] to-[#000020] rounded-xl border border-white/20 flex items-center justify-center">
                <Brain className="h-5 w-5 text-cyan-400" />
              </div>
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Druv<span className="text-cyan-400">.AI</span>
            </span>
          </Link>
          <p className="text-gray-400 text-sm mb-6 leading-relaxed">
            India's first Cognitive OS for JEE, NEET & UPSC. Powered by dual-layer AI combining emotional intelligence and symbolic reasoning.
          </p>
          {/* Social Links */}
          <div className="flex gap-3">
            {[
              { icon: '𝕏', label: 'Twitter', href: '#' },
              { icon: '📘', label: 'Facebook', href: '#' },
              { icon: '💼', label: 'LinkedIn', href: '#' },
              { icon: '📸', label: 'Instagram', href: '#' }
            ].map((social) => (
              <a
                key={social.label}
                href={social.href}
                className="w-10 h-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center hover:bg-cyan-500/20 hover:border-cyan-500/50 transition-all group"
                aria-label={social.label}
              >
                <span className="text-lg group-hover:scale-110 transition-transform">{social.icon}</span>
              </a>
            ))}
          </div>
        </div>

        {/* Product Links */}
        <div>
          <h3 className="text-white font-bold text-sm uppercase tracking-wider mb-4">Product</h3>
          <ul className="space-y-3">
            {[
              { name: 'AI Tutor', href: '#features' },
              { name: 'Mock Tests', href: '#features' },
              { name: 'Error Genome', href: '#features' },
              { name: 'Visual Professor', href: '#features' },
              { name: 'Pricing', href: '#pricing' }
            ].map((link) => (
              <li key={link.name}>
                <a href={link.href} className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  {link.name}
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Company Links */}
        <div>
          <h3 className="text-white font-bold text-sm uppercase tracking-wider mb-4">Company</h3>
          <ul className="space-y-3">
            {[
              { name: 'About Us', href: '#' },
              { name: 'Careers', href: '#' },
              { name: 'Blog', href: '#' },
              { name: 'Press Kit', href: '#' },
              { name: 'Contact', href: '#' }
            ].map((link) => (
              <li key={link.name}>
                <a href={link.href} className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  {link.name}
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Legal Links */}
        <div>
          <h3 className="text-white font-bold text-sm uppercase tracking-wider mb-4">Legal</h3>
          <ul className="space-y-3">
            {[
              { name: 'Privacy Policy', href: '#' },
              { name: 'Terms of Service', href: '#' },
              { name: 'Cookie Policy', href: '#' },
              { name: 'Refund Policy', href: '#' },
              { name: 'Disclaimer', href: '#' }
            ].map((link) => (
              <li key={link.name}>
                <a href={link.href} className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  {link.name}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Newsletter Section */}
      <div className="border-t border-white/10 pt-8 mb-8">
        <div className="max-w-md mx-auto text-center">
          <h3 className="text-white font-bold text-lg mb-2">Stay Updated</h3>
          <p className="text-gray-400 text-sm mb-4">Get the latest updates on AI-powered learning</p>
          <div className="flex gap-2">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 transition-colors text-sm"
            />
            <button className="px-6 py-2.5 bg-gradient-to-r from-cyan-600 to-purple-600 text-white font-bold text-sm rounded-lg hover:shadow-[0_0_30px_rgba(6,214,160,0.5)] transition-all">
              Subscribe
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span>© 2025 Druv.AI</span>
          <span className="hidden md:inline">•</span>
          <span className="flex items-center gap-1.5">
            Made with <Heart className="h-3.5 w-3.5 text-red-500 fill-current animate-pulse" /> for India
          </span>
        </div>
        <div className="flex items-center gap-6 text-xs text-gray-500">
          <a href="#" className="hover:text-cyan-400 transition-colors">Status</a>
          <a href="#" className="hover:text-cyan-400 transition-colors">Changelog</a>
          <a href="#" className="hover:text-cyan-400 transition-colors">Support</a>
        </div>
      </div>
    </div>
  </footer>
);

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-[#000005] text-white overflow-x-hidden font-sans selection:bg-[#FF9933] selection:text-white relative">
      <FloatingOrbs />
      <Navbar />

      <main>
        <HeroSection />
        <DualLayerSystem />
        <InnovativeFeaturesGrid />
        <VisualLearning />
        <StudentTestimonials />
        <CTASection />
      </main>

      <Footer />
    </div>
  );
};

export default LandingPage;