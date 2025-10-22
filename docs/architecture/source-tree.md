# 12. Source Tree Navigation Guide

## Overview

This document provides a comprehensive guide to navigating the Innovation Intelligence System codebase. Use this as your map to understand where everything lives and where to add new code.

---

## Repository Structure (High-Level)

```
innovation-intelligence-system/
├── .bmad-core/              # BMAD agent system configuration
├── data/                    # Static data files (YAML, Markdown)
├── docs/                    # Documentation (architecture, PRD, stories)
├── innovation-web/          # Next.js web application (TO BE CREATED)
├── pipeline/                # Python LLM pipeline (EXISTING - DO NOT MODIFY)
├── scripts/                 # Python utility scripts
└── tests/                   # Test files
```

**Critical Distinction:**
- **`innovation-web/`** - New Next.js application (hackathon build)
- **`pipeline/`** - Existing Python implementation (FROZEN - minimal changes only)

---

## Python Pipeline (Existing Code)

### Pipeline Structure

```
pipeline/
├── __init__.py
├── chains.py                # LangChain configurations
├── utils.py                 # Shared utilities
└── stages/
    ├── stage1_input_processing.py        # Extract 2 inspirations
    ├── stage2_signal_amplification.py    # Identify trends
    ├── stage3_general_translation.py     # Universal lessons
    ├── stage4_brand_contextualization.py # Brand-specific insights
    └── stage5_opportunity_generation.py  # Generate 5 opportunity cards
```

**⚠️ DO NOT MODIFY STAGES:**
- These files are validated and working
- Only modify if absolutely critical for integration
- Changes require regression testing

### Scripts Directory

```
scripts/
├── run_pipeline.py          # ✏️ MODIFY THIS - Pipeline entry point
└── test_pipeline.py         # Optional test runner
```

**Modifications Allowed:**
- `run_pipeline.py` - Add CLI arguments, logging, JSON output
- Add new wrapper scripts (e.g., `status_checker.py`)

### Data Directory

```
data/
├── brand-profiles/          # 🔍 READ THESE - Company YAML configs
│   ├── lactalis-canada.yaml
│   ├── pepsico.yaml
│   └── ...
├── brand-research/          # 📚 CONTEXT DATA - Markdown research files
│   ├── lactalis-canada.md
│   ├── pepsico.md
│   └── ...
└── test-outputs/            # 📂 PIPELINE OUTPUTS
    └── {run_id}/
        ├── logs/
        │   └── pipeline.log
        ├── stage1/
        │   ├── inspiration-analysis.md
        │   └── inspirations.json
        ├── stage2/ ... stage5/
        └── stage5/
            ├── opportunity-1.md
            ├── opportunity-2.md
            ├── opportunity-3.md
            ├── opportunity-4.md
            └── opportunity-5.md
```

**Key Files to Reference:**
- **`brand-profiles/*.yaml`** - Used in onboarding company selection
- **`test-outputs/{run_id}/`** - Pipeline execution results

---

## Next.js Web Application (innovation-web/)

### Application Structure

```
innovation-web/
├── app/                     # Next.js 15 App Router
│   ├── api/                 # Backend API routes
│   ├── onboarding/          # Page routes
│   ├── analyze/             # Page routes
│   ├── pipeline/            # Page routes
│   ├── results/             # Page routes
│   ├── runs/                # Run history & detail pages
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Homepage (onboarding)
├── components/              # React components
│   ├── ui/                  # shadcn/ui primitives (DO NOT EDIT)
│   └── ...                  # Custom components
├── lib/                     # Utilities and helpers
│   ├── prisma.ts            # ⭐ Prisma Client singleton
│   └── utils.ts             # Utility functions
├── prisma/                  # ⭐ Database schema and migrations
│   ├── schema.prisma        # Complete database schema
│   ├── migrations/          # Version-controlled SQL migrations
│   │   ├── 20250121000000_init/
│   │   │   └── migration.sql
│   │   └── migration_lock.toml
│   └── seed.ts              # Seed data for development
├── public/                  # Static assets
├── .env.local               # Environment variables (NOT IN GIT)
├── .env.example             # Environment template
├── next.config.js
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

---

## Next.js App Router (app/)

### Directory Mapping to Routes

**File-based Routing:**
```
app/page.tsx                    → /
app/onboarding/page.tsx         → /onboarding
app/analyze/[uploadId]/page.tsx → /analyze/abc123
app/pipeline/[runId]/page.tsx   → /pipeline/run-001
app/results/[runId]/page.tsx    → /results/run-001
```

### Pages Directory

```
app/
├── page.tsx                 # Homepage - File upload interface
├── onboarding/
│   └── page.tsx            # Company selection (first-time user)
├── analyze/
│   └── [uploadId]/
│       └── page.tsx        # Intermediary card - Document analysis
├── pipeline/
│   └── [runId]/
│       └── page.tsx        # Pipeline viewer - Real-time execution
├── results/
│   └── [runId]/
│       └── page.tsx        # Results display - 5 opportunity cards
└── layout.tsx              # Root layout (global styles, fonts)
```

**Where to Add New Pages:**
1. Create folder in `app/`
2. Add `page.tsx` file
3. Export default component
4. Route is automatically created

**Example: Add `/about` page**
```typescript
// app/about/page.tsx
export default function AboutPage() {
  return <div>About Innovation Intelligence System</div>
}
// Automatically accessible at /about
```

---

## API Routes (app/api/)

### API Directory Structure

```
app/api/
├── analyze-document/
│   └── route.ts            # POST /api/analyze-document
├── cards/
│   └── [cardId]/
│       └── star/
│           └── route.ts    # POST /api/cards/:id/star (toggle favorite)
├── onboarding/
│   ├── current-company/
│   │   └── route.ts        # GET /api/onboarding/current-company
│   └── set-company/
│       └── route.ts        # POST /api/onboarding/set-company
├── runs/
│   ├── route.ts            # GET /api/runs (list), POST /api/runs (create)
│   └── [runId]/
│       ├── route.ts        # GET /api/runs/:id (detail), DELETE /api/runs/:id
│       └── rerun/
│           └── route.ts    # POST /api/runs/:id/rerun
├── status/
│   └── [runId]/
│       └── route.ts        # GET /api/status/{runId} (proxy to Railway)
└── upload/
    └── route.ts            # POST /api/upload (Vercel Blob)
```

**Prisma-Powered Routes:**
- ✅ `GET /api/runs` - List user's runs with pagination
- ✅ `GET /api/runs/:id` - Get run details with cards, report, stages
- ✅ `POST /api/runs` - Create new run & trigger pipeline
- ✅ `POST /api/runs/:id/rerun` - Duplicate and rerun pipeline
- ✅ `DELETE /api/runs/:id` - Delete run (cascade deletes)
- ✅ `POST /api/cards/:id/star` - Toggle favorite card

**Backend Proxy Routes:**
- ⚡ `GET /api/status/:runId` - Proxies to Railway FastAPI
- ⚡ `POST /api/run` - Proxies to Railway (deprecated, use `/api/runs`)
```

**API Route File Pattern:**
```typescript
// app/api/example/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  return NextResponse.json({ message: 'Hello' })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  return NextResponse.json({ received: body })
}
```

**Where to Add New Endpoints:**
1. Create folder in `app/api/`
2. Add `route.ts` file
3. Export HTTP method handlers (GET, POST, PUT, DELETE)
4. Endpoint is automatically created

---

## Components Directory (components/)

### Component Organization

```
components/
├── ui/                      # 🚫 DO NOT EDIT - shadcn/ui primitives
│   ├── badge.tsx
│   ├── button.tsx
│   ├── card.tsx
│   ├── select.tsx
│   └── skeleton.tsx
├── CompanyBadge.tsx         # ✏️ Custom - Display company name/logo
├── FileUploadZone.tsx       # ✏️ Custom - Drag & drop upload
├── InspirationTrack.tsx     # ✏️ Custom - Stage 1 inspiration card
├── LeftSidebar.tsx          # ✏️ Custom - Collapsible home menu
└── StageBox.tsx             # ✏️ Custom - Stages 2-5 status box
```

