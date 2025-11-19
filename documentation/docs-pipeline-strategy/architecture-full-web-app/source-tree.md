# Source Tree

## Project Root Structure

```
innovation-intelligence-system/
├── apps/
│   └── web/                      # Next.js 14 frontend application
├── api/
│   └── python/                   # Python serverless functions (Vercel)
├── packages/
│   └── database/                 # Drizzle ORM schema and migrations
├── docs/
│   ├── prd/                      # Product Requirements Documentation
│   ├── architecture/             # Architecture Documentation (this folder)
│   └── stories/                  # User stories and development tasks
├── .bmad-core/                   # BMAD agent system configuration
├── vercel.json                   # Vercel deployment configuration
├── turbo.json                    # Turborepo configuration
└── package.json                  # Root package.json for monorepo
```

## Frontend Application Structure

**Location**: `apps/web/src/`

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

## Backend API Structure

**Location**: `api/python/`

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

## Database Package Structure

**Location**: `packages/database/`

```
packages/database/
├── src/
│   ├── schema/
│   │   ├── prompts.ts            # Prompt configurations table
│   │   ├── runs.ts               # Test run executions table
│   │   ├── opportunities.ts      # Generated opportunities table
│   │   ├── brands.ts             # Brand metadata table
│   │   └── index.ts              # Schema exports
│   ├── migrations/
│   │   ├── 0001_initial.sql
│   │   └── meta/
│   └── client.ts                 # Drizzle client configuration
├── drizzle.config.ts
└── package.json
```

## Documentation Structure

**Location**: `docs/`

```
docs/
├── prd/                          # Product Requirements
│   ├── index.md
│   ├── 1-executive-summary.md
│   ├── 2-problem-statement.md
│   └── ...
├── architecture/                 # Architecture Documentation
│   ├── index.md
│   ├── coding-standards.md      # ⭐ DevLoadAlways
│   ├── tech-stack.md            # ⭐ DevLoadAlways
│   ├── source-tree.md           # ⭐ DevLoadAlways (this file)
│   ├── 1-introduction.md
│   ├── 2-high-level-architecture.md
│   └── ...
└── stories/                      # User stories and tasks
    ├── epic-1-prompt-editor.md
    └── ...
```

## BMAD Configuration Structure

**Location**: `.bmad-core/`

```
.bmad-core/
├── core-config.yaml              # Project-wide configuration
├── agents/                       # Agent persona definitions
│   ├── analyst.md
│   ├── architect.md
│   ├── dev.md
│   └── ...
├── templates/                    # Document templates
│   ├── prd-tmpl.yaml
│   ├── architecture-tmpl.yaml
│   └── ...
├── tasks/                        # Executable workflows
│   ├── create-doc.md
│   ├── document-project.md
│   └── ...
└── checklists/                   # Quality assurance checklists
    ├── architect-checklist.md
    └── ...
```

## Key Directory Conventions

### Frontend Conventions
- **Server Components** (RSC): List/read pages without interactivity
- **Client Components**: Forms, editors, interactive UI (`'use client'`)
- **Route Handlers**: `/app/api/**/*.ts` for Next.js API routes
- **UI Components**: shadcn/ui in `/components/ui/`
- **Feature Components**: Grouped by feature domain

### Backend Conventions
- **Entry Points**: `stage{1-5}.py` are Vercel serverless function handlers
- **Pipeline Logic**: Isolated in `/pipeline/stages/` modules
- **Shared Utilities**: `/pipeline/*.py` for cross-stage functionality
- **Templates**: Jinja2 templates in `/templates/`

### Database Conventions
- **Schema**: One file per table/entity in `/src/schema/`
- **Migrations**: Auto-generated by Drizzle in `/src/migrations/`
- **Client**: Single shared Drizzle client instance

### Documentation Conventions
- **Sharded Docs**: Large docs split into numbered sections
- **Index Files**: Navigation hub for sharded documentation
- **DevLoadAlways**: Files auto-loaded for development context
