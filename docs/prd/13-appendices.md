# 13. Appendices

## 13.1 Glossary

| Term | Definition |
|------|------------|
| Blob Storage | Vercel's file storage service for large assets |
| Brand Profile | JSON file with brand attributes (values, audience, constraints) |
| Inspiration Track | One of two main patterns extracted in Stage 1 |
| Opportunity Card | Final deliverable - single innovation concept with rationale |
| Pipeline | 5-stage LLM workflow transforming signals into opportunities |
| Run ID | Unique identifier for each pipeline execution (format: `run-{timestamp}`) |
| SPECTRE | Validation framework (Structural, Psychological, Economic, Cultural, Technical, Risk, Execution) |

## 13.2 Reference Documents

- **Architecture:** `/docs/architecture-hackathon-web-app.md`
- **Implementation Guide:** `/HACKATHON-START-HERE.md`
- **Current State Analysis:** `/docs/hackathon-analysis-current-state.md`
- **Original PRD:** `/docs/prd.md` (CLI version)
- **Visual Reference:** `/docs/image/main-page.png`

## 13.3 API Documentation

**Base URL:** `https://your-app.vercel.app`

**Endpoints:**
- `POST /api/upload` - Upload file to Blob
- `POST /api/run` - Start pipeline execution
- `GET /api/status/[runId]` - Get pipeline status
- (Future: `GET /api/results/[runId]` - Get opportunities JSON)

**Rate Limits:** None (hackathon), 100 requests/hour (Phase 2)

## 13.4 Environment Variables

```bash
# .env.local (Next.js)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-sonnet-4.5
BLOB_READ_WRITE_TOKEN=vercel_blob_...  # Auto-generated
```

---
