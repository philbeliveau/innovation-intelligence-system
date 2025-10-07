# Innovation Intelligence Pipeline - Complete Documentation

## Table of Contents
1. [Pipeline Overview](#pipeline-overview)
2. [Core Concepts](#core-concepts)
3. [Pipeline Stages (1-5)](#pipeline-stages)
4. [Data Flow](#data-flow)
5. [File Structure](#file-structure)
6. [Execution Modes](#execution-modes)
7. [Testing Strategy](#testing-strategy)

---

## Pipeline Overview

### What This Pipeline Does
The Innovation Intelligence Pipeline transforms **external inspiration** (trend reports, case studies, spotted innovations) into **brand-specific innovation opportunities**.

**Input:** A document describing an innovation, trend, or business model
**Output:** 1-5 actionable opportunity cards tailored to a specific CPG brand

### The 5-Stage Transformation Process

```
Input Document (PDF)
        ↓
[Stage 1] Extract core inspiration & innovation principles
        ↓
[Stage 2] Amplify signals & identify broader trends
        ↓
[Stage 3] Translate to universal lessons (brand-agnostic)
        ↓
[Stage 4] Contextualize for target brand (brand-specific)
        ↓
[Stage 5] Generate opportunity cards (actionable innovation ideas)
        ↓
Opportunity Card(s) (Markdown)
```

---

## Core Concepts

### What is a "Scenario"?
A **scenario** = ONE complete pipeline execution = ONE input document processed for ONE target brand.

**Formula:** Scenarios = Input Documents × Target Brands

**Example:**
- 6 input documents × 4 target brands = **24 scenarios**
- Each scenario produces 1-5 opportunity cards (configurable)

### What is an "Opportunity Card"?
A structured markdown document containing:
- **Title:** Innovation opportunity name
- **Description:** 2-3 paragraphs explaining the opportunity
- **Why This Matters:** Business rationale
- **Actionable Next Steps:** 3-5 concrete actions to explore the opportunity
- **Visual Suggestion:** Description of supporting imagery
- **Follow-up Prompts:** 2-3 questions to deepen exploration
- **Metadata:** Inspiration source, brand, innovation type, tags, timestamp

---

## Pipeline Stages

### Stage 1: Input Processing and Inspiration Identification
**File:** `pipeline/stages/stage1_input_processing.py`
**Prompt:** `pipeline/prompts/stage1_prompt.py`

**Purpose:** Extract the core innovation principles from the input document.

**Input:**
- Raw PDF document text (trend report, case study, or spotted innovation)

**Processing:**
- Identify what makes this innovation compelling
- Extract business model insights
- Identify customer value propositions
- Note implementation approaches
- Capture key metrics or evidence of success

**Output:** `stage1/inspiration-analysis.md`
- Structured analysis of the innovation's core principles
- Key insights that could inspire other contexts
- ~3,000-3,500 characters

**Model Config:**
- Model: Claude Sonnet 4.5 (via OpenRouter)
- Temperature: 0.3 (factual analysis)

---

### Stage 2: Signal Amplification and Trend Extraction
**File:** `pipeline/stages/stage2_signal_amplification.py`
**Prompt:** `pipeline/prompts/stage2_prompt.py`

**Purpose:** Amplify weak signals and identify broader market trends.

**Input:**
- Stage 1 inspiration analysis
- Original document text (for context)

**Processing:**
- Identify patterns and trends underlying the innovation
- Look for emerging consumer behaviors or market shifts
- Connect to broader industry movements
- Spot adjacent opportunities
- Note potential future directions

**Output:** `stage2/trend-analysis.md`
- Trend identification and categorization
- Signal strength and market trajectory
- Connections to broader movements
- ~3,500-4,000 characters

**Model Config:**
- Model: Claude Sonnet 4.5 (via OpenRouter)
- Temperature: 0.4 (balanced analysis with some creativity)

---

### Stage 3: General Translation to Universal Lessons
**File:** `pipeline/stages/stage3_general_translation.py`
**Prompt:** `pipeline/prompts/stage3_prompt.py`

**Purpose:** Translate insights into universal, brand-agnostic lessons.

**Input:**
- Stage 2 trend analysis
- Stage 1 inspiration analysis (for reference)

**Processing:**
- Extract transferable principles that work across industries
- Identify systematic innovation methods (TRIZ patterns, biomimicry, etc.)
- Create abstract frameworks applicable to any brand
- Remove industry-specific context
- Generate reusable innovation patterns

**Output:** `stage3/universal-lessons.md`
- Universal innovation principles
- Cross-industry applicability notes
- Systematic innovation patterns
- ~5,000-5,500 characters

**Model Config:**
- Model: Claude Sonnet 4.5 (via OpenRouter)
- Temperature: 0.5 (creative pattern recognition)

---

### Stage 4: Brand Contextualization
**File:** `pipeline/stages/stage4_brand_contextualization.py`
**Prompt:** `pipeline/prompts/stage4_prompt.py`

**Purpose:** Adapt universal lessons to a specific target brand's context.

**Input:**
- Stage 3 universal lessons
- Brand research data from `data/brand-research/{brand-slug}/`
  - Brand overview and positioning
  - Product portfolio
  - Strategic priorities
  - Market challenges
  - Innovation history

**Processing:**
- Match universal lessons to brand's strategic priorities
- Identify relevant product categories or market segments
- Connect to existing brand strengths
- Consider brand's operational capabilities
- Adapt to brand's market position and competitive landscape

**Output:** `stage4/brand-specific-insights.md`
- Brand-contextualized insights
- Connections to specific products/categories
- Strategic fit analysis
- ~4,000-5,000 characters

**Model Config:**
- Model: Claude Sonnet 4.5 (via OpenRouter)
- Temperature: 0.4 (focused brand application)

---

### Stage 5: Opportunity Generation
**File:** `pipeline/stages/stage5_opportunity_generation.py`
**Prompt:** `pipeline/prompts/stage5_prompt.py`

**Purpose:** Generate actionable, brand-specific innovation opportunity cards.

**Input:**
- Stage 4 brand-specific insights
- Brand research data (for validation)

**Processing:**
- Create distinct innovation opportunities spanning different types:
  - Product innovation
  - Service innovation
  - Marketing innovation
  - Experience innovation
  - Partnership innovation
- Ensure each opportunity is:
  - **Actionable:** Has concrete next steps
  - **Distinct:** Not variations of the same idea
  - **Brand-relevant:** Mentions specific products/context
  - **Implementable:** Not science fiction
  - **Value-creating:** Clear customer benefit

**Output:**
**Current (Story 4.2):** 5 opportunities per scenario
- `stage5/opportunity-1.md`
- `stage5/opportunity-2.md`
- `stage5/opportunity-3.md`
- `stage5/opportunity-4.md`
- `stage5/opportunity-5.md`
- `stage5/opportunities-summary.md` (index of all 5)

**Future (Story 4.3 batch execution):** 1 opportunity per scenario
- `stage5/opportunity.md`

**Model Config:**
- Model: Claude Sonnet 4.5 (via OpenRouter)
- Temperature: 0.7 (high creativity for opportunity generation)

---

## Data Flow

### Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT                                                           │
│ documentation/document/{input-id}.pdf                           │
│ data/brand-research/{brand-slug}/                               │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: Input Processing                                      │
│ • Load PDF → extract text                                      │
│ • Analyze innovation principles                                │
│ • Extract core insights                                        │
│                                                                 │
│ Output: stage1/inspiration-analysis.md (~3,200 chars)          │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: Signal Amplification                                  │
│ • Read Stage 1 output                                          │
│ • Amplify weak signals                                         │
│ • Identify broader trends                                      │
│                                                                 │
│ Output: stage2/trend-analysis.md (~3,800 chars)                │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: General Translation                                   │
│ • Read Stage 2 output                                          │
│ • Extract universal lessons                                    │
│ • Create brand-agnostic frameworks                             │
│                                                                 │
│ Output: stage3/universal-lessons.md (~5,300 chars)             │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: Brand Contextualization                               │
│ • Read Stage 3 output                                          │
│ • Load brand research data                                     │
│ • Adapt lessons to brand context                               │
│                                                                 │
│ Output: stage4/brand-specific-insights.md (~4,500 chars)       │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: Opportunity Generation                                │
│ • Read Stage 4 output                                          │
│ • Generate 1-5 opportunity cards                               │
│ • Render using Jinja2 template                                 │
│                                                                 │
│ Output: stage5/opportunity-{1-5}.md (5 cards per scenario)     │
│         stage5/opportunities-summary.md (index)                │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ OUTPUT                                                          │
│ Actionable innovation opportunity cards ready for review        │
└─────────────────────────────────────────────────────────────────┘
```

### Data Accumulation Pattern
Each stage **builds on** previous stages:
- **Stage 2** reads Stage 1 output
- **Stage 3** reads Stage 2 output (references Stage 1)
- **Stage 4** reads Stage 3 output + brand research
- **Stage 5** reads Stage 4 output + brand research

This creates a **progressive refinement** process where context accumulates through the pipeline.

---

## File Structure

### Input Files

```
documentation/document/
├── savannah-bananas.pdf
├── premium-fast-food-trend.pdf
├── nonalcoholic-beverage-trend.pdf
├── sacred-sync-trend.pdf
├── cat-dad-campaign.pdf
└── qr-garment-resale.pdf
```

### Brand Research Data

```
data/brand-research/
├── lactalis/
│   ├── overview.md
│   ├── products.md
│   ├── strategy.md
│   └── innovation-history.md
├── mccormick/
│   └── [similar structure]
├── seventh-generation/
│   └── [similar structure]
└── colgate-palmolive/
    └── [similar structure]
```

### Pipeline Output Structure (per scenario)

```
data/test-outputs/{execution-name}/{input-id}--{brand-slug}/
├── stage1/
│   └── inspiration-analysis.md
├── stage2/
│   └── trend-analysis.md
├── stage3/
│   └── universal-lessons.md
├── stage4/
│   └── brand-specific-insights.md
└── stage5/
    ├── opportunity-1.md
    ├── opportunity-2.md
    ├── opportunity-3.md
    ├── opportunity-4.md
    ├── opportunity-5.md
    └── opportunities-summary.md
```

### Example Output Path

```
data/test-outputs/integration-test-stages-1-3/savannah-bananas--lactalis/
```

This represents:
- **Execution name:** `integration-test-stages-1-3`
- **Input:** `savannah-bananas`
- **Brand:** `lactalis`

---

## Execution Modes

### Single Scenario Execution

**Command:**
```bash
python run_pipeline.py --input savannah-bananas --brand lactalis --output-dir data/test-outputs/single-run
```

**What Happens:**
1. Loads `savannah-bananas.pdf`
2. Loads brand research for `lactalis`
3. Runs Stages 1→2→3→4→5 sequentially
4. Generates 5 opportunity cards in `data/test-outputs/single-run/savannah-bananas--lactalis/stage5/`

**Use Case:** Testing, debugging, single opportunity generation

---

### Batch Execution (Story 4.3)

**Command:**
```bash
python run_pipeline.py --batch
```

**What Happens:**
1. Loads test manifest with all scenarios (6 inputs × 4 brands = 24 scenarios)
2. Executes each scenario sequentially
3. Displays progress: `"Test 5/24: premium-fast-food → mccormick - Stage 3/5 complete"`
4. **Error resilience:** If one scenario fails, logs error and continues
5. Generates batch summary report: `data/test-outputs/batch-summary.md`

**Output:**
- 24 output directories (one per scenario)
- 24 opportunity cards total (1 per scenario in batch mode)
- Execution time tracking
- Success/failure status per scenario

**Success Metric:** ≥23 out of 24 scenarios complete successfully (95% success rate)

---

### Retry Failed Scenarios

**Command:**
```bash
python run_pipeline.py --batch --retry-failed
```

**What Happens:**
1. Reads previous batch execution results
2. Identifies failed scenarios
3. Re-runs only those scenarios
4. Updates batch summary with retry results

---

## Testing Strategy

### Test Scenarios (24 Total)

**6 Input Documents:**
1. **savannah-bananas** (case study) - The Savannah Bananas sports entertainment business model
2. **premium-fast-food** (trend report) - Mintel report on premium fast food
3. **nonalcoholic-beverage** (trend report) - Mintel 2025 non-alcoholic beverage trends
4. **sacred-sync** (trend report) - Trendwatching FastForward on Sacred Sync trend
5. **cat-dad-campaign** (spotted innovation) - Mars Petcare "Sexiest Cat Dad" campaign
6. **qr-garment-resale** (spotted innovation) - QR codes for garment resale

**4 Target Brands:**
1. **Lactalis** (dairy products)
2. **McCormick** (spices and seasonings)
3. **Seventh Generation** (sustainable household products)
4. **Colgate-Palmolive** (oral care, personal care, home care)

**24 Scenarios = All Combinations:**
```
1.  savannah-bananas → lactalis
2.  savannah-bananas → mccormick
3.  savannah-bananas → seventh-generation
4.  savannah-bananas → colgate-palmolive
5.  premium-fast-food → lactalis
6.  premium-fast-food → mccormick
7.  premium-fast-food → seventh-generation
8.  premium-fast-food → colgate-palmolive
9.  nonalcoholic-beverage → lactalis
10. nonalcoholic-beverage → mccormick
11. nonalcoholic-beverage → seventh-generation
12. nonalcoholic-beverage → colgate-palmolive
13. sacred-sync → lactalis
14. sacred-sync → mccormick
15. sacred-sync → seventh-generation
16. sacred-sync → colgate-palmolive
17. cat-dad-campaign → lactalis
18. cat-dad-campaign → mccormick
19. cat-dad-campaign → seventh-generation
20. cat-dad-campaign → colgate-palmolive
21. qr-garment-resale → lactalis
22. qr-garment-resale → mccormick
23. qr-garment-resale → seventh-generation
24. qr-garment-resale → colgate-palmolive
```

### Testing Milestones

**Story 2.4:** Stages 1-3 Integration Test
- Test file: `test_stages_1_3.py`
- Validates: Stage 1 → Stage 2 → Stage 3 pipeline
- Inputs tested: All 6 input documents
- Output: 6 test results with stage1/stage2/stage3 outputs

**Story 3.1:** Research Data Integration Test
- Validates: Brand research data loading
- Tests: All 4 brand research directories load correctly

**Story 3.2:** Stage 4 Integration Test
- Test file: `test_stage4.py` (not yet created)
- Validates: Stage 3 → Stage 4 pipeline with brand data

**Story 4.2:** Stage 5 Single Scenario Test
- Test: Savannah Bananas → Lactalis
- Validates: Generates exactly 5 distinct opportunity cards
- Quality checks: Actionability, distinctiveness, brand relevance

**Story 4.3:** Complete Batch Execution
- Test: All 24 scenarios
- Validates: Error resilience, progress monitoring, batch summary
- Target: 24 opportunity cards (1 per scenario)

---

## Configuration

### Model Configuration

All stages use **Claude Sonnet 4.5** via OpenRouter:
- **Provider:** OpenRouter (`https://openrouter.ai/api/v1`)
- **Model:** `anthropic/claude-sonnet-4.5`
- **API Key:** Loaded from `.env` file (`OPENROUTER_API_KEY`)

**Temperature Settings by Stage:**
- Stage 1: 0.3 (factual analysis)
- Stage 2: 0.4 (balanced analysis)
- Stage 3: 0.5 (creative pattern recognition)
- Stage 4: 0.4 (focused application)
- Stage 5: 0.7 (high creativity for opportunities)

### Template Configuration

**Jinja2 Templates:**
- Location: `templates/`
- `opportunity-card-template.md.j2` - Opportunity card rendering

**YAML Configuration:**
- `.env.template` - Environment variables
- Test manifests in `data/test-manifests/` (if created)

---

## Performance Characteristics

### Execution Time (Observed from Stage 1-3 Test)

**Total for 6 inputs (Stages 1-3 only):** 364.69 seconds (~6 minutes)

**Per Input (average):** ~60 seconds for Stages 1-3

**Estimated Full Pipeline (Stages 1-5):**
- Single scenario: ~90-120 seconds (1.5-2 minutes)
- Batch execution (24 scenarios): ~36-48 minutes

### Token Usage

**Approximate per stage:**
- Stage 1: ~2,000 tokens input + 800 tokens output
- Stage 2: ~3,000 tokens input + 900 tokens output
- Stage 3: ~4,000 tokens input + 1,200 tokens output
- Stage 4: ~5,000 tokens input + 1,000 tokens output
- Stage 5: ~6,000 tokens input + 1,500 tokens output

**Total per scenario:** ~32,400 tokens (~$0.15-0.20 per scenario at OpenRouter pricing)

---

## Quality Assurance

### Stage Output Quality Checklist

**Stage 1:**
- [ ] Identifies core innovation principles
- [ ] Extracts business model insights
- [ ] Notes customer value propositions
- [ ] ~3,000-3,500 characters

**Stage 2:**
- [ ] Identifies broader trends
- [ ] Amplifies weak signals
- [ ] Connects to market movements
- [ ] ~3,500-4,000 characters

**Stage 3:**
- [ ] Universal lessons are brand-agnostic
- [ ] Transferable across industries
- [ ] Systematic innovation patterns identified
- [ ] ~5,000-5,500 characters

**Stage 4:**
- [ ] Insights contextualized to brand
- [ ] References specific products/categories
- [ ] Connects to brand's strategic priorities
- [ ] ~4,000-5,000 characters

**Stage 5:**
- [ ] Opportunities are distinct (not variations)
- [ ] Each has 3-5 actionable next steps
- [ ] Brand-relevant (mentions specific context)
- [ ] Spans different innovation types
- [ ] Clear customer value proposition

### Error Handling

**Graceful Degradation:**
- Missing brand research → Stage 4 uses partial data
- API errors → Retry with exponential backoff
- PDF parsing failures → Log error, continue batch
- Invalid output format → Fallback to raw text

---

## Troubleshooting

### Common Issues

**"No output generated for Stage X"**
- Check API key in `.env`
- Verify OpenRouter account has credits
- Check network connectivity
- Review logs for API errors

**"Brand research not found"**
- Verify `data/brand-research/{brand-slug}/` exists
- Check brand slug matches exactly (lowercase, hyphens)
- Ensure at least one .md file exists in brand directory

**"Invalid PDF document"**
- Verify PDF is not encrypted
- Check PDF contains extractable text (not scanned image)
- Try re-downloading source PDF

**"Batch execution slow"**
- Normal: 24 scenarios takes 36-48 minutes
- Use `--retry-failed` to only re-run failures
- Consider parallel execution (future enhancement)

---

## Future Enhancements

### Planned (Story Backlog)
- [ ] Parallel scenario execution for faster batch runs
- [ ] Web UI for opportunity card browsing
- [ ] Opportunity scoring/ranking system
- [ ] User feedback collection on opportunities
- [ ] A/B testing different prompt strategies
- [ ] Export to PowerPoint/PDF formats
- [ ] Integration with external trend databases

### Potential Research Areas
- [ ] RAG (Retrieval Augmented Generation) for brand research
- [ ] Fine-tuning models on successful opportunities
- [ ] Multi-agent validation (red team / blue team)
- [ ] Real-time trend monitoring and alerting
- [ ] Cross-brand opportunity sharing

---

## References

### Related Documentation
- `/docs/stories/` - User stories for each feature
- `/docs/qa/gates/` - Quality assurance gates
- `/docs/brand-research-data-structure.md` - Brand research format
- `/docs/opportunity-card-format.md` - Opportunity card specification
- `/CLAUDE.md` - Project context and business model

### Key Files
- `run_pipeline.py` - Main execution script
- `pipeline/utils.py` - Shared utilities
- `test_stages_1_3.py` - Integration test for Stages 1-3

---

**Document Version:** 1.0
**Last Updated:** 2025-10-07
**Author:** Pipeline Development Team
