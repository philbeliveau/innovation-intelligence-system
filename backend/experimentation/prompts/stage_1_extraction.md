# Stage 1: Multi-Trend Decomposition with Abstraction Ladder

## Context
You are extracting structured trends from a WGSN/Mintel trend report with **multi-level abstraction** (L1-L4) to enable transferability across industries.

## Input Report Text
```
{report_text}
```

## Task
Extract ALL distinct trends from this report. For each trend, provide:

1. **Trend Name**: The trend identifier (e.g., "Witherwill", "Strategic Joy")
2. **Lifecycle Stage**: EMERGING, ACCELERATING, PEAKING, or DECLINING
3. **Timeline**: Emergence year and predicted peak year
4. **Evidence**: Market signals, statistics, examples (3-5 items)
5. **Weak Signals**: Early indicators or subtle patterns (2-3 items)
6. **Emotional Drivers**:
   - **Current Negative**: What consumers feel NOW (negative emotions)
   - **Aspirational Positive**: What consumers WANT to feel (positive emotions)
7. **Abstraction Ladder** (L1 → L4):
   - **L1 (Domain-Specific)**: CPG/industry-specific application
   - **L2 (Category-Level)**: Category pattern that crosses product types
   - **L3 (Cross-Category)**: Transferable mechanism that works across industries
   - **L4 (Universal Principle)**: Fundamental human dynamic

## Abstraction Ladder Examples

### Example 1: "Witherwill" Trend
- **L1**: "Gen Z dairy consumers want bread choices simplified at point of purchase"
- **L2**: "Grocery shoppers want to reduce decision fatigue in staple food categories"
- **L3**: "People seek to reduce cognitive load in routine daily decisions"
- **L4**: "Humans desire mental freedom from trivial choices"

### Example 2: "Strategic Joy" Trend
- **L1**: "CPG brands want to inject playfulness into functional products"
- **L2**: "Consumer brands want to balance utility with emotional uplift"
- **L3**: "Organizations want to make practical experiences more enjoyable"
- **L4**: "People seek to find pleasure in necessary activities"

## Output Format (JSON)
Return a JSON array of trend objects:

```json
{{
  "trends": [
    {{
      "trend_id": "unique_identifier",
      "name": "Trend Name",
      "lifecycle_stage": "ACCELERATING",
      "timeline": {{
        "emergence_year": 2024,
        "peak_year": 2027
      }},
      "evidence": [
        "Market signal 1 with specific example",
        "Market signal 2 with data/stat",
        "Market signal 3 with company example"
      ],
      "weak_signals": [
        "Early indicator 1",
        "Early indicator 2"
      ],
      "emotional_drivers": {{
        "current_negative": [
          "Decision fatigue",
          "Overwhelm",
          "Choice paralysis"
        ],
        "aspirational_positive": [
          "Clarity",
          "Simplicity",
          "Freedom"
        ]
      }},
      "abstraction_ladder": {{
        "L1_domain_specific": "Consumers overwhelmed by bread choices at grocery stores",
        "L2_category": "Shoppers want simplified product selection in staple categories",
        "L3_cross_category": "People seek to reduce cognitive load in daily routine decisions",
        "L4_universal": "Humans desire mental freedom from trivial choices"
      }}
    }}
  ]
}}
```

## Quality Criteria
- Extract 5-10 trends per report (if available)
- ALL trends MUST have complete L1-L4 abstraction ladder
- Emotional drivers should be SPECIFIC emotions, not vague statements
- Evidence should cite SPECIFIC examples from report (brand names, stats, examples)
- Lifecycle stage should match report indicators (look for keywords like "emerging", "growing", "mainstream")

## Constraints
- DO NOT invent trends not in the report
- DO NOT skip abstraction levels
- Keep each abstraction level to 1 sentence maximum
- Ensure L4 is truly universal (could apply to any human, any context)
