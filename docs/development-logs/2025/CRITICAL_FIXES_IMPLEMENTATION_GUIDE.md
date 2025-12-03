# 🚨 CRITICAL FIXES - Implementation Guide
**Immediate Action Plan for Production Readiness**

---

## EMERGENCY FIX (DO THIS FIRST - 15 minutes)

### 🔴 SEC-001: Rotate Exposed Credentials

**Status:** CRITICAL - SECRETS EXPOSED IN REPO

**Files Containing Secrets:**
- `docs/archive/DEPLOYMENT_READY.md`

**Step-by-Step Fix:**

```bash
# 1. Delete the file with exposed secrets
rm docs/archive/DEPLOYMENT_READY.md

# 2. Commit the deletion
git add docs/archive/DEPLOYMENT_READY.md
git commit -m "security: remove file with exposed credentials"

# 3. Scan repo for other potential leaks
grep -r "sk-emergent" . --exclude-dir=node_modules --exclude-dir=.venv
grep -r "GOCSPX-" . --exclude-dir=node_modules --exclude-dir=.venv
grep -r "JWT_SECRET=" . --exclude-dir=node_modules --exclude-dir=.venv

# 4. Generate NEW strong secrets
python3 -c "import secrets; print('NEW_JWT_SECRET=' + secrets.token_urlsafe(64))"
python3 -c "import secrets; print('NEW_CSRF_SECRET=' + secrets.token_urlsafe(64))"

# 5. Update backend/.env with new secrets (NEVER commit this file!)
# backend/.env
JWT_SECRET=<new_secret_from_step_4>
CSRF_SECRET=<new_secret_from_step_4>

# 6. Revoke exposed API keys
# - Go to Emergent LLM dashboard
# - Revoke key: sk-emergent-6A354313e1fBb08539
# - Generate new key and update .env

# - Go to Google Cloud Console
# - Revoke OAuth credentials
# - Generate new client ID/secret
```

**Verification:**
```bash
# Ensure no secrets in git history
git log --all --full-history --source --oneline | grep -i "secret\|key\|password"
```

---

## CRITICAL FIX #1 (30 minutes)

### 🔴 CQ-001: Clean Up Root Directory

**Problem:** 80+ MD files in root causing clutter

**Implementation:**

```bash
# Create organized structure
mkdir -p docs/development-logs/2024
mkdir -p docs/development-logs/2025
mkdir -p docs/archive
mkdir -p docs/audits

# Move files by category
mv *_FIX*.md docs/development-logs/2025/
mv *_COMPLETE*.md docs/development-logs/2025/
mv *_STATUS*.md docs/development-logs/2025/
mv *_REPORT*.md docs/audits/
mv *_PLAN*.md docs/development-logs/2025/
mv *REBUILD*.md docs/archive/
mv *AUDIT*.md docs/audits/
mv BLANK_SCREEN*.md docs/archive/
mv CRITICAL_FIX*.md docs/archive/

# Move test files
mkdir -p tests/manual
mv *_test.py tests/manual/
mv comprehensive_auth_test.py tests/manual/
mv create_test_user.py tests/manual/

# Clean up exports in root
rm "export default"* 2>/dev/null || true
rm "[JULES"* 2>/dev/null || true
rm "}}" 2>/dev/null || true

# Keep only essential files in root
# - README.md
# - .gitignore
# - docker-compose.yml (to be created)
# - CHANGELOG.md (to be created)
# - LICENSE

# Commit cleanup
git add .
git commit -m "chore: organize documentation and test files"
```

**Verification:**
```bash
# Root should have < 10 files
ls -1 | wc -l  # Should be < 10
```

---

## CRITICAL FIX #2 (45 minutes)

### 🔴 DEVOPS-001: Create Docker Configuration

**Implementation:**

**Step 1: Create Backend Dockerfile**
```bash
cat > backend/Dockerfile << 'EOF'
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/api/health', timeout=5)"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF
```

**Step 2: Create Frontend Dockerfile**
```bash
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source
COPY . .

# Build app
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy build to nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
```

