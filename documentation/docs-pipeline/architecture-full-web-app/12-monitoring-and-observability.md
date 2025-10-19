# 12. Monitoring and Observability

## Logging Strategy

**Frontend Logger**:

```typescript
// lib/logger.ts
import * as Sentry from '@sentry/nextjs';

class Logger {
  pipelineEvent(event: 'start' | 'complete' | 'failed', runId: string, context?: any) {
    this.info(`Pipeline ${event}`, { runId, event, ...context });
  }

  costIncurred(runId: string, stage: number, cost: number, modelId: string) {
    this.info('LLM cost incurred', {
      runId,
      stage,
      cost,
      modelId,
      metric: 'llm_cost',
    });
  }
}

export const logger = new Logger();
```

**Backend Logger**:

```python
# pipeline/logger.py
import logging
import json

class StructuredLogger:
    def stage_complete(self, run_id: str, stage: int, duration_ms: float, tokens_used: int):
        self.info(
            f"Stage {stage} completed",
            run_id=run_id,
            stage=stage,
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            event='stage_complete'
        )
```

## Cost Monitoring Dashboard

**File**: `apps/web/app/admin/costs/page.tsx`

Displays:
- Daily/monthly spend vs. budget
- Cost per run average
- Most expensive stage identification
- Cost breakdown by model
- Daily cost trend chart

## Health Check Endpoint

**File**: `apps/web/app/api/health/route.ts`

```typescript
export async function GET() {
  const checks = {
    database: await checkDatabase(),
    blob_storage: await checkBlobStorage(),
    openrouter: await checkOpenRouter(),
  };

  const status = Object.values(checks).every(c => c.status === 'healthy')
    ? 'healthy'
    : 'unhealthy';

  return NextResponse.json({ status, checks }, {
    status: status === 'healthy' ? 200 : 503
  });
}
```

## Key Metrics & Thresholds

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Daily LLM Cost | <$10 | $10-$15 | >$15 |
| Pipeline Success Rate | >95% | 90-95% | <90% |
| Avg Stage Duration | <60s | 60-120s | >120s |
| API Response Time (p95) | <2s | 2-5s | >5s |
| Error Rate | <1% | 1-5% | >5% |

---
