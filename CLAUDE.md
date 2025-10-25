# Innovation Intelligence System - Claude Configuration
      340 +  ## Deployment to Railway
       341 +  
       342 +  ### Backend Deployment
       343 +  
       344 +  The Python FastAPI backend is deployed to Railway. The service is configured with:
       345 +  - **Root Directory**: `backend` (configured in Railway dashboard)
       346 +  - **Build**: Dockerfile-based build
       347 +  - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
       348 +  
       349 +  **Deploying from CLI:**
       350 +  
       351 +  ```bash
       352 +  # Deploy from PROJECT ROOT (not from backend directory)
       353 +  # Railway is configured with root directory as 'backend'
       354 +  railway deploy
       355 +  
       356 +  # Or using Railway MCP tool
       357 +  # Must provide absolute path to PROJECT ROOT
       358 +  /Users/your-username/path/to/innovation-intelligence-system
       359 +  ```
       360 +  
       361 +  **Important Notes:**
       362 +  - ✅ Deploy from the **project root** directory (`innovation-intelligence-system/`)
       363 +  - ❌ Do NOT deploy from `backend/` subdirectory
       364 +  - The Railway service has `backend` configured as the root directory in the dashboard
       365 +  - This means Railway expects to find the `backend/` folder relative to where you deploy from
       366 +  
       367 +  **Environment Variables:**
       368 +  - Set in Railway dashboard under Settings → Variables
       369 +  - Required: `DATABASE_URL`, `OPENROUTER_API_KEY`, `WEBHOOK_SECRET`, `VERCEL_BLOB_READ_WRITE_TOKEN`
       370 +  
       371 +  **Monitoring Deployment:**
       372 +  - Build logs are available in Railway dashboard
       373 +  - Or access via CLI: `railway logs`
## Current Sprint: Pipeline Visualization Frontend Build

**Status:** Building the Pipeline Visualization Page (`/pipeline/[runId]`) with 4 progressive UI states

**Goal:** Transform the existing pipeline page into a live, real-time UI that visualizes all 5 pipeline stages and displays final Opportunity Cards

## Architecture Overview

**Tech Stack:**
- Next.js 15 App Router with TypeScript
- shadcn/ui component library
- Tailwind CSS for styling
- Python backend pipeline (5 stages)
- File-based state (no database)

**Key Directories:**
- `innovation-web/` - Next.js frontend application
- `innovation-web/app/pipeline/[runId]/page.tsx` - Main pipeline page to refactor
- `innovation-web/components/pipeline/` - Pipeline-related components
- `docs/front-end-spec.md` - Complete UX/UI specification
- `backend/pipeline/` - Python pipeline implementation

## Frontend Build Task: Pipeline Visualization Page

### Overview
The pipeline page exists as **a single component with 4 progressive states** that evolve as the backend pipeline executes:

**State 1: Stage 1 Running**
- Left box: Extraction animation (beaker/flask visual)
- Right box: Workflow illustration

**State 2: Stage 1 Complete + Stages 2-5 Running**
- Left box: Extracted mechanisms cards with PDF download
- Right box: Stages 2-5 animation with progress indicators

**State 3: All Complete - Opportunity Cards Grid**
- 2-column grid of opportunity cards
- Download All and New Pipeline buttons

**State 4: Card Detail View**
- Collapsed sidebar (thumbnails)
- Expanded opportunity detail with full markdown

### Current Implementation Status

**Existing (`innovation-web/app/pipeline/[runId]/page.tsx`):**
- ✅ Real-time polling with exponential backoff
- ✅ Left sidebar with stage boxes
- ✅ Main content area with basic visualization
- ❌ Auto-redirects to `/results/[runId]` (needs removal)
- ❌ `DetailPanel` component (needs replacement with state machine)

### Major Changes Required

1. **Delete:** Auto-redirect to `/results/[runId]`
2. **Replace:** `DetailPanel` → `PipelineStateMachine` component
3. **Create:** 10 new components for the 4 states
4. **Enhance:** Stage 1 JSON output to include mechanism details
5. **Update:** API status endpoint with timestamps

### New Components to Create

