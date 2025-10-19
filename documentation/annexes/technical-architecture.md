# Technical Architecture Annex

**Purpose:** Complete technical documentation for developers and technical stakeholders who need to understand or reproduce the Innovation Intelligence System.

**Audience:** Software engineers, technical architects, MLOps teams

---

## Architecture Overview

### Technology Stack

**Core Framework:**
- **LangChain** (0.3.x): Orchestration framework for LLM pipelines
- **Python** (3.10+): Primary language
- **OpenRouter API**: LLM provider gateway
- **Claude Sonnet 4.5**: Primary reasoning model

**Dependencies:**
```python
langchain==0.3.x
langchain-anthropic
python-dotenv
PyPDF2
pyyaml
```

### System Components

```
innovation-intelligence-system/
├── pipeline/
│   ├── stages/          # 5 stage implementations
│   ├── prompts/         # Stage-specific prompts
│   └── utils.py         # Shared utilities
├── data/
│   ├── inputs/          # PDF input documents
│   ├── brand-profiles/  # Brand research YAML
│   └── test-outputs/    # Execution results
├── run_pipeline.py      # Main execution script
└── docs/                # Documentation
```

---

## Pipeline Architecture

### Data Flow Diagram

```
┌─────────────────┐
│  Input Document │ (PDF)
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Stage 1: Input Processing               │
│  - Extract text from PDF                 │
│  - Identify core inspirations            │
│  - Output: inspiration-analysis.md       │
└────────┬─────────────────────────────────┘
         │ (3,000-3,500 chars)
         ▼
┌──────────────────────────────────────────┐
│  Stage 2: Signal Amplification           │
│  - Input: inspiration-analysis + PDF     │
│  - Extract trends (BHCTE categories)     │
│  - Output: trend-analysis.md             │
└────────┬─────────────────────────────────┘
         │ (3,500-4,000 chars)
         ▼
┌──────────────────────────────────────────┐
│  Stage 3: General Translation            │
│  - Input: trend-analysis                 │
│  - Generate universal principles         │
│  - Output: universal-lessons.md          │
└────────┬─────────────────────────────────┘
         │ (5,000-5,500 chars)
         ▼
┌──────────────────────────────────────────┐
│  Stage 4: Brand Contextualization        │
│  - Input: universal-lessons + brand.yaml │
│  - Adapt to brand strategy/capabilities  │
│  - Output: brand-contextualization.md    │
└────────┬─────────────────────────────────┘
         │ (7,000-8,000 chars)
         ▼
┌──────────────────────────────────────────┐
│  Stage 5: Opportunity Generation         │
│  - Input: brand-contextualization        │
│  - Generate N opportunity cards          │
│  - Output: opportunity-1.md ... N.md     │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│ Opportunity Cards│ (5 per scenario)
└──────────────────┘
```

---

## Stage Implementation Details

### Stage 1: Input Processing

**File:** `pipeline/stages/stage1_input_processing.py`

**LangChain Components:**
```python
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Model configuration
llm = ChatAnthropic(
    model="anthropic/claude-sonnet-4-5-20250929:beta",
    temperature=0.3,
    max_tokens=4000
)

# Prompt template
prompt = PromptTemplate(
    input_variables=["document_text"],
    template=STAGE1_PROMPT
)

# Chain execution
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.invoke({"document_text": pdf_text})
```

**Temperature Rationale:** 0.3 for factual analysis - minimal creativity needed

**Output Format:** Markdown with structured sections (Document Overview, Key Inspirations, Context Notes)

**Performance Metrics (Story 4.3):**
- Average execution time: 26.4 seconds
- Success rate: 100% (24/24 scenarios)
- Average output length: 3,200 characters

---

### Stage 2: Signal Amplification

**File:** `pipeline/stages/stage2_signal_amplification.py`

**LangChain Components:**
```python
# Model configuration
llm = ChatAnthropic(
    model="anthropic/claude-sonnet-4-5-20250929:beta",
    temperature=0.4,  # Slightly higher for pattern recognition
    max_tokens=4500
)

# Chain with Stage 1 output as input
chain = LLMChain(llm=llm, prompt=stage2_prompt)
result = chain.invoke({
    "inspiration_analysis": stage1_output,
    "original_document": pdf_text
})
```

**Temperature Rationale:** 0.4 balances analytical rigor with creative pattern recognition

**Trend Categories (BHCTE):**
- **B**ehavioral: Consumer behavior patterns
- **H**ealth: (Not used - merged into C)
- **C**ultural: Social and cultural shifts
- **T**echnological: Technology enablement
- **E**conomic: Business model and economic factors

**Signal Strength Levels:**
- HIGH: Strong evidence, multiple supporting examples
- MEDIUM: Clear pattern, limited examples
- LOW: Weak signal, requires validation

**Performance Metrics (Story 4.3):**
- Average execution time: 30.3 seconds
- Success rate: 100%
- Average output length: 3,700 characters

---

### Stage 3: General Translation

**File:** `pipeline/stages/stage3_general_translation.py`

