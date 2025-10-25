# 8. Deployment

## 8.1 Frontend Deployment (Vercel)

**Vercel Project Name:** `innovation-web`
**Connected Railway Backend:** `My-board-of-ideators`

**`vercel.json`:**
```json
{
  "buildCommand": "npm run build",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_BACKEND_URL": "@railway-backend-url",
    "BLOB_READ_WRITE_TOKEN": "@blob-read-write-token"
  }
}
```

**Environment Variables (Vercel Dashboard):**
- `NEXT_PUBLIC_BACKEND_URL` - Railway backend URL (e.g., `https://innovation-backend.railway.app`)
- `BLOB_READ_WRITE_TOKEN` - Vercel Blob token (auto-generated)
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk publishable key (for frontend authentication)
- `CLERK_SECRET_KEY` - Clerk secret key (for webhook verification)

**Note:** No `maxDuration` override needed - API routes now proxy to Railway (fast response)

---

## 8.2 Backend Deployment (Railway)

**Railway Project Name:** `My-board-of-ideators`
**Connected Vercel Frontend:** `innovation-web`

### Dockerfile

**`/backend/Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway Configuration

**`/backend/railway.json`:**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ALWAYS"
  }
}
```

**Environment Variables (Railway Dashboard):**
- `OPENROUTER_API_KEY` - OpenRouter API key for LLM calls
- `OPENROUTER_BASE_URL` - `https://openrouter.ai/api/v1`
- `LLM_MODEL` - `anthropic/claude-sonnet-4.5`
- `VERCEL_BLOB_READ_WRITE_TOKEN` - Token for downloading PDFs from Vercel Blob
- `CLERK_SECRET_KEY` - Clerk secret key for JWT validation (Story 8.1)
- `FRONTEND_WEBHOOK_URL` - Vercel frontend URL for completion webhook
- `WEBHOOK_SECRET` - Shared secret for webhook authentication
- `PORT` - Railway auto-sets this (default: 8000)

---

## 8.3 Python Dependencies (Backend)

**`/backend/requirements.txt`:**
```
fastapi==0.115.0
uvicorn==0.32.0
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.1
openai>=1.0.0
pypdf>=3.17.0
pyyaml>=6.0
jinja2>=3.1.3
python-dotenv>=1.0.0
pydantic>=2.5.0
clerk-backend-api>=1.0.0  # Story 8.1: JWT validation
requests>=2.31.0          # Story 8.1: Webhook calls to frontend
```

---

## 8.4 Node.js Dependencies (Frontend)

**`/innovation-web/package.json`:**
```json
{
  "name": "innovation-web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@vercel/blob": "^0.23.0",
    "next": "15.1.8",
    "pdf-parse": "^1.1.1",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-dropzone": "^14.3.0",
    "react-markdown": "^9.0.0",
    "yaml": "^2.3.4"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.0.0"
  }
}
```

---

## 8.5 Deployment Workflow

### Local Development

**Terminal 1 - Backend (Railway Docker):**
```bash
cd backend
docker build -t innovation-backend .
docker run -p 8000:8000 --env-file .env innovation-backend
```

**Terminal 2 - Frontend (Next.js):**
```bash
cd innovation-web
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 npm run dev
```

### Production Deployment

**Step 1: Deploy Backend to Railway**
```bash
# From repository root
cd backend
railway login
railway init  # Create new project: My-board-of-ideators
railway up    # Deploy
```

**Step 2: Configure Railway Environment Variables**
- Project name: `My-board-of-ideators`
- Set `OPENROUTER_API_KEY`, `LLM_MODEL`, `VERCEL_BLOB_READ_WRITE_TOKEN`
- Copy Railway public URL (e.g., `https://innovation-backend.railway.app`)

**Step 3: Deploy Frontend to Vercel**
```bash
cd innovation-web
vercel deploy --prod
```

**Step 4: Configure Vercel Environment Variables**
- Project name: `innovation-web`
- Set `NEXT_PUBLIC_BACKEND_URL` to Railway public URL (from My-board-of-ideators)
- Set `BLOB_READ_WRITE_TOKEN`
- Set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (Story 8.1)
- Set `CLERK_SECRET_KEY` (Story 8.1)

---

## 8.6 Story 8.1 Deployment: Direct Railway Backend Call

