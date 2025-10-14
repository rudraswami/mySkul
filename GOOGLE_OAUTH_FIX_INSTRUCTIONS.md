# Google OAuth Redirect Loop Fix

## Problem
After selecting Google account, user is redirected back to login screen. This happens because the OAuth redirect URI is not properly configured in Google Cloud Console.

## Root Cause
Both `BACKEND_URL` and `FRONTEND_URL` are set to the same domain (`https://seamless-auth-1.emergent.host`), which is correct for the Kubernetes Ingress setup. However, the Google Cloud Console needs to have the exact redirect URI whitelisted.

## Required Configuration

### 1. Google Cloud Console Setup

You need to add the following **Authorized redirect URI** in your Google Cloud Console:

```
https://seamless-auth-1.emergent.host/api/auth/google/callback
```

#### Steps to Add Redirect URI:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Find your OAuth 2.0 Client ID: `401989768341-cs8oaj25c4jik3ai23did8u5fghj7v74`
4. Click on it to edit
5. Under **Authorized redirect URIs**, add:
   ```
   https://seamless-auth-1.emergent.host/api/auth/google/callback
   ```
6. Click **Save**

### 2. Verify Environment Variables

The environment variables are correctly configured in `/app/backend/.env`:

```env
BACKEND_URL=https://seamless-auth-1.emergent.host
FRONTEND_URL=https://seamless-auth-1.emergent.host
GOOGLE_CLIENT_ID=401989768341-cs8oaj25c4jik3ai23did8u5fghj7v74
GOOGLE_CLIENT_SECRET=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
```

**IMPORTANT:** Make sure the Emergent dashboard also has these same values configured for deployment.

## How the OAuth Flow Works

1. User clicks "Continue with Google" on `/login`
2. Backend redirects to Google with `redirect_uri=https://seamless-auth-1.emergent.host/api/auth/google/callback`
3. User selects Google account
4. Google redirects back to `https://seamless-auth-1.emergent.host/api/auth/google/callback` with authorization code
5. Backend exchanges code for user info
6. Backend sets session cookie and redirects to `/profile-setup` or `/dashboard`

## Why Same Domain Works

In your Kubernetes Ingress setup:
- All `/api/*` requests → Backend (port 8001)
- All other requests → Frontend (port 3000)

So `https://seamless-auth-1.emergent.host/api/auth/google/callback` correctly hits the backend.

## Testing After Fix

After adding the redirect URI to Google Console, test the flow:

1. Clear browser cookies for `seamless-auth-1.emergent.host`
2. Go to `https://seamless-auth-1.emergent.host/login`
3. Click "Continue with Google"
4. Select your Google account
5. You should be redirected to `/profile-setup` (first time) or `/dashboard` (returning user)

## Additional Check: CORS Configuration

The CORS configuration in `.env` already includes the production domain:
```env
CORS_ORIGINS="http://localhost:3000,https://seamless-auth-1.emergent.host,https://dhruv-seamless-login.preview.emergentagent.com,https://dhruv-ai-fix.preview.static.emergentagent.com"
```

This is correct and should work.

## Potential Issues to Monitor

1. **Cookie not being set**: Check browser DevTools → Application → Cookies for `dhruv_ai_session`
2. **CORS errors**: Check browser console for CORS-related errors
3. **Session not persisting**: Verify session cookie has correct domain and path settings

## If Issue Persists

If the issue continues after adding the redirect URI:

1. Check browser console for errors
2. Check Network tab for failed requests
3. Verify the session cookie is being set correctly
4. Ensure Google OAuth consent screen is properly configured