**LangChain Components:**
```python
# Model configuration
llm = ChatAnthropic(
    model="anthropic/claude-sonnet-4-5-20250929:beta",
    temperature=0.5,  # Higher for creative abstraction
    max_tokens=6000
)

# Chain execution
chain = LLMChain(llm=llm, prompt=stage3_prompt)
result = chain.invoke({
    "trend_analysis": stage2_output,
    "inspiration_analysis": stage1_output
})
```

**Temperature Rationale:** 0.5 enables creative abstraction while maintaining logical coherence

**Innovation Framework Integration:**
- TRIZ 40 Inventive Principles
- SIT (Systematic Inventive Thinking) Templates
- Biomimicry patterns
- Jobs-to-be-Done frameworks

**De-contextualization Process:**
1. Extract core principle from trend
2. Remove industry-specific references
3. Generalize to universal rule
4. Identify cross-industry applications
5. Map to systematic innovation frameworks

**Performance Metrics (Story 4.3):**
- Average execution time: 43.7 seconds
- Success rate: 100%
- Average output length: 5,300 characters

---

### Stage 4: Brand Contextualization

**File:** `pipeline/stages/stage4_brand_contextualization.py`

**LangChain Components:**
```python
# Model configuration
llm = ChatAnthropic(
    model="anthropic/claude-sonnet-4-5-20250929:beta",
    temperature=0.6,  # Highest for creative application
    max_tokens=8500
)

# Load brand profile
with open(f"data/brand-profiles/{brand_id}.yaml") as f:
    brand_profile = yaml.safe_load(f)

# Chain execution with brand context
chain = LLMChain(llm=llm, prompt=stage4_prompt)
result = chain.invoke({
    "universal_lessons": stage3_output,
    "brand_profile": yaml.dump(brand_profile)
})
```

**Temperature Rationale:** 0.6 enables creative brand-specific application while staying grounded in strategy

**Brand Profile Schema:**
```yaml
brand_id: mccormick-usa
brand_name: McCormick USA
overview: [Strategic positioning, market context]
strategic_priorities:
  - [Priority 1]
  - [Priority 2]
products_services: [Portfolio description]
target_customers:
  - segment: [Segment name]
    demographics: [Age, income, etc.]
    psychographics: [Values, behaviors]
    needs: [Key needs addressed]
innovation_context: [Recent launches, capabilities]
competitive_positioning: [Market position]
```

**Contextualization Process:**
1. Map universal principles to brand strategic priorities
2. Assess brand capability fit
3. Identify customer segment alignment
4. Generate 5-7 brand-specific strategic insights
5. Provide concrete implementation examples

**Performance Metrics (Story 4.3):**
- Average execution time: 69.5 seconds (longest stage)
- Success rate: 100%
- Average output length: 7,500 characters

---

### Stage 5: Opportunity Generation

**File:** `pipeline/stages/stage5_opportunity_generation.py`

**LangChain Components:**
```python
# Model configuration
llm = ChatAnthropic(
    model="anthropic/claude-sonnet-4-5-20250929:beta",
    temperature=0.7,  # Maximum creativity for final ideas
    max_tokens=12000  # Largest token budget
)

# Structured output parser
from langchain.output_parsers import PydanticOutputParser
output_parser = PydanticOutputParser(pydantic_object=OpportunitiesOutput)

# Chain execution
chain = LLMChain(llm=llm, prompt=stage5_prompt)
result = chain.invoke({
    "brand_contextualization": stage4_output,
    "num_opportunities": 5
})
```

**Temperature Rationale:** 0.7 maximizes creative idea generation while maintaining coherence

**Opportunity Card Format:**
```markdown
---
opportunity_id: opp-01
brand: [brand_id]
input_source: [input_id]
timestamp: [ISO 8601]
tags: [tag1, tag2, tag3]
---

# [Opportunity Title]

## Description
[2-3 paragraph description]

## Actionability
- [Next step 1]
- [Next step 2]
- [Next step 3]
- [Next step 4]

## Visual
*[Visual concept description]*

## Follow-up Prompts
1. [Question 1]
2. [Question 2]
```

**JSON Output Structure:**
```json
{
  "opportunities": [
    {
      "title": "...",
      "description": "...",
      "actionability": [...],
      "visual": "...",
      "follow_up_prompts": [...]
    }
  ]
}
```

**Error Handling:**
- JSON parsing failures: 2 of 24 scenarios (8.3%)
- Fallback: Log error, skip scenario, continue batch
- Production recommendation: Implement structured output validation

**Performance Metrics (Story 4.3):**
- Average execution time: 49.3 seconds
- Success rate: 91.7% (22/24)
- Failure mode: JSON parsing errors
- Average opportunities per scenario: 5

---

## Prompt Engineering Strategy

### Design Principles

1. **Progressive Refinement:** Each stage builds on previous outputs
2. **Context Preservation:** Pass forward only essential information
3. **Clear Instructions:** Explicit structure, format, and constraints
4. **Examples Provided:** Few-shot learning for consistent outputs
5. **Length Constraints:** Character targets to prevent bloat

### Prompt Structure Template

