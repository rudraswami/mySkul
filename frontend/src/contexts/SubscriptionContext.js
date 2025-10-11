import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SubscriptionContext = createContext();

export function SubscriptionProvider({ children }) {
  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  const [dailyUsage, setDailyUsage] = useState({});
  const [loading, setLoading] = useState(true);
  const [upsellModal, setUpsellModal] = useState(null);

  const fetchSubscriptionInfo = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return;

      const response = await axios.get(`${API}/subscription/info`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.data) {
        setSubscriptionInfo(response.data);
        setDailyUsage(response.data.daily_usage || {});
      }
    } catch (error) {
      console.error('Failed to fetch subscription info:', error);
      // Set default FREE tier on error - use planConfig_ai_tutor.json values
      setSubscriptionInfo({
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
        daily_usage: {}
      });
    } finally {
      setLoading(false);
    }
  };

  const openUpsellModal = (featureName, detailLike) => {
    if (!detailLike) detailLike = {};
    const upsellInfo = detailLike.upsell_info || detailLike;
    const modalData = {
      featureName,
      upsellInfo,
      currentUsage: detailLike.used || detailLike.current_usage || 0,
      limit: detailLike.limit || 0,
      title: getFeatureTitle(featureName),
      description: getFeatureDescription(featureName),
      benefits: getFeatureBenefits(featureName)
    };
    setUpsellModal(modalData);
    return modalData;
  };

  const checkFeatureAccess = async (featureName) => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) return { has_access: false, upgrade_needed: true };

      const response = await axios.post(`${API}/subscription/check-access`, 
        { feature_name: featureName }, 
        { headers: { 'Authorization': `Bearer ${token}` } }
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
        return { 
          has_access: false, 
          upgrade_needed: true,
          reason: detail?.reason || 'limit_reached',
          upsell_info: detail?.upsell_info
        };
      }
      
      // SECURITY FIX: Don't fail open on errors - deny access by default
      // This prevents bypassing limits when there are network/server errors
      console.error('❌ Feature access check error - denying access by default');
      return { 
        has_access: false, 
        upgrade_needed: false,
        error: true,
        message: 'Unable to verify access. Please try again.'
      };
    }
  };

  // Helper functions for market-standard messaging
  const getFeatureTitle = (featureName) => {
    const titles = {
      'ai_tutor_daily': '🎓 Unlock Unlimited AI Tutoring',
      'mock_tests_weekly': '🏆 Access More Mock Tests',
      'auto_note_recordings_daily': '🎤 Record Unlimited Classes',
      'auto_note_uploads_daily': '📁 Upload More Files'
    };
    return titles[featureName] || '⚡ Upgrade Your Learning';
  };

  const getFeatureDescription = (featureName) => {
    const descriptions = {
      'ai_tutor_daily': "You've reached your daily AI Tutor limit. Upgrade to Premium for unlimited conversations with your personal AI Professor and Mentor.",
      'mock_tests_weekly': "You've used all your mock tests this week. Upgrade to Premium for unlimited practice tests and detailed performance analytics.",
      'auto_note_recordings_daily': "You've reached your daily recording limit. Upgrade to Premium for unlimited live recording sessions.",
      'auto_note_uploads_daily': "You've reached your daily upload limit. Upgrade to Premium for unlimited file uploads and processing."
    };
    return descriptions[featureName] || "You've reached your limit for this feature. Upgrade to Premium for unlimited access.";
  };

  const getFeatureBenefits = (featureName) => {
    const baseBenefits = [
      'Unlimited access to all features',
      'Priority AI processing',
      'Advanced analytics & insights',
      'Download notes & test reports',
      '24/7 premium support'
    ];
    
    const featureBenefits = {
      'ai_tutor_daily': [
        'Unlimited AI conversations',
        'Advanced problem-solving guidance',
        'Personalized study recommendations',
        ...baseBenefits.slice(1)
      ],
      'mock_tests_weekly': [
        'Unlimited mock tests',
        'Detailed performance analytics',
        'Subject-wise improvement tracking',
        ...baseBenefits.slice(1)
      ],
      'auto_note_recordings_daily': [
        'Unlimited live recordings',
        'Real-time transcription',
        'Auto-generated flashcards',
        ...baseBenefits.slice(1)
      ],
      'auto_note_uploads_daily': [
        'Unlimited file uploads',
        'Support for all file formats',
        'Bulk processing capabilities',
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