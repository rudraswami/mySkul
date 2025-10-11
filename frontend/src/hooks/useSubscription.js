/**
 * React Query hooks for Subscription module
 * Replaces ad-hoc fetch calls with cached, auto-refetching queries
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { subscriptionAPI } from '../api/client';

// Query keys for cache management
export const subscriptionKeys = {
  all: ['subscription'],
  plans: () => [...subscriptionKeys.all, 'plans'],
  current: () => [...subscriptionKeys.all, 'current'],
  info: () => [...subscriptionKeys.all, 'info'],
  access: (featureName) => [...subscriptionKeys.all, 'access', featureName],
};

/**
 * Hook to fetch subscription plans
 */
export function useSubscriptionPlans() {
  return useQuery({
    queryKey: subscriptionKeys.plans(),
    queryFn: async () => {
      const response = await subscriptionAPI.getPlans();
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // Plans rarely change - 10 min freshness
  });
}

/**
 * Hook to fetch current user subscription
 */
export function useCurrentSubscription() {
  return useQuery({
    queryKey: subscriptionKeys.current(),
    queryFn: async () => {
      const response = await subscriptionAPI.getCurrentSubscription();
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes freshness
    retry: 2,
  });
}

/**
 * Hook to fetch subscription info with usage stats
 */
export function useSubscriptionInfo() {
  return useQuery({
    queryKey: subscriptionKeys.info(),
    queryFn: async () => {
      const response = await subscriptionAPI.getSubscriptionInfo();
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute freshness for usage data
  });
}

/**
 * Hook to check feature access
 */
export function useFeatureAccess(featureName) {
  return useQuery({
    queryKey: subscriptionKeys.access(featureName),
    queryFn: async () => {
      const response = await subscriptionAPI.checkAccess(featureName);
      return response.data;
    },
    enabled: !!featureName, // Only run if feature name provided
    staleTime: 30 * 1000, // 30 seconds - access can change frequently
    retry: (failureCount, error) => {
      // Don't retry on 402 Payment Required
      if (error.response?.status === 402) {
        return false;
      }
      return failureCount < 2;
    },
  });
}

/**
 * Hook to track feature usage
 */
export function useTrackUsage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ featureName, amount = 1 }) => {
      const response = await subscriptionAPI.trackUsage(featureName, amount);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate subscription info to refresh usage stats
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.info() });
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.current() });
    },
  });
}

/**
 * Hook to upgrade subscription
 */
export function useUpgradeSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ targetTier, billingCycle }) => {
      const response = await subscriptionAPI.upgradeSubscription(targetTier, billingCycle);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate all subscription queries after upgrade
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.all });
    },
  });
}
