import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { LoadingSpinner } from './ui/loading';
import { 
  Crown, 
  Check, 
  CreditCard, 
  Zap,
  Star,
  Calendar,
  Sparkles,
  ArrowRight,
  Clock
} from 'lucide-react';

export default function Subscription() {
  const { user } = useAuth();
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');

  useEffect(() => {
    loadCurrentSubscription();
  }, []);

  const loadCurrentSubscription = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      const response = await fetch(`${backendUrl}/api/subscription/current`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSubscription(data);
      }
    } catch (error) {
      console.error('Failed to load subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUsage = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      const response = await fetch(`${backendUrl}/api/subscription/usage`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Failed to load usage:', error);
      return null;
    }
  };

  const handleUpgrade = async (planName, billingCycle = 'monthly') => {
    setUpgrading(true);
    setSelectedPlan(planName);
    
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const backendUrl = process.env.REACT_APP_BACKEND_URL;

      const response = await fetch(`${backendUrl}/api/subscription/upgrade?target_tier=${planName}&billing_cycle=${billingCycle}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Redirect to payment or show success
        const data = await response.json();
        if (data.redirect_url) {
          window.location.href = data.redirect_url;
        }
      } else {
        const errorData = await response.json();
        console.error('Upgrade failed:', errorData);
        // Show error message
      }
    } catch (error) {
      console.error('Upgrade error:', error);
    } finally {
      setUpgrading(false);
      setSelectedPlan(null);
    }
  };

  const subscriptionPlans = [
    {
      name: 'Free',
      price_monthly: 0,
      price_yearly: 0,
      features: [
        '2 mock tests per month',
        '5 AI tutor queries per day',
        'Basic performance tracking',
        'Access to study materials'
      ],
      current: currentSubscription?.plan_name === 'free',
      popular: false
    },
    {
      name: 'Basic',
      price_monthly: 299,
      price_yearly: 2990,
      features: [
        '20 mock tests per month',
        'Unlimited AI tutor queries',
        'Detailed performance analytics',
        'Auto-note generation',
        'Priority support'
      ],
      current: currentSubscription?.plan_name === 'basic',
      popular: true
    },
    {
      name: 'Premium',
      price_monthly: 599,
      price_yearly: 5990,
      features: [
        'Unlimited mock tests',
        'Advanced AI tutor with dual analysis',
        'Comprehensive analytics dashboard',
        'Auto-note generation with OCR',
        'Spaced repetition scheduling',
        'Parent dashboard access',
        'Priority support'
      ],
      current: currentSubscription?.plan_name === 'premium',
      popular: false
    }
  ];

  if (loading) {
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
                            onClick={() => handleUpgrade(plan.name, billingCycle)}
                            disabled={upgrading && selectedPlan === plan.name}
                            className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                          >
                            {upgrading && selectedPlan === plan.name ? (
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
                    <th className="pb-3 px-4 text-center">Basic</th>
                    <th className="pb-3 px-4 text-center">Premium</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <tr className="border-b">
                    <td className="py-3 pr-4">Mock Tests per Month</td>
                    <td className="py-3 px-4 text-center">2</td>
                    <td className="py-3 px-4 text-center">20</td>
                    <td className="py-3 px-4 text-center">Unlimited</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">AI Tutor Queries</td>
                    <td className="py-3 px-4 text-center">5/day</td>
                    <td className="py-3 px-4 text-center">Unlimited</td>
                    <td className="py-3 px-4 text-center">Unlimited + Dual AI</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">Auto-Note Generation</td>
                    <td className="py-3 px-4 text-center">❌</td>
                    <td className="py-3 px-4 text-center">✅</td>
                    <td className="py-3 px-4 text-center">✅ + OCR</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-3 pr-4">Advanced Analytics</td>
                    <td className="py-3 px-4 text-center">❌</td>
                    <td className="py-3 px-4 text-center">✅</td>
                    <td className="py-3 px-4 text-center">✅ + Parent Access</td>
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
    </div>
  );
}