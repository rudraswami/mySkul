/**
 * 🎮 Gamification Components Index
 * 
 * Export all gamification components for easy importing
 */

export { default as MicroReward, StreakCelebration, LevelUpCelebration, XPPopup } from './MicroReward';
export { default as ProgressDashboard, CompactProgress, LevelCard, StreakCard, TodayStats, BadgesCard } from './ProgressDashboard';

// Re-export hook for convenience
export { useGamification, useCompactProgress } from '../../hooks/useGamification';