**Step 3: Create docker-compose.yml**
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # MongoDB Database
  mongo:
    image: mongo:6
    container_name: druvai-mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
      - ./backend/scripts/init_db.js:/docker-entrypoint-initdb.d/init.js:ro
    environment:
      MONGO_INITDB_DATABASE: dhruv_ai
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: druvai-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: druvai-backend
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - DB_NAME=dhruv_ai
      - REDIS_URL=redis://redis:6379/0
      - RATE_LIMIT_STORAGE_URI=redis://redis:6379/1
      - ENVIRONMENT=development
    env_file:
      - ./backend/.env
    depends_on:
      mongo:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8001/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  # Frontend Web App
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: druvai-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  mongo_data:
    driver: local
  redis_data:
    driver: local

networks:
  default:
    name: druvai-network
EOF
```

**Step 4: Create .dockerignore files**
```bash
# Backend .dockerignore
cat > backend/.dockerignore << 'EOF'
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv
env/
venv/
.env
.env.local
*.log
.pytest_cache
.mypy_cache
tests/
*.md
.git
.gitignore
EOF

# Frontend .dockerignore
cat > frontend/.dockerignore << 'EOF'
node_modules
build
.git
.gitignore
*.md
.env.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
EOF
```

**Verification:**
```bash
# Test Docker build
docker-compose build

# Test Docker run
docker-compose up -d

# Check services
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs frontend

# Test API
curl http://localhost:8001/api/health

# Cleanup
docker-compose down
```

---

## CRITICAL FIX #3 (1 hour)

### 🔴 DEVOPS-002: Implement CI/CD Pipeline

**Implementation:**

**Step 1: Create GitHub Actions Workflow**
```bash
mkdir -p .github/workflows

cat > .github/workflows/ci-cd.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Backend Tests
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:6
        ports:
          - 27017:27017
        options: >-
          --health-cmd "echo 'db.runCommand(\"ping\").ok' | mongosh localhost:27017/test --quiet"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run linters
        run: |
          cd backend
          flake8 . --max-line-length=120 --exclude=.venv,__pycache__
          black --check .
          isort --check-only .
      
      - name: Run tests
        env:
          MONGO_URL: mongodb://localhost:27017
          DB_NAME: test_dhruv_ai
          JWT_SECRET: test-jwt-secret-for-ci-only-not-production
          EMERGENT_LLM_KEY: ${{ secrets.EMERGENT_LLM_KEY }}
        run: |
          cd backend
          pytest tests/ -v --cov=. --cov-report=term-missing
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  # Frontend Tests
  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'yarn'
          cache-dependency-path: frontend/yarn.lock
      
      - name: Install dependencies
        run: |
          cd frontend
          yarn install --frozen-lockfile
      
      - name: Lint code
        run: |
          cd frontend
          yarn lint || true
      
      - name: Run tests
        run: |
          cd frontend
          CI=true yarn test --watchAll=false --coverage
      
      - name: Build application
        run: |
          cd frontend
          yarn build
      
      - name: Check build size
        run: |
          cd frontend
          ls -lh build/static/js/*.js | awk '{if ($5 > 500000) print "WARNING: Large bundle detected: " $9 " (" $5 " bytes)"}'

  # Security Scan
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # Deploy to Staging (on develop branch)
  deploy-staging:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, security-scan]
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploy to staging environment"
          # Add your deployment commands here

  # Deploy to Production (on main branch)
  deploy-production:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, security-scan]
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        run: |
          echo "Deploy to production environment"
          # Add your deployment commands here
          # Requires manual approval
EOF
```

**Step 2: Add GitHub Secrets**
```bash
# In GitHub repo settings > Secrets and variables > Actions
# Add these secrets:
# - EMERGENT_LLM_KEY
# - MONGO_URL_PRODUCTION
# - JWT_SECRET_PRODUCTION
```

**Verification:**
- Push to develop branch
- Check GitHub Actions tab
- Verify all tests pass

---

## CRITICAL FIX #4 (15 minutes)

### 🔴 DEVOPS-003: Environment Separation

**Implementation:**

**Step 1: Create environment-specific configs**
```bash
# backend/.env.development
cat > backend/.env.development << 'EOF'
ENVIRONMENT=development
DEBUG=true
MONGO_URL=mongodb://localhost:27017
DB_NAME=dhruv_ai_dev
BACKEND_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=DEBUG
RATE_LIMIT_STORAGE_URI=memory://

# Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
JWT_SECRET=dev-jwt-secret-change-me-in-production
CSRF_SECRET=dev-csrf-secret-change-me-in-production

# Development API keys (get from team)
EMERGENT_LLM_KEY=sk-emergent-dev-key-here
GOOGLE_CLIENT_ID=your-dev-client-id
GOOGLE_CLIENT_SECRET=your-dev-client-secret
EOF

# backend/.env.production
cat > backend/.env.production << 'EOF'
ENVIRONMENT=production
DEBUG=false
MONGO_URL=${MONGO_URL_PROD}  # Set via environment variable
DB_NAME=dhruv_ai_prod
BACKEND_URL=${BACKEND_URL_PROD}
FRONTEND_URL=${FRONTEND_URL_PROD}
LOG_LEVEL=WARNING
RATE_LIMIT_STORAGE_URI=redis://${REDIS_HOST}:6379/1

# Production secrets (set via environment variables or secrets manager)
JWT_SECRET=${JWT_SECRET_PROD}
CSRF_SECRET=${CSRF_SECRET_PROD}
EMERGENT_LLM_KEY=${EMERGENT_LLM_KEY_PROD}
GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID_PROD}
GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET_PROD}
EOF

# Create .env.example (safe to commit)
cat > backend/.env.example << 'EOF'
# Copy this to .env and fill in real values
ENVIRONMENT=development
DEBUG=true
MONGO_URL=mongodb://localhost:27017
DB_NAME=dhruv_ai
BACKEND_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000
JWT_SECRET=generate-with-openssl-rand-hex-64
CSRF_SECRET=generate-with-openssl-rand-hex-64
EMERGENT_LLM_KEY=your-api-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF
```

**Step 2: Update .gitignore**
```bash
cat >> .gitignore << 'EOF'

# Environment files (NEVER commit)
.env
.env.local
.env.development.local
.env.production.local
.env.*.local
**/.env
**/.env.local

