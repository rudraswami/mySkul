# Unified Subscription Service - Implementation Guide

## Overview

The **UnifiedSubscriptionService** centralizes all subscription and feature-access logic into a single, student-centric service. This eliminates code duplication, ensures consistent enforcement, and provides a better experience for students.

### Philosophy: "Pay for Progress, Not Access"

- **Students** get essential learning tools for free
- **Premium features** enhance the learning experience
- **Clear messaging** helps students understand their options
- **No dark patterns** - transparent limits and upgrade paths

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│            UnifiedSubscriptionService                         │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Subscription Tiers                                   │   │
│  │  - FREE: Basic access to core features               │   │
│  │  - BASIC: 10x more usage, some premium features      │   │
│  │  - PREMIUM: Unlimited access to everything           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Feature Access Control                               │   │
│  │  - check_feature_access(user_id, feature, amount)    │   │
│  │  - Returns: FeatureAccessResult                       │   │
│  │    • allowed: bool                                    │   │
│  │    • usage: {used, limit, remaining}                  │   │
│  │    • message: student-friendly explanation            │   │
│  │    • upgrade_message: if limit reached                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Usage Tracking                                        │   │
│  │  - track_feature_use(user_id, feature, amount)       │   │
│  │  - Daily reset at midnight UTC                        │   │
│  │  - Automatic usage aggregation                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### 1. Available Features (Enum)

```python
class FeatureName(str, Enum):
    AI_MENTOR = "ai_mentor"              # AI Tutor conversations
    MOCK_TESTS = "mock_tests"            # Practice exams
    AUTO_NOTES = "auto_notes"            # AI-generated study notes
    DETAILED_ANALYSIS = "detailed_analysis"  # Performance insights
    EXAM_STRATEGIES = "exam_strategies"  # Personalized exam tips
    DOUBT_SOLVING = "doubt_solving"      # Quick doubt resolution
```

### 2. Subscription Tiers

| Tier | AI Mentor | Mock Tests | Auto Notes | Detailed Analysis | Exam Strategies |
|------|-----------|------------|------------|-------------------|-----------------|
| **FREE** | 5/day | 2/day | 3/day | ❌ | ❌ |
| **BASIC** | 50/day | 10/day | 20/day | 10/day | 10/day |
| **PREMIUM** | ♾️ Unlimited | ♾️ Unlimited | ♾️ Unlimited | ♾️ Unlimited | ♾️ Unlimited |

### 3. Limits Configuration

Limits are loaded from `core/config.py` (environment variables):

```env
# Free Tier
FREE_TIER_AI_MENTOR_LIMIT=5
FREE_TIER_MOCK_TEST_LIMIT=2
FREE_TIER_AUTO_NOTES_LIMIT=3

# Basic Tier
BASIC_TIER_AI_MENTOR_LIMIT=50
BASIC_TIER_MOCK_TEST_LIMIT=10
BASIC_TIER_AUTO_NOTES_LIMIT=20

# Premium Tier (-1 = unlimited)
PREMIUM_TIER_AI_MENTOR_LIMIT=-1
PREMIUM_TIER_MOCK_TEST_LIMIT=-1
PREMIUM_TIER_AUTO_NOTES_LIMIT=-1
```

---

## Usage Examples

### 1. Check Feature Access in Router

```python
from fastapi import APIRouter, HTTPException, Depends
from services.unified_subscription_service import (
    UnifiedSubscriptionService,
    FeatureName
)
from dependencies import get_unified_subscription_service, get_current_user

@router.post("/ai/chat")
async def ai_chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """AI chat with subscription check"""
    
    # Check if user can access feature
    access_result = await sub_service.check_feature_access(
        user.user_id,
        FeatureName.AI_MENTOR.value,
        requested_amount=1  # How many uses requested
    )
    
    if not access_result.allowed:
        # Return 402 Payment Required with student-friendly message
        raise HTTPException(
            status_code=402,
            detail=access_result.to_dict()
        )
    
    # Feature access granted - proceed with business logic
    response = await generate_ai_response(request)
    
    # Track usage AFTER successful completion
    await sub_service.track_feature_use(
        user.user_id,
        FeatureName.AI_MENTOR.value,
        amount=1
    )
    
    return response
```

