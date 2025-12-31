# 🚀 DRUV AI - PRODUCTION ENVIRONMENT VARIABLES GUIDE

## Complete `.env` File for Production Deployment

Copy this to `backend/.env` and fill in your actual values. **DO NOT commit `.env` to git!**

---

## 📋 QUICK REFERENCE: Required vs Optional

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `ENVIRONMENT` | ✅ | `production` | Must be `production` |
| `DEBUG` | ✅ | `false` | Must be `false` |
| `MONGO_URL` | ✅ **CRITICAL** | None | MongoDB Atlas connection string |
| `JWT_SECRET` | ✅ **CRITICAL** | None | Min 32 chars (64 hex recommended) |
| `EMERGENT_LLM_KEY` | ✅ **CRITICAL** | None | Primary LLM provider |
| `BACKEND_URL` | ✅ | None | Your deployed backend URL |
| `FRONTEND_URL` | ✅ | None | Your deployed frontend URL |
| `OPENAI_API_KEY` | ⚠️ Recommended | None | For semantic memory embeddings |
| `GOOGLE_CLIENT_ID` | ⚠️ For OAuth | None | Google OAuth credentials |
| `GOOGLE_CLIENT_SECRET` | ⚠️ For OAuth | None | Google OAuth credentials |
| `RAZORPAY_KEY_ID` | ⚠️ For Payments | None | Razorpay API keys |
| `RAZORPAY_KEY_SECRET` | ⚠️ For Payments | None | Razorpay API keys |
| `CSRF_SECRET` | ⚠️ Recommended | Auto-generated | Set explicitly for consistency |
| `CORS_ORIGINS` | ⚠️ Recommended | Auto from FRONTEND_URL | Explicitly set for clarity |

---

## 🔐 COMPLETE `.env` FILE TEMPLATE

```env
# =============================================================================
# APPLICATION SETTINGS (REQUIRED)
# =============================================================================
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# =============================================================================
# SERVER SETTINGS (REQUIRED)
# =============================================================================
HOST=0.0.0.0
PORT=8001
BACKEND_URL=https://your-backend-domain.com
FRONTEND_URL=https://your-frontend-domain.com

# =============================================================================
# DATABASE SETTINGS (CRITICAL - REQUIRED)
# =============================================================================
# Format: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
MONGO_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/dhruv_ai?retryWrites=true&w=majority
DB_NAME=dhruv_ai

# =============================================================================
# SECURITY SETTINGS (CRITICAL - REQUIRED)
# =============================================================================
# Generate with: openssl rand -hex 32
JWT_SECRET=your-64-character-hex-secret-generate-with-openssl-rand-hex-32
CSRF_SECRET=your-64-character-hex-secret-generate-with-openssl-rand-hex-32
SESSION_COOKIE_SAMESITE=none
SESSION_EXPIRY_DAYS=7
JWT_EXPIRATION_HOURS=168

# =============================================================================
# CORS SETTINGS (REQUIRED)
# =============================================================================
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com,https://your-app.vercel.app
CORS_ALLOW_ALL_SUBDOMAINS=false

# =============================================================================
# AI / LLM SETTINGS (CRITICAL - REQUIRED)
# =============================================================================
EMERGENT_LLM_KEY=your-emergent-integrations-api-key
OPENAI_API_KEY=sk-your-openai-api-key-here
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000

# =============================================================================
# GEMINI SETTINGS (OPTIONAL)
# =============================================================================
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_PRO_MODEL=gemini-1.5-pro-latest
GEMINI_VISUAL_MODEL=gemini-2.0-flash-001
USE_GEMINI_PRIMARY=false

# =============================================================================
# OAUTH SETTINGS (REQUIRED for Google Login)
# =============================================================================
GOOGLE_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret

# =============================================================================
# PAYMENT SETTINGS (REQUIRED for subscriptions)
# =============================================================================
RAZORPAY_KEY_ID=rzp_live_your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# =============================================================================
# REDIS SETTINGS (OPTIONAL - Recommended for production)
# =============================================================================
REDIS_URL=redis://your-redis-host:6379/0
RATE_LIMIT_STORAGE_URI=redis://your-redis-host:6379/1
```

