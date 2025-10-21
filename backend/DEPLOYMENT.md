# Railway Deployment Guide

This document provides step-by-step instructions for deploying the Innovation Intelligence Backend to Railway.

---

## Prerequisites

- Railway account (free tier available at https://railway.app)
- GitHub repository access
- OpenRouter API key
- Vercel Blob read/write token

---

## Railway Project Setup

### 1. Create New Railway Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose the `innovation-intelligence-system` repository
5. **Project Name:** `My-board-of-ideators`
6. **Service Name:** `innovation-backend` (or auto-generated)

### 2. Configure Root Directory

Railway needs to know where the backend code lives:

1. In Railway dashboard, go to **Settings** → **Service Settings**
2. Set **Root Directory:** `/backend`
3. Railway will now use the `Dockerfile` in `/backend` for builds

### 3. Set Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
# Required: OpenRouter LLM API
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-sonnet-4.5

# Required: Vercel Blob storage
VERCEL_BLOB_READ_WRITE_TOKEN=vercel_blob_rw_xxxxxxxxxxxxxxxxxxxx

# Required: Port configuration
PORT=8000

# Optional: CORS configuration for Vercel preview deployments
ALLOWED_ORIGINS=https://preview-abc123.vercel.app,https://preview-xyz789.vercel.app
```

**IMPORTANT:** The `PORT` variable must be set to `8000` to match the Dockerfile and health check configuration.

**CORS Configuration:**
- Production frontend (`https://innovation-web.vercel.app`) is pre-configured in code
- For Vercel preview deployments, add each preview URL to `ALLOWED_ORIGINS` (comma-separated)
- Local development (`http://localhost:3000`) is pre-configured in code

### 4. Configure Service Settings

In Railway dashboard, **Settings** tab:

- **Region:** `us-west1` (or closest to your users)
- **Instance Type:** Starter plan (512MB RAM)
- **Auto-deploy:** Enable for `main` branch
- **Health Check:** Automatically configured via `railway.json`
  - **Path:** `/health`
  - **Interval:** 30 seconds
  - **Timeout:** 100 seconds

---

## Deployment Process

### Automatic Deployment (Recommended)

1. Push code to `main` branch:
   ```bash
   git add .
   git commit -m "feat(backend): add Railway deployment config"
   git push origin main
   ```

2. Railway automatically detects the push and starts deployment
3. Monitor build progress in Railway dashboard **Deployments** tab
4. Deployment typically takes 3-5 minutes

### Manual Deployment

1. In Railway dashboard, go to **Deployments** tab
2. Click **"Deploy Now"** button
3. Select the commit you want to deploy
4. Railway builds and deploys the selected commit

---

## Verification Steps

### 1. Check Deployment Status

- Railway dashboard shows **"Active"** status (green indicator)
- Build logs show no errors
- Public URL is generated: `https://<random>.railway.app`

### 2. Test Health Endpoint

```bash
curl https://<your-railway-url>.railway.app/health
```

**Expected Response:**
```json
{"status": "ok"}
```

### 3. Test OpenAPI Documentation

Visit in browser:
```
https://<your-railway-url>.railway.app/docs
```

You should see the FastAPI interactive documentation (Swagger UI).

### 4. Test CORS Configuration

From Vercel frontend (local or deployed):
```javascript
// Test CORS from frontend
fetch('https://<your-railway-url>.railway.app/health')
  .then(r => r.json())
  .then(data => console.log('CORS working:', data))
```

**Expected:** No CORS errors in browser console.

### 5. Test Auto-Restart

1. In Railway dashboard, go to **Logs** tab
2. Find the running process and note the uptime
3. In **Settings** → **Service**, click **"Restart Service"**
4. Wait 30-60 seconds
5. Verify service is back online (check `/health` endpoint)

**Expected:** Service restarts automatically and becomes healthy.

---

## Monitoring and Logs

### Viewing Logs

1. Railway dashboard → **Logs** tab
2. Filter by log level:
   - `INFO` - Normal operation logs
   - `WARNING` - Non-critical issues
   - `ERROR` - Critical errors requiring attention

### Common Log Messages

**Successful Startup:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Health Check Success:**
```
INFO:     127.0.0.1:xxxxx - "GET /health HTTP/1.1" 200 OK
```

**CORS Preflight:**
```
INFO:     <origin> - "OPTIONS /run HTTP/1.1" 200 OK
```

### Monitoring Metrics

Railway provides built-in metrics:
- **CPU Usage** - Should stay below 50% for MVP
- **Memory Usage** - 512MB limit (Starter plan)
- **Network I/O** - Incoming/outgoing requests
- **Deployment Count** - Track deployment frequency

---

## Rollback Procedure

### Rollback to Previous Deployment

1. Railway dashboard → **Deployments** tab
2. Find the previous successful deployment
3. Click **"•••"** menu → **"Redeploy"**
4. Confirm rollback
5. Railway redeploys the selected commit
6. Verify health endpoint after rollback

**Rollback Time:** Typically 2-3 minutes.

---

## Troubleshooting

### Issue: Build Fails with "requirements.txt not found"

**Cause:** Railway is not using the correct root directory.

**Solution:**
1. Settings → Service Settings
2. Set **Root Directory:** `/backend`
3. Trigger manual redeployment

### Issue: Health Check Failing

**Cause:** Application not responding on port 8000 or `/health` endpoint broken.

**Solution:**
1. Check Railway logs for startup errors
2. Verify `PORT=8000` environment variable is set
3. Test `/health` endpoint returns `{"status": "ok"}`
4. Ensure Dockerfile CMD matches `railway.json` startCommand

### Issue: CORS Errors from Vercel Frontend

**Cause:** Frontend origin not in allowed CORS origins list.

**Solution:**
1. Check frontend URL (e.g., `https://preview-abc123.vercel.app`)
2. Add to `ALLOWED_ORIGINS` environment variable in Railway
3. Restart Railway service to apply new environment variables
4. Test CORS from frontend again

### Issue: Environment Variables Not Loading

**Cause:** Variables not set in Railway dashboard or typos.

**Solution:**
1. Railway dashboard → **Variables** tab
2. Verify all required variables are present
3. Check for typos in variable names (case-sensitive)
4. Click **"Redeploy"** to apply changes

### Issue: Deployment Takes Too Long (>10 minutes)

**Cause:** Docker image build is slow or stuck.

**Solution:**
1. Check Railway **Build Logs** for bottlenecks
2. Verify `requirements.txt` doesn't have unnecessary packages
3. Cancel deployment and retry
4. Contact Railway support if persistent

### Issue: Service Crashes After Deployment

**Cause:** Missing dependencies, import errors, or invalid environment variables.

**Solution:**
1. Check Railway **Logs** for Python tracebacks
2. Common errors:
   - `ModuleNotFoundError` - Missing dependency in `requirements.txt`
   - `ImportError` - Incorrect import paths
   - `KeyError` - Missing required environment variable
3. Fix the error locally first
4. Test with `uvicorn app.main:app --reload`
5. Push fix to trigger redeployment

---

## Local Docker Testing

Before deploying to Railway, test the Docker build locally:

### Build Docker Image

```bash
cd backend
docker build -t innovation-backend .
```

**Expected Build Time:** 2-4 minutes
**Expected Image Size:** <500MB

### Run Docker Container Locally

```bash
# Create .env file first (don't commit to git)
cp .env.example .env
# Edit .env with your actual API keys

# Run container with environment variables
docker run -p 8000:8000 --env-file .env innovation-backend
```

### Test Local Docker Container

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status": "ok"}

# Test OpenAPI docs
open http://localhost:8000/docs
```

### Cleanup Local Docker

```bash
# Stop container
docker ps  # Find container ID
docker stop <container_id>

# Remove image (optional)
docker rmi innovation-backend
```

---

## Railway Public URL

After successful deployment, Railway generates a public URL:

**Production URL:** `https://innovation-backend-production.up.railway.app`

**Format:** `https://<service-name>-<environment>.up.railway.app`

**Usage:**
1. Copy the public URL from Railway dashboard
2. Update frontend API client to use this URL
3. Test frontend → backend communication
4. Document URL in Story 5.3 for frontend integration

**Custom Domain (Optional):**
- Railway supports custom domains (e.g., `api.innovation-intelligence.com`)
- Configure in **Settings** → **Domains**
- Requires DNS configuration (CNAME record)

---

## Cost Estimation

**Railway Starter Plan:**
- **Base Cost:** $5/month for hobby projects
- **Includes:** 512MB RAM, 1 vCPU, 1GB disk
- **Bandwidth:** 100GB outbound/month
- **Deployments:** Unlimited

**Scaling Considerations:**
- For production, consider upgrading to **Pro Plan** ($20/month)
- Pro plan includes 8GB RAM, 8 vCPU, auto-scaling
- Monitor usage in Railway dashboard to avoid overages

---

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENROUTER_API_KEY` | ✅ Yes | OpenRouter API key for LLM calls | `sk-or-v1-...` |
| `OPENROUTER_BASE_URL` | ✅ Yes | OpenRouter API base URL | `https://openrouter.ai/api/v1` |
| `LLM_MODEL` | ✅ Yes | LLM model identifier | `anthropic/claude-sonnet-4.5` |
| `VERCEL_BLOB_READ_WRITE_TOKEN` | ✅ Yes | Vercel Blob storage token | `vercel_blob_rw_...` |
| `PORT` | ✅ Yes | Port for uvicorn server | `8000` |
| `ALLOWED_ORIGINS` | ❌ No | Additional CORS origins (comma-separated) | `https://preview-abc.vercel.app` |

---

## Next Steps

After successful Railway deployment:

1. **Document Railway URL** - Copy public URL for Story 5.3
2. **Update Frontend** - Configure frontend API client to use Railway URL
3. **Test E2E Flow** - Upload PDF → Pipeline execution → Results display
4. **Setup Monitoring** - Configure Railway alerts for downtime
5. **Production Hardening** - Add rate limiting, authentication (future stories)

---

## Support

**Railway Documentation:** https://docs.railway.app
**Railway Discord:** https://discord.gg/railway
**Railway Status:** https://status.railway.app

**Project-Specific Issues:**
- File bug reports in GitHub issues
- Tag with `deployment` label
- Include Railway logs and error messages

---

**Last Updated:** 2025-10-21
**Maintained By:** DevOps Team
**Railway Project:** `My-board-of-ideators`
**Railway Service:** `innovation-backend`
