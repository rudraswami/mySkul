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
  Clock,
  TrendingUp,
  BookOpen,
  MessageCircle,
  FileText,
  Menu,
  X,
  AlertCircle,
  Coffee,
  Sparkles
} from 'lucide-react';
import { PLANS_CONFIG, formatPrice } from '../config/plans';

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

  const painPoints = [
    {
      emoji: "😰",
      title: "Stuck at 11 PM?",
      description: "That physics problem isn't solving itself, and your coaching teacher is unavailable",
      stat: "87% students struggle after coaching hours"
    },
    {
      emoji: "📚",
      title: "Drowning in Notes?",
      description: "3 months of coaching notes, but you can't find that one formula when you need it",
      stat: "Students waste 2+ hours daily searching notes"
    },
    {
      emoji: "😓",
      title: "Exam Anxiety?",
      description: "Mock tests feel overwhelming, and you're not sure which topics need more attention",
      stat: "68% students experience high exam stress"
    },
    {
      emoji: "⏰",
      title: "Running Out of Time?",
      description: "Syllabus is huge, time is short, and you don't know what to prioritize",
      stat: "Only 23% students complete full revision"
    }
  ];

  const solutions = [
    {
      icon: MessageCircle,
      title: "24/7 AI Tutor - Your Midnight Study Buddy",
      description: "Stuck at 11 PM? Get instant, verified answers to any doubt - Physics, Chemistry, Math - anytime.",
      benefit: "Never feel alone in your preparation",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: FileText,
      title: "Auto-Note Mentor - From Chaos to Clarity",
      description: "Upload lecture recordings, get organized, searchable notes in minutes. Find that formula instantly.",
      benefit: "Save 2+ hours daily in note searching",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: Target,
      title: "Smart Mock Tests - Practice That Adapts to YOU",
      description: "Tests that match your level. Too easy? Gets harder. Too hard? Adjusts to build confidence.",
      benefit: "Build confidence, not overwhelm",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: TrendingUp,
      title: "AI Progress Tracking - Know Exactly What to Study",
      description: "See your weak areas, track improvement, get personalized study recommendations daily.",
      benefit: "Study smart, not just hard",
      color: "from-orange-500 to-red-500"
    }
  ];

  const testimonials = [
    {
      name: "Priya Sharma",
      grade: "Class 12, Mumbai",
      progress: "Day 47 of preparation",
      image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop",
      quote: "Today I solved 15 chemistry doubts at midnight using the AI Tutor. No fake answers like ChatGPT - everything is verified! My confidence is growing daily.",
      feature: "🤖 AI Tutor",
      dailyStat: "Solved 15 doubts today",
      improvement: "87% → 92% in mock tests"
    },
    {
      name: "Arjun Patel",
      grade: "Class 11, Ahmedabad",
      progress: "Week 6 of using Dhruv AI",
      image: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&h=100&fit=crop",
      quote: "Uploaded my 3-hour physics lecture yesterday. Got organized notes in 10 minutes! Now I can actually find formulas when I need them. Game changer!",
      feature: "📝 Auto-Note Mentor",
      dailyStat: "3 lectures converted today",
      improvement: "2+ hours saved daily"
    },
    {
      name: "Ananya Reddy",
      grade: "Class 10, Hyderabad",
      progress: "Daily streak: 28 days",
      image: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop",
      quote: "Mock tests adapt to my level perfectly. Started easy, now they're challenging me just right. My mom can see my daily progress on the parent dashboard!",
      feature: "🎯 Smart Mock Tests",
      dailyStat: "Completed 2 tests today",
      improvement: "65% → 78% accuracy"
    }
  ];

  const stats = [
    { number: "50,000+", label: "Students Trust Us" },
    { number: "98%", label: "Accuracy Rate" },
    { number: "24/7", label: "Always Available" },
    { number: "10x", label: "Faster Learning" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white overflow-x-hidden">
      {/* Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-blue-400 mr-3" />
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                Dhruv AI
              </h1>
              <span className="ml-3 text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded-full border border-green-400/30 font-semibold">
                ✓ Hallucination-Free
              </span>
            </div>

            {/* Desktop Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
              <a href="#testimonials" className="text-gray-300 hover:text-white transition-colors">Success Stories</a>
              <a href="#how-it-works" className="text-gray-300 hover:text-white transition-colors">How It Works</a>
            </div>

            {/* Mobile Menu Button & Auth Buttons */}
            <div className="flex items-center space-x-4">
              {/* Mobile Menu Toggle */}
              <button
                className="md:hidden text-gray-300 hover:text-white transition-colors p-2"
                onClick={() => setShowMobileMenu(!showMobileMenu)}
              >
                {showMobileMenu ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>

              {/* Auth Buttons */}
              <Link 
                to="/login" 
                className="hidden sm:block text-gray-300 hover:text-white transition-colors px-4 py-2 rounded-lg hover:bg-white/10"
              >
                Sign In
              </Link>
              <Link 
                to="/register" 
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 px-4 sm:px-6 py-2 rounded-lg font-semibold transition-all duration-300 text-sm sm:text-base flex items-center"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                <span className="sm:hidden">Start Free</span>
                <span className="hidden sm:inline">Start Free Today</span>
              </Link>
            </div>
          </div>
        </div>
        
        {/* Mobile Menu Dropdown */}
        {showMobileMenu && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-slate-900/95 backdrop-blur-md border-b border-white/10">
            <div className="max-w-7xl mx-auto px-6 py-4 space-y-4">
              <a 
                href="#features" 
                className="block text-gray-300 hover:text-white transition-colors py-2"
                onClick={() => setShowMobileMenu(false)}
              >
                Features
              </a>
              <a 
                href="#testimonials" 
                className="block text-gray-300 hover:text-white transition-colors py-2"
                onClick={() => setShowMobileMenu(false)}
              >
                Success Stories
              </a>
              <a 
                href="#how-it-works" 
                className="block text-gray-300 hover:text-white transition-colors py-2"
                onClick={() => setShowMobileMenu(false)}
              >
                How It Works
              </a>
              <div className="pt-2 border-t border-white/10 sm:hidden">
                <Link 
                  to="/login" 
                  className="block text-gray-300 hover:text-white transition-colors py-2"
                  onClick={() => setShowMobileMenu(false)}
                >
                  Sign In
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section - Student-Centric */}
      <section id="hero" className="relative min-h-screen flex items-center justify-center px-6 overflow-hidden pt-20">
        {/* Multi-Layer Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900"></div>
        <div className="absolute inset-0 bg-gradient-to-tr from-cyan-900/30 via-transparent to-pink-900/30"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-500/20 via-transparent to-transparent"></div>
        
        {/* Animated Mesh Gradient Overlay */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 -left-4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
          <div className="absolute top-0 -right-4 w-96 h-96 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
          <div className="absolute bottom-8 right-20 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-6000"></div>
        </div>
        
        {/* Animated Background Particles */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Large Floating Circles */}
          {[...Array(8)].map((_, i) => (
            <div
              key={`circle-${i}`}
              className="absolute rounded-full border-2 border-white/10 animate-float-slow"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                width: `${100 + Math.random() * 200}px`,
                height: `${100 + Math.random() * 200}px`,
                animationDelay: `${Math.random() * 8}s`,
                animationDuration: `${15 + Math.random() * 10}s`
              }}
            />
          ))}
          
          {/* Glowing Particles */}
          {[...Array(20)].map((_, i) => (
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
              <div className="w-2 h-2 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full opacity-70 animate-pulse shadow-lg shadow-cyan-500/50"></div>
            </div>
          ))}
          
          {/* Floating Icons */}
          {[...Array(6)].map((_, i) => (
            <div
              key={`icon-${i}`}
              className="absolute animate-float-slow opacity-20"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 10}s`,
                animationDuration: `${20 + Math.random() * 10}s`
              }}
            >
              {i % 3 === 0 && <Brain className="h-12 w-12 text-purple-400" />}
              {i % 3 === 1 && <BookOpen className="h-10 w-10 text-cyan-400" />}
              {i % 3 === 2 && <Target className="h-11 w-11 text-pink-400" />}
            </div>
          ))}
          
          {/* Animated Lines */}
          {[...Array(5)].map((_, i) => (
            <div
              key={`line-${i}`}
              className="absolute h-px bg-gradient-to-r from-transparent via-cyan-400/30 to-transparent animate-pulse"
              style={{
                left: '0',
                right: '0',
                top: `${20 + i * 15}%`,
                animationDelay: `${i * 0.5}s`,
                animationDuration: '3s'
              }}
            />
          ))}
        </div>

        <div className="relative z-10 max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Column - Emotional Connection */}
            <div className="text-center lg:text-left space-y-8">
              {/* HALLUCINATION-FREE Badge - Main USP */}
              <div className="inline-flex items-center bg-gradient-to-r from-green-500/30 to-emerald-500/30 border-2 border-green-400/60 rounded-full px-8 py-4 mb-6 backdrop-blur-md shadow-2xl shadow-green-500/30 animate-pulse-slow">
                <div className="relative">
                  <Shield className="h-7 w-7 text-green-400 mr-3" />
                  <div className="absolute inset-0 blur-lg bg-green-400/60 rounded-full animate-pulse"></div>
                  <CheckCircle className="absolute -top-1 -right-1 h-4 w-4 text-green-300 animate-bounce" />
                </div>
                <span className="text-green-100 text-base md:text-lg font-black tracking-wide">
                  🏆 World's First HALLUCINATION-FREE AI Tutor
                </span>
              </div>

              {/* Emotional Headline with Enhanced Styling */}
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-black mb-6 leading-[1.1]">
                <div className="relative inline-block">
                  <span className="bg-gradient-to-r from-white via-cyan-100 to-blue-100 bg-clip-text text-transparent drop-shadow-2xl">
                    Every Answer Verified.
                  </span>
                  <div className="absolute inset-0 blur-2xl bg-gradient-to-r from-cyan-500/20 to-blue-500/20 -z-10"></div>
                </div>
                <br />
                <div className="relative inline-block mt-2">
                  <span className="bg-gradient-to-r from-green-400 via-emerald-400 to-cyan-400 bg-clip-text text-transparent animate-gradient drop-shadow-2xl">
                    Learn with 100% Confidence.
                  </span>
                  <div className="absolute inset-0 blur-2xl bg-gradient-to-r from-green-500/20 via-emerald-500/20 to-cyan-500/20 -z-10"></div>
                </div>
              </h1>
              
              {/* Sub-headline emphasizing hallucination-free */}
              <p className="text-xl md:text-2xl text-blue-100 mb-8 font-semibold leading-relaxed">
                Unlike other AI tutors that make up answers, <span className="text-green-400 font-black">we verify everything</span> before teaching you.
              </p>

              {/* Enhanced Problem-Focused Sub-headline with Icons */}
              <div className="space-y-4 text-lg md:text-xl">
                <div className="flex items-center justify-center lg:justify-start space-x-3 bg-gradient-to-r from-amber-500/10 to-transparent px-6 py-3 rounded-2xl backdrop-blur-sm border border-amber-500/20">
                  <AlertCircle className="h-6 w-6 text-amber-400 flex-shrink-0 animate-pulse" />
                  <p className="text-blue-100">
                    <span className="text-amber-300 font-bold">11 PM doubt?</span> <span className="text-white">We're here.</span>
                  </p>
                </div>
                <div className="flex items-center justify-center lg:justify-start space-x-3 bg-gradient-to-r from-green-500/10 to-transparent px-6 py-3 rounded-2xl backdrop-blur-sm border border-green-500/20">
                  <FileText className="h-6 w-6 text-green-400 flex-shrink-0 animate-pulse animation-delay-1000" />
                  <p className="text-blue-100">
                    <span className="text-green-400 font-bold">Notes lost?</span> <span className="text-white">We organize them.</span>
                  </p>
                </div>
                <div className="flex items-center justify-center lg:justify-start space-x-3 bg-gradient-to-r from-blue-500/10 to-transparent px-6 py-3 rounded-2xl backdrop-blur-sm border border-blue-500/20">
                  <Heart className="h-6 w-6 text-blue-400 flex-shrink-0 animate-pulse animation-delay-2000" />
                  <p className="text-blue-100">
                    <span className="text-blue-300 font-bold">Exam stress?</span> <span className="text-white">We adapt to you.</span>
                  </p>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-6 justify-center lg:justify-start mb-12">
                <Link 
                  to="/register" 
                  className="group relative bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 px-10 py-5 rounded-2xl font-bold text-lg transition-all duration-500 transform hover:scale-110 shadow-2xl hover:shadow-green-500/40 text-white no-underline inline-block text-center overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-green-400 via-emerald-400 to-cyan-400 rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-500 blur-md"></div>
                  <div className="absolute inset-0 -skew-x-12 translate-x-full group-hover:translate-x-[-200%] bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-1000"></div>
                  
                  <span className="relative flex items-center justify-center">
                    <Sparkles className="mr-3 h-6 w-6 group-hover:rotate-12 transition-transform duration-300" />
                    Start Free - No Credit Card
                    <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-2 transition-transform duration-300" />
                  </span>
                </Link>
                
                <button className="group relative border-2 border-blue-400/50 hover:border-blue-300 px-10 py-5 rounded-2xl font-bold text-lg transition-all duration-500 backdrop-blur-sm hover:bg-blue-500/20 text-white overflow-hidden">
                  <span className="relative flex items-center justify-center">
                    <Play className="h-6 w-6 mr-3 group-hover:scale-110 transition-transform duration-300" />
                    See How It Works
                  </span>
                </button>
              </div>

              {/* Trust Indicators - Student Focused */}
              <div className="flex flex-wrap justify-center lg:justify-start items-center gap-6 text-blue-200 text-sm">
                <div className="flex items-center">
                  <Users className="h-4 w-4 text-green-400 mr-2" />
                  <span>50,000+ students like you</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-blue-400 mr-2" />
                  <span>100% Free to start</span>
                </div>
                <div className="flex items-center">
                  <Star className="h-4 w-4 text-yellow-400 mr-2" />
                  <span>4.9/5 rating</span>
                </div>
              </div>
            </div>

            {/* Right Column - 3D Card Stack with Stats */}
            <div className="relative">
              {/* Floating Elements Around Image */}
              <div className="absolute -top-6 -left-6 w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl rotate-12 animate-float opacity-80 shadow-2xl shadow-purple-500/50"></div>
              <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-2xl -rotate-12 animate-float animation-delay-2000 opacity-80 shadow-2xl shadow-cyan-500/50"></div>
              <div className="absolute top-1/2 -right-8 w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full animate-bounce opacity-80 shadow-2xl shadow-green-500/50"></div>
              
              {/* Main Image Card with 3D Effect */}
              <div className="relative rounded-3xl overflow-hidden shadow-2xl transform hover:scale-105 hover:rotate-1 transition-all duration-700 group bg-gradient-to-br from-purple-900/50 to-blue-900/50 p-1">
                <div className="relative rounded-3xl overflow-hidden">
                  <img 
                    src="https://images.unsplash.com/photo-1522661067900-ab829854a57f?w=800&h=600&fit=crop" 
                    alt="Students succeeding with AI learning" 
                    className="w-full h-96 lg:h-[500px] object-cover group-hover:scale-110 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-purple-900/90 via-blue-900/40 to-transparent"></div>
                  
                  {/* Floating Achievement Badges */}
                  <div className="absolute top-6 left-6 bg-gradient-to-r from-green-500/90 to-emerald-500/90 backdrop-blur-md px-4 py-2 rounded-full border border-white/30 shadow-lg animate-bounce-slow">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5 text-white" />
                      <span className="text-white font-bold text-sm">98% Success Rate</span>
                    </div>
                  </div>
                  
                  <div className="absolute top-20 right-6 bg-gradient-to-r from-amber-500/90 to-orange-500/90 backdrop-blur-md px-4 py-2 rounded-full border border-white/30 shadow-lg animate-bounce-slow animation-delay-1000">
                    <div className="flex items-center space-x-2">
                      <Star className="h-5 w-5 text-white animate-spin-slow" />
                      <span className="text-white font-bold text-sm">4.9★ Rating</span>
                    </div>
                  </div>
                  
                  {/* Enhanced Stats Card */}
                  <div className="absolute bottom-6 left-6 right-6">
                    <div className="bg-gradient-to-r from-purple-900/80 to-blue-900/80 backdrop-blur-2xl rounded-2xl p-6 border border-white/20 shadow-2xl">
                      <div className="grid grid-cols-3 gap-6 text-center">
                        <div className="transform hover:scale-110 transition-transform duration-300">
                          <div className="text-3xl font-black bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent mb-1">98%</div>
                          <div className="text-xs text-green-300 font-semibold">Accuracy</div>
                        </div>
                        <div className="transform hover:scale-110 transition-transform duration-300">
                          <div className="text-3xl font-black bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent mb-1">24/7</div>
                          <div className="text-xs text-amber-300 font-semibold">Available</div>
                        </div>
                        <div className="transform hover:scale-110 transition-transform duration-300">
                          <div className="text-3xl font-black bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent mb-1">10x</div>
                          <div className="text-xs text-cyan-300 font-semibold">Faster</div>
                        </div>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="mt-4 space-y-2">
                        <div className="flex justify-between text-xs text-gray-300">
                          <span>Student Success</span>
                          <span>98%</span>
                        </div>
                        <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-green-400 to-emerald-400 rounded-full animate-progress" style={{width: '98%'}}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Glow Effect */}
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                </div>
              </div>
              
              {/* Decorative Elements */}
              <div className="absolute -z-10 inset-0 bg-gradient-to-r from-purple-600/20 to-cyan-600/20 blur-3xl rounded-3xl"></div>
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

      {/* Pain Points Section */}
      <section id="pain-points" className="py-24 px-6 relative bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
              Sound Familiar?
            </h2>
            <p className="text-xl text-blue-200 max-w-3xl mx-auto">
              You're not alone. Every serious student faces these challenges.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {painPoints.map((point, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-red-900/20 to-orange-900/20 border border-red-400/20 rounded-2xl p-6 backdrop-blur-sm hover:border-red-400/40 transition-all duration-300 transform hover:scale-105"
              >
                <div className="text-5xl mb-4">{point.emoji}</div>
                <h3 className="text-xl font-bold text-red-300 mb-3">{point.title}</h3>
                <p className="text-gray-300 mb-4 leading-relaxed">{point.description}</p>
                <div className="bg-red-900/30 px-3 py-2 rounded-lg border border-red-400/20">
                  <p className="text-xs text-red-200">{point.stat}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Emotional Connection */}
          <div className="text-center mt-12">
            <div className="inline-block bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-400/30 px-8 py-4 rounded-2xl backdrop-blur-sm">
              <p className="text-lg text-red-200 font-semibold">
                We built Dhruv AI because we've been there. We understand.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Hallucination-Free Guarantee Section */}
      <section id="hallucination-free" className="py-24 px-6 relative">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 bg-clip-text text-transparent">
              Other AI Tutors vs Dhruv AI
            </h2>
            <p className="text-xl text-blue-200">
              Why hallucination-free matters for your success
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Other AI - Problem */}
            <div className="bg-gradient-to-br from-red-900/30 to-orange-900/30 border-2 border-red-400/30 rounded-3xl p-8 backdrop-blur-sm">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mr-4">
                  <AlertCircle className="h-7 w-7 text-red-400" />
                </div>
                <h3 className="text-2xl font-bold text-red-300">ChatGPT, Gemini & Others</h3>
              </div>
              
              <div className="space-y-4 mb-6">
                <div className="flex items-start">
                  <X className="h-5 w-5 text-red-400 mr-3 flex-shrink-0 mt-1" />
                  <p className="text-gray-300"><strong className="text-red-400">Makes up fake answers</strong> but sounds confident</p>
                </div>
                <div className="flex items-start">
                  <X className="h-5 w-5 text-red-400 mr-3 flex-shrink-0 mt-1" />
                  <p className="text-gray-300"><strong className="text-red-400">Wrong formulas</strong> and concepts</p>
                </div>
                <div className="flex items-start">
                  <X className="h-5 w-5 text-red-400 mr-3 flex-shrink-0 mt-1" />
                  <p className="text-gray-300"><strong className="text-red-400">No verification</strong> - you learn mistakes</p>
                </div>
                <div className="flex items-start">
                  <X className="h-5 w-5 text-red-400 mr-3 flex-shrink-0 mt-1" />
                  <p className="text-gray-300"><strong className="text-red-400">Your exam score suffers</strong></p>
                </div>
              </div>

              <div className="bg-red-900/30 border border-red-400/30 px-4 py-3 rounded-xl">
                <p className="text-red-200 text-sm font-semibold text-center">
                  ⚠️ Hallucinations = Learning Wrong Information
                </p>
              </div>
            </div>

            {/* Dhruv AI - Solution */}
            <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border-2 border-green-400/50 rounded-3xl p-8 backdrop-blur-sm relative overflow-hidden">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-emerald-500/10 animate-pulse-slow"></div>
              
              <div className="relative z-10">
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-green-500/30 rounded-full flex items-center justify-center mr-4 relative">
                    <Shield className="h-7 w-7 text-green-400 animate-pulse" />
                    <CheckCircle className="absolute -top-1 -right-1 h-5 w-5 text-green-300" />
                  </div>
                  <h3 className="text-2xl font-bold text-green-300">Dhruv AI</h3>
                  <div className="ml-auto bg-green-500/20 px-3 py-1 rounded-full border border-green-400/30">
                    <span className="text-green-300 text-xs font-bold">HALLUCINATION-FREE</span>
                  </div>
                </div>
                
                <div className="space-y-4 mb-6">
                  <div className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                    <p className="text-white"><strong className="text-green-400">Every answer verified</strong> before showing you</p>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                    <p className="text-white"><strong className="text-green-400">100% accurate</strong> formulas and concepts</p>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                    <p className="text-white"><strong className="text-green-400">Cross-checked</strong> against verified sources</p>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                    <p className="text-white"><strong className="text-green-400">Your confidence grows</strong> with correct learning</p>
                  </div>
                </div>

                <div className="bg-green-900/30 border border-green-400/50 px-4 py-3 rounded-xl">
                  <p className="text-green-200 text-sm font-semibold text-center">
                    ✓ Trust Every Answer - Learn with Confidence
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom CTA */}
          <div className="text-center mt-12">
            <div className="inline-block bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-400/40 px-8 py-4 rounded-2xl backdrop-blur-md">
              <p className="text-green-200 font-semibold text-lg">
                🎯 The only AI tutor you can trust for 100% accurate learning
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section id="features" className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
              Here's How We Help You Win
            </h2>
            <p className="text-xl text-blue-200 max-w-3xl mx-auto">
              Four AI-powered tools designed specifically for serious students like you
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {solutions.map((solution, index) => (
              <div
                key={index}
                className="group relative bg-gradient-to-br from-blue-900/30 to-indigo-900/30 border border-blue-400/20 rounded-3xl p-8 backdrop-blur-sm hover:border-blue-400/40 transition-all duration-500 transform hover:scale-105"
              >
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-r ${solution.color} mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <solution.icon className="h-8 w-8 text-white" />
                </div>
                
                <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-blue-200 transition-colors">
                  {solution.title}
                </h3>
                
                <p className="text-gray-300 mb-6 leading-relaxed">
                  {solution.description}
                </p>

                <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-400/30 px-4 py-3 rounded-xl">
                  <div className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" />
                    <p className="text-green-300 font-semibold text-sm">{solution.benefit}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof - Daily Progress Stories */}
      <section id="testimonials" className="py-24 px-6 relative bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
              See How Students Progress Daily
            </h2>
            <p className="text-xl text-blue-200 max-w-3xl mx-auto">
              Real students. Real daily improvements. Real features helping them succeed.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 border border-purple-400/20 rounded-3xl p-8 backdrop-blur-sm hover:border-purple-400/40 transition-all duration-300 transform hover:scale-105"
              >
                {/* Student Info */}
                <div className="flex items-center mb-6">
                  <img 
                    src={testimonial.image} 
                    alt={testimonial.name}
                    className="w-16 h-16 rounded-full border-2 border-purple-400/50 mr-4 object-cover"
                  />
                  <div>
                    <h4 className="font-bold text-white text-lg">{testimonial.name}</h4>
                    <p className="text-sm text-purple-300">{testimonial.grade}</p>
                    <p className="text-xs text-cyan-400 font-semibold flex items-center mt-1">
                      <Clock className="h-3 w-3 mr-1" />
                      {testimonial.progress}
                    </p>
                  </div>
                </div>

                {/* Feature Badge */}
                <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-400/30 px-4 py-2 rounded-xl mb-4 inline-block">
                  <span className="text-blue-300 font-semibold text-sm">{testimonial.feature}</span>
                </div>

                {/* Quote */}
                <p className="text-gray-300 mb-4 leading-relaxed">
                  "{testimonial.quote}"
                </p>

                {/* Daily Activity */}
                <div className="bg-amber-500/10 border border-amber-400/30 px-4 py-2 rounded-lg mb-3">
                  <div className="flex items-center">
                    <Zap className="h-4 w-4 text-amber-400 mr-2" />
                    <span className="text-amber-300 font-semibold text-sm">{testimonial.dailyStat}</span>
                  </div>
                </div>

                {/* Overall Improvement */}
                <div className="bg-green-500/20 border border-green-400/30 px-4 py-2 rounded-lg inline-block">
                  <div className="flex items-center">
                    <TrendingUp className="h-4 w-4 text-green-400 mr-2" />
                    <span className="text-green-300 font-semibold text-sm">{testimonial.improvement}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Stats Bar */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent mb-2">
                  {stat.number}
                </div>
                <div className="text-blue-200">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6 relative">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Get Started in 3 Simple Steps
            </h2>
            <p className="text-xl text-blue-200">
              No complicated setup. Start learning in under 2 minutes.
            </p>
          </div>

          <div className="space-y-8">
            {[
              {
                step: "1",
                title: "Sign Up Free",
                description: "No credit card needed. Start with our free plan and explore all features.",
                icon: UserPlus,
                color: "from-blue-500 to-cyan-500"
              },
              {
                step: "2",
                title: "Ask Your First Question or Upload Notes",
                description: "Have a doubt? Ask the AI tutor. Need organized notes? Upload your lecture recordings.",
                icon: MessageCircle,
                color: "from-purple-500 to-pink-500"
              },
              {
                step: "3",
                title: "Watch Your Performance Improve",
                description: "Track your progress, take adaptive mock tests, and see real improvement in weeks.",
                icon: TrendingUp,
                color: "from-green-500 to-emerald-500"
              }
            ].map((item, index) => (
              <div
                key={index}
                className="flex flex-col md:flex-row items-center gap-8 bg-gradient-to-br from-blue-900/30 to-indigo-900/30 border border-blue-400/20 rounded-3xl p-8 backdrop-blur-sm hover:border-blue-400/40 transition-all duration-300"
              >
                <div className={`flex-shrink-0 w-20 h-20 rounded-2xl bg-gradient-to-r ${item.color} flex items-center justify-center text-3xl font-bold text-white`}>
                  {item.step}
                </div>
                <div className="flex-grow text-center md:text-left">
                  <h3 className="text-2xl font-bold text-white mb-3">{item.title}</h3>
                  <p className="text-gray-300 leading-relaxed">{item.description}</p>
                </div>
                <item.icon className="h-12 w-12 text-blue-400 flex-shrink-0" />
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link 
              to="/register"
              className="inline-block bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 px-12 py-5 rounded-2xl font-bold text-xl transition-all duration-300 transform hover:scale-110 shadow-2xl hover:shadow-green-500/40 text-white no-underline"
            >
              Start Your Free Journey Now →
            </Link>
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="py-16 px-6 relative bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div className="bg-green-500/10 border border-green-400/20 rounded-2xl p-6 backdrop-blur-sm">
              <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Hallucination-Free AI</h3>
              <p className="text-gray-300">Every answer is verified. No fake information.</p>
            </div>
            <div className="bg-blue-500/10 border border-blue-400/20 rounded-2xl p-6 backdrop-blur-sm">
              <Shield className="h-12 w-12 text-blue-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">NCERT-Aligned Content</h3>
              <p className="text-gray-300">All content verified against official syllabus.</p>
            </div>
            <div className="bg-purple-500/10 border border-purple-400/20 rounded-2xl p-6 backdrop-blur-sm">
              <Lock className="h-12 w-12 text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">100% Private & Secure</h3>
              <p className="text-gray-300">Your data is encrypted and never shared.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section - Repositioned at Bottom with Better Framing */}
      <section id="pricing" className="py-24 px-6 relative">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Choose Your Learning Journey
            </h2>
            <p className="text-xl text-blue-200 max-w-3xl mx-auto mb-4">
              Start free. Upgrade only when you're ready.
            </p>
            <div className="inline-flex items-center bg-green-500/20 border border-green-400/30 px-6 py-3 rounded-full">
              <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
              <span className="text-green-300 font-semibold">No credit card required to start</span>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Free Plan */}
            <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-gray-600/30 rounded-3xl p-8 backdrop-blur-sm">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-4">Free</h3>
                <div className="text-5xl font-bold text-white mb-2">₹0</div>
                <p className="text-gray-400">Perfect for trying out</p>
              </div>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-300">5 AI tutor queries daily</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-300">2 mock tests weekly</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-300">1 file upload daily</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-300">Basic progress tracking</span>
                </div>
              </div>

              <Link
                to="/register"
                className="block w-full text-center bg-slate-700 hover:bg-slate-600 text-white px-6 py-4 rounded-xl font-semibold transition-all duration-300 no-underline"
              >
                Start Free
              </Link>
              <p className="text-center text-xs text-gray-400 mt-3">No credit card needed</p>
            </div>

            {/* Scholar Plan - Most Popular */}
            <div className="relative bg-gradient-to-br from-blue-900/50 to-indigo-900/50 border-2 border-blue-400 rounded-3xl p-8 backdrop-blur-sm transform scale-105 shadow-2xl">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-2 rounded-full border border-blue-400 shadow-lg">
                  <span className="text-white font-bold text-sm">⭐ Most Popular</span>
                </div>
              </div>

              <div className="text-center mb-8 mt-4">
                <h3 className="text-2xl font-bold text-white mb-4">{PLANS_CONFIG.SCHOLAR.short_name}</h3>
                <div className="text-5xl font-bold text-white mb-2">
                  {formatPrice(PLANS_CONFIG.SCHOLAR.price_monthly)}
                  <span className="text-lg text-blue-300">/month</span>
                </div>
                <p className="text-blue-300">{PLANS_CONFIG.SCHOLAR.tagline}</p>
                <p className="text-xs text-green-400 mt-2">Less than ₹17/day - cheaper than a coffee!</p>
              </div>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white font-semibold">{PLANS_CONFIG.SCHOLAR.features.ai_sessions_monthly} AI sessions/month</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">{PLANS_CONFIG.SCHOLAR.features.mock_tests_weekly} mock tests weekly</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">Unlimited auto-notes & uploads</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">Advanced analytics & insights</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">{PLANS_CONFIG.SCHOLAR.features.mentor_tips_daily} mentor tips daily</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">Concept tagging & tracking</span>
                </div>
              </div>

              <Link
                to="/register"
                className="block w-full text-center bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-4 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 no-underline"
              >
                Start {PLANS_CONFIG.SCHOLAR.short_name}
              </Link>
              <p className="text-center text-xs text-blue-300 mt-3">Start free → Upgrade anytime</p>
            </div>

            {/* Achiever Plan */}
            <div className="bg-gradient-to-br from-purple-900/50 to-indigo-900/50 border border-purple-400/30 rounded-3xl p-8 backdrop-blur-sm">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-4">{PLANS_CONFIG.ACHIEVER.short_name}</h3>
                <div className="text-5xl font-bold text-white mb-2">
                  {formatPrice(PLANS_CONFIG.ACHIEVER.price_monthly)}
                  <span className="text-lg text-purple-300">/month</span>
                </div>
                <p className="text-purple-300">For top rankers</p>
              </div>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start">
                  <Star className="h-5 w-5 text-yellow-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white font-semibold">Everything in Scholar</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">{PLANS_CONFIG.ACHIEVER.features.ai_sessions_monthly} AI sessions/month</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">Unlimited mock tests</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">Priority AI support</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">Voice mode & offline access</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">Deep analytics & reports</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-white">Priority AI model access</span>
                </div>
              </div>

              <Link
                to="/register"
                className="block w-full text-center bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white px-6 py-4 rounded-xl font-semibold transition-all duration-300 no-underline"
              >
                Start Pro
              </Link>
              <p className="text-center text-xs text-purple-300 mt-3">Start free → Upgrade anytime</p>
            </div>
          </div>

          {/* Pricing Note */}
          <div className="text-center mt-12">
            <p className="text-blue-200 text-sm">
              💡 All plans include our hallucination-free AI guarantee and 100% verified content
            </p>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 px-6 relative">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
            Join 50,000+ Students Crushing Their Goals
          </h2>
          <p className="text-xl text-blue-200 mb-12">
            Start free. No credit card required. Cancel anytime.
          </p>

          <Link
            to="/register"
            className="inline-block bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 px-16 py-6 rounded-2xl font-bold text-2xl transition-all duration-300 transform hover:scale-110 shadow-2xl hover:shadow-green-500/40 text-white no-underline"
          >
            Start Your Free Journey Now →
          </Link>

          <p className="text-blue-300 mt-8 text-sm">
            Takes less than 2 minutes. No credit card needed.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            {/* Brand */}
            <div className="md:col-span-2">
              <div className="flex items-center mb-4">
                <Brain className="h-8 w-8 text-blue-400 mr-3" />
                <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                  Dhruv AI
                </h3>
              </div>
              <p className="text-gray-400 mb-4">
                Your 24/7 AI study companion for every student. From school to competitive exams - learn verified, study smart, succeed faster.
              </p>
              <div className="flex space-x-4">
                <Shield className="h-5 w-5 text-green-400" />
                <span className="text-sm text-gray-400">World's First Hallucination-Free AI</span>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="font-bold text-white mb-4">Product</h4>
              <div className="space-y-2">
                <a href="#features" className="block text-gray-300 hover:text-blue-400 transition-colors">Features</a>
                <a href="#testimonials" className="block text-gray-300 hover:text-blue-400 transition-colors">Success Stories</a>
                <a href="#pricing" className="block text-gray-300 hover:text-blue-400 transition-colors">Pricing</a>
                <a href="#how-it-works" className="block text-gray-300 hover:text-blue-400 transition-colors">How It Works</a>
              </div>
            </div>

            {/* Support */}
            <div>
              <h4 className="font-bold text-white mb-4">Legal & Support</h4>
              <div className="space-y-2">
                <Link to="/policies/contact" className="block text-gray-300 hover:text-blue-400 transition-colors">Contact Us</Link>
                <Link to="/policies/privacy" className="block text-gray-300 hover:text-blue-400 transition-colors">Privacy Policy</Link>
                <Link to="/policies/terms" className="block text-gray-300 hover:text-blue-400 transition-colors">Terms & Conditions</Link>
                <Link to="/policies/refund" className="block text-gray-300 hover:text-blue-400 transition-colors">Refund Policy</Link>
                <Link to="/policies/shipping" className="block text-gray-300 hover:text-blue-400 transition-colors">Shipping Policy</Link>
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm mb-4 md:mb-0">
              © 2024 Dhruv AI. Built for students, by educators who care.
            </p>
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-sm text-gray-400">
                <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                <span>Trusted by 50,000+ students</span>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* Custom CSS for Animations */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          25% { transform: translateY(-20px) translateX(10px); }
          50% { transform: translateY(-10px) translateX(-10px); }
          75% { transform: translateY(-25px) translateX(5px); }
        }

        @keyframes float-slow {
          0%, 100% { transform: translateY(0px) translateX(0px) rotate(0deg); }
          25% { transform: translateY(-30px) translateX(20px) rotate(5deg); }
          50% { transform: translateY(-15px) translateX(-20px) rotate(-5deg); }
          75% { transform: translateY(-35px) translateX(10px) rotate(3deg); }
        }

        @keyframes blob {
          0%, 100% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }

        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }

        @keyframes progress {
          0% { width: 0%; }
          100% { width: 98%; }
        }

        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes pulse-slow {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.8;
            transform: scale(1.05);
          }
        }

        .animate-float {
          animation: float linear infinite;
        }

        .animate-float-slow {
          animation: float-slow linear infinite;
        }

        .animate-blob {
          animation: blob 7s infinite;
        }

        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 6s ease infinite;
        }

        .animate-progress {
          animation: progress 2s ease-out;
        }

        .animate-bounce-slow {
          animation: bounce-slow 3s ease-in-out infinite;
        }

        .animate-spin-slow {
          animation: spin-slow 8s linear infinite;
        }

        .animate-pulse-slow {
          animation: pulse-slow 4s ease-in-out infinite;
        }

        .delay-300 {
          animation-delay: 300ms;
        }

        .delay-700 {
          animation-delay: 700ms;
        }

        .delay-1000,
        .animation-delay-1000 {
          animation-delay: 1s;
        }

        .delay-2000,
        .animation-delay-2000 {
          animation-delay: 2s;
        }

        .animation-delay-4000 {
          animation-delay: 4s;
        }

        .animation-delay-6000 {
          animation-delay: 6s;
        }
      `}</style>
    </div>
  );
};

const UserPlus = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
  </svg>
);

export default LandingPage;