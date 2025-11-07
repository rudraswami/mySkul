Backend (FastAPI)

Requirements
- Python 3.10+
- MongoDB connection string in `MONGO_URL`

Environment Variables
- `MONGO_URL` (required)
- `DB_NAME` (default: `dhruv_ai`)
- `JWT_SECRET` (required)
- `BACKEND_URL` (e.g., `http://localhost:8001`)
- `FRONTEND_URL` (e.g., `http://localhost:3000`)
- `LOG_LEVEL` (default: `INFO`)
- `RATE_LIMIT_STORAGE_URI` (optional, e.g., `redis://localhost:6379/0`)

Install & Run
1. `pip install -r backend/requirements.txt`
2. `uvicorn backend.main:app --host 0.0.0.0 --port 8001`

Notes
- CSRF tokens are available from `GET /api/auth/csrf-token` (in response body and `X-CSRF-Token` header).
- Rate limiting uses in-memory storage by default; set `RATE_LIMIT_STORAGE_URI` (Redis) for production.
