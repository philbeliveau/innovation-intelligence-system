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

---

## 8.6 Architecture Benefits

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
