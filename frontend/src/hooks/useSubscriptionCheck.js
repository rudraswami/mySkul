/**
 * useSubscriptionCheck Hook
 * 
 * Manages subscription feature access checks and usage tracking
 * 
 * @returns {Object} Subscription check state and operations
 */

import { useState, useCallback } from 'react';
import client from '../api/client';
import { getPlanByTier } from '../config/plans';

export const useSubscriptionCheck = () => {
  const [canUseFeature, setCanUseFeature] = useState(true);
  const [usage, setUsage] = useState({ used: 0, limit: 0, percentage: 0 });
  const [upgradeHint, setUpgradeHint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Check if user can access a feature
   * 
   * @param {string} featureName - Feature to check (e.g., 'ai_sessions_monthly')
   * @returns {Object} - Access info with has_access, used, limit, etc.
   */
  const checkFeatureAccess = useCallback(async (featureName) => {
    try {
      setLoading(true);
      setError(null);

      const response = await client.post('/subscription/check-access', {
        feature_name: featureName
      });
      const accessData = response.data;

      // Update state
      setCanUseFeature(accessData.has_access);
      
      const usageData = {
        used: accessData.current_usage || accessData.used || 0,
        limit: accessData.total || accessData.limit || 0,
        percentage: accessData.usage_percent || 0
      };
      setUsage(usageData);

      // Handle upgrade hint
      if (accessData.upgrade_hint) {
        const targetPlan = getPlanByTier(accessData.upgrade_hint.target_plan || 'STARTER');
        
        setUpgradeHint({
          type: accessData.upgrade_hint.type || 'limit_reached',
          mentor_message: accessData.upgrade_hint.mentor_message || 
            'Upgrade to continue your learning journey! 🚀',
          professor_message: accessData.upgrade_hint.professor_message || 
            'Consistent practice is essential for mastery.',
          target_plan: targetPlan.id,
          pricing: {
            monthly: targetPlan.price_monthly,
            quarterly: targetPlan.price_quarterly,
            yearly: targetPlan.price_yearly
          },
          benefits: generateBenefits(targetPlan),
          cta: 'View Plans & Upgrade'
        });
      } else {
        setUpgradeHint(null);
      }

      return accessData;

    } catch (err) {
      console.error('Failed to check feature access:', err);
      setError(err.message || 'Failed to check access');
      
      // Fail open - allow access if check fails (better UX)
      setCanUseFeature(true);
      
      return {
        has_access: true,
        current_usage: 0,
        total: 0,
        usage_percent: 0
      };

    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Generate benefits list for a plan
   * 
   * @param {Object} plan - Plan object from config
   * @returns {Array<string>} - Benefits list
   */
  const generateBenefits = (plan) => {
    const benefits = [];
    const { features } = plan;

    if (features.ai_sessions_monthly === 'unlimited') {
      benefits.push('Unlimited AI Tutor sessions');
    } else if (features.ai_sessions_monthly > 50) {
      benefits.push(`${features.ai_sessions_monthly} AI sessions per month`);
    }

    if (features.mock_tests_weekly === 'unlimited') {
      benefits.push('Unlimited mock tests');
    } else if (features.mock_tests_weekly > 2) {
      benefits.push(`${features.mock_tests_weekly} mock tests weekly`);
    }

    if (features.priority_support) {
      benefits.push('Priority support');
    }

    if (features.voice_mode) {
      benefits.push('Voice mode & offline access');
    }

    if (features.dedicated_mentor) {
      benefits.push('Dedicated AI mentor');
    }

    // Ensure we have at least 3 benefits
    if (benefits.length < 3) {
      benefits.push('Advanced analytics & insights');
      benefits.push('Personalized learning paths');
    }

    return benefits.slice(0, 4); // Max 4 benefits
  };

  /**
   * Track feature usage (optimistic update)
   * 
   * @param {string} featureName - Feature being used
   */
  const trackUsage = useCallback((featureName) => {
    setUsage(prev => ({
      ...prev,
      used: prev.used + 1,
      percentage: prev.limit > 0 ? Math.round(((prev.used + 1) / prev.limit) * 100) : 0
    }));
  }, []);

  /**
   * Clear upgrade hint
   */
  const clearUpgradeHint = useCallback(() => {
    setUpgradeHint(null);
  }, []);

  /**
   * Reset usage tracking (for new billing period)
   */
  const resetUsage = useCallback(() => {
    setUsage({ used: 0, limit: 0, percentage: 0 });
    setCanUseFeature(true);
    setUpgradeHint(null);
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    canUseFeature,
    usage,
    upgradeHint,
    loading,
    error,
    
    // Operations
    checkFeatureAccess,
    trackUsage,
    clearUpgradeHint,
    resetUsage,
    clearError
  };
};

export default useSubscriptionCheck;
