import React from 'react';
import { BookOpen, Zap, Brain, TrendingUp, Award, Users } from 'lucide-react';
import '../../styles/auth.css';

export default function PremiumShowcase() {
  const features = [
    {
      icon: <Brain className="h-8 w-8 text-white" />,
      title: "Hallucination-Free AI Mentor",
      description: "Get accurate, exam-focused guidance powered by advanced reasoning",
      gradient: "from-purple-500 to-indigo-600",
      delay: ""
    },
    {
      icon: <Zap className="h-8 w-8 text-white" />,
      title: "Unlimited Sessions",
      description: "Practice as much as you need. No limits on your learning journey",
      gradient: "from-blue-500 to-cyan-600",
      delay: "animate-float-delay-1"
    },
    {
      icon: <TrendingUp className="h-8 w-8 text-white" />,
      title: "Advanced Mock Tests",
      description: "Realistic exam simulations with detailed analytics",
      gradient: "from-pink-500 to-rose-600",
      delay: "animate-float-delay-2"
    },
    {
      icon: <BookOpen className="h-8 w-8 text-white" />,
      title: "Smart Auto-Notes",
      description: "Transform lectures into structured, exam-ready notes",
      gradient: "from-green-500 to-emerald-600",
      delay: ""
    },
    {
      icon: <Award className="h-8 w-8 text-white" />,
      title: "Progress Tracking",
      description: "Monitor your improvement with intelligent insights",
      gradient: "from-yellow-500 to-orange-600",
      delay: "animate-float-delay-1"
    },
    {
      icon: <Users className="h-8 w-8 text-white" />,
      title: "Personalized Learning",
      description: "Adaptive content that matches your exam goals",
      gradient: "from-red-500 to-pink-600",
      delay: "animate-float-delay-2"
    }
  ];

  return (
    <div className="hidden lg:flex lg:flex-1 flex-col justify-center items-center p-12 gradient-animated relative overflow-hidden">
      {/* Decorative blobs */}
      <div className="absolute top-10 left-10 w-72 h-72 bg-white/10 rounded-full blur-3xl animate-float"></div>
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-float-slow"></div>
      
      <div className="relative z-10 w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-12 fade-in">
          <h1 className="text-5xl font-bold text-white mb-4">
            Welcome to <span className="text-yellow-300">Dhruv AI</span>
          </h1>
          <p className="text-xl text-white/90 font-light">
            Your AI-powered learning companion for JEE, NEET & UPSC
          </p>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className={`glass-card-dark rounded-2xl p-6 feature-card ${feature.delay} fade-in-delay-${index % 3 + 1}`}
            >
              <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.gradient} mb-4 pulse-glow`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-white/80 text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Stats/Social Proof */}
        <div className="grid grid-cols-3 gap-6 mt-12 fade-in-delay-3">
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-1">50K+</div>
            <div className="text-white/70 text-sm">Active Students</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-1">1M+</div>
            <div className="text-white/70 text-sm">AI Sessions</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-1">95%</div>
            <div className="text-white/70 text-sm">Success Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
}