### 2. FeatureAccessResult Response

When access is **allowed**:
```json
{
  "allowed": true,
  "current_tier": "free",
  "usage": {
    "used": 2,
    "limit": 5,
    "remaining": 2
  },
  "message": "✅ Access granted! 2 remaining today",
  "upgrade_message": null,
  "next_reset": "2025-10-17T00:00:00Z"
}
```

When limit is **reached**:
```json
{
  "allowed": false,
  "current_tier": "free",
  "usage": {
    "used": 5,
    "limit": 5,
    "remaining": 0
  },
  "message": "Daily limit reached (5/5 used)",
  "upgrade_message": "🤖 AI Mentor limit reached! Upgrade for unlimited conversations with your AI study buddy.",
  "next_reset": "2025-10-17T00:00:00Z"
}
```

For **Premium** users (unlimited):
```json
{
  "allowed": true,
  "current_tier": "premium",
  "usage": {
    "used": 0,
    "limit": -1,
    "remaining": -1
  },
  "message": "✨ Unlimited AI Mentor access!",
  "upgrade_message": null,
  "next_reset": null
}
```

---

## Migration Guide

### Step 1: Update Router Imports

**Before:**
```python
from services.subscription_service import SubscriptionService
```

**After:**
```python
from services.unified_subscription_service import (
    UnifiedSubscriptionService,
    FeatureName
)
from dependencies import get_unified_subscription_service
```

### Step 2: Replace Subscription Checks

**Before (Scattered checks):**
```python
# Different patterns across routers
user_subscription = await db.subscriptions.find_one({"user_id": user.user_id})
if user_subscription["subscription_type"] == "free":
    if usage_count >= 5:
        raise HTTPException(status_code=402, detail="Limit reached")
```

**After (Unified):**
```python
access_result = await sub_service.check_feature_access(
    user.user_id,
    FeatureName.AI_MENTOR.value,
    requested_amount=1
)

if not access_result.allowed:
    raise HTTPException(status_code=402, detail=access_result.to_dict())
```

### Step 3: Track Usage

**Before (Manual tracking):**
```python
await db.usage_tracking.update_one(
    {"user_id": user.user_id, "feature": "ai_mentor"},
    {"$inc": {"count": 1}},
    upsert=True
)
```

**After (Automatic):**
```python
# Track AFTER successful feature use
await sub_service.track_feature_use(
    user.user_id,
    FeatureName.AI_MENTOR.value,
    amount=1
)
```

---

## Frontend Integration

### 1. API Response Handling

```javascript
// In frontend API client
async function callAITutor(message) {
  try {
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
      credentials: 'include'
    });
    
    if (response.status === 402) {
      // Subscription limit reached
      const data = await response.json();
      
      // Show upgrade modal with student-friendly message
      showUpgradeModal({
        message: data.upgrade_message,
        currentTier: data.current_tier,
        usage: data.usage,
        nextReset: data.next_reset
      });
      
      return null;
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}
```

### 2. Upgrade Modal Component

```javascript
function UpgradeModal({ message, currentTier, usage, nextReset }) {
  return (
    <div className="upgrade-modal">
      <h2>✨ Ready to Level Up?</h2>
      
      <p className="limit-message">{message}</p>
      
      <div className="usage-info">
        <p>Today's Usage: {usage.used}/{usage.limit}</p>
        <p>Resets: {formatTime(nextReset)}</p>
      </div>
      
      <div className="upgrade-options">
        {currentTier === 'free' && (
          <>
            <button onClick={() => upgradeTo('basic')}>
              Upgrade to Basic
              <span>50 AI chats/day</span>
            </button>
            <button onClick={() => upgradeTo('premium')}>
              Go Premium
              <span>Unlimited everything!</span>
            </button>
          </>
        )}
        {currentTier === 'basic' && (
          <button onClick={() => upgradeTo('premium')}>
            Go Premium
            <span>Unlimited access</span>
          </button>
        )}
      </div>
    </div>
  );
}
```

