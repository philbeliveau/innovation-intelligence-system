# 2. Architecture Overview

## System Diagram

```mermaid
graph TB
    subgraph "User Authentication"
        AUTH[Clerk<br/>User Auth & Sessions]
    end

    subgraph "Frontend - Next.js 15 (Vercel)"
        A0[Onboarding<br/>Company Selection]
        A[Homepage<br/>Drag & Drop Only]
        A1[Intermediary Card<br/>Document Summary + Industry]
        B[Pipeline Viewer<br/>Real-time Stage Visualization]
        C[Left Sidebar<br/>Collapsible Home Menu]
        RUNS[Run History<br/>Paginated Grid View]
        DETAIL[Run Detail<br/>Cards + Report + Stages]
    end

    subgraph "API Layer - Next.js Route Handlers (Vercel)"
        D[POST /api/upload<br/>Save to Vercel Blob]
        D1[POST /api/analyze-document<br/>LLM Extract Summary + Industry]
        E[POST /api/pipeline/run<br/>Create Run & Trigger Pipeline]
        F[GET /api/pipeline/:runId/status<br/>Read Status from Prisma]
        STAGE_UPDATE[POST /api/pipeline/:runId/stage-update<br/>Webhook from Backend]
        RUNS_API[GET /api/pipeline<br/>List User Runs - Prisma]
        RUN_API[GET /api/pipeline/:id<br/>Get Run Details - Prisma]
        RERUN_API[POST /api/pipeline/:id/rerun<br/>Duplicate & Rerun - Prisma]
        CARD_API[POST /api/cards/:id/star<br/>Toggle Favorite - Prisma]
        PRISMA_LIB[lib/prisma.ts<br/>Singleton Client]
    end

    subgraph "Backend - FastAPI (Railway)"
        R1[POST /run<br/>Download PDF & Execute Pipeline]
        R2[GET /status/:runId<br/>DEPRECATED - Legacy Endpoint]
        R3[GET /health<br/>Health Check]
        PRISMA_CLIENT[PrismaAPIClient<br/>HTTP Client to Next.js]
    end

    subgraph "Pipeline Execution - Python (Railway)"
        G1[Stage 1: Input Processing<br/>Extract 2 Main Inspirations]
        G2[Stage 2: Signal Amplification<br/>Extract Trends]
        G3[Stage 3: General Translation<br/>Universal Lessons]
        G4[Stage 4: Brand Contextualization<br/>Brand-Specific Insights]
        G5[Stage 5: Opportunity Generation<br/>5 Opportunity Cards]
    end

    subgraph "Data Layer"
        H[Vercel Blob<br/>PDF Files]
        PG[(PostgreSQL<br/>Vercel/Neon<br/><br/>Tables:<br/>User, PipelineRun,<br/>OpportunityCard,<br/>InspirationReport,<br/>StageOutput)]
    end

    AUTH --> A0
    AUTH --> RUNS_API
    AUTH --> RUN_API

    A --> D
    D --> D1
    D1 --> A1
    A1 --> E
    B --> F
    C --> A
    C --> RUNS
    RUNS --> RUNS_API
    DETAIL --> RUN_API
    DETAIL --> CARD_API

    RUNS_API --> PRISMA_LIB
    RUN_API --> PRISMA_LIB
    RERUN_API --> PRISMA_LIB
    CARD_API --> PRISMA_LIB
    STAGE_UPDATE --> PRISMA_LIB
    PRISMA_LIB --> PG
    F --> PRISMA_LIB

    D --> H
    E --> R1
    E --> PRISMA_LIB
    R1 --> H
    R1 --> G1
    G1 --> G2
    G2 --> G3
    G3 --> G4
    G4 --> G5

    G1 --> PRISMA_CLIENT
    G2 --> PRISMA_CLIENT
    G3 --> PRISMA_CLIENT
    G4 --> PRISMA_CLIENT
    G5 --> PRISMA_CLIENT
    PRISMA_CLIENT --> STAGE_UPDATE

    style G1 fill:#e3f2fd
    style G2 fill:#f3e5f5
    style G3 fill:#fff3e0
    style G4 fill:#e8f5e9
    style G5 fill:#fce4ec
    style R1 fill:#fff9c4
    style R2 fill:#ffcccc
    style R3 fill:#fff9c4
    style PG fill:#d1c4e9
    style PRISMA_LIB fill:#b2ebf2
    style PRISMA_CLIENT fill:#b2ebf2
    style STAGE_UPDATE fill:#c8e6c9
    style AUTH fill:#c8e6c9
```

## Architecture Principles

1. **User Authentication Layer**: Clerk handles authentication, provides `userId` for all database queries
2. **Prisma-First Database**: Single ORM for all database operations (reads AND writes)
3. **HTTP API Integration**: Python backend writes to Prisma via Next.js API webhook endpoints
4. **Backend Separation**: FastAPI backend on Railway handles Python pipeline execution
5. **Vercel Blob Storage**: Store uploaded PDFs, Railway backend downloads via blob URLs
6. **Database-Driven State**: PostgreSQL stores runs, cards, reports, stage outputs (single source of truth)
7. **Sequential Execution**: Run stages 1-5 sequentially, writing to Prisma after each stage via HTTP
8. **Real-time Status Updates**: Frontend reads directly from Prisma, no polling Railway backend
9. **User Data Isolation**: Every query filtered by authenticated Clerk user ID
10. **shadcn/ui MCP**: Use Magic component builder for rapid UI development

## Data Flow Architecture

### Frontend Read Path (Prisma)
```
User Request → Clerk Auth → Next.js API Route → Prisma Client → PostgreSQL
```

### Backend Write Path (Prisma via HTTP API)
```
Pipeline Stage → PrismaAPIClient → POST /api/pipeline/:runId/stage-update → Prisma Client → PostgreSQL
```

### Prisma-First Architecture Benefits

**Why Prisma for Everything:**
- ✅ Single source of truth (no dual-state management)
- ✅ Type-safe schema shared between frontend and backend contracts
- ✅ Real-time status updates (no polling, no sync issues)
- ✅ Survives Railway dyno restarts (database persistence)
- ✅ Auto-completion logic (stage 5 done → PipelineRun.status = COMPLETED)
- ✅ Simplified testing (one database to mock/seed)

**Backend Integration via HTTP:**
- Python backend calls Next.js API endpoints via HTTP
- Authenticated with `X-Webhook-Secret` header
- No direct database connection needed from Railway
- Frontend acts as database gateway (Prisma ORM layer)

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
