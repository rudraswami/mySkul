# Preview vs Production Testing Guide

## Current Situation

You have **two environments**:
1. **Preview**: `https://edtech-fixes.preview.emergentagent.com`
2. **Production**: `https://seamless-auth-1.emergent.host`

Currently, the `.env` files are configured for **production** URLs, which is why preview testing encounters OAuth state errors.

## The Problem

When you test on preview with production URLs in `.env`:
```
Frontend .env: REACT_APP_BACKEND_URL=https://edtech-fixes.preview.emergentagent.com ✓
Backend .env:  BACKEND_URL=https://seamless-auth-1.emergent.host ✗
               FRONTEND_URL=https://seamless-auth-1.emergent.host ✗
```

**What happens:**
1. User clicks login on preview frontend
2. Preview backend initiates OAuth with production redirect_uri
3. Google redirects to production, not preview
4. OAuth state stored in preview DB, but callback goes to production DB
5. Result: "Invalid or expired OAuth state" error

## Solutions

### ✅ **Option 1: Test on Production (RECOMMENDED)**

**Advantages:**
- ✅ No environment configuration changes needed
- ✅ .env files already configured correctly
- ✅ No risk of breaking production
- ✅ Exactly matches real user experience
- ✅ Shared database means all data is in sync

**How to test:**
1. Go to: `https://seamless-auth-1.emergent.host`
2. Test complete login flow
3. All features work as expected

**Why it's safe:**
- Preview and production are **separate deployments** in Kubernetes
- They run in **isolated containers**
- Changes you make in code only affect the environment you deploy to
- Testing on production URL uses production environment (not preview code)

---

### Option 2: Environment Variable Overrides (For Preview Testing)

If you specifically need to test on preview URL, use Emergent's environment variable override feature.

#### Step-by-Step Setup:

1. **In Emergent Dashboard:**
   - Navigate to your app settings
   - Find "Environment Variables" section
   - Look for "Preview Environment Overrides" or similar

2. **Add Preview-Specific Variables:**
   ```
   For Preview Environment:
   BACKEND_URL=https://edtech-fixes.preview.emergentagent.com
   FRONTEND_URL=https://edtech-fixes.preview.emergentagent.com
   ```

3. **Keep Production Variables As-Is:**
   ```
   For Production Environment:
   BACKEND_URL=https://seamless-auth-1.emergent.host
   FRONTEND_URL=https://seamless-auth-1.emergent.host
   ```

4. **Redeploy Preview** (production remains unchanged)

#### How It Works:
- Environment-specific overrides take precedence over `.env` files
- Preview gets preview URLs
- Production keeps production URLs
- No code changes needed
- Both environments work independently

---

### Option 3: Google OAuth Console Update (Allows Both)

Add **both** callback URLs to your Google OAuth Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to: APIs & Services → Credentials
4. Find your OAuth 2.0 Client ID
5. Add both redirect URIs:
   ```
   https://seamless-auth-1.emergent.host/api/auth/google/callback
   https://edtech-fixes.preview.emergentagent.com/api/auth/google/callback
   ```

**Advantages:**
- Both environments work simultaneously
- No configuration changes needed
- Useful for parallel testing

**Limitation:**
- Still need environment variable overrides (Option 2) for backend to use correct URL

---

## Understanding Preview vs Production

### They Are Completely Separate:

| Aspect | Preview | Production |
|--------|---------|------------|
| **Code** | Latest changes from your session | Last deployed/published code |
| **Container** | Separate Kubernetes pod | Separate Kubernetes pod |
| **Database** | Usually shared MongoDB | Usually shared MongoDB |
| **URL** | *.preview.emergentagent.com | Your custom domain |
| **Impact** | Testing only | Real users |

### Key Points:

1. **Code Changes Only Affect the Environment You Deploy To**
   - Making changes in your session doesn't auto-update production
   - You control when changes go to production via deployment

2. **Database is Typically Shared**
   - Both environments often use the same MongoDB instance
   - Data changes affect both environments
   - User accounts created in one are visible in the other

3. **Environment Variables Can Be Different**
   - Use dashboard overrides for environment-specific configs
   - URLs, API keys, feature flags can differ

4. **Testing on Production is Safe IF:**
   - You've already deployed to production
   - You're testing functionality, not experimental changes
   - You understand the code is the same as what users see

---

## Recommended Workflow

### For Active Development:
```
1. Make code changes in your session
2. Test on PREVIEW with environment overrides
3. Fix issues, iterate
4. Deploy to preview environment (official preview)
5. Test on preview URL
6. Deploy to production
7. Test on production URL
```

### For Quick Fixes (Current Situation):
```
1. Make fixes
2. Test on PRODUCTION URL directly
   - Uses production environment
   - Verifies real-world behavior
3. If works → You're done
4. If issues → Continue fixing
```

---

## Current Recommendation

Given that:
- ✅ Your fixes are ready
- ✅ Production .env is correctly configured
- ✅ You want to test end-to-end login flow
- ✅ Preview needs environment overrides (extra setup)

**I recommend testing on production URL:**
## `https://seamless-auth-1.emergent.host`

This will:
- Work immediately (no config changes)
- Verify the complete flow with correct OAuth redirects
- Confirm all session fixes are working
- Represent exactly what real users will experience

Once verified on production, if you need preview testing for future development, you can set up environment variable overrides in the dashboard.

---

## Setting Up Preview (If Needed Later)

If you decide to set up preview testing:

1. **Update Google OAuth Console** (one-time):
   - Add preview callback URL

2. **In Emergent Dashboard**:
   - Add environment variable overrides for preview
   - Set BACKEND_URL and FRONTEND_URL to preview domain

3. **Redeploy preview environment**

4. **Test on preview URL**

This keeps production untouched while enabling preview testing.

---

## Summary

**For Now:**
✅ Test on production: `https://seamless-auth-1.emergent.host`

**For Future:**
If you need preview testing, use environment variable overrides in the Emergent dashboard to set preview-specific URLs.

**Safety Note:**
Testing on production URL is safe because you're using the production environment, which already has your deployed code. Preview testing requires environment-specific configuration to avoid OAuth redirect mismatches.