```
innovation-web/components/pipeline/
├── PipelineStateMachine.tsx       (Orchestrator)
├── ExtractionAnimation.tsx        (State 1)
├── WorkflowIllustration.tsx       (State 1)
├── ExtractedTextView.tsx          (State 2)
├── MechanismCard.tsx              (State 2)
├── StagesAnimation.tsx            (State 2)
├── OpportunityCardsGrid.tsx       (State 3)
├── OpportunityCard.tsx            (State 3)
├── CollapsedSidebar.tsx           (State 4)
└── ExpandedOpportunityDetail.tsx  (State 4)
```

### Key Technical Details

**State Management:**
- React hooks + local state (no Redux)
- State transitions driven by `currentStage` and `status`
- Polling continues until pipeline complete

**API Integration:**
- Poll `GET /api/status/[runId]` every 5 seconds
- Fetch opportunities when `status === 'completed' && currentStage === 5`
- Download endpoints for PDFs

**Visual Design:**
- Color: Teal (#5B9A99 primary)
- Typography: System UI font stack
- Animations: 300-800ms transitions with `ease-in-out`
- Responsive: Mobile (1 col) → Tablet (2 col) → Desktop (2 col)

**Reference:** Complete specification in `docs/front-end-spec.md`

## Working with This Repository

### BMAD Agent System Integration

This repository leverages the **BMAD™ Core** agent orchestration system for systematic innovation intelligence workflows. The system provides specialized agents that integrate with your Innovation Intelligence System.

#### Available BMAD Agents

**Core Development & Analysis Team:**
- `/BMad:agents:analyst` - Business Analyst (Mary) 📊 - Market research, brainstorming, competitive analysis
- `/BMad:agents:architect` - System Architect - Technical architecture and system design
- `/BMad:agents:dev` - Developer Agent - Implementation and coding tasks
- `/BMad:agents:pm` - Project Manager - Coordination and delivery management
- `/BMad:agents:po` - Product Owner - Requirements and feature prioritization
- `/BMad:agents:qa` - Quality Assurance - Testing and validation protocols
- `/BMad:agents:ux-expert` - UX Expert - User experience and interface design
- `/BMad:agents:sm` - Scrum Master - Agile process facilitation

**System Orchestration:**
- `/BMad:agents:bmad-master` - Master Orchestrator for complex multi-agent workflows
- `/BMad:agents:bmad-orchestrator` - Workflow coordination and agent management

### Operational Command Structure

**BMAD-Integrated Innovation Commands:**
```bash
# Agent-Powered Research & Analysis
/BMad:agents:analyst *brainstorm {innovation-topic} - Structured brainstorming with templates
/BMad:agents:analyst *create-competitor-analysis - Comprehensive competitive analysis
/BMad:agents:analyst *perform-market-research - Market research with validation frameworks
/BMad:agents:analyst *research-prompt {topic} - Deep research prompt generation

# Research & Analysis
/BMad:agents:qa *validate-innovation {concept} - Research validation methodologies
/BMad:agents:analyst *elicit - Advanced requirements elicitation for research

# Exploration Coordination
/BMad:agents:bmad-master - Orchestrate multi-disciplinary research workflows
/BMad:agents:bmad-orchestrator - Coordinate research and analysis activities

# Research Workflows
/BMad:workflows:innovation-discovery - Explore information processing approaches
/BMad:workflows:validation-protocol - Research validation methodology concepts
/BMad:workflows:agent-synthesis - Investigate multi-perspective analysis methods
```

**Legacy Innovation Commands (for reference):**
```bash
# Research and analysis
/research [topic] - Search research documents for specific concepts
/validate [concept] - Apply SPECTRE validation framework
/challenge [idea] - Run adversarial analysis on innovation concepts

# Agent collaboration
/pattern-hunt [problem] - Apply TRIZ/SIT systematic innovation
/biomimicry [challenge] - Find nature-inspired solutions
/market-analysis [innovation] - Assess user adoption psychology
/red-team [concept] - Systematic vulnerability identification
/foresight [trend] - Long-term strategic analysis
/synthesize [perspectives] - Integrate multiple viewpoints

# System workflow
/workflow [phase] - Access specific workflow documentation
/framework [type] - Apply psychological or validation frameworks
```

### BMAD Agent Quick Reference for This Task

**Primary Agents for Frontend Build:**
- `/BMad:agents:dev` - Implementation and coding
- `/BMad:agents:ux-expert` - UI/UX design guidance (created the spec)
- `/BMad:agents:architect` - System architecture decisions

**Supporting Agents:**
- `/BMad:agents:pm` - Project coordination
- `/BMad:agents:qa` - Testing and validation

### BMAD System Architecture

**Agent Configuration (`.bmad-core/agents/`):**
- Pre-configured innovation intelligence agents with specialized capabilities
- Each agent includes persona definitions, commands, and dependency mappings
- Seamless integration between BMAD agents and Innovation Intelligence personas

**Templates & Frameworks (`.bmad-core/templates/`):**
- `competitor-analysis-tmpl.yaml` - Structured competitive intelligence
- `market-research-tmpl.yaml` - Systematic market analysis with psychological frameworks
- `project-brief-tmpl.yaml` - Innovation project scoping and definition
- `brainstorming-output-tmpl.yaml` - Structured ideation session outputs
- Integration with SPECTRE validation templates

**Tasks & Workflows (`.bmad-core/tasks/`):**
- `advanced-elicitation.md` - Multi-method requirements discovery
- `facilitate-brainstorming-session.md` - Structured innovation ideation
- `create-deep-research-prompt.md` - Systematic research query generation
- `create-doc.md` - Template-driven document creation
- Integration with innovation intelligence workflows

**Agent Teams (`.bmad-core/agent-teams/`):**
- `team-fullstack.yaml` - Complete innovation intelligence team
- `team-all.yaml` - Maximum agent coordination for complex challenges
- `team-ide-minimal.yaml` - Core analytical team for rapid insights
- Configurable team compositions for different innovation challenges


## Development Guidelines

### BMAD System Configuration

**Core Configuration (`/.bmad-core/core-config.yaml`):**
```yaml
slashPrefix: BMad  # Enables /BMad:agents:* commands
markdownExploder: true  # Enhanced document processing (md-tree)
prd:
  prdFile: docs/prd.md
  prdSharded: true  # PRD split into modular sections
architecture:
  architectureFile: docs/architecture.md
  architectureSharded: true  # Architecture split into 15 modules
  architectureShardedLocation: docs/architecture
```

**Active Development Agent Protocol:**
```bash
# Primary development coordination
/BMad:agents:architect  # System design and architecture
/BMad:agents:dev        # Implementation and coding tasks
/BMad:agents:qa         # Testing and validation

# Supporting development
/BMad:agents:pm         # Project coordination and roadmap
/BMad:agents:ux-expert  # UI/UX design and component specs
```

### Code Style & Standards

**Next.js/React Conventions:**
- Next.js 15 App Router patterns (React Server Components)
- TypeScript strict mode
- Tailwind CSS utility-first styling
- shadcn/ui component library

**Implementation Priorities:**
1. **Functional completeness** - All 4 states working
2. **Minimal dependencies** - Use existing shadcn/ui components
3. **Real-time feedback** - Smooth polling and transitions
4. **Mobile responsive** - Tailwind responsive classes
5. **Error handling** - Graceful failures with user feedback

## Implementation Phases

### Phase 1: Foundation (Estimated: 2-3 hours)
- [ ] Create component file structure
- [ ] Set up TypeScript interfaces
- [ ] Implement `PipelineStateMachine` orchestrator
- [ ] Wire up state transition logic
- [ ] Remove auto-redirect to `/results`

### Phase 2: State 1-2 Components (Estimated: 3-4 hours)
- [ ] Build `ExtractionAnimation`
- [ ] Build `WorkflowIllustration`
- [ ] Build `ExtractedTextView`
- [ ] Build `MechanismCard`
- [ ] Build `StagesAnimation`

### Phase 3: State 3-4 Components (Estimated: 3-4 hours)
- [ ] Build `OpportunityCardsGrid`
- [ ] Build `OpportunityCard`
- [ ] Build `CollapsedSidebar`
- [ ] Build `ExpandedOpportunityDetail`
- [ ] Add Download/New Pipeline actions

### Phase 4: Polish & Testing (Estimated: 2-3 hours)
- [ ] Add state transition animations
- [ ] Test responsive breakpoints
- [ ] Add accessibility attributes
- [ ] Test error states
- [ ] Cross-browser testing

### Phase 5: Backend Integration (Estimated: 1-2 hours)
- [ ] Enhance Stage 1 JSON output
- [ ] Update API status endpoint
- [ ] Create download endpoints
- [ ] Test full pipeline integration

**Total Estimated Time:** 11-16 hours