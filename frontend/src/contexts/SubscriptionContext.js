import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

const SubscriptionContext = createContext();

// Centralized subscription data fetching with React Query
const fetchSubscriptionInfo = async () => {
  try {
    const response = await apiClient.get('/subscription/info');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch subscription info:', error);
    // Return default FREE tier on error
    return {
      subscription_tier: 'FREE',
      plan_info: {
        display_name: '🆓 Free - Try Before You Commit',
        features: {
          ai_sessions_monthly: 10,
          mentor_tips_daily: 0,
          mock_tests_weekly: 1,
          auto_note_uploads_daily: 1,
          focus_engine_type: 'static',
          ai_insights: 'locked',
          voice_mode: 'locked',
          offline_mode: false,
          analytics_tier: 'basic',
          visuals: 'standard',
          priority_support: false,
          export_notes: false,
          concept_tagging: false
        }
      },
      daily_usage: {},
      usage_summary: { features: {} }
    };
  }
};

export function SubscriptionProvider({ children }) {
  const [upsellModal, setUpsellModal] = useState(null);
  const queryClient = useQueryClient();

  // Use React Query for subscription data - fetched once per session, cached
  const {
    data: subscriptionInfo,
    isLoading: loading,
    refetch: refetchSubscription,
    error
  } = useQuery({
    queryKey: ['subscription', 'info'],
    queryFn: fetchSubscriptionInfo,
    staleTime: 5 * 60 * 1000, // 5 minutes - data is fresh
    cacheTime: 30 * 60 * 1000, // 30 minutes - keep in cache
    refetchOnWindowFocus: false, // Don't refetch on window focus
    refetchOnMount: false, // Don't refetch on component mount if data exists
    retry: 1, // Only retry once on failure
  });

  const dailyUsage = subscriptionInfo?.daily_usage || subscriptionInfo?.usage_summary?.features || {};

  const openUpsellModal = useCallback((featureName, detailLike) => {
    if (!detailLike) detailLike = {};
    const upsellInfo = detailLike.upsell_info || detailLike;
    
    // Get target plan and pricing from upsell_info
    const targetPlan = upsellInfo?.target_plan || 'STARTER';
    const pricing = getPlanPricing(targetPlan);
    
    const modalData = {
      featureName,
      upsellInfo: {
        ...upsellInfo,
        target_plan: targetPlan,
        pricing: pricing
      },
      currentUsage: detailLike.used || detailLike.current_usage || 0,
      limit: detailLike.limit || 0,
      title: getFeatureTitle(featureName),
      description: getFeatureDescription(featureName),
      benefits: getFeatureBenefits(featureName)
    };
    setUpsellModal(modalData);
    return modalData;
  }, []);

  const checkFeatureAccess = useCallback(async (featureName) => {
    try {
      const response = await apiClient.post('/subscription/check-access', 
        { feature_name: featureName }
      );

      return response.data;
    } catch (error) {
      console.error('Feature access check failed:', error);
      
      // Handle subscription errors (402 = payment required, 429 = rate limit)
      if (error.response?.status === 402 || error.response?.status === 429) {
        const errorData = error.response.data;
        console.log('🔒 Subscription limit reached:', error.response.status, errorData);
        
        const detail = errorData.detail || errorData;
        if (detail?.upsell_info) {
          openUpsellModal(featureName, detail);
          console.log(`✅ Upsell modal triggered: ${featureName} (${detail.used || 0}/${detail.limit || 0})`);
        }
        
        // Return ALL the data from the backend 402 response
        return { 
          has_access: false, 
          upgrade_needed: true,
          reason: detail?.reason || 'limit_reached',
          upsell_info: detail?.upsell_info,
          used: detail?.used || detail?.current_usage || 0,
          current_usage: detail?.current_usage || detail?.used || 0,
          limit: detail?.limit || 0,
          total: detail?.limit || 0,
          remaining: detail?.remaining || 0,
          subscription_tier: detail?.subscription_tier || 'FREE'
        };
      }
      
      // SECURITY FIX: Don't fail open on errors - deny access by default
      console.error('❌ Feature access check error - denying access by default');
      return { 
        has_access: false, 
        upgrade_needed: false,
        error: true,
        message: 'Unable to verify access. Please try again.'
      };
    }
  }, [openUpsellModal]);

  // Helper function to get plan pricing
  const getPlanPricing = (planTier) => {
    const pricingMap = {
      'STARTER': { monthly: 99, quarterly: 249, yearly: 899 },
      'SCHOLAR': { monthly: 299, quarterly: 799, yearly: 2799 },
      'ACHIEVER': { monthly: 799, quarterly: 2199, yearly: 7999 },
      'LEGEND': { monthly: 1599, quarterly: 3599, yearly: 10799 }
    };
    return pricingMap[planTier] || pricingMap['STARTER'];
  };

  // Helper functions for market-standard messaging (updated for planConfig_ai_tutor.json)
  const getFeatureTitle = (featureName) => {
    const titles = {
      'ai_sessions_monthly': '🎓 Unlock More AI Tutoring Sessions',
      'mentor_tips_daily': '💡 Unlock Daily Mentor Tips',
      'mock_tests_weekly': '🏆 Access More Mock Tests',
      'auto_note_uploads_daily': '📁 Upload More Notes & Files'
    };
    return titles[featureName] || '⚡ Upgrade Your Learning';
  };

  const getFeatureDescription = (featureName) => {
    const descriptions = {
      'ai_sessions_monthly': "You've reached your monthly AI Tutor limit. Upgrade to get more conversations with your personal AI Professor and Mentor.",
      'mentor_tips_daily': "Unlock daily motivational mentor tips. Upgrade to receive personalized encouragement and study tips every day.",
      'mock_tests_weekly': "You've used all your mock tests this week. Upgrade for more practice tests and detailed performance analytics.",
      'auto_note_uploads_daily': "You've reached your daily upload limit. Upgrade for more file uploads and unlimited processing."
    };
    return descriptions[featureName] || "You've reached your limit for this feature. Upgrade for enhanced access.";
  };

  const getFeatureBenefits = (featureName) => {
    const baseBenefits = [
      'Enhanced feature access',
      'Priority AI processing',
      'Advanced analytics & insights',
      'Download notes & test reports',
      'Premium support'
    ];
    
    const featureBenefits = {
      'ai_sessions_monthly': [
        'More AI Tutor conversations per month',
        'Advanced problem-solving guidance',
        'Personalized study recommendations',
        'Dual AI (Professor + Mentor) responses',
        ...baseBenefits.slice(1)
      ],
      'mentor_tips_daily': [
        'Daily motivational mentor tips',
        'Personalized encouragement',
        'Study habit improvement guidance',
        'Mental wellness support',
        ...baseBenefits.slice(1)
      ],
      'mock_tests_weekly': [
        'More mock tests per week',
        'Detailed performance analytics',
        'Subject-wise improvement tracking',
        'Adaptive difficulty adjustment',
        ...baseBenefits.slice(1)
      ],
      'auto_note_uploads_daily': [
        'More file uploads daily',
        'Support for all file formats',
        'AI-powered note structuring',
        'Auto-generated flashcards',
        ...baseBenefits.slice(1)
      ]
    };
    
    return featureBenefits[featureName] || baseBenefits;
  };

  const trackFeatureUsage = async (featureName) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      await axios.post(`${API}/subscription/track-usage`, 
        { feature_name: featureName }, 
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      // Refresh usage after tracking
      await fetchDailyUsage();
    } catch (error) {
      console.error('Usage tracking failed:', error);
    }
  };

  const fetchDailyUsage = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await axios.get(`${API}/subscription/usage`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.data) {
        setDailyUsage(response.data.daily_usage || {});
      }
    } catch (error) {
      console.error('Failed to fetch daily usage:', error);
    }
  };

  const upgradeSubscription = async (targetTier, billingCycle = 'monthly') => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) throw new Error('Not authenticated');

      const response = await axios.post(`${API}/subscription/upgrade`, {
        target_tier: targetTier,
        billing_cycle: billingCycle
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.data.upgraded) {
        // Refresh subscription info
        await fetchSubscriptionInfo();
        setUpsellModal(null); // Close upsell modal
        
        return {
          success: true,
          message: response.data.message,
          newTier: response.data.new_tier
        };
      }
    } catch (error) {
      console.error('Subscription upgrade failed:', error);
      return {
        success: false,
        message: error.response?.data?.detail || 'Upgrade failed'
      };
    }
  };

  const handleUpsellResponse = async (interactionId, response) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      await axios.post(`${API}/subscription/upsell-response`, {
        interaction_id: interactionId,
        response: response
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response === 'dismissed' || response === 'later') {
        setUpsellModal(null);
      }
    } catch (error) {
      console.error('Upsell response failed:', error);
    }
  };

  const getFeatureLimit = (featureName) => {
    if (!subscriptionInfo?.plan_info?.features) return 0;
    const limit = subscriptionInfo.plan_info.features[featureName];
    return limit === 'unlimited' ? Infinity : (limit === 'locked' ? 0 : limit || 0);
  };

  const getFeatureUsage = (featureName) => {
    return dailyUsage[featureName] || 0;
  };

  const getFeatureRemaining = (featureName) => {
    const limit = getFeatureLimit(featureName);
    const usage = getFeatureUsage(featureName);
    return limit === Infinity ? Infinity : Math.max(0, limit - usage);
  };

  const isFeatureUnlimited = (featureName) => {
    const limit = getFeatureLimit(featureName);
    return limit === Infinity;
  };

  const isFeatureLocked = (featureName) => {
    if (!subscriptionInfo?.plan_info?.features) return false;
    return subscriptionInfo.plan_info.features[featureName] === 'locked';
  };

  // Helper to programmatically trigger upsell modal for a feature
  const triggerFeatureUpsell = async (featureName) => {
    try {
      const accessInfo = await checkFeatureAccess(featureName);
      if (!accessInfo.has_access && accessInfo.upsell_info) {
        const modalData = {
          featureName,
          upsellInfo: accessInfo.upsell_info,
          currentUsage: accessInfo.used || accessInfo.current_usage || 0,
          limit: accessInfo.limit,
          title: getFeatureTitle(featureName),
          description: getFeatureDescription(featureName),
          benefits: getFeatureBenefits(featureName)
        };
        setUpsellModal(modalData);
        return true; // Modal triggered
      }
      return false; // No modal needed
    } catch (error) {
      console.error('Failed to trigger upsell modal:', error);
      return false;
    }
  };

  useEffect(() => {
    fetchSubscriptionInfo();
  }, []);

  const value = {
    // State
    subscriptionInfo,
    dailyUsage,
    loading,
    upsellModal,
    
    // Actions
    fetchSubscriptionInfo,
    checkFeatureAccess,
    trackFeatureUsage,
    fetchDailyUsage,
    upgradeSubscription,
    handleUpsellResponse,
    setUpsellModal,
    triggerFeatureUpsell,
    openUpsellModal,
    
    // Helper functions
    getFeatureLimit,
    getFeatureUsage,
    getFeatureRemaining,
    isFeatureUnlimited,
    isFeatureLocked,
    
    // Current tier info
    currentTier: subscriptionInfo?.subscription_tier || 'FREE',
    planInfo: subscriptionInfo?.plan_info || null
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
}

export function useSubscription() {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
}

export default SubscriptionContext;