**Component Categories:**

**1. UI Primitives (`components/ui/`):**
- Auto-generated by shadcn/ui CLI or MCP tool
- NEVER modify directly
- Use as building blocks for custom components

**2. Custom Components (Top-level):**
- Application-specific components
- Compose UI primitives
- Implement business logic

**Where to Add New Components:**

**For shadcn/ui primitives:**
```bash
npx shadcn@latest add dialog
# Adds components/ui/dialog.tsx
```

**For custom components:**
```typescript
// components/OpportunityCard.tsx
import { Card, CardHeader, CardContent } from '@/components/ui/card'

export default function OpportunityCard({ opportunity }) {
  return (
    <Card>
      <CardHeader>{opportunity.title}</CardHeader>
      <CardContent>{opportunity.description}</CardContent>
    </Card>
  )
}
```

---

## Library Directory (lib/)

### Utilities and Helpers

```
lib/
├── prisma.ts                # ⭐ Prisma Client singleton (CRITICAL)
├── utils.ts                 # General utilities (cn, formatters)
├── blob-client.ts           # Vercel Blob upload/download
├── pipeline-client.ts       # Python pipeline execution wrapper
└── brand-loader.ts          # Load brand YAML profiles
```

**Critical File: `lib/prisma.ts`**

```typescript
// lib/prisma.ts - Prisma Client Singleton Pattern
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development'
    ? ['query', 'error', 'warn']
    : ['error'],
})

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
```

**Why Singleton Pattern?**
- Prevents "too many connections" error in serverless environments
- Reuses single Prisma Client instance across hot reloads
- Essential for Vercel Edge/Serverless functions

**When to Add Files to `lib/`:**
- Shared utility functions
- API client wrappers
- Data transformation helpers
- Configuration loaders

**Example: Add new utility**
```typescript
// lib/pdf-validator.ts
export function isValidPDF(file: File): boolean {
  return file.type === 'application/pdf' && file.size < 10_000_000
}

// Usage in components:
import { isValidPDF } from '@/lib/pdf-validator'
```

---

## Prisma & Database (prisma/)

### Schema and Migrations

```
prisma/
├── schema.prisma            # ⭐ Complete database schema
├── migrations/              # Version-controlled SQL migrations
│   ├── 20250121000000_init/
│   │   └── migration.sql    # Initial schema (5 models)
│   ├── 20250121120000_add_user_run_management/
│   │   └── migration.sql    # User run management schema
│   └── migration_lock.toml  # Lock file for migration tracking
└── seed.ts                  # Seed data for development testing
```

**Database Schema Overview (5 Models):**

1. **User** - Authenticated users via Clerk
2. **Run** - Pipeline execution records
3. **OpportunityCard** - 5 cards from Stage 5
4. **InspirationReport** - Stage 1 inspiration tracks
5. **StageOutput** - Raw outputs from all 5 stages

**Entity Relationships:**
```
User (1) → (Many) Runs
User (1) → (Many) OpportunityCards
Run (1) → (Many) OpportunityCards
Run (1) → (1) InspirationReport
Run (1) → (Many) StageOutputs (stages 1-5)
```

### Common Prisma Commands

```bash
# Generate Prisma Client (after schema changes)
npx prisma generate

# Create new migration (development)
npx prisma migrate dev --name add_starred_field

# Apply migrations (production)
npx prisma migrate deploy

# Open Prisma Studio (visual database browser)
npx prisma studio

# Reset database (WARNING: deletes all data)
npx prisma migrate reset

# View migration status
npx prisma migrate status

# Seed database with test data
npx prisma db seed
```

### Prisma Usage in API Routes

```typescript
// app/api/runs/route.ts
import { prisma } from '@/lib/prisma'
import { auth } from '@clerk/nextjs/server'

export async function GET() {
  const { userId } = await auth()

  // Type-safe query with autocomplete
  const runs = await prisma.run.findMany({
    where: {
      user: { clerkId: userId }  // User isolation
    },
    include: {
      opportunityCards: true,     // Load relations
      inspirationReport: true
    },
    orderBy: { createdAt: 'desc' }
  })

  return NextResponse.json({ runs })
}
```

