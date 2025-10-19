# Risk Mitigation

## ⚠️ Vercel Function Timeout (300s limit)

**Problem:** Pipeline takes 15-30 minutes, Vercel kills after 300s

**Solution:** Run pipeline in background, don't wait for completion

```typescript
// app/api/run/route.ts (FIXED)
export async function POST(request: Request) {
  const { blob_url, brand_id } = await request.json()
  const run_id = generateRunId()

  // Spawn process WITHOUT awaiting
  exec(
    `nohup python scripts/run_pipeline.py --input-file /tmp/${run_id}.pdf --brand ${brand_id} --run-id ${run_id} &`,
    { cwd: process.cwd() }
  )

  // Return immediately
  return NextResponse.json({ run_id, status: 'running' })
}
```

Frontend polls `/api/status/:runId` to track progress (no timeout issues).

---
