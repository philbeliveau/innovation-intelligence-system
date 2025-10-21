# Innovation Intelligence System - Frontend

Next.js frontend for the CPG Innovation Intelligence Pipeline. Connects to Railway-hosted FastAPI backend for pipeline execution.

## Architecture

- **Frontend:** Next.js 15 (App Router) + shadcn/ui
- **Backend:** FastAPI on Railway (`https://innovation-backend-production.up.railway.app`)
- **Storage:** Vercel Blob for PDF uploads
- **Auth:** Clerk authentication

## Getting Started

### Prerequisites

- Node.js 18+
- Access to Railway backend (see `backend/DEPLOYMENT.md`)
- Vercel Blob storage token
- Clerk authentication keys

### Environment Variables

Create `.env.local` file:

```bash
# Vercel Blob Storage
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_...

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Railway Backend URL
# Production: Railway public URL
# Local development: http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=https://innovation-backend-production.up.railway.app
```

For **local development** with Dockerized backend:
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Build

```bash
npm run build
npm run start
```

## Backend Integration

The frontend communicates with the Railway FastAPI backend via API routes:

- **POST `/api/run`** - Triggers pipeline execution
  - Sends blob URL and brand ID to Railway backend
  - Returns `run_id` for tracking

- **GET `/api/status/[runId]`** - Polls pipeline status
  - Proxies requests to Railway backend
  - Returns current stage, status, and data

### Backend Client (`lib/backend-client.ts`)

Provides typed functions with retry logic:

```typescript
import { runPipeline, getStatus } from '@/lib/backend-client'

// Start pipeline
const { run_id } = await runPipeline(blobUrl, brandId)

// Check status
const status = await getStatus(run_id)
```

**Retry Logic:**
- 3 retry attempts with exponential backoff (1s, 2s, 4s)
- 30-second timeout per request
- Graceful error handling for network failures

## Deployment

### Vercel Deployment

1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_BACKEND_URL` - Railway public URL
   - `BLOB_READ_WRITE_TOKEN` - Vercel Blob token
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk public key
   - `CLERK_SECRET_KEY` - Clerk secret key

3. Deploy:
```bash
vercel deploy --prod
```

### Railway Backend Setup

Ensure Railway backend is deployed and healthy:
```bash
curl https://innovation-backend-production.up.railway.app/health
# Expected: {"status":"ok","version":"1.0.0"}
```

See `backend/DEPLOYMENT.md` for Railway configuration.

## Troubleshooting

### Backend Connection Issues

**Error:** "Cannot connect to backend"

**Solutions:**
1. Verify `NEXT_PUBLIC_BACKEND_URL` is set correctly
2. Check Railway backend health: `curl $BACKEND_URL/health`
3. Check Railway logs for errors
4. Verify CORS is configured (see `backend/app/main.py`)

**Error:** "Request timeout (30s exceeded)"

**Solutions:**
1. Railway backend may be cold starting (first request after idle)
2. Check Railway instance logs for slow LLM responses
3. Increase timeout in `lib/backend-client.ts` if needed

**Error:** "Run ID not found"

**Solutions:**
1. Pipeline may not have started yet (check backend logs)
2. `run_id` may be invalid (check format: `run-{timestamp}`)
3. Railway backend may have restarted (runs stored in-memory)

### Local Development with Dockerized Backend

1. Start Railway backend locally:
```bash
cd backend
docker run -p 8000:8000 innovation-backend
```

2. Update `.env.local`:
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

3. Start frontend:
```bash
npm run dev
```

### CORS Errors

If you see CORS errors in browser console:

1. Verify frontend domain is in Railway `ALLOWED_ORIGINS`
2. Check `backend/app/main.py` CORS configuration
3. Add preview deployment URL to Railway environment variables:
```bash
ALLOWED_ORIGINS=https://innovation-web-git-feature-yourname.vercel.app
```

## Project Structure

```
innovation-web/
├── app/
│   ├── api/
│   │   ├── run/route.ts              # Trigger pipeline (Railway backend)
│   │   └── status/[runId]/route.ts   # Poll status (Railway proxy)
│   ├── pipeline/[runId]/page.tsx     # Pipeline viewer with polling
│   ├── results/[runId]/page.tsx      # Results display
│   └── upload/page.tsx               # File upload
├── components/
│   └── pipeline/                     # Pipeline visualization components
├── lib/
│   ├── backend-client.ts             # Railway API client (NEW)
│   └── upload-history.ts             # Vercel Blob utilities
└── .env.local                        # Environment variables
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Railway Documentation](https://docs.railway.app)
- [Vercel Blob Documentation](https://vercel.com/docs/storage/vercel-blob)
- [Clerk Documentation](https://clerk.com/docs)
