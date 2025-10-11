/**
 * React Query hooks for AI Tutor module
 * Manages chat sessions, messages, and AI interactions with caching
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { aiAPI } from '../api/client';

// Query keys for cache management
export const aiKeys = {
  all: ['ai'],
  contexts: () => [...aiKeys.all, 'contexts'],
  sessions: () => [...aiKeys.all, 'sessions'],
  session: (sessionId) => [...aiKeys.all, 'session', sessionId],
  messages: (sessionId) => [...aiKeys.all, 'messages', sessionId],
};

/**
 * Hook to fetch available AI contexts
 */
export function useAvailableContexts() {
  return useQuery({
    queryKey: aiKeys.contexts(),
    queryFn: async () => {
      const response = await aiAPI.getAvailableContexts();
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // Contexts rarely change - 10 min freshness
  });
}

/**
 * Hook to fetch user's chat sessions
 */
export function useChatSessions() {
  return useQuery({
    queryKey: aiKeys.sessions(),
    queryFn: async () => {
      const response = await aiAPI.getChatSessions();
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute freshness
  });
}

/**
 * Hook to create a new chat session
 */
export function useCreateSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (sessionData) => {
      const response = await aiAPI.createSession(sessionData);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate sessions list to include new session
      queryClient.invalidateQueries({ queryKey: aiKeys.sessions() });
    },
  });
}

/**
 * Hook to send a message in a chat session
 */
export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (messageData) => {
      const response = await aiAPI.sendMessage(messageData);
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Invalidate messages for this session
      if (variables.session_id) {
        queryClient.invalidateQueries({ 
          queryKey: aiKeys.messages(variables.session_id) 
        });
      }
      // Update sessions list (last_updated might have changed)
      queryClient.invalidateQueries({ queryKey: aiKeys.sessions() });
    },
    retry: (failureCount, error) => {
      // Don't retry on 402 Payment Required (subscription limit)
      if (error.response?.status === 402) {
        return false;
      }
      return failureCount < 2;
    },
  });
}

/**
 * Hook to validate mathematical expressions
 */
export function useValidateMath() {
  return useMutation({
    mutationFn: async (expression) => {
      const response = await aiAPI.validateMath(expression);
      return response.data;
    },
  });
}

/**
 * Hook to verify facts
 */
export function useVerifyFact() {
  return useMutation({
    mutationFn: async ({ statement, subject }) => {
      const response = await aiAPI.verifyFact(statement, subject);
      return response.data;
    },
  });
}

/**
 * Hook to get citations for a topic
 */
export function useCitations(subject, topic) {
  return useQuery({
    queryKey: [...aiKeys.all, 'citations', subject, topic],
    queryFn: async () => {
      const response = await aiAPI.verifyCitation(subject, topic);
      return response.data;
    },
    enabled: !!(subject && topic), // Only run if both params provided
    staleTime: 5 * 60 * 1000, // Citations don't change often - 5 min
  });
}