---

## 📝 DETAILED VARIABLE EXPLANATIONS

### 1. **ENVIRONMENT** (Required)
```env
ENVIRONMENT=production
```
- **Purpose**: Sets application environment
- **Options**: `production`, `development`, `staging`
- **Default**: `production`
- **Validation**: Must be `production` for production deployment

### 2. **DEBUG** (Required)
```env
DEBUG=false
```
- **Purpose**: Enables/disables debug mode
- **Options**: `true`, `false`
- **Default**: `false`
- **Production**: **MUST be `false`** (security)

### 3. **MONGO_URL** (CRITICAL - Required)
```env
MONGO_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/dhruv_ai?retryWrites=true&w=majority
```
- **Purpose**: MongoDB connection string
- **Format**: `mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority`
- **Where to get**: 
  1. Go to [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas)
  2. Create free cluster
  3. Database Access → Create user
  4. Network Access → Add IP `0.0.0.0/0` (allow all for Railway)
  5. Clusters → Connect → Connect your application → Copy connection string
- **Replace**: `<username>`, `<password>`, `<cluster>` with your values
- **Validation**: Must be valid MongoDB connection string

### 4. **DB_NAME** (Required)
```env
DB_NAME=dhruv_ai
```
- **Purpose**: Database name
- **Default**: `dhruv_ai`
- **Note**: Should match database name in `MONGO_URL`

### 5. **JWT_SECRET** (CRITICAL - Required)
```env
JWT_SECRET=your-64-character-hex-secret-generate-with-openssl-rand-hex-32
```
- **Purpose**: Secret key for JWT token signing
- **Generate**: `openssl rand -hex 32` (produces 64 hex characters)
- **Minimum**: 32 characters (64 hex = 32 bytes)
- **Security**: **NEVER share or commit this!**
- **Validation**: Code checks `len(JWT_SECRET) >= 32`

### 6. **CSRF_SECRET** (Recommended)
```env
CSRF_SECRET=your-64-character-hex-secret-generate-with-openssl-rand-hex-32
```
- **Purpose**: Secret key for CSRF protection
- **Generate**: `openssl rand -hex 32`
- **Default**: Auto-generated if not provided (not recommended for production)
- **Note**: Set explicitly for production consistency

### 7. **BACKEND_URL** (Required)
```env
BACKEND_URL=https://your-backend-domain.com
```
- **Purpose**: Your deployed backend URL
- **Examples**: 
  - Railway: `https://your-app.railway.app`
  - Render: `https://your-app.onrender.com`
  - Custom domain: `https://api.druvai.com`
- **Note**: Must be HTTPS in production
- **Used for**: CORS, session cookies, API calls from frontend

### 8. **FRONTEND_URL** (Required)
```env
FRONTEND_URL=https://your-frontend-domain.com
```
- **Purpose**: Your deployed frontend URL
- **Examples**:
  - Vercel: `https://your-app.vercel.app`
  - Custom domain: `https://druvai.com`
- **Note**: Automatically added to `CORS_ORIGINS`
- **Used for**: CORS configuration, redirects

### 9. **CORS_ORIGINS** (Recommended)
```env
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com,https://your-app.vercel.app
```
- **Purpose**: Comma-separated list of allowed origins
- **Note**: `FRONTEND_URL` is automatically added, but set explicitly for clarity
- **Format**: Comma-separated, no spaces after commas

### 10. **SESSION_COOKIE_SAMESITE** (Required)
```env
SESSION_COOKIE_SAMESITE=none
```
- **Purpose**: Cookie SameSite attribute
- **Options**: `strict`, `lax`, `none`
- **Production**: Use `none` for cross-origin (frontend on different domain)
- **Note**: If `none`, cookies require HTTPS

