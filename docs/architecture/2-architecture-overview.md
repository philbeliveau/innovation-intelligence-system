# 2. Architecture Overview

## System Diagram

```mermaid
graph TB
    subgraph "Frontend - Next.js 15"
        A0[Onboarding<br/>Company Selection]
        A[Homepage<br/>Drag & Drop Only]
        A1[Intermediary Card<br/>Document Summary + Industry]
        B[Pipeline Viewer<br/>Real-time Stage Visualization]
        C[Left Sidebar<br/>Collapsible Home Menu]
    end

    subgraph "API Layer - Next.js Route Handlers"
        D[POST /api/upload<br/>Save to Vercel Blob]
        D1[POST /api/analyze-document<br/>LLM Extract Summary + Industry]
        E[POST /api/run<br/>Execute Pipeline Stages]
        F[GET /api/status/:runId<br/>Poll Stage Progress]
    end

    subgraph "Pipeline Execution - Python"
        G1[Stage 1: Input Processing<br/>Extract 2 Main Inspirations]
        G2[Stage 2: Signal Amplification<br/>Extract Trends]
        G3[Stage 3: General Translation<br/>Universal Lessons]
        G4[Stage 4: Brand Contextualization<br/>Brand-Specific Insights]
        G5[Stage 5: Opportunity Generation<br/>5 Opportunity Cards]
    end

    subgraph "Storage"
        H[Vercel Blob<br/>PDF Files]
        I[Local Filesystem<br/>Stage Outputs + Logs]
    end

    A --> D
    D --> D1
    D1 --> A1
    A1 --> E
    B --> F
    C --> A

    D --> H
    D1 --> I
    E --> G1
    G1 --> G2
    G2 --> G3
    G3 --> G4
    G4 --> G5
    G5 --> I

    F --> I

    style G1 fill:#e3f2fd
    style G2 fill:#f3e5f5
    style G3 fill:#fff3e0
    style G4 fill:#e8f5e9
    style G5 fill:#fce4ec
```

## Architecture Principles

1. **Minimal Web Wrapper**: Next.js frontend + API routes trigger existing Python pipeline
2. **Vercel Blob Storage**: Store uploaded PDFs, serve via public URLs
3. **File-Based State**: No database - use filesystem for stage outputs
4. **Sequential Execution**: Run stages 1-5 sequentially in single API call
5. **Log-Based Progress**: Poll log files to detect current stage
6. **shadcn/ui MCP**: Use Magic component builder for rapid UI development

---
