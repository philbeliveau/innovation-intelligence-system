# Innovation Intelligence System - Claude Configuration

Project Context: CPG Innovation Intelligence Tool (Working Title)
Status: **ACTIVE DEVELOPMENT - Hackathon Build Phase**

## Current Sprint: Web Application MVP

**Build Goal:** Minimal web interface wrapping existing Python pipeline (8-10 hour hackathon scope)

**Architecture Decided:**
- Next.js 15 frontend with shadcn/ui components
- Vercel Blob for file storage
- Existing Python pipeline (unchanged - 5-stage LLM processing)
- Real-time pipeline visualization
- File-based state (no database)

**Key Features:**
1. Company pre-selection during onboarding (loads brand YAML profiles)
2. PDF upload via drag & drop
3. LLM-powered document analysis (intermediary card)
4. Real-time pipeline execution viewer (5 stages)
5. Opportunity card results display

**Development Status:**
- ✅ Architecture finalized (`docs/architecture.md` - sharded into 15 modules)
- ✅ Tech stack selected (Next.js 15, shadcn/ui, Vercel Blob, Python)
- 🚧 Ready to begin implementation (Hour 0 of 10-hour build)
- 📋 Implementation roadmap defined with hour-by-hour tasks

**Repository Structure:**
- `docs/architecture/` - Complete technical specifications (sharded)
- `pipeline/` - Existing Python implementation (stages 1-5)
- `data/brand-profiles/` - Company YAML configurations
- `innovation-web/` - New Next.js application (to be created)

## Project Overview

This repository contains a **working Innovation Intelligence Pipeline** that processes trend reports and generates brand-specific innovation opportunities through a 5-stage LLM workflow.

**✅ VALIDATED PIPELINE:**
- Stage 1: Input Processing (extract 2 main inspirations)
- Stage 2: Signal Amplification (identify trends)
- Stage 3: General Translation (universal lessons)
- Stage 4: Brand Contextualization (brand-specific insights)
- Stage 5: Opportunity Generation (5 actionable opportunity cards)

**🚧 IN DEVELOPMENT - Web Interface:**
Building minimal web wrapper to make pipeline accessible via browser with real-time visualization.

### Core Capabilities (Implemented)

**Current Pipeline Implementation:**
- ✅ PDF document processing with text extraction
- ✅ 5-stage LLM workflow for opportunity generation
- ✅ Brand profile integration (YAML-based)
- ✅ Brand research data contextualization (Markdown)
- ✅ Structured opportunity card output format

**Web Interface (In Development):**
- 🚧 Next.js 15 frontend with App Router
- 🚧 Real-time pipeline progress visualization
- 🚧 Document analysis with LLM extraction
- 🚧 Company onboarding and brand context loading
- 🚧 Opportunity card display and export

**Technical Architecture:**
- LangChain for LLM orchestration
- OpenRouter API (Claude Sonnet 4.5 via DeepSeek)
- Vercel deployment with Blob storage
- File-based state management
- Sequential stage execution with logging

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

### Repository Structure

**Research Foundation** (9 documents):
- Psychological and cognitive science foundations
- Innovation methodologies (TRIZ, SIT, Lateral Thinking, Biomimicry)
- Latest neuroscience and creativity research integration

**Psychology Framework** (4 documents):
- SPECTRE validation framework
- Challenge validation protocols
- Psychological safety maintenance
- Red team/blue team dynamics

**Agent Personas** (7 documents):
- Detailed psychological profiles for each specialized agent
- Big Five personality trait specifications
- Unique capabilities and interaction protocols

**Workflow Design** (1 document):
- Complete end-to-end system workflow
- Phase-by-phase processing pipeline
- Intelligence generation and validation stages

**BMAD Adaptation** (1 document):
- Framework transformation from software development to innovation intelligence
- Agent coordination and template systems
- Quality assurance and validation protocols

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

### Working Principles

**Innovation Discovery:**
- Process multiple intelligence streams simultaneously
- Identify weak signals and emerging patterns
- Apply cross-industry pattern recognition
- Translate solutions between domains

**Systematic Validation:**
- Use SPECTRE framework for comprehensive assessment
- Apply progressive challenge levels (gentle to adversarial)
- Maintain psychological safety while ensuring rigor
- Integrate multiple perspectives for robust analysis

**Agent Collaboration:**
- Leverage specialized psychological profiles
- Coordinate multi-agent analysis and synthesis
- Balance different cognitive approaches
- Generate consensus through constructive conflict

### Innovation Intelligence Integration Workflows

**1. Discovery & Research Phase:**
```bash
# Start with Business Analyst for structured research
/BMad:agents:analyst *brainstorm {emerging-technology}
/BMad:agents:analyst *perform-market-research
/BMad:agents:analyst *create-competitor-analysis

# Coordinate multi-agent research for comprehensive intelligence
/BMad:agents:bmad-orchestrator *coordinate-research-team
```

**2. Concept Development & Validation:**
```bash
# Apply SPECTRE validation through QA agent
/BMad:agents:qa *validate-innovation {concept}
/BMad:agents:analyst *elicit  # Advanced requirements discovery

# Cross-domain pattern analysis (connect to Pattern Hunter persona)
/BMad:agents:analyst *research-prompt "TRIZ principles for {problem-domain}"
```

**3. Implementation Planning:**
```bash
# System architecture and technical feasibility
/BMad:agents:architect *design-innovation-architecture
/BMad:agents:pm *create-implementation-roadmap

# UX and adoption strategy
/BMad:agents:ux-expert *design-user-adoption-strategy
```

**4. Multi-Agent Synthesis:**
```bash
# Orchestrate full innovation intelligence workflow
/BMad:agents:bmad-master *innovation-intelligence-synthesis
# Coordinate all 6 specialized psychological personas through BMAD system
```

**Research Area Mapping to BMAD System:**
- **Pattern Recognition Research** ↔ `/BMad:agents:analyst` + TRIZ/SIT research prompts
- **Cross-domain Knowledge Research** ↔ `/BMad:agents:analyst` + biomimicry research workflows
- **Market Psychology Research** ↔ `/BMad:agents:analyst` + market research templates
- **Validation Methodology Research** ↔ `/BMad:agents:qa` + validation research protocols
- **Strategic Analysis Research** ↔ `/BMad:agents:pm` + foresight planning research
- **Synthesis Method Research** ↔ `/BMad:agents:bmad-master` + multi-agent coordination research

### Business Context

**Target Market:**
- VP Innovation teams in Fortune 1000 companies
- Management consulting innovation practices
- Innovation agencies and research organizations
- Corporate venture capital and strategic planning teams

**Value Proposition:**
- Transform trend reports into brand-specific innovation opportunities
- 5-stage LLM pipeline generates actionable opportunity cards
- Cross-industry pattern recognition and translation
- Reduces time from trend report to innovation brief from weeks to minutes

**Current Implementation Focus:**
- Hackathon MVP: Web interface for existing pipeline
- Demo-ready product for stakeholder validation
- Foundation for future SaaS platform

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
/BMad:agents:architect  # System design and architecture (Winston)
/BMad:agents:dev        # Implementation and coding tasks
/BMad:agents:qa         # Testing and validation

# Supporting development
/BMad:agents:pm         # Project coordination and roadmap
/BMad:agents:ux-expert  # UI/UX design and component specs
```

**Current Build Focus:**
- Hour-by-hour implementation roadmap (`docs/architecture/9-implementation-roadmap.md`)
- shadcn/ui component generation via MCP tool
- Next.js 15 App Router patterns
- Vercel deployment optimization

### Code Style (Web Application)
- Next.js 15 App Router patterns (React Server Components)
- TypeScript strict mode
- Tailwind CSS utility-first styling
- shadcn/ui component library
- File-based routing conventions

### Implementation Priorities
1. **Speed over perfection** - 8-10 hour hackathon build
2. **Minimal UI** - shadcn/ui components only, no custom CSS frameworks
3. **Reuse existing pipeline** - Zero refactoring of Python code
4. **File-based state** - No database setup overhead
5. **Real-time visualization** - Core UX feature for demo impact

### Quality Standards
- **Functional completeness** - All 5 pipeline stages visualized
- **Error handling** - Graceful failures with user feedback
- **Security basics** - XSS protection in markdown rendering, no SQL injection risk (no DB)
- **Mobile responsive** - Basic Tailwind responsive classes
- **Browser compatibility** - Modern browsers only (Chrome, Safari, Firefox)

## Quick Start Guide

### For Development:

1. **Review Architecture:**
   ```bash
   # Read sharded architecture docs
   cat docs/architecture/index.md
   cat docs/architecture/9-implementation-roadmap.md
   ```

2. **Start Development:**
   ```bash
   # Activate architect agent for guidance
   /BMad:agents:architect

   # Or activate developer agent to begin coding
   /BMad:agents:dev
   ```

3. **Follow Implementation Roadmap:**
   - Hour 0-1: Project setup (Next.js + shadcn/ui)
   - Hour 1-2: Onboarding page
   - Hour 2-3: Homepage UI
   - Hour 3-4: Intermediary card page
   - Hour 4-5: API routes
   - Hour 5-6: Pipeline modifications
   - Hour 6-8: Pipeline viewer UI
   - Hour 8-9: Results page
   - Hour 9-10: Polish and deployment

### Key Files:

- `docs/architecture/` - Complete technical specifications
- `docs/prd.md` - Product requirements
- `pipeline/stages/` - 5-stage Python implementation
- `data/brand-profiles/` - Company YAML configurations
- `scripts/run_pipeline.py` - Pipeline entry point

### Testing Existing Pipeline:

```bash
# Run pipeline locally
python scripts/run_pipeline.py \
  --input-file data/test-docs/sample.pdf \
  --brand lactalis-canada \
  --run-id test-001
```