**Key Principles:**
- ✅ Always filter by authenticated user (`user.clerkId`)
- ✅ Use `include` for relations, not separate queries (prevents N+1)
- ✅ Use transactions for operations that must succeed/fail together
- ✅ Handle Prisma error codes (`P2025`, `P2002`, etc.)

---

## Backend (Railway FastAPI)

### Backend Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── routers/
│   │   └── pipeline.py      # Pipeline execution endpoints
│   ├── services/
│   │   ├── database_service.py   # ⭐ asyncpg PostgreSQL service
│   │   └── pipeline_service.py   # Python pipeline wrapper
│   └── models/
│       └── schemas.py       # Pydantic models
├── Dockerfile               # Railway deployment container
├── railway.json             # Railway configuration
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variable template
```

### Database Service (asyncpg)

**File: `backend/app/services/database_service.py`**

```python
import asyncpg
import os
from typing import Dict, Optional, List

class DatabaseService:
    """Async PostgreSQL service for pipeline writes."""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self._pool: Optional[asyncpg.Pool] = None

    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
        return self._pool

    async def update_run_stage(self, run_id: str, stage: int):
        """Update currentStage during pipeline execution."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                'UPDATE "Run" SET "currentStage" = $1 WHERE id = $2',
                stage, run_id
            )

    async def save_opportunity_cards(self, run_id: str, user_id: str, cards: List[Dict]):
        """Save 5 opportunity cards from Stage 5."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                for card in cards:
                    await conn.execute(
                        '''INSERT INTO "OpportunityCard" (...)
                           VALUES (...)''',
                        run_id, user_id, card['number'], ...
                    )
```

### Pipeline Integration Flow

```
1. Next.js API (/api/runs) → Creates Run record in PostgreSQL via Prisma
2. Next.js triggers Railway backend → POST /run
3. Railway FastAPI receives request
4. For each stage (1-5):
   a. Database Service updates currentStage
   b. Python Pipeline executes stage
   c. Database Service saves StageOutput
5. After Stage 5:
   a. Database Service parses opportunity cards
   b. Database Service saves 5 OpportunityCard records
   c. Database Service marks Run as COMPLETED
6. Next.js polls /api/status/:runId → Reads from PostgreSQL via Prisma
```

### Why Two Database Clients?

| Client | Language | Use Case | Location |
|--------|----------|----------|----------|
| **Prisma** | TypeScript | Type-safe reads, user queries | Next.js (Vercel) |
| **asyncpg** | Python | High-performance writes during pipeline | FastAPI (Railway) |

**Rationale:**
- Prisma is TypeScript-only (can't use in Python backend)
- asyncpg provides async high-performance writes for long-running pipeline
- Separation of concerns: Frontend reads, backend writes

---

## Public Directory (public/)

### Static Assets

```
public/
├── images/
│   ├── company-logos/
│   │   ├── lactalis.png
│   │   ├── pepsico.png
│   │   └── ...
│   └── icons/
│       └── upload-icon.svg
└── fonts/                   # Optional custom fonts
```

**Asset Access:**
```typescript
// In components:
<Image src="/images/company-logos/lactalis.png" alt="Lactalis" />

