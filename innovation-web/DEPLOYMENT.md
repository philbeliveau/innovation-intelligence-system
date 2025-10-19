# Deployment Documentation

## Production Environment

**Production URL:** https://innovation-hsco435p9-philippe-beliveaus-projects.vercel.app

**Deployment Platform:** Vercel
**Project ID:** `prj_4TeLwzlUAQdcevARQd4knrWqIib2`
**Last Deployment:** October 19, 2025
**Deployment ID:** `FQR4JS9m6i9VYxRxyBFDFncfRTLd`
**Build Time:** 48 seconds
**Status:** ✅ Ready

## Environment Variables

All environment variables are configured in Vercel dashboard for Production, Preview, and Development environments:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-***
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-sonnet-4.5

# Vercel Blob Storage (auto-generated)
BLOB_READ_WRITE_TOKEN=vercel_blob_***
```

See `.env.example` for complete list of required variables.

## Deployment Process

### Prerequisites
- Vercel CLI installed: `npm i -g vercel`
- Authenticated with Vercel: `vercel login`
- Project linked: `vercel link`

### Deploy to Production

```bash
# From innovation-web directory
cd innovation-web

# Build locally first (recommended)
npm run build

# Deploy to production
vercel --prod --yes
```

### Deploy to Preview

```bash
# Deploy to preview environment
vercel
```

### Check Deployment Status

```bash
# List recent deployments
vercel ls

# View logs for specific deployment
vercel logs [deployment-url]
```

## Known Limitations

### Python Pipeline

⚠️ **Python is NOT available in Vercel's Node.js runtime.**

**Issue:**
- Vercel uses Node.js serverless functions
- Python interpreter not available (`python3: command not found`)
- Pipeline execution fails in production

**Test Endpoint:**
- `/api/test-python` - Returns Python availability status
- Production result: `{ "success": false, "error": "python3: command not found" }`

**Contingency Options:**

1. **Deploy Python Pipeline Separately:**
   - Option A: Railway.app (supports Python + Docker)
   - Option B: Render.com (native Python support)
   - Option C: PythonAnywhere (Python-native hosting)
   - Option D: Google Cloud Run (containerized deployment)

2. **Hybrid Architecture:**
   - Keep Next.js frontend on Vercel
   - Deploy Python pipeline as separate microservice
   - Update API routes to call external Python service
   - Use webhook pattern for pipeline execution

3. **Docker Container (Advanced):**
   - Deploy entire stack (Next.js + Python) in single container
   - Use Railway, Fly.io, or Google Cloud Run
   - Requires Dockerfile with multi-language support

## Production Testing Results

### ✅ Verified Working
- Onboarding flow (company selection)
- Upload page rendering
- Company context persistence
- Mobile responsiveness (375x667 iPhone SE)
- Error boundary implementation
- Left sidebar hover detection
- CSS transitions (300ms ease-in-out)
- No console errors
- Page load performance (< 3s)

### ⚠️ Requires Additional Testing
- File upload to Vercel Blob
- Python pipeline execution
- Status polling (5-second intervals)
- Track selection and visualization
- Markdown rendering in results
- End-to-end pipeline flow (upload → analyze → pipeline → results)

### 🚧 Blocked by Python Limitation
- Pipeline execution (`/api/run`)
- Stage processing (Stages 1-5)
- Opportunity card generation
- Full E2E testing with real PDF

## Deployment Checklist

- [x] Environment variables configured in Vercel
- [x] Build succeeds locally (`npm run build`)
- [x] No TypeScript errors
- [x] No ESLint errors
- [x] Deployment to production successful
- [x] Production URL accessible
- [x] Onboarding flow tested
- [x] Mobile responsiveness verified
- [x] No console errors in production
- [ ] Python pipeline deployed separately
- [ ] API routes updated for external Python service
- [ ] Full E2E test with file upload
- [ ] Performance testing (Lighthouse score)

## Troubleshooting

### Build Failures

**Clean build cache:**
```bash
rm -rf .next
npm run build
```

**Check Node version:**
```bash
node --version  # Should be >= 18.x
```

### Environment Variables

**Add new variable:**
```bash
vercel env add VARIABLE_NAME production
vercel env add VARIABLE_NAME preview
vercel env add VARIABLE_NAME development
```

**List all variables:**
```bash
vercel env ls
```

### Deployment Issues

**Force redeploy:**
```bash
vercel --prod --force
```

**View deployment logs:**
```bash
vercel logs --follow
```

## Monitoring

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Analytics:** Available in Vercel dashboard
- **Error Tracking:** Built-in error boundary + Vercel logs
- **Performance:** Vercel Speed Insights (if enabled)

## Rollback Procedure

1. Go to Vercel dashboard
2. Navigate to Deployments
3. Find previous working deployment
4. Click "Promote to Production"

Or via CLI:
```bash
vercel rollback [deployment-url]
```

## Next Steps

1. **Deploy Python Pipeline:**
   - Evaluate hosting options (Railway vs Render vs GCP)
   - Create Python service with API endpoints
   - Document Python service deployment

2. **Update API Routes:**
   - Modify `/api/run` to call external Python service
   - Modify `/api/status/[runId]` to poll external service
   - Test webhook integration

3. **Complete E2E Testing:**
   - Upload PDF file
   - Verify pipeline execution
   - Test all 5 stages
   - Verify opportunity card generation

## Support

- **Vercel Documentation:** https://vercel.com/docs
- **Project GitHub:** [Repository URL]
- **Deployment Issues:** Contact philippe.beliveau@[domain]
