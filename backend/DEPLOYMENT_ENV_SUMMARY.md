# 🚀 BACKEND DEPLOYMENT - ENVIRONMENT VARIABLES SUMMARY

## ✅ CRITICAL VARIABLES (MUST SET)

```env
# Application
ENVIRONMENT=production
DEBUG=false

# Database
MONGO_URL=mongodb+srv://<user>:<password>@cluster.mongodb.net/dhruv_ai
DB_NAME=dhruv_ai

# Security (Generate with: openssl rand -hex 32)
JWT_SECRET=<64-char-hex-string>
CSRF_SECRET=<64-char-hex-string>

# URLs (Update after deployment)
BACKEND_URL=https://your-backend.railway.app
FRONTEND_URL=https://your-frontend.vercel.app

# AI (CRITICAL)
EMERGENT_LLM_KEY=<your-emergent-key>
OPENAI_API_KEY=<your-openai-key>

# OAuth (For Google Login)
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>

# Payments (For Subscriptions)
RAZORPAY_KEY_ID=<your-razorpay-key-id>
RAZORPAY_KEY_SECRET=<your-razorpay-secret>

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app,https://druvai.com
SESSION_COOKIE_SAMESITE=none
```

---

## 📋 WHERE TO GET EACH VALUE

### 1. **MONGO_URL** (MongoDB Atlas)
- Go to: https://cloud.mongodb.com
- Steps:
  1. Create free cluster
  2. Database Access → Create user (save password!)
  3. Network Access → Add IP `0.0.0.0/0`
  4. Clusters → Connect → "Connect your application"
  5. Copy connection string
  6. Replace `<password>` with your password
  7. Replace `<dbname>` with `dhruv_ai`

**Example:**
```
mongodb+srv://admin:MyPassword123@cluster0.abc123.mongodb.net/dhruv_ai?retryWrites=true&w=majority
```

### 2. **JWT_SECRET** & **CSRF_SECRET**
Generate secure secrets:
```bash
# Linux/Mac:
openssl rand -hex 32

# Windows PowerShell:
-([System.Web.Security.Membership]::GeneratePassword(64, 0))

# Or use online: https://www.random.org/strings/?num=1&len=64
```

**Example output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### 3. **EMERGENT_LLM_KEY**
- Go to: https://emergent.host (or your Emergent dashboard)
- Get your API key from dashboard
- **This is CRITICAL** - app won't work without it

### 4. **OPENAI_API_KEY**
- Go to: https://platform.openai.com/api-keys
- Create new secret key
- Copy key (starts with `sk-`)

### 5. **GOOGLE_CLIENT_ID** & **GOOGLE_CLIENT_SECRET**
- Go to: https://console.cloud.google.com
- Steps:
  1. Create new project (or select existing)
  2. APIs & Services → Credentials
  3. Create Credentials → OAuth 2.0 Client ID
  4. Application type: Web application
  5. Authorized redirect URIs: `https://your-backend-domain.com/api/auth/google/callback`
  6. Copy Client ID and Client Secret

### 6. **RAZORPAY_KEY_ID** & **RAZORPAY_KEY_SECRET**
- Go to: https://dashboard.razorpay.com
- Steps:
  1. Settings → API Keys
  2. Generate Live Keys (not test keys!)
  3. Copy Key ID (starts with `rzp_live_`)
  4. Copy Key Secret

### 7. **BACKEND_URL** & **FRONTEND_URL**
- **BACKEND_URL**: Your deployed backend URL
  - Railway: `https://your-app.railway.app`
  - Render: `https://your-app.onrender.com`
  - Custom: `https://api.druvai.com`
  
- **FRONTEND_URL**: Your deployed frontend URL
  - Vercel: `https://your-app.vercel.app`
  - Custom: `https://druvai.com`

**Note:** Update these AFTER deployment with actual URLs!

### 8. **CORS_ORIGINS**
Comma-separated list of allowed origins:
```
CORS_ORIGINS=https://your-app.vercel.app,https://druvai.com,https://www.druvai.com
```

---

## 🎯 MINIMAL PRODUCTION `.env` FILE

Here's the absolute minimum to get started:

```env
ENVIRONMENT=production
DEBUG=false
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/dhruv_ai
DB_NAME=dhruv_ai
JWT_SECRET=<generate-64-char-hex>
CSRF_SECRET=<generate-64-char-hex>
BACKEND_URL=https://your-backend.railway.app
FRONTEND_URL=https://your-frontend.vercel.app
EMERGENT_LLM_KEY=<your-key>
OPENAI_API_KEY=<your-key>
GOOGLE_CLIENT_ID=<your-id>
GOOGLE_CLIENT_SECRET=<your-secret>
RAZORPAY_KEY_ID=<your-key-id>
RAZORPAY_KEY_SECRET=<your-secret>
CORS_ORIGINS=https://your-frontend.vercel.app
SESSION_COOKIE_SAMESITE=none
```

---

## ⚠️ OPTIONAL BUT RECOMMENDED

```env
# Redis (for caching - improves performance)
REDIS_URL=redis://your-redis-host:6379/0
RATE_LIMIT_STORAGE_URI=redis://your-redis-host:6379/1

# Logging
LOG_LEVEL=WARNING

# Gemini (for advanced features)
GEMINI_API_KEY=<optional>
```

---

## 🔍 VALIDATION

The code validates on startup:
- ✅ `JWT_SECRET` exists and ≥ 32 chars
- ✅ `MONGO_URL` exists
- ✅ `EMERGENT_LLM_KEY` exists
- ⚠️ Warns if `CSRF_SECRET` not set (auto-generates)
- ⚠️ Warns if OAuth not configured

---

## 📝 QUICK COPY-PASTE TEMPLATE

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8001
BACKEND_URL=https://your-backend.railway.app
FRONTEND_URL=https://your-frontend.vercel.app
MONGO_URL=mongodb+srv://<user>:<password>@cluster.mongodb.net/dhruv_ai?retryWrites=true&w=majority
DB_NAME=dhruv_ai
JWT_SECRET=<generate-with-openssl-rand-hex-32>
CSRF_SECRET=<generate-with-openssl-rand-hex-32>
SESSION_COOKIE_SAMESITE=none
SESSION_EXPIRY_DAYS=7
JWT_EXPIRATION_HOURS=168
CORS_ORIGINS=https://your-frontend.vercel.app
CORS_ALLOW_ALL_SUBDOMAINS=false
EMERGENT_LLM_KEY=<your-emergent-key>
OPENAI_API_KEY=<your-openai-key>
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
RAZORPAY_KEY_ID=<your-razorpay-key-id>
RAZORPAY_KEY_SECRET=<your-razorpay-secret>
```

---

## ✅ NEXT STEPS

1. ✅ Create `backend/.env` file
2. ✅ Fill in all values above
3. ✅ Deploy to Railway/Render
4. ✅ Test: `curl https://your-backend/api/health`
5. ✅ Initialize indexes: `python -m scripts.init_indexes`

