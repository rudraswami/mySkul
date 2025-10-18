# SameSite=None Cookie Fix - Cross-Domain OAuth

## Problem Summary

**Issue:** After successful Google OAuth login, users get 401 on `/api/auth/session`

**Root Cause:** Cookie with `SameSite=Lax` not sent in cross-domain requests

**Environment:**
- Frontend: `https://eduai-platform-25.preview.emergentagent.com` (`.emergentagent.com` domain)
- Backend: `https://seamless-auth-1.emergent.host` (`.emergent.host` domain)

**Impact:** Different top-level domains → all requests are cross-site → browser blocks `SameSite=Lax` cookies

---

## Technical Explanation

### SameSite Cookie Policy

Browsers implement SameSite cookie policies to prevent CSRF attacks:

**SameSite=Strict:**
- Cookie only sent on same-site requests
- Most secure, but breaks many legitimate use cases

**SameSite=Lax:** (Previous setting)
- Cookie sent on top-level navigation (clicking links)
- NOT sent on cross-site sub-requests (fetch, XHR, img, etc.)
- Default in modern browsers

**SameSite=None:**
- Cookie sent on all requests (same-site and cross-site)
- Requires `Secure=True` (HTTPS only)
- Used for legitimate cross-site use cases (like OAuth)

### Why Our Setup Failed

```
User Flow:
1. Frontend (emergentagent.com) → User clicks "Continue with Google"
2. Backend (emergent.host) → Redirects to Google OAuth
3. Google → User authenticates
4. Google → Redirects to backend callback (emergent.host)
5. Backend → Sets cookie with SameSite=Lax
6. Backend → Redirects to frontend (emergentagent.com)
7. Frontend → Makes XHR to backend /api/auth/session
8. Browser → BLOCKS cookie (cross-site XHR with SameSite=Lax)
9. Backend → Returns 401 (no cookie received)
```

**Key Issue:** Step 8 - Browser blocks the cookie because:
- Request is from `.emergentagent.com` to `.emergent.host` (cross-site)
- Cookie has `SameSite=Lax`
- Browser policy: Lax cookies not sent on cross-site sub-requests

---

## Solution Implemented

### Code Change

**File:** `/app/backend/api/auth.py` (Line ~340)

**Before:**
```python
response.set_cookie(
    key="dhruv_ai_session",
    value=session_token,
    max_age=7 * 24 * 60 * 60,
    httponly=True,
    secure=is_https,
    samesite="lax",  # ❌ Blocks cross-site requests
    path="/",
    domain=None
)
```

**After:**
```python
response.set_cookie(
    key="dhruv_ai_session",
    value=session_token,
    max_age=7 * 24 * 60 * 60,
    httponly=True,
    secure=is_https,  # True for HTTPS
    samesite="none",  # ✅ Allows cross-site requests
    path="/",
    domain=None
)
```

### Cookie Attributes Explained

**`httponly=True`:**
- Cookie not accessible via JavaScript
- Prevents XSS attacks
- ✅ Keep enabled for security

**`secure=is_https`:**
- Cookie only sent over HTTPS
- Required for `SameSite=None`
- ✅ Auto-detected from BACKEND_URL

**`samesite="none"`:**
- Allows cross-site cookie sending
- Enables preview frontend → production backend
- ⚠️ Requires `Secure=True`

**`path="/"`:**
- Cookie sent for all paths
- ✅ Correct for session cookies

**`domain=None`:**
- Browser sets domain to exact host
- Most compatible approach
- ✅ Works for all scenarios

---

## Security Considerations

### Is SameSite=None Safe?

**YES**, because we have multiple layers of protection:

1. **HttpOnly Flag:** Prevents JavaScript access (XSS protection)
2. **Secure Flag:** Only sent over HTTPS (prevents interception)
3. **CSRF Token:** Backend has CSRF middleware (when enabled)
4. **Origin Validation:** CORS configured to allow specific origins only
5. **Session Expiry:** Tokens expire after 7 days
6. **Token Uniqueness:** Each session has unique token

**SameSite=None is appropriate for:**
- OAuth flows across domains
- Legitimate cross-site authenticated requests
- When other security measures are in place

---

## Testing Requirements

### Expected Cookie Attributes

After OAuth callback, in DevTools → Application → Cookies:

```
Name: dhruv_ai_session
Value: [long-token-string]
Domain: seamless-auth-1.emergent.host
Path: /
Expires: [7 days from now]
Size: ~50-100 bytes
HttpOnly: ✓
Secure: ✓
SameSite: None
Priority: Medium
```

### Network Tab Verification

**OAuth Callback Response:**
```
Status: 302 Found
Set-Cookie: dhruv_ai_session=abc123...; Path=/; HttpOnly; Secure; SameSite=None
Location: https://eduai-platform-25.preview.emergentagent.com/profile-setup
```

**Session Check Request:**
```
GET /api/auth/session
Cookie: dhruv_ai_session=abc123...
```

**Session Check Response:**
```
Status: 200 OK
Body: { "user": { "user_id": "...", "email": "...", ... } }
```

---

## Deployment Checklist

### Pre-Deployment
- [x] Code change implemented (`samesite="none"`)
- [x] Backend tested locally
- [x] No syntax errors
- [x] Backend starts successfully

### Post-Deployment
- [ ] Deploy to production
- [ ] Wait 5 minutes for full deployment
- [ ] Test OAuth flow from preview frontend
- [ ] Verify cookie in DevTools (SameSite=None)
- [ ] Verify `/api/auth/session` returns 200 OK
- [ ] Verify user enters dashboard successfully

### Verification Steps

1. **Clear Browser State**
   ```
   Chrome DevTools → Application → Storage → Clear site data
   ```

2. **Open DevTools Network Tab**
   ```
   F12 → Network → Check "Preserve log"
   ```

3. **Visit Preview Frontend**
   ```
   https://eduai-platform-25.preview.emergentagent.com
   ```

4. **Complete OAuth Flow**
   - Click "Continue with Google"
   - Select Google account
   - Should redirect to profile-setup or dashboard

5. **Verify in DevTools**
   - Check callback response for `Set-Cookie` header
   - Verify cookie attributes in Application → Cookies
   - Verify cookie sent in session check request
   - Verify session check returns 200 OK

---

## Troubleshooting

### Issue: Cookie Still Not Sent

**Check 1: Cookie Attributes**
- SameSite must be "None" (capital N)
- Secure must be checked (✓)
- HttpOnly must be checked (✓)

**Check 2: HTTPS**
- Both frontend and backend must use HTTPS
- `SameSite=None` requires Secure flag
- Secure flag requires HTTPS

**Check 3: Browser Support**
- All modern browsers support SameSite=None
- Very old browsers might not support it

### Issue: Still Getting 401

**Check 1: Cookie in Request**
- Network tab → session request → Request Headers
- Should have: `Cookie: dhruv_ai_session=...`
- If missing, cookie not being sent

**Check 2: Session in Database**
- Query MongoDB for session_token
- Verify token exists and not expired
- Check session_expiry is in future

**Check 3: Backend Logs**
- Look for: "🍪 Session cookie set (secure=True, samesite=none, token=...)"
- Verify cookie is being set during callback

---

## Expected User Flow (After Fix)

```
1. User visits: https://eduai-platform-25.preview.emergentagent.com
   ↓
2. Clicks "Continue with Google"
   ↓
3. Frontend redirects to: https://seamless-auth-1.emergent.host/api/auth/google/login
   ↓
4. Backend redirects to: https://accounts.google.com/o/oauth2/v2/auth?...
   ↓
5. User selects Google account
   ↓
6. Google redirects to: https://seamless-auth-1.emergent.host/api/auth/google/callback?code=...
   ↓
7. Backend:
   - Exchanges code for tokens ✅
   - Gets user info from Google ✅
   - Creates/updates user in MongoDB ✅
   - Sets cookie (SameSite=None) ✅
   ↓
8. Backend redirects to: https://eduai-platform-25.preview.emergentagent.com/profile-setup
   ↓
9. Frontend loads, makes XHR to: https://seamless-auth-1.emergent.host/api/auth/session
   ↓
10. Browser includes cookie (SameSite=None allows this) ✅
    ↓
11. Backend validates session ✅
    ↓
12. Backend returns 200 OK with user data ✅
    ↓
13. User enters dashboard ✅
```

---

## Alternative Solutions (If Issue Persists)

If `SameSite=None` doesn't work, we have backup options:

### Option 1: Token-Based Auth
- Return token in URL query parameter after OAuth
- Frontend stores token in localStorage
- Send token in Authorization header
- No cookies needed

### Option 2: Same-Domain Setup
- Use production URL for frontend too
- Both on `.emergent.host` domain
- Cookies work with `SameSite=Lax`

### Option 3: Proxy Pattern
- Frontend proxies backend requests through same domain
- All requests appear same-site to browser
- Cookies work with `SameSite=Lax`

---

## Summary

### Change Made
✅ Changed `samesite="lax"` to `samesite="none"` in OAuth callback cookie

### Why It Fixes The Issue
- Allows cookies to be sent in cross-site requests
- Enables preview frontend (emergentagent.com) to send cookies to production backend (emergent.host)
- Required for OAuth flow across different domains

### Security
- Still secure with HttpOnly, Secure, CSRF protection, and origin validation
- `SameSite=None` is industry-standard for legitimate cross-site auth

### Next Steps
1. Deploy the fix
2. Test OAuth flow from preview frontend
3. Verify cookie in DevTools (SameSite=None)
4. Confirm `/api/auth/session` returns 200 OK

---

**Status:** ✅ **FIX IMPLEMENTED - READY FOR DEPLOYMENT**

Cookie configuration updated to support cross-domain OAuth between preview frontend and production backend.
