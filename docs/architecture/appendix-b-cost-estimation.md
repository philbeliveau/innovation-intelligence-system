# Appendix B: Cost Estimation

## B.1 Token Usage Estimates

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

## B.2 Cost Optimization Strategies

1. **Use cheaper models for early stages** - DeepSeek ($0.14/1M) for Stages 1-2
2. **Cache brand profiles** - Reduce repeated token usage
3. **Optimize prompts** - Remove unnecessary instructions
4. **Token limits** - Set max_tokens per stage to prevent runaway generation

---