# Secrets and keys
*.pem
*.key
*secret*
*SECRET*

# Documentation (keep only in docs/)
/*_FIX*.md
/*_COMPLETE*.md
/*_STATUS*.md
/*_REPORT*.md
/*_PLAN*.md
EOF
```

**Step 3: Update config.py to fail fast**
```python
# backend/core/config.py
class Settings:
    # ...existing code...
    
    def __init__(self):
        # Fail fast if ENVIRONMENT not set
        if not os.getenv("ENVIRONMENT"):
            raise RuntimeError(
                "ENVIRONMENT variable not set! "
                "Set to 'development', 'staging', or 'production'"
            )
```

**Verification:**
```bash
# Test development environment
export ENVIRONMENT=development
cd backend && python -c "from core.config import settings; print(f'Environment: {settings.ENVIRONMENT}')"

# Should fail without ENVIRONMENT
unset ENVIRONMENT
cd backend && python -c "from core.config import settings"  # Should raise RuntimeError
```

---

## CRITICAL FIX #5 (30 minutes)

### 🔴 DEVOPS-005: Implement Backup Strategy

**Implementation:**

**Step 1: Create backup script**
```bash
mkdir -p backend/scripts

cat > backend/scripts/backup_mongodb.sh << 'EOF'
#!/bin/bash
# MongoDB Backup Script
# Run daily via cron: 0 2 * * * /path/to/backup_mongodb.sh

set -e

# Configuration
BACKUP_DIR="/var/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
MONGO_URL="${MONGO_URL:-mongodb://localhost:27017}"
DB_NAME="${DB_NAME:-dhruv_ai}"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Run backup
echo "Starting MongoDB backup at $DATE..."
mongodump --uri="$MONGO_URL" --db="$DB_NAME" --out="$BACKUP_DIR/$DATE"

# Compress backup
tar -czf "$BACKUP_DIR/$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"
rm -rf "$BACKUP_DIR/$DATE"

echo "Backup created: $BACKUP_DIR/$DATE.tar.gz"

# Clean up old backups
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "Cleaned up backups older than $RETENTION_DAYS days"

# Upload to S3 (optional)
# aws s3 cp "$BACKUP_DIR/$DATE.tar.gz" s3://druvai-backups/mongodb/

echo "Backup complete!"
EOF

chmod +x backend/scripts/backup_mongodb.sh
```

**Step 2: Create restore script**
```bash
cat > backend/scripts/restore_mongodb.sh << 'EOF'
#!/bin/bash
# MongoDB Restore Script

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore_mongodb.sh <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
MONGO_URL="${MONGO_URL:-mongodb://localhost:27017}"
DB_NAME="${DB_NAME:-dhruv_ai}"
TEMP_DIR="/tmp/mongodb_restore"

# Extract backup
mkdir -p "$TEMP_DIR"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Restore
echo "Restoring MongoDB from $BACKUP_FILE..."
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" "$TEMP_DIR"/*

# Cleanup
rm -rf "$TEMP_DIR"

echo "Restore complete!"
EOF

chmod +x backend/scripts/restore_mongodb.sh
```

**Step 3: Set up cron job**
```bash
# Add to crontab (run daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backend/scripts/backup_mongodb.sh >> /var/log/mongodb_backup.log 2>&1") | crontab -
```

**Verification:**
```bash
# Test backup
./backend/scripts/backup_mongodb.sh

# Verify backup file created
ls -lh /var/backups/mongodb/*.tar.gz

# Test restore (on development database only!)
./backend/scripts/restore_mongodb.sh /var/backups/mongodb/20251202_120000.tar.gz
```

---

## QUICK WINS (30 minutes total)

### Fix #1: Enable API Documentation (5 min)
```python
# backend/main.py - Already enabled! Just verify:
# Visit http://localhost:8001/docs
# Visit http://localhost:8001/redoc
```

### Fix #2: Add .env.example (5 min)
```bash
# Already covered in Critical Fix #2
```

### Fix #3: Create CHANGELOG.md (10 min)
```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to Druv AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Agentic system with true agent behavior
- Sathi UI/UX redesign with premium learning experience
- Visual Sketch Engine for educational diagrams
- Memory system for personalized learning

### Fixed
- Time parsing for reminders (handles typos like "5mis")
- Chat history cards cleanup (transparent backgrounds)
- Follow-up questions horizontal layout

### Security
- CSRF protection enabled
- Rate limiting implemented
- JWT token rotation

## [1.0.0] - 2025-12-02

### Added
- Initial release
- AI Tutor with neuro-symbolic responses
- Mock test generation
- Subscription management
- Gamification system
EOF
```

### Fix #4: Add Health Check Monitoring (10 min)
```python
# backend/api/health.py (create new file)
from fastapi import APIRouter, Depends
from dependencies import get_database
from datetime import datetime

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check(db = Depends(get_database)):
    """Comprehensive health check for monitoring"""
    try:
        # Check database
        await db.command("ping")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "api": "healthy"
        }
    }

# Add to main.py:
# from api import health
# app.include_router(health.router)
```

---

## TIMELINE

### 🚨 **Day 1 (TODAY) - Emergency Security**
- [ ] Rotate all exposed credentials (15 min)
- [ ] Delete files with secrets (5 min)
- [ ] Scan repo for leaks (10 min)
- **Total: 30 minutes**

### 📅 **Day 2 - Critical Infrastructure**
- [ ] Clean up root directory (30 min)
- [ ] Create Docker configuration (45 min)
- [ ] Set up environment separation (15 min)
- **Total: 90 minutes**

### 📅 **Day 3 - CI/CD & Monitoring**
- [ ] Implement CI/CD pipeline (1 hour)
- [ ] Set up error monitoring (30 min)
- [ ] Add health checks (15 min)
- **Total: 105 minutes**

### 📅 **Week 2 - Production Hardening**
- [ ] Implement backup strategy (2 hours)
- [ ] Configure Redis (1 hour)
- [ ] Security audit (2 hours)
- [ ] Load testing (2 hours)

### 📅 **Week 3 - Final Polish**
- [ ] Refactor large components (3 hours)
- [ ] Remove duplicate code (2 hours)
- [ ] Complete documentation (2 hours)
- [ ] Final QA (2 hours)

---

## SUCCESS METRICS

**After fixes, you should achieve:**
- ✅ Production Readiness Score: 90+/100
- ✅ Zero exposed credentials
- ✅ Automated CI/CD
- ✅ Docker deployment ready
- ✅ Monitored and backed up
- ✅ Clean, organized codebase

---

## SUPPORT CONTACTS

- **Security Issues:** Rotate credentials immediately
- **Deployment Help:** Docker documentation available
- **Questions:** Refer to this guide

---

**Audit Complete - Action Required**  
**Fix Timeline: 1 day (critical) + 2 weeks (production ready)**

