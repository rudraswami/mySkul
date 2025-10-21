# Phase 2: Core Fix & Refactor - Detailed Plan

**Status**: 🔄 IN PROGRESS
**Started**: 2025
**Estimated Duration**: 4-5 hours

---

## Wave 1: Security & Critical Bugs (PRIORITY)

### 1.1 Enable CSRF Protection ⏳
**File**: `/app/backend/main.py`
**Action**: Uncomment CSRF middleware, configure exempt paths
**Impact**: Protects against CSRF attacks
**ETA**: 10 mins

### 1.2 Fix JWT Secret Validation ⏳
**File**: `/app/backend/core/config.py`
**Action**: Raise exception if JWT_SECRET missing
**Impact**: Prevents insecure deployments
**ETA**: 5 mins

### 1.3 Service Worker Error Handling ⏳
**File**: `/app/frontend/public/sw.js`
**Action**: Verify catch handlers on all fetch() calls
**Impact**: Fixes 520 errors
**ETA**: 15 mins

### 1.4 Remove Hardcoded Fallbacks ⏳
**Files**: Multiple backend and frontend files
**Action**: Remove localhost fallbacks, fail fast
**Impact**: Prevents configuration errors
**ETA**: 20 mins

### 1.5 Fix Dashboard API Errors ⏳
**Files**: `/app/backend/api/dashboard_analytics.py`, `/app/backend/api/gamification.py`
**Action**: Verify dependency injection, add defensive coding
**Impact**: Dashboard works reliably
**ETA**: 20 mins

---

## Wave 2: Architecture & Cleanup

### 2.1 Complete Subscription Service Migration ⏳
**Files**: All files using `SubscriptionService`
**Action**: Replace with `UnifiedSubscriptionService`, remove legacy
**Impact**: Consistent subscription logic
**ETA**: 30 mins

### 2.2 Remove Legacy Files ⏳
**Files**: *.legacy, *.backup, *.broken, *.old
**Action**: Delete all legacy files
**Impact**: Cleaner codebase
**ETA**: 10 mins

### 2.3 Clean Up Test Files ⏳
**Files**: 772 test files in repository
**Action**: Move to /tests/, archive obsolete
**Impact**: Organized testing
**ETA**: 30 mins

### 2.4 Remove API_CACHE_NAME ⏳
**File**: `/app/frontend/public/sw.js`
**Action**: Remove unused API cache
**Impact**: Cleaner service worker
**ETA**: 10 mins

### 2.5 Complete React Query Migration ⏳
**File**: `/app/frontend/src/contexts/AuthContext.js`
**Action**: Migrate to React Query hooks
**Impact**: Consistent data fetching
**ETA**: 40 mins

### 2.6 Remove Hardcoded Mock Data ⏳
**Files**: Analytics, gamification endpoints
**Action**: Remove or implement real calculations
**Impact**: Accurate data display
**ETA**: 30 mins

---

## Wave 3: UI/UX Polish

### 3.1 Add Error Boundaries ⏳
**Files**: Frontend components
**Action**: Implement React Error Boundary
**Impact**: Graceful error handling
**ETA**: 20 mins

### 3.2 Fix Mobile Responsiveness ⏳
**Files**: Dashboard, MockTests, AITutor
**Action**: Test and fix mobile layouts
**Impact**: Better mobile UX
**ETA**: 45 mins

### 3.3 Add Null Checks & Defensive Coding ⏳
**Files**: All frontend components
**Action**: Add null/undefined checks
**Impact**: Prevents crashes
**ETA**: 30 mins

### 3.4 Fix AI Tutor Issues ⏳
**Files**: AITutor.js, message components
**Action**: Fix duplicates, formatting
**Impact**: Better chat experience
**ETA**: 40 mins

### 3.5 Add ARIA Labels ⏳
**Files**: All interactive components
**Action**: Add aria-label, aria-describedby
**Impact**: Accessibility compliance
**ETA**: 40 mins

---

## Wave 4: Performance & Optimization

### 4.1 Fix N+1 Queries ⏳
**Files**: Dashboard, analytics services
**Action**: Use MongoDB aggregation
**Impact**: Faster queries
**ETA**: 45 mins

### 4.2 Add Pagination ⏳
**Files**: List endpoints
**Action**: Implement limit/skip pagination
**Impact**: Better performance
**ETA**: 30 mins

### 4.3 Remove Console Logs ⏳
**Files**: All frontend files
**Action**: Remove development logs
**Impact**: Cleaner console
**ETA**: 15 mins

---

## Testing Strategy

After each wave:
1. ✅ Backend testing with `deep_testing_backend_v2`
2. ✅ Frontend testing with `auto_frontend_testing_agent`
3. ✅ Manual verification of critical flows

---

## Success Criteria

- [ ] All P0 issues resolved
- [ ] All P1 issues resolved or tracked
- [ ] No legacy files in codebase
- [ ] Test files organized (<100 in root)
- [ ] All critical user flows working
- [ ] Mobile responsive
- [ ] Accessibility improvements
- [ ] Performance baseline established

---

**Status**: Wave 1 starting now...