### 11. **EMERGENT_LLM_KEY** (CRITICAL - Required)
```env
EMERGENT_LLM_KEY=your-emergent-integrations-api-key
```
- **Purpose**: Primary LLM provider API key
- **Where to get**: [emergent.host](https://emergent.host) or your Emergent dashboard
- **Validation**: Code checks this is not empty
- **Used for**: All AI responses, reasoning, agent system

### 12. **OPENAI_API_KEY** (Recommended)
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```
- **Purpose**: OpenAI API key for embeddings
- **Where to get**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Used for**: Semantic memory embeddings (`text-embedding-3-small`)
- **Note**: Optional but recommended for memory features

### 13. **LLM_MODEL** (Optional)
```env
LLM_MODEL=gpt-4.1-mini
```
- **Purpose**: Default LLM model for reasoning
- **Default**: `gpt-4.1-mini`
- **Options**: Any model supported by Emergent Integrations

### 14. **GOOGLE_CLIENT_ID** (Required for OAuth)
```env
GOOGLE_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
```
- **Purpose**: Google OAuth client ID
- **Where to get**: 
  1. [console.cloud.google.com](https://console.cloud.google.com)
  2. APIs & Services → Credentials
  3. Create OAuth 2.0 Client ID → Web application
  4. Authorized redirect URIs: `https://your-backend-domain.com/api/auth/google/callback`

### 15. **GOOGLE_CLIENT_SECRET** (Required for OAuth)
```env
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```
- **Purpose**: Google OAuth client secret
- **Where to get**: Same as `GOOGLE_CLIENT_ID` (shown after creation)

### 16. **RAZORPAY_KEY_ID** (Required for Payments)
```env
RAZORPAY_KEY_ID=rzp_live_your-razorpay-key-id
```
- **Purpose**: Razorpay API key ID
- **Where to get**: [dashboard.razorpay.com](https://dashboard.razorpay.com) → Settings → API Keys
- **Note**: Use `rzp_live_` prefix for production (not `rzp_test_`)

### 17. **RAZORPAY_KEY_SECRET** (Required for Payments)
```env
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
```
- **Purpose**: Razorpay API key secret
- **Where to get**: Same as `RAZORPAY_KEY_ID`

### 18. **REDIS_URL** (Optional - Recommended)
```env
REDIS_URL=redis://your-redis-host:6379/0
```
- **Purpose**: Redis connection for caching
- **Format**: `redis://<host>:<port>/<db>`
- **Default**: Uses in-memory storage if not provided (not recommended for production)
- **Where to get**: Railway/Render Redis addon, or external Redis service

---

## 🔧 GENERATING SECRETS

### Generate JWT_SECRET and CSRF_SECRET:
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))

# Or use online generator:
# https://www.random.org/strings/?num=1&len=64&digits=on&upperalpha=on&loweralpha=on&unique=on&format=html&rnd=new
```

---

## ✅ VALIDATION CHECKLIST

After creating your `.env` file, the code will validate:

- ✅ `JWT_SECRET` exists and is at least 32 characters
- ✅ `MONGO_URL` exists and is not empty
- ✅ `EMERGENT_LLM_KEY` exists and is not empty
- ⚠️ `CSRF_SECRET` warning if not set (auto-generated)
- ⚠️ `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` warning if not set

---

## 🚀 NEXT STEPS

1. Copy this template to `backend/.env`
2. Fill in all **CRITICAL** variables (marked with ✅)
3. Fill in **Recommended** variables (marked with ⚠️)
4. Deploy backend
5. Test health endpoint: `curl https://your-backend-domain.com/api/health`
6. Initialize database indexes: `python -m scripts.init_indexes`

---

## 📞 NEED HELP?

If you see validation errors on startup, check:
1. All **CRITICAL** variables are set
2. `JWT_SECRET` is at least 32 characters
3. `MONGO_URL` is valid MongoDB connection string
4. `EMERGENT_LLM_KEY` is not empty
5. URLs are HTTPS (not HTTP) in production

