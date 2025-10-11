/**
 * React Query hooks for Mock Tests module
 * Replaces ad-hoc fetch calls with cached, auto-refetching queries
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mockTestsAPI } from '../api/client';

// Query keys for cache management
export const mockTestsKeys = {
  all: ['mock-tests'],
  library: () => [...mockTestsKeys.all, 'library'],
  recentTests: () => [...mockTestsKeys.all, 'recent-tests'],
  dashboard: () => [...mockTestsKeys.all, 'dashboard'],
  performanceTrends: () => [...mockTestsKeys.all, 'performance-trends'],
  subjects: (examType) => [...mockTestsKeys.all, 'subjects', examType],
  detailedReview: (testId) => [...mockTestsKeys.all, 'detailed-review', testId],
  resumeTests: () => [...mockTestsKeys.all, 'resume-tests'],
};

/**
 * Hook to fetch mock tests library
 */
export function useMockTestsLibrary() {
  return useQuery({
    queryKey: mockTestsKeys.library(),
    queryFn: async () => {
      const response = await mockTestsAPI.getLibrary();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes freshness for library
    retry: 2,
  });
}

/**
 * Hook to fetch recent mock tests
 */
export function useRecentMockTests() {
  return useQuery({
    queryKey: mockTestsKeys.recentTests(),
    queryFn: async () => {
      const response = await mockTestsAPI.getRecentTests();
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute freshness for recent tests
  });
}

/**
 * Hook to fetch mock tests dashboard data
 */
export function useMockTestsDashboard() {
  return useQuery({
    queryKey: mockTestsKeys.dashboard(),
    queryFn: async () => {
      const response = await mockTestsAPI.getDashboard();
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes freshness for dashboard
  });
}

/**
 * Hook to fetch performance trends
 */
export function useMockTestsPerformanceTrends() {
  return useQuery({
    queryKey: mockTestsKeys.performanceTrends(),
    queryFn: async () => {
      const response = await mockTestsAPI.getPerformanceTrends();
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes freshness for trends
  });
}

/**
 * Hook to fetch subjects for an exam type
 */
export function useMockTestsSubjects(examType) {
  return useQuery({
    queryKey: mockTestsKeys.subjects(examType),
    queryFn: async () => {
      const response = await mockTestsAPI.getSubjects(examType);
      return response.data;
    },
    enabled: !!examType, // Only run if exam type provided
    staleTime: 30 * 60 * 1000, // 30 minutes freshness for subjects (rarely change)
  });
}

/**
 * Hook to fetch detailed review for a test
 */
export function useMockTestDetailedReview(testId) {
  return useQuery({
    queryKey: mockTestsKeys.detailedReview(testId),
    queryFn: async () => {
      const response = await mockTestsAPI.getDetailedReview(testId);
      return response.data;
    },
    enabled: !!testId, // Only run if test ID provided
    staleTime: 60 * 60 * 1000, // 1 hour freshness for detailed reviews
  });
}

/**
 * Hook to fetch resumable tests
 */
export function useMockTestsResumeTests() {
  return useQuery({
    queryKey: mockTestsKeys.resumeTests(),
    queryFn: async () => {
      const response = await mockTestsAPI.getResumeTests();
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute freshness for resume tests
  });
}

/**
 * Hook to invalidate all mock tests data
 * Useful after completing a test or other state changes
 */
export function useInvalidateMockTests() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: mockTestsKeys.all });
  };
}