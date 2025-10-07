# LLM Model Configuration Guide

## Quick Start: Change Model Across Entire Pipeline

**⚡ To change the LLM model, edit ONE line in `.env`:**

```bash
# In .env file:
LLM_MODEL=deepseek/deepseek-chat
```

That's it! All stages (1-4) will automatically use the new model.

## Popular Model Options

### Fast & Cost-Effective
```bash
LLM_MODEL=deepseek/deepseek-chat          # DeepSeek V3.2 Exp (CURRENT)
LLM_MODEL=meta-llama/llama-3.3-70b        # Llama 3.3 70B
```

### High Performance
```bash
LLM_MODEL=anthropic/claude-3.5-sonnet     # Claude 3.5 Sonnet
LLM_MODEL=anthropic/claude-sonnet-4.5-20250514  # Claude Sonnet 4.5
LLM_MODEL=openai/gpt-4-turbo              # GPT-4 Turbo
```

### Specialized Models
```bash
LLM_MODEL=google/gemini-pro-1.5           # Google Gemini Pro 1.5
LLM_MODEL=mistralai/mixtral-8x7b          # Mixtral 8x7B
```

See full list at: https://openrouter.ai/models

## How It Works

### Centralized Configuration
- **Single Source of Truth:** `pipeline/utils.py:create_llm()`
- **All stages use:** `create_llm()` instead of hardcoded models
- **Model comes from:** `LLM_MODEL` environment variable in `.env`

### Stage-Specific Parameters
Each stage configures temperature/tokens based on its needs:

| Stage | Temperature | Max Tokens | Purpose |
|-------|-------------|------------|---------|
| Stage 1 | 0.3 | 2500 | Consistent analysis |
| Stage 2 | 0.4 | 3000 | Pattern recognition |
| Stage 3 | 0.5 | 3500 | Creative synthesis |
| Stage 4 | 0.5 | 4000 | Brand contextualization |

## Testing Different Models

```bash
# 1. Edit .env
nano .env  # Change LLM_MODEL value

# 2. Run pipeline
python run_pipeline.py savannah-bananas lactalis-canada

# 3. Compare outputs in data/test-outputs/
```

## Model Selection Guidelines

### For Development/Testing
- **Use:** `deepseek/deepseek-chat` (fast, cheap)
- **Why:** Quick iterations, cost-effective

### For Production Quality
- **Use:** `anthropic/claude-3.5-sonnet` or `claude-sonnet-4.5-20250514`
- **Why:** Superior reasoning, better brand contextualization

### For Budget Optimization
- **Use:** `meta-llama/llama-3.3-70b` or `deepseek/deepseek-chat`
- **Why:** Good balance of quality and cost

## Troubleshooting

### Model Not Available
```
Error: Model 'xyz' not found
```
**Solution:** Check model ID at https://openrouter.ai/models

### API Key Issues
```
Error: OPENROUTER_API_KEY not set
```
**Solution:** Ensure `.env` file has valid API key

### Performance Issues
- **Too slow:** Try `deepseek/deepseek-chat` or reduce max_tokens
- **Too expensive:** Switch from GPT-4 to Llama 3.3 or DeepSeek
- **Low quality:** Upgrade to Claude 3.5 Sonnet or GPT-4 Turbo

## Advanced: Per-Stage Model Override

If you need different models per stage, edit `pipeline/utils.py:create_llm()`:

```python
def create_llm(temperature: float = 0.5, max_tokens: int = 4000, stage: str = None) -> ChatOpenAI:
    # Add stage-specific logic here
    if stage == "stage4":
        model = os.getenv("STAGE4_MODEL", os.getenv("LLM_MODEL", "deepseek/deepseek-chat"))
    else:
        model = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
    # ... rest of function
```

---

**Current Configuration:** DeepSeek V3.2 Exp (`deepseek/deepseek-chat`)
