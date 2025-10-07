import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { 
  X, 
  Sparkles, 
  Heart, 
  GraduationCap, 
  Users,
  Zap,
  Crown,
  TrendingUp,
  Shield,
  CheckCircle,
  ArrowRight
} from 'lucide-react';
import { useSubscription } from '../contexts/SubscriptionContext';

export default function UpsellModal({ isOpen, onClose, onUpgradeSuccess }) {
  const { upsellModal, handleUpsellResponse, upgradeSubscription } = useSubscription();
  const [upgrading, setUpgrading] = useState(false);
  const [billingCycle, setBillingCycle] = useState('monthly');

  if (!isOpen || !upsellModal) return null;

  const { upsellInfo, featureName, currentUsage, limit } = upsellModal;
  const targetTier = upsellInfo?.target_tier || 'PREMIUM';
  const targetPlan = upsellInfo?.target_plan || {};

  const handleUpgrade = async () => {
    setUpgrading(true);
    try {
      const result = await upgradeSubscription(targetTier, billingCycle);
      if (result.success) {
        // Handle upgrade success callback first (for retry logic)
        if (onUpgradeSuccess) {
          await onUpgradeSuccess();
        }
        
        // Show success message and close modal
        onClose();
        if (upsellInfo?.interaction_id) {
          await handleUpsellResponse(upsellInfo.interaction_id, 'upgraded');
        }
      }
    } catch (error) {
      console.error('Upgrade failed:', error);
    } finally {
      setUpgrading(false);
    }
  };

  const handleDismiss = async () => {
    if (upsellInfo?.interaction_id) {
      await handleUpsellResponse(upsellInfo.interaction_id, 'dismissed');
    }
    onClose();
  };

  const handleLater = async () => {
    if (upsellInfo?.interaction_id) {
      await handleUpsellResponse(upsellInfo.interaction_id, 'later');
    }
    onClose();
  };

  const getFeatureIcon = (feature) => {
    const iconMap = {
      'ai_tutor_daily': GraduationCap,
      'mock_tests_weekly': Zap,
      'auto_note_uploads_daily': Heart,
      'voice_mode': Users
    };
    return iconMap[feature] || Sparkles;
  };

  const FeatureIcon = getFeatureIcon(featureName);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="max-w-2xl w-full max-h-[90vh] overflow-auto animate-in fade-in-0 zoom-in-95 duration-300">
        <Card className="overflow-hidden border-0 shadow-2xl">
          {/* Header with gradient */}
          <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 p-4 md:p-6 text-white relative">
            <button
              onClick={handleDismiss}
              className="absolute top-3 right-3 md:top-4 md:right-4 text-white/80 hover:text-white transition-colors min-h-10 min-w-10 flex items-center justify-center rounded-lg mobile-transition"
              aria-label="Close modal"
            >
              <X className="h-5 w-5 md:h-6 md:w-6" />
            </button>
            
            <div className="flex items-center space-x-3 md:space-x-4 pr-12">
              <div className="w-10 h-10 md:w-12 md:h-12 bg-white/20 rounded-full flex items-center justify-center">
                <FeatureIcon className="h-5 w-5 md:h-6 md:w-6 text-white" />
              </div>
              <div>
                <h2 className="text-lg md:text-2xl font-bold">
                  {upsellModal?.title || 'Ready for the Next Level? 🚀'}
                </h2>
                <p className="text-blue-100 text-sm md:text-base">Your learning journey is accelerating!</p>
              </div>
            </div>
          </div>

          <CardContent className="p-6">
            {/* AI Dialogue Section */}
            <div className="space-y-4 mb-6">
              {/* Mentor Message */}
              <div className="flex items-start space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Heart className="h-5 w-5 text-blue-600" />
                </div>
                <div className="bg-blue-50 rounded-lg p-4 flex-1">
                  <div className="flex items-center mb-2">
                    <span className="font-medium text-blue-900">Mentor AI</span>
                    <Badge className="ml-2 bg-blue-100 text-blue-800 border-blue-200">
                      💙 Supportive
                    </Badge>
                  </div>
                  <p className="text-blue-800 text-sm leading-relaxed">
                    {upsellInfo?.mentor_message || upsellModal?.description || `Hey champ! You've completed ${currentUsage}/${limit} verified sessions today — that's impressive progress! Ready to unlock unlimited verified learning?`}
                  </p>
                </div>
              </div>

              {/* Professor Message */}
              <div className="flex items-start space-x-3">
                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <GraduationCap className="h-5 w-5 text-purple-600" />
                </div>
                <div className="bg-purple-50 rounded-lg p-4 flex-1">
                  <div className="flex items-center mb-2">
                    <span className="font-medium text-purple-900">Professor AI</span>
                    <Badge className="ml-2 bg-purple-100 text-purple-800 border-purple-200">
                      🎓 Analytical
                    </Badge>
                  </div>
                  <p className="text-purple-800 text-sm leading-relaxed">
                    {upsellInfo?.professor_message || "Your analytical skills are developing excellently. Premium access would unlock adaptive insights for accelerated mastery."}
                  </p>
                </div>
              </div>
            </div>

            {/* Growth Stats */}
            {upsellInfo?.growth_stats && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 mb-6">
                <div className="flex items-center mb-3">
                  <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                  <span className="font-medium text-green-900">Your Verified Progress</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-green-700">
                      {upsellInfo.growth_stats.accuracy || 87}%
                    </div>
                    <div className="text-xs text-green-600">Accuracy</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-700">
                      Level {upsellInfo.growth_stats.current_level || 1}
                    </div>
                    <div className="text-xs text-green-600">XP Level</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-700">
                      {upsellInfo.growth_stats.total_xp || 0}
                    </div>
                    <div className="text-xs text-green-600">Total XP</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-700">
                      {upsellInfo.growth_stats.efficiency || 85}%
                    </div>
                    <div className="text-xs text-green-600">Efficiency</div>
                  </div>
                </div>
              </div>
            )}

            {/* Plan Upgrade Preview */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Crown className="h-5 w-5 text-indigo-600 mr-2" />
                  <span className="font-semibold text-indigo-900">
                    {targetPlan.display_name || '⚡ Premium - The Achiever'}
                  </span>
                </div>
                <Badge className="bg-indigo-100 text-indigo-800 border-indigo-200">
                  Recommended
                </Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                {(upsellModal?.benefits || [
                  'Unlimited AI Conversations',
                  '3 Mock Tests/Week', 
                  'Unlimited Note Uploads',
                  'Voice Mode (Mentor)',
                  'Priority AI processing',
                  'Advanced analytics'
                ]).slice(0, 6).map((benefit, index) => (
                  <div key={index} className="flex items-center text-sm text-indigo-800">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    {benefit}
                  </div>
                ))}
              </div>

              {/* Billing Toggle */}
              <div className="flex items-center justify-center space-x-2 mb-4">
                <span className={`text-sm ${billingCycle === 'monthly' ? 'font-semibold text-indigo-900' : 'text-gray-600'}`}>
                  Monthly
                </span>
                <button
                  onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    billingCycle === 'yearly' ? 'bg-indigo-600' : 'bg-gray-300'
                  }`}
                >
                  <div
                    className={`absolute w-5 h-5 bg-white rounded-full top-0.5 transition-transform ${
                      billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-0.5'
                    }`}
                  />
                </button>
                <span className={`text-sm ${billingCycle === 'yearly' ? 'font-semibold text-indigo-900' : 'text-gray-600'}`}>
                  Yearly
                </span>
                {billingCycle === 'yearly' && (
                  <Badge className="bg-green-100 text-green-800 border-green-200 text-xs">
                    Save 17%
                  </Badge>
                )}
              </div>

              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-900">
                  ₹{billingCycle === 'monthly' ? 
                    (targetPlan.price_monthly || 499) : 
                    Math.round((targetPlan.price_yearly || 4999) / 12)
                  }
                  <span className="text-lg text-indigo-600">/month</span>
                </div>
                {billingCycle === 'yearly' && (
                  <div className="text-sm text-indigo-600">
                    Billed yearly at ₹{targetPlan.price_yearly || 4999}
                  </div>
                )}
              </div>
            </div>

            {/* Verified Badge */}
            <div className="flex items-center justify-center mb-6">
              <div className="flex items-center bg-green-50 border border-green-200 rounded-full px-4 py-2">
                <Shield className="h-4 w-4 text-green-600 mr-2" />
                <span className="text-sm font-medium text-green-800">
                  ✓ 100% Hallucination-Free AI Guarantee
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
              <Button
                onClick={handleUpgrade}
                disabled={upgrading}
                className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-3 transition-all duration-300 hover:scale-105"
              >
                {upgrading ? (
                  <div className="flex items-center">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                    Upgrading...
                  </div>
                ) : (
                  <div className="flex items-center">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Unlock Verified Growth
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </div>
                )}
              </Button>
              
              <Button
                onClick={handleLater}
                variant="outline"
                className="border-gray-300 text-gray-600 hover:bg-gray-50"
              >
                Maybe Later
              </Button>
            </div>

            {/* Trust Message */}
            <div className="text-center mt-4">
              <p className="text-xs text-gray-500">
                Join 50,000+ students who trust Dhruv AI for verified, hallucination-free learning
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}