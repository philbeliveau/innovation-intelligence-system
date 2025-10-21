# 2. Architecture Overview

## System Diagram

```mermaid
graph TB
    subgraph "Frontend - Next.js 15 (Vercel)"
        A0[Onboarding<br/>Company Selection]
        A[Homepage<br/>Drag & Drop Only]
        A1[Intermediary Card<br/>Document Summary + Industry]
        B[Pipeline Viewer<br/>Real-time Stage Visualization]
        C[Left Sidebar<br/>Collapsible Home Menu]
    end

    subgraph "API Layer - Next.js Route Handlers (Vercel)"
        D[POST /api/upload<br/>Save to Vercel Blob]
        D1[POST /api/analyze-document<br/>LLM Extract Summary + Industry]
        E[POST /api/run<br/>Proxy to Railway Backend]
        F[GET /api/status/:runId<br/>Proxy Status from Railway]
    end

    subgraph "Backend - FastAPI (Railway)"
        R1[POST /run<br/>Download PDF & Execute Pipeline]
        R2[GET /status/:runId<br/>Return Pipeline Status]
        R3[GET /health<br/>Health Check]
    end

    subgraph "Pipeline Execution - Python (Railway)"
        G1[Stage 1: Input Processing<br/>Extract 2 Main Inspirations]
        G2[Stage 2: Signal Amplification<br/>Extract Trends]
        G3[Stage 3: General Translation<br/>Universal Lessons]
        G4[Stage 4: Brand Contextualization<br/>Brand-Specific Insights]
        G5[Stage 5: Opportunity Generation<br/>5 Opportunity Cards]
    end

    subgraph "Storage"
        H[Vercel Blob<br/>PDF Files]
        I[Railway Filesystem<br/>Stage Outputs + Logs]
    end

    A --> D
    D --> D1
    D1 --> A1
    A1 --> E
    B --> F
    C --> A

    D --> H
    E --> R1
    F --> R2
    R1 --> H
    R1 --> G1
    G1 --> G2
    G2 --> G3
    G3 --> G4
    G4 --> G5
    G5 --> I
    R2 --> I

    style G1 fill:#e3f2fd
    style G2 fill:#f3e5f5
    style G3 fill:#fff3e0
    style G4 fill:#e8f5e9
    style G5 fill:#fce4ec
    style R1 fill:#fff9c4
    style R2 fill:#fff9c4
    style R3 fill:#fff9c4
```

## Architecture Principles

1. **Backend Separation**: FastAPI backend on Railway handles Python pipeline execution (Stories 5.1-5.3)
2. **Frontend Proxy Pattern**: Next.js API routes proxy requests to Railway backend
3. **Vercel Blob Storage**: Store uploaded PDFs, Railway backend downloads via blob URLs
4. **File-Based State**: No database - Railway filesystem stores stage outputs
5. **Sequential Execution**: Run stages 1-5 sequentially on Railway infrastructure
6. **CORS & Environment**: Railway backend configured with CORS for Vercel domains
7. **shadcn/ui MCP**: Use Magic component builder for rapid UI development

## Deployment Architecture (Epic 5)

**Frontend (Vercel):**
- Next.js 15 application
- API routes proxy to Railway backend
- Environment variable: `NEXT_PUBLIC_BACKEND_URL`

**Backend (Railway):**
- FastAPI application with 3 endpoints: `/run`, `/status/:runId`, `/health`
- Python pipeline execution (stages 1-5)
- Dockerfile deployment with uvicorn server
- Environment variables: `OPENROUTER_API_KEY`, `VERCEL_BLOB_READ_WRITE_TOKEN`

**Benefits:**
- ✅ No Vercel serverless timeout issues (300s limit)
- ✅ Independent scaling of backend processing
- ✅ Simplified development (local Docker backend + Vercel frontend)
- ✅ Clear separation of concerns

---
