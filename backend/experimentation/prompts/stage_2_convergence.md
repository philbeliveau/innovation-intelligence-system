# Stage 2: Consumer Insight Synthesis via Trend Convergence

## Context
You are generating **brand-specific consumer insights** by identifying convergence patterns across multiple trends and mapping them to the brand's category challenges.

{few_shot_examples}

## Input Data

### Trends (from Stage 1)
```json
{trends}
```

### Brand Context (from Stage 0)
```json
{brand_context}
```

## Task

### Step 1: Identify Trend Convergences
Find trends that share:
- **Common emotional drivers** (overlapping current negative OR aspirational positive emotions)
- **Related abstraction levels** (L2 or L3 patterns that complement each other)

### Step 2: Generate Brand-Specific Consumer Insights
For each relevant convergence, create a consumer insight using this formula:

```
"I'm a [brand's target customer] and I [current negative emotion]
because [brand-relevant problem]. I want to [aspirational positive]
through [brand's product category]."
```

### Step 3: Map Insight Dimensions
For each insight, identify:
- **Functional Need**: What practical problem to solve?
- **Emotional Need**: What feeling to achieve?
- **Social Need**: What identity/belonging to signal?
- **Brand Relevance Score**: 0.0-1.0 (does brand have permission to play here?)

## Example Output Structure

**Convergence**: "Witherwill" (decision fatigue) + "Strategic Joy" (finding pleasure in routine)

**Consumer Insight**: "I'm overwhelmed by bread choices at the grocery store - just tell me THE ONE bread for my family"

**Dimensions**:
- **Functional**: Simplify decision-making at point of purchase
- **Emotional**: Reduce cognitive load and decision fatigue
- **Social**: Feel confident I'm making the 'right' choice for my family
- **Brand Relevance**: 0.9 (high - bakery brand with 25 SKUs faces choice overload problem)

## Output Format (JSON)

```json
{{
  "insights": [
    {{
      "insight_id": "unique_identifier",
      "source_trends": ["trend_id_1", "trend_id_2"],
      "consumer_statement": "I'm a busy parent and I feel overwhelmed by bread choices because there are 25 SKUs on the shelf and I don't know which is best. I want to feel confident I'm making the right choice for my family through a simple recommendation tool.",
      "functional_need": "Simplify decision-making at point of purchase with personalized recommendation",
      "emotional_need": "Reduce cognitive load and achieve clarity and confidence",
      "social_need": "Signal that I'm a thoughtful parent making informed choices for my family",
      "brand_relevance_score": 0.9
    }}
  ],
  "convergence_count": 5
}}
```

## Quality Criteria
- Generate 3-7 insights per brand (focus on highest brand relevance scores)
- Consumer statements should be FIRST-PERSON and SPECIFIC to brand's category
- Functional needs should be ACTIONABLE (clear problem to solve)
- Brand relevance score should reflect:
  - 0.9-1.0: Brand has clear permission and assets to address
  - 0.7-0.8: Brand could address with strategic pivot
  - <0.7: Outside brand's current permission space

## Constraints
- DO NOT generate insights for trends with no brand relevance
- DO NOT invent consumer problems not grounded in trend emotional drivers
- DO NOT create generic insights - they must be SPECIFIC to brand's product category
- Consumer statements should be 1-2 sentences maximum
- Focus on MULTI-TREND convergences (at least 2 source trends per insight)
