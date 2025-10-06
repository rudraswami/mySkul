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
      // Set default FREE tier on error
      setSubscriptionInfo({
        subscription_tier: 'FREE',
        plan_info: {
          display_name: '🧩 Free - The Explorer',
          features: {
            ai_tutor_daily: 5,
            mock_tests_weekly: 1,
            auto_note_uploads_daily: 1
          }
        },
        daily_usage: {}
      });
    } finally {
      setLoading(false);
    }
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
      
      // If it's an upsell situation (402), show upsell modal
      if (error.response?.status === 402) {
        const errorData = error.response.data;
        if (errorData.detail?.upsell_info) {
          setUpsellModal({
            featureName,
            upsellInfo: errorData.detail.upsell_info,
            currentUsage: errorData.detail.current_usage,
            limit: errorData.detail.limit
          });
        }
        return { 
          has_access: false, 
          upgrade_needed: true,
          upsell_info: errorData.detail?.upsell_info
        };
      }
      
      return { has_access: true, upgrade_needed: false }; // Fail open
    }
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