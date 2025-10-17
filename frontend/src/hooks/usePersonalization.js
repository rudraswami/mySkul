/**
 * usePersonalization Hook
 * 
 * Manages user personalization data - XP, streaks, mastery, levels
 * 
 * @returns {Object} Personalization state and operations
 */

import { useState, useCallback, useEffect } from 'react';
import client from '../api/client';

export const usePersonalization = () => {
  const [xpInfo, setXPInfo] = useState({
    total_xp: 0,
    current_level: 1,
    progress_percentage: 0,
    xp_for_next_level: 100
  });
  
  const [streakInfo, setStreakInfo] = useState({
    current_streak: 0,
    longest_streak: 0,
    last_activity_date: null
  });
  
  const [topicMastery, setTopicMastery] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Load personalization data from backend
   */
  const loadPersonalization = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await client.get('/personalization/profile');
      
      if (response.data) {
        // Update XP info
        if (response.data.xp_info) {
          setXPInfo(prev => ({
            ...prev,
            ...response.data.xp_info
          }));
        }
        
        // Update streak info
        if (response.data.streak_info) {
          setStreakInfo(prev => ({
            ...prev,
            ...response.data.streak_info
          }));
        }
        
        // Update topic mastery
        if (response.data.topic_mastery) {
          setTopicMastery(response.data.topic_mastery);
        }
      }
    } catch (err) {
      console.error('Failed to load personalization data:', err);
      setError(err.message || 'Failed to load personalization data');
      // Set default values on error
      setXPInfo({ total_xp: 0, current_level: 1, progress_percentage: 0, xp_for_next_level: 100 });
      setStreakInfo({ current_streak: 0, longest_streak: 0, last_activity_date: null });
      setTopicMastery({});
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Handle XP gain from an action
   * 
   * @param {Object} xpResult - XP result from backend
   */
  const handleXPGain = useCallback((xpResult) => {
    if (!xpResult) return;

    const {
      xp_gained,
      total_xp,
      current_level,
      level_up,
      progress_percentage,
      xp_for_next_level
    } = xpResult;

    // Update XP info
    setXPInfo({
      total_xp: total_xp || xpInfo.total_xp,
      current_level: current_level || xpInfo.current_level,
      progress_percentage: progress_percentage || 0,
      xp_for_next_level: xp_for_next_level || 100
    });

    // Show feedback if level up occurred
    if (level_up) {
      console.log(`🎉 Level up! Now at level ${current_level}`);
      // TODO: Show level up animation/toast
    }

    if (xp_gained > 0) {
      console.log(`⭐ +${xp_gained} XP gained!`);
      // TODO: Show XP gain animation
    }
  }, [xpInfo]);

  /**
   * Update topic mastery after completing an activity
   * 
   * @param {string} topic - Topic name
   * @param {number} score - Score/performance (0-100)
   */
  const updateTopicMastery = useCallback((topic, score) => {
    setTopicMastery(prev => ({
      ...prev,
      [topic]: {
        score,
        last_practiced: new Date().toISOString(),
        attempts: (prev[topic]?.attempts || 0) + 1
      }
    }));
  }, []);

  /**
   * Update streak after an activity
   * 
   * @param {Object} newStreakInfo - Updated streak info
   */
  const updateStreak = useCallback((newStreakInfo) => {
    if (!newStreakInfo) return;
    
    setStreakInfo(prev => ({
      ...prev,
      ...newStreakInfo
    }));
  }, []);

  /**
   * Calculate XP required for a given level
   * 
   * @param {number} level - Target level
   * @returns {number} - XP required
   */
  const getXPForLevel = useCallback((level) => {
    // XP formula: 100 * (level ^ 1.5)
    // Level 1: 100 XP
    // Level 2: 282 XP
    // Level 3: 519 XP
    // Level 5: 1118 XP
    // Level 10: 3162 XP
    return Math.floor(100 * Math.pow(level, 1.5));
  }, []);

  /**
   * Get mastery level for a topic
   * 
   * @param {string} topic - Topic name
   * @returns {string} - Mastery level (beginner, intermediate, advanced, expert)
   */
  const getMasteryLevel = useCallback((topic) => {
    const mastery = topicMastery[topic];
    if (!mastery || !mastery.score) return 'beginner';
    
    if (mastery.score >= 90) return 'expert';
    if (mastery.score >= 75) return 'advanced';
    if (mastery.score >= 50) return 'intermediate';
    return 'beginner';
  }, [topicMastery]);

  /**
   * Load personalization data on mount
   */
  useEffect(() => {
    loadPersonalization();
  }, [loadPersonalization]);

  return {
    // State
    xpInfo,
    streakInfo,
    topicMastery,
    loading,
    error,
    
    // Operations
    loadPersonalization,
    handleXPGain,
    updateTopicMastery,
    updateStreak,
    getXPForLevel,
    getMasteryLevel
  };
};

export default usePersonalization;
