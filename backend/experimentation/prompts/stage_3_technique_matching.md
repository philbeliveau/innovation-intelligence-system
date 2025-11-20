# Stage 3: Innovation Technique Matching

## Objective

Match each consumer insight to appropriate innovation techniques from SIT, TRIZ, and Doblin frameworks. Select techniques that are **defensible** (hard for competitors to copy) and **applicable** to the brand's resources and category.

---

## Inputs

### Consumer Insights (from Stage 2)
{insights}

### Brand Context
{brand_context}

---

## Innovation Technique Libraries

{sit_techniques}

{triz_principles}

{doblin_types}

---

## Matching Instructions

For each consumer insight, you must:

1. **Select Primary SIT Technique** (REQUIRED)
   - Choose 1 SIT technique that best addresses the consumer insight
   - Explain WHY this technique applies to the specific problem
   - Assess defensibility score (0.0-1.0):
     - 0.0-0.3: Easy to copy (low barrier to entry)
     - 0.4-0.6: Moderate defensibility (requires some investment)
     - 0.7-1.0: Hard to copy (requires unique assets, behavior change, or complex integration)

2. **Select Secondary TRIZ Principle** (CONDITIONAL - Only if SIT insufficient)
   - Use TRIZ ONLY if the consumer need is highly technical or SIT alone doesn't address complexity
   - Most consumer insights should be solved with SIT alone
   - If using TRIZ, explain why SIT was insufficient

3. **Map to Doblin Innovation Type** (REQUIRED)
   - Classify the innovation into one of the 10 Doblin types
   - This is for strategic portfolio classification, not technique selection

4. **Generate Transferability Mapping** (REQUIRED)
   - L1 Domain: How this applies to the brand's specific industry
   - L4 Universal: The fundamental principle that could transfer to any industry

---

## Output Format

Return a JSON object with this structure:

```json
{{
  "matched_techniques": [
    {{
      "insight_id": "<insight_id from input>",
      "primary_technique": {{
        "framework": "SIT",
        "technique": "<SIT technique name>",
        "rationale": "<2-3 sentences explaining why this technique applies>",
        "defensibility_score": 0.75
      }},
      "secondary_technique": {{
        "framework": "TRIZ",
        "technique": "<TRIZ principle name or null if not needed>",
        "rationale": "<Why TRIZ was needed, or null>"
      }},
      "doblin_type": "<Doblin innovation type>",
      "transferability": {{
        "L1_domain": "<Domain-specific application for this brand>",
        "L4_universal": "<Universal principle>"
      }}
    }}
  ]
}}
```

---

## Defensibility Assessment Criteria

When scoring defensibility (0.0-1.0), consider:

- **Asset Leverage**: Does it use unique brand assets competitors don't have? (+0.2)
- **Behavioral Shift**: Does it require customers to change habits? (+0.3)
- **Technical Complexity**: Hard to replicate technically? (+0.2)
- **Network Effects**: Gets better with more users? (+0.3)
- **Ease of Copying**: Can competitors launch similar in < 6 months? (-0.4)

---

## Example Output

```json
{{
  "matched_techniques": [
    {{
      "insight_id": "insight_001",
      "primary_technique": {{
        "framework": "SIT",
        "technique": "Task Unification",
        "rationale": "The consumer wants to reduce decision fatigue at point of purchase. Existing shelf labels can be assigned a NEW task: choice simplification. This leverages an existing resource (shelf) to perform an additional function (decision support).",
        "defensibility_score": 0.65
      }},
      "secondary_technique": null,
      "doblin_type": "Service",
      "transferability": {{
        "L1_domain": "Bakery shelf labels become decision-support tools for overwhelmed bread shoppers",
        "L4_universal": "Environmental cues can be repurposed to simplify complex choices"
      }}
    }}
  ]
}}
```

---

## Critical Reminders

- **SIT First**: Always try SIT before TRIZ. TRIZ is for complex technical problems only.
- **Defensibility Matters**: Higher scores = harder to copy = more valuable innovation
- **Brand Fit**: Ensure techniques leverage brand's existing resources, not hypothetical ones
- **Transferability**: L1 should be specific to industry, L4 should be universal enough to apply anywhere

Return ONLY the JSON object, no additional commentary.