```
# ROLE
You are a [specific role] with expertise in [domain].

# CONTEXT
[Previous stage outputs, brand information]

# TASK
[Specific transformation required]

# OUTPUT FORMAT
[Markdown structure, sections, character length]

# CONSTRAINTS
- [Constraint 1]
- [Constraint 2]

# EXAMPLES
[1-2 examples of desired output]
```

### Temperature Progression

| Stage | Temperature | Rationale |
|-------|------------|-----------|
| Stage 1 | 0.3 | Factual extraction |
| Stage 2 | 0.4 | Pattern recognition with precision |
| Stage 3 | 0.5 | Creative abstraction |
| Stage 4 | 0.6 | Brand-specific creativity |
| Stage 5 | 0.7 | Maximum idea generation |

**Design Philosophy:** Increase creativity as we move from analysis to synthesis

---

## Code Structure

### Main Execution Flow

**File:** `run_pipeline.py`

```python
def run_scenario(input_id, brand_id):
    """Execute complete 5-stage pipeline for one scenario"""

    # Setup
    output_dir = create_output_directory(input_id, brand_id)

    # Stage 1
    stage1_result = stage1_input_processing(input_pdf_path)
    save_output(output_dir, "stage1", stage1_result)

    # Stage 2
    stage2_result = stage2_signal_amplification(stage1_result, input_pdf)
    save_output(output_dir, "stage2", stage2_result)

    # Stage 3
    stage3_result = stage3_general_translation(stage2_result)
    save_output(output_dir, "stage3", stage3_result)

    # Stage 4
    stage4_result = stage4_brand_contextualization(stage3_result, brand_profile)
    save_output(output_dir, "stage4", stage4_result)

    # Stage 5
    stage5_result = stage5_opportunity_generation(stage4_result, num_opportunities=5)
    save_output(output_dir, "stage5", stage5_result)

    return output_dir
```

### Batch Execution Mode

```python
def run_batch(input_ids, brand_ids):
    """Execute all scenarios in batch mode"""
    scenarios = [(i, b) for i in input_ids for b in brand_ids]

    results = []
    for input_id, brand_id in scenarios:
        try:
            result = run_scenario(input_id, brand_id)
            results.append({"status": "success", "output": result})
        except Exception as e:
            results.append({"status": "error", "error": str(e)})

    generate_batch_summary(results)
    return results
```

---

## Performance Data (Story 4.3 Batch Execution)

### Overall Metrics

- **Total Scenarios:** 24
- **Successful:** 22 (91.7%)
- **Failed:** 2 (JSON parsing errors in Stage 5)
- **Total Execution Time:** 3,435.4 seconds (57.3 minutes)
- **Average Time per Scenario:** 143.1 seconds (2.4 minutes)
- **Total Opportunities Generated:** 110

### Stage-by-Stage Performance

| Stage | Avg Time (s) | % of Total | Success Rate |
|-------|-------------|------------|--------------|
| Stage 1 | 26.4 | 18% | 100% |
| Stage 2 | 30.3 | 21% | 100% |
| Stage 3 | 43.7 | 31% | 100% |
| Stage 4 | 69.5 | 49% | 100% |
| Stage 5 | 49.3 | 34% | 91.7% |

**Bottleneck:** Stage 4 (Brand Contextualization) takes longest due to:
- Largest context (brand profile + universal lessons)
- Most complex reasoning (strategic fit analysis)
- Highest output token requirements

### Error Analysis

**2 Failures in Stage 5:**
1. `premium-fast-food-columbia-sportswear`: JSON delimiter error at line 40
2. `cat-dad-campaign-mccormick-usa`: JSON delimiter error at line 40

**Root Cause:** Claude occasionally generates malformed JSON when opportunity descriptions contain quotes or complex punctuation

**Recommended Fix:** Implement structured output schema with validation and retry logic

---

## Deployment Considerations

### Scalability

**Current Throughput:**
- 24 scenarios in 57 minutes
- ~2.4 minutes per scenario
- Sequential execution (no parallelization)

**Production Targets:**
- Daily delivery: 10-20 opportunities per customer
- Weekly newsletter: 50-100 opportunities total
- Requires: ~2-5 minutes per opportunity (currently meeting target)

### Cost Analysis

**OpenRouter API Costs (Story 4.3):**
- Model: Claude Sonnet 4.5
- Input tokens: ~150K per scenario
- Output tokens: ~30K per scenario
- Estimated cost: ~$2-3 per scenario

**Monthly Cost Projection:**
- Tier 2 (Daily): 365 scenarios/year = ~$1,000/year per customer
- Tier 1 (Weekly): 52 scenarios/year = ~$150/year per customer

### Reliability Requirements

**Current State:**
- 91.7% success rate (below 95% target)
- No retry logic
- No monitoring/alerting

**Production Requirements:**
- Target: ≥95% success rate
- Implement: Exponential backoff retry
- Add: Structured output validation
- Include: Real-time error monitoring
- Enable: Dead letter queue for failed scenarios

---

## Next: Productionization Roadmap

For recommendations on taking this proof of concept to production, see:
`docs/annexes/productionization-roadmap.md`

For quality validation methodology and results, see:
`docs/annexes/validation-results.md`