**Summary:** Story 8.1 changes the document analysis flow from Next.js API route → direct Railway backend call to bypass Vercel's 10-second timeout.

### Deployment Strategy (Gradual Rollout)

**Phase 1: Railway Backend Update (Week 1)**
```bash
# Add Clerk JWT validation to Railway backend
cd backend
# Update requirements.txt to include clerk-backend-api
railway up

# Configure Railway environment variables:
# - CLERK_SECRET_KEY
# - FRONTEND_WEBHOOK_URL
# - WEBHOOK_SECRET
```

**Phase 2: Vercel Frontend Update with Feature Flag (Week 1)**
```bash
cd innovation-web
vercel deploy --prod

# Configure Vercel environment variables:
# - NEXT_PUBLIC_BACKEND_URL (already set)
# - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
# - CLERK_SECRET_KEY
# - ENABLE_DIRECT_RAILWAY_CALL=false (initially disabled)
```

**Phase 3: Gradual Rollout (Week 2)**
1. Enable for 10% of users: `ENABLE_DIRECT_RAILWAY_CALL=true` for test accounts
2. Monitor error rates for 24 hours (target: <5%)
3. If successful, increase to 25% → 50% → 100%
4. If errors >10%, rollback to `ENABLE_DIRECT_RAILWAY_CALL=false`

**Phase 4: Deprecate Old Endpoint (Week 3)**
```bash
# After 100% rollout success:
# 1. Mark /api/analyze-document as deprecated (return 410 Gone)
# 2. Log usage for 30 days
# 3. Delete endpoint after deprecation period
```

### Rollback Procedure

**If Railway backend Clerk auth fails (>10% error rate):**

```bash
# Step 1: Disable feature flag immediately
vercel env set ENABLE_DIRECT_RAILWAY_CALL false
vercel deploy --prod

# Step 2: Verify /api/analyze-document still functional
curl -X POST https://innovation-web-rho.vercel.app/api/analyze-document \
  -H "Content-Type: application/json" \
  -d '{"blob_url": "..."}'

# Step 3: Monitor for 24 hours
# Step 4: Investigate Clerk auth issue
# Step 5: Retry rollout after fix
```

### Monitoring & Alerting

**Critical Metrics:**
- Clerk authentication failure rate (target: <5%)
- Railway backend response time (target: <2s for initial response)
- Webhook delivery success rate (target: >95%)
- Document analysis completion rate (target: >90%)

**Alerts:**
- ⚠️ Warning: Clerk auth failures >5% in 5 minutes
- 🔴 Critical: Clerk auth failures >10% in 5 minutes → Auto-rollback
- 🔴 Critical: Railway backend unavailable >3 minutes

### CORS Configuration (Railway Backend)

**Required for direct frontend calls:**
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://innovation-web-rho.vercel.app",  # Production
        "https://*.vercel.app",                   # Preview deployments
        "http://localhost:3000"                   # Local development
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Testing Checklist

**Pre-Deployment:**
- [ ] Railway backend validates Clerk JWT successfully (curl test)
- [ ] Frontend can obtain Clerk token with `useAuth()`
- [ ] CSP allows `https://*.railway.app` connections
- [ ] Webhook endpoint receives completion notifications
- [ ] Polling endpoint still returns run status

**Post-Deployment:**
- [ ] Upload document → analyze → verify no 504 timeout
- [ ] Test authentication failure scenario (expired token)
- [ ] Test network failure scenario (Railway backend down)
- [ ] Verify polling and webhook still work
- [ ] Monitor Railway logs for auth validation success

---

## 8.7 Architecture Benefits

**Separation of Concerns:**
- ✅ Frontend (Vercel): Handles UI, user sessions, file uploads
- ✅ Backend (Railway): Handles CPU-intensive pipeline execution

**No Serverless Timeout:**
- ✅ Railway allows long-running processes (15-30 min pipeline executions)
- ✅ Vercel API routes respond instantly (proxy pattern)

**Cost Efficiency:**
- ✅ Vercel: Free tier for frontend hosting
- ✅ Railway: ~$5/month for backend (Starter plan)

**Scalability:**
- ✅ Backend can scale independently based on pipeline workload
- ✅ Frontend edge network remains fast globally

---
