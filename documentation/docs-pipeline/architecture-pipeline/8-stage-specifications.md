# 8. Stage Specifications

## 8.1 Stage 1: Input Processing

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

# 1. [Inspiration Title]
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

## 8.2 Stage 2: Signal Amplification

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

# [Trend Name]
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

## 8.3 Stage 3: General Translation

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

# 1. [Principle Name]
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

## 8.4 Stage 4: Brand Contextualization (Critical Stage)

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

# 1. [Insight Title]
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

## 8.5 Stage 5: Opportunity Generation

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