// In CSS (if needed):
background-image: url('/images/icons/upload-icon.svg');
```

---

## Documentation Directory (docs/)

### Documentation Structure

```
docs/
├── architecture/            # 📐 Technical specifications (15 files)
│   ├── index.md            # Master table of contents
│   ├── 1-introduction.md
│   ├── 2-architecture-overview.md
│   ├── 3-tech-stack.md
│   ├── 31-project-directory-structure.md
│   ├── 4-user-journey.md
│   ├── 5-ui-specifications.md
│   ├── 6-api-design.md
│   ├── 7-pipeline-integration.md
│   ├── 8-deployment.md
│   ├── 9-implementation-roadmap.md
│   ├── 10-component-specifications-shadcnui-mcp.md
│   ├── 11-coding-standards.md          # ⭐ THIS SECTION
│   ├── 12-source-tree-guide.md         # ⭐ YOU ARE HERE
│   ├── risk-mitigation.md
│   └── success-metrics.md
├── prd/                     # 📋 Product requirements (5 files)
│   ├── index.md
│   ├── 1-executive-summary.md
│   ├── 2-product-context.md
│   ├── 3-product-overview.md
│   └── 4-detailed-feature-requirements.md
└── stories/                 # 📖 User stories (implementation tasks)
    ├── 1.1.landing-page-company-selection.md
    ├── 1.2.file-upload-vercel-blob.md
    ├── 1.3.upload-page-ui-company-badge.md
    ├── 2.1.stage-1-input-processing.md
    ├── 2.2.intermediary-card-ui.md
    ├── 3.1.run-api-endpoint.md
    ├── 3.2.python-pipeline-modifications.md
    ├── 3.3.status-polling-monitoring.md
    ├── 4.1.vertical-pipeline-viewer-ui.md
    └── 5.1.results-page-opportunity-cards.md
```

**Documentation Reading Order (For Developers):**

**1. Pre-Implementation (REQUIRED):**
- `docs/architecture/11-coding-standards.md` (THIS IS CRITICAL)
- `docs/architecture/12-source-tree-guide.md` (YOU ARE HERE)
- `docs/architecture/3-tech-stack.md`
- `docs/architecture/31-project-directory-structure.md`

**2. Feature Implementation:**
- `docs/architecture/9-implementation-roadmap.md` (Hour-by-hour tasks)
- `docs/stories/{story-number}.md` (Specific feature requirements)

**3. Component Development:**
- `docs/architecture/5-ui-specifications.md`
- `docs/architecture/10-component-specifications-shadcnui-mcp.md`

**4. API Development:**
- `docs/architecture/6-api-design.md`
- `docs/architecture/7-pipeline-integration.md`

---

## BMAD Agent System (.bmad-core/)

### BMAD Configuration

```
.bmad-core/
├── core-config.yaml         # 🔧 Project configuration
├── agents/                  # 🤖 Agent personas
│   ├── architect.md
│   ├── dev.md
│   ├── pm.md
│   ├── qa.md
│   └── ...
├── tasks/                   # 📝 Executable workflows
│   ├── create-doc.md
│   ├── document-project.md
│   └── ...
├── templates/               # 📄 Document templates
│   ├── architecture-tmpl.yaml
│   ├── prd-tmpl.yaml
│   └── ...
└── checklists/              # ✅ Validation checklists
    └── architect-checklist.md
```

**When to Reference BMAD Files:**
- Using agent commands (`/BMad:agents:architect`)
- Creating new documentation from templates
- Running validation checklists

**DO NOT MODIFY** (unless you know what you're doing):
- `.bmad-core/core-config.yaml` - Project settings
- Agent persona files - Specialized behaviors

---

## File Naming Quick Reference

### Naming Convention Map

| Type | Convention | Example |
|------|-----------|---------|
| **React Components** | PascalCase.tsx | `FileUploadZone.tsx` |
| **UI Primitives** | lowercase.tsx | `button.tsx` |
| **Pages** | page.tsx | `app/analyze/[id]/page.tsx` |
| **API Routes** | route.ts | `app/api/upload/route.ts` |
| **Utilities** | kebab-case.ts | `blob-client.ts` |
| **Types** | PascalCase.ts | `Pipeline.ts` |
| **Tests** | *.test.tsx | `FileUploadZone.test.tsx` |
| **Config** | kebab-case.js | `next.config.js` |

---

## Common Navigation Scenarios

### Scenario 1: "I need to add a new page"

**Steps:**
1. Navigate to `innovation-web/app/`
2. Create new folder (e.g., `dashboard/`)
3. Add `page.tsx` inside
4. Export default component
5. Route is auto-created at `/dashboard`

**Example:**
```bash
cd innovation-web/app
mkdir dashboard
touch dashboard/page.tsx
```

```typescript
// dashboard/page.tsx
export default function DashboardPage() {
  return <div>Dashboard</div>
}
```

### Scenario 2: "I need to add an API endpoint"

**Steps:**
1. Navigate to `innovation-web/app/api/`
2. Create folder (e.g., `delete-upload/`)
3. Add `route.ts` inside
4. Export HTTP method handlers

**Example:**
```bash
cd innovation-web/app/api
mkdir delete-upload
touch delete-upload/route.ts
```

```typescript
// delete-upload/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function DELETE(request: NextRequest) {
  const { uploadId } = await request.json()
  // ... delete logic
  return NextResponse.json({ success: true })
}
```

### Scenario 3: "I need to add a reusable component"

**Steps:**
1. Determine if it's a UI primitive or custom component
2. **If UI primitive:** Use shadcn CLI (`npx shadcn@latest add {component}`)
3. **If custom:** Create in `innovation-web/components/`

**Example (Custom Component):**
```bash
cd innovation-web/components
touch OpportunityCard.tsx
```

```typescript
// OpportunityCard.tsx
import { Card } from '@/components/ui/card'

