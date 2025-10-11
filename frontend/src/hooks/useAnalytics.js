/**
 * React Query hooks for Analytics module
 * Replaces ad-hoc fetch calls with cached, auto-refetching queries
 */
import { useQuery } from '@tanstack/react-query';
import { analyticsAPI } from '../api/client';

// Query keys for cache management
export const analyticsKeys = {
  all: ['analytics'],
  dashboard: () => [...analyticsKeys.all, 'dashboard'],
  dailyGoals: () => [...analyticsKeys.all, 'daily-goals'],
  subjectProgress: () => [...analyticsKeys.all, 'subject-progress'],
  wellnessCheck: () => [...analyticsKeys.all, 'wellness-check'],
};

/**
 * Hook to fetch dashboard analytics
 */
export function useDashboardAnalytics() {
  return useQuery({
    queryKey: analyticsKeys.dashboard(),
    queryFn: async () => {
      const response = await analyticsAPI.getDashboard();
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes freshness for dashboard data
    retry: 2,
  });
}

/**
 * Hook to fetch daily goals
 */
export function useDailyGoals() {
  return useQuery({
    queryKey: analyticsKeys.dailyGoals(),
    queryFn: async () => {
      const response = await analyticsAPI.getDailyGoals();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes freshness for goals
  });
}

/**
 * Hook to fetch subject progress
 */
export function useSubjectProgress() {
  return useQuery({
    queryKey: analyticsKeys.subjectProgress(),
    queryFn: async () => {
      const response = await analyticsAPI.getSubjectProgress();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes freshness for progress data
  });
}

/**
 * Hook to fetch wellness check data
 */
export function useWellnessCheck() {
  return useQuery({
    queryKey: analyticsKeys.wellnessCheck(),
    queryFn: async () => {
      const response = await analyticsAPI.getWellnessCheck();
      return response.data;
    },
    staleTime: 30 * 60 * 1000, // 30 minutes freshness for wellness data
    retry: 1, // Less aggressive retry for wellness checks
  });
}