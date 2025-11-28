/**
 * 🎮 useGamification Hook
 * 
 * Manages all gamification state and interactions:
 * - Student stats (XP, level, streak)
 * - Micro rewards
 * - Level ups
 * - Badges
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

/**
 * Main gamification hook
 */
export function useGamification(userId) {
  // State
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Reward state (for displaying celebrations)
  const [currentReward, setCurrentReward] = useState(null);
  const [levelUp, setLevelUp] = useState(null);
  const [streakCelebration, setStreakCelebration] = useState(null);
  
  // Track pending rewards
  const rewardQueue = useRef([]);
  const isProcessingReward = useRef(false);
  
  /**
   * Fetch student stats
   */
  const fetchStats = useCallback(async () => {
    if (!userId) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/gamification/stats/${userId}`);
      setStats(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching gamification stats:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);
  
  /**
   * Process an interaction (question/answer)
   */
  const processInteraction = useCallback(async ({
    interactionType = 'question',
    isCorrect = true,
    responseTimeMs = 0,
    concept = '',
    subject = ''
  }) => {
    if (!userId) return null;
    
    try {
      const response = await axios.post(`${API_BASE}/gamification/interaction`, {
        user_id: userId,
        interaction_type: interactionType,
        is_correct: isCorrect,
        response_time_ms: responseTimeMs,
        concept,
        subject
      });
      
      const result = response.data;
      
      // Queue rewards for display
      if (result.micro_reward) {
        queueReward(result.micro_reward);
      }
      
      // Check for level up
      if (result.level_up) {
        setLevelUp(result.level_up);
      }
      
      // Check for streak badge
      if (result.streak_update?.badge_earned) {
        setStreakCelebration({
          streakDays: result.streak_update.new_streak,
          badgeEarned: result.streak_update.badge_earned
        });
      }
      
      // Update stats
      if (result.level_progress) {
        setStats(prev => ({
          ...prev,
          level: result.level_progress,
          streak: {
            ...prev?.streak,
            current: result.streak_update?.new_streak || prev?.streak?.current
          }
        }));
      }
      
      return result;
    } catch (err) {
      console.error('Error processing interaction:', err);
      return null;
    }
  }, [userId]);
  
  /**
   * Queue a reward for display
   */
  const queueReward = useCallback((reward) => {
    rewardQueue.current.push(reward);
    processRewardQueue();
  }, []);
  
  /**
   * Process reward queue (show one at a time)
   */
  const processRewardQueue = useCallback(() => {
    if (isProcessingReward.current || rewardQueue.current.length === 0) {
      return;
    }
    
    isProcessingReward.current = true;
    const reward = rewardQueue.current.shift();
    setCurrentReward(reward);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      setCurrentReward(null);
      isProcessingReward.current = false;
      processRewardQueue(); // Process next in queue
    }, 3000);
  }, []);
  
  /**
   * Dismiss current reward
   */
  const dismissReward = useCallback(() => {
    setCurrentReward(null);
    isProcessingReward.current = false;
    processRewardQueue();
  }, [processRewardQueue]);
  
  /**
   * Dismiss level up celebration
   */
  const dismissLevelUp = useCallback(() => {
    setLevelUp(null);
  }, []);
  
  /**
   * Dismiss streak celebration
   */
  const dismissStreakCelebration = useCallback(() => {
    setStreakCelebration(null);
  }, []);
  
  /**
   * Get a random encouragement message
   */
  const getEncouragement = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/gamification/micro-reward/encouragement`);
      return response.data;
    } catch (err) {
      console.error('Error getting encouragement:', err);
      return {
        message: "Keep going! You've got this! 💪",
        emoji: "💪",
        xp_earned: 2,
        celebration_type: "pulse"
      };
    }
  }, []);
  
  /**
   * Manually trigger a celebration (for testing)
   */
  const triggerCelebration = useCallback((type, data = {}) => {
    switch (type) {
      case 'correct':
        queueReward({
          message: "Boom! You nailed it! 🎉",
          emoji: "🎉",
          xp_earned: 10,
          celebration_type: "confetti"
        });
        break;
      case 'streak':
        setStreakCelebration({
          streakDays: data.days || 7,
          badgeEarned: data.badge || "blue_streak"
        });
        break;
      case 'levelup':
        setLevelUp({
          old_level: data.oldLevel || "Explorer",
          new_level: data.newLevel || "Analyst"
        });
        break;
      default:
        break;
    }
  }, [queueReward]);
  
  // Fetch stats on mount and when userId changes
  useEffect(() => {
    fetchStats();
  }, [fetchStats]);
  
  return {
    // State
    stats,
    loading,
    error,
    
    // Celebration state
    currentReward,
    levelUp,
    streakCelebration,
    
    // Actions
    fetchStats,
    processInteraction,
    dismissReward,
    dismissLevelUp,
    dismissStreakCelebration,
    getEncouragement,
    triggerCelebration,
    
    // Computed values
    level: stats?.level?.level_name || 'Explorer',
    xp: stats?.level?.current_xp || 0,
    streak: stats?.streak?.current || 0,
    todayQuestions: stats?.today?.questions || 0,
    todayAccuracy: stats?.today?.accuracy || 0,
    badges: stats?.badges || []
  };
}

/**
 * Hook for just displaying compact progress (no interaction processing)
 */
export function useCompactProgress(userId) {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (!userId) return;
    
    const fetchProgress = async () => {
      try {
        const response = await axios.get(`${API_BASE}/gamification/stats/${userId}`);
        setProgress({
          level: response.data.level,
          streak: response.data.streak
        });
      } catch (err) {
        console.error('Error fetching progress:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProgress();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchProgress, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [userId]);
  
  return { progress, loading };
}

export default useGamification;



