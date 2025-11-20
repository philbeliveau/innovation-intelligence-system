# Stage 0: Brand Profile Enrichment Prompt

## Context
You are enriching a basic brand profile with additional context from recent news and market analysis.

{few_shot_examples}

## Input Brand Profile
```
{brand_profile}
```

## Task
Enrich this brand profile with:
1. **Positioning analysis**: Based on product portfolio, infer brand positioning in the market
2. **Recent news** (if available): Key developments, launches, or strategic moves from the past 12 months
3. **Competitive landscape**: Major competitors and market position

## Output Format (JSON)
Return a JSON object with this structure:

```json
{{
  "brand_name": "{brand_profile.brand_name}",
  "industry": "{brand_profile.industry}",
  "country": "{brand_profile.country}",
  "product_portfolio": {brand_profile.product_portfolio},
  "enrichment": {{
    "positioning": "Brief positioning statement (1-2 sentences)",
    "recent_news": [
      "Recent development 1",
      "Recent development 2"
    ],
    "competitive_landscape": "Brief competitive context (1-2 sentences)",
    "confidence_score": 0.0-1.0
  }}
}}
```

## Constraints
- DO NOT invent news or statistics
- If no recent news available from search, leave empty array
- Confidence score should reflect certainty of enrichment data (1.0 = from provided YAML only, 0.7-0.9 = from search results)
- Keep positioning and competitive landscape BRIEF (1-2 sentences max each)
