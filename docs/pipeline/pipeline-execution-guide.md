# Pipeline Execution Guide

## Overview

This guide provides step-by-step instructions for running the Innovation Intelligence Pipeline (Stages 1-4), along with troubleshooting tips discovered during integration testing.

## Quick Start

### Single Scenario Execution

```bash
# Run complete pipeline for one input/brand combination
python run_pipeline.py <input-id> <brand-id>

# Example:
python run_pipeline.py savannah-bananas lactalis-canada
```

### Integration Testing

```bash
# Quick validation (2 scenarios, ~4 minutes)
python test_stages_1_4_quick.py

# Full integration test (8 scenarios, ~15-20 minutes)
python test_stages_1_4_integration.py

# Error handling validation
python test_error_handling.py
```

## Prerequisites

### 1. Environment Configuration

Ensure `.env` file exists with required variables:

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# LLM Model (change this one value to switch models)
LLM_MODEL=deepseek/deepseek-chat
```

**See `docs/model-configuration.md` for model options**

### 2. Verify Data Files

```bash
# Check input documents
ls documentation/document/

# Check brand profiles
ls data/brand-profiles/

# Check research data
ls docs/web-search-setup/*-research.md
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Execution Process

### Stage-by-Stage Flow

The pipeline executes 4 stages sequentially:

| Stage | Purpose | Input | Output | Avg Time |
|-------|---------|-------|--------|----------|
| **1** | Input Processing | PDF document | 3-5 inspirations | ~15s |
| **2** | Signal Amplification | Stage 1 output | 3-4 trends | ~15s |
| **3** | General Translation | Stages 1+2 | Universal lessons | ~25s |
| **4** | Brand Contextualization | Stage 3 + brand data | Brand-specific insights | ~45s |

**Total Average:** ~100-140 seconds (1.7-2.3 minutes) per scenario

### Output Structure

```
data/test-outputs/{input-id}-{brand-id}-{timestamp}/
├── stage1/
│   └── inspiration-analysis.md
├── stage2/
│   └── trend-analysis.md
├── stage3/
│   └── universal-lessons.md
├── stage4/
│   └── brand-contextualization.md
└── logs/
    ├── pipeline.log      # All debug logs
    └── errors.log        # Errors only
```

## Common Issues & Solutions

### 1. API Rate Limiting

**Symptom:**
```
Error: Rate limit exceeded (429)
```

**Solution:**
- Wait 60 seconds between runs
- Use `LLM_MODEL=deepseek/deepseek-chat` for higher rate limits
- Check OpenRouter dashboard for usage

### 2. Missing Research Data

**Symptom:**
```
WARNING: Research file not found: docs/web-search-setup/{brand-id}-research.md
WARNING: Proceeding without research data
```

**Impact:**
- Pipeline completes successfully (non-fatal)
- Stage 4 output quality reduced (degraded mode)
- Brand contextualization less specific

**Solution:**
- Verify research file exists: `ls docs/web-search-setup/`
- File naming must match: `{brand-id}-research.md`
- If intentional, outputs will indicate degraded mode

### 3. PDF Loading Failures

**Symptom:**
```
FileNotFoundError: Input PDF not found: documentation/document/{filename}
```

**Solution:**
```bash
# Verify PDF exists
ls documentation/document/

# Check manifest
cat data/input-manifest.yaml | grep "filename:"

# Ensure file_path in manifest matches actual location
```

### 4. Slow Execution Times

**Symptom:**
- Scenarios exceed 5 minutes
- Timeout errors after 10 minutes

**Possible Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Large research files (>50KB) | Expected behavior for Stage 4 |
| High LLM API latency | Switch to faster model (`deepseek/deepseek-chat`) |
| Network issues | Check internet connection, retry |
| Model overloaded | Try different model or wait 5 minutes |

### 5. Invalid Brand Profile

**Symptom:**
```
ValueError: Invalid brand profile YAML
```

**Solution:**
```bash
# Validate YAML syntax
python test_brand_profiles.py

# Check for common issues:
# - Missing quotes around special characters
# - Incorrect indentation (use 2 spaces)
# - Unclosed lists or dictionaries
```

### 6. LangChain Deprecation Warnings

**Symptom:**
```
LangChainDeprecationWarning: The class `LLMChain` was deprecated...
```

**Impact:**
- No impact on functionality
- Warning only, pipeline continues normally

**Solution:**
- Ignore for now (planned upgrade to RunnableSequence in future)

## Performance Optimization

### Baseline Performance (DeepSeek V3.2)

Based on integration testing results:

- **Average per scenario:** 113.73 seconds (1.9 minutes)
- **Minimum:** 88.43 seconds (1.5 minutes)
- **Maximum:** 139.02 seconds (2.3 minutes)
- **Target met:** ✅ <30 minutes per scenario

### Speed vs. Quality Trade-offs

| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| `deepseek/deepseek-chat` | ⚡⚡⚡ Fast | ✅ Good | 💰 Low |
| `anthropic/claude-3.5-sonnet` | ⚡⚡ Medium | ✅✅ Excellent | 💰💰 Medium |
| `openai/gpt-4-turbo` | ⚡ Slow | ✅✅ Excellent | 💰💰💰 High |

**Recommendation:**
- **Development/Testing:** Use DeepSeek (fast, cheap)
- **Production:** Use Claude 3.5 (best balance)
- **High-Stakes:** Use GPT-4 Turbo (highest quality)

## Quality Validation

### Manual Spot-Check Process

After running integration test, manually review 2 random outputs:

```bash
# Review Stage 1
cat data/test-outputs/{random-scenario}/stage1/inspiration-analysis.md
# ✅ Verify: Inspirations relevant to input document

# Review Stage 2
cat data/test-outputs/{random-scenario}/stage2/trend-analysis.md
# ✅ Verify: Trends derived from document content

# Review Stage 3
cat data/test-outputs/{random-scenario}/stage3/universal-lessons.md
# ✅ Verify: Lessons are universal and generalizable

# Review Stage 4
cat data/test-outputs/{random-scenario}/stage4/brand-contextualization.md
# ✅ Verify: Insights are brand-specific
```

### Quality Criteria (from Integration Testing)

**Stage 1: Inspirations**
- [ ] 3-5 distinct inspiration elements
- [ ] Directly relevant to input document
- [ ] Actionable and specific

**Stage 2: Trends**
- [ ] 3-4 identified trends
- [ ] Evidence clearly derived from Stage 1
- [ ] No hallucination or external knowledge

**Stage 3: Universal Lessons**
- [ ] Brand-agnostic and generalizable
- [ ] Applicable across industries
- [ ] Connected to innovation frameworks (TRIZ/SIT)

**Stage 4: Brand Context**
- [ ] References specific brand products/initiatives
- [ ] Aligns with brand strategic priorities
- [ ] Addresses specific target customer segments
- [ ] Gracefully handles missing research data

## Error Handling Validation

### Testing Graceful Degradation

```bash
# Test with missing research file
python test_error_handling.py
```

**Expected Behavior:**
- ✅ Pipeline completes (no fatal errors)
- ✅ Warning logged about missing research
- ✅ Stage 4 generates degraded output
- ✅ Output indicates "degraded mode" in results

**Failure Modes NOT Allowed:**
- ❌ Fatal exception stops pipeline
- ❌ No output generated
- ❌ Silent failure (no warnings logged)

## Debugging Tips

### Enable Debug Logging

```python
# In run_pipeline.py or test scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs

```bash
# View full pipeline log
cat data/test-outputs/{scenario}/logs/pipeline.log

# View errors only
cat data/test-outputs/{scenario}/logs/errors.log

# Search for specific stage
grep "Stage 3" data/test-outputs/{scenario}/logs/pipeline.log
```

### Monitor LLM API Calls

Check logs for:
- Request timing: `HTTP Request: POST https://openrouter.ai/...`
- Response times: Look for delays between request/response
- Token usage: Available in OpenRouter dashboard

## Integration Test Workflows

### Pre-Stage 5 Validation Checklist

Before developing Stage 5:

- [ ] Run `test_stages_1_4_quick.py` - passes in <5 minutes
- [ ] Verify 2/2 scenarios complete successfully
- [ ] Average execution time <3 minutes per scenario
- [ ] Manual spot-check confirms quality criteria
- [ ] Error handling test passes (degraded mode works)
- [ ] Review `test-summary.md` for any anomalies

### Continuous Integration

For ongoing development:

```bash
# Quick smoke test (2 scenarios)
python test_stages_1_4_quick.py

# Full validation (8 scenarios, before major releases)
python test_stages_1_4_integration.py

# Error handling regression test
python test_error_handling.py
```

## Next Steps

After successful integration testing:

1. **Review Outputs:** Manually spot-check 2 random scenarios
2. **Optimize Prompts:** Based on quality findings
3. **Performance Baseline:** Document in `performance-baseline.md`
4. **Proceed to Stage 5:** Opportunity generation development

---

**Last Updated:** Based on Story 3.4 integration testing
**Model Used:** DeepSeek V3.2 Exp (`deepseek/deepseek-chat`)