export default function OpportunityCard({ opportunity }) {
  return <Card>{opportunity.title}</Card>
}
```

### Scenario 4: "I need to load brand profile data"

**Steps:**
1. Brand YAML files are in `data/brand-profiles/`
2. Create utility in `innovation-web/lib/brand-loader.ts`
3. Use server-side in API routes or server components

**Example:**
```typescript
// lib/brand-loader.ts
import fs from 'fs'
import yaml from 'yaml'

export function loadBrandProfile(brandId: string) {
  const filePath = `../data/brand-profiles/${brandId}.yaml`
  const fileContent = fs.readFileSync(filePath, 'utf-8')
  return yaml.parse(fileContent)
}

// Usage in API route:
import { loadBrandProfile } from '@/lib/brand-loader'

const profile = loadBrandProfile('lactalis-canada')
```

### Scenario 5: "I need to run the Python pipeline"

**Steps:**
1. Pipeline is in `pipeline/stages/`
2. Entry point is `scripts/run_pipeline.py`
3. Call from API route using Node.js `spawn`

**Example:**
```typescript
// app/api/run/route.ts
import { spawn } from 'child_process'

export async function POST(request: NextRequest) {
  const { inputFile, brand, runId } = await request.json()

  const pythonProcess = spawn('python', [
    'scripts/run_pipeline.py',
    '--input-file', inputFile,
    '--brand', brand,
    '--run-id', runId
  ])

  // ... handle process output
}
```

### Scenario 6: "Where do I find UI specifications?"

**Documentation Path:**
1. Read `docs/architecture/5-ui-specifications.md`
2. Check component specs in `docs/architecture/10-component-specifications-shadcnui-mcp.md`
3. Reference design in `docs/stories/{feature}.md`

**Example:**
```bash
# Read onboarding page UI specs
cat docs/architecture/5-ui-specifications.md
# Section: 5.0 Onboarding/Landing Page - Company Selection
```

---

## Search Strategies

### Finding Code by Feature

**Use Grep/Search Tools:**
```bash
# Find upload-related code
grep -r "upload" innovation-web/app

# Find all API routes
find innovation-web/app/api -name "route.ts"

# Find all shadcn components
ls innovation-web/components/ui/
```

### Finding Documentation

**Use Table of Contents:**
```bash
# Architecture docs index
cat docs/architecture/index.md

# PRD index
cat docs/prd/index.md

# List all stories
ls docs/stories/
```

### Finding Brand Data

**Brand Profiles:**
```bash
# List available brands
ls data/brand-profiles/