---

## Router Migration Checklist

### Routers to Update

- [x] **`/api/ai`** - AI Tutor (✅ Updated)
- [ ] **`/api/mock-tests`** - Mock test generation
- [ ] **`/api/auto-notes`** - Auto-note generation
- [ ] **`/api/analytics`** - Detailed analysis (premium feature)

### For Each Router:

1. **Import unified service**
   ```python
   from services.unified_subscription_service import UnifiedSubscriptionService, FeatureName
   from dependencies import get_unified_subscription_service
   ```

2. **Add dependency to route**
   ```python
   sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
   ```

3. **Check access before feature use**
   ```python
   access_result = await sub_service.check_feature_access(user.user_id, feature, amount)
   if not access_result.allowed:
       raise HTTPException(status_code=402, detail=access_result.to_dict())
   ```

4. **Track usage after success**
   ```python
   await sub_service.track_feature_use(user.user_id, feature, amount)
   ```

5. **Remove old subscription checks**
   - Delete manual subscription queries
   - Remove hard-coded limit checks
   - Remove scattered usage tracking

---

## Testing

### 1. Test Access Control

```python
# Test FREE tier limits
async def test_free_tier_limits():
    service = UnifiedSubscriptionService(db)
    user_id = "test_user_free"
    
    # First 5 requests should succeed
    for i in range(5):
        result = await service.check_feature_access(
            user_id,
            FeatureName.AI_MENTOR.value
        )
        assert result.allowed == True
        await service.track_feature_use(user_id, FeatureName.AI_MENTOR.value)
    
    # 6th request should fail
    result = await service.check_feature_access(
        user_id,
        FeatureName.AI_MENTOR.value
    )
    assert result.allowed == False
    assert "limit reached" in result.message.lower()
```

### 2. Test Upgrade Flow

```python
async def test_upgrade_flow():
    service = UnifiedSubscriptionService(db)
    user_id = "test_user_upgrade"
    
    # Start as FREE
    tier = await service.get_user_tier(user_id)
    assert tier == "free"
    
    # Upgrade to PREMIUM
    success, message = await service.upgrade_subscription(user_id, "premium")
    assert success == True
    
    # Verify unlimited access
    result = await service.check_feature_access(
        user_id,
        FeatureName.AI_MENTOR.value
    )
    assert result.allowed == True
    assert result.limit == -1  # Unlimited
```

---

## Benefits

### 1. **Consistency**
- ✅ Single source of truth for all subscription logic
- ✅ Same limits enforced everywhere
- ✅ Consistent student messaging

### 2. **Maintainability**
- ✅ Update limits in one place (config)
- ✅ Add new features easily
- ✅ Clear separation of concerns

### 3. **Student Experience**
- ✅ Clear, friendly upgrade messages
- ✅ Transparent usage information
- ✅ Helpful reset times
- ✅ No surprise blocks

### 4. **Developer Experience**
- ✅ Simple API: check → use → track
- ✅ Type-safe enums
- ✅ Comprehensive error handling
- ✅ Well-documented

---

## Next Steps

1. **Complete router migration** (see checklist above)
2. **Update frontend components** with new 402 handling
3. **Add comprehensive tests** for all tiers and features
4. **Monitor usage patterns** to optimize limits
5. **Deprecate old SubscriptionService** after migration complete

---

## Support

For questions or issues:
- Check `/app/backend/services/unified_subscription_service.py` for implementation
- See `/app/backend/api/ai.py` for example usage
- Review this guide for patterns and best practices
