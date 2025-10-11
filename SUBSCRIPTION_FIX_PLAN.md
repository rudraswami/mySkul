# Subscription System Consolidation & Fix Plan

## Issues Identified

### 1. Backend Duplication
- **server.py** has 14 duplicate subscription endpoints (lines 6589-11011)
- **api/subscription.py** has the modular subscription router
- **services/subscription_service.py** has business logic
- Both systems coexist causing conflicts and inconsistent behavior

### 2. Feature Name Mismatches
**planConfig_ai_tutor.json defines:**
- `ai_sessions_monthly`: 10 (FREE)
- `mentor_tips_daily`: 0 (FREE)
- `mock_tests_weekly`: 1 (FREE)
- `auto_note_uploads_daily`: 1 (FREE)

**Code uses various names:**
- `ai_tutor_daily` vs `ai_sessions_monthly`
- `ai_conversations_daily` vs `ai_sessions_monthly`
- `mock_tests_weekly` (correct in some places)
- Inconsistent tracking periods (daily vs monthly vs weekly)

### 3. Status Code Issues
- `check-access` endpoint returns 200 OK when access is denied
- Should return 402 Payment Required to trigger frontend modals
- Frontend relies on 402/429 status codes for modal display

### 4. Frontend Duplication
- **SubscriptionContext.js** has full implementation
- **useSubscription.js** has React Query hooks
- Some components bypass context with direct axios calls
- Feature limit fallbacks use wrong values

## Implementation Plan

### Phase 1: Backend Fixes

#### 1.1 Update subscription_service.py
- [x] Load planConfig_ai_tutor.json (already done)
- [ ] Standardize all feature names
- [ ] Fix monthly vs daily vs weekly tracking logic
- [ ] Ensure check_feature_access returns correct structure

#### 1.2 Update api/subscription.py
- [ ] Verify 402 status code returns for denied access
- [ ] Ensure all endpoints use subscription_service.py
- [ ] Add proper error handling

#### 1.3 Clean server.py
- [ ] Comment out duplicate subscription endpoints
- [ ] Add deprecation notices
- [ ] Keep only modular router includes

### Phase 2: Frontend Fixes

#### 2.1 Update SubscriptionContext.js
- [ ] Use correct feature names from planConfig_ai_tutor.json
- [ ] Fix fallback values in error handling
- [ ] Ensure 402/429 status handling works correctly
- [ ] Remove any hardcoded limits

#### 2.2 Update Components
- [ ] AITutor.js - use `ai_sessions_monthly`
- [ ] MockTests.js - use `mock_tests_weekly`  
- [ ] AutoNoteMentor.js - use `auto_note_uploads_daily`
- [ ] Ensure all use SubscriptionContext instead of direct API calls

#### 2.3 Update Header/Modal Display
- [ ] Verify usage stats show correct values
- [ ] Ensure tier info displays correctly
- [ ] Test modal triggering on limit reached

### Phase 3: Testing

#### 3.1 Free Plan Testing
- [ ] AI Sessions: 10/month limit enforcement
- [ ] Mock Tests: 1/week limit enforcement
- [ ] Auto-Notes: 1/day limit enforcement
- [ ] Modal triggers when limits reached

#### 3.2 Upgrade Flow Testing
- [ ] Free → Starter (20 sessions, 2 tests, 3 uploads)
- [ ] Starter → Scholar (100 sessions, 5 tests, unlimited uploads)
- [ ] Scholar → Achiever (300 sessions, unlimited tests)
- [ ] Achiever → Legend (unlimited everything)

#### 3.3 Usage Display Testing
- [ ] Header shows correct current usage
- [ ] Modal shows correct plan comparison
- [ ] Pricing reflects planConfig_ai_tutor.json

## Feature Name Mapping

### Standardized Names (from planConfig_ai_tutor.json)
```
ai_sessions_monthly    -> AI Tutor conversations (monthly limit)
mentor_tips_daily      -> Mentor motivational tips (daily limit)
mock_tests_weekly      -> Mock test generation (weekly limit)
auto_note_uploads_daily -> Note upload/recording (daily limit)
```

### Usage Tracking Period
- **ai_sessions_monthly**: Track by month, reset on 1st of month
- **mentor_tips_daily**: Track by day, reset at midnight
- **mock_tests_weekly**: Track by week (Monday-Sunday), reset Monday
- **auto_note_uploads_daily**: Track by day, reset at midnight

## Files to Modify

### Backend
1. `/app/backend/services/subscription_service.py` - Core logic fixes
2. `/app/backend/api/subscription.py` - 402 status code fix
3. `/app/backend/server.py` - Remove duplicate endpoints

### Frontend
1. `/app/frontend/src/contexts/SubscriptionContext.js` - Feature name fixes
2. `/app/frontend/src/components/AITutor.js` - Use correct feature name
3. `/app/frontend/src/components/MockTests.js` - Verify feature name
4. `/app/frontend/src/components/AutoNoteMentor.js` - Use correct feature name

## Expected Outcomes

1. **Single Source of Truth**: Only modular API handles subscription
2. **Consistent Feature Names**: All code uses planConfig_ai_tutor.json names
3. **Proper Error Codes**: 402 triggers modals correctly
4. **Accurate Limits**: Free plan enforces correct limits (10/1/1)
5. **Working Modals**: Upgrade prompts display with correct tier info
6. **Clean Code**: No duplicate logic, easy to maintain

## Validation Checklist

- [ ] Backend uses only modular subscription API
- [ ] All feature names match planConfig_ai_tutor.json
- [ ] 402 status codes trigger frontend modals
- [ ] Free plan limits work correctly
- [ ] Usage stats display accurately
- [ ] Upgrade modal shows correct pricing
- [ ] All tier transitions tested
- [ ] No duplicate subscription code remains
