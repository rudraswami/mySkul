# Re-Login and Profile Setup Fix

## Problems Identified

### Issue 1: Re-login Failed with "Session expired or invalid"
After logout, users attempting to log in again received a 401 error with "Session expired or invalid" message.

### Issue 2: Existing Users Shown Profile Setup
Users who had already completed their profile were being redirected to the profile setup screen on re-login instead of the dashboard.

## Root Cause Analysis

### Issue 1 Root Cause: Race Condition

**The Problem Flow:**
```
1. User redirected to /dashboard?session_token=abc123
2. React Router renders Dashboard component
3. AuthContext useEffect runs IMMEDIATELY
4. AuthContext calls /api/auth/session to verify session
5. BUT cookie hasn't been set yet! (Dashboard sets it later)
6. Backend can't find session → "Session expired or invalid"
7. User appears logged out
```

**Why It Happened:**
- AuthContext and Dashboard components were **both** trying to handle `session_token` independently
- AuthContext's session check ran **before** Dashboard could set the cookie
- The timing was non-deterministic - sometimes Dashboard won, sometimes AuthContext won
- This created an unreliable authentication flow

### Issue 2 Root Cause: User Info Not Available

ProfileSetup was relying on sessionStorage to display user info (name, photo), but:
- sessionStorage wasn't being populated during OAuth flow
- No mechanism to pass user info from backend to ProfileSetup
- Resulted in missing user display data

## Solution Implemented

### 1. Centralized Session Token Handling in AuthContext

**File**: `/app/frontend/src/contexts/AuthContext.js`

Moved ALL session_token URL parameter handling into AuthContext's initialization:

```javascript
useEffect(() => {
  const checkAuth = async () => {
    // CRITICAL: Check if session_token is in URL (OAuth redirect)
    const params = new URLSearchParams(window.location.search);
    const sessionToken = params.get('session_token');
    
    if (sessionToken) {
      console.log('🍪 OAuth redirect detected - setting session cookie from URL');
      
      // Set session cookie client-side BEFORE checking session
      const domain = window.location.hostname.includes('emergent.host') 
        ? '.emergent.host' 
        : window.location.hostname;
      
      const cookieString = `dhruv_ai_session=${sessionToken}; path=/; domain=${domain}; secure; samesite=none; max-age=604800`;
      document.cookie = cookieString;
      
      console.log('✅ Session cookie set in AuthContext');
      
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // NOW check session (cookie is already set)
    const response = await fetch(`${BACKEND_URL}/api/auth/session`, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (response.ok) {
      const data = await response.json();
      setUser(data.user);
      console.log('✅ Session validated, user loaded:', data.user.email);
    }
    ...
  };
  
  checkAuth();
}, [token]);
```

**Key Changes:**
1. ✅ Cookie is set **synchronously** before session check
2. ✅ Single source of truth for session initialization
3. ✅ No race condition between components
4. ✅ Removed Authorization header (relies on cookie only)

### 2. Removed Duplicate Session Handling

**Files Modified:**
- `/app/frontend/src/components/Dashboard.js`
- `/app/frontend/src/components/auth/ProfileSetup.js`

Removed duplicate session_token handling code from both components:

```javascript
// REMOVED from Dashboard and ProfileSetup:
const urlParams = new URLSearchParams(window.location.search);
const sessionToken = urlParams.get('session_token');
if (sessionToken) {
  // Set cookie logic...
}
```

Now these components trust AuthContext to handle authentication.

### 3. Pass User Info to ProfileSetup via URL

**File**: `/app/backend/api/auth.py`

Updated OAuth callback to pass user details in URL for new users:

```python
# For new users, pass user info in URL for ProfileSetup display
if not profile_completed:
    from urllib.parse import quote
    redirect_url = (
        f"{frontend_url}/profile-setup?"
        f"session_token={session_token}&"
        f"name={quote(name)}&"
        f"email={quote(email)}&"
        f"photo_url={quote(picture)}"
    )
else:
    # Existing users go directly to dashboard
    redirect_url = f"{frontend_url}/dashboard?session_token={session_token}"
```

### 4. ProfileSetup Reads User Info from URL

**File**: `/app/frontend/src/components/auth/ProfileSetup.js`

```javascript
useEffect(() => {
  // Get user info from URL parameters (passed by OAuth callback)
  const urlParams = new URLSearchParams(window.location.search);
  const name = urlParams.get('name');
  const email = urlParams.get('email');
  const photoUrl = urlParams.get('photo_url');
  
  if (name && email) {
    setUserInfo({
      name: decodeURIComponent(name),
      email: decodeURIComponent(email),
      photo_url: photoUrl ? decodeURIComponent(photoUrl) : null
    });
    
    // Clean URL
    window.history.replaceState({}, document.title, window.location.pathname);
  }
  ...
}, []);
```

## Complete Flow After Fix

### New User Login:
```
1. User clicks "Continue with Google"
2. Google OAuth → Backend callback
3. Backend creates user (profile_completed: false)
4. Backend redirects: /profile-setup?session_token=...&name=...&email=...&photo_url=...
5. AuthContext detects session_token → Sets cookie FIRST
6. AuthContext calls /api/auth/session → Validates & loads user
7. ProfileSetup reads name/email/photo from URL → Displays user info
8. User completes profile → updateUser() → navigate to dashboard ✅
```

### Existing User Re-login:
```
1. User clicks "Continue with Google"
2. Google OAuth → Backend callback
3. Backend finds existing user (profile_completed: true)
4. Backend redirects: /dashboard?session_token=...
5. AuthContext detects session_token → Sets cookie FIRST
6. AuthContext calls /api/auth/session → Validates & loads user
7. App.js checks user.profile_completed: true → Renders Dashboard ✅
8. User lands on Dashboard (no profile setup) ✅
```

### Logout → Re-login Flow:
```
1. User logs out → session cleared in DB and cookie
2. User clicks login again
3. OAuth flow → New session created
4. AuthContext sets new cookie → Session validates
5. Existing user redirected to dashboard ✅
6. No "Session expired" error ✅
```

## Files Modified

1. `/app/frontend/src/contexts/AuthContext.js`
   - Centralized session_token handling
   - Sets cookie before session check
   - Added detailed logging

2. `/app/frontend/src/components/Dashboard.js`
   - Removed duplicate session_token handling

3. `/app/frontend/src/components/auth/ProfileSetup.js`
   - Removed duplicate session_token handling
   - Reads user info from URL parameters
   - Fallback to sessionStorage for compatibility

4. `/app/backend/api/auth.py`
   - Pass user info (name, email, photo_url) in redirect URL for new users
   - URL-encode values for safety

## Testing Checklist

### Test 1: New User Flow
- [x] Click "Continue with Google"
- [x] Complete OAuth
- [x] Land on profile setup
- [x] See user photo and name
- [x] Complete profile
- [x] Redirect to dashboard
- [x] No errors in console

### Test 2: Existing User Re-login
- [x] Login (if not already)
- [x] Logout
- [x] Click "Continue with Google" again
- [x] Skip profile setup (should go to dashboard)
- [x] Land on dashboard directly
- [x] No "Session expired" error
- [x] Dashboard loads correctly

### Test 3: Session Persistence
- [x] Login
- [x] Refresh page
- [x] Still logged in
- [x] No repeated redirects

## Status

✅ **FIXED** - Both issues resolved:
1. Re-login now works without "Session expired" errors
2. Existing users skip profile setup and go directly to dashboard
3. New users see profile setup with their info displayed
4. No race conditions in authentication flow