# View specific brand
cat data/brand-profiles/lactalis-canada.yaml
```

---

## Directory Ownership & Modification Rules

### ✅ SAFE TO MODIFY:

| Directory | Purpose | Rules |
|-----------|---------|-------|
| `innovation-web/app/` | Pages & API routes | Add new pages/routes freely |
| `innovation-web/components/` (except ui/) | Custom components | Create new components |
| `innovation-web/lib/` | Utilities | Add helpers, clients |
| `innovation-web/public/` | Static assets | Add images, fonts |
| `scripts/run_pipeline.py` | Pipeline entry point | Modify for integration |
| `docs/` | Documentation | Update as needed |

### ⚠️ MODIFY WITH CAUTION:

| Directory | Purpose | Rules |
|-----------|---------|-------|
| `pipeline/` | Python pipeline | Only if critical for integration |
| `data/brand-profiles/` | Brand configs | Add new brands only |
| `innovation-web/components/ui/` | shadcn primitives | Never edit directly |
| `.bmad-core/` | Agent system | Only if extending BMAD |

### 🚫 DO NOT MODIFY:

| Directory | Purpose | Why Not |
|-----------|---------|---------|
| `pipeline/stages/` | Stage implementations | Validated, working code |
| `innovation-web/node_modules/` | Dependencies | Managed by npm |
| `.next/` | Build artifacts | Auto-generated |

---

## Quick Reference: "Where Do I Put...?"

| Item | Location | Example |
|------|----------|---------|
| New page | `app/{route}/page.tsx` | `app/dashboard/page.tsx` |
| New API endpoint | `app/api/{endpoint}/route.ts` | `app/api/export/route.ts` |
| Custom component | `components/ComponentName.tsx` | `components/ExportButton.tsx` |
| shadcn component | `components/ui/{name}.tsx` | Auto-generated via CLI |
| Utility function | `lib/{name}.ts` | `lib/validators.ts` |
| Type definition | `types/{name}.ts` | `types/Pipeline.ts` |
| Image asset | `public/images/{name}.png` | `public/images/logo.png` |
| Environment variable | `.env.local` | `BLOB_READ_WRITE_TOKEN=...` |
| Test file | Next to source file | `components/Button.test.tsx` |
| Documentation | `docs/{section}/{name}.md` | `docs/guides/deployment.md` |

---

## Integration Points

### Python ↔ Next.js Communication

**Data Flow:**
```
Next.js API Route
  ↓ (spawn Python process)
Python Pipeline
  ↓ (write to data/test-outputs/{run_id}/)
File System
  ↑ (read JSON/Markdown files)
Next.js API Route
  ↓ (return JSON to client)
React Component
```

**Key Files:**
- **Next.js:** `app/api/run/route.ts` (spawns Python)
- **Next.js:** `app/api/status/[runId]/route.ts` (reads output)
- **Python:** `scripts/run_pipeline.py` (writes output)
- **Output:** `data/test-outputs/{run_id}/` (shared filesystem)

### Brand Data Integration

**Data Flow:**
```
YAML Files (data/brand-profiles/)
  ↓ (read on server)
lib/brand-loader.ts
  ↓ (parse YAML)
API Route / Server Component
  ↓ (return JSON)
React Component
```

**Key Files:**
- **Data:** `data/brand-profiles/{brand-id}.yaml`
- **Loader:** `lib/brand-loader.ts`
- **API:** `app/api/onboarding/set-company/route.ts`

---

## Common File Paths (Cheat Sheet)

**Configuration Files:**
```
innovation-web/next.config.js           # Next.js config
innovation-web/tailwind.config.ts       # Tailwind config
innovation-web/tsconfig.json            # TypeScript config
innovation-web/.env.local               # Environment variables
.bmad-core/core-config.yaml             # BMAD project config
```

**Critical Documentation:**
```
docs/architecture/11-coding-standards.md      # Code style guide
docs/architecture/12-source-tree-guide.md     # This file
docs/architecture/9-implementation-roadmap.md # Build timeline
CLAUDE.md                                     # Project context
```

**Entry Points:**
```
innovation-web/app/page.tsx             # Homepage (/)
scripts/run_pipeline.py                 # Python pipeline
```

---

## Questions?

**For navigating the codebase:**
1. Check this guide first
2. Review `docs/architecture/31-project-directory-structure.md`
3. Use grep/find to search for files
4. Ask the architect agent (`/BMad:agents:architect`)

**Last Updated**: 2025-10-19
**Maintained By**: Winston (Architect Agent)
