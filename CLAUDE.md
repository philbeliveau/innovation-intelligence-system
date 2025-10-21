# Innovation Intelligence System - Claude Configuration

Project Context: CPG Innovation Intelligence Tool - **Mechanism Extraction Engine**
Status: **ENHANCED PIPELINE ARCHITECTURE - Perplexity Methodology Integration**

## 🚀 Major Pipeline Enhancement: Latent Factor Extraction

**Critical Update:** The pipeline has been fundamentally redesigned to extract **innovation mechanisms** (the HOW and WHY), not just surface observations (the WHAT). This transformation is based on advanced extraction methodologies that identify transferable patterns across industries.

## Current Sprint: Enhanced Pipeline + Web MVP

**Build Goal:** Web interface wrapping **enhanced mechanism-extraction pipeline** with CPG-specific optimization

**Architecture Stack:**
- Next.js 15 frontend with shadcn/ui components
- Vercel Blob for file storage
- **Enhanced Python pipeline** - 5-stage mechanism extraction workflow
- Real-time pipeline visualization with stage insights
- File-based state (no database)

**Enhanced Pipeline Features:**
1. **Mechanism Extraction** using abstraction ladder methodology
2. **Innovation Type Classification** via Doblin's 10 Types framework
3. **Jobs-to-be-Done Mapping** with quantified constraint elimination
4. **CPG-Specific Translation** focused on 5 core patterns
5. **Retail-Ready Opportunities** with speed-to-market metrics

**Development Status:**
- ✅ Original pipeline validated and operational
- ✅ **NEW: Enhanced prompts created** (`pipeline/prompts/stage*_prompt.py`)
- ✅ Mechanism extraction methodology integrated
- 🚧 Web interface implementation ready to begin
- 📋 CPG-specific optimizations defined

**Repository Structure:**
- `docs/architecture/` - Complete technical specifications
- `pipeline/` - **Enhanced** Python implementation (mechanism extraction)
- `pipeline/prompts/stage*_prompt.py` - **Enhanced stage prompts**
- `data/brand-profiles/` - Company YAML configurations
- `innovation-web/` - Next.js application (in development)
- `documentation/perplexity/` - Extraction methodology documentation

## Project Overview

This repository contains an **Enhanced Innovation Intelligence Pipeline** that extracts transferable innovation mechanisms from trend reports and generates brand-specific, retail-ready opportunities for CPG companies.

### 🔄 Pipeline Evolution: From Observation to Mechanism

**❌ OLD PIPELINE (Surface Level):**
- Stage 1: Extract inspirations → "Company X did Y"
- Stage 2: Identify trends → "Digital transformation is happening"
- Stage 3: Universal lessons → "Focus on customer experience"
- Stage 4: Brand context → "Our brand should consider digital"
- Stage 5: Opportunities → Generic innovation ideas

**✅ NEW ENHANCED PIPELINE (Mechanism Extraction):**
- Stage 1: **Mechanism Extraction** → HOW innovations work structurally
- Stage 2: **Innovation Anatomy** → Which of Doblin's 10 Types activated
- Stage 3: **Job Architecture** → Functional/Emotional/Social jobs + constraints
- Stage 4: **CPG Translation** → 5 patterns + retail viability + speed metrics
- Stage 5: **Retail-Ready Cards** → 30-second buyer pitch with metrics

## 🎯 Enhanced Pipeline Deep Dive

### Stage 1: Mechanism Extraction (Latent Factors)

**Purpose:** Extract HOW innovations work, not just what happened

**Methodology:**
- **Abstraction Ladder:** Climb from specific implementation to universal principle
- **Mechanism Types:** Unbundle, Combine, Remove Friction, Change Model, Reframe, etc.
- **Constraint Quantification:** Time (X→Y), Cost ($X→$Y), Knowledge, Access, Effort

**Example Output:**
```
Mechanism: "Subscription eliminates replenishment friction"
Type: Changed Model + Service Innovation
Constraint Eliminated: Time (45 min shopping → 0 min auto-delivery)
Structural Pattern: "When [recurring need] creates [effort burden],
                    subscription model eliminates friction"
```

### Stage 2: Innovation Anatomy (Doblin's 10 Types)

**Purpose:** Diagnose which dimensions of business were innovated

**Doblin's Framework:**
```
CONFIGURATION (Backend)     OFFERING (Product)      EXPERIENCE (Frontend)
1. Profit Model             5. Product Performance   7. Service
2. Network                  6. Product System        8. Channel
3. Structure                                        9. Brand
4. Process                                         10. Customer Engagement
```

**Why It Matters:**
- Single type = Easy to copy (LOW defensibility)
- 2-3 types = Harder to replicate (MEDIUM defensibility)
- 4+ types = Nearly impossible to copy (HIGH defensibility)

**Example:** Netflix innovated 7 types (Profit Model, Network, Process, Channel, Brand, etc.) making them uncopyable

### Stage 3: Jobs-to-be-Done Architecture

**Purpose:** Understand WHY customers "hire" innovations

**Three-Dimensional Job Mapping:**
```
FUNCTIONAL: "I need to [accomplish task] so that [outcome]"
EMOTIONAL: "I want to feel [specific emotion]"
SOCIAL: "I want to be perceived as [identity]"
```

**Example - RXBar:**
- Functional: "I need to know exactly what I'm eating"
- Emotional: "I want to feel in control of my nutrition"
- Social: "I want to be seen as no-BS, informed"

### Stage 4: CPG-Specific Brand Translation

**Purpose:** Apply mechanisms to specific brand reality

**The 5 Core CPG Innovation Patterns:**
1. **Better-For-You-ification** → Add protein, remove sugar, clean label
2. **Premiumization** → Craft story, 2x price, better ingredients
3. **Convenience Shift** → RTD, single-serve, grab-and-go
4. **Format Migration** → Bar→bite, powder→shot, new form factors
5. **Occasion Expansion** → Breakfast→snack, new consumption moments

**Retail Viability Gates:**
- Will Walmart/Target accept this? ✓/✗
- Can we achieve >35% margin? ✓/✗
- <12 month launch feasible? ✓/✗
- <$500K investment? ✓/✗

### Stage 5: Retail-Ready Opportunity Cards

**Purpose:** Generate buyer-ready concepts for immediate pitch

**30-Second Buyer Test:** Can you explain it to a Walmart buyer in half a minute?

**Required Metrics:**
- Price point: $X.XX
- Velocity target: X units/store/week
- Gross margin: XX%
- Launch timeline: X months

---

## 🏭 The Brand Contextualization Magic

### How Universal Mechanisms Become Brand-Specific

**The Formula:**
```
UNIVERSAL MECHANISM (from Stages 1-3)
×
BRAND SPECIFIC CONTEXT (portfolio, capabilities, positioning)
=
UNIQUE OPPORTUNITY (only THIS brand can execute)
```

### Real Example: Dollar Shave Club Mechanism Applied

**Universal Mechanism:** "Subscription eliminates replenishment friction"

**Different Brand Applications:**

**Lactalis (Dairy):**
- Can't ship milk weekly (spoilage)
- BUT: "Monthly Artisan Cheese Discovery Box" ($39.99/month)
- Solves: "I want to seem sophisticated when hosting"

**KIND Snacks:**
- Already in every store
- BUT: "KIND Office - B2B Snack Subscription" (100-pack variety)
- Solves: "Keep employees happy without vending machines"

**Hidden Valley Ranch:**
- Ranch doesn't run out monthly
- BUT: "Ranch Reserve - Quarterly Chef Collaborations" ($19.99/quarter)
- Solves: "I want to be adventurous but safe"

Same mechanism → Completely different executions based on brand reality

---

## 🚀 Why This Enhancement Matters

### The Competitive Advantage

**Traditional Approach:** "Let's copy what's trending"
- Result: Everyone launches the same me-too products
- Example: 50 CBD beverages that all failed

**Mechanism Extraction Approach:** "Let's understand WHY it works, then apply uniquely"
- Result: Differentiated innovations only you can execute
- Example: Blue Buffalo adapting meal kit mechanics for pet food toppers

### Expected Improvements

- **12x faster extraction:** 60 min manual → 5 min automated
- **10x better insights:** Mechanisms vs observations
- **5x faster to market:** CPG pattern focus
- **Higher retail acceptance:** Built-in viability gates

---

## Technical Implementation

**Enhanced Pipeline Files:**
- `pipeline/prompts/stage1_prompt.py` - Mechanism extraction
- `pipeline/prompts/stage2_prompt.py` - Innovation anatomy
- `pipeline/prompts/stage3_prompt.py` - Jobs architecture
- `pipeline/prompts/stage4_prompt.py` - CPG translation
- `pipeline/prompts/stage5_prompt.py` - Retail-ready cards

**Integration Steps:**
1. Update stage imports to use enhanced prompts
2. Test with sample documents
3. Validate mechanism extraction quality
4. Monitor retail viability scores

**Technical Architecture:**
- LangChain for LLM orchestration
- OpenRouter API (Claude Sonnet 4.5)
- Enhanced prompts with forcing functions
- Validation gates between stages
- CPG-specific scoring metrics

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

**Primary Target Market: CPG Mid-Market ($50M-$1B Revenue)**
- 2-5 person innovation teams (not 50-person R&D departments)
- Quarterly pipeline pressure from retail buyers
- Limited research budgets ($50K, not $500K)
- Need concepts ready for Walmart/Target in 90 days
- Risk-averse leadership requiring proven mechanisms

**Secondary Markets:**
- Management consulting innovation practices
- Innovation agencies serving CPG clients
- Corporate venture teams in food & beverage
- Private equity portfolio company innovation

**Core Value Proposition:**
- **Extract mechanisms, not observations** - Understand HOW innovations work
- **CPG-specific translation** - 5 proven patterns that retailers accept
- **Speed to shelf** - 12-month launch timeline focus
- **Retail-ready concepts** - Pass the 30-second buyer test
- **Brand differentiation** - Mechanisms only YOUR brand can execute

**Competitive Differentiation:**
- **vs. Trend Reports:** We extract mechanisms, not list observations
- **vs. Consultants:** $50K tool vs $500K engagement
- **vs. AI Tools:** CPG-specific with retail viability gates
- **vs. Internal Teams:** 12x faster with proven methodology

**Current Implementation Focus:**
- Enhanced pipeline with mechanism extraction
- Web MVP for demonstration and validation
- CPG-specific optimizations for mid-market
- Foundation for SaaS platform launch

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

### Testing Enhanced Pipeline:

```bash
# Test with original prompts (baseline)
python scripts/run_pipeline.py \
  --input-file data/test-docs/sample.pdf \
  --brand lactalis-canada \
  --run-id test-baseline

# Test with enhanced prompts (mechanism extraction)
python scripts/run_pipeline.py \
  --input-file data/test-docs/sample.pdf \
  --brand lactalis-canada \
  --run-id test-enhanced \
  --use-enhanced-prompts

# Compare outputs to see improvement in mechanism extraction
```

### Implementation Checklist:

**To activate enhanced pipeline:**
1. ✅ Enhanced prompts created in `pipeline/prompts/*_enhanced.py`
2. ⬜ Update stage files to import enhanced prompts
3. ⬜ Test mechanism extraction quality
4. ⬜ Validate Doblin's 10 Types classification
5. ⬜ Verify JTBD mapping accuracy
6. ⬜ Check CPG pattern translation
7. ⬜ Confirm retail viability scoring

### Quality Validation Metrics:

**Stage 1:** Mechanisms should be transferable across 3+ industries
**Stage 2:** Innovation types should map to 2-4 of Doblin's categories
**Stage 3:** Jobs should be specific with quantified constraints
**Stage 4:** Each opportunity should fit 1 of 5 CPG patterns
**Stage 5:** Cards should pass 30-second buyer pitch test