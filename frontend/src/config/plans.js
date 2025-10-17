/**
 * SINGLE SOURCE OF TRUTH FOR SUBSCRIPTION PLANS
 * 
 * This file mirrors the backend planConfig_ai_tutor.json
 * All components must import from here - NO HARDCODED PRICES
 * 
 * Last synced with backend: January 17, 2025
 */

export const PLAN_TIERS = {
  FREE: 'FREE',
  STARTER: 'STARTER',
  SCHOLAR: 'SCHOLAR',
  ACHIEVER: 'ACHIEVER',
  LEGEND: 'LEGEND'
};

export const PLANS_CONFIG = {
  FREE: {
    id: 'FREE',
    display_name: '🆓 Free - Try Before You Commit',
    short_name: 'Free',
    price_monthly: 0,
    price_quarterly: 0,
    price_yearly: 0,
    tagline: 'Explore AI learning at your own pace',
    description: 'Get started with AI Tutor basics - 10 sessions to experience the power of AI learning',
    emoji: '🆓',
    color: 'gray',
    features: {
      ai_sessions_monthly: 10,
      mentor_tips_daily: 0,
      mock_tests_weekly: 1,
      auto_note_uploads_daily: 1,
      analytics_tier: 'basic',
      priority_support: false
    },
    highlight: false
  },
  
  STARTER: {
    id: 'STARTER',
    display_name: '🟢 Starter - Begin Your AI Journey',
    short_name: 'Starter',
    price_monthly: 199,
    price_quarterly: 499,
    price_yearly: 1699,
    tagline: 'Begin your AI journey - Student friendly',
    description: 'Perfect for students exploring AI-powered learning without breaking the bank',
    emoji: '🟢',
    color: 'green',
    features: {
      ai_sessions_monthly: 20,
      mentor_tips_daily: 0,
      mock_tests_weekly: 2,
      auto_note_uploads_daily: 3,
      analytics_tier: 'basic',
      priority_support: false,
      export_notes: true
    },
    student_verified_price: {
      monthly: 149,
      quarterly: 399,
      yearly: 1349
    },
    highlight: false,
    savings: {
      quarterly: 'Save ₹98',
      yearly: 'Save ₹689'
    }
  },
  
  SCHOLAR: {
    id: 'SCHOLAR',
    display_name: '🔵 Scholar - Master Concepts with Smart Guidance',
    short_name: 'Scholar',
    price_monthly: 499,
    price_quarterly: 1299,
    price_yearly: 4499,
    tagline: 'Master concepts with smart guidance - Most popular',
    description: 'Ideal for serious students preparing for competitive exams like JEE, NEET, UPSC',
    emoji: '🔵',
    color: 'blue',
    features: {
      ai_sessions_monthly: 100,
      mentor_tips_daily: 5,
      mock_tests_weekly: 5,
      auto_note_uploads_daily: 'unlimited',
      analytics_tier: 'advanced',
      priority_support: false,
      export_notes: true,
      concept_tagging: true
    },
    student_verified_price: {
      monthly: 399,
      quarterly: 1099,
      yearly: 3799
    },
    highlight: true,
    badge: 'MOST POPULAR',
    savings: {
      quarterly: 'Save ₹198',
      yearly: 'Save ₹1487'
    }
  },
  
  ACHIEVER: {
    id: 'ACHIEVER',
    display_name: '🟠 Achiever (Pro) - Your AI Mentor for Competitive Success',
    short_name: 'Achiever',
    price_monthly: 999,
    price_quarterly: 2699,
    price_yearly: 8999,
    tagline: 'Your AI mentor for competitive success - Premium features',
    description: 'For students committed to excellence, top percentile scores, and AIR ranks',
    emoji: '🟠',
    color: 'orange',
    features: {
      ai_sessions_monthly: 300,
      mentor_tips_daily: 30,
      mock_tests_weekly: 'unlimited',
      auto_note_uploads_daily: 'unlimited',
      analytics_tier: 'deep',
      priority_support: true,
      export_notes: true,
      concept_tagging: true,
      offline_mode: true,
      voice_mode: true
    },
    student_verified_price: {
      monthly: 799,
      quarterly: 2199,
      yearly: 7499
    },
    highlight: false,
    savings: {
      quarterly: 'Save ₹298',
      yearly: 'Save ₹2992'
    }
  },
  
  LEGEND: {
    id: 'LEGEND',
    display_name: '🟣 Legend (Elite) - Personal AI Mentor, 24×7 Learning Lab',
    short_name: 'Legend',
    price_monthly: 1999,
    price_quarterly: 5499,
    price_yearly: 18999,
    tagline: 'Personal AI mentor, 24×7 learning lab - Elite coaching',
    description: 'The ultimate learning experience for top aspirants targeting AIR single-digit ranks',
    emoji: '🟣',
    color: 'purple',
    features: {
      ai_sessions_monthly: 'unlimited',
      mentor_tips_daily: 'unlimited',
      mock_tests_weekly: 'unlimited',
      auto_note_uploads_daily: 'unlimited',
      analytics_tier: 'premium',
      priority_support: true,
      export_notes: true,
      concept_tagging: true,
      offline_mode: true,
      voice_mode: true,
      dedicated_mentor: true,
      custom_study_plan: true
    },
    student_verified_price: {
      monthly: 1599,
      quarterly: 4499,
      yearly: 15999
    },
    highlight: false,
    badge: 'ELITE',
    savings: {
      quarterly: 'Save ₹498',
      yearly: 'Save ₹5003'
    }
  }
};

/**
 * Get plan by tier ID
 */
export const getPlanByTier = (tier) => {
  return PLANS_CONFIG[tier] || PLANS_CONFIG.FREE;
};

/**
 * Get all paid plans (excluding FREE)
 */
export const getPaidPlans = () => {
  return Object.values(PLANS_CONFIG).filter(plan => plan.id !== 'FREE');
};

/**
 * Get featured plans for landing page (typically SCHOLAR and ACHIEVER)
 */
export const getFeaturedPlans = () => {
  return [PLANS_CONFIG.SCHOLAR, PLANS_CONFIG.ACHIEVER];
};

/**
 * Get all plans in order
 */
export const getAllPlans = () => {
  return [
    PLANS_CONFIG.FREE,
    PLANS_CONFIG.STARTER,
    PLANS_CONFIG.SCHOLAR,
    PLANS_CONFIG.ACHIEVER,
    PLANS_CONFIG.LEGEND
  ];
};

/**
 * Format price with currency
 */
export const formatPrice = (price) => {
  if (price === 0) return 'Free';
  if (price === 'unlimited') return 'Unlimited';
  return `₹${price}`;
};

/**
 * Get upgrade path from current tier
 */
export const getUpgradePath = (currentTier) => {
  const tierOrder = ['FREE', 'STARTER', 'SCHOLAR', 'ACHIEVER', 'LEGEND'];
  const currentIndex = tierOrder.indexOf(currentTier);
  
  if (currentIndex === -1 || currentIndex === tierOrder.length - 1) {
    return null;
  }
  
  return tierOrder[currentIndex + 1];
};

/**
 * Check if tier has feature
 */
export const hasPlanFeature = (tier, featureName) => {
  const plan = getPlanByTier(tier);
  return plan?.features?.[featureName] || false;
};

export default PLANS_CONFIG;
