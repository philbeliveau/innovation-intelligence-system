# Innovation Intelligence Pipeline - Quick Reference

## TL;DR

**What it does:** Transforms external inspiration (trends, case studies) into brand-specific innovation opportunities

**Input:** PDF document
**Output:** 1-5 actionable opportunity cards for a target brand
**Pipeline:** 5 stages (Input → Signal → Translation → Brand Context → Opportunities)

---

## Key Numbers

| Metric | Value |
|--------|-------|
| **Pipeline Stages** | 5 |
| **Input Documents** | 6 |
| **Target Brands** | 4 |
| **Total Scenarios** | 24 (6 inputs × 4 brands) |
| **Opportunity Cards per Scenario** | 1 (batch mode) or 5 (single mode) |
| **Time per Scenario** | ~90-120 seconds |
| **Full Batch Time** | ~36-48 minutes |
| **Success Rate Target** | ≥95% (23/24 scenarios) |

---

## The 5 Stages

```
┌─────────────┐
│   Stage 1   │  Extract core inspiration & innovation principles
│   Input     │  Temperature: 0.3 | Output: ~3,200 chars
└──────┬──────┘
       ↓
┌─────────────┐
│   Stage 2   │  Amplify signals & identify broader trends
│   Signal    │  Temperature: 0.4 | Output: ~3,800 chars
└──────┬──────┘
       ↓
┌─────────────┐
│   Stage 3   │  Translate to universal, brand-agnostic lessons
│  Universal  │  Temperature: 0.5 | Output: ~5,300 chars
└──────┬──────┘
       ↓
┌─────────────┐
│   Stage 4   │  Contextualize for target brand
│    Brand    │  Temperature: 0.4 | Output: ~4,500 chars | Uses brand research
└──────┬──────┘
       ↓
┌─────────────┐
│   Stage 5   │  Generate actionable opportunity cards
│ Opportunity │  Temperature: 0.7 | Output: 1-5 cards | Jinja2 templates
└─────────────┘
```

---

## Quick Commands

### Run Single Scenario
```bash
python run_pipeline.py --input savannah-bananas --brand lactalis --output-dir data/test-outputs/single-run
```

### Run Batch (All 24 Scenarios)
```bash
python run_pipeline.py --batch
```

### Retry Failed Scenarios
```bash
python run_pipeline.py --batch --retry-failed
```

### Run Stages 1-3 Test
```bash
python test_stages_1_3.py
```

---

## Test Inputs

| ID | Type | Description |
|----|------|-------------|
| **savannah-bananas** | Case Study | Sports entertainment business model |
| **premium-fast-food** | Trend Report | Mintel premium fast food |
| **nonalcoholic-beverage** | Trend Report | Mintel non-alcoholic trends |
| **sacred-sync** | Trend Report | Trendwatching Sacred Sync |
| **cat-dad-campaign** | Spotted Innovation | Mars Petcare campaign |
| **qr-garment-resale** | Spotted Innovation | QR codes for resale |

---

## Target Brands

| Brand | Industry | Key Products |
|-------|----------|--------------|
| **Lactalis** | Dairy | Milk, cheese, yogurt |
| **McCormick** | Food | Spices, seasonings |
| **Seventh Generation** | Household | Sustainable cleaning |
| **Colgate-Palmolive** | Personal Care | Oral care, hygiene |

---

## File Locations

### Input Files
```
documentation/document/{input-id}.pdf
```

### Brand Research
```
data/brand-research/{brand-slug}/
├── overview.md
├── products.md
├── strategy.md
└── innovation-history.md
```

### Pipeline Output
```
data/test-outputs/{execution-name}/{input-id}--{brand-slug}/
├── stage1/inspiration-analysis.md
├── stage2/trend-analysis.md
├── stage3/universal-lessons.md
├── stage4/brand-specific-insights.md
└── stage5/
    ├── opportunity-1.md
    ├── opportunity-2.md
    ├── opportunity-3.md
    ├── opportunity-4.md
    ├── opportunity-5.md
    └── opportunities-summary.md
```

### Code Structure
```
pipeline/
├── stages/
│   ├── stage1_input_processing.py
│   ├── stage2_signal_amplification.py
│   ├── stage3_general_translation.py
│   ├── stage4_brand_contextualization.py
│   └── stage5_opportunity_generation.py
├── prompts/
│   ├── stage1_prompt.py
│   ├── stage2_prompt.py
│   ├── stage3_prompt.py
│   ├── stage4_prompt.py
│   └── stage5_prompt.py
└── utils.py

templates/
└── opportunity-card.md.j2

run_pipeline.py
test_stages_1_3.py
```

---

## Opportunity Card Structure

Each opportunity card contains:

