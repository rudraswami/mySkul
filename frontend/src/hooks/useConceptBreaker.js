/**
 * React Query hook for ConceptBreaker
 * Handles concept breaking with caching and error handling
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { aiAPI } from '../api/client';

// Query keys
export const conceptBreakerKeys = {
  all: ['concept-breaker'],
  break: (question, context) => [...conceptBreakerKeys.all, 'break', question, context],
};

/**
 * Hook to break a concept into visual blueprint
 * @param {string} question - Natural language question
 * @param {Object} context - Context (subject, level, etc.)
 * @param {Object} options - Query options
 */
export function useBreakConcept(question, context = {}, options = {}) {
  return useQuery({
    queryKey: conceptBreakerKeys.break(question, context),
    queryFn: async () => {
      const response = await aiAPI.breakConcept(question, context);
      return response.data.blueprint;
    },
    enabled: !!question, // Only run if question provided
    staleTime: 5 * 60 * 1000, // Concepts don't change - 5 min freshness
    cacheTime: 30 * 60 * 1000, // Keep in cache for 30 min
    retry: 2,
    ...options,
  });
}

/**
 * Mutation hook for breaking concepts (for imperative calls)
 */
export function useBreakConceptMutation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ question, context }) => {
      const response = await aiAPI.breakConcept(question, context);
      return response.data.blueprint;
    },
    onSuccess: (data, variables) => {
      // Cache the result
      queryClient.setQueryData(
        conceptBreakerKeys.break(variables.question, variables.context),
        data
      );
    },
    retry: 1,
  });
}

/**
 * Prefetch concept breaking (for predictive loading)
 */
export function usePrefetchConcept() {
  const queryClient = useQueryClient();
  
  return async (question, context = {}) => {
    await queryClient.prefetchQuery({
      queryKey: conceptBreakerKeys.break(question, context),
      queryFn: async () => {
        const response = await aiAPI.breakConcept(question, context);
        return response.data.blueprint;
      },
      staleTime: 5 * 60 * 1000,
    });
  };
}

export default useBreakConcept;

