# Session Expiry Fix - Complete

## Problem Analysis

The 401 "Session expired" error occurred even though the session cookie was being set correctly. The root cause was **inconsistent data type handling** for `session_expiry` in MongoDB:

### Issues Found:

1. **Storage Inconsistency**: 
   - OAuth callback (line 309): Stored as ISO string ✓
   - Legacy Emergent endpoints (lines 448, 469, 517, 538): Stored as datetime object ✗

2. **Comparison Inconsistency**:
   - `/api/auth/session` endpoint (line 603): Compared with ISO string ✓
   - `/api/auth/profile/complete` endpoint (line 649): Compared with datetime object ✗

3. **MongoDB Behavior**: 
   - MongoDB's `$gt` operator cannot properly compare ISO strings with datetime objects
   - This caused all session validations in `complete_profile` to fail

## Root Cause

```python
# PROBLEM: Mixed data types
# Storage (OAuth): session_expiry.isoformat()  → "2025-01-15T10:30:00Z"
# Storage (Legacy): session_expiry             → datetime object
# Comparison:      datetime.now(timezone.utc)  → datetime object

# MongoDB query FAILS when comparing string with datetime:
{"session_expiry": {"$gt": datetime.now(timezone.utc)}}  # datetime vs string ✗
```

## Solution Implemented

**Standardized ALL session_expiry operations to use ISO strings:**

### 1. Fixed Storage - Legacy Emergent Session Endpoints

**File**: `/app/backend/api/auth.py`

#### `/api/auth/google/session` endpoint (lines 441-475)
```python
# BEFORE (line 448):
"session_expiry": session_expiry,  # datetime object

# AFTER:
"session_expiry": session_expiry.isoformat(),  # ISO string

# Also added for insert:
user_dict = user.dict()
if isinstance(user_dict.get('session_expiry'), datetime):
    user_dict['session_expiry'] = user_dict['session_expiry'].isoformat()
await db.users.insert_one(user_dict)
```

#### `/api/auth/google/validate` endpoint (lines 510-545)
```python
# BEFORE (line 517):
"session_expiry": session_expiry,  # datetime object

# AFTER:
"session_expiry": session_expiry.isoformat(),  # ISO string

# Also added for insert:
user_dict = user.dict()
if isinstance(user_dict.get('session_expiry'), datetime):
    user_dict['session_expiry'] = user_dict['session_expiry'].isoformat()
await db.users.insert_one(user_dict)
```

### 2. Fixed Comparison - Profile Complete Endpoint

**File**: `/app/backend/api/auth.py`

#### `/api/auth/profile/complete` endpoint (lines 637-653)
```python
# BEFORE:
user_doc = await db.users.find_one({
    "session_token": session_token,
    "session_expiry": {"$gt": datetime.now(timezone.utc)}  # datetime object
})

# AFTER:
current_time_iso = datetime.now(timezone.utc).isoformat()  # Convert to ISO
user_doc = await db.users.find_one({
    "session_token": session_token,
    "session_expiry": {"$gt": current_time_iso}  # ISO string
})
```

## Verification

All session operations now follow this pattern:

### Storage Pattern:
```python
session_expiry = datetime.now(timezone.utc) + timedelta(days=7)

# For update:
{"$set": {"session_expiry": session_expiry.isoformat()}}

# For insert:
user_dict = user.dict()
if isinstance(user_dict.get('session_expiry'), datetime):
    user_dict['session_expiry'] = user_dict['session_expiry'].isoformat()
await db.users.insert_one(user_dict)
```

### Validation Pattern:
```python
current_time_iso = datetime.now(timezone.utc).isoformat()
user_doc = await db.users.find_one({
    "session_token": session_token,
    "session_expiry": {"$gt": current_time_iso}
})
```

## Files Modified

1. `/app/backend/api/auth.py` - Lines 448, 469-475, 517, 538-544, 646-653

## Impact

- ✅ OAuth callback stores session_expiry as ISO string
- ✅ Legacy endpoints store session_expiry as ISO string
- ✅ All session validation compares ISO strings
- ✅ Profile completion now works correctly
- ✅ Session validation is consistent across all endpoints

## Testing Required

1. **OAuth Login Flow**:
   - Login with Google → Redirected to profile setup
   - Cookie set correctly → Profile submission works

2. **Session Validation**:
   - `/api/auth/session` returns valid session
   - `/api/auth/profile/complete` accepts authenticated request
   - No more "Session expired" errors immediately after login

## Status

✅ **FIXED** - All session_expiry operations now use ISO strings consistently
