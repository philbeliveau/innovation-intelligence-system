# Innovation Intelligence Pipeline Testing System - Architecture Document

**Version:** 1.0 (Draft - Full Production Architecture)
**Last Updated:** 2025-01-XX
**Status:** In Progress
**Architecture Type:** Fullstack Web Application (Next.js + Python Serverless)

---

## ⚠️ HACKATHON IMPLEMENTATION

**For 1-day hackathon build, see simplified architecture:**
→ `/docs/architecture-hackathon-web-app.md`

**This document** describes the full production architecture with Postgres, serverless functions, and advanced features (18-25 hours of development).

**Hackathon architecture** is a minimal web wrapper around the existing pipeline (8-10 hours of development).

---

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [High Level Architecture](#2-high-level-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Data Models](#4-data-models)
5. [API Specification](#5-api-specification)
6. [Components](#6-components)
7. [Database Schema](#7-database-schema)
8. [Frontend Architecture](#8-frontend-architecture)
9. [Backend Architecture](#9-backend-architecture)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Testing Strategy](#11-testing-strategy)
12. [Monitoring and Observability](#12-monitoring-and-observability)
13. [Coding Standards](#13-coding-standards) *(To be completed)*
14. [Error Handling Strategy](#14-error-handling-strategy) *(To be completed)*

---

## 1. Introduction

### Purpose

The **Innovation Intelligence Pipeline Testing System** is an experimentation platform designed to enable rapid iteration on a 5-stage LangChain-based pipeline that transforms market signals into brand-specific innovation opportunities. This architecture supports the core workflow defined in the PRD:

**Input** → **Signal Amplification** → **General Translation** → **Brand Contextualization** → **Opportunity Generation**

### Key Business Requirements

1. **Experimentation Platform**: Users need to test different prompts, models, and configurations to find optimal pipeline performance
2. **Cost Transparency**: LLM API calls are expensive - every test run must display estimated and actual costs
3. **Research Data Integration**: Each test requires comprehensive brand research data (120+ data points across 8 dimensions)
4. **One-at-a-Time Execution**: Run single tests with specific input/brand combinations for focused iteration
5. **Side-by-Side Comparison**: Compare opportunity outputs across different brands for the same input

### Architecture Decisions

**Platform Choice: Vercel**
- **Rationale**: Unified deployment for Next.js frontend + Python serverless functions, eliminates multi-cloud complexity
- **Constraints**: 300-second function timeout requires stage-by-stage execution (not monolithic pipeline)
- **Benefits**: Atomic deployments, instant rollbacks, integrated Blob storage and Postgres

**Storage Strategy: Hybrid (Postgres + Blob)**
- **Postgres**: Metadata, test run status, prompt configurations (fast queries, relational data)
- **Vercel Blob**: Raw inputs, research files, stage outputs, opportunity cards (large documents, versioning)
- **Rationale**: Postgres for indexing/search, Blob for cost-effective content storage

**UI Framework: Next.js 14 App Router + shadcn/ui**
- **Rationale**: React Server Components reduce client-side bundle, shadcn provides copy-paste components (no NPM bloat)
- **Monaco Editor**: VS Code-powered prompt editing with syntax highlighting and multi-line support

**LLM Access: OpenRouter API**
- **Rationale**: Single API for 6 models (DeepSeek to Claude Sonnet 4), no vendor lock-in, transparent pricing
- **Cost Range**: $0.14/1M tokens (DeepSeek) to $3.00/1M tokens (Claude Sonnet 4)

---

## 2. High Level Architecture

### System Overview

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

### Architecture Principles

1. **Stateless Serverless Functions**: Each stage is an independent Python function, survives 300s Vercel timeout
2. **Blob-Based State Persistence**: All intermediate outputs saved to Vercel Blob for debugging and auditability
3. **Stage-by-Stage Orchestration**: API routes trigger stages sequentially, update Postgres status after each
4. **Research Data Injection**: Stage 4 loads comprehensive brand profiles from Blob storage (8 sections, 120+ facts)
5. **Per-Stage Model Selection**: Users can override default model for specific stages (e.g., use expensive Claude for Stage 4 only)

### Deployment Model

- **Platform**: Vercel (Hobby or Pro tier)
- **Monorepo Structure**: NPM workspaces with `apps/web` (Next.js) and `api/python` (serverless functions)
- **Regions**: Single region (US East - `iad1`) for simplicity
- **Scaling**: Auto-scaling via Vercel (no manual configuration)

---

## 3. Tech Stack

### Complete Technology Matrix

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Frontend Framework** | Next.js | 15.1.8 | React Server Components + App Router |
| **UI Components** | shadcn/ui | latest | Copy-paste components, no NPM bloat |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS framework |
| **Code Editor** | Monaco Editor | 4.6.0 | VS Code-powered prompt editing |
| **React Wrapper** | @monaco-editor/react | 4.6.0 | React integration for Monaco |
| **State Management** | Zustand | 4.5+ | Lightweight client-side state |
| **Form Handling** | React Hook Form | 7.50+ | Type-safe form validation |
| **API Client** | Native Fetch | - | Built-in fetch with TypeScript types |
| **Backend Runtime** | Python | 3.11 | Vercel serverless functions |
| **LLM Framework** | LangChain | 0.1.0 | Pipeline orchestration |
| **LLM Integration** | langchain-openai | 0.0.5 | OpenRouter API compatibility |
| **LLM Provider** | OpenRouter | latest | Unified API gateway for 6+ models |
| **LLM Models** | Multiple providers | - | DeepSeek ($0.14/1M) to Claude Sonnet 4 ($3.00/1M) |
| **Database** | Vercel Postgres | latest | Metadata, configs, run status |
| **ORM** | Drizzle ORM | 0.30+ | Type-safe SQL queries |
| **Blob Storage** | Vercel Blob | 0.2.0 | Documents, outputs, research files |
| **Templating** | Jinja2 | 3.1.3 | Opportunity card generation |
| **Validation** | Pydantic | 2.5.3 | Python data validation |
| **Deployment** | Vercel | latest | Frontend + serverless deployment |
| **Monitoring** | Sentry | latest | Error tracking |
| **Logging** | Axiom | latest | Structured log aggregation |
| **Analytics** | Vercel Analytics | latest | Web vitals, user analytics |
| **Performance** | Vercel Speed Insights | latest | Real user monitoring |

### Model Configuration

```typescript
interface LLMModelConfiguration {
  id: string;
  provider: "deepseek" | "anthropic" | "openai" | "moonshot";
  display_name: string;
  model_identifier: string; // OpenRouter format: "provider/model-name"
  input_price_per_1m_tokens: number;
  output_price_per_1m_tokens: number;
  context_window: number;
  capabilities: string[];
  recommended_for: string;
}

const AVAILABLE_MODELS: LLMModelConfiguration[] = [
  {
    id: "deepseek-chat",
    provider: "deepseek",
    display_name: "DeepSeek Chat",
    model_identifier: "deepseek/deepseek-chat",
    input_price_per_1m_tokens: 0.14,
    output_price_per_1m_tokens: 0.28,
    context_window: 64000,
    capabilities: ["text"],
    recommended_for: "Cost-effective experimentation, high-volume testing",
  },
  {
    id: "claude-haiku-3-5",
    provider: "anthropic",
    display_name: "Claude Haiku 3.5",
    model_identifier: "anthropic/claude-3-5-haiku-20241022",
    input_price_per_1m_tokens: 0.80,
    output_price_per_1m_tokens: 4.00,
    context_window: 200000,
    capabilities: ["text"],
    recommended_for: "Fast processing, moderate quality requirements",
  },
  {
    id: "claude-sonnet-4",
    provider: "anthropic",
    display_name: "Claude Sonnet 4",
    model_identifier: "anthropic/claude-sonnet-4-20250514",
    input_price_per_1m_tokens: 3.00,
    output_price_per_1m_tokens: 15.00,
    context_window: 200000,
    capabilities: ["text", "vision"],
    recommended_for: "Highest quality outputs, critical stages (Stage 4)",
  },
  {
    id: "gpt-4o-mini",
    provider: "openai",
    display_name: "GPT-4o Mini",
    model_identifier: "openai/gpt-4o-mini",
    input_price_per_1m_tokens: 0.15,
    output_price_per_1m_tokens: 0.60,
    context_window: 128000,
    capabilities: ["text", "vision"],
    recommended_for: "Balanced cost and performance",
  },
  {
    id: "gpt-4o",
    provider: "openai",
    display_name: "GPT-4o",
    model_identifier: "openai/gpt-4o",
    input_price_per_1m_tokens: 2.50,
    output_price_per_1m_tokens: 10.00,
    context_window: 128000,
    capabilities: ["text", "vision"],
    recommended_for: "Complex reasoning, multi-modal inputs",
  },
  {
    id: "kimi-k1-5",
    provider: "moonshot",
    display_name: "Kimi K1.5",
    model_identifier: "moonshot/kimi-k1.5",
    input_price_per_1m_tokens: 0.30,
    output_price_per_1m_tokens: 0.30,
    context_window: 128000,
    capabilities: ["text"],
    recommended_for: "Long context processing, research synthesis",
  },
];
```

---

## 4. Data Models

### Core TypeScript Interfaces

```typescript
// Test Run (Primary Entity)
interface TestRun {
  id: string; // UUID
  status: "pending" | "running" | "completed" | "failed";
  input_id: string; // FK to InputDocument
  brand_id: string; // FK to BrandProfile
  prompt_config_id: string; // FK to PromptConfiguration

  // Model selection
  models_used: {
    stage_1: string; // Model ID used for Stage 1
    stage_2: string;
    stage_3: string;
    stage_4: string;
    stage_5: string;
  };

  // Cost tracking
  estimated_cost_usd: number | null;
  actual_cost_usd: number | null;
  per_stage_costs: {
    stage_1: number;
    stage_2: number;
    stage_3: number;
    stage_4: number;
    stage_5: number;
  } | null;

  // Progress tracking
  current_stage: number; // 1-5
  stage_outputs: {
    stage_1_path: string | null; // Blob storage path
    stage_2_path: string | null;
    stage_3_path: string | null;
    stage_4_path: string | null;
    stage_5_path: string | null; // Final opportunity cards
  };

  // Metadata
  created_at: Date;
  updated_at: Date;
  completed_at: Date | null;
  error_message: string | null;
}

// Prompt Configuration (Reusable Template)
interface PromptConfiguration {
  id: string; // UUID
  name: string; // User-defined name
  description: string | null;

  // Stage prompts
  stage_1_prompt: string;
  stage_2_prompt: string;
  stage_3_prompt: string;
  stage_4_prompt: string;
  stage_5_prompt: string;

  // Model selection
  default_model_id: string; // Default model for all stages
  stage_model_overrides: {
    stage_1?: string; // Optional per-stage overrides
    stage_2?: string;
    stage_3?: string;
    stage_4?: string;
    stage_5?: string;
  };

  // Metadata
  created_at: Date;
  updated_at: Date;
  is_default: boolean; // Mark as default configuration
}

// Brand Profile (Metadata Only)
interface BrandProfile {
  id: string; // e.g., "lactalis-canada"
  display_name: string; // "Lactalis Canada"
  industry: string;
  research_file_path: string; // Blob storage path to research markdown
  last_updated: Date;
}

// Input Document (Innovation Trend/Signal)
interface InputDocument {
  id: string; // e.g., "sustainable-packaging-trends"
  title: string;
  description: string;
  source: string; // URL or document source
  content_path: string; // Blob storage path
  created_at: Date;
}

// Stage Output (Intermediate Results)
interface StageOutput {
  run_id: string; // FK to TestRun
  stage: number; // 1-5
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  duration_ms: number;
  model_id: string;
  output_path: string; // Blob storage path
  created_at: Date;
}

// Opportunity Card (Final Output)
interface OpportunityCard {
  run_id: string; // FK to TestRun
  opportunity_number: number; // 1-5
  title: string;
  strategic_rationale: string;
  implementation_approach: string;
  success_metrics: string;
  risks_and_mitigations: string;
  estimated_timeline: string;
  estimated_investment: string;
  markdown_path: string; // Blob storage path
  created_at: Date;
}

// Research Data (Loaded from Blob)
interface ResearchData {
  brand_id: string;
  sections: {
    brand_overview: ResearchSection;
    product_portfolio: ResearchSection;
    recent_innovations: ResearchSection; // CRITICAL for Stage 4
    strategic_priorities: ResearchSection;
    target_customers: ResearchSection;
    sustainability: ResearchSection;
    competitive_context: ResearchSection;
    recent_news: ResearchSection;
  };
  key_insights: {
    innovation_dna: string;
    strategic_north_star: string;
    opportunity_whitespace: string;
  };
  total_data_points: number; // Target: 120+
  research_date: Date;
}

interface ResearchSection {
  title: string;
  content: string; // Markdown content
  data_points: number;
}
```

### Cost Estimation Model

```typescript
interface CostEstimation {
  total_cost_usd: number;
  per_stage_costs: {
    stage_1: number;
    stage_2: number;
    stage_3: number;
    stage_4: number;
    stage_5: number;
  };
  breakdown: Array<{
    stage: number;
    model_id: string;
    estimated_input_tokens: number;
    estimated_output_tokens: number;
    cost_usd: number;
  }>;
}
```

---

## 5. API Specification

### REST API Endpoints

**Base URL**: `https://pipeline.yourdomain.com/api`

#### 1. Execute Pipeline Test

```http
POST /api/pipeline/execute
Content-Type: application/json
Authorization: Bearer {token}

{
  "input_id": "sustainable-packaging-trends",
  "brand_id": "lactalis-canada",
  "prompt_config_id": "config-123"
}
```

**Response** (202 Accepted):
```json
{
  "run_id": "run-abc-123",
  "status": "pending",
  "estimated_cost_usd": 0.42,
  "models_used": {
    "stage_1": "deepseek/deepseek-chat",
    "stage_2": "deepseek/deepseek-chat",
    "stage_3": "deepseek/deepseek-chat",
    "stage_4": "anthropic/claude-sonnet-4-20250514",
    "stage_5": "deepseek/deepseek-chat"
  }
}
```

#### 2. Get Pipeline Status (Polling)

```http
GET /api/pipeline/status/{runId}
```

**Response** (200 OK):
```json
{
  "run_id": "run-abc-123",
  "status": "running",
  "current_stage": 3,
  "progress_percentage": 60,
  "models_used": { /* ... */ },
  "estimated_cost_usd": 0.42,
  "actual_cost_usd": 0.18,
  "per_stage_costs": {
    "stage_1": 0.05,
    "stage_2": 0.06,
    "stage_3": 0.07,
    "stage_4": null,
    "stage_5": null
  },
  "error_message": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

**Response when completed**:
```json
{
  "run_id": "run-abc-123",
  "status": "completed",
  "current_stage": 5,
  "progress_percentage": 100,
  "actual_cost_usd": 0.38,
  "per_stage_costs": {
    "stage_1": 0.05,
    "stage_2": 0.06,
    "stage_3": 0.07,
    "stage_4": 0.15,
    "stage_5": 0.05
  },
  "opportunities": [
    {
      "number": 1,
      "title": "Plant-Based Dairy Line Extension",
      "markdown_url": "https://blob.vercel-storage.com/runs/run-abc-123/opportunity_1.md"
    },
    // ... 4 more opportunities
  ],
  "completed_at": "2025-01-15T10:40:00Z"
}
```

#### 3. Get Run Results

```http
GET /api/pipeline/results/{runId}
```

**Response** (200 OK):
```json
{
  "run_id": "run-abc-123",
  "input": {
    "id": "sustainable-packaging-trends",
    "title": "Sustainable Packaging Innovations 2025"
  },
  "brand": {
    "id": "lactalis-canada",
    "display_name": "Lactalis Canada"
  },
  "opportunities": [
    {
      "number": 1,
      "title": "Plant-Based Dairy Line Extension",
      "strategic_rationale": "...",
      "implementation_approach": "...",
      "success_metrics": "...",
      "risks_and_mitigations": "...",
      "estimated_timeline": "12-18 months",
      "estimated_investment": "$2-5M",
      "markdown_content": "# Opportunity #1\n\n..."
    }
    // ... 4 more
  ],
  "metadata": {
    "actual_cost_usd": 0.38,
    "models_used": { /* ... */ },
    "completed_at": "2025-01-15T10:40:00Z"
  }
}
```

#### 4. Save Prompt Configuration

```http
POST /api/prompts
Content-Type: application/json

{
  "name": "V2 - Enhanced Brand Context",
  "description": "Uses longer prompts for Stage 4 with explicit research dimensions",
  "stage_1_prompt": "Extract key insights from this innovation trend...",
  "stage_2_prompt": "Amplify weak signals by...",
  "stage_3_prompt": "Translate into general strategic concepts...",
  "stage_4_prompt": "Contextualize for {brand_name} using:\n\n## Recent Innovations\n{recent_innovations}\n\n...",
  "stage_5_prompt": "Generate exactly 5 opportunity cards...",
  "default_model_id": "deepseek/deepseek-chat",
  "stage_model_overrides": {
    "stage_4": "anthropic/claude-sonnet-4-20250514"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "config-456",
  "name": "V2 - Enhanced Brand Context",
  "created_at": "2025-01-15T11:00:00Z"
}
```

#### 5. Get Prompt Configuration

```http
GET /api/prompts/{configId}
```

**Response** (200 OK):
```json
{
  "id": "config-456",
  "name": "V2 - Enhanced Brand Context",
  "description": "...",
  "stage_1_prompt": "...",
  // ... all prompts
  "default_model_id": "deepseek/deepseek-chat",
  "stage_model_overrides": { /* ... */ },
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

#### 6. Cost Estimation

```http
POST /api/cost-estimate
Content-Type: application/json

{
  "model_id": "deepseek/deepseek-chat",
  "stage_model_overrides": {
    "stage_4": "anthropic/claude-sonnet-4-20250514"
  },
  "num_runs": 10
}
```

**Response** (200 OK):
```json
{
  "total_cost_usd": 4.20,
  "cost_per_run": 0.42,
  "per_stage_costs": {
    "stage_1": 0.05,
    "stage_2": 0.06,
    "stage_3": 0.07,
    "stage_4": 0.19,
    "stage_5": 0.05
  },
  "breakdown": [
    {
      "stage": 1,
      "model_id": "deepseek/deepseek-chat",
      "estimated_input_tokens": 5000,
      "estimated_output_tokens": 2000,
      "cost_usd": 0.05
    }
    // ... stages 2-5
  ]
}
```

#### 7. Compare Opportunities Across Brands

```http
POST /api/comparison
Content-Type: application/json

{
  "input_id": "sustainable-packaging-trends",
  "brand_ids": ["lactalis-canada", "mccormick-usa"],
  "prompt_config_id": "config-456"
}
```

**Response** (200 OK):
```json
{
  "input": {
    "id": "sustainable-packaging-trends",
    "title": "Sustainable Packaging Innovations 2025"
  },
  "comparisons": [
    {
      "brand_id": "lactalis-canada",
      "brand_name": "Lactalis Canada",
      "run_id": "run-xyz-789",
      "status": "completed",
      "opportunities": [ /* 5 opportunities */ ],
      "actual_cost_usd": 0.38
    },
    {
      "brand_id": "mccormick-usa",
      "brand_name": "McCormick USA",
      "run_id": "run-xyz-790",
      "status": "completed",
      "opportunities": [ /* 5 opportunities */ ],
      "actual_cost_usd": 0.41
    }
  ]
}
```

#### 8. Get Brand Research Data

```http
GET /api/brands/{brandId}/research
```

**Response** (200 OK):
```json
{
  "brand_id": "lactalis-canada",
  "display_name": "Lactalis Canada",
  "sections": {
    "brand_overview": {
      "title": "Brand Overview & Positioning",
      "content": "...",
      "data_points": 18
    },
    "recent_innovations": {
      "title": "Recent Innovations (Last 18 Months)",
      "content": "...",
      "data_points": 22
    }
    // ... 6 more sections
  },
  "key_insights": {
    "innovation_dna": "Lactalis focuses on product innovation...",
    "strategic_north_star": "Growth through premium positioning...",
    "opportunity_whitespace": "Limited presence in plant-based alternatives..."
  },
  "total_data_points": 127,
  "research_date": "2025-01-15T00:00:00Z"
}
```

---

*(Continued in next section...)*

## 6. Components

### Frontend Component Architecture

**Next.js 14 App Router Structure**:

```
apps/web/src/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout with providers
│   ├── page.tsx                  # Homepage
│   ├── prompts/
│   │   ├── page.tsx              # List prompt configurations (RSC)
│   │   ├── new/page.tsx          # Create new prompt (Client Component)
│   │   └── [id]/
│   │       ├── page.tsx          # View/edit prompt (Client Component)
│   │       └── run/page.tsx      # Execute test from this config
│   ├── run/
│   │   └── page.tsx              # Execute new test run (Client Component)
│   ├── results/
│   │   └── [runId]/
│   │       └── page.tsx          # View test results (RSC)
│   ├── comparison/
│   │   └── page.tsx              # Side-by-side brand comparison (Client Component)
│   └── api/
│       ├── pipeline/
│       │   ├── execute/route.ts
│       │   ├── status/[runId]/route.ts
│       │   └── results/[runId]/route.ts
│       ├── prompts/
│       │   ├── route.ts
│       │   └── [id]/route.ts
│       ├── cost-estimate/route.ts
│       ├── comparison/route.ts
│       └── brands/
│           └── [brandId]/
│               └── research/route.ts
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── tabs.tsx
│   │   └── ... (30+ components)
│   ├── prompt-editor/
│   │   ├── PromptEditor.tsx      # Monaco editor wrapper
│   │   ├── ModelSelector.tsx     # Model dropdown with pricing
│   │   ├── CostEstimator.tsx     # Real-time cost calculation
│   │   └── PromptTabs.tsx        # 5-stage tab interface
│   ├── test-execution/
│   │   ├── ExecutionMonitor.tsx  # Real-time progress tracker
│   │   ├── StageProgress.tsx     # Individual stage status
│   │   └── CostTracker.tsx       # Live cost accumulation
│   └── results/
│       ├── OpportunityCard.tsx   # Single opportunity display
│       ├── OpportunityGrid.tsx   # 5-card grid layout
│       └── ComparisonView.tsx    # Side-by-side brand comparison
├── lib/
│   ├── api-client.ts             # API wrapper class
│   ├── cost-estimator.ts         # Cost calculation logic
│   ├── models.ts                 # LLM model configurations
│   ├── db.ts                     # Drizzle client
│   └── blob-client.ts            # Vercel Blob wrapper
└── stores/
    ├── prompt-editor-store.ts    # Zustand: prompt drafts
    └── execution-store.ts        # Zustand: polling state
```

### Key Components

#### 1. PromptEditor Component

```typescript
// components/prompt-editor/PromptEditor.tsx
'use client';

import Editor from '@monaco-editor/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ModelSelector } from './ModelSelector';
import { CostEstimator } from './CostEstimator';

interface PromptEditorProps {
  initialConfig?: PromptConfiguration;
  onSave: (config: PromptConfiguration) => Promise<void>;
}

export function PromptEditor({ initialConfig, onSave }: PromptEditorProps) {
  const [config, setConfig] = useState(initialConfig || getDefaultConfig());
  const [activeStage, setActiveStage] = useState(1);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Prompt Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={`stage-${activeStage}`} onValueChange={(v) => setActiveStage(Number(v.split('-')[1]))}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="stage-1">Stage 1</TabsTrigger>
              <TabsTrigger value="stage-2">Stage 2</TabsTrigger>
              <TabsTrigger value="stage-3">Stage 3</TabsTrigger>
              <TabsTrigger value="stage-4">Stage 4</TabsTrigger>
              <TabsTrigger value="stage-5">Stage 5</TabsTrigger>
            </TabsList>

            {[1, 2, 3, 4, 5].map((stage) => (
              <TabsContent key={stage} value={`stage-${stage}`}>
                <div className="space-y-4">
                  <Editor
                    height="400px"
                    language="markdown"
                    theme="vs-dark"
                    value={config[`stage_${stage}_prompt`]}
                    onChange={(value) =>
                      setConfig({ ...config, [`stage_${stage}_prompt`]: value || '' })
                    }
                    options={{
                      minimap: { enabled: false },
                      fontSize: 14,
                      wordWrap: 'on',
                    }}
                  />

                  <ModelSelector
                    value={config.stage_model_overrides?.[`stage_${stage}`] || config.default_model_id}
                    onChange={(modelId) => {
                      setConfig({
                        ...config,
                        stage_model_overrides: {
                          ...config.stage_model_overrides,
                          [`stage_${stage}`]: modelId,
                        },
                      });
                    }}
                  />
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      <CostEstimator config={config} />

      <Button onClick={() => onSave(config)}>Save Configuration</Button>
    </div>
  );
}
```

#### 2. ExecutionMonitor Component

```typescript
// components/test-execution/ExecutionMonitor.tsx
'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { ApiClient } from '@/lib/api-client';

interface ExecutionMonitorProps {
  runId: string;
  onComplete: (results: TestRun) => void;
}

export function ExecutionMonitor({ runId, onComplete }: ExecutionMonitorProps) {
  const [status, setStatus] = useState<TestRun | null>(null);
  const client = new ApiClient();

  useEffect(() => {
    const pollStatus = async () => {
      const result = await client.getStatus(runId);
      setStatus(result);

      if (result.status === 'completed' || result.status === 'failed') {
        onComplete(result);
      }
    };

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);
    pollStatus(); // Initial fetch

    return () => clearInterval(interval);
  }, [runId]);

  if (!status) return <Loader2 className="animate-spin" />;

  const stages = [
    { number: 1, name: 'Input Processing' },
    { number: 2, name: 'Signal Amplification' },
    { number: 3, name: 'General Translation' },
    { number: 4, name: 'Brand Contextualization' },
    { number: 5, name: 'Opportunity Generation' },
  ];

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-6">
          <Progress value={status.progress_percentage} />

          <div className="space-y-2">
            {stages.map((stage) => {
              const isComplete = stage.number < status.current_stage;
              const isActive = stage.number === status.current_stage;

              return (
                <div key={stage.number} className="flex items-center gap-3">
                  {isComplete ? (
                    <CheckCircle2 className="text-green-500" />
                  ) : isActive ? (
                    <Loader2 className="animate-spin text-blue-500" />
                  ) : (
                    <Circle className="text-gray-400" />
                  )}

                  <span className={isComplete || isActive ? 'font-medium' : 'text-gray-500'}>
                    Stage {stage.number}: {stage.name}
                  </span>

                  {isComplete && status.per_stage_costs?.[`stage_${stage.number}`] && (
                    <span className="ml-auto text-sm text-gray-600">
                      ${status.per_stage_costs[`stage_${stage.number}`].toFixed(3)}
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          <div className="border-t pt-4">
            <div className="flex justify-between text-sm">
              <span>Total Cost</span>
              <span className="font-mono">
                ${status.actual_cost_usd?.toFixed(3) || '0.000'} / ${status.estimated_cost_usd.toFixed(3)}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

#### 3. API Client

```typescript
// lib/api-client.ts
export class ApiClient {
  private baseUrl = '/api';

  async executeTest(params: {
    input_id: string;
    brand_id: string;
    prompt_config_id: string;
  }): Promise<{ run_id: string }> {
    const response = await fetch(`${this.baseUrl}/pipeline/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async getStatus(runId: string): Promise<TestRun> {
    const response = await fetch(`${this.baseUrl}/pipeline/status/${runId}`);

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async getResults(runId: string): Promise<{
    run_id: string;
    opportunities: OpportunityCard[];
    metadata: any;
  }> {
    const response = await fetch(`${this.baseUrl}/pipeline/results/${runId}`);

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async savePromptConfig(config: Omit<PromptConfiguration, 'id' | 'created_at' | 'updated_at'>): Promise<{ id: string }> {
    const response = await fetch(`${this.baseUrl}/prompts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async estimateCost(params: {
    model_id: string;
    stage_model_overrides?: Record<string, string>;
    num_runs?: number;
  }): Promise<CostEstimation> {
    const response = await fetch(`${this.baseUrl}/cost-estimate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }
}
```

---

## 7. Database Schema

### PostgreSQL Tables (Drizzle ORM)

```typescript
// db/schema.ts
import { pgTable, uuid, varchar, text, jsonb, timestamp, integer, numeric, boolean } from 'drizzle-orm/pg-core';

export const testRuns = pgTable('test_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  status: varchar('status', { length: 20 }).notNull(), // pending, running, completed, failed

  // Foreign keys
  inputId: varchar('input_id', { length: 100 }).notNull(),
  brandId: varchar('brand_id', { length: 100 }).notNull(),
  promptConfigId: uuid('prompt_config_id').notNull(),

  // Model selection
  modelsUsed: jsonb('models_used').notNull(), // { stage_1: string, ..., stage_5: string }

  // Cost tracking
  estimatedCostUsd: numeric('estimated_cost_usd', { precision: 10, scale: 4 }),
  actualCostUsd: numeric('actual_cost_usd', { precision: 10, scale: 4 }),
  perStageCosts: jsonb('per_stage_costs'), // { stage_1: number, ..., stage_5: number }

  // Progress
  currentStage: integer('current_stage').default(0),
  stageOutputs: jsonb('stage_outputs').default('{}'), // { stage_1_path: string, ... }

  // Metadata
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
  errorMessage: text('error_message'),
});

export const promptConfigurations = pgTable('prompt_configurations', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: varchar('name', { length: 255 }).notNull(),
  description: text('description'),

  // Stage prompts
  stage1Prompt: text('stage_1_prompt').notNull(),
  stage2Prompt: text('stage_2_prompt').notNull(),
  stage3Prompt: text('stage_3_prompt').notNull(),
  stage4Prompt: text('stage_4_prompt').notNull(),
  stage5Prompt: text('stage_5_prompt').notNull(),

  // Model selection
  defaultModelId: varchar('default_model_id', { length: 100 }).notNull(),
  stageModelOverrides: jsonb('stage_model_overrides').default('{}'),

  // Metadata
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  isDefault: boolean('is_default').default(false),
});

export const brandProfiles = pgTable('brand_profiles', {
  id: varchar('id', { length: 100 }).primaryKey(), // e.g., "lactalis-canada"
  displayName: varchar('display_name', { length: 255 }).notNull(),
  industry: varchar('industry', { length: 100 }),
  researchFilePath: text('research_file_path').notNull(), // Blob storage path
  lastUpdated: timestamp('last_updated').defaultNow(),
});

export const inputDocuments = pgTable('input_documents', {
  id: varchar('id', { length: 100 }).primaryKey(),
  title: varchar('title', { length: 255 }).notNull(),
  description: text('description'),
  source: text('source'),
  contentPath: text('content_path').notNull(), // Blob storage path
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const stageOutputs = pgTable('stage_outputs', {
  id: uuid('id').primaryKey().defaultRandom(),
  runId: uuid('run_id').notNull().references(() => testRuns.id),
  stage: integer('stage').notNull(), // 1-5

  // Execution metrics
  inputTokens: integer('input_tokens').notNull(),
  outputTokens: integer('output_tokens').notNull(),
  costUsd: numeric('cost_usd', { precision: 10, scale: 4 }).notNull(),
  durationMs: integer('duration_ms').notNull(),
  modelId: varchar('model_id', { length: 100 }).notNull(),

  // Output
  outputPath: text('output_path').notNull(), // Blob storage path
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const opportunityCards = pgTable('opportunity_cards', {
  id: uuid('id').primaryKey().defaultRandom(),
  runId: uuid('run_id').notNull().references(() => testRuns.id),
  opportunityNumber: integer('opportunity_number').notNull(), // 1-5

  // Content
  title: varchar('title', { length: 255 }).notNull(),
  strategicRationale: text('strategic_rationale').notNull(),
  implementationApproach: text('implementation_approach').notNull(),
  successMetrics: text('success_metrics').notNull(),
  risksAndMitigations: text('risks_and_mitigations').notNull(),
  estimatedTimeline: varchar('estimated_timeline', { length: 100 }),
  estimatedInvestment: varchar('estimated_investment', { length: 100 }),

  // Storage
  markdownPath: text('markdown_path').notNull(), // Blob storage path
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_test_runs_status ON test_runs(status);
CREATE INDEX idx_test_runs_created_at ON test_runs(created_at DESC);
CREATE INDEX idx_test_runs_brand ON test_runs(brand_id);
CREATE INDEX idx_test_runs_input ON test_runs(input_id);
CREATE INDEX idx_stage_outputs_run ON stage_outputs(run_id);
CREATE INDEX idx_opportunity_cards_run ON opportunity_cards(run_id);
CREATE INDEX idx_prompt_configs_default ON prompt_configurations(is_default) WHERE is_default = true;
```

---

## 8. Frontend Architecture

### Next.js 14 App Router Pattern

**Server Components (Default)**:
- `/prompts/page.tsx` - List configurations (fetch from DB)
- `/results/[runId]/page.tsx` - Display results (fetch from Blob + DB)
- Root layouts with static content

**Client Components** (`'use client'`):
- `/prompts/new/page.tsx` - Prompt editor (Monaco requires browser)
- `/run/page.tsx` - Test execution (real-time polling)
- `/comparison/page.tsx` - Brand comparison (interactive UI)
- All components using Zustand stores

### State Management Strategy

**Zustand Store - Prompt Editor**:

```typescript
// stores/prompt-editor-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface PromptEditorState {
  draftConfig: PromptConfiguration | null;
  activeStage: number;

  setDraftConfig: (config: PromptConfiguration) => void;
  updateStagePrompt: (stage: number, prompt: string) => void;
  setActiveStage: (stage: number) => void;
  clearDraft: () => void;
}

export const usePromptEditorStore = create<PromptEditorState>()(
  persist(
    (set) => ({
      draftConfig: null,
      activeStage: 1,

      setDraftConfig: (config) => set({ draftConfig: config }),

      updateStagePrompt: (stage, prompt) =>
        set((state) => ({
          draftConfig: state.draftConfig
            ? {
                ...state.draftConfig,
                [`stage_${stage}_prompt`]: prompt,
              }
            : null,
        })),

      setActiveStage: (stage) => set({ activeStage: stage }),

      clearDraft: () => set({ draftConfig: null }),
    }),
    {
      name: 'prompt-editor-storage',
    }
  )
);
```

**Zustand Store - Execution Polling**:

```typescript
// stores/execution-store.ts
import { create } from 'zustand';

interface ExecutionState {
  activeRuns: Map<string, TestRun>;

  addRun: (runId: string, initialData: TestRun) => void;
  updateRun: (runId: string, data: Partial<TestRun>) => void;
  removeRun: (runId: string) => void;
}

export const useExecutionStore = create<ExecutionState>((set) => ({
  activeRuns: new Map(),

  addRun: (runId, initialData) =>
    set((state) => ({
      activeRuns: new Map(state.activeRuns).set(runId, initialData),
    })),

  updateRun: (runId, data) =>
    set((state) => {
      const newRuns = new Map(state.activeRuns);
      const existing = newRuns.get(runId);
      if (existing) {
        newRuns.set(runId, { ...existing, ...data });
      }
      return { activeRuns: newRuns };
    }),

  removeRun: (runId) =>
    set((state) => {
      const newRuns = new Map(state.activeRuns);
      newRuns.delete(runId);
      return { activeRuns: newRuns };
    }),
}));
```

### Routing Structure

```
/ (homepage)
├── /prompts (list all configurations)
│   ├── /new (create new prompt config)
│   └── /[id] (view/edit existing)
│       └── /run (execute test with this config)
├── /run (quick test execution)
├── /results/[runId] (view test results)
├── /comparison (side-by-side brand comparison)
└── /admin
    └── /costs (cost monitoring dashboard)
```

---

## 9. Backend Architecture

### Python Serverless Functions (Vercel)

**Directory Structure**:

```
api/python/
├── stage1.py                     # Vercel entry point for Stage 1
├── stage2.py                     # Vercel entry point for Stage 2
├── stage3.py                     # Vercel entry point for Stage 3
├── stage4.py                     # Vercel entry point for Stage 4
├── stage5.py                     # Vercel entry point for Stage 5
├── pipeline/
│   ├── stages/
│   │   ├── stage1_input_processing.py
│   │   ├── stage2_signal_amplification.py
│   │   ├── stage3_general_translation.py
│   │   ├── stage4_brand_contextualization.py
│   │   └── stage5_opportunity_generation.py
│   ├── llm_client.py             # OpenRouter ChatOpenAI wrapper
│   ├── blob_client.py            # Vercel Blob SDK wrapper
│   ├── research_loader.py        # Load & parse brand research
│   ├── logger.py                 # Structured logging
│   └── utils.py                  # Retry logic, error handling
├── templates/
│   └── opportunity-card.md.j2    # Jinja2 template
├── requirements.txt
└── tests/
    ├── test_research_loader.py
    ├── test_stage4_brand_contextualization.py
    └── ...
```

### Stage 4: Brand Contextualization (Critical Stage)

**File**: `api/python/pipeline/stages/stage4_brand_contextualization.py`

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pipeline.llm_client import create_llm_client
from pipeline.blob_client import BlobClient
from pipeline.research_loader import ResearchDataLoader
from pipeline.logger import logger
import json

def execute_stage4(
    run_id: str,
    brand_id: str,
    stage3_output_path: str,
    prompt: str,
    llm_config: dict
) -> dict:
    """
    Stage 4: Brand Contextualization

    Injects comprehensive brand research (8 sections, 120+ data points)
    into the prompt to generate brand-specific opportunities.
    """
    logger.stage_start(run_id, stage=4, model=llm_config['model'])

    # Load Stage 3 output (general concepts)
    blob_client = BlobClient()
    stage3_content = blob_client.read(stage3_output_path)
    stage3_data = json.loads(stage3_content)

    # Load comprehensive brand research
    research_loader = ResearchDataLoader()
    research = research_loader.get_brand_research(brand_id)

    # Build research context for prompt injection
    research_context = f"""
## BRAND RESEARCH DATA FOR {research.brand_profile.display_name}

### 1. Brand Overview & Positioning
{research.sections['brand_overview'].content}

### 2. Product Portfolio & Innovation
{research.sections['product_portfolio'].content}

### 3. Recent Innovations (Last 18 Months) ⭐ CRITICAL
{research.sections['recent_innovations'].content}

### 4. Strategic Priorities & Business Strategy
{research.sections['strategic_priorities'].content}

### 5. Target Customers & Market Positioning
{research.sections['target_customers'].content}

### 6. Sustainability & Social Responsibility
{research.sections['sustainability'].content}

### 7. Competitive Context & Market Trends
{research.sections['competitive_context'].content}

### 8. Recent News & Market Signals (Last 6 Months)
{research.sections['recent_news'].content}

---

## KEY INSIGHTS SUMMARY

### Innovation DNA
{research.key_insights.innovation_dna}

### Strategic North Star
{research.key_insights.strategic_north_star}

### Opportunity Whitespace
{research.key_insights.opportunity_whitespace}

---

**Total Research Data Points**: {research.total_data_points}
**Research Date**: {research.research_date.strftime('%Y-%m-%d')}
"""

    # Inject research into prompt template
    prompt_template = PromptTemplate.from_template(prompt)
    formatted_prompt = prompt_template.format(
        brand_name=research.brand_profile.display_name,
        brand_research=research_context,
        general_concepts=json.dumps(stage3_data['general_concepts'], indent=2)
    )

    # Execute LLM
    llm = create_llm_client(llm_config)
    response = llm.invoke(formatted_prompt)

    # Parse response
    contextualized_opportunities = json.loads(response.content)

    # Save output to Blob
    output_path = f"runs/{run_id}/stage4_output.json"
    blob_client.write(
        output_path,
        json.dumps(contextualized_opportunities, indent=2)
    )

    # Log completion and cost
    logger.stage_complete(
        run_id,
        stage=4,
        duration_ms=(time.time() - start_time) * 1000,
        tokens_used=response.usage.total_tokens
    )

    cost_usd = calculate_cost(
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
        llm_config['model']
    )
    logger.cost_incurred(run_id, stage=4, cost_usd=cost_usd, model=llm_config['model'])

    return {
        'output_path': output_path,
        'tokens_used': response.usage.total_tokens,
        'cost_usd': cost_usd,
    }
```

### Research Data Loader

**File**: `api/python/pipeline/research_loader.py`

```python
import re
from dataclasses import dataclass
from typing import Dict
from datetime import datetime
from pipeline.blob_client import BlobClient

@dataclass
class ResearchSection:
    title: str
    content: str
    data_points: int

@dataclass
class BrandResearch:
    brand_id: str
    brand_profile: any  # BrandProfile from DB
    sections: Dict[str, ResearchSection]
    key_insights: Dict[str, str]
    total_data_points: int
    research_date: datetime

class ResearchDataLoader:
    """Loads and parses comprehensive brand research files from Blob storage."""

    SECTION_MAP = {
        "1. Brand Overview & Positioning": "brand_overview",
        "2. Product Portfolio & Innovation": "product_portfolio",
        "3. Recent Innovations (Last 18 Months)": "recent_innovations",
        "4. Strategic Priorities & Business Strategy": "strategic_priorities",
        "5. Target Customers & Market Positioning": "target_customers",
        "6. Sustainability & Social Responsibility": "sustainability",
        "7. Competitive Context & Market Trends": "competitive_context",
        "8. Recent News & Market Signals (Last 6 Months)": "recent_news",
    }

    def __init__(self):
        self.blob_client = BlobClient()
        self._cache = {}  # Cache loaded research

    def get_brand_research(self, brand_id: str) -> BrandResearch:
        """Load brand research from Blob storage with caching."""
        if brand_id in self._cache:
            return self._cache[brand_id]

        # Load brand profile from DB
        brand_profile = get_brand_profile(brand_id)  # From DB

        # Load research file from Blob
        research_content = self.blob_client.read(brand_profile.research_file_path)

        # Parse markdown
        research = self._parse_research_file(research_content, brand_id)
        research.brand_profile = brand_profile

        # Cache
        self._cache[brand_id] = research

        return research

    def _parse_research_file(self, content: str, brand_id: str) -> BrandResearch:
        """Parse research markdown into structured data."""
        sections = {}
        key_insights = {}

        # Extract metadata
        research_date_match = re.search(r'\*\*Research Date:\*\* (\d{4}-\d{2}-\d{2})', content)
        research_date = datetime.strptime(research_date_match.group(1), '%Y-%m-%d') if research_date_match else datetime.now()

        # Extract sections
        for section_title, section_key in self.SECTION_MAP.items():
            pattern = rf'## {re.escape(section_title)}(.*?)(?=##|\Z)'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                section_content = match.group(1).strip()
                data_points = self._count_data_points(section_content)

                sections[section_key] = ResearchSection(
                    title=section_title,
                    content=section_content,
                    data_points=data_points
                )

        # Extract key insights
        insights_pattern = r'## Key Insights Summary.*?### Innovation DNA\n(.*?)\n\n### Strategic North Star\n(.*?)\n\n### Opportunity Whitespace\n(.*?)\n'
        insights_match = re.search(insights_pattern, content, re.DOTALL)

        if insights_match:
            key_insights = {
                'innovation_dna': insights_match.group(1).strip(),
                'strategic_north_star': insights_match.group(2).strip(),
                'opportunity_whitespace': insights_match.group(3).strip(),
            }

        total_data_points = sum(s.data_points for s in sections.values())

        return BrandResearch(
            brand_id=brand_id,
            brand_profile=None,  # Will be set by caller
            sections=sections,
            key_insights=key_insights,
            total_data_points=total_data_points,
            research_date=research_date
        )

    def _count_data_points(self, content: str) -> int:
        """Estimate data points by counting bullet points and sub-items."""
        bullets = len(re.findall(r'^[\-\*]\s', content, re.MULTILINE))
        numbered = len(re.findall(r'^\d+\.\s', content, re.MULTILINE))
        return bullets + numbered
```

### LLM Client Wrapper

**File**: `api/python/pipeline/llm_client.py`

```python
from langchain_openai import ChatOpenAI
import os

def create_llm_client(llm_config: dict) -> ChatOpenAI:
    """
    Create LangChain ChatOpenAI client configured for OpenRouter.

    Args:
        llm_config: {
            'model': 'anthropic/claude-sonnet-4-20250514',
            'temperature': 0.5
        }
    """
    return ChatOpenAI(
        model=llm_config['model'],
        temperature=llm_config.get('temperature', 0.5),
        openai_api_key=os.getenv('OPENROUTER_API_KEY'),
        openai_api_base='https://openrouter.ai/api/v1',
        default_headers={
            'HTTP-Referer': os.getenv('APP_URL', 'https://pipeline.yourdomain.com'),
            'X-Title': 'Innovation Intelligence Pipeline'
        }
    )
```

---

## 10. Deployment Architecture

### Vercel Configuration

**File**: `vercel.json`

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "functions": {
    "api/python/**/*.py": {
      "runtime": "python3.11",
      "maxDuration": 300,
      "memory": 1024
    }
  },
  "env": {
    "OPENROUTER_API_KEY": "@openrouter-api-key",
    "BLOB_READ_WRITE_TOKEN": "@blob-read-write-token",
    "POSTGRES_URL": "@postgres-url"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_APP_URL": "https://pipeline.yourdomain.com"
    }
  }
}
```

### Environment Variables

```bash
# Required for all environments (Development, Preview, Production)

# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Vercel Blob Storage
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_xxxxx

# Vercel Postgres
POSTGRES_URL=postgres://default:xxxxx@xxxxx-pooler.us-east-1.postgres.vercel-storage.com/verceldb
POSTGRES_PRISMA_URL=postgres://default:xxxxx@xxxxx-pooler.us-east-1.postgres.vercel-storage.com/verceldb?pgbouncer=true&connect_timeout=15
POSTGRES_URL_NON_POOLING=postgres://default:xxxxx@xxxxx.us-east-1.postgres.vercel-storage.com/verceldb

# Application URL (for OpenRouter HTTP-Referer header)
NEXT_PUBLIC_APP_URL=https://pipeline.yourdomain.com

# Monitoring (optional)
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
AXIOM_TOKEN=xxxxx
```

### Python Requirements

**File**: `api/python/requirements.txt`

```txt
# LangChain ecosystem
langchain==0.1.0
langchain-openai==0.0.5
langchain-core==0.1.10

# OpenAI SDK (required by langchain-openai)
openai==1.10.0

# Vercel integrations
vercel-blob==0.2.0

# Templating and validation
jinja2==3.1.3
pydantic==2.5.3

# Utilities
requests==2.31.0
```

### CI/CD Pipeline

**File**: `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npm run test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/coverage-final.json

  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - run: pip install -r api/python/requirements.txt
      - run: pip install pytest pytest-cov pytest-asyncio
      - run: pytest api/python/tests --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - run: npm ci
      - run: npx playwright install --with-deps

      - run: npm run build
      - run: npm run test:e2e
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY_TEST }}
          BLOB_READ_WRITE_TOKEN: ${{ secrets.BLOB_TOKEN_TEST }}
          POSTGRES_URL: ${{ secrets.POSTGRES_URL_TEST }}

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 11. Testing Strategy

### Test Pyramid

```
        ┌─────────────────┐
        │   E2E Tests     │  20% - Critical user journeys
        │   (Playwright)   │
        ├─────────────────┤
        │ Integration Tests│  30% - API + DB + Blob
        │  (Vitest + MSW)  │
        ├─────────────────┤
        │   Unit Tests     │  50% - Business logic
        │     (Vitest)     │
        └─────────────────┘
```

### Frontend Unit Tests

**File**: `apps/web/__tests__/lib/cost-estimator.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { estimateCost } from '@/lib/cost-estimator';

describe('Cost Estimator', () => {
  it('calculates cost for single model across all stages', () => {
    const result = estimateCost({
      model_id: 'deepseek/deepseek-chat',
      num_runs: 1,
    });

    expect(result.total_cost_usd).toBeGreaterThan(0);
    expect(result.per_stage_costs.stage_1).toBeGreaterThan(0);
    expect(result.breakdown).toHaveLength(5);
  });

  it('applies per-stage model overrides correctly', () => {
    const result = estimateCost({
      model_id: 'deepseek/deepseek-chat',
      stage_model_overrides: {
        stage_4: 'anthropic/claude-sonnet-4-20250514',
      },
      num_runs: 1,
    });

    expect(result.per_stage_costs.stage_4).toBeGreaterThan(
      result.per_stage_costs.stage_1
    );
  });
});
```

### Backend Unit Tests

**File**: `api/python/tests/test_research_loader.py`

```python
import pytest
from pipeline.research_loader import ResearchDataLoader

def test_parse_research_file_success(sample_research_markdown, tmp_path):
    research_file = tmp_path / "lactalis-canada-research.md"
    research_file.write_text(sample_research_markdown)

    loader = ResearchDataLoader()
    result = loader._parse_research_file(str(research_file), "lactalis-canada")

    assert result.brand_id == "lactalis-canada"
    assert len(result.sections) == 8
    assert result.total_data_points > 0
```

### E2E Tests

**File**: `apps/web/e2e/prompt-editing-workflow.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('user can create, save, and execute prompt configuration', async ({ page }) => {
  await page.goto('/prompts/new');

  // Edit Stage 1 prompt
  await page.getByRole('tab', { name: 'Stage 1' }).click();
  await page.getByRole('textbox').fill('Extract key insights...');

  // Save configuration
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText(/saved successfully/i)).toBeVisible();

  // Execute test
  await page.getByRole('button', { name: 'Run Test' }).click();
  await expect(page.getByText(/Completed/i)).toBeVisible({ timeout: 300000 });
});
```

---

## 12. Monitoring and Observability

### Logging Strategy

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

### Cost Monitoring Dashboard

**File**: `apps/web/app/admin/costs/page.tsx`

Displays:
- Daily/monthly spend vs. budget
- Cost per run average
- Most expensive stage identification
- Cost breakdown by model
- Daily cost trend chart

### Health Check Endpoint

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

### Key Metrics & Thresholds

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Daily LLM Cost | <$10 | $10-$15 | >$15 |
| Pipeline Success Rate | >95% | 90-95% | <90% |
| Avg Stage Duration | <60s | 60-120s | >120s |
| API Response Time (p95) | <2s | 2-5s | >5s |
| Error Rate | <1% | 1-5% | >5% |

---

## 13. Coding Standards

### Overview

Coding standards ensure consistency, maintainability, and quality across the fullstack application. These standards apply to both TypeScript/JavaScript (frontend) and Python (backend) codebases.

---

### TypeScript/JavaScript Standards

#### File Organization

```typescript
// Standard file structure for components
// components/prompt-editor/PromptEditor.tsx

'use client'; // Only if Client Component

import { useState } from 'react'; // React imports first
import { Card } from '@/components/ui/card'; // Internal UI components
import { ApiClient } from '@/lib/api-client'; // Libraries
import type { PromptConfiguration } from '@/types'; // Types last

interface PromptEditorProps { // Props interface before component
  config: PromptConfiguration;
  onSave: (config: PromptConfiguration) => Promise<void>;
}

export function PromptEditor({ config, onSave }: PromptEditorProps) {
  // Component implementation
}
```

#### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Components | PascalCase | `PromptEditor`, `ExecutionMonitor` |
| Hooks | camelCase with `use` prefix | `usePromptEditor`, `useExecutionStore` |
| Utilities | camelCase | `estimateCost`, `formatCurrency` |
| Constants | SCREAMING_SNAKE_CASE | `AVAILABLE_MODELS`, `MAX_RETRIES` |
| Types/Interfaces | PascalCase | `TestRun`, `PromptConfiguration` |
| Files | kebab-case | `prompt-editor.tsx`, `cost-estimator.ts` |

#### TypeScript Best Practices

```typescript
// ✅ Good: Explicit return types for functions
export function estimateCost(params: CostParams): CostEstimation {
  // ...
}

// ❌ Bad: Implicit return type
export function estimateCost(params: CostParams) {
  // ...
}

// ✅ Good: Avoid `any`, use `unknown` if truly dynamic
function processData(data: unknown): void {
  if (typeof data === 'string') {
    // Type narrowing
  }
}

// ❌ Bad: Using `any`
function processData(data: any): void {
  // ...
}

// ✅ Good: Prefer interfaces over types for object shapes
interface User {
  id: string;
  name: string;
}

// ✅ Good: Use types for unions/aliases
type Status = 'pending' | 'running' | 'completed' | 'failed';

// ✅ Good: Exhaustive switch statements
function handleStatus(status: Status): string {
  switch (status) {
    case 'pending':
      return 'Waiting to start';
    case 'running':
      return 'In progress';
    case 'completed':
      return 'Done';
    case 'failed':
      return 'Error occurred';
    default:
      const _exhaustive: never = status;
      throw new Error(`Unhandled status: ${_exhaustive}`);
  }
}
```

#### React Patterns

```typescript
// ✅ Good: Use Server Components by default
export default async function ResultsPage({ params }: { params: { runId: string } }) {
  const results = await getResults(params.runId); // Server-side fetch
  return <OpportunityGrid opportunities={results.opportunities} />;
}

// ✅ Good: Client Components only when needed
'use client';

export function ExecutionMonitor({ runId }: { runId: string }) {
  const [status, setStatus] = useState<TestRun | null>(null);
  // Real-time polling requires client-side state
}

// ✅ Good: Extract complex logic to custom hooks
function useExecutionPolling(runId: string) {
  const [status, setStatus] = useState<TestRun | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const poll = async () => {
      try {
        const result = await api.getStatus(runId);
        setStatus(result);
      } catch (err) {
        setError(err as Error);
      }
    };

    const interval = setInterval(poll, 2000);
    poll();

    return () => clearInterval(interval);
  }, [runId]);

  return { status, error };
}

// ✅ Good: Memoize expensive computations
const expensiveCalculation = useMemo(() => {
  return opportunities.map(opp => calculateROI(opp));
}, [opportunities]);
```

#### Error Handling

```typescript
// ✅ Good: Type-safe error handling
try {
  await api.executeTest(params);
} catch (error) {
  if (error instanceof ApiError) {
    logger.error('API request failed', { code: error.code, message: error.message });
  } else if (error instanceof Error) {
    logger.error('Unexpected error', { message: error.message });
  } else {
    logger.error('Unknown error', { error });
  }
}

// ✅ Good: Custom error classes
class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// ✅ Good: Result types for expected failures
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function validatePrompt(prompt: string): Result<string, ValidationError> {
  if (prompt.length === 0) {
    return { success: false, error: new ValidationError('Prompt cannot be empty') };
  }
  return { success: true, data: prompt };
}
```

---

### Python Standards

#### File Organization

```python
# pipeline/stages/stage4_brand_contextualization.py

"""
Stage 4: Brand Contextualization

Injects comprehensive brand research into general opportunities
to create brand-specific innovation insights.
"""

# Standard library imports
import json
import time
from typing import Dict, Any

# Third-party imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Local imports
from pipeline.llm_client import create_llm_client
from pipeline.blob_client import BlobClient
from pipeline.research_loader import ResearchDataLoader
from pipeline.logger import logger


def execute_stage4(
    run_id: str,
    brand_id: str,
    stage3_output_path: str,
    prompt: str,
    llm_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute Stage 4 of the pipeline."""
    # Implementation
```

#### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Functions | snake_case | `execute_stage4`, `load_research` |
| Classes | PascalCase | `ResearchDataLoader`, `BlobClient` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `SECTION_MAP` |
| Private methods | _leading_underscore | `_parse_markdown`, `_count_data_points` |
| Files | snake_case | `stage4_brand_contextualization.py` |

#### Type Hints

```python
# ✅ Good: Use type hints for all function signatures
from typing import Dict, List, Optional, Any

def execute_stage(
    run_id: str,
    input_data: Dict[str, Any],
    llm_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute pipeline stage with full type hints."""
    pass

# ✅ Good: Use dataclasses for structured data
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ResearchSection:
    title: str
    content: str
    data_points: int

@dataclass
class BrandResearch:
    brand_id: str
    sections: Dict[str, ResearchSection]
    research_date: datetime
    total_data_points: int

# ✅ Good: Use Optional for nullable values
def load_cache(key: str) -> Optional[Dict[str, Any]]:
    cache = get_cache()
    return cache.get(key)  # Returns None if not found
```

#### Error Handling

```python
# ✅ Good: Specific exception types
class ResearchNotFoundError(Exception):
    """Raised when brand research file is not found."""
    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        super().__init__(f"Research not found for brand: {brand_id}")

class StageExecutionError(Exception):
    """Raised when a pipeline stage fails."""
    def __init__(self, stage: int, reason: str):
        self.stage = stage
        self.reason = reason
        super().__init__(f"Stage {stage} failed: {reason}")

# ✅ Good: Try-except with specific handling
def execute_stage(run_id: str, config: dict) -> dict:
    try:
        result = process_data(config)
        return result
    except ResearchNotFoundError as e:
        logger.error(f"Missing research data", brand_id=e.brand_id)
        raise
    except LLMTimeoutError as e:
        logger.error(f"LLM request timed out", timeout=e.timeout)
        raise StageExecutionError(stage=4, reason="LLM timeout")
    except Exception as e:
        logger.error(f"Unexpected error in stage execution", error=str(e))
        raise

# ✅ Good: Context managers for cleanup
from contextlib import contextmanager

@contextmanager
def stage_execution_context(run_id: str, stage: int):
    """Context manager for stage execution with automatic cleanup."""
    logger.stage_start(run_id, stage)
    start_time = time.time()

    try:
        yield
    except Exception as e:
        logger.error(f"Stage {stage} failed", run_id=run_id, error=str(e))
        raise
    finally:
        duration = (time.time() - start_time) * 1000
        logger.stage_complete(run_id, stage, duration_ms=duration)
```

#### Docstrings

```python
# ✅ Good: Google-style docstrings
def execute_stage4(
    run_id: str,
    brand_id: str,
    stage3_output_path: str,
    prompt: str,
    llm_config: dict
) -> dict:
    """
    Execute Stage 4: Brand Contextualization.

    Loads comprehensive brand research (8 sections, 120+ data points)
    and injects it into the prompt to contextualize general opportunities
    for the specific brand.

    Args:
        run_id: Unique identifier for the test run
        brand_id: Brand identifier (e.g., "lactalis-canada")
        stage3_output_path: Blob storage path to Stage 3 output
        prompt: User-defined prompt template for Stage 4
        llm_config: LLM configuration dict with 'model' and 'temperature'

    Returns:
        dict containing:
            - output_path: Blob storage path to Stage 4 output
            - tokens_used: Total tokens consumed
            - cost_usd: Actual cost in USD

    Raises:
        ResearchNotFoundError: If brand research file is missing
        StageExecutionError: If LLM execution fails
    """
    # Implementation
```

---

### Code Quality Tools

#### TypeScript/JavaScript

**ESLint Configuration** (`.eslintrc.json`):

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react-hooks/exhaustive-deps": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

**Prettier Configuration** (`.prettierrc`):

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

#### Python

**Ruff Configuration** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["pipeline"]
```

**mypy Configuration** (`pyproject.toml`):

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

### Critical Coding Rules

#### Security

```typescript
// ✅ Good: Never log sensitive data
logger.info('User authenticated', { userId: user.id }); // OK

// ❌ Bad: Logging API keys or tokens
logger.info('API call', { apiKey: process.env.OPENROUTER_API_KEY }); // NEVER

// ✅ Good: Validate all user inputs
const validateRunId = (id: string): boolean => {
  return /^[a-zA-Z0-9-]{36}$/.test(id); // UUID format
};

// ✅ Good: Use environment variables for secrets
const apiKey = process.env.OPENROUTER_API_KEY;
if (!apiKey) {
  throw new Error('OPENROUTER_API_KEY is required');
}
```

#### Performance

```typescript
// ✅ Good: Avoid N+1 queries
const runs = await db.query.testRuns.findMany({
  with: {
    opportunities: true, // Load with JOIN
  },
});

// ❌ Bad: N+1 query
const runs = await db.query.testRuns.findMany();
for (const run of runs) {
  const opportunities = await db.query.opportunityCards.findMany({
    where: eq(opportunityCards.runId, run.id),
  });
}

// ✅ Good: Debounce API calls
const debouncedEstimate = useMemo(
  () => debounce((config: PromptConfiguration) => {
    estimateCost(config);
  }, 500),
  []
);
```

#### Maintainability

```typescript
// ✅ Good: Single Responsibility Principle
function ExecutionMonitor({ runId }: { runId: string }) {
  const { status, error } = useExecutionPolling(runId); // Separate hook

  if (error) return <ErrorDisplay error={error} />; // Separate component
  if (!status) return <LoadingSpinner />;

  return <StageProgressList stages={status.stages} />;
}

// ✅ Good: Avoid magic numbers
const POLLING_INTERVAL_MS = 2000;
const MAX_RETRIES = 3;
const STAGE_TIMEOUT_MS = 300000; // 5 minutes

// ❌ Bad: Magic numbers
setInterval(poll, 2000); // What is 2000?
```

---

### Git Commit Standards

```bash
# Format: <type>(<scope>): <subject>

# Types:
feat: New feature
fix: Bug fix
docs: Documentation changes
style: Formatting, missing semicolons, etc.
refactor: Code restructuring without behavior change
test: Adding tests
chore: Build process, dependencies, etc.

# Examples:
feat(prompt-editor): add Monaco syntax highlighting
fix(stage4): handle missing research data gracefully
docs(architecture): complete coding standards section
refactor(cost-estimator): extract token calculation logic
test(research-loader): add parsing edge cases
```

---

## 14. Error Handling Strategy

### Overview

The Innovation Intelligence Pipeline requires robust error handling across three layers:
1. **User-Facing Errors** - Clear, actionable messages in the UI
2. **System Errors** - Logged for debugging and monitoring
3. **Recovery Strategies** - Automatic retries and fallbacks

---

### Error Classification

| Error Type | User Impact | Recovery Strategy | Example |
|------------|-------------|-------------------|---------|
| **Validation Error** | Immediate feedback | User corrects input | Empty prompt field |
| **Client Error (4xx)** | Actionable message | User fixes request | Invalid brand ID |
| **Server Error (5xx)** | Retry option | Automatic retry (3x) | LLM API timeout |
| **Network Error** | Retry option | Exponential backoff | Connection lost |
| **Data Not Found** | Informative message | Suggest alternatives | Missing research file |

---

### Frontend Error Handling

#### API Error Types

```typescript
// lib/errors.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, public field: string) {
    super(message, 400, 'VALIDATION_ERROR', { field });
  }
}

export class ResourceNotFoundError extends ApiError {
  constructor(resourceType: string, resourceId: string) {
    super(
      `${resourceType} not found: ${resourceId}`,
      404,
      'RESOURCE_NOT_FOUND',
      { resourceType, resourceId }
    );
  }
}

export class LLMTimeoutError extends ApiError {
  constructor(stage: number, timeout: number) {
    super(
      `Stage ${stage} timed out after ${timeout}ms`,
      504,
      'LLM_TIMEOUT',
      { stage, timeout }
    );
  }
}

export class InsufficientCreditsError extends ApiError {
  constructor(required: number, available: number) {
    super(
      `Insufficient credits: ${available} available, ${required} required`,
      402,
      'INSUFFICIENT_CREDITS',
      { required, available }
    );
  }
}
```

#### Error Boundary Component

```typescript
// components/ErrorBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';
import { logger } from '@/lib/logger';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logger.error('Uncaught error in component tree', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, () =>
          this.setState({ hasError: false, error: null })
        );
      }

      return (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>
            {this.state.error.message}
            <Button
              variant="outline"
              size="sm"
              className="mt-2"
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              Try again
            </Button>
          </AlertDescription>
        </Alert>
      );
    }

    return this.props.children;
  }
}
```

#### API Client with Error Handling

```typescript
// lib/api-client.ts
export class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      // Handle different error types
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        switch (response.status) {
          case 400:
            throw new ValidationError(
              errorData.message || 'Validation failed',
              errorData.field
            );
          case 404:
            throw new ResourceNotFoundError(
              errorData.resourceType || 'Resource',
              errorData.resourceId || 'unknown'
            );
          case 402:
            throw new InsufficientCreditsError(
              errorData.required,
              errorData.available
            );
          case 504:
            throw new LLMTimeoutError(errorData.stage, errorData.timeout);
          default:
            throw new ApiError(
              errorData.message || 'Request failed',
              response.status,
              errorData.code || 'UNKNOWN_ERROR',
              errorData
            );
        }
      }

      return response.json();
    } catch (error) {
      // Network errors
      if (error instanceof TypeError) {
        throw new ApiError(
          'Network error - check your connection',
          0,
          'NETWORK_ERROR'
        );
      }

      // Re-throw API errors
      throw error;
    }
  }

  // Usage with retry logic
  async executeTest(params: ExecuteTestParams): Promise<{ run_id: string }> {
    return this.withRetry(() => this.request('/pipeline/execute', {
      method: 'POST',
      body: JSON.stringify(params),
    }));
  }

  private async withRetry<T>(
    fn: () => Promise<T>,
    maxRetries = 3,
    delay = 1000
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // Don't retry validation errors or 4xx errors
        if (error instanceof ValidationError ||
            (error instanceof ApiError && error.statusCode < 500)) {
          throw error;
        }

        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, delay * (attempt + 1)));
        }
      }
    }

    throw lastError!;
  }
}
```

#### User-Facing Error Messages

```typescript
// lib/error-messages.ts
export function getUserFriendlyMessage(error: Error): {
  title: string;
  message: string;
  action?: string;
} {
  if (error instanceof ValidationError) {
    return {
      title: 'Validation Error',
      message: error.message,
      action: `Please check the ${error.field} field and try again.`,
    };
  }

  if (error instanceof ResourceNotFoundError) {
    return {
      title: 'Not Found',
      message: `The requested ${error.details.resourceType} could not be found.`,
      action: 'Please check the ID and try again, or select from available options.',
    };
  }

  if (error instanceof LLMTimeoutError) {
    return {
      title: 'Processing Timeout',
      message: `Stage ${error.details.stage} is taking longer than expected.`,
      action: 'This sometimes happens with complex prompts. Try again or use a different model.',
    };
  }

  if (error instanceof InsufficientCreditsError) {
    return {
      title: 'Insufficient Credits',
      message: `This test requires $${error.details.required.toFixed(2)}, but you have $${error.details.available.toFixed(2)} available.`,
      action: 'Add credits to your account or use a cheaper model.',
    };
  }

  if (error instanceof ApiError && error.code === 'NETWORK_ERROR') {
    return {
      title: 'Connection Error',
      message: 'Unable to reach the server.',
      action: 'Check your internet connection and try again.',
    };
  }

  return {
    title: 'Unexpected Error',
    message: error.message,
    action: 'If this persists, please contact support.',
  };
}
```

---

### Backend Error Handling

#### Python Exception Hierarchy

```python
# pipeline/exceptions.py
class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    def __init__(self, message: str, stage: int = None, details: dict = None):
        self.message = message
        self.stage = stage
        self.details = details or {}
        super().__init__(message)

class ResearchNotFoundError(PipelineError):
    """Raised when brand research file is not found."""
    def __init__(self, brand_id: str):
        super().__init__(
            f"Research not found for brand: {brand_id}",
            details={'brand_id': brand_id, 'resource_type': 'brand_research'}
        )

class LLMTimeoutError(PipelineError):
    """Raised when LLM request exceeds timeout."""
    def __init__(self, stage: int, timeout: int):
        super().__init__(
            f"LLM request timed out after {timeout}ms",
            stage=stage,
            details={'timeout': timeout}
        )

class LLMAPIError(PipelineError):
    """Raised when LLM API returns an error."""
    def __init__(self, stage: int, status_code: int, error_message: str):
        super().__init__(
            f"LLM API error: {error_message}",
            stage=stage,
            details={'status_code': status_code, 'api_message': error_message}
        )

class InvalidPromptError(PipelineError):
    """Raised when prompt template is invalid."""
    def __init__(self, stage: int, reason: str):
        super().__init__(
            f"Invalid prompt for stage {stage}: {reason}",
            stage=stage,
            details={'reason': reason}
        )
```

#### Retry Decorator

```python
# pipeline/utils.py
import time
import functools
from typing import Callable, Type, Tuple

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exception types to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {current_delay}s",
                            error=str(e),
                            function=func.__name__
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed",
                            error=str(e),
                            function=func.__name__
                        )

            raise last_exception

        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, delay=2.0, exceptions=(LLMAPIError, LLMTimeoutError))
def call_llm_api(prompt: str, config: dict) -> str:
    response = llm.invoke(prompt)
    return response.content
```

#### Stage Execution Error Handling

```python
# pipeline/stages/base.py
from contextlib import contextmanager
from typing import Generator

@contextmanager
def stage_execution(
    run_id: str,
    stage: int,
    model: str
) -> Generator[None, None, None]:
    """Context manager for stage execution with comprehensive error handling."""
    logger.stage_start(run_id, stage, model)
    start_time = time.time()

    try:
        yield

        duration_ms = (time.time() - start_time) * 1000
        logger.stage_complete(run_id, stage, duration_ms=duration_ms)

    except ResearchNotFoundError as e:
        logger.error(
            f"Research data missing for stage {stage}",
            run_id=run_id,
            stage=stage,
            brand_id=e.details.get('brand_id')
        )
        # Update DB: mark run as failed
        update_run_status(run_id, 'failed', f"Missing research data: {e.message}")
        raise

    except LLMTimeoutError as e:
        logger.error(
            f"LLM timeout in stage {stage}",
            run_id=run_id,
            stage=stage,
            timeout=e.details.get('timeout')
        )
        # Update DB: mark run as failed
        update_run_status(run_id, 'failed', f"Stage {stage} timed out")
        raise

    except LLMAPIError as e:
        logger.error(
            f"LLM API error in stage {stage}",
            run_id=run_id,
            stage=stage,
            status_code=e.details.get('status_code'),
            api_message=e.details.get('api_message')
        )
        # Update DB: mark run as failed
        update_run_status(run_id, 'failed', f"LLM API error: {e.message}")
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error in stage {stage}",
            run_id=run_id,
            stage=stage,
            error=str(e),
            error_type=type(e).__name__
        )
        # Update DB: mark run as failed
        update_run_status(run_id, 'failed', f"Unexpected error: {str(e)}")
        raise PipelineError(f"Stage {stage} failed", stage=stage, details={'error': str(e)})

# Usage in stage function
def execute_stage4(run_id: str, brand_id: str, ...) -> dict:
    with stage_execution(run_id, stage=4, model=llm_config['model']):
        # Load research
        research = research_loader.get_brand_research(brand_id)

        # Execute LLM with retry
        response = call_llm_api(formatted_prompt, llm_config)

        # Save output
        blob_client.write(output_path, response)

        return {'output_path': output_path, ...}
```

---

### Error Recovery Strategies

#### Graceful Degradation

```typescript
// If cost estimation fails, show approximate cost
async function estimateWithFallback(config: PromptConfiguration): Promise<number> {
  try {
    const estimate = await api.estimateCost(config);
    return estimate.total_cost_usd;
  } catch (error) {
    logger.warn('Cost estimation failed, using approximate value', { error });
    // Fallback: Use average cost based on model
    return getApproximateCost(config.default_model_id);
  }
}
```

#### Partial Failure Handling

```python
# If one opportunity card generation fails, continue with others
def generate_opportunity_cards(opportunities: List[dict]) -> List[OpportunityCard]:
    cards = []
    errors = []

    for idx, opp in enumerate(opportunities):
        try:
            card = render_opportunity_card(opp, idx + 1)
            cards.append(card)
        except Exception as e:
            logger.error(f"Failed to generate card {idx + 1}", error=str(e))
            errors.append((idx + 1, str(e)))
            # Continue with next card

    if len(cards) == 0:
        raise PipelineError(f"All opportunity card generation failed: {errors}")

    if errors:
        logger.warning(f"Generated {len(cards)}/5 cards successfully", errors=errors)

    return cards
```

---

### Error Monitoring & Alerting

```typescript
// Send critical errors to Sentry with context
function reportCriticalError(error: Error, context: Record<string, any>) {
  Sentry.captureException(error, {
    level: 'error',
    contexts: {
      pipeline: context,
    },
    tags: {
      error_type: error.constructor.name,
      component: context.component || 'unknown',
    },
  });
}

// Usage
try {
  await api.executeTest(params);
} catch (error) {
  reportCriticalError(error as Error, {
    component: 'ExecutionMonitor',
    run_id: runId,
    brand_id: params.brand_id,
    prompt_config_id: params.prompt_config_id,
  });
  throw error;
}
```

---

**Rationale for Error Handling Decisions**:

1. **Typed errors**: TypeScript classes enable compile-time checking and better autocomplete
2. **User-friendly messages**: Non-technical language with actionable next steps
3. **Automatic retries**: Transient failures (network, LLM timeouts) recovered without user intervention
4. **Graceful degradation**: Cost estimation fallback prevents UI from breaking
5. **Comprehensive logging**: All errors logged with context for debugging
6. **Error boundaries**: Prevent entire app crashes from component errors
7. **Sentry integration**: Production error tracking with full context

---

**Document Status**: ✅ All 14 sections completed.

**Last Updated**: 2025-01-XX
**Version**: 1.0 (Final Draft)
