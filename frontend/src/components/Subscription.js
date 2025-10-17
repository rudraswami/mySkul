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
  X
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
    tagline: plan.tagline
  }));

  // Helper function to format plan features for display
  function formatPlanFeatures(plan) {
    const features = [];
    const { features: planFeatures } = plan;
    
    if (plan.id === 'FREE') {
      features.push(`🎯 ${planFeatures.ai_sessions_monthly} AI sessions monthly - Perfect for trying`);
      features.push(`📝 ${planFeatures.mock_tests_weekly} mock test weekly - Build confidence`);
      features.push(`📁 ${planFeatures.auto_note_uploads_daily} file upload daily - Try note generation`);
      features.push('📊 Basic analytics - See your progress');
    } else if (plan.id === 'STARTER') {
      features.push(`🚀 ${planFeatures.ai_sessions_monthly} AI sessions monthly - Get started`);
      features.push(`📝 ${planFeatures.mock_tests_weekly} mock tests weekly - Regular practice`);
      features.push(`📁 ${planFeatures.auto_note_uploads_daily} uploads daily - More content`);
      features.push('📊 Basic analytics - Track improvement');
      features.push('📤 Export notes - Save your work');
    } else if (plan.id === 'SCHOLAR') {
      features.push(`🚀 ${planFeatures.ai_sessions_monthly} AI sessions monthly - Serious learning`);
      features.push(`📝 ${planFeatures.mock_tests_weekly} mock tests weekly - Intensive practice`);
      features.push('📁 Unlimited uploads - All your material');
      features.push(`💡 ${planFeatures.mentor_tips_daily} mentor tips daily - Expert guidance`);
      features.push('📊 Advanced analytics - Deep insights');
      features.push('🔍 Concept tagging - Connect topics');
    } else if (plan.id === 'ACHIEVER') {
      features.push(`🚀 ${planFeatures.ai_sessions_monthly} AI sessions monthly - Heavy usage`);
      features.push(`💡 ${planFeatures.mentor_tips_daily} mentor tips daily - Constant guidance`);
      features.push('🏆 Unlimited mock tests - Practice freely');
      features.push('📁 Unlimited uploads - Everything');
      features.push('⚡ Priority support - Fast responses');
      features.push('🎙️ Voice mode - Hands-free learning');
      features.push('📱 Offline mode - Learn anywhere');
    } else if (plan.id === 'LEGEND') {
      features.push('🚀 Unlimited AI sessions - No limits');
      features.push('💡 Unlimited mentor tips - 24×7 guidance');
      features.push('🏆 Unlimited everything - Full access');
      features.push('👨‍🏫 Dedicated AI mentor - Personal coach');
      features.push('📋 Custom study plans - Tailored for you');
      features.push('📊 Premium analytics - Deepest insights');
      features.push('🎯 AIR single-digit training - Elite prep');
    }
    
    return features;
  }

  if (loading || plansLoading) {
    return (
      <div className="p-8 bg-gray-50 min-h-screen">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <LoadingSpinner size="lg" className="text-blue-600 mb-4" />
            <p className="text-gray-600">Loading subscription information...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-xl mr-4">
              <Crown className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Learning Plan
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Unlock your full potential with AI-powered personalized learning
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 p-1 bg-gray-100 rounded-lg inline-flex">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-4 py-2 rounded-md transition-colors ${
                billingCycle === 'monthly' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-4 py-2 rounded-md transition-colors ${
                billingCycle === 'yearly' 
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span className="mr-2">Yearly</span>
              <Badge variant="secondary" className="bg-green-100 text-green-800 text-xs">
                Save 17%
              </Badge>
            </button>
          </div>
        </div>

        {/* Current Subscription */}
        {currentSubscription && (
          <Card className="mb-8 border-blue-200 bg-blue-50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Crown className="h-6 w-6 text-blue-600 mr-3" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 capitalize">
                      Current Plan: {currentSubscription.plan_name || currentSubscription.plan}
                    </h3>
                    <p className="text-gray-600">
                      {currentSubscription.plan_details ? 
                        `₹${currentSubscription.plan_details.price_monthly}/month`
                        : 'Free Plan'
                      }
                    </p>
                  </div>
                </div>
                <Badge 
                  variant={currentSubscription.status === 'active' ? 'default' : 'secondary'}
                  className={
                    currentSubscription.status === 'active' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-blue-500'
                  }
                >
                  {currentSubscription.status}
                </Badge>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Subscription Plans */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {subscriptionPlans.map((plan, index) => (
            <Card 
              key={plan.name} 
              className={`relative border-2 transition-all hover:shadow-lg ${
                plan.popular 
                  ? 'border-blue-500 shadow-lg' 
                  : plan.current 
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-blue-600 text-white px-4 py-1">
                    <Star className="h-3 w-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pb-4">
                <CardTitle className="text-2xl font-bold text-gray-900">
                  {plan.name}
                </CardTitle>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-gray-900">
                    ₹{billingCycle === 'yearly' ? plan.price_yearly : plan.price_monthly}
                  </span>
                  {plan.price_monthly > 0 && (
                    <span className="text-gray-600">
                      /{billingCycle === 'yearly' ? 'year' : 'month'}
                    </span>
                  )}
                </div>
                {plan.price_yearly > 0 && billingCycle === 'yearly' && (
                  <p className="text-sm text-green-600 mt-2">
                    Save ₹{(plan.price_monthly * 12) - plan.price_yearly} with yearly billing
                  </p>
                )}
              </CardHeader>

              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <Check className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <div className="space-y-3">
                  {plan.current ? (
                    <Button disabled className="w-full py-3 bg-green-100 text-green-800">
                      <Check className="h-4 w-4 mr-2" />
                      Current Plan
                    </Button>
                  ) : (
                    <>
                      {plan.price_monthly > 0 && (
                        <>
                          <Button
                            onClick={() => handleUpgrade(plan.tier, billingCycle)}
                            disabled={upgrading && selectedPlan === plan.tier}
                            className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                          >
                            {upgrading && selectedPlan === plan.tier ? (
                              <LoadingSpinner size="sm" />
                            ) : (
                              <Zap className="h-4 w-4" />
                            )}
                            Upgrade {billingCycle === 'yearly' ? 'Yearly' : 'Monthly'}
                          </Button>
                        </>
                      )}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features Comparison */}
        <Card>
          <CardHeader>
            <CardTitle className="text-center">Feature Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="pb-3 pr-4">Features</th>
                    <th className="pb-3 px-4 text-center">Free</th>
                    <th className="pb-3 px-4 text-center">Premium</th>
                    <th className="pb-3 px-4 text-center">Pro</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <tr className="border-b">
                    <td className="py-3 pr-4">Mock Tests per Week</td>
                    <td className="py-3 px-4 text-center">2</td>
                    <td className="py-3 px-4 text-center">3</td>
                    <td className="py-3 px-4 text-center">Unlimited</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">AI Tutor Queries</td>
                    <td className="py-3 px-4 text-center">5/day</td>
                    <td className="py-3 px-4 text-center">Unlimited</td>
                    <td className="py-3 px-4 text-center">Unlimited + Emotion-Aware</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">File Uploads</td>
                    <td className="py-3 px-4 text-center">1/day</td>
                    <td className="py-3 px-4 text-center">Unlimited</td>
                    <td className="py-3 px-4 text-center">Unlimited + Advanced OCR</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">Analytics & Progress Tracking</td>
                    <td className="py-3 px-4 text-center">Basic</td>
                    <td className="py-3 px-4 text-center">Advanced + Weekly Insights</td>
                    <td className="py-3 px-4 text-center">Advanced + Daily Personalized</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">Parent Dashboard</td>
                    <td className="py-3 px-4 text-center">❌</td>
                    <td className="py-3 px-4 text-center">❌</td>
                    <td className="py-3 px-4 text-center">✅ Detailed Reports</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">Priority Support</td>
                    <td className="py-3 px-4 text-center">Community</td>
                    <td className="py-3 px-4 text-center">✅ Priority</td>
                    <td className="py-3 px-4 text-center">✅ Fastest Response</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Contact Support */}
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">
            Need help choosing the right plan? Our team is here to help!
          </p>
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Contact Support
          </button>
        </div>
      </div>

      {/* Razorpay Payment Modal */}
      {showPaymentModal && paymentDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div className="relative w-full max-w-lg">
            {/* Close Button */}
            <button
              onClick={() => setShowPaymentModal(false)}
              className="absolute -top-2 -right-2 z-60 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100 transition-colors"
            >
              <X className="h-5 w-5 text-gray-600" />
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