# Innovation Intelligence Pipeline Testing System - Architecture Document

**Version:** 1.0
**Date:** 2025-10-07
**Status:** Draft
**Aligned with:** PRD v1.0

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Architecture Principles](#3-architecture-principles)
4. [Technology Stack](#4-technology-stack)
5. [Pipeline Architecture](#5-pipeline-architecture)
6. [Data Models](#6-data-models)
7. [File Structure](#7-file-structure)
8. [Stage Specifications](#8-stage-specifications)
9. [Execution Flow](#9-execution-flow)
10. [Error Handling](#10-error-handling)
11. [Testing Strategy](#11-testing-strategy)
12. [Development Workflow](#12-development-workflow)

---

## 1. Introduction

### 1.1 Purpose

This architecture defines a **simple CLI-based Python tool** for validating the Innovation Intelligence Pipeline hypothesis. This is a **throwaway demo** designed for rapid validation (1-2 week build target), not a production system.

**Core Question:** Can an automated pipeline systematically transform market signals into brand-specific, actionable innovation opportunities worth $149-$1,500/month?

### 1.2 Scope

**In Scope:**
- Local Python CLI tool (`run_pipeline.py`)
- 5-stage LangChain pipeline (Input → Signal → Translation → Context → Opportunities)
- File-based storage (no database)
- Single test and batch execution modes
- Manual quality review with checklists
- 100 opportunity card generation (20 tests × 5 opportunities)

**Out of Scope:**
- Web UI or frontend
- Database or cloud storage
- Deployment infrastructure
- Real-time monitoring dashboards
- Automated quality scoring
- Production-grade error handling

### 1.3 Design Philosophy

> **"Make it work, then make it better"** - Focus on proving the transformation works, not building perfect software.

- **Simplicity over sophistication** - Hardcoded configurations acceptable
- **Local-first** - Everything runs on developer's machine
- **File-based** - All state persisted to filesystem
- **Manual intervention OK** - If a stage fails, manual retry is acceptable for 20 tests
- **Copy-paste patterns** - Use LangChain cookbook examples directly

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User (Developer)                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ Command: python run_pipeline.py --input X --brand Y
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     run_pipeline.py (CLI)                        │
│                                                                  │
│  - Parse arguments                                               │
│  - Load input document & brand profile                           │
│  - Create output directory                                       │
│  - Initialize logging                                            │
│  - Execute LangChain SequentialChain                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              LangChain SequentialChain                           │
│                                                                  │
│  Stage 1: Input Processing        (LLMChain)                    │
│           ↓                                                      │
│  Stage 2: Signal Amplification    (LLMChain)                    │
│           ↓                                                      │
│  Stage 3: General Translation     (LLMChain)                    │
│           ↓                                                      │
│  Stage 4: Brand Contextualization (LLMChain + Research Data)    │
│           ↓                                                      │
│  Stage 5: Opportunity Generation  (LLMChain + Jinja2)           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ├──────────────────┐
                  │                  │
                  ▼                  ▼
          ┌──────────────┐   ┌──────────────┐
          │  OpenRouter  │   │ File System  │
          │     API      │   │   Storage    │
          │              │   │              │
          │ Claude Sonnet│   │ Intermediate │
          │     4.5      │   │   Outputs    │
          └──────────────┘   └──────────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │   Results    │
                              │              │
                              │ 5 Opportunity│
                              │    Cards     │
                              └──────────────┘
```

### 2.2 Data Flow

```
INPUT DOCUMENT (PDF)
    ↓
[STAGE 1: Input Processing]
    → stage1/inspiration-analysis.md
    ↓
[STAGE 2: Signal Amplification]
    → stage2/trend-analysis.md
    ↓
[STAGE 3: General Translation]
    → stage3/universal-lessons.md
    ↓
[STAGE 4: Brand Contextualization] ← BRAND PROFILE (YAML)
    → stage4/brand-contextualization.md  ← RESEARCH DATA (Local Files)
    ↓
[STAGE 5: Opportunity Generation]
    → stage5/opportunity-1.md
    → stage5/opportunity-2.md
    → stage5/opportunity-3.md
    → stage5/opportunity-4.md
    → stage5/opportunity-5.md
    → stage5/opportunities-summary.md
```

---

## 3. Architecture Principles

### 3.1 Core Principles

1. **Sequential Execution** - Stages run in order, each using previous outputs as input
2. **Stateless Stages** - Each stage is independent, no shared state beyond I/O
3. **File-Based Persistence** - All intermediate outputs saved to disk for debugging
4. **Fail-Fast** - Fatal errors halt execution immediately with clear error messages
5. **Context Preservation** - LangChain memory maintains context across stages

### 3.2 Simplicity Constraints

- **No Database** - All data in YAML/JSON/Markdown files
- **No API Server** - Direct Python script execution only
- **No Async** - Synchronous execution sufficient for 20 tests
- **No Complex Error Recovery** - Log error and halt, manual investigation acceptable
- **No Optimization** - Prioritize readability over performance

---

## 4. Technology Stack

### 4.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Runtime** | Python | 3.10+ | Primary language |
| **LLM Framework** | LangChain | 0.1.0+ | Pipeline orchestration |
| **LLM Integration** | langchain-openai | 0.0.5+ | OpenRouter API client |
| **LLM Provider** | OpenRouter | latest | Unified API gateway |
| **LLM Model** | Claude Sonnet 4.5 | anthropic/claude-sonnet-4.5-20250514 | Primary reasoning model |
| **PDF Parsing** | pypdf | latest | Document ingestion |
| **Data Loading** | PyYAML | 6.0+ | Brand profile parsing |
| **Templating** | Jinja2 | 3.1+ | Opportunity card generation |
| **Validation** | Pydantic | 2.5+ | Data validation (optional) |

### 4.2 Python Dependencies

```txt
# requirements.txt
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.1
openai>=1.0.0
pypdf>=3.17.0
pyyaml>=6.0
jinja2>=3.1.3
python-dotenv>=1.0.0
pydantic>=2.5.0
```

### 4.3 Development Tools

- **Virtual Environment:** `venv` (Python standard library)
- **Package Manager:** `pip`
- **Version Control:** Git
- **Code Formatting:** Black (optional)
- **Linting:** Flake8 (optional)

---

## 5. Pipeline Architecture

### 5.1 LangChain Components

```python
# Simplified Architecture Diagram (Python pseudocode)

from langchain.chains import LLMChain, SequentialChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Initialize LLM
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-sonnet-4.5-20250514",
    temperature=0.5
)

# Define 5 stage chains
stage1_chain = LLMChain(
    llm=llm,
    prompt=stage1_prompt_template,
    output_key="stage1_output"
)

stage2_chain = LLMChain(
    llm=llm,
    prompt=stage2_prompt_template,
    output_key="stage2_output"
)

# ... stage3, stage4, stage5 chains

# Connect into sequential pipeline
pipeline = SequentialChain(
    chains=[stage1_chain, stage2_chain, stage3_chain, stage4_chain, stage5_chain],
    input_variables=["input_document", "brand_profile", "research_data"],
    output_variables=["stage1_output", "stage2_output", "stage3_output",
                     "stage4_output", "stage5_output"],
    verbose=True
)

# Execute
results = pipeline({
    "input_document": loaded_pdf_content,
    "brand_profile": loaded_brand_yaml,
    "research_data": loaded_research_files
})
```

### 5.2 Stage Isolation

Each stage is implemented as a separate module in `pipeline/stages/`:

```
pipeline/stages/
├── stage1_input_processing.py      # Returns inspiration analysis
├── stage2_signal_amplification.py  # Returns trend analysis
├── stage3_general_translation.py   # Returns universal lessons
├── stage4_brand_contextualization.py # Returns brand insights
└── stage5_opportunity_generation.py  # Returns 5 opportunity cards
```

**Each stage module exports:**
- `create_chain(llm)` - Returns configured LLMChain
- `get_prompt_template()` - Returns PromptTemplate
- `save_output(output, directory)` - Persists stage output to file

---

## 6. Data Models

### 6.1 Brand Profile Schema (YAML)

```yaml
# data/brand-profiles/{brand-id}.yaml

brand_name: "Lactalis Canada"
brand_id: "lactalis-canada"
country: "Canada"
industry: "Food & Beverage - Dairy"
positioning: "Premium dairy products with heritage craftsmanship and local sourcing"

product_portfolio:
  - "Cheese (Lactantia, Black Diamond, Cheestrings)"
  - "Butter and spreads"
  - "Milk and cream products"

target_customers:
  - "Health-conscious families"
  - "Premium food enthusiasts"
  - "Convenience seekers"

recent_innovations:
  - "Plant-based cheese alternatives launch (2024)"
  - "Sustainable packaging initiative"
  - "Lactose-free product line expansion"

strategic_priorities:
  - "Sustainability and carbon neutrality by 2030"
  - "Digital customer engagement"
  - "Premium product line expansion"

brand_values:
  - "Quality craftsmanship"
  - "Canadian heritage"
  - "Sustainability"
  - "Innovation"

research_data_path: "docs/web-search-setup/lactalis-canada-research.md"
```

**Note:** Brand profiles provide high-level context, but comprehensive research data is loaded separately from `docs/web-search-setup/` (see section 6.2).

### 6.2 Brand Research Data Structure (Markdown)

**Location:** `docs/web-search-setup/{brand-id}-research.md`

**Purpose:** Comprehensive, pre-researched brand intelligence that powers Stage 4 contextualization. This is the **critical differentiation data** that enables the pipeline to generate meaningfully different opportunities for each brand from the same input.

**File Structure:**

Each brand research file contains 8 strategic dimensions with ~46 subsections:

```markdown
# {Brand Name} - Comprehensive Brand Research
**Research Date:** 2025-10-07
**Researcher:** Claude (Innovation Intelligence System)
**Sources Reviewed:** 45+

## 1. Brand Overview & Positioning
### Official Positioning
### Brand Values
### Iconic Brand Portfolio
### Target Audience
### Current Campaigns (2024-2025)

## 2. Product Portfolio & Innovation
### Core Product Categories
### Flagship Products
### Recent Product Launches (2023-2025)

## 3. Recent Innovations (Last 18 Months)
### Product Innovations
### Sustainability Innovations
### Technology Innovations
### Marketing & Experience Innovations
### Partnership Innovations

## 4. Strategic Priorities & Business Strategy
### Publicly Stated Goals
### Growth Markets & Expansion Plans
### Digital Transformation Initiatives
### Sustainability Commitments & Targets

## 5. Target Customers & Market Positioning
### Demographics
### Psychographics
### Purchase Behaviors & Preferences
### Customer Journey Insights

## 6. Sustainability & Social Responsibility
### ESG Commitments
### Certifications & Standards
### Circular Economy Initiatives
### Community Engagement

## 7. Competitive Context & Market Trends
### Key Competitors
### Industry Dynamics
### Consumer Trends Affecting Brand
### Market Opportunities & Threats

## 8. Recent News & Market Signals (Last 6 Months)
### Press Releases & Announcements
### Media Coverage
### Analyst Reports
### Social Media Trends

## Research Methodology
[Research approach and source types]

## Key Insights Summary (For Pipeline Context)
[Executive summary of most relevant insights for opportunity generation]
```

**File Statistics:**
- **Size:** ~550-720 lines per brand (35-48KB)
- **Sources:** 45+ cited sources per brand (news, press releases, industry reports, company websites)
- **Content Depth:** ~46 subsections with specific examples, data points, and strategic insights
- **Recency:** Focus on 2023-2025 innovations and last 6 months of news
- **Citation Format:** URLs provided for source verification

**Available Research Files:**
- `lactalis-canada-research.md` (545 lines, 36.7KB)
- `mccormick-usa-research.md` (720 lines, 48.1KB)
- `columbia-sportswear-research.md` (574 lines, 43.1KB)
- `decathlon-research.md` (603 lines, 44.9KB)

**Stage 4 Loading Pattern:**

```python
def load_brand_research(brand_id):
    """Load comprehensive brand research from markdown file."""
    research_path = Path(f"docs/web-search-setup/{brand_id}-research.md")

    if not research_path.exists():
        logging.warning(f"Research file not found: {research_path}")
        return ""

    research_content = research_path.read_text(encoding='utf-8')

    # Optional: Extract key sections for token efficiency
    # Could parse specific sections (e.g., Recent Innovations, Strategic Priorities)
    # For MVP: Load entire file into Stage 4 prompt context

    return research_content
```

**Critical Notes:**
- Research files are **pre-generated** and **static** - no live web search during pipeline execution
- Files must be updated manually/periodically to maintain currency
- Missing research file is **non-fatal** - Stage 4 proceeds with brand profile only (degraded mode)
- Research content is injected directly into Stage 4 LLM prompt for contextualization

### 6.3 Input Manifest Schema (YAML)

```yaml
# data/input-manifest.yaml

inputs:
  - id: "savannah-bananas"
    filename: "savannah-bananas.pdf"
    type: "case_study"
    description: "Baseball team creating fan entertainment experience"
    industry: "Sports & Entertainment"

  - id: "premium-fast-food"
    filename: "premium-fast-food-trend.pdf"
    type: "trend_report"
    description: "Premiumization trend in fast food industry"
    industry: "Food & Beverage"
```

### 6.4 Opportunity Card Schema (Markdown + Frontmatter)

```markdown
---
opportunity_id: "savannah-bananas-lactalis-001"
brand: "lactalis-canada"
input_source: "savannah-bananas"
timestamp: "2025-10-07T14:23:45Z"
tags: ["customer-experience", "entertainment", "brand-building"]
stage4_insight_source: "Brand contextualization analysis - experiential marketing for dairy products"
---

# Interactive Dairy Farm Virtual Tours

## Description

Create immersive virtual farm tours that transform dairy product education into entertainment, mirroring Savannah Bananas' approach of turning a commodity experience (baseball) into must-see entertainment. Lactalis can leverage its Canadian heritage farms to create engaging digital experiences that build brand loyalty while educating consumers about sustainable dairy practices.

The experience would feature 360-degree farm tours, meet-the-farmer video series, and interactive cheese-making demonstrations. This addresses growing consumer demand for transparency and connection to food sources while differentiating Lactalis products in competitive dairy aisles.

## Actionability

- Partner with 3-5 heritage supplier farms to film immersive video content (Q1 2026)
- Develop mobile-first web experience with QR codes on premium product packaging
- Create monthly "Meet Your Farmer" livestream events with Q&A sessions
- Integrate with existing loyalty program to reward engagement
- Pilot with Black Diamond cheese line before expanding portfolio-wide

## Visual Description

Split-screen image: Left side shows traditional cheese aging cave with warm lighting and wooden shelves, right side shows modern family watching virtual tour on tablet in kitchen. QR code visible on cheese package. Warm, inviting color palette emphasizing heritage and technology harmony.

## Follow-up Prompts

1. How might we measure the ROI of virtual farm tours on brand perception and purchase intent?
2. What partnerships with Canadian tourism boards or agricultural organizations could amplify this initiative?
3. How could we extend this experience into retail environments or special events?
```

---

## 7. File Structure

### 7.1 Complete Repository Layout

```
innovation-intelligence-system/
├── .env                                # Environment variables (API keys)
├── .env.template                       # Template for environment setup
├── .gitignore                          # Git ignore rules
├── README.md                           # Setup and usage instructions
├── requirements.txt                    # Python dependencies
├── run_pipeline.py                     # Main CLI execution script
│
├── pipeline/                           # Pipeline implementation
│   ├── __init__.py
│   ├── chains.py                       # SequentialChain setup
│   ├── utils.py                        # Helper functions
│   │
│   ├── stages/                         # Stage implementations
│   │   ├── __init__.py
│   │   ├── stage1_input_processing.py
│   │   ├── stage2_signal_amplification.py
│   │   ├── stage3_general_translation.py
│   │   ├── stage4_brand_contextualization.py
│   │   └── stage5_opportunity_generation.py
│   │
│   └── prompts/                        # PromptTemplate definitions
│       ├── __init__.py
│       ├── stage1_prompt.py
│       ├── stage2_prompt.py
│       ├── stage3_prompt.py
│       ├── stage4_prompt.py
│       └── stage5_prompt.py
│
├── templates/                          # Jinja2 templates
│   └── opportunity-card.md.j2          # Opportunity card markdown template
│
├── data/                               # All data files (NOT committed to git)
│   ├── input-manifest.yaml             # Input document registry
│   ├── brand-profiles/                 # Brand YAML files
│   │   ├── lactalis-canada.yaml
│   │   ├── mccormick-usa.yaml
│   │   ├── columbia-sportswear.yaml
│   │   └── decathlon.yaml
│   │
│   └── test-outputs/                   # Test execution results
│       ├── {input-id}-{brand-id}-{timestamp}/
│       │   ├── logs/
│       │   │   ├── pipeline.log
│       │   │   └── errors.log
│       │   ├── stage1/
│       │   │   └── inspiration-analysis.md
│       │   ├── stage2/
│       │   │   └── trend-analysis.md
│       │   ├── stage3/
│       │   │   └── universal-lessons.md
│       │   ├── stage4/
│       │   │   └── brand-contextualization.md
│       │   └── stage5/
│       │       ├── opportunity-1.md
│       │       ├── opportunity-2.md
│       │       ├── opportunity-3.md
│       │       ├── opportunity-4.md
│       │       ├── opportunity-5.md
│       │       └── opportunities-summary.md
│
├── documentation/                      # Input documents + research
│   ├── document/                       # Test input PDFs
│   │   ├── savannah-bananas.pdf
│   │   ├── premium-fast-food-trend.pdf
│   │   ├── combined-trends-nonalcoholic-sacred-sync.pdf
│   │   ├── cat-dad-campaign.pdf
│   │   └── qr-garment-resale.pdf
│   │
│   └── innovation-research/            # TRIZ/SIT/SPECTRE frameworks (reference only)
│
├── docs/                               # Documentation
│   ├── architecture.md                 # This document
│   ├── prd.md                          # Product requirements
│   ├── brand-profile-schema.md         # Brand YAML documentation
│   ├── opportunity-card-format.md      # Opportunity card spec
│   ├── stage-1-3-quality-checklist.md  # Manual review checklist
│   ├── differentiation-rubric.md       # Brand comparison scoring
│   ├── opportunity-quality-rubric.md   # Final quality assessment
│   │
│   └── web-search-setup/               # Pre-existing brand research data
│       ├── lactalis-canada-research.md       # 545 lines, 8 sections, 46 subsections
│       ├── mccormick-usa-research.md         # 720 lines, 8 sections, 46 subsections
│       ├── columbia-sportswear-research.md   # 574 lines, 8 sections, 46 subsections
│       ├── decathlon-research.md             # 603 lines, 8 sections, 46 subsections
│       └── brand-research-agent-prompt.md    # Research methodology template
│
└── tests/                              # Test scripts
    ├── test_input_loading.py           # Validate input documents load
    ├── test_brand_profiles.py          # Validate brand YAML syntax
    ├── test_stage.py                   # Test individual stages
    ├── test_stages_1_3.py              # Integration test Stages 1-3
    └── test_stage4_differentiation.py  # Multi-brand comparison test
```

### 7.2 Output Directory Naming Convention

```
data/test-outputs/{input-id}-{brand-id}-{timestamp}/

Example:
data/test-outputs/savannah-bananas-lactalis-20251007-142345/
```

**Rationale:** Timestamp ensures unique directories for re-runs, input-brand prefix enables easy filtering.

---

## 8. Stage Specifications

### 8.1 Stage 1: Input Processing

**Purpose:** Extract key inspiration elements from input document.

**Implementation:**
```python
# pipeline/stages/stage1_input_processing.py

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def create_chain(llm):
    prompt = PromptTemplate(
        input_variables=["input_document"],
        template=get_prompt_template()
    )
    return LLMChain(llm=llm, prompt=prompt, output_key="stage1_output")

def get_prompt_template():
    return """You are analyzing an innovation case study or trend report.

INPUT DOCUMENT:
{input_document}

TASK:
1. Review the document thoroughly
2. Identify 3-5 key inspiration elements (innovations, strategies, successful tactics)
3. For each inspiration, note:
   - What it is (concise description)
   - Why it's interesting (key insight)
   - Potential applicability (where this could be applied)
4. Summarize overall context and significance

OUTPUT FORMAT:
# Document Overview
[2-3 sentence summary]

# Key Inspirations

## 1. [Inspiration Title]
- **What:** [Description]
- **Why Interesting:** [Key insight]
- **Potential Applicability:** [Where this could apply]

[Repeat for 3-5 inspirations]

# Context Notes
[Any additional relevant context]
"""

def save_output(output, directory):
    filepath = directory / "stage1" / "inspiration-analysis.md"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(output)
```

**Model Configuration:**
- Temperature: 0.3 (consistency over creativity)
- Max Tokens: 2000

**Input:** Raw PDF content (via PyPDFLoader)
**Output:** `stage1/inspiration-analysis.md`

---

### 8.2 Stage 2: Signal Amplification

**Purpose:** Extract trend patterns from document content (no external data).

**Implementation:**
```python
# pipeline/stages/stage2_signal_amplification.py

def get_prompt_template():
    return """You are a trend analyst identifying patterns in innovation signals.

INSPIRATION ANALYSIS (from Stage 1):
{stage1_output}

ORIGINAL DOCUMENT CONTENT:
{input_document}

TASK:
1. Analyze the inspirations for recurring themes and patterns
2. Identify underlying trends:
   - Consumer behavior shifts
   - Industry movements
   - Emerging needs or gaps
   - Technological or cultural changes
3. Categorize trends by type: Behavioral, Technological, Cultural, Economic
4. Assess signal strength: High (multiple evidence points), Medium (some evidence), Low (emerging/weak signal)

IMPORTANT: Extract trends ONLY from the document content provided. Do not reference external knowledge or social media data.

OUTPUT FORMAT:
# Identified Trends

## [Trend Name]
- **Category:** [Behavioral/Technological/Cultural/Economic]
- **Signal Strength:** [High/Medium/Low]
- **Description:** [2-3 sentence explanation]
- **Evidence from Document:** [Specific references]

[Repeat for 3-5 trends]

# Signal Strength Assessment
[Overall analysis of trend reliability]
"""
```

**Model Configuration:**
- Temperature: 0.4
- Max Tokens: 2500

**Input:** Stage 1 output + original document
**Output:** `stage2/trend-analysis.md`

---

### 8.3 Stage 3: General Translation

**Purpose:** Translate inspirations + trends into brand-agnostic universal principles.

**Implementation:**
```python
# pipeline/stages/stage3_general_translation.py

def get_prompt_template():
    return """You are a strategic innovation consultant translating specific examples into universal principles.

INSPIRATION ANALYSIS:
{stage1_output}

TREND ANALYSIS:
{stage2_output}

TASK:
1. Synthesize inspirations + trends into universal lessons
2. De-contextualize: Remove specific brand/industry references
3. Extract underlying principles that work across contexts
4. Generate 5-7 universal lessons
5. For each lesson:
   - State the principle clearly
   - Explain why it works (psychological/strategic rationale)
   - Suggest where it could apply (broad categories)

OPTIONAL FRAMEWORKS (reference if helpful):
- TRIZ: Contradiction resolution, inventive principles
- SIT: Subtraction, multiplication, division, task unification, attribute dependency
- Biomimicry: Nature-inspired solutions
- Lateral thinking: Alternative perspectives

OUTPUT FORMAT:
# Universal Lessons

## 1. [Principle Name]
**Principle:** [Clear statement of the universal principle]

**Why It Works:** [2-3 sentences on psychological/strategic rationale]

**Applicability:** [Industries/contexts where this applies]

[Repeat for 5-7 lessons]
"""
```

**Model Configuration:**
- Temperature: 0.5 (balance abstraction and specificity)
- Max Tokens: 3000

**Input:** Stage 1 + Stage 2 outputs
**Output:** `stage3/universal-lessons.md`

---

### 8.4 Stage 4: Brand Contextualization (Critical Stage)

**Purpose:** Transform universal lessons into brand-specific strategic insights using brand profile + research data.

**Implementation:**
```python
# pipeline/stages/stage4_brand_contextualization.py

def create_chain(llm, brand_profile, research_data):
    prompt = PromptTemplate(
        input_variables=["stage3_output", "brand_profile", "research_data"],
        template=get_prompt_template()
    )
    return LLMChain(llm=llm, prompt=prompt, output_key="stage4_output")

def get_prompt_template():
    return """You are a brand innovation strategist customizing universal insights for a specific brand.

BRAND PROFILE:
{brand_profile}

COMPREHENSIVE BRAND RESEARCH DATA (8 sections: Positioning, Portfolio, Recent Innovations, Strategy, Customers, Sustainability, Competitive Context, Recent News):
{research_data}

UNIVERSAL LESSONS (from Stage 3):
{stage3_output}

TASK:
1. Review brand profile and research data thoroughly
2. Review universal lessons from Stage 3
3. For each lesson, analyze: How does this apply to THIS specific brand?
   - Consider their product portfolio
   - Consider their target customers
   - Consider their strategic priorities
   - Consider their recent innovations and market context
4. Generate 5-7 brand-specific strategic insights
5. Each insight must:
   - Reference specific products/categories from the brand
   - Address their unique customer needs
   - Align with their strategic priorities
   - Be actionable within their capabilities

OUTPUT FORMAT:
# Brand Context Summary
[2-3 sentences synthesizing brand profile + research data]

# Brand-Specific Strategic Insights

## 1. [Insight Title]
**Universal Principle Applied:** [Which lesson from Stage 3]

**Brand-Specific Application:** [How this specifically applies to {brand_name}]

**Strategic Rationale:** [Why this matters for this brand's customers/strategy]

**Product/Category Relevance:** [Which specific products/categories this affects]

[Repeat for 5-7 insights]

# Prioritization Guidance
[Which insights are highest priority given brand's current strategic context]
"""

def load_research_data(brand_id, research_base_path="docs/web-search-setup"):
    """Load comprehensive brand research from single markdown file.

    Each brand has a pre-generated comprehensive research file containing 8 sections:
    1. Brand Overview & Positioning
    2. Product Portfolio & Innovation
    3. Recent Innovations (Last 18 Months)
    4. Strategic Priorities & Business Strategy
    5. Target Customers & Market Positioning
    6. Sustainability & Social Responsibility
    7. Competitive Context & Market Trends
    8. Recent News & Market Signals (Last 6 Months)

    File size: ~550-720 lines (35-48KB) with 45+ cited sources.
    """
    research_filepath = Path(research_base_path) / f"{brand_id}-research.md"

    if not research_filepath.exists():
        logging.warning(f"No research data found: {research_filepath}")
        logging.warning(f"Proceeding with brand profile only (degraded mode)")
        return ""

    logging.info(f"Loading brand research: {research_filepath}")
    research_content = research_filepath.read_text(encoding='utf-8')

    # Log file statistics
    line_count = len(research_content.split('\n'))
    size_kb = len(research_content.encode('utf-8')) / 1024
    logging.info(f"Research loaded: {line_count} lines, {size_kb:.1f}KB")

    return research_content
```

**Model Configuration:**
- Temperature: 0.6 (higher creativity for contextualization)
- Max Tokens: 3500

**Input:** Stage 3 output + Brand Profile YAML + Research Data (local files)
**Output:** `stage4/brand-contextualization.md`

**Critical Notes:**
- This is the **differentiation stage** - same input must produce different outputs per brand
- **Research data is comprehensive** - Each brand has ~550-720 lines of detailed intelligence across 8 strategic dimensions with 45+ cited sources
- **Research data loading is offline** - All files pre-generated in `docs/web-search-setup/`, no live web searches during pipeline execution
- **Graceful degradation:** If research data missing, Stage 4 proceeds with brand profile only (logs warning)
- **Token consideration:** Research files are 35-48KB each - ensure LLM context window can accommodate Stage 3 output + brand profile + full research data

---

### 8.5 Stage 5: Opportunity Generation

**Purpose:** Generate exactly 5 distinct, actionable innovation opportunities from brand insights.

**Implementation:**
```python
# pipeline/stages/stage5_opportunity_generation.py

from jinja2 import Template

def get_prompt_template():
    return """You are an innovation opportunity generator creating actionable ideas for a specific brand.

BRAND-SPECIFIC INSIGHTS (from Stage 4):
{stage4_output}

BRAND CONTEXT:
{brand_profile}

TASK:
Generate exactly 5 distinct, actionable innovation opportunities based on the strategic insights.

REQUIREMENTS for each opportunity:
1. **Distinct:** Each opportunity must be meaningfully different (not variations of same idea)
2. **Actionable:** Include 3-5 concrete next steps
3. **Brand-Relevant:** Reference specific brand products/customers/strategy
4. **Implementable:** No science fiction - feasible within 12-18 months
5. **Customer Value:** Clear benefit to target customers
6. **Diverse Types:** Span different innovation categories:
   - Product innovation
   - Service innovation
   - Marketing/communication innovation
   - Experience innovation
   - Partnership/ecosystem innovation

OUTPUT FORMAT (JSON):
{{
  "opportunities": [
    {{
      "title": "5-10 word concise title",
      "description": "2-3 paragraph description explaining the opportunity, why it's relevant, and how it addresses brand needs",
      "actionability": [
        "Concrete next step 1",
        "Concrete next step 2",
        "Concrete next step 3",
        "Concrete next step 4 (optional)",
        "Concrete next step 5 (optional)"
      ],
      "visual_description": "Description of suggested visual/image for this opportunity card",
      "follow_up_prompts": [
        "Question to explore ROI or measurement",
        "Question to explore partnerships or resources",
        "Question to explore implementation or scaling"
      ],
      "innovation_type": "product|service|marketing|experience|partnership",
      "stage4_insight_source": "Which Stage 4 insight inspired this opportunity"
    }}
  ]
}}

Generate all 5 opportunities in this JSON format.
"""

def generate_opportunity_cards(opportunities_json, brand_id, input_id, output_dir):
    """Generate markdown files for each opportunity using Jinja2 template."""
    template_path = Path("templates/opportunity-card.md.j2")
    template = Template(template_path.read_text())

    opportunities = json.loads(opportunities_json)["opportunities"]

    for i, opp in enumerate(opportunities, 1):
        markdown = template.render(
            opportunity_id=f"{input_id}-{brand_id}-{i:03d}",
            brand=brand_id,
            input_source=input_id,
            timestamp=datetime.now().isoformat(),
            tags=["innovation", opp["innovation_type"]],
            title=opp["title"],
            description=opp["description"],
            actionability=opp["actionability"],
            visual_description=opp["visual_description"],
            follow_up_prompts=opp["follow_up_prompts"],
            stage4_insight_source=opp["stage4_insight_source"]
        )

        filepath = output_dir / f"opportunity-{i}.md"
        filepath.write_text(markdown)

    # Generate summary file
    summary = generate_summary(opportunities)
    (output_dir / "opportunities-summary.md").write_text(summary)
```

**Model Configuration:**
- Temperature: 0.7 (highest creativity for opportunity generation)
- Max Tokens: 4000

**Input:** Stage 4 output + Brand Profile
**Output:**
- `stage5/opportunity-1.md` through `opportunity-5.md`
- `stage5/opportunities-summary.md`

---

## 9. Execution Flow

### 9.1 Main Execution Script

```python
# run_pipeline.py

import argparse
import logging
from pathlib import Path
from datetime import datetime

from pipeline.chains import create_pipeline
from pipeline.utils import (
    load_input_document,
    load_brand_profile,
    load_research_data,
    create_output_directory,
    setup_logging
)

def main():
    parser = argparse.ArgumentParser(description="Innovation Intelligence Pipeline")
    parser.add_argument("--input", help="Input document ID (from input-manifest.yaml)")
    parser.add_argument("--brand", help="Brand profile ID (without .yaml extension)")
    parser.add_argument("--batch", action="store_true", help="Run all 20 test scenarios")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.batch:
        run_batch_tests(args.verbose)
    elif args.input and args.brand:
        run_single_test(args.input, args.brand, args.verbose)
    else:
        parser.print_help()
        exit(1)

def run_single_test(input_id, brand_id, verbose=False):
    """Execute pipeline for single input/brand combination."""

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = create_output_directory(input_id, brand_id, timestamp)

    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(output_dir / "logs", log_level)

    logging.info(f"Starting pipeline: {input_id} + {brand_id}")

    try:
        # Load inputs
        input_doc = load_input_document(input_id)
        brand_profile = load_brand_profile(brand_id)
        research_data = load_research_data(brand_id)

        # Create and execute pipeline
        pipeline = create_pipeline(output_dir)

        results = pipeline({
            "input_document": input_doc,
            "brand_profile": brand_profile,
            "research_data": research_data,
            "brand_id": brand_id,
            "input_id": input_id
        })

        logging.info(f"Pipeline completed successfully")
        logging.info(f"Results saved to: {output_dir}")

        return results

    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise

def run_batch_tests(verbose=False):
    """Execute all 20 test scenarios (5 inputs × 4 brands)."""

    from pipeline.utils import load_input_manifest

    manifest = load_input_manifest()
    brands = ["lactalis-canada", "mccormick-usa", "columbia-sportswear", "decathlon"]

    results = []
    total_tests = len(manifest["inputs"]) * len(brands)

    print(f"Starting batch execution: {total_tests} tests")

    for i, input_item in enumerate(manifest["inputs"], 1):
        for j, brand_id in enumerate(brands, 1):
            test_num = (i - 1) * len(brands) + j
            print(f"\n[{test_num}/{total_tests}] Running: {input_item['id']} + {brand_id}")

            try:
                result = run_single_test(input_item["id"], brand_id, verbose)
                results.append({
                    "input": input_item["id"],
                    "brand": brand_id,
                    "status": "success",
                    "output_dir": result["output_dir"]
                })
            except Exception as e:
                logging.error(f"Test failed: {input_item['id']} + {brand_id}: {str(e)}")
                results.append({
                    "input": input_item["id"],
                    "brand": brand_id,
                    "status": "failed",
                    "error": str(e)
                })

    # Generate batch summary
    generate_batch_summary(results)

    print(f"\nBatch execution complete: {sum(1 for r in results if r['status'] == 'success')}/{total_tests} successful")

if __name__ == "__main__":
    main()
```

### 9.2 Execution Commands

**Single Test:**
```bash
python run_pipeline.py --input savannah-bananas --brand lactalis-canada
```

**Batch Execution:**
```bash
python run_pipeline.py --batch
```

**Debug Mode:**
```bash
python run_pipeline.py --input savannah-bananas --brand lactalis-canada --verbose
```

### 9.3 Execution Time Expectations

| Operation | Expected Time |
|-----------|--------------|
| Single test (all 5 stages) | 5-10 minutes |
| Batch execution (20 tests) | 100-200 minutes (1.5-3.5 hours) |
| Stage 1-3 (per test) | 2-4 minutes |
| Stage 4 (per test) | 1-2 minutes |
| Stage 5 (per test) | 2-4 minutes |

**Rationale:** Sequential LLM API calls with ~30-60 second latency per stage.

---

## 10. Error Handling

### 10.1 Error Classification

| Error Type | Severity | Handling Strategy |
|------------|----------|-------------------|
| **Missing input file** | Fatal | Halt immediately, clear error message |
| **Missing brand profile** | Fatal | Halt immediately, clear error message |
| **Missing research data** | Warning | Log warning, proceed with brand profile only |
| **LLM API timeout** | Retryable | Retry up to 3 times with exponential backoff |
| **LLM API rate limit** | Retryable | Wait and retry (respect rate limit headers) |
| **Invalid YAML syntax** | Fatal | Halt immediately, show YAML validation error |
| **Stage output empty** | Fatal | Halt immediately, log LLM response |
| **JSON parsing failure (Stage 5)** | Fatal | Halt immediately, show raw LLM output |

### 10.2 Error Handling Implementation

```python
# pipeline/utils.py

import logging
import time
from functools import wraps

def retry_on_api_error(max_retries=3, backoff_factor=2):
    """Decorator for retrying LLM API calls with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise

                    wait_time = backoff_factor ** attempt
                    logging.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        return wrapper
    return decorator

class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass

class InputError(PipelineError):
    """Error loading input document or brand profile."""
    pass

class StageExecutionError(PipelineError):
    """Error during stage execution."""
    def __init__(self, stage_num, message, llm_output=None):
        self.stage_num = stage_num
        self.llm_output = llm_output
        super().__init__(f"Stage {stage_num} failed: {message}")
```

### 10.3 Logging Configuration

```python
# pipeline/utils.py

def setup_logging(log_dir, level=logging.INFO):
    """Configure logging for pipeline execution."""
    log_dir.mkdir(parents=True, exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler (detailed)
    file_handler = logging.FileHandler(log_dir / "pipeline.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Error file handler
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
```

---

## 11. Testing Strategy

### 11.1 Test Types

1. **Unit Tests** - Test individual stage chains in isolation
2. **Integration Tests** - Test stage sequences (1-3, 1-4, full pipeline)
3. **Data Validation Tests** - Verify YAML/JSON loading and schema validation
4. **Manual Quality Tests** - Human review using scoring rubrics

### 11.2 Unit Test Example

```python
# tests/test_stage1.py

import pytest
from pathlib import Path
from pipeline.stages.stage1_input_processing import create_chain, save_output
from langchain_openai import ChatOpenAI
from unittest.mock import Mock

def test_stage1_chain_creation():
    """Test Stage 1 chain can be created."""
    llm = Mock(spec=ChatOpenAI)
    chain = create_chain(llm)

    assert chain is not None
    assert chain.output_key == "stage1_output"

def test_stage1_with_mock_input():
    """Test Stage 1 with mock input document."""
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm.return_value = "# Document Overview\nTest output..."

    chain = create_chain(mock_llm)
    result = chain({"input_document": "Mock PDF content about innovation..."})

    assert "stage1_output" in result
    assert len(result["stage1_output"]) > 0

def test_stage1_output_saving(tmp_path):
    """Test Stage 1 output is saved correctly."""
    output_content = "# Document Overview\nTest output..."
    save_output(output_content, tmp_path)

    saved_file = tmp_path / "stage1" / "inspiration-analysis.md"
    assert saved_file.exists()
    assert saved_file.read_text() == output_content
```

### 11.3 Integration Test Example

```python
# tests/test_stages_1_3.py

import pytest
from pipeline.chains import create_pipeline
from pipeline.utils import load_input_document

def test_stages_1_3_integration(tmp_path):
    """Test Stages 1-3 execute successfully in sequence."""

    # Load test input
    input_doc = load_input_document("savannah-bananas")

    # Create pipeline (Stages 1-3 only)
    pipeline = create_pipeline(tmp_path, stages=[1, 2, 3])

    # Execute
    results = pipeline({"input_document": input_doc})

    # Verify outputs exist
    assert (tmp_path / "stage1" / "inspiration-analysis.md").exists()
    assert (tmp_path / "stage2" / "trend-analysis.md").exists()
    assert (tmp_path / "stage3" / "universal-lessons.md").exists()

    # Verify outputs have content
    stage3_content = (tmp_path / "stage3" / "universal-lessons.md").read_text()
    assert "Universal Lessons" in stage3_content
    assert len(stage3_content) > 500  # Non-trivial content
```

### 11.4 Manual Quality Tests

**Quality Checklists:**
- `docs/stage-1-3-quality-checklist.md` - Review inspiration/trend/lesson quality
- `docs/differentiation-rubric.md` - Assess Stage 4 brand differentiation (70%+ unique)
- `docs/opportunity-quality-rubric.md` - Score final opportunities (novelty, actionability, relevance, specificity)

**Manual Test Execution:**
1. Run integration test: `python tests/test_stages_1_3.py`
2. Review outputs using checklist
3. Document quality issues in test results
4. Refine prompts based on findings
5. Re-test and verify improvements

---

## 12. Development Workflow

### 12.1 Initial Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd innovation-intelligence-system

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.template .env
# Edit .env and add your OPENROUTER_API_KEY

# 5. Verify setup
python -c "import langchain; from langchain_openai import ChatOpenAI; print('Environment ready')"

# 6. Run initial test
python run_pipeline.py --input savannah-bananas --brand lactalis-canada
```

### 12.2 Iterative Development Workflow

**Stage Development Cycle:**
1. **Implement stage** - Create stage module in `pipeline/stages/`
2. **Write prompt** - Define PromptTemplate in `pipeline/prompts/`
3. **Unit test** - Create test in `tests/` and verify stage works in isolation
4. **Integration test** - Run stage in full pipeline context
5. **Manual review** - Check output quality against rubric
6. **Prompt refinement** - Iterate on prompt based on quality review
7. **Re-test** - Verify improvements, commit when satisfied

**Example Stage Development:**
```bash
# Step 1: Implement Stage 1
vim pipeline/stages/stage1_input_processing.py
vim pipeline/prompts/stage1_prompt.py

# Step 2: Unit test
python -m pytest tests/test_stage1.py -v

# Step 3: Integration test
python tests/test_stages_1_3.py

# Step 4: Manual quality review
cat data/test-outputs/savannah-bananas-lactalis-*/stage1/inspiration-analysis.md
# Review against docs/stage-1-3-quality-checklist.md

# Step 5: Refine prompt if needed
vim pipeline/prompts/stage1_prompt.py

# Step 6: Re-test
python run_pipeline.py --input savannah-bananas --brand lactalis-canada

# Step 7: Commit when satisfied
git add pipeline/stages/stage1_input_processing.py pipeline/prompts/stage1_prompt.py
git commit -m "Implement Stage 1: Input Processing"
```

### 12.3 Validation Testing Workflow

**After Epic 4 (all stages implemented):**

```bash
# 1. Run full batch test
python run_pipeline.py --batch

# 2. Review batch summary
cat data/test-outputs/batch-summary.md

# 3. Sample 20 opportunities for quality review
python scripts/sample_opportunities.py --count 20 --output quality-assessment.csv

# 4. Manual scoring
# Fill out quality-assessment.csv with scores (1-5 for each dimension)

# 5. Analyze results
python scripts/analyze_quality.py --input quality-assessment.csv

# 6. Document findings
vim docs/validation-results.md

# 7. Make recommendation (proceed/pivot/iterate)
```

### 12.4 Prompt Engineering Best Practices

1. **Start simple** - Get basic functionality working before optimizing
2. **Use examples** - Include 1-2 examples in prompts for clarity
3. **Be specific** - Exact output format requirements prevent parsing errors
4. **Test edge cases** - Try shortest/longest inputs, different document types
5. **Version prompts** - Git commit after each prompt refinement
6. **Document rationale** - Comment why specific prompt instructions were added

---

## Appendix A: Environment Variables

```bash
# .env.template

# OpenRouter API Configuration
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Model Configuration
DEFAULT_MODEL=anthropic/claude-sonnet-4.5-20250514
DEFAULT_TEMPERATURE=0.5

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

---

## Appendix B: Cost Estimation

### B.1 Token Usage Estimates

| Stage | Input Tokens (avg) | Output Tokens (avg) | Cost per Run (Claude Sonnet 4.5) |
|-------|-------------------|--------------------|---------------------------------|
| Stage 1 | 5,000 | 1,500 | $0.0375 |
| Stage 2 | 2,000 | 1,000 | $0.021 |
| Stage 3 | 3,000 | 2,000 | $0.039 |
| Stage 4 | 4,000 | 2,000 | $0.042 |
| Stage 5 | 3,000 | 3,000 | $0.054 |
| **Total per test** | **17,000** | **9,500** | **$0.194** |

**Full batch (20 tests):** ~$3.88

**Pricing (Claude Sonnet 4.5 via OpenRouter):**
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens

### B.2 Cost Optimization Strategies

1. **Use cheaper models for early stages** - DeepSeek ($0.14/1M) for Stages 1-2
2. **Cache brand profiles** - Reduce repeated token usage
3. **Optimize prompts** - Remove unnecessary instructions
4. **Token limits** - Set max_tokens per stage to prevent runaway generation

---

## Appendix C: Troubleshooting Guide

### C.1 Common Issues

**Problem:** `ModuleNotFoundError: No module named 'langchain'`
```bash
# Solution: Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** `OpenRouter API authentication failed`
```bash
# Solution: Verify API key in .env file
cat .env | grep OPENROUTER_API_KEY
# Test API key manually:
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_KEY_HERE"
```

**Problem:** Stage output is empty or truncated
```bash
# Solution: Check LLM max_tokens setting, increase if needed
# Edit pipeline/stages/stageX_*.py and increase max_tokens parameter
```

**Problem:** `FileNotFoundError` when loading brand profile
```bash
# Solution: Verify brand ID matches filename (without .yaml)
ls data/brand-profiles/
# Correct: python run_pipeline.py --brand lactalis-canada
# Wrong: python run_pipeline.py --brand lactalis-canada.yaml
```

**Problem:** Pipeline hangs on Stage 4
```bash
# Solution: Check research data loading, may be reading large files
# Add verbose logging:
python run_pipeline.py --input X --brand Y --verbose
# Check logs/pipeline.log for details
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-07 | Product Owner | Initial architecture aligned with PRD v1.0 |

---

**End of Architecture Document**
