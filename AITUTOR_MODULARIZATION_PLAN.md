# AI Tutor Modularization Plan

**Date**: January 17, 2025  
**Goal**: Transform 3399-line legacy AITutor.js into modular, maintainable, robust code

---

## Current Analysis

### Legacy File Structure (AITutor.js):
- **Size**: 3,399 lines (141KB)
- **State Variables**: 25+ useState hooks
- **Functions**: 40+ functions
- **Responsibilities**: Too many (violates Single Responsibility Principle)

### Key Responsibilities Identified:
1. **Session Management** - Create, load, switch sessions
2. **Message Management** - Send, receive, display messages
3. **AI Generation** - Call AI APIs, handle streaming
4. **Voice Input** - Speech recognition
5. **Personalization** - XP, streaks, mastery tracking
6. **Subscription** - Check limits, show upgrade modal
7. **UI Rendering** - Display chat, input, sidebar
8. **Error Handling** - API errors, network failures

---

## Proposed Modular Architecture

### Directory Structure:
```
/app/frontend/src/components/AITutor/
├── index.js                    # Main container/orchestrator
├── AITutorChat.js             # Chat window component
├── ChatInput.js               # Input field + controls
├── ChatMessage.js             # Individual message display
├── SessionSidebar.js          # Session list sidebar
├── PersonalizationPanel.js    # XP, streaks, mastery
├── SubjectSelector.js         # Subject/mode selector
└── UpgradePrompt.js           # Inline upgrade prompt

/app/frontend/src/hooks/
├── useAITutorSession.js       # Session CRUD operations
├── useAITutorMessages.js      # Message management
├── useAIGeneration.js         # AI API calls
├── useVoiceInput.js           # Speech recognition
├── usePersonalization.js      # XP, streaks, mastery
└── useSubscriptionCheck.js    # Subscription limits

/app/frontend/src/utils/
├── aiTutorHelpers.js          # Pure helper functions
└── messageFormatters.js       # Format AI responses
```

---

## Implementation Strategy

### Phase 1: Extract Custom Hooks (Day 1)
**Priority**: High - Foundation for everything

1. **useAITutorSession.js**
   - State: currentSession, sessions, loading
   - Functions: fetchSessions, createSession, switchSession, deleteSession
   - API: `/api/chat/sessions`

2. **useAITutorMessages.js**
   - State: messages, loading, error
   - Functions: loadMessages, sendMessage, clearMessages
   - API: `/api/chat/sessions/:id/messages`

3. **useAIGeneration.js**
   - State: generating, error, streaming
   - Functions: generateAIResponse, generateDualResponse
   - API: `/api/ai/dual-response`

4. **useVoiceInput.js**
   - State: isListening, recognition, transcript
   - Functions: startListening, stopListening, initRecognition
   - Browser: Web Speech API

5. **usePersonalization.js**
   - State: xp, streaks, mastery, level
   - Functions: loadPersonalization, updateXP, trackMastery
   - API: `/api/personalization/profile`

6. **useSubscriptionCheck.js**
   - State: canUseFeature, usage, upgradeHint
   - Functions: checkFeature, trackUsage, showUpgradeModal
   - API: `/api/subscription/features/:feature`

**Testing**: Each hook tested independently with mock data

---

### Phase 2: Create UI Components (Day 2)
**Priority**: High - User-facing elements

1. **ChatMessage.js** (50-100 lines)
   ```jsx
   - Props: message, role, timestamp, loading
   - Renders: User/AI message with formatting
   - Features: Semantic rendering, LaTeX, code blocks
   - Error boundary: Yes
   ```

2. **ChatInput.js** (150-200 lines)
   ```jsx
   - Props: onSend, disabled, voice, maxLength
   - State: input, charCount
   - Features: Voice toggle, submit, keyboard shortcuts
   - Validation: Max length, empty check
   ```

3. **AITutorChat.js** (200-250 lines)
   ```jsx
   - Props: messages, loading, onLoadMore
   - Features: Virtual scrolling, auto-scroll, timestamps
   - Components: Uses ChatMessage
   - Performance: React.memo, useMemo
   ```

4. **SessionSidebar.js** (150-200 lines)
   ```jsx
   - Props: sessions, currentSession, onSwitch, onCreate
   - Features: Search, filter, create new, delete
   - UI: Collapsible, responsive
   ```

5. **SubjectSelector.js** (100-150 lines)
   ```jsx
   - Props: subjects, selectedSubject, mode, onChange
   - Features: Dropdown, mode switch, exam type
   - UI: Clean, accessible
   ```

6. **PersonalizationPanel.js** (150-200 lines)
   ```jsx
   - Props: xp, streaks, mastery
   - Features: Progress bars, achievements, badges
   - UI: Animated, gamified
   ```

**Testing**: Visual regression testing, screenshot comparison

---

### Phase 3: Main Container (Day 3)
**Priority**: Critical - Orchestrates everything

**index.js** (300-400 lines)
```jsx
- Responsibilities:
  * Import and use all hooks
  * Manage global state coordination
  * Handle subscription checks
  * Coordinate UI components
  * Error boundaries
  * Loading states
  
- Structure:
  1. Hook initialization
  2. Effect for loading data
  3. Event handlers
  4. Render layout
  
- Error Handling:
  * Try-catch in all async operations
  * Error boundaries for components
  * Graceful degradation
  * User-friendly error messages
```

---

### Phase 4: Error Handling & Edge Cases (Day 4)
**Priority**: Critical - Production readiness

1. **Error Boundaries**
   - Wrap each major component
   - Fallback UI
   - Error reporting

2. **Loading States**
   - Skeleton screens
   - Progressive loading
   - Optimistic UI updates

3. **Edge Cases**
   - No internet connection
   - API timeouts
   - Malformed responses
   - Empty states
   - Maximum message limit
   - Session expiry

4. **Accessibility**
   - Keyboard navigation
   - Screen reader support
   - ARIA labels
   - Focus management

---

### Phase 5: Testing & Validation (Day 5)
**Priority**: Critical - Ensure nothing breaks

1. **Unit Tests**
   - Each hook tested with mock APIs
   - Pure functions tested
   - Component render tests

2. **Integration Tests**
   - Full chat flow
   - Session switching
   - Voice input
   - Subscription checks

3. **Visual Tests**
   - Screenshot comparison legacy vs new
   - Responsive design
   - Dark mode

4. **Performance Tests**
   - Bundle size comparison
   - Render performance
   - Memory leaks
   - Virtual scrolling efficiency

---

### Phase 6: Gradual Rollout (Day 6)
**Priority**: High - Safe deployment

1. **Feature Flag Implementation**
   ```javascript
   const USE_MODULAR_AI_TUTOR = localStorage.getItem('use_modular_ai_tutor') === 'true';
   ```

2. **A/B Testing**
   - 10% users → Modular version
   - Monitor error rates
   - Collect feedback

3. **Monitoring**
   - Error tracking (console.error)
   - Performance metrics
   - User feedback

4. **Rollback Plan**
   - Keep legacy version intact
   - Quick switch mechanism
   - Clear rollback procedure

---

## Success Criteria

### Functional:
- ✅ All features from legacy version work
- ✅ No new bugs introduced
- ✅ Subscription limits respected
- ✅ Messages save correctly
- ✅ Voice input works
- ✅ Streaming responses work

### Code Quality:
- ✅ No component over 300 lines
- ✅ No hook over 150 lines
- ✅ All functions < 50 lines
- ✅ Proper error handling everywhere
- ✅ TypeScript-ready (JSDoc comments)
- ✅ 100% prop-types coverage

### Performance:
- ✅ Bundle size < 100KB (vs 141KB legacy)
- ✅ Initial render < 1s
- ✅ Smooth scrolling
- ✅ No memory leaks

### Maintainability:
- ✅ Clear separation of concerns
- ✅ Easy to add new features
- ✅ Self-documenting code
- ✅ Comprehensive comments

---

## Risk Mitigation

### High Risks:
1. **Breaking existing functionality**
   - Mitigation: Keep legacy, feature flag, thorough testing

2. **Performance regression**
   - Mitigation: Performance budgets, profiling, optimization

3. **User disruption**
   - Mitigation: Gradual rollout, monitoring, quick rollback

### Medium Risks:
1. **Increased complexity**
   - Mitigation: Clear documentation, simple interfaces

2. **Bundle size increase**
   - Mitigation: Code splitting, lazy loading, tree shaking

---

## Timeline

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| 1 | Extract hooks | 4-6h | Pending |
| 2 | Create UI components | 4-6h | Pending |
| 3 | Main container | 3-4h | Pending |
| 4 | Error handling | 3-4h | Pending |
| 5 | Testing | 4-6h | Pending |
| 6 | Rollout | 2-3h | Pending |
| **Total** | **20-29 hours** | | |

---

## Next Steps

1. ✅ Get user approval for plan
2. ⏳ Start with Phase 1: Extract hooks
3. ⏳ Test each hook independently
4. ⏳ Proceed to Phase 2: UI components
5. ⏳ Continue through all phases

---

**Approved by**: Pending  
**Start Date**: TBD  
**Estimated Completion**: TBD
