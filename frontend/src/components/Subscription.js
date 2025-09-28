import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  Crown, 
  Star, 
  Zap, 
  Check, 
  X, 
  Loader2, 
  AlertCircle,
  Calendar,
  TrendingUp,
  Users,
  Headphones
} from 'lucide-react';

const Subscription = () => {
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [availablePlans, setAvailablePlans] = useState([]);
  const [usageSummary, setUsageSummary] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [processingPlan, setProcessingPlan] = useState('');

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('dhruv_ai_token');
      const backendUrl = process.env.REACT_APP_BACKEND_URL;

      // Load current subscription
      const subscriptionResponse = await fetch(`${backendUrl}/api/subscription/current`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        setCurrentSubscription(subscriptionData);
        setUsageSummary(subscriptionData.usage_summary || {});
      }

      // Load available plans
      const plansResponse = await fetch(`${backendUrl}/api/subscription/plans`);
      if (plansResponse.ok) {
        const plansData = await plansResponse.json();
        setAvailablePlans(plansData.plans || []);
      }

    } catch (error) {
      console.error('Failed to load subscription data:', error);
      setError('Failed to load subscription information');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpgrade = async (planName, billingCycle = 'monthly') => {
    try {
      setProcessingPlan(planName);
      setError('');
      
      const token = localStorage.getItem('dhruv_ai_token');
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      // Get current URL for success/cancel redirects
      const currentUrl = window.location.origin + '/subscription';
      const successUrl = `${currentUrl}?session_id={CHECKOUT_SESSION_ID}`;
      const cancelUrl = currentUrl;

      const response = await fetch(`${backendUrl}/api/subscription/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan_name: planName,
          billing_cycle: billingCycle,
          success_url: successUrl,
          cancel_url: cancelUrl
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create checkout session');
      }

      const data = await response.json();
      
      // Redirect to Stripe Checkout
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error('No checkout URL received');
      }

    } catch (error) {
      console.error('Upgrade error:', error);
      setError(error.message);
    } finally {
      setProcessingPlan('');
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your billing period.')) {
      return;
    }

    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const backendUrl = process.env.REACT_APP_BACKEND_URL;

      const response = await fetch(`${backendUrl}/api/subscription/cancel`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Failed to cancel subscription');
      }

      await loadSubscriptionData();
      alert('Subscription cancelled successfully');

    } catch (error) {
      console.error('Cancel error:', error);
      setError(error.message);
    }
  };

  const checkPaymentStatus = async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId) {
      try {
        const token = localStorage.getItem('dhruv_ai_token');
        const backendUrl = process.env.REACT_APP_BACKEND_URL;

        const response = await fetch(`${backendUrl}/api/subscription/payment-status/${sessionId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.payment_status === 'paid') {
            alert('Payment successful! Your subscription has been activated.');
            await loadSubscriptionData();
            // Clear the session_id from URL
            window.history.replaceState({}, document.title, '/subscription');
          }
        }
      } catch (error) {
        console.error('Payment status check error:', error);
      }
    }
  };

  useEffect(() => {
    checkPaymentStatus();
  }, []);

  const getPlanIcon = (planName) => {
    const icons = {
      free: <Users className="w-8 h-8 text-gray-500" />,
      basic: <Star className="w-8 h-8 text-blue-500" />,
      premium: <Crown className="w-8 h-8 text-purple-500" />,
      pro: <Zap className="w-8 h-8 text-orange-500" />
    };
    return icons[planName] || <Star className="w-8 h-8" />;
  };

  const formatUsage = (featureName, usage) => {
    if (!usage) return 'N/A';
    
    if (usage.unlimited) {
      return 'Unlimited';
    }
    
    return `${usage.used}/${usage.limit}`;
  };

  const getUsagePercentage = (usage) => {
    if (!usage || usage.unlimited) return 0;
    return usage.limit > 0 ? (usage.used / usage.limit) * 100 : 0;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="flex items-center gap-3 text-blue-600">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-lg">Loading subscription details...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Subscription Management
          </h1>
          <p className="text-xl text-gray-600">
            Manage your Dhruv AI subscription and unlock premium features
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Current Subscription Status */}
        {currentSubscription && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Current Plan</h2>
              {currentSubscription.subscription.status === 'cancelled' && (
                <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                  Cancelled
                </span>
              )}
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  {getPlanIcon(currentSubscription.subscription.plan_name)}
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 capitalize">
                      {currentSubscription.plan_details.display_name}
                    </h3>
                    <p className="text-gray-600">
                      ₹{currentSubscription.plan_details.price_monthly}/month
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar className="w-5 h-5" />
                  <span>
                    {currentSubscription.days_remaining} days remaining
                  </span>
                </div>

                {currentSubscription.subscription.plan_name !== 'free' && 
                 currentSubscription.subscription.status === 'active' && (
                  <button
                    onClick={handleCancelSubscription}
                    className="text-red-600 hover:text-red-800 font-medium"
                  >
                    Cancel Subscription
                  </button>
                )}
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Usage Summary</h4>
                <div className="space-y-3">
                  {Object.entries(usageSummary).map(([feature, usage]) => (
                    <div key={feature} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 capitalize">
                          {feature.replace(/_/g, ' ')}
                        </span>
                        <span className="font-medium">
                          {formatUsage(feature, usage)}
                        </span>
                      </div>
                      {!usage.unlimited && usage.limit > 0 && (
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-300 ${
                              getUsagePercentage(usage) > 80 
                                ? 'bg-red-500' 
                                : getUsagePercentage(usage) > 60
                                ? 'bg-yellow-500'
                                : 'bg-blue-500'
                            }`}
                            style={{ width: `${Math.min(getUsagePercentage(usage), 100)}%` }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Available Plans */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Choose Your Plan
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {availablePlans.map((plan) => {
              const isCurrentPlan = currentSubscription?.subscription.plan_name === plan.name;
              const isPremium = plan.name !== 'free';
              
              return (
                <div
                  key={plan.name}
                  className={`bg-white rounded-xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl ${
                    plan.name === 'premium' ? 'ring-2 ring-purple-500 scale-105' : ''
                  }`}
                >
                  {plan.name === 'premium' && (
                    <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white text-center py-2 text-sm font-medium">
                      Most Popular
                    </div>
                  )}
                  
                  <div className="p-6">
                    <div className="text-center mb-6">
                      {getPlanIcon(plan.name)}
                      <h3 className="text-xl font-bold text-gray-900 mt-3 mb-2">
                        {plan.display_name}
                      </h3>
                      <div className="text-3xl font-bold text-gray-900">
                        ₹{plan.price_monthly}
                        <span className="text-base font-normal text-gray-600">/month</span>
                      </div>
                      {plan.price_yearly > 0 && (
                        <p className="text-sm text-green-600 mt-1">
                          Save ₹{(plan.price_monthly * 12) - plan.price_yearly} with yearly billing
                        </p>
                      )}
                    </div>

                    <div className="space-y-3 mb-6">
                      {plan.features.map((feature, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-gray-600">{feature}</span>
                        </div>
                      ))}
                    </div>

                    <div className="space-y-2">
                      {!isCurrentPlan && isPremium && (
                        <>
                          <button
                            onClick={() => handleUpgrade(plan.name, 'monthly')}
                            disabled={processingPlan === plan.name}
                            className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                          >
                            {processingPlan === plan.name ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <CreditCard className="w-4 h-4" />
                            )}
                            Upgrade Monthly
                          </button>
                          
                          {plan.price_yearly > 0 && (
                            <button
                              onClick={() => handleUpgrade(plan.name, 'yearly')}
                              disabled={processingPlan === plan.name}
                              className="w-full py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                              {processingPlan === plan.name ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <TrendingUp className="w-4 h-4" />
                              )}
                              Upgrade Yearly
                            </button>
                          )}
                        </>
                      )}
                      
                      {isCurrentPlan && (
                        <div className="w-full py-2 px-4 bg-gray-100 text-gray-700 rounded-lg text-center font-medium">
                          Current Plan
                        </div>
                      )}
                      
                      {plan.name === 'free' && !isCurrentPlan && (
                        <div className="w-full py-2 px-4 bg-gray-100 text-gray-700 rounded-lg text-center font-medium">
                          Free Plan
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Support Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <Headphones className="w-12 h-12 text-blue-500 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Need Help?</h3>
          <p className="text-gray-600 mb-4">
            Our support team is here to help you with any questions about your subscription.
          </p>
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Contact Support
          </button>
        </div>
      </div>
    </div>
  );
};

export default Subscription;