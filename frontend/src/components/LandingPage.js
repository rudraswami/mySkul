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
  UserPlus
} from 'lucide-react';

const LandingPage = () => {
  const [scrollY, setScrollY] = useState(0);
  const [isVisible, setIsVisible] = useState({});

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
        
        {/* Floating Elements Animation */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className={`absolute animate-float w-2 h-2 bg-blue-400/30 rounded-full`}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${3 + Math.random() * 4}s`
              }}
            ></div>
          ))}
        </div>

        <div className="relative z-10 max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Text Content */}
            <div className="text-center lg:text-left">
              {/* Verification Badge */}
              <div className="inline-flex items-center bg-green-500/20 border border-green-400/30 rounded-full px-6 py-2 mb-8 backdrop-blur-sm">
                <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                <span className="text-green-300 text-sm font-medium">100% Hallucination-Free AI • Verified Answers</span>
              </div>

              {/* Main Headline */}
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-blue-100 to-indigo-200 bg-clip-text text-transparent leading-tight">
                Dhruv AI
                <br />
                <span className="text-3xl md:text-5xl lg:text-6xl bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                  Your Verified AI Mentor
                </span>
              </h1>

              {/* Sub-headline */}
              <p className="text-lg md:text-xl lg:text-2xl text-blue-100 mb-12 leading-relaxed">
                Hallucination-free, personalised learning. Turn any class into verified notes, flashcards, and adaptive tests — <span className="text-yellow-400 font-semibold">instantly.</span>
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-6 justify-center lg:justify-start mb-12">
                <Link 
                  to="/register" 
                  className="group relative bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-blue-500/25 text-white no-underline inline-block text-center"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-xl opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                  <span className="relative flex items-center justify-center">
                    <UserPlus className="mr-2 h-5 w-5" />
                    Try Free Now
                    <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Link>
                
                <Link 
                  to="/login" 
                  className="group border-2 border-blue-400/50 hover:border-blue-400 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 backdrop-blur-sm hover:bg-blue-500/10 text-white no-underline inline-block text-center"
                >
                  <span className="flex items-center justify-center">
                    <LogIn className="mr-2 h-5 w-5" />
                    Sign In
                  </span>
                </Link>
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

            {/* Right Column - Hero Image */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl transform hover:scale-105 transition-transform duration-500">
                <img 
                  src="https://images.unsplash.com/photo-1541178735493-479c1a27ed24" 
                  alt="Student learning with AI technology" 
                  className="w-full h-96 lg:h-[500px] object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-blue-900/80 via-blue-600/20 to-transparent"></div>
                <div className="absolute bottom-6 left-6 right-6">
                  <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
                    <div className="flex items-center justify-between text-white">
                      <div>
                        <p className="text-sm text-blue-200">✓ Live AI Analysis</p>
                        <p className="font-semibold">Generating verified notes...</p>
                      </div>
                      <div className="animate-pulse">
                        <Brain className="h-6 w-6 text-blue-400" />
                      </div>
                    </div>
                  </div>
                </div>
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
                  The Learning Crisis
                </h3>
                <div className="space-y-4 text-red-100">
                  <p>• Students waste <strong className="text-red-300">hours rewriting notes</strong></p>
                  <p>• Unreliable AI gives <strong className="text-red-300">wrong answers</strong></p>
                  <p>• Traditional tutoring costs <strong className="text-red-300">₹50,000+ per year</strong></p>
                  <p>• No personalized learning path</p>
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
                  <p>• <strong className="text-green-300">Verified, hallucination-free</strong> answers</p>
                  <p>• <strong className="text-green-300">Instant note generation</strong> from any lecture</p>
                  <p>• <strong className="text-green-300">₹499/month</strong> - 99% cost reduction</p>
                  <p>• Adaptive learning with dual AI mentorship</p>
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
                description: "Record or upload. Get verified notes & flashcards in seconds.",
                color: "from-purple-500 to-pink-500",
                bgColor: "purple-500/10"
              },
              {
                icon: Target,
                title: "Adaptive Mock Tests",
                emoji: "🧩",
                description: "Tests that evolve with you – not against you.",
                color: "from-blue-500 to-cyan-500",
                bgColor: "blue-500/10"
              },
              {
                icon: BarChart3,
                title: "Mastery Map",
                emoji: "📊",
                description: "See what you've mastered and what needs attention.",
                color: "from-green-500 to-emerald-500",
                bgColor: "green-500/10"
              },
              {
                icon: Heart,
                title: "Verified Mentor",
                emoji: "🤖",
                description: "Empathy + Accuracy = Perfect Guidance.",
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
            Watch Dhruv AI in Action
          </h2>
          <p className="text-xl text-blue-200 mb-12 max-w-3xl mx-auto">
            See how a real lecture becomes structured, verified notes + flashcards in under 60 seconds
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
                name: "Aditi Sharma",
                role: "NEET Aspirant, Delhi",
                quote: "Finally, an AI that explains AND verifies. My Biology scores improved 40% in 2 months!",
                rating: 5,
                image: "👩‍🎓"
              },
              {
                name: "Rohit Patel",
                role: "JEE Student, Mumbai",
                quote: "It feels like a real coach guiding me. The adaptive tests know exactly where I struggle.",
                rating: 5,
                image: "👨‍💻"
              },
              {
                name: "Priya Gupta",
                role: "UPSC Aspirant, Chennai",
                quote: "Dhruv AI turned my chaotic study notes into organized, verified knowledge. Game changer!",
                rating: 5,
                image: "📚"
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
                period: "Forever",
                description: "Perfect for trying out Dhruv AI",
                features: [
                  "5 verified answers per day",
                  "Basic note generation",
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
                period: "per month",
                description: "Best for serious students",
                features: [
                  "Unlimited verified answers",
                  "Advanced note generation",
                  "Mock tests & analytics",
                  "Priority support",
                  "Offline access"
                ],
                cta: "Start Premium",
                popular: true,
                color: "blue"
              },
              {
                name: "Pro",
                price: "₹999",
                period: "per month",
                description: "For competitive exam preparation",
                features: [
                  "Everything in Premium",
                  "Custom AI agent",
                  "1M context window",
                  "Advanced analytics",
                  "1-on-1 mentorship calls"
                ],
                cta: "Go Pro",
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

                <p className="text-center text-gray-400 text-sm mt-4">
                  Start Free → Upgrade Anytime
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust & Tech Section */}
      <section id="trust" className="py-24 px-6 relative">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-12 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
            Built on Accuracy, Privacy & AI Ethics
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: "Verified by Design",
                description: "Our dual-layer AI architecture ensures 100% accurate, hallucination-free responses."
              },
              {
                icon: Lock,
                title: "Secure & Private",
                description: "Your data is encrypted and never shared. Full compliance with Indian data protection laws."
              },
              {
                icon: Eye,
                title: "Transparent AI",
                description: "We show our reasoning process. No black box - you understand how every answer is generated."
              }
            ].map((item, index) => (
              <div key={index} className="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-sm">
                <div className="bg-gradient-to-br from-green-500/20 to-blue-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                  <item.icon className="h-8 w-8 text-green-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-4">{item.title}</h3>
                <p className="text-gray-300 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section id="final-cta" className="py-24 px-6 relative">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border border-blue-400/30 rounded-3xl p-12 backdrop-blur-sm">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Ready to Automate Your Learning Journey?
            </h2>
            <p className="text-xl text-blue-200 mb-8 leading-relaxed">
              Join thousands of students who've transformed their studies with AI-powered learning
            </p>
            
            <Link 
              to="/register"
              className="group bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 px-12 py-4 rounded-xl font-bold text-xl transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-blue-500/25 text-white no-underline inline-block"
            >
              <span className="flex items-center justify-center">
                Get Started with Dhruv AI
                <Zap className="ml-3 h-6 w-6 group-hover:rotate-12 transition-transform" />
              </span>
            </Link>

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

      {/* Custom Styles */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        .animate-float {
          animation: float 6s ease-in-out infinite;
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

        /* Custom gradient backgrounds */
        .bg-gradient-conic {
          background: conic-gradient(from 0deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6);
        }
      `}</style>
    </div>
  );
};

export default LandingPage;