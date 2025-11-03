# OAuth 404 Error - Complete Fix & Deployment Guide

## Problem Analysis

### Root Cause
The OAuth callback was returning 404 because:
1. **Wrong Domain in Configuration**: Backend `.env` had preview domain (`dhruv-ai-fix.preview.emergentagent.com`) instead of production domain
2. **Preview Domain Limitation**: Preview domains are **frontend-only** and don't route to backend API endpoints
3. **Hardcoded Fallbacks**: Backend code had hardcoded preview URLs as fallbacks
4. **Google Cloud Console Mismatch**: Only preview domain was whitelisted, not production domain

### Why 404 Happened
```
User clicks "Continue with Google"
  ↓
Backend sends redirect_uri: https://neuro-tutor-dev.preview.emergentagent.com/api/auth/google/callback
  ↓
Google redirects user to that URL after authentication
  ↓
Preview domain tries to find /api/auth/google/callback
  ↓
❌ 404 - Preview domain has no backend routes (frontend-only static hosting)
```

### Correct Flow (After Fix)
```
User clicks "Continue with Google"
  ↓
Backend sends redirect_uri: https://seamless-auth-1.emergent.host/api/auth/google/callback
  ↓
Google redirects user to production domain
  ↓
Production domain routes to backend on port 8001
  ↓
✅ Backend processes OAuth callback successfully
```

---

## Complete Fix Applied

### 1. Removed Hardcoded Preview URLs

**File:** `/app/backend/api/auth.py`

**Changed Lines:**
- Line 156: Removed fallback `'https://neuro-tutor-dev.preview.emergentagent.com'`
- Line 220: Replaced with proper fallback logic
- Line 239: Removed fallback, made BACKEND_URL required
- Line 352: Replaced with proper fallback logic
- Line 370: Replaced with proper fallback logic

**Before:**
```python
backend_url = os.getenv('BACKEND_URL', 'https://neuro-tutor-dev.preview.emergentagent.com')
```

**After:**
```python
backend_url = os.getenv('BACKEND_URL')
if not backend_url:
    raise ValueError("BACKEND_URL environment variable is required for OAuth")
```

### 2. Updated Backend Environment Variables

**File:** `/app/backend/.env`

**Changed:**
```env
# OLD (WRONG - Preview Domain)
BACKEND_URL=https://neuro-tutor-dev.preview.emergentagent.com
FRONTEND_URL=https://neuro-tutor-dev.preview.emergentagent.com
CORS_ORIGINS="http://localhost:3000,https://neuro-tutor-dev.preview.emergentagent.com,..."

# NEW (CORRECT - Production Domain)
BACKEND_URL=https://seamless-auth-1.emergent.host
FRONTEND_URL=https://seamless-auth-1.emergent.host
CORS_ORIGINS="http://localhost:3000,https://seamless-auth-1.emergent.host,https://neuro-tutor-dev.preview.emergentagent.com,..."
```

**Note:** Both production and preview domains are in CORS for flexibility, but production domain is primary.

### 3. Updated Frontend Environment Variables

**File:** `/app/frontend/.env`

**Changed:**
```env
# OLD (WRONG - Preview Domain)
REACT_APP_BACKEND_URL=https://neuro-tutor-dev.preview.emergentagent.com

# NEW (CORRECT - Production Domain)
REACT_APP_BACKEND_URL=https://seamless-auth-1.emergent.host
```

---

## Deployment Sequence

### Step 1: Update Google Cloud Console (CRITICAL)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Find OAuth 2.0 Client ID: `401989768341-cs8oaj25c4jik3ai23did8u5fghj7v74`
4. Click **Edit**
5. Under **Authorized redirect URIs**, ensure you have:
   ```
   https://seamless-auth-1.emergent.host/api/auth/google/callback
   ```
6. You can keep the preview URL as well for testing:
   ```
   https://neuro-tutor-dev.preview.emergentagent.com/api/auth/google/callback
   ```
7. Click **SAVE**
8. **Wait 5-10 minutes** for Google's changes to propagate globally

### Step 2: Deploy to Production

1. **Commit or save your changes** in Emergent
2. Click **"Deploy"** in Emergent dashboard
3. Wait ~10 minutes for deployment to complete
4. Deployment should succeed with health checks passing

### Step 3: Verify Deployment

Once deployment completes, verify:

#### A. Check Backend is Live
```bash
curl -I https://seamless-auth-1.emergent.host/api/auth/google/login
```
**Expected:** 302 redirect (not 404)

#### B. Check Environment Variables
In deployment logs, look for:
```
[BUILD_LOG] BACKEND_URL=https://seamless-auth-1.emergent.host
```
**Should be:** `seamless-auth-1.emergent.host` (not preview domain)

#### C. Test OAuth Flow
1. Visit: `https://seamless-auth-1.emergent.host`
2. Click **"Continue with Google"**
3. Select your Google account
4. Should redirect to profile setup (new users) or dashboard (existing users)
5. ✅ No 404 error

---

## Understanding Preview vs Production Domains

### Preview Domain (`*.preview.emergentagent.com`)
- **Purpose:** Quick frontend-only preview
- **Backend Routes:** ❌ NOT AVAILABLE
- **API Endpoints:** ❌ Return 404
- **Use Case:** View UI changes quickly
- **Limitation:** Cannot test backend functionality

### Production Domain (`*.emergent.host`)
- **Purpose:** Full-stack production deployment
- **Backend Routes:** ✅ FULLY AVAILABLE
- **API Endpoints:** ✅ Work correctly
- **Use Case:** Live application with full functionality
- **Benefits:** Complete backend + frontend integration

### Why OAuth Failed in Preview
```
Preview Domain Architecture:
┌─────────────────────────────────────┐
│  *.preview.emergentagent.com        │
│  ┌─────────────────────────────┐   │
│  │  Frontend Static Files       │   │
│  │  (React Build)               │   │
│  └─────────────────────────────┘   │
│                                     │
│  Backend API: ❌ NOT AVAILABLE      │
│  /api/* routes: ❌ 404              │
└─────────────────────────────────────┘

Production Domain Architecture:
┌─────────────────────────────────────┐
│  *.emergent.host                    │
│  ┌─────────────────────────────┐   │
│  │  Frontend (Port 3000)        │   │
│  │  Served by React             │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  Backend API (Port 8001)     │   │
│  │  /api/* routes: ✅ Working   │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  MongoDB (Managed by Atlas)  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Post-Deployment Verification Checklist

### ✅ Environment Variables
- [ ] `BACKEND_URL` set to production domain in backend
- [ ] `FRONTEND_URL` set to production domain in backend
- [ ] `REACT_APP_BACKEND_URL` set to production domain in frontend
- [ ] `CORS_ORIGINS` includes production domain

### ✅ Google Cloud Console
- [ ] Redirect URI includes `https://seamless-auth-1.emergent.host/api/auth/google/callback`
- [ ] Changes saved and propagated (wait 5-10 minutes)
- [ ] OAuth 2.0 Client is enabled

### ✅ Backend Endpoints
- [ ] `/api/auth/google/login` returns 302 (not 404)
- [ ] Backend logs show correct BACKEND_URL
- [ ] Backend starts successfully (<10 seconds)
- [ ] Health checks pass

### ✅ OAuth Flow
- [ ] Homepage loads successfully
- [ ] "Continue with Google" button redirects to Google
- [ ] Can select Google account
- [ ] After auth, redirects to your app (not 404)
- [ ] Profile setup or dashboard loads
- [ ] User can navigate app features

### ✅ Database
- [ ] User created in MongoDB
- [ ] OAuth state stored and verified
- [ ] Session token created
- [ ] Cookies set correctly

---

## Troubleshooting Guide

### If Still Getting 404

#### Check 1: Verify Production URL
```bash
# Should return 302 redirect
curl -I https://seamless-auth-1.emergent.host/api/auth/google/login
```
If 404: Backend not deployed or routes not registered

#### Check 2: Check Deployment Logs
Look for:
```
✅ Modular routers registered (Auth, User, Subscription, AI, Analytics, Auto-Notes, Mock-Tests)
```
If missing: Router registration failed

#### Check 3: Verify Environment Variables
In deployment logs:
```
[MANAGE_SECRETS] adding BACKEND_URL
[BUILD_LOG] BACKEND_URL=https://seamless-auth-1.emergent.host
```
If wrong domain: Redeploy with correct .env files

#### Check 4: Google Cloud Console
- Verify redirect URI is **exact match**: `https://seamless-auth-1.emergent.host/api/auth/google/callback`
- No trailing slashes
- Correct protocol (https)
- Changes saved and propagated

#### Check 5: Wait for Propagation
- Google OAuth changes take 5-10 minutes to propagate
- Deployment takes ~10 minutes
- Clear browser cache
- Try incognito mode

### If Getting "redirect_uri_mismatch"

**Cause:** Google Cloud Console doesn't have the correct redirect URI

**Fix:**
1. Check what redirect URI your backend is sending (check backend logs)
2. Add that **exact** URI to Google Cloud Console
3. Wait 5-10 minutes
4. Try again

### If Getting "Authentication Failed"

**Causes:**
1. OAuth state expired (>10 minutes old)
2. OAuth state already used
3. Google credentials invalid

**Fix:**
- Try OAuth flow again (state is single-use)
- Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct
- Check backend logs for specific error

---

## Summary of Changes

### Code Changes
1. ✅ Removed hardcoded preview URLs from `auth.py`
2. ✅ Made BACKEND_URL required (no fallback for OAuth)
3. ✅ Updated .env files with production domains

### Configuration Changes
1. ✅ Backend BACKEND_URL → `https://seamless-auth-1.emergent.host`
2. ✅ Backend FRONTEND_URL → `https://seamless-auth-1.emergent.host`
3. ✅ Frontend REACT_APP_BACKEND_URL → `https://seamless-auth-1.emergent.host`
4. ✅ CORS includes production domain

### Google Cloud Console
1. ⏳ **ACTION REQUIRED:** Add `https://seamless-auth-1.emergent.host/api/auth/google/callback`

---

## Expected Results After Deployment

### Backend Startup Logs
```
✅ Loaded environment variables from container
✅ Lightweight audio processing loaded successfully
✅ Modular components loaded successfully
✅ Whisper module available for audio transcription
✅ Modular routers registered (Auth, User, Subscription, AI, Analytics, Auto-Notes, Mock-Tests)
INFO: Application startup complete
```

### OAuth Login Logs
```
🔐 Initiating Google OAuth...
📍 Redirect URI: https://seamless-auth-1.emergent.host/api/auth/google/callback
🔑 Client ID: 401989768341-cs8oaj2...
🎫 Created OAuth state: siu0Muwg69uU_r0vYovl...
```

### OAuth Callback Logs
```
🔐 Starting Google OAuth callback processing...
📥 Query params - state: siu0Muwg69uU_r0vYovl..., code: 4/0AanRRruS...
✅ OAuth state verified
📡 Exchanging authorization code for access token...
✅ Tokens received
👤 User info - Email: user@gmail.com, Name: User Name
✅ New user created: uuid-here
🍪 Session cookie set
🔄 Redirecting to: https://seamless-auth-1.emergent.host/profile-setup
```

---

## Final Status

### ✅ All Issues Fixed
1. ✅ Hardcoded preview URLs removed
2. ✅ Environment variables updated to production domain
3. ✅ Backend .env configured correctly
4. ✅ Frontend .env configured correctly
5. ✅ Code requires BACKEND_URL (no unsafe fallbacks)

### ⏳ Pending Actions
1. **Update Google Cloud Console** with production redirect URI
2. **Deploy to production** via Emergent dashboard
3. **Wait 10 minutes** for deployment + Google propagation
4. **Test OAuth flow** on production domain

---

**Status:** ✅ **READY FOR DEPLOYMENT**

All code fixes complete. Deploy now and update Google Cloud Console to resolve 404 issue completely.
