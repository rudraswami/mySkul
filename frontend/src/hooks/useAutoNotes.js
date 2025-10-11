/**
 * React Query hooks for Auto-Notes module
 * Replaces ad-hoc fetch calls with cached, auto-refetching queries
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { autoNotesAPI } from '../api/client';

// Query keys for cache management
export const autoNotesKeys = {
  all: ['auto-notes'],
  sessions: () => [...autoNotesKeys.all, 'sessions'],
  session: (sessionId) => [...autoNotesKeys.all, 'session', sessionId],
  analytics: () => [...autoNotesKeys.all, 'analytics'],
  classSeries: () => [...autoNotesKeys.all, 'class-series'],
};

/**
 * Hook to fetch auto-notes sessions list
 */
export function useAutoNotesSessions() {
  return useQuery({
    queryKey: autoNotesKeys.sessions(),
    queryFn: async () => {
      const response = await autoNotesAPI.getSessions();
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes freshness for sessions list
    retry: 2,
  });
}

/**
 * Hook to fetch a specific auto-notes session
 */
export function useAutoNotesSession(sessionId) {
  return useQuery({
    queryKey: autoNotesKeys.session(sessionId),
    queryFn: async () => {
      const response = await autoNotesAPI.getSession(sessionId);
      return response.data;
    },
    enabled: !!sessionId, // Only run if session ID provided
    staleTime: 5 * 60 * 1000, // 5 minutes freshness for individual session
  });
}

/**
 * Hook to fetch auto-notes analytics
 */
export function useAutoNotesAnalytics() {
  return useQuery({
    queryKey: autoNotesKeys.analytics(),
    queryFn: async () => {
      const response = await autoNotesAPI.getAnalytics();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes freshness for analytics
  });
}

/**
 * Hook to fetch class series
 */
export function useAutoNotesClassSeries() {
  return useQuery({
    queryKey: autoNotesKeys.classSeries(),
    queryFn: async () => {
      const response = await autoNotesAPI.getClassSeries();
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes freshness for class series
  });
}

/**
 * Hook to start a new auto-notes session
 */
export function useStartAutoNotesSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (sessionData) => {
      const response = await autoNotesAPI.startSession(sessionData);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate sessions list to refresh after creating new session
      queryClient.invalidateQueries({ queryKey: autoNotesKeys.sessions() });
      queryClient.invalidateQueries({ queryKey: autoNotesKeys.analytics() });
    },
  });
}