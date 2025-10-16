# AITutor Refactoring Implementation Guide

## Overview
This document provides a detailed plan for refactoring the AITutor.js component (3,399 lines) into smaller, maintainable, and performant components.

## Current Issues
1. **Size**: 3,399 lines in a single file
2. **Performance**: Slow initial render and re-renders
3. **Maintainability**: Difficult to test and modify
4. **Bundle Size**: All features loaded upfront

## Proposed Architecture

### Component Hierarchy
```
AITutor/ (Main Container)
├── index.js (Entry point, lazy loading)
├── AITutorContainer.js (Main logic, ~200 lines)
├── components/
│   ├── ChatWindow/
│   │   ├── index.js
│   │   ├── MessageList.js (Uses VirtualizedMessageList)
│   │   ├── MessageItem.js
│   │   └── TypingIndicator.js
│   ├── Controls/
│   │   ├── index.js
│   │   ├── SubjectSelector.js
│   │   ├── ModeSelector.js
│   │   └── SettingsPanel.js
│   ├── Input/
│   │   ├── index.js
│   │   ├── TextInput.js
│   │   ├── VoiceRecorder.js (Lazy loaded)
│   │   └── AttachmentsPanel.js (Lazy loaded)
│   └── Response/
│       ├── index.js
│       ├── AIResponseRenderer.js
│       ├── FormulaRenderer.js
│       └── ImageRenderer.js
├── hooks/
│   ├── useChatMessages.js
│   ├── useAIResponse.js
│   ├── useVoiceRecorder.js
│   └── useAttachments.js
└── utils/
    ├── messageParser.js
    └── responseFormatter.js
```

## Step-by-Step Refactoring Plan

### Phase 1: Extract Presentational Components (Week 1)

#### 1.1 Create MessageItem Component
```javascript
// components/ChatWindow/MessageItem.js
import React, { memo } from 'react';
import { createSafeHTML } from '../../../utils/sanitize';

export const MessageItem = memo(({ message, onReact, onDelete }) => {
  return (
    <div className={`message message-${message.role}`}>
      <div dangerouslySetInnerHTML={createSafeHTML(message.content)} />
      {/* Actions */}
    </div>
  );
});
```

#### 1.2 Create ChatWindow Component
```javascript
// components/ChatWindow/index.js
import React from 'react';
import { VirtualizedMessageList } from '../../VirtualizedMessageList';
import { MessageItem } from './MessageItem';

export function ChatWindow({ messages, onMessageAction }) {
  const renderMessage = (message, index) => (
    <MessageItem 
      message={message} 
      onReact={(emoji) => onMessageAction('react', message.id, emoji)}
      onDelete={() => onMessageAction('delete', message.id)}
    />
  );

  return (
    <VirtualizedMessageList
      messages={messages}
      renderMessage={renderMessage}
      defaultItemSize={120}
      scrollToBottom={true}
    />
  );
}
```

### Phase 2: Extract Business Logic to Hooks (Week 1-2)

#### 2.1 Create useChatMessages Hook
```javascript
// hooks/useChatMessages.js
import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';

export function useChatMessages(sessionId) {
  const queryClient = useQueryClient();

  // Fetch messages
  const { data: messages, isLoading } = useQuery({
    queryKey: ['chat-messages', sessionId],
    queryFn: async () => {
      const response = await apiClient.get(`/tutor/sessions/${sessionId}/messages`);
      return response.data;
    },
    enabled: !!sessionId,
  });

  // Send message
  const sendMessageMutation = useMutation({
    mutationFn: async (content) => {
      const response = await apiClient.post(`/tutor/sessions/${sessionId}/messages`, {
        content,
        role: 'user'
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['chat-messages', sessionId]);
    }
  });

  const sendMessage = useCallback((content) => {
    return sendMessageMutation.mutateAsync(content);
  }, [sendMessageMutation]);

  return {
    messages: messages || [],
    isLoading,
    sendMessage,
    isSending: sendMessageMutation.isPending,
  };
}
```

#### 2.2 Create useAIResponse Hook
```javascript
// hooks/useAIResponse.js
import { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';

export function useAIResponse() {
  const [isGenerating, setIsGenerating] = useState(false);

  const generateResponseMutation = useMutation({
    mutationFn: async ({ sessionId, message }) => {
      setIsGenerating(true);
      const response = await apiClient.post('/tutor/generate-response', {
        session_id: sessionId,
        message
      });
      return response.data;
    },
    onSettled: () => {
      setIsGenerating(false);
    }
  });

  const generateResponse = useCallback((sessionId, message) => {
    return generateResponseMutation.mutateAsync({ sessionId, message });
  }, [generateResponseMutation]);

  return {
    generateResponse,
    isGenerating,
    error: generateResponseMutation.error,
  };
}
```

### Phase 3: Implement Lazy Loading (Week 2)

#### 3.1 Lazy Load Heavy Components
```javascript
// AITutorContainer.js
import React, { lazy, Suspense } from 'react';

// Lazy load heavy features
const VoiceRecorder = lazy(() => import('./components/Input/VoiceRecorder'));
const AttachmentsPanel = lazy(() => import('./components/Input/AttachmentsPanel'));
const FormulaRenderer = lazy(() => import('./components/Response/FormulaRenderer'));

export function AITutorContainer() {
  const [showVoice, setShowVoice] = useState(false);
  const [showAttachments, setShowAttachments] = useState(false);

  return (
    <div className="ai-tutor">
      {/* Main chat interface */}
      
      {showVoice && (
        <Suspense fallback={<div>Loading voice recorder...</div>}>
          <VoiceRecorder />
        </Suspense>
      )}
      
      {showAttachments && (
        <Suspense fallback={<div>Loading attachments...</div>}>
          <AttachmentsPanel />
        </Suspense>
      )}
    </div>
  );
}
```

### Phase 4: Main Container Integration (Week 3)

#### 4.1 Refactored AITutorContainer
```javascript
// AITutorContainer.js
import React, { useState, useCallback } from 'react';
import { ChatWindow } from './components/ChatWindow';
import { Controls } from './components/Controls';
import { Input } from './components/Input';
import { useChatMessages } from './hooks/useChatMessages';
import { useAIResponse } from './hooks/useAIResponse';
import { useSubscription } from '../../contexts/SubscriptionContext';

export function AITutorContainer() {
  const [sessionId, setSessionId] = useState(null);
  const [subject, setSubject] = useState('Mathematics');
  
  const { messages, sendMessage, isSending } = useChatMessages(sessionId);
  const { generateResponse, isGenerating } = useAIResponse();
  const { checkFeatureAccess } = useSubscription();

  const handleSendMessage = useCallback(async (content) => {
    // Check feature access
    const access = await checkFeatureAccess('ai_sessions_monthly');
    if (!access.has_access) {
      // Show upgrade modal
      return;
    }

    // Send user message
    await sendMessage(content);
    
    // Generate AI response
    await generateResponse(sessionId, content);
  }, [sessionId, sendMessage, generateResponse, checkFeatureAccess]);

  return (
    <div className="ai-tutor-container">
      <Controls 
        subject={subject}
        onSubjectChange={setSubject}
      />
      
      <ChatWindow 
        messages={messages}
        onMessageAction={handleMessageAction}
      />
      
      <Input
        onSend={handleSendMessage}
        disabled={isSending || isGenerating}
      />
    </div>
  );
}
```

## Performance Optimizations

### 1. Memoization
```javascript
// Memoize expensive components
export const MessageItem = memo(MessageItem, (prev, next) => {
  return prev.message.id === next.message.id && 
         prev.message.content === next.message.content;
});
```

### 2. useCallback for Handlers
```javascript
const handleDelete = useCallback((messageId) => {
  // Delete logic
}, [dependencies]);
```

### 3. useMemo for Computed Values
```javascript
const filteredMessages = useMemo(() => {
  return messages.filter(m => m.role !== 'system');
}, [messages]);
```

### 4. Code Splitting
```javascript
// Route-level code splitting
const AITutor = lazy(() => import('./components/AITutor'));

<Route path="/tutor" element={
  <Suspense fallback={<PageLoader />}>
    <AITutor />
  </Suspense>
} />
```

## Testing Strategy

### 1. Unit Tests
```javascript
// MessageItem.test.js
describe('MessageItem', () => {
  it('renders sanitized HTML', () => {
    const message = {
      id: '1',
      content: '<script>alert("xss")</script>Hello',
      role: 'assistant'
    };
    const { container } = render(<MessageItem message={message} />);
    expect(container.innerHTML).not.toContain('<script>');
    expect(container).toHaveTextContent('Hello');
  });
});
```

### 2. Integration Tests
```javascript
// useChatMessages.test.js
describe('useChatMessages', () => {
  it('fetches and sends messages', async () => {
    const { result } = renderHook(() => useChatMessages('session-1'));
    
    await waitFor(() => expect(result.current.messages).toHaveLength(5));
    
    act(() => {
      result.current.sendMessage('Hello');
    });
    
    await waitFor(() => expect(result.current.messages).toHaveLength(6));
  });
});
```

### 3. Performance Tests
```javascript
// Performance benchmark
import { render } from '@testing-library/react';
import { measureRender } from './test-utils';

test('renders 1000 messages efficiently', () => {
  const messages = Array.from({ length: 1000 }, (_, i) => ({
    id: String(i),
    content: `Message ${i}`,
    role: 'user'
  }));

  const duration = measureRender(() => {
    render(<ChatWindow messages={messages} />);
  });

  expect(duration).toBeLessThan(100); // Should render in < 100ms
});
```

## Bundle Size Analysis

### Before Refactoring
```
AITutor.js: ~450 KB
Total bundle: ~2.5 MB
```

### After Refactoring (Expected)
```
AITutorContainer.js: ~50 KB
ChatWindow: ~80 KB
Controls: ~40 KB
Input: ~60 KB
VoiceRecorder (lazy): ~120 KB (loaded on demand)
Attachments (lazy): ~90 KB (loaded on demand)

Initial bundle: ~230 KB (49% reduction)
Total (all features): ~440 KB (2% overhead from modularization)
```

## Migration Checklist

- [ ] Create component structure
- [ ] Extract MessageItem component
- [ ] Extract ChatWindow component
- [ ] Extract Controls component
- [ ] Extract Input component
- [ ] Create useChatMessages hook
- [ ] Create useAIResponse hook
- [ ] Implement lazy loading for VoiceRecorder
- [ ] Implement lazy loading for AttachmentsPanel
- [ ] Update main AITutorContainer
- [ ] Add memoization
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Performance benchmarking
- [ ] Bundle size analysis
- [ ] Update documentation

## Rollback Plan

If issues arise during refactoring:
1. Feature flags can toggle between old and new implementation
2. Git branch strategy allows easy rollback
3. Gradual rollout to users (A/B testing)

## Success Metrics

1. **Render Performance**: 50% faster initial render
2. **Bundle Size**: 40% reduction in initial bundle
3. **Maintainability**: <500 lines per file
4. **Test Coverage**: >80%
5. **User Experience**: No regressions, same functionality

---

**Status**: Plan Ready for Implementation
**Estimated Time**: 3 weeks for full refactoring
**Priority**: Medium (can be done in Phase 2)
