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

// V1 SIMPLIFIED PRICING - 3 Tiers Only
export const PLANS_CONFIG = {
  FREE: {
    id: 'FREE',
    display_name: '🆓 Free Forever',
    short_name: 'Free',
    price_monthly: 0,
    price_quarterly: 0,
    price_yearly: 0,
    tagline: 'Perfect for exploring AI learning',
    description: 'Try Dhruv AI risk-free with daily question limits',
    emoji: '🆓',
    color: 'gray',
    features: {
      ai_sessions_monthly: 10,  // 10 questions per day
      image_uploads: true,
      hinglish_support: true,
      whatsapp_share: true,
      gamification: 'basic',
      priority_support: false
    },
    highlight: false
  },
  
  STUDENT: {
    id: 'STUDENT',
    display_name: '🎓 Student Plan',
    short_name: 'Student',
    price_monthly: 199,
    price_quarterly: 499,  // ₹166/month - Save ₹98
    price_yearly: 1799,  // ₹150/month - Save ₹589
    tagline: 'Most popular for regular learners',
    description: 'Perfect for students who want unlimited AI help with homework and exam prep',
    emoji: '🎓',
    color: 'blue',
    features: {
      ai_sessions_monthly: 'unlimited',
      mock_tests_weekly: 3,
      auto_note_uploads_daily: 'unlimited',
      mentor_tips_daily: 5,
      image_uploads: 'unlimited',
      hinglish_support: true,
      whatsapp_share: true,
      gamification: 'full',
      priority_support: false,
      response_speed: 'standard',
      voice_mode: 'mentor_only',
      analytics_tier: 'advanced',
      export_notes: true,
      concept_tagging: true
    },
    highlight: true,
    badge: 'MOST POPULAR',
    savings: {
      quarterly: 'Save ₹98',
      yearly: 'Save ₹589'
    }
  },
  
  PRO: {
    id: 'PRO',
    display_name: '⭐ Pro Plan',
    short_name: 'Pro',
    price_monthly: 299,
    price_quarterly: 799,  // ₹267/month - Save ₹98
    price_yearly: 2999,  // ₹250/month - Save ₹589
    tagline: 'Unlimited everything for serious students',
    description: 'Best for JEE, NEET, CBSE students who need unlimited AI support',
    emoji: '⭐',
    color: 'purple',
    features: {
      ai_sessions_monthly: 'unlimited',
      mock_tests_weekly: 'unlimited',
      auto_note_uploads_daily: 'unlimited',
      mentor_tips_daily: 'unlimited',
      image_uploads: 'unlimited',
      hinglish_support: true,
      whatsapp_share: true,
      gamification: 'full',
      priority_support: true,
      response_speed: 'priority',
      early_access: true,
      voice_mode: 'full_sync',
      analytics_tier: 'deep',
      export_notes: true,
      concept_tagging: true,
      offline_mode: true,
      parent_dashboard: true,
      advanced_ocr: true,
      emotion_aware_ai: true
    },
    highlight: false,
    savings: {
      quarterly: 'Save ₹98',
      yearly: 'Save ₹589'
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
 * Get featured plans for landing page (V1 - Student and Pro)
 */
export const getFeaturedPlans = () => {
  return [PLANS_CONFIG.STUDENT, PLANS_CONFIG.PRO];
};

/**
 * Get all plans in order (V1 - 3 tiers only)
 */
export const getAllPlans = () => {
  return [
    PLANS_CONFIG.FREE,
    PLANS_CONFIG.STUDENT,
    PLANS_CONFIG.PRO
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
 * Get upgrade path from current tier (V1 - simplified)
 */
export const getUpgradePath = (currentTier) => {
  const tierOrder = ['FREE', 'STUDENT', 'PRO'];
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
