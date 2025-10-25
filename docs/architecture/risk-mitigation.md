# Risk Mitigation

## ⚠️ Vercel Function Timeout (10s Hobby / 300s Pro limit)

**Problem:** Pipeline takes 30-60 seconds for document analysis, 15-30 minutes for full pipeline execution. Vercel Hobby plan kills serverless functions after 10 seconds.

**Solution (Story 8.1):** Frontend calls Railway backend directly, bypassing Vercel API routes entirely

### **✅ IMPLEMENTED: Direct Railway Backend Call (Story 8.1)**

**Architecture Change:**
```
OLD (Broken):
User → /api/analyze-document (Vercel) → LLM Analysis
                ↓
          504 Timeout after 10s ❌

NEW (Fixed):
User → Railway Backend Directly → Pipeline Execution → Webhook → Vercel
         (60-minute timeout)            ✓                ↓
                                                 /api/runs/[runId]/complete
                                                          ↓
                                                Frontend Polling (/api/runs)
```

**Frontend Implementation:**
```typescript
// app/analyze/[uploadId]/page.tsx
import { useAuth } from '@clerk/nextjs'

const analyzeDocument = async (blobUrl: string, companyId: string) => {
  const token = await getToken()  // Clerk JWT

  // Call Railway directly (bypasses Vercel timeout)
  const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      blob_url: blobUrl,
      company_id: companyId,
      user_id: userId
    })
  })

  return response.json()  // { run_id, status: "PROCESSING" }
}
```

**Benefits:**
- ✅ No Vercel timeout issues (Railway has 60-minute limit)
- ✅ Existing polling (`/api/runs`) and webhook (`/api/runs/[runId]/complete`) infrastructure preserved
- ✅ Clerk authentication ensures secure direct backend access

**Rollback Strategy:**
1. If Railway backend Clerk auth fails → Revert frontend to call `/api/analyze-document`
2. Keep deprecated endpoint live for 30-day migration period
3. Monitor error rates: <5% acceptable, >10% triggers rollback
4. Feature flag: `ENABLE_DIRECT_RAILWAY_CALL` environment variable

**New Risk: Clerk Authentication Failures**

| Risk | Mitigation |
|------|-----------|
| Invalid Clerk JWT | Return 401 with clear error message → Redirect to sign-in |
| Network failure to Railway | Show "Unable to reach service" with retry button |
| CORS errors | Railway backend configured with Vercel domain allowlist |
| CSP violations | `https://*.railway.app` already allowed in Story 7.8 |

**Monitoring:**
- Alert on Clerk auth failures >5% error rate
- Track Railway backend response times
- Monitor webhook delivery success rate

---
