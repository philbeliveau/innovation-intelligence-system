# 2. High Level Architecture

## System Overview

```mermaid
graph TB
    subgraph "Frontend - Next.js 14 App Router"
        A[Prompt Editor<br/>Monaco Editor]
        B[Test Execution UI]
        C[Results Viewer]
        D[Brand Comparison]
    end

    subgraph "API Layer - Next.js Route Handlers"
        E[POST /api/pipeline/execute]
        F[GET /api/pipeline/status/:runId]
        G[POST /api/prompts]
        H[POST /api/cost-estimate]
    end

    subgraph "Backend - Python Serverless Functions"
        I1[Stage 1:<br/>Input Processing]
        I2[Stage 2:<br/>Signal Amplification]
        I3[Stage 3:<br/>General Translation]
        I4[Stage 4:<br/>Brand Contextualization]
        I5[Stage 5:<br/>Opportunity Generation]
    end

    subgraph "Storage Layer"
        J[Vercel Postgres<br/>Metadata & Config]
        K[Vercel Blob Storage<br/>Documents & Outputs]
    end

    subgraph "External Services"
        L[OpenRouter API<br/>6 LLM Models]
    end

    A --> E
    B --> E
    B --> F
    C --> F
    D --> F

    E --> I1
    I1 --> K
    I1 --> J
    I1 --> I2
    I2 --> K
    I2 --> I3
    I3 --> K
    I3 --> I4
    I4 --> K
    I4 --> I5
    I5 --> K
    I5 --> J

    I1 & I2 & I3 & I4 & I5 --> L
    I4 --> K

    G --> J
    H --> J

    style I4 fill:#ff6b6b
    style K fill:#4ecdc4
    style L fill:#ffe66d
```

## Architecture Principles

1. **Stateless Serverless Functions**: Each stage is an independent Python function, survives 300s Vercel timeout
2. **Blob-Based State Persistence**: All intermediate outputs saved to Vercel Blob for debugging and auditability
3. **Stage-by-Stage Orchestration**: API routes trigger stages sequentially, update Postgres status after each
4. **Research Data Injection**: Stage 4 loads comprehensive brand profiles from Blob storage (8 sections, 120+ facts)
5. **Per-Stage Model Selection**: Users can override default model for specific stages (e.g., use expensive Claude for Stage 4 only)

## Deployment Model

- **Platform**: Vercel (Hobby or Pro tier)
- **Monorepo Structure**: NPM workspaces with `apps/web` (Next.js) and `api/python` (serverless functions)
- **Regions**: Single region (US East - `iad1`) for simplicity
- **Scaling**: Auto-scaling via Vercel (no manual configuration)

---
