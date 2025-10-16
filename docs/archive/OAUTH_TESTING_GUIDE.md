# OAuth Complete Testing & Verification Guide

## Current Status

Based on backend testing:
- ✅ OAuth login endpoint: WORKING (307 redirect)
- ✅ OAuth state management: WORKING (MongoDB storage)
- ✅ Session validation logic: WORKING (401 without cookie)
- ✅ CORS configuration: WORKING (credentials allowed)
- ❌ **Session cookie setting: FAILING** (cookies not persisting)

---

## Root Cause Analysis

The backend infrastructure is 100% functional, but cookies aren't being set during OAuth callback. This could be due to:

1. **Response object handling** - Cookie might not be attached properly to redirect response
2. **Timing issue** - Cookie set but redirect happens before browser processes it
3. **Domain mismatch** - Cookie domain attribute not matching request domain
4. **Browser security** - Modern browsers rejecting cookies for various reasons

---

## Verification Steps (Manual Testing Required)

### Step 1: Clear Browser State
Before testing, ensure clean state:
```
1. Open Chrome DevTools (F12)
2. Application tab → Storage → Clear site data
3. Or use Incognito/Private mode
4. Close all tabs for the domain
```

### Step 2: Test OAuth Flow with DevTools Open

1. **Open DevTools Network Tab**
   - Press F12
   - Go to Network tab
   - Check "Preserve log"

2. **Visit Production URL**
   ```
   https://seamless-auth-1.emergent.host
   ```

3. **Click "Continue with Google"**
   - Watch Network tab for requests
   - Look for `/api/auth/google/login`
   - Should see 307 redirect

4. **Select Google Account**
   - Complete Google OAuth
   - Watch for `/api/auth/google/callback` request

5. **Check Callback Response**
   In Network tab, find the callback request:
   ```
   Name: google/callback?state=...&code=...
   Status: Should be 302 or 307
   ```
   
   Click on it and check:
   - **Response Headers** tab:
     - Look for `Set-Cookie: dhruv_ai_session=...`
     - Should have: `HttpOnly; Secure; SameSite=Lax; Path=/`
   
   - **Preview/Response** tab:
     - Should be a redirect response

6. **Check if Cookie Was Set**
   - DevTools → Application tab → Cookies
   - Expand `https://seamless-auth-1.emergent.host`
   - Look for `dhruv_ai_session` cookie
   
   **If cookie exists:**
   - ✅ Cookie is being set
   - Check: Secure ✓, HttpOnly ✓, SameSite: Lax
   - Value should be a long token string
   
   **If cookie does NOT exist:**
   - ❌ Cookie setting is failing
   - Check Console for errors
   - Proceed to troubleshooting

7. **Check /api/auth/session Request**
   - After redirect, look for `/api/auth/session` request
   - Click on it in Network tab
   - Check **Request Headers**:
     - Should have: `Cookie: dhruv_ai_session=...`
   
   **If cookie is sent:**
   - ✅ Cookie is being sent correctly
   - If still getting 401, it's a validation issue
   
   **If cookie is NOT sent:**
   - ❌ Browser is not sending the cookie
   - Possible domain/security issue

---

## Detailed Troubleshooting

### Issue 1: Cookie Not Being Set

**Symptoms:**
- After OAuth callback, no `dhruv_ai_session` cookie in DevTools
- Every request to `/api/auth/session` returns 401

**Check:**
1. In callback response, look for `Set-Cookie` header
2. If `Set-Cookie` exists but cookie not saved:
   - Check for `Secure` flag (required for HTTPS)
   - Check for domain attribute (should be empty or match domain)
   - Check browser console for cookie warnings

**Potential Causes:**
- Cookie `Secure` flag still False (should be True for HTTPS)
- Domain attribute set incorrectly
- Browser blocking third-party cookies (shouldn't apply here)

### Issue 2: Cookie Set But Not Sent

**Symptoms:**
- Cookie exists in DevTools → Application → Cookies
- But not sent in request headers to `/api/auth/session`

**Check:**
1. Cookie domain: Should match request domain
2. Cookie path: Should be `/` (matches all paths)
3. Cookie Secure: Should be checked (✓)
4. Cookie SameSite: Should be "Lax"

**Fix:**
- If domain is wrong, cookie won't be sent
- If path is wrong, cookie won't match
- If SameSite is "Strict", might not be sent after redirect

### Issue 3: Cookie Sent But Still 401

**Symptoms:**
- Cookie visible in DevTools
- Cookie sent in request headers (visible in Network tab)
- But still getting 401 response

**Check Backend:**
- Session token might not be in database
- Session might be expired
- DateTime comparison issue in validation query

**Debug Steps:**
1. Get the session token from cookie in DevTools
2. Check if it exists in MongoDB:
   ```javascript
   db.users.findOne({ session_token: "your-token-here" })
   ```
3. Check session_expiry format and value
4. Verify it's in the future

---

## Expected Behavior (Success Case)

### 1. OAuth Login Request
```
GET /api/auth/google/login
Status: 307 Temporary Redirect
Location: https://accounts.google.com/o/oauth2/v2/auth?...&state=abc123...
```

### 2. OAuth Callback Request
```
GET /api/auth/google/callback?state=abc123&code=xyz789...
Status: 302 Found
Location: https://seamless-auth-1.emergent.host/profile-setup (or /dashboard)
Set-Cookie: dhruv_ai_session=long-token-here; Path=/; HttpOnly; Secure; SameSite=Lax
```

### 3. Profile Setup/Dashboard Page
```
GET /profile-setup (or /dashboard)
Status: 200 OK
```

### 4. Session Check Request
```
GET /api/auth/session
Headers:
  Cookie: dhruv_ai_session=long-token-here
Status: 200 OK
Response: { "user": { "user_id": "...", "email": "...", ... } }
```

---

## Common Browser Console Errors

### Error: "Set-Cookie blocked by browser"
```
Indicates: Cookie rejected due to security policy
Fix: Ensure Secure flag is True for HTTPS domains
```

### Error: "SameSite attribute warning"
```
Indicates: Cookie SameSite attribute not set properly
Fix: Should be "Lax" for OAuth redirects
```

### Error: "Cookie domain mismatch"
```
Indicates: Cookie domain doesn't match request domain
Fix: Leave domain empty or set to null in set_cookie()
```

---

## Debug Checklist

### Before Testing:
- [ ] Cleared browser cache and cookies
- [ ] Using incognito/private mode
- [ ] DevTools open with Network tab
- [ ] "Preserve log" enabled in Network tab

### During OAuth Flow:
- [ ] `/api/auth/google/login` returns 307
- [ ] Redirected to Google OAuth
- [ ] Selected Google account successfully
- [ ] Redirected back to app
- [ ] `/api/auth/google/callback` appears in Network tab

### After Callback:
- [ ] Check callback response has `Set-Cookie` header
- [ ] Check DevTools → Application → Cookies for `dhruv_ai_session`
- [ ] Check if cookie has correct attributes (Secure, HttpOnly, SameSite)
- [ ] Check if `/api/auth/session` request includes cookie
- [ ] Check response from `/api/auth/session`

### If Still 401:
- [ ] Verify cookie value matches what's stored in MongoDB
- [ ] Check session_expiry in MongoDB (should be 7 days in future)
- [ ] Check backend logs for cookie setting confirmation
- [ ] Verify environment variables are correct in deployment

---

## Backend Log Messages to Look For

When OAuth works correctly, backend should log:

```
🔐 Initiating Google OAuth...
📍 Redirect URI: https://seamless-auth-1.emergent.host/api/auth/google/callback
🔑 Client ID: 401989768341-cs8oaj2...
🎫 Created OAuth state: abc123...

🔐 Starting Google OAuth callback processing...
📥 Query params - state: abc123..., code: xyz789...
✅ OAuth state verified
📡 Exchanging authorization code for access token...
✅ Tokens received
👤 User info - Email: user@gmail.com, Name: User Name
✅ New user created: uuid-here (or)
✅ Existing user found: uuid-here
🍪 Session cookie set (secure=True, token=abc123...)
🔄 Redirecting to: https://seamless-auth-1.emergent.host/profile-setup
```

---

## If Problem Persists

### Option 1: Check Deployment Logs
In Emergent dashboard:
1. Go to deployment details
2. Check backend logs
3. Look for cookie setting messages
4. Check for any errors during OAuth callback

### Option 2: Test with curl
```bash
# This won't work fully but helps debug cookie setting
curl -v https://seamless-auth-1.emergent.host/api/auth/google/callback?state=test&code=test
```
Check if response includes `Set-Cookie` header

### Option 3: Verify Environment Variables
In Emergent dashboard, confirm:
```
BACKEND_URL=https://seamless-auth-1.emergent.host (not preview domain)
FRONTEND_URL=https://seamless-auth-1.emergent.host
```

---

## Alternative Solution (If Cookie Approach Fails)

If cookies continue to fail, we can implement token-based auth:

1. After OAuth callback, instead of setting cookie, return token in URL query parameter
2. Frontend extracts token from URL
3. Store token in localStorage
4. Send token in Authorization header

This would require code changes but would bypass cookie issues entirely.

---

## Report Format

After testing, please provide:

**1. OAuth Login:**
- [ ] Works / Doesn't work
- Screenshot of Network tab showing redirect

**2. OAuth Callback:**
- [ ] Callback request appears in Network
- [ ] Response status code: ___
- [ ] `Set-Cookie` header present: Yes / No
- Screenshot of callback response headers

**3. Cookie in DevTools:**
- [ ] Cookie `dhruv_ai_session` exists: Yes / No
- Cookie attributes (if exists):
  - Secure: ✓ / ✗
  - HttpOnly: ✓ / ✗
  - SameSite: ___
  - Domain: ___
  - Path: ___
- Screenshot of cookies in DevTools

**4. Session Check:**
- [ ] Cookie sent in request: Yes / No
- [ ] Response status: ___
- Screenshot of /api/auth/session request headers

**5. Console Errors:**
- Any cookie-related warnings or errors
- Screenshot of console

This information will help identify the exact issue and provide a targeted fix.

---

**Next Steps:**
1. Follow the verification steps above
2. Document findings with screenshots
3. Report back with the detailed information
4. We'll implement a targeted fix based on findings
