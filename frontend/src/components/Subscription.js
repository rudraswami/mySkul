import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { LoadingSpinner } from './ui/loading';
import RazorpayPayment from './RazorpayPayment';
import { 
  Crown, 
  Check, 
  CreditCard, 
  Zap,
  Star,
  Calendar,
  Sparkles,
  ArrowRight,
  Clock,
  X,
  Infinity,
  Rocket,
  Brain,
  Target,
  TrendingUp,
  Shield,
  Gift
} from 'lucide-react';

// #PHASE3-SECURITY-FRONTEND - React Query Migration
import { 
  useCurrentSubscription, 
  useSubscriptionPlans, 
  useSubscriptionInfo,
  useUpgradeSubscription
} from '../hooks/useSubscription';

// Import centralized plans configuration
import { PLANS_CONFIG, getAllPlans } from '../config/plans';

export default function Subscription() {
  const { user } = useAuth();
  
  // #PHASE3-SECURITY-FRONTEND - Replace useState/useEffect with React Query hooks
  const { 
    data: currentSubscription, 
    isLoading: loading, 
    error: subscriptionError 
  } = useCurrentSubscription();
  
  const { 
    data: subscriptionInfo, 
    isLoading: infoLoading 
  } = useSubscriptionInfo();
  
  const { 
    data: plansData, 
    isLoading: plansLoading 
  } = useSubscriptionPlans();
  
  const upgradeSubscriptionMutation = useUpgradeSubscription();
  
  const [upgrading, setUpgrading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentDetails, setPaymentDetails] = useState(null);

  const handleUpgrade = async (planTier, cycle = 'monthly') => {
    setUpgrading(true);
    setSelectedPlan(planTier);
    
    // Use plansData from React Query instead of hardcoded subscriptionPlans
    const plan = plansData?.plans?.find(p => p.tier === planTier) || 
                 subscriptionPlans.find(p => p.tier === planTier);
    if (!plan) {
      console.error('Plan not found');
      setUpgrading(false);
      setSelectedPlan(null);
      return;
    }

    // Calculate amount based on billing cycle
    const amount = cycle === 'yearly' ? plan.price_yearly : plan.price_monthly;
    
    // Set payment details and show modal
    setPaymentDetails({
      planName: plan.name,
      planTier: planTier,
      billingCycle: cycle,
      amount: amount,
      userDetails: {
        user_id: user?.user_id,
        name: user?.name,
        email: user?.email,
        phone: user?.phone
      }
    });
    
    setShowPaymentModal(true);
    setUpgrading(false);
  };

  const handlePaymentSuccess = (paymentData) => {
    console.log('Payment successful:', paymentData);
    setShowPaymentModal(false);
    setPaymentDetails(null);
    
    // Refresh subscription data using React Query
    // The useUpgradeSubscription hook already handles query invalidation
    
    // Show success message or redirect
    alert('Subscription upgraded successfully!');
  };

  const handlePaymentError = (error) => {
    console.error('Payment error:', error);
    alert(`Payment failed: ${error}`);
  };

  const handlePaymentCancel = () => {
    console.log('Payment cancelled by user');
    setShowPaymentModal(false);
    setPaymentDetails(null);
  };

  // Use centralized plans configuration
  const subscriptionPlans = getAllPlans().map(plan => ({
    name: plan.short_name,
    price_monthly: plan.price_monthly,
    price_yearly: plan.price_yearly,
    price_quarterly: plan.price_quarterly,
    features: formatPlanFeatures(plan),
    current: currentSubscription?.plan_name === plan.id,
    popular: plan.highlight,
    tier: plan.id,
    badge: plan.badge,
    tagline: plan.tagline,
    emoji: plan.emoji,
    color: plan.color
  }));

  // Helper function to format plan features for display - UPDATED FOR 3-TIER STRUCTURE
  function formatPlanFeatures(plan) {
    const features = [];
    const { features: planFeatures } = plan;
    
    if (plan.id === 'FREE') {
      features.push({
        icon: '🎯',
        text: `${planFeatures.ai_sessions_monthly || 10} AI sessions monthly`,
        subtext: 'Perfect for trying out'
      });
      features.push({
        icon: '📝',
        text: `${planFeatures.mock_tests_weekly || 1} mock test weekly`,
        subtext: 'Build confidence'
      });
      features.push({
        icon: '📁',
        text: `${planFeatures.auto_note_uploads_daily || 1} file upload daily`,
        subtext: 'Try note generation'
      });
      features.push({
        icon: '📊',
        text: 'Basic analytics',
        subtext: 'See your progress'
      });
    } else if (plan.id === 'STUDENT') {
      features.push({
        icon: '🚀',
        text: 'Unlimited AI Tutor sessions',
        subtext: 'Ask anything, anytime - No limits!'
      });
      features.push({
        icon: '💡',
        text: '5 mentor tips daily',
        subtext: 'Daily motivation & study hacks'
      });
      features.push({
        icon: '📝',
        text: '3 mock tests weekly',
        subtext: 'Regular practice for exams'
      });
      features.push({
        icon: '📁',
        text: 'Unlimited file uploads',
        subtext: 'Upload notes, images, PDFs'
      });
      features.push({
        icon: '🎤',
        text: 'Voice input enabled',
        subtext: 'Ask questions hands-free'
      });
      features.push({
        icon: '📊',
        text: 'Advanced analytics',
        subtext: 'Track progress & insights'
      });
      features.push({
        icon: '🔗',
        text: 'Concept tagging',
        subtext: 'Connect related topics'
      });
      features.push({
        icon: '💾',
        text: 'Export notes & reports',
        subtext: 'Save your learning'
      });
      features.push({
        icon: '🇮🇳',
        text: 'Hinglish support',
        subtext: 'Speak naturally in Hinglish'
      });
    } else if (plan.id === 'PRO') {
      features.push({
        icon: '♾️',
        text: 'Unlimited everything',
        subtext: 'AI sessions, tests, uploads - All unlimited!'
      });
      features.push({
        icon: '🧠',
        text: 'Emotion-aware AI',
        subtext: 'AI adapts to your learning mood'
      });
      features.push({
        icon: '⚡',
        text: 'Priority AI responses',
        subtext: 'Faster answers, always first'
      });
      features.push({
        icon: '🏆',
        text: 'Unlimited mock tests',
        subtext: 'Practice as much as you want'
      });
      features.push({
        icon: '💡',
        text: 'Unlimited mentor tips',
        subtext: '24×7 guidance & motivation'
      });
      features.push({
        icon: '📱',
        text: 'Offline mode',
        subtext: 'Learn without internet'
      });
      features.push({
        icon: '👨‍👩‍👧',
        text: 'Parent dashboard',
        subtext: 'Detailed progress reports'
      });
      features.push({
        icon: '🔍',
        text: 'Advanced OCR',
        subtext: 'Better image & document analysis'
      });
      features.push({
        icon: '📊',
        text: 'Daily personalized insights',
        subtext: 'AI-powered study recommendations'
      });
      features.push({
        icon: '🛡️',
        text: 'Priority support',
        subtext: 'Fastest response time'
      });
    }
    
    return features;
  }

  if (loading || plansLoading) {
    return (
      <div className="p-8 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <LoadingSpinner size="lg" className="text-violet-500 mb-4" />
            <p className="text-slate-400">Loading subscription information...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header with gradient background */}
        <div className="text-center mb-12 relative">
          <div className="absolute inset-0 bg-gradient-to-r from-violet-600/10 via-indigo-600/10 to-purple-600/10 rounded-3xl blur-3xl"></div>
          <div className="relative">
            <div className="flex items-center justify-center mb-6">
              <div className="bg-gradient-to-r from-violet-600 to-indigo-600 p-4 rounded-2xl shadow-xl transform hover:scale-105 transition-transform">
                <Crown className="h-10 w-10 text-white" />
              </div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-violet-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent mb-4">
              Choose Your Learning Plan
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 mb-8 font-medium">
              Unlock your full potential with AI-powered personalized learning
            </p>
            
            {/* Billing Toggle - Enhanced */}
            <div className="flex items-center justify-center space-x-2 p-1.5 bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-lg inline-flex border border-slate-700/50">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-3 rounded-lg transition-all font-semibold ${
                  billingCycle === 'monthly' 
                    ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg scale-105' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-6 py-3 rounded-lg transition-all font-semibold flex items-center gap-2 ${
                  billingCycle === 'yearly' 
                    ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg scale-105'
                    : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                }`}
              >
                <span>Yearly</span>
                <Badge className="bg-emerald-500 text-white text-xs px-2 py-0.5">
                  Save 17%
                </Badge>
              </button>
            </div>
          </div>
        </div>

        {/* Current Subscription - Enhanced */}
        {currentSubscription && (
          <div className="mb-10 relative">
            <div className="bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl p-6 shadow-xl border border-violet-500/30">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                  <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
                    <Crown className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white capitalize">
                      Current Plan: {currentSubscription.plan_name || currentSubscription.plan}
                    </h3>
                    <p className="text-white/90 text-lg">
                      {currentSubscription.plan_details ? 
                        `₹${currentSubscription.plan_details.price_monthly}/month`
                        : 'Free Plan'
                      }
                    </p>
                  </div>
                </div>
                <Badge 
                  className="bg-white text-violet-600 px-4 py-2 text-lg font-bold shadow-lg"
                >
                  ✓ Active
                </Badge>
              </div>
            </div>
          </div>
        )}

        {/* Subscription Plans - Completely Redesigned */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 mb-12">
          {subscriptionPlans.map((plan, index) => {
            const isPopular = plan.popular;
            const isCurrent = plan.current;
            const monthlyPrice = billingCycle === 'yearly' ? Math.round(plan.price_yearly / 12) : plan.price_monthly;
            const yearlySavings = billingCycle === 'yearly' ? (plan.price_monthly * 12) - plan.price_yearly : 0;
            
            return (
              <div
                key={plan.name}
                className={`relative transform transition-all duration-300 hover:scale-105 ${
                  isPopular ? 'md:-mt-4 md:mb-4' : ''
                }`}
              >
                {/* Popular Badge */}
                {isPopular && (
                  <div className="absolute -top-5 left-1/2 transform -translate-x-1/2 z-10">
                    <div className="bg-gradient-to-r from-amber-400 to-orange-500 text-white px-6 py-2 rounded-full shadow-xl flex items-center gap-2 font-bold text-sm">
                      <Star className="h-4 w-4 fill-current" />
                      MOST POPULAR
                    </div>
                  </div>
                )}

                {/* Plan Card - Dark theme with calm content areas */}
                <Card 
                  className={`h-full border transition-all duration-300 ${
                    isPopular 
                      ? 'border-violet-500/50 shadow-2xl shadow-violet-500/10 bg-slate-800/60 backdrop-blur-sm' 
                      : isCurrent 
                        ? 'border-emerald-500/50 shadow-xl bg-slate-800/60 backdrop-blur-sm'
                        : 'border-slate-700/50 hover:border-violet-500/30 shadow-lg bg-slate-800/40 backdrop-blur-sm'
                  }`}
                >
                  <CardHeader className={`text-center pb-6 pt-8 ${isPopular ? 'pt-12' : ''}`}>
                    {/* Plan Emoji & Name */}
                    <div className="flex items-center justify-center gap-3 mb-4">
                      <span className="text-5xl">{plan.emoji || '🎓'}</span>
                      <CardTitle className="text-3xl font-bold text-white">
                        {plan.name}
                      </CardTitle>
                    </div>

                    {/* Price */}
                    <div className="mb-4">
                      {plan.price_monthly === 0 ? (
                        <div className="text-5xl font-bold text-white">Free</div>
                      ) : (
                        <>
                          <div className="flex items-baseline justify-center gap-2">
                            <span className="text-5xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
                              ₹{monthlyPrice}
                            </span>
                            <span className="text-slate-400 text-xl">
                              /{billingCycle === 'yearly' ? 'month' : 'month'}
                            </span>
                          </div>
                          {billingCycle === 'yearly' && yearlySavings > 0 && (
                            <div className="mt-2">
                              <Badge className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-sm px-3 py-1">
                                Save ₹{yearlySavings}/year
                              </Badge>
                            </div>
                          )}
                        </>
                      )}
                    </div>

                    {/* Tagline */}
                    {plan.tagline && (
                      <p className="text-slate-400 text-sm italic mb-6">
                        {plan.tagline}
                      </p>
                    )}
                  </CardHeader>

                  <CardContent className="px-6 pb-8">
                    {/* Features List */}
                    <ul className="space-y-4 mb-8">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-start gap-3 group">
                          <div className="flex-shrink-0 mt-1">
                            <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                              isPopular 
                                ? 'bg-gradient-to-r from-violet-500 to-indigo-500' 
                                : 'bg-emerald-500'
                            }`}>
                              <Check className="h-4 w-4 text-white" />
                            </div>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xl">{feature.icon}</span>
                              <span className="font-semibold text-slate-200 group-hover:text-violet-400 transition-colors">
                                {feature.text}
                              </span>
                            </div>
                            {feature.subtext && (
                              <p className="text-sm text-slate-500 ml-8 mt-0.5">
                                {feature.subtext}
                              </p>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>

                    {/* CTA Button */}
                    <div className="mt-auto">
                      {isCurrent ? (
                        <Button 
                          disabled 
                          className="w-full py-4 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold text-lg rounded-xl cursor-not-allowed"
                        >
                          <Check className="h-5 w-5 mr-2" />
                          Current Plan
                        </Button>
                      ) : (
                        <>
                          {plan.price_monthly > 0 && (
                            <Button
                              onClick={() => handleUpgrade(plan.tier, billingCycle)}
                              disabled={upgrading && selectedPlan === plan.tier}
                              className={`w-full py-4 font-bold text-lg rounded-xl transition-all transform hover:scale-105 ${
                                isPopular
                                  ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-xl hover:shadow-violet-500/25'
                                  : 'bg-violet-600 text-white hover:bg-violet-700 shadow-lg'
                              } disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
                            >
                              {upgrading && selectedPlan === plan.tier ? (
                                <>
                                  <LoadingSpinner size="sm" />
                                  <span>Processing...</span>
                                </>
                              ) : (
                                <>
                                  <Zap className="h-5 w-5" />
                                  Upgrade {billingCycle === 'yearly' ? 'Yearly' : 'Monthly'}
                                  <ArrowRight className="h-5 w-5" />
                                </>
                              )}
                            </Button>
                          )}
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            );
          })}
        </div>

        {/* Features Comparison Table - Enhanced */}
        <Card className="mb-12 shadow-xl border border-slate-700/50 bg-slate-800/40 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-t-lg">
            <CardTitle className="text-3xl font-bold text-center flex items-center justify-center gap-3">
              <Target className="h-8 w-8" />
              Feature Comparison
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b-2 border-slate-700/50">
                    <th className="pb-4 pr-6 text-lg font-bold text-white">Features</th>
                    <th className="pb-4 px-4 text-center text-lg font-bold text-slate-400">Free</th>
                    <th className="pb-4 px-4 text-center text-lg font-bold text-violet-400">Student</th>
                    <th className="pb-4 px-4 text-center text-lg font-bold text-indigo-400">Pro</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <tr className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="py-4 pr-6 font-semibold text-slate-200">AI Tutor Queries</td>
                    <td className="py-4 px-4 text-center text-slate-500">10/month</td>
                    <td className="py-4 px-4 text-center">
                      <span className="font-bold text-violet-400 flex items-center justify-center gap-1">
                        <Infinity className="h-4 w-4" />
                        Unlimited
                      </span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span className="font-bold text-indigo-400 flex items-center justify-center gap-1">
                        <Infinity className="h-4 w-4" />
                        Unlimited + Priority
                      </span>
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="py-4 pr-6 font-semibold text-slate-200">Mock Tests per Week</td>
                    <td className="py-4 px-4 text-center text-slate-500">1</td>
                    <td className="py-4 px-4 text-center text-violet-400 font-semibold">3</td>
                    <td className="py-4 px-4 text-center">
                      <span className="font-bold text-indigo-400 flex items-center justify-center gap-1">
                        <Infinity className="h-4 w-4" />
                        Unlimited
                      </span>
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="py-4 pr-6 font-semibold text-slate-200">File Uploads</td>
                    <td className="py-4 px-4 text-center text-slate-500">1/day</td>
                    <td className="py-4 px-4 text-center">
                      <span className="font-bold text-violet-400 flex items-center justify-center gap-1">
                        <Infinity className="h-4 w-4" />
                        Unlimited
                      </span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span className="font-bold text-indigo-400 flex items-center justify-center gap-1">
                        <Infinity className="h-4 w-4" />
                        Unlimited + OCR
                      </span>
                    </td>
                  </tr>
                  <tr className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="py-4 pr-6 font-semibold text-slate-200">Analytics & Insights</td>
                    <td className="py-4 px-4 text-center text-slate-500">Basic</td>
                    <td className="py-4 px-4 text-center text-violet-400 font-semibold">Advanced + Weekly</td>
                    <td className="py-4 px-4 text-center text-indigo-400 font-semibold">Deep + Daily Personalized</td>
                  </tr>
                  <tr className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="py-4 pr-6 font-semibold text-slate-200">Voice Input</td>
                    <td className="py-4 px-4 text-center text-slate-600">❌</td>
                    <td className="py-4 px-4 text-center text-emerald-400 font-semibold">✅</td>
                    <td className="py-4 px-4 text-center text-emerald-400 font-semibold">✅ Full Sync</td>
                  </tr>
                  <tr className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="py-4 pr-6 font-semibold text-slate-200">Parent Dashboard</td>
                    <td className="py-4 px-4 text-center text-slate-600">❌</td>
                    <td className="py-4 px-4 text-center text-slate-600">❌</td>
                    <td className="py-4 px-4 text-center text-emerald-400 font-semibold">✅ Detailed Reports</td>
                  </tr>
                  <tr className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="py-4 pr-6 font-semibold text-slate-200">Priority Support</td>
                    <td className="py-4 px-4 text-center text-slate-500">Community</td>
                    <td className="py-4 px-4 text-center text-slate-500">Standard</td>
                    <td className="py-4 px-4 text-center text-indigo-400 font-semibold">✅ Fastest Response</td>
                  </tr>
                  <tr className="hover:bg-gray-50 transition-colors">
                    <td className="py-4 pr-6 font-semibold text-slate-200">Offline Mode</td>
                    <td className="py-4 px-4 text-center text-slate-600">❌</td>
                    <td className="py-4 px-4 text-center text-slate-600">❌</td>
                    <td className="py-4 px-4 text-center text-emerald-400 font-semibold">✅</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Trust Signals */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 shadow-lg text-center border-2 border-gray-100">
            <Shield className="h-12 w-12 text-violet-400 mx-auto mb-3" />
            <h3 className="font-bold text-lg text-gray-900 mb-2">100% Secure</h3>
            <p className="text-slate-500">Your payment is safe and encrypted</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-lg text-center border-2 border-gray-100">
            <Gift className="h-12 w-12 text-indigo-400 mx-auto mb-3" />
            <h3 className="font-bold text-lg text-gray-900 mb-2">Cancel Anytime</h3>
            <p className="text-slate-500">No long-term commitment required</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-lg text-center border-2 border-gray-100">
            <TrendingUp className="h-12 w-12 text-emerald-400 mx-auto mb-3" />
            <h3 className="font-bold text-lg text-gray-900 mb-2">Student Discount</h3>
            <p className="text-slate-500">Special pricing for verified students</p>
          </div>
        </div>

        {/* Contact Support */}
        <div className="text-center bg-white rounded-2xl p-8 shadow-xl border-2 border-gray-200">
          <h3 className="text-2xl font-bold text-gray-900 mb-3">
            Need help choosing the right plan?
          </h3>
          <p className="text-slate-500 mb-6 text-lg">
            Our team is here to help you find the perfect plan for your learning journey!
          </p>
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 text-lg font-semibold rounded-xl hover:shadow-xl transition-all">
            Contact Support
          </Button>
        </div>
      </div>

      {/* Razorpay Payment Modal */}
      {showPaymentModal && paymentDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm">
          <div className="relative w-full max-w-lg">
            {/* Close Button */}
            <button
              onClick={() => setShowPaymentModal(false)}
              className="absolute -top-2 -right-2 z-60 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100 transition-colors"
            >
              <X className="h-5 w-5 text-slate-500" />
            </button>
            
            {/* Payment Component */}
            <RazorpayPayment
              planName={paymentDetails.planName}
              billingCycle={paymentDetails.billingCycle}
              amount={paymentDetails.amount}
              onSuccess={handlePaymentSuccess}
              onError={handlePaymentError}
              onCancel={handlePaymentCancel}
              userDetails={paymentDetails.userDetails}
            />
          </div>
        </div>
      )}
    </div>
  );
}
