import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Play, 
  CheckCircle, 
  ArrowRight, 
  Brain, 
  Target, 
  BarChart3, 
  Shield, 
  Star,
  Users,
  Zap,
  Award,
  Heart,
  Lock,
  Eye,
  Phone,
  Mail,
  ExternalLink,
  LogIn,
  UserPlus,
  Menu,
  X
} from 'lucide-react';

const LandingPage = () => {
  const [scrollY, setScrollY] = useState(0);
  const [isVisible, setIsVisible] = useState({});
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Intersection Observer for animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          setIsVisible(prev => ({
            ...prev,
            [entry.target.id]: entry.isIntersecting
          }));
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('[id]').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white overflow-x-hidden">
      {/* Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center">
              <svg className="h-8 w-8 text-blue-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                Dhruv AI
              </h1>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
              <a href="#pricing" className="text-gray-300 hover:text-white transition-colors">Pricing</a>
              <a href="#testimonials" className="text-gray-300 hover:text-white transition-colors">Testimonials</a>
            </div>

            {/* Auth Buttons */}
            <div className="flex items-center space-x-4">
              <Link 
                to="/login" 
                className="text-gray-300 hover:text-white transition-colors px-4 py-2 rounded-lg hover:bg-white/10"
              >
                Sign In
              </Link>
              <Link 
                to="/register" 
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 px-6 py-2 rounded-lg font-semibold transition-all duration-300"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-4 -right-4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/3 -left-20 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 right-1/3 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      {/* Hero Section */}
      <section id="hero" className="relative min-h-screen flex items-center justify-center px-6 overflow-hidden pt-20">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-900/20 to-slate-900/40"></div>
        
        {/* Enhanced Neural Network Particle Animation */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Neural Network Particles */}
          {[...Array(15)].map((_, i) => (
            <div
              key={`particle-${i}`}
              className="absolute animate-float rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${4 + Math.random() * 6}s`
              }}
            >
              <div className="w-3 h-3 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-full opacity-60 animate-pulse"></div>
            </div>
          ))}
          
          {/* Verification Checkmarks */}
          {[...Array(8)].map((_, i) => (
            <div
              key={`check-${i}`}
              className="absolute animate-float opacity-20"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 8}s`,
                animationDuration: `${6 + Math.random() * 4}s`
              }}
            >
              <CheckCircle className="h-4 w-4 text-green-400" />
            </div>
          ))}
          
          {/* Neural Connection Lines */}
          {[...Array(5)].map((_, i) => (
            <div
              key={`line-${i}`}
              className="absolute bg-gradient-to-r from-blue-400/20 to-transparent h-px animate-pulse"
              style={{
                left: `${Math.random() * 80}%`,
                top: `${Math.random() * 100}%`,
                width: `${50 + Math.random() * 100}px`,
                animationDelay: `${Math.random() * 3}s`,
                transform: `rotate(${Math.random() * 360}deg)`
              }}
            ></div>
          ))}
        </div>

        <div className="relative z-10 max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Text Content */}
            <div className="text-center lg:text-left">
              {/* Enhanced Verification Badge with Pulsing Animation */}
              <div className="inline-flex items-center bg-green-500/20 border border-green-400/30 rounded-full px-6 py-2 mb-8 backdrop-blur-sm animate-pulse-glow">
                <div className="relative">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 animate-pulse" />
                  <div className="absolute inset-0 rounded-full bg-green-400/20 animate-ping"></div>
                </div>
                <span className="text-green-300 text-sm font-medium bg-gradient-to-r from-green-300 to-emerald-300 bg-clip-text text-transparent">
                  ✅ World's First Hallucination-Free AI Mentor
                </span>
              </div>

              {/* Enhanced Main Headline */}
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-8 leading-tight">
                <span className="bg-gradient-to-r from-white via-blue-100 to-indigo-200 bg-clip-text text-transparent">
                  Learn with Confidence.
                </span>
                <br />
                <span className="text-3xl md:text-5xl lg:text-6xl bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent animate-gradient">
                  Never Learn Wrong Again.
                </span>
              </h1>

              {/* Enhanced Sub-headline */}
              <p className="text-lg md:text-xl lg:text-2xl text-blue-100 mb-4 leading-relaxed">
                Every answer <span className="text-green-400 font-semibold">verified</span>. Every concept <span className="text-blue-300 font-semibold">cross-checked</span>.
              </p>
              <p className="text-xl md:text-2xl lg:text-3xl font-bold mb-12 leading-relaxed">
                <span className="bg-gradient-to-r from-yellow-400 via-orange-400 to-yellow-300 bg-clip-text text-transparent animate-pulse">
                  Confidence built on correctness.
                </span>
              </p>

              {/* Enhanced CTA Buttons with Micro-Interactions */}
              <div className="flex flex-col sm:flex-row gap-6 justify-center lg:justify-start mb-12">
                <Link 
                  to="/register" 
                  className="group relative bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 px-10 py-5 rounded-2xl font-bold text-lg transition-all duration-500 transform hover:scale-110 shadow-2xl hover:shadow-blue-500/40 text-white no-underline inline-block text-center overflow-hidden"
                >
                  {/* Glowing Background Effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-400 rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-500 blur-md"></div>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                  
                  {/* Shimmer Effect */}
                  <div className="absolute inset-0 -skew-x-12 translate-x-full group-hover:translate-x-[-200%] bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-1000"></div>
                  
                  <span className="relative flex items-center justify-center">
                    <CheckCircle className="mr-3 h-6 w-6 group-hover:rotate-12 transition-transform duration-300" />
                    Start Verified Learning
                    <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-2 transition-transform duration-300" />
                  </span>
                </Link>
                
                <button className="group relative border-2 border-blue-400/50 hover:border-blue-300 px-10 py-5 rounded-2xl font-bold text-lg transition-all duration-500 backdrop-blur-sm hover:bg-blue-500/20 text-white overflow-hidden">
                  {/* Subtle Glow Effect */}
                  <div className="absolute inset-0 bg-blue-400/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  
                  <span className="relative flex items-center justify-center">
                    <div className="relative mr-3">
                      <Play className="h-6 w-6 group-hover:scale-110 transition-transform duration-300" />
                      <div className="absolute inset-0 bg-blue-400/20 rounded-full group-hover:animate-ping"></div>
                    </div>
                    Watch Demo
                  </span>
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="flex flex-wrap justify-center lg:justify-start items-center gap-6 text-blue-200 text-sm">
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                  <span>Trusted by 50,000+ students</span>
                </div>
                <div className="flex items-center">
                  <Shield className="h-4 w-4 text-blue-400 mr-2" />
                  <span>100% Privacy Protected</span>
                </div>
                <div className="flex items-center">
                  <Star className="h-4 w-4 text-yellow-400 mr-2" />
                  <span>4.9/5 Rating</span>
                </div>
              </div>
            </div>

            {/* Right Column - Enhanced Hero with AI Hologram Effect */}
            <div className="relative">
              <div className="relative rounded-3xl overflow-hidden shadow-2xl transform hover:scale-105 transition-transform duration-700 group">
                <img 
                  src="https://images.unsplash.com/photo-1541178735493-479c1a27ed24" 
                  alt="Student learning with AI hologram technology" 
                  className="w-full h-96 lg:h-[500px] object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-blue-900/90 via-blue-600/30 to-transparent"></div>
                
                {/* AI Hologram Effect */}
                <div className="absolute top-4 right-4 w-32 h-32 opacity-80">
                  <div className="relative w-full h-full">
                    {/* Hologram Brain */}
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/60 to-blue-500/60 rounded-full animate-pulse-slow blur-sm"></div>
                    <div className="absolute inset-2 bg-gradient-to-br from-cyan-300/80 to-blue-400/80 rounded-full flex items-center justify-center">
                      <Brain className="h-16 w-16 text-white animate-pulse" />
                    </div>
                    
                    {/* Holographic Rings */}
                    <div className="absolute inset-0 rounded-full border-2 border-cyan-400/40 animate-ping"></div>
                    <div className="absolute inset-4 rounded-full border border-blue-300/30 animate-ping delay-1000"></div>
                    
                    {/* Floating Data Points */}
                    {[...Array(6)].map((_, i) => (
                      <div
                        key={i}
                        className="absolute w-2 h-2 bg-cyan-400 rounded-full animate-bounce opacity-60"
                        style={{
                          left: `${20 + Math.cos(i * 60 * Math.PI / 180) * 50}%`,
                          top: `${20 + Math.sin(i * 60 * Math.PI / 180) * 50}%`,
                          animationDelay: `${i * 0.2}s`
                        }}
                      ></div>
                    ))}
                  </div>
                </div>
                
                {/* Enhanced Verification Panel */}
                <div className="absolute bottom-6 left-6 right-6">
                  <div className="bg-white/15 backdrop-blur-xl rounded-2xl p-5 border border-white/30 shadow-2xl">
                    <div className="flex items-center justify-between text-white">
                      <div>
                        <p className="text-sm text-cyan-200 flex items-center mb-2">
                          <CheckCircle className="h-5 w-5 text-green-400 mr-2 animate-pulse" />
                          AI Verification Complete
                        </p>
                        <p className="font-bold text-lg">Structured verified notes created</p>
                        <p className="text-xs text-blue-200 mt-1">100% Hallucination-Free • Dual-Layer Validated</p>
                      </div>
                      <div className="flex flex-col space-y-1">
                        <div className="flex space-x-1">
                          <div className="animate-pulse">
                            <CheckCircle className="h-4 w-4 text-green-400" />
                          </div>
                          <div className="animate-pulse delay-300">
                            <CheckCircle className="h-4 w-4 text-green-400" />
                          </div>
                          <div className="animate-pulse delay-700">
                            <CheckCircle className="h-4 w-4 text-green-400" />
                          </div>
                        </div>
                        <div className="text-xs text-green-300 text-center">Verified</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Holographic Glow */}
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/10 via-transparent to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-blue-400 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-blue-400 rounded-full mt-2 animate-pulse"></div>
          </div>
        </div>
      </section>

      {/* Problem → Solution Section */}
      <section id="problem-solution" className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            {/* Problem Side */}
            <div className={`transform transition-all duration-1000 ${isVisible['problem-solution'] ? 'translate-x-0 opacity-100' : '-translate-x-20 opacity-0'}`}>
              <div className="bg-red-500/10 border border-red-400/20 rounded-2xl p-8 backdrop-blur-sm">
                <h3 className="text-2xl font-bold text-red-300 mb-6 flex items-center">
                  <Target className="h-6 w-6 mr-3 text-red-400" />
                  The Problem
                </h3>
                <div className="space-y-4 text-red-100">
                  <p className="text-lg leading-relaxed">
                    Most AI tutors <strong className="text-red-300">sound confident</strong> — even when they're wrong. 
                    Students learn incorrect information without knowing it.
                  </p>
                  <div className="bg-red-900/20 p-4 rounded-lg border border-red-400/20">
                    <p className="text-sm text-red-200 italic">
                      "Chaotic, unverified AI output leads to confusion and wrong learning"
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Solution Side */}
            <div className={`transform transition-all duration-1000 delay-300 ${isVisible['problem-solution'] ? 'translate-x-0 opacity-100' : 'translate-x-20 opacity-0'}`}>
              <div className="bg-gradient-to-br from-green-500/10 to-blue-500/10 border border-green-400/20 rounded-2xl p-8 backdrop-blur-sm">
                <h3 className="text-2xl font-bold text-green-300 mb-6 flex items-center">
                  <CheckCircle className="h-6 w-6 mr-3 text-green-400" />
                  Dhruv AI Solution
                </h3>
                <div className="space-y-4 text-green-100">
                  <p className="text-lg leading-relaxed">
                    <strong className="text-green-300">Dhruv AI verifies before teaching</strong>, so students never learn wrong. 
                    Every answer is cross-checked and validated.
                  </p>
                  <div className="bg-green-900/20 p-4 rounded-lg border border-green-400/20">
                    <p className="text-sm text-green-200 italic">
                      "Organized, verified knowledge with confidence built on correctness"
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Transform Arrow */}
          <div className="text-center my-12">
            <div className="inline-block bg-gradient-to-r from-yellow-400 to-orange-400 text-black px-8 py-3 rounded-full font-bold text-lg animate-pulse">
              AI-Powered Transformation →
            </div>
          </div>
        </div>
      </section>

      {/* Core Features Section */}
      <section id="features" className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Everything You Need to Learn Smarter
            </h2>
            <p className="text-xl text-blue-200 max-w-3xl mx-auto">
              Four powerful AI tools working together to transform your learning experience
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: Brain,
                title: "Auto-Note Mentor",
                emoji: "🧠",
                description: "Turns lectures into verified notes & flashcards.",
                color: "from-purple-500 to-pink-500",
                bgColor: "purple-500/10"
              },
              {
                icon: Target,
                title: "Adaptive Mock Tests",
                emoji: "🧩",
                description: "Tests evolve with your verified progress.",
                color: "from-blue-500 to-cyan-500",
                bgColor: "blue-500/10"
              },
              {
                icon: BarChart3,
                title: "Mastery Map",
                emoji: "📊",
                description: "Visualize what's verified in your mind.",
                color: "from-green-500 to-emerald-500",
                bgColor: "green-500/10"
              },
              {
                icon: Heart,
                title: "Dual-Layer Mentor",
                emoji: "🤖",
                description: "Empathy meets accuracy — Mentor teaches, Professor verifies.",
                color: "from-orange-500 to-red-500",
                bgColor: "orange-500/10"
              }
            ].map((feature, index) => (
              <div
                key={index}
                className={`group relative bg-${feature.bgColor} border border-white/10 rounded-2xl p-8 backdrop-blur-sm hover:bg-white/5 transition-all duration-500 transform hover:scale-105 hover:shadow-2xl cursor-pointer`}
              >
                <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-20 rounded-2xl transition-opacity duration-500" 
                     style={{backgroundImage: `linear-gradient(135deg, var(--tw-gradient-stops))`}}></div>
                
                <div className="relative z-10">
                  <div className="text-4xl mb-4">{feature.emoji}</div>
                  <feature.icon className={`h-8 w-8 mb-4 bg-gradient-to-r ${feature.color} rounded-lg p-1.5`} />
                  <h3 className="text-xl font-bold mb-4 text-white group-hover:text-blue-200 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-300 leading-relaxed">
                    {feature.description}
                  </p>
                </div>

                {/* Hover Glow Effect */}
                <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 bg-gradient-to-r ${feature.color} blur-xl -z-10 transition-opacity duration-500`}></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo" className="py-24 px-6 relative">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
            Watch How Dhruv AI Eliminates AI Errors in Real Time
          </h2>
          <p className="text-xl text-blue-200 mb-12 max-w-3xl mx-auto">
            Experience verified, trustworthy AI learning.
          </p>

          <div className="relative group cursor-pointer">
            <div className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border border-blue-400/30 rounded-2xl p-8 backdrop-blur-sm hover:border-blue-400/50 transition-all duration-300">
              <div className="aspect-video bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl flex items-center justify-center relative overflow-hidden">
                {/* Play Button */}
                <div className="bg-blue-600 hover:bg-blue-700 rounded-full p-6 transition-all duration-300 transform group-hover:scale-110 shadow-2xl">
                  <Play className="h-12 w-12 text-white ml-1" />
                </div>
                
                {/* Demo Preview Elements */}
                <div className="absolute inset-4 border-2 border-dashed border-blue-400/30 rounded-lg"></div>
                <div className="absolute top-8 left-8 bg-green-500/20 border border-green-400 rounded-lg px-3 py-1 text-green-300 text-sm">
                  ✓ Live Demo
                </div>
              </div>
              
              <div className="mt-6 text-blue-200">
                <p className="text-sm">🎥 3:24 min • Full Product Walkthrough</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Loved by Students, Trusted by Parents
            </h2>
            <p className="text-xl text-blue-200">Real results from real students across India</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Aditi",
                role: "NEET Aspirant",
                quote: "Finally, an AI I can trust.",
                rating: 5,
                image: "👩‍🎓"
              },
              {
                name: "Rohit",
                role: "JEE Student",
                quote: "No more wrong answers.",
                rating: 5,
                image: "👨‍💻"
              },
              {
                name: "Sneha",
                role: "UPSC Candidate",
                quote: "Feels like two teachers — one to teach, one to verify.",
                rating: 5,
                image: "👩‍🏫"
              }
            ].map((testimonial, index) => (
              <div
                key={index}
                className="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-sm hover:bg-white/10 transition-all duration-300 transform hover:scale-105"
              >
                <div className="flex items-center mb-6">
                  <div className="text-4xl mr-4">{testimonial.image}</div>
                  <div>
                    <h4 className="font-bold text-white">{testimonial.name}</h4>
                    <p className="text-blue-300 text-sm">{testimonial.role}</p>
                  </div>
                </div>

                {/* Star Rating */}
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>

                <p className="text-gray-200 leading-relaxed italic">
                  "{testimonial.quote}"
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 px-6 relative">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Simple Plans. Maximum Value.
            </h2>
            <p className="text-xl text-blue-200">Choose the perfect plan for your learning journey</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Free",
                price: "₹0",
                period: "",
                description: "Try verified learning.",
                features: [
                  "Basic verified answers",
                  "Sample note generation",
                  "Community support",
                  "Mobile app access"
                ],
                cta: "Start Free",
                popular: false,
                color: "gray"
              },
              {
                name: "Premium",
                price: "₹499",
                period: "/mo",
                description: "Unlimited verified notes & tests.",
                features: [
                  "Unlimited verified answers",
                  "Advanced note generation",
                  "Adaptive mock tests",
                  "Priority support",
                  "Dual-layer AI mentor"
                ],
                cta: "Start Premium",
                popular: true,
                color: "blue"
              },
              {
                name: "Pro",
                price: "₹999",
                period: "/mo",
                description: "Your personal AI Professor with 1M context.",
                features: [
                  "Everything in Premium",
                  "Personal AI Professor",
                  "1M context window",
                  "Advanced analytics",
                  "Priority verification"
                ],
                cta: "Start Pro",
                popular: false,
                color: "purple"
              }
            ].map((plan, index) => (
              <div
                key={index}
                className={`relative bg-white/5 border-2 rounded-2xl p-8 backdrop-blur-sm transition-all duration-300 transform hover:scale-105 ${
                  plan.popular 
                    ? 'border-blue-400 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 shadow-2xl shadow-blue-500/20' 
                    : 'border-white/10 hover:border-white/20'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-full text-sm font-bold">
                    Most Popular
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                    <span className="text-blue-200 text-lg">/{plan.period}</span>
                  </div>
                  <p className="text-gray-300">{plan.description}</p>
                </div>

                <div className="space-y-4 mb-8">
                  {plan.features.map((feature, i) => (
                    <div key={i} className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" />
                      <span className="text-gray-200">{feature}</span>
                    </div>
                  ))}
                </div>

                <Link
                  to="/register"
                  className={`w-full py-3 rounded-xl font-semibold transition-all duration-300 no-underline text-center inline-block ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg'
                      : 'border-2 border-white/20 hover:border-white/40 text-white hover:bg-white/10'
                  }`}
                >
                  {plan.cta}
                </Link>

                <p className="text-center text-blue-300 text-sm mt-4 font-medium">
                  Start Free → Upgrade Anytime
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Enhanced Trust & Credibility Section */}
      <section id="trust" className="py-24 px-6 relative overflow-hidden">
        {/* Animated Background with Pulsing Tick Marks */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/40 via-blue-800/30 to-indigo-900/40"></div>
        <div className="absolute inset-0 overflow-hidden">
          {/* Pulsing Tick Marks Background */}
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="absolute opacity-10 animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 4}s`,
                animationDuration: `${2 + Math.random() * 3}s`
              }}
            >
              <CheckCircle className="h-6 w-6 text-green-400" />
            </div>
          ))}
          
          {/* Floating Verification Lines */}
          {[...Array(8)].map((_, i) => (
            <div
              key={`line-${i}`}
              className="absolute bg-gradient-to-r from-green-400/20 via-blue-400/10 to-transparent h-px animate-pulse"
              style={{
                left: `${Math.random() * 80}%`,
                top: `${Math.random() * 100}%`,
                width: `${100 + Math.random() * 200}px`,
                animationDelay: `${Math.random() * 3}s`,
                transform: `rotate(${Math.random() * 180}deg)`
              }}
            ></div>
          ))}
        </div>

        <div className={`relative max-w-6xl mx-auto text-center transform transition-all duration-1000 ${isVisible['trust'] ? 'translate-y-0 opacity-100' : 'translate-y-20 opacity-0'}`}>
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white via-green-100 to-blue-200 bg-clip-text text-transparent">
            Built for Accuracy. Engineered for Trust.
          </h2>
          <p className="text-xl md:text-2xl text-blue-200 mb-16 max-w-4xl mx-auto leading-relaxed">
            Every answer verified by Dhruv's symbolic reasoning core. <span className="text-green-400 font-semibold">Data encrypted, accuracy guaranteed.</span>
          </p>

          {/* Trust Badges Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            {[
              {
                icon: Shield,
                title: "Verified Symbolic Engine",
                badge: "✓",
                description: "Dual-layer reasoning prevents AI hallucinations with 100% verification coverage."
              },
              {
                icon: Brain,
                title: "AI Hallucination-Free Core",
                badge: "✓",
                description: "Every response cross-validated by our proprietary verification algorithms."
              },
              {
                icon: Lock,
                title: "100% Privacy Protected",
                badge: "✓",
                description: "End-to-end encryption with full compliance to Indian data protection standards."
              },
              {
                icon: Star,
                title: "Rated 4.9★ by Learners",
                badge: "✓",
                description: "Trusted by 50,000+ students across JEE, NEET, and UPSC preparation."
              }
            ].map((item, index) => (
              <div 
                key={index} 
                className="group bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm hover:bg-white/10 transition-all duration-500 transform hover:scale-105 hover:shadow-2xl hover:shadow-green-500/20"
              >
                {/* Icon with Glow */}
                <div className="relative mb-6">
                  <div className="bg-gradient-to-br from-green-500/20 to-blue-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto group-hover:from-green-400/30 group-hover:to-blue-400/30 transition-all duration-300">
                    <item.icon className="h-8 w-8 text-green-400 group-hover:scale-110 transition-transform duration-300" />
                  </div>
                  {/* Verification Badge */}
                  <div className="absolute -top-2 -right-2 bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold animate-pulse">
                    {item.badge}
                  </div>
                </div>
                
                <h3 className="text-lg font-bold text-white mb-3 group-hover:text-green-100 transition-colors">
                  {item.title}
                </h3>
                <p className="text-gray-300 text-sm leading-relaxed group-hover:text-gray-200 transition-colors">
                  {item.description}
                </p>
              </div>
            ))}
          </div>

          {/* Enhanced Final CTA */}
          <div className="relative">
            {/* Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 via-blue-500/10 to-indigo-500/10 rounded-3xl blur-xl"></div>
            
            <div className="relative bg-gradient-to-br from-green-500/10 to-blue-500/10 border border-green-400/20 rounded-3xl p-8 backdrop-blur-sm">
              <h3 className="text-2xl md:text-3xl font-bold mb-4 bg-gradient-to-r from-green-300 to-blue-300 bg-clip-text text-transparent">
                Join the Hallucination-Free Learning Revolution
              </h3>
              
              <Link 
                to="/register"
                className="group inline-flex items-center bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 px-10 py-4 rounded-2xl font-bold text-lg text-white transition-all duration-500 transform hover:scale-110 shadow-2xl hover:shadow-green-500/30 no-underline"
              >
                <CheckCircle className="mr-3 h-6 w-6 group-hover:rotate-12 transition-transform duration-300" />
                Start Verified Learning
                <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-2 transition-transform duration-300" />
                
                {/* Shimmer Effect */}
                <div className="absolute inset-0 -skew-x-12 translate-x-full group-hover:translate-x-[-200%] bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-1000"></div>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section id="final-cta" className="py-24 px-6 relative">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border border-blue-400/30 rounded-3xl p-12 backdrop-blur-sm">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Join the Hallucination-Free Learning Revolution
            </h2>
            <p className="text-xl text-blue-200 mb-8 leading-relaxed">
              Experience the world's first verified AI learning platform
            </p>
            
            {/* Animated verification ticks background */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center justify-center overflow-hidden pointer-events-none">
                {[...Array(6)].map((_, i) => (
                  <div
                    key={i}
                    className="absolute animate-float opacity-20"
                    style={{
                      left: `${20 + i * 12}%`,
                      top: `${Math.random() * 100}%`,
                      animationDelay: `${i * 0.5}s`,
                      animationDuration: `${3 + Math.random() * 2}s`
                    }}
                  >
                    <CheckCircle className="h-8 w-8 text-green-400" />
                  </div>
                ))}
              </div>
              
              <Link 
                to="/register"
                className="group relative bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 px-12 py-4 rounded-xl font-bold text-xl transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-blue-500/25 text-white no-underline inline-block"
              >
                <span className="flex items-center justify-center">
                  <CheckCircle className="mr-3 h-6 w-6" />
                  Start Verified Learning Today
                  <Zap className="ml-3 h-6 w-6 group-hover:rotate-12 transition-transform" />
                </span>
              </Link>
            </div>

            <p className="text-blue-300 text-sm mt-4">
              ✓ Free forever • ✓ No credit card required • ✓ Instant access
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900/50 border-t border-white/10 py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            {/* Brand */}
            <div className="md:col-span-2">
              <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent mb-4">
                Dhruv AI
              </h3>
              <p className="text-gray-300 mb-6 max-w-md">
                Your verified AI mentor for competitive exam success. Transforming learning through hallucination-free artificial intelligence.
              </p>
              <div className="flex space-x-4">
                {/* Social Links */}
                <div className="bg-white/10 hover:bg-white/20 p-2 rounded-lg cursor-pointer transition-colors">
                  <Users className="h-5 w-5 text-blue-400" />
                </div>
                <div className="bg-white/10 hover:bg-white/20 p-2 rounded-lg cursor-pointer transition-colors">
                  <Mail className="h-5 w-5 text-blue-400" />
                </div>
                <div className="bg-white/10 hover:bg-white/20 p-2 rounded-lg cursor-pointer transition-colors">
                  <Phone className="h-5 w-5 text-blue-400" />
                </div>
              </div>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-bold text-white mb-4">Product</h4>
              <div className="space-y-2">
                {['Features', 'Pricing', 'Demo', 'API'].map(link => (
                  <a key={link} href={`#${link.toLowerCase()}`} className="block text-gray-300 hover:text-blue-400 transition-colors">
                    {link}
                  </a>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Support</h4>
              <div className="space-y-2">
                {['Help Center', 'Contact', 'Privacy Policy', 'Terms'].map(link => (
                  <a key={link} href="#" className="block text-gray-300 hover:text-blue-400 transition-colors">
                    {link}
                  </a>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom */}
          <div className="border-t border-white/10 pt-8 text-center">
            <p className="text-gray-400">
              Made with <Heart className="h-4 w-4 text-red-400 inline mx-1" /> in India for Students Everywhere
            </p>
            <p className="text-gray-500 text-sm mt-2">
              © 2024 Dhruv AI. All rights reserved. • Transforming Education Through AI
            </p>
          </div>
        </div>
      </footer>

      {/* Enhanced Custom Styles */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        @keyframes pulse-glow {
          0%, 100% { 
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
            transform: scale(1);
          }
          50% { 
            box-shadow: 0 0 40px rgba(34, 197, 94, 0.6);
            transform: scale(1.02);
          }
        }
        
        @keyframes pulse-slow {
          0%, 100% { opacity: 0.6; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.1); }
        }
        
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        
        .animate-pulse-glow {
          animation: pulse-glow 3s ease-in-out infinite;
        }
        
        .animate-pulse-slow {
          animation: pulse-slow 4s ease-in-out infinite;
        }
        
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease-in-out infinite;
        }
        
        .animate-shimmer {
          animation: shimmer 2s ease-in-out infinite;
        }

        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        /* Smooth scrolling */
        html {
          scroll-behavior: smooth;
        }

        /* Enhanced gradient backgrounds */
        .bg-gradient-conic {
          background: conic-gradient(from 0deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6);
        }
        
        /* Neural network effect */
        .neural-glow {
          filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.5));
        }
        
        /* Holographic effect */
        .hologram-effect {
          background: linear-gradient(45deg, rgba(59, 130, 246, 0.1), rgba(34, 197, 94, 0.1));
          backdrop-filter: blur(10px);
        }
      `}</style>
    </div>
  );
};

export default LandingPage;