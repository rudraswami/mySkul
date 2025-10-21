import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import client from '../api/client';

/**
 * React Query hooks for AI Tutor functionality
 * Handles schema defaults, sanitization, and analytics events
 * AI Tutor 2.4 - ISS-3 Implementation
 * FIXED: Corrected API endpoints (404 errors resolved)
 */

// Client-side sanitization to match backend
const sanitizeText = (text) => {
  if (!text) return '';
  
  return text
    .replace(/\*\*(.+?)\*\*/g, '$1')  // Remove bold markers
    .replace(/\*(.+?)\*/g, '$1')      // Remove italic markers
    .replace(/✅/g, '')                // Remove checkmarks
    .replace(/❌/g, '')
    .replace(/\\"/g, '"')
    .replace(/\\'/g, "'")
    .replace(/\\\\/g, '')
    .replace(/\u00a0/g, ' ')
    .trim();
};

// Sanitize response data recursively
const sanitizeResponse = (data) => {
  if (!data) return data;
  
  // Sanitize dual response structure
  if (data.dual_response) {
    const { primary, secondary } = data.dual_response;
    
    // Sanitize primary (Professor) response
    if (primary?.micro_lesson_sections) {
      const sections = primary.micro_lesson_sections;
      primary.micro_lesson_sections = {
        concept_overview: sanitizeText(sections.concept_overview),
        key_formula: Array.isArray(sections.key_formula) 
          ? sections.key_formula.map(f => sanitizeText(f))
          : sanitizeText(sections.key_formula),
        step_by_step: sanitizeText(sections.step_by_step),
        real_life_analogy: sanitizeText(sections.real_life_analogy),
        mentor_tip: sanitizeText(sections.mentor_tip),
        visual_prompt: sanitizeText(sections.visual_prompt)
      };
    }
    
    // Sanitize secondary (Mentor) response
    if (secondary?.mentor_sections) {
      const sections = secondary.mentor_sections;
      secondary.mentor_sections = {
        motivation_spark: sanitizeText(sections.motivation_spark),
        simplified_recap: sanitizeText(sections.simplified_recap),
        confidence_tips: sanitizeText(sections.confidence_tips),
        encouragement: sanitizeText(sections.encouragement)
      };
    }
  }
  
  return data;
};

// Track analytics event
const trackEvent = (eventName, eventData) => {
  if (window.gtag) {
    window.gtag('event', eventName, eventData);
  }
  console.log(`[Analytics] ${eventName}:`, eventData);
};

/**
 * Hook to fetch user's AI Tutor sessions
 * FIXED: /api/ai/sessions → /api/ai/chat/sessions
 */
export const useAITutorSessions = () => {
  return useQuery({
    queryKey: ['ai-tutor-sessions'],
    queryFn: async () => {
      const response = await client.get('/api/ai/chat/sessions');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 30 * 60 * 1000 // 30 minutes
  });
};

/**
 * Hook to fetch messages for a specific session
 * FIXED: /api/ai/sessions/{id}/messages → /api/ai/chat/{id}/messages
 */
export const useSessionMessages = (sessionId) => {
  return useQuery({
    queryKey: ['ai-tutor-messages', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const response = await client.get(`/api/ai/chat/${sessionId}/messages`);
      return response.data;
    },
    enabled: !!sessionId,
    staleTime: 2 * 60 * 1000 // 2 minutes
  });
};

/**
 * Hook to create a new AI Tutor session
 * FIXED: /api/ai/create-session → /api/ai/chat/sessions (POST)
 */
export const useCreateSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ title, subject, topic }) => {
      const response = await client.post('/api/ai/chat/sessions', {
        title,
        subject,
        topic: topic || 'General'
      });
      
      trackEvent('ai_tutor_session_created', {
        subject,
        topic: topic || 'General'
      });
      
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-tutor-sessions'] });
    }
  });
};

/**
 * Hook to send a message and get dual AI response
 * Includes sanitization and analytics tracking
 * Supports depth_level and exam_mode parameters
 */
export const useSendMessage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ message, sessionId, subject, depthLevel, examMode, mode = 'dual' }) => {
      const startTime = Date.now();
      
      // Determine endpoint based on mode
      let endpoint = '/api/ai/dual-response';
      if (mode === 'mentor') {
        endpoint = '/api/ai/mentor-only';
      } else if (mode === 'professor') {
        endpoint = '/api/ai/professor-only';
      }
      
      const response = await client.post(endpoint, {
        message,
        session_id: sessionId,
        subject,
        depth_level: depthLevel || 'standard',
        exam_mode: examMode || 'JEE'
      });
      
      const responseTime = Date.now() - startTime;
      
      // Sanitize response data
      const sanitizedData = sanitizeResponse(response.data);
      
      // Track analytics
      trackEvent('ai_tutor_message_sent', {
        session_id: sessionId,
        subject,
        mode,
        depth_level: depthLevel,
        exam_mode: examMode,
        response_time_ms: responseTime,
        has_formula: sanitizedData.dual_response?.primary?.micro_lesson_sections?.key_formula?.length > 0,
        has_visual: sanitizedData.visual?.generated || false
      });
      
      return sanitizedData;
    },
    onSuccess: (data, variables) => {
      // Invalidate session messages to refetch
      queryClient.invalidateQueries({ 
        queryKey: ['ai-tutor-messages', variables.sessionId] 
      });
      
      // Track lesson rendered event
      trackEvent('lesson_rendered', {
        session_id: variables.sessionId,
        sentiment: data.sentiment_analysis?.primary_sentiment
      });
    },
    onError: (error, variables) => {
      trackEvent('ai_tutor_error', {
        session_id: variables.sessionId,
        error_message: error.message
      });
    }
  });
};

/**
 * Hook to handle quick actions (save notes, practice, etc.)
 */
export const useQuickAction = () => {
  return useMutation({
    mutationFn: async ({ action, messageData }) => {
      let endpoint = '';
      let payload = {};
      
      switch (action) {
        case 'save_to_notes':
          endpoint = '/api/actions/add-to-notes';
          payload = {
            content: messageData.dual_response?.primary?.response,
            subject: messageData.subject,
            tags: ['ai-tutor', messageData.subject]
          };
          break;
          
        case 'generate_practice':
          endpoint = '/api/actions/practice-more';
          payload = {
            topic: messageData.subject,
            difficulty: 'medium'
          };
          break;
          
        case 'explain_different':
          // This would trigger a new message with different style
          return { action: 'explain_different', messageData };
          
        case 'generate_visual':
          endpoint = '/api/actions/generate-visual';
          payload = {
            concept: messageData.dual_response?.primary?.micro_lesson_sections?.concept_overview
          };
          break;
          
        default:
          throw new Error(`Unknown action: ${action}`);
      }
      
      if (endpoint) {
        const response = await client.post(endpoint, payload);
        
        // Track analytics
        trackEvent('quick_action_clicked', {
          action,
          subject: messageData.subject
        });
        
        return response.data;
      }
      
      return { action, messageData };
    }
  });
};

/**
 * Hook to track mentor panel interactions
 */
export const useMentorInteraction = () => {
  return {
    trackExpanded: (sessionId, messageId) => {
      trackEvent('mentor_expanded', {
        session_id: sessionId,
        message_id: messageId
      });
    },
    trackCollapsed: (sessionId, messageId) => {
      trackEvent('mentor_collapsed', {
        session_id: sessionId,
        message_id: messageId
      });
    },
    trackSectionViewed: (sectionName, sessionId) => {
      trackEvent('mentor_section_viewed', {
        section: sectionName,
        session_id: sessionId
      });
    }
  };
};

/**
 * Hook to track formula interactions
 */
export const useFormulaInteraction = () => {
  return {
    trackCopied: (formula, sessionId) => {
      trackEvent('formula_copied', {
        formula: formula.substring(0, 50), // Truncate for analytics
        session_id: sessionId
      });
    },
    trackViewed: (formulaCount, sessionId) => {
      trackEvent('formula_viewed', {
        count: formulaCount,
        session_id: sessionId
      });
    }
  };
};

/**
 * Hook to rename a session
 * FIXED: /api/chat/{sessionId}/rename → /api/ai/chat/{sessionId}/rename
 */
export const useRenameSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ sessionId, title }) => {
      const response = await client.put(`/api/ai/chat/${sessionId}/rename`, { title });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-tutor-sessions'] });
    }
  });
};

/**
 * Hook to delete a session
 * FIXED: /api/chat/{sessionId} → /api/ai/chat/{sessionId}
 */
export const useDeleteSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (sessionId) => {
      const response = await client.delete(`/api/ai/chat/${sessionId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-tutor-sessions'] });
    }
  });
};

/**
 * Hook to pin/unpin a session
 * FIXED: /api/chat/{sessionId}/pin → /api/ai/chat/{sessionId}/pin
 */
export const usePinSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ sessionId, isPinned }) => {
      const response = await client.put(`/api/ai/chat/${sessionId}/pin`, { is_pinned: isPinned });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-tutor-sessions'] });
    }
  });
};

/**
 * Hook to bookmark a message
 * FIXED: /api/chat/{sessionId}/bookmark → /api/ai/chat/{sessionId}/bookmark
 */
export const useBookmarkMessage = () => {
  return useMutation({
    mutationFn: async ({ sessionId, messageId, isBookmarked }) => {
      const response = await client.put(`/api/ai/chat/${sessionId}/bookmark`, { 
        message_id: messageId,
        is_bookmarked: isBookmarked 
      });
      return response.data;
    }
  });
};

/**
 * Hook to save message to notes
 */
export const useSaveToNotes = () => {
  return useMutation({
    mutationFn: async ({ content, subject, tags }) => {
      const response = await client.post('/api/actions/add-to-notes', {
        content,
        subject,
        tags: tags || ['ai-tutor', subject]
      });
      
      trackEvent('note_saved', { subject, from: 'ai_tutor' });
      return response.data;
    }
  });
};

/**
 * Hook to generate practice problems
 */
export const useGeneratePractice = () => {
  return useMutation({
    mutationFn: async ({ topic, difficulty, concept }) => {
      const response = await client.post('/api/actions/practice-more', {
        topic,
        difficulty: difficulty || 'medium',
        concept
      });
      
      trackEvent('practice_generated', { topic, difficulty });
      return response.data;
    }
  });
};

/**
 * Hook to create flashcards
 */
export const useCreateFlashcards = () => {
  return useMutation({
    mutationFn: async ({ content, subject }) => {
      const response = await client.post('/api/actions/create-flashcards', {
        content,
        subject,
        description: `Flashcards for ${subject}`
      });
      
      trackEvent('flashcards_created', { subject });
      return response.data;
    }
  });
};

/**
 * Hook to schedule revision
 */
export const useScheduleRevision = () => {
  return useMutation({
    mutationFn: async ({ topic, date, content }) => {
      const response = await client.post('/api/actions/schedule-revision', {
        topic,
        scheduled_date: date,
        content
      });
      
      trackEvent('revision_scheduled', { topic, date });
      return response.data;
    }
  });
};

/**
 * Hook to perform wellness check
 */
export const useWellnessCheck = () => {
  return useMutation({
    mutationFn: async ({ stressLevel, studyDuration }) => {
      const response = await client.post('/api/analytics/wellness-check', {
        stress_level: stressLevel,
        study_duration_minutes: studyDuration
      });
      
      return response.data;
    }
  });
};

export default {
  useAITutorSessions,
  useSessionMessages,
  useCreateSession,
  useSendMessage,
  useQuickAction,
  useMentorInteraction,
  useFormulaInteraction,
  useRenameSession,
  useDeleteSession,
  usePinSession,
  useBookmarkMessage,
  useSaveToNotes,
  useGeneratePractice,
  useCreateFlashcards,
  useScheduleRevision,
  useWellnessCheck
};