```yaml
---
opportunity_id: "opp-001"
title: "Innovation Title"
inspiration_source: "savannah-bananas"
target_brand: "lactalis"
innovation_type: "Product|Service|Marketing|Experience|Partnership"
tags: [tag1, tag2, tag3]
generated_date: "2025-10-07"
---

# Innovation Title

## Description
2-3 paragraphs explaining the opportunity

## Why This Matters
Business rationale and strategic fit

## Actionable Next Steps
1. First concrete action
2. Second concrete action
3. Third concrete action
4. Fourth concrete action (optional)
5. Fifth concrete action (optional)

## Visual Suggestion
Description of supporting imagery

## Follow-up Prompts
1. First deepening question
2. Second deepening question
3. Third deepening question (optional)
```

---

## Model Configuration

**LLM:** Claude Sonnet 4.5 (via OpenRouter)
**Provider:** `https://openrouter.ai/api/v1`
**Model ID:** `anthropic/claude-sonnet-4.5`
**API Key:** `OPENROUTER_API_KEY` in `.env`

**Temperature by Stage:**
- Stage 1: **0.3** (factual)
- Stage 2: **0.4** (balanced)
- Stage 3: **0.5** (creative)
- Stage 4: **0.4** (focused)
- Stage 5: **0.7** (highly creative)

---

## Quality Criteria

### Stage Outputs
- ✓ **Stage 1:** Core principles identified, ~3,200 chars
- ✓ **Stage 2:** Broader trends identified, ~3,800 chars
- ✓ **Stage 3:** Universal lessons extracted, ~5,300 chars
- ✓ **Stage 4:** Brand-specific insights, ~4,500 chars
- ✓ **Stage 5:** 1-5 distinct opportunity cards

### Opportunity Quality
- ✓ **Distinct:** Not variations of same idea
- ✓ **Actionable:** 3-5 concrete next steps
- ✓ **Brand-relevant:** Mentions specific products/context
- ✓ **Implementable:** Not science fiction
- ✓ **Diverse:** Spans different innovation types

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No output generated | Check API key, OpenRouter credits, network |
| Brand research not found | Verify `data/brand-research/{brand-slug}/` exists |
| Invalid PDF | Check PDF not encrypted, has extractable text |
| Batch execution slow | Normal (36-48 min), use `--retry-failed` for failures |
| Temperature too high/low | Stage 5 uses 0.7 for creativity, earlier stages lower |

---

## Common Scenarios

### "I want to test one idea quickly"
```bash
python run_pipeline.py --input savannah-bananas --brand lactalis
```
→ Output: 5 opportunity cards in 90-120 seconds

### "I want to test all combinations"
```bash
python run_pipeline.py --batch
```
→ Output: 24 opportunity cards in 36-48 minutes

### "A few scenarios failed, retry them"
```bash
python run_pipeline.py --batch --retry-failed
```
→ Output: Only failed scenarios re-run

### "I want to check Stage 1-3 quality"
```bash
python test_stages_1_3.py
```
→ Output: 6 test results with stage outputs

---

## Success Metrics

**Batch Execution:**
- ≥95% success rate (23/24 scenarios pass)
- Average execution time <120 seconds per scenario
- All opportunity cards pass quality criteria

**Opportunity Quality:**
- Innovation type diversity: All 5 types represented
- Actionability: 100% have 3-5 next steps
- Brand relevance: 100% mention specific products
- Distinctiveness: 0% duplicate/variation ideas

---

## 24 Test Scenarios

```
# Savannah Bananas (Case Study) × 4 Brands
1-4:   savannah-bananas → {lactalis, mccormick, seventh-generation, colgate-palmolive}

# Premium Fast Food (Trend) × 4 Brands
5-8:   premium-fast-food → {lactalis, mccormick, seventh-generation, colgate-palmolive}

# Non-Alcoholic Beverage (Trend) × 4 Brands
9-12:  nonalcoholic-beverage → {lactalis, mccormick, seventh-generation, colgate-palmolive}

# Sacred Sync (Trend) × 4 Brands
13-16: sacred-sync → {lactalis, mccormick, seventh-generation, colgate-palmolive}

# Cat Dad Campaign (Spotted) × 4 Brands
17-20: cat-dad-campaign → {lactalis, mccormick, seventh-generation, colgate-palmolive}

# QR Garment Resale (Spotted) × 4 Brands
21-24: qr-garment-resale → {lactalis, mccormick, seventh-generation, colgate-palmolive}
```

---

## Documentation Links

- **Full Pipeline Documentation:** `/docs/pipeline-documentation.md`
- **Flow Diagram:** `/pipeline-flow-diagram.md` (visualize at mermaid.live)
- **Opportunity Card Format:** `/docs/opportunity-card-format.md`
- **Brand Research Structure:** `/docs/brand-research-data-structure.md`
- **Project Context:** `/CLAUDE.md`

---

**Last Updated:** 2025-10-07
**Version:** 1.0
