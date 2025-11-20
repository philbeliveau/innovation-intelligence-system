# Stage 4: Directional Concept Generation

## Objective

Generate 3-5 **directional concepts** (NOT detailed specifications) by applying matched innovation techniques to consumer insights. Each concept must remain at the "30-second pitch" level.

---

## 🚨 CRITICAL: No-Hallucination Boundaries

{no_hallucination_rules}

---

## Inputs

### Consumer Insights (from Stage 2)
{insights}

### Matched Techniques (from Stage 3)
{matched_techniques}

### Brand Context
{brand_context}

---

## Concept Generation Instructions

For each matched technique, generate a **directional concept** by applying the SIT/TRIZ technique to the consumer insight within the brand's context.

### What is a "Directional Concept"?

A directional concept is:
- ✅ A 30-second pitch describing WHAT it is and WHY it works
- ✅ Focused on DIRECTION (the idea), not implementation details
- ✅ Grounded in provided data (trends, insights, brand context)
- ❌ NOT a detailed product spec, business plan, or financial model

### Concept Requirements

Each concept must include:

1. **concept_name**: Clear, memorable name (3-5 words)
2. **concept_statement**: 1-sentence what-is-it statement
3. **mechanism**: How it works (mechanism only, not implementation steps)
4. **why_it_works**: Why it addresses the consumer insight (using provided data)
5. **boundary_disclosure**: Standard disclosure about what's NOT included

---

## Output Format

Return a JSON object with 3-5 concepts:

```json
{{
  "concepts": [
    {{
      "insight_id": "<insight_id from input>",
      "technique_id": "<reference to matched technique>",
      "concept_name": "The Bread Finder Tool",
      "concept_statement": "A 3-question quiz that recommends THE ONE bread for your family",
      "mechanism": "QR code on shelf → 3-question quiz (family size, dietary needs, taste preference) → Personalized recommendation → Product location in store",
      "why_it_works": "Applies Task Unification by assigning choice-simplification task to existing shelf labels. Reduces decision fatigue (consumer need) by transforming shelf into decision-support tool.",
      "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
    }}
  ]
}}
```

---

## Concept Quality Checklist

Before finalizing each concept, verify:

- [ ] **Directional, Not Detailed**: Stays at 30-second pitch level
- [ ] **Grounded in Data**: Uses ONLY provided trends, insights, brand context
- [ ] **Technique Application**: Clearly shows SIT/TRIZ technique in action
- [ ] **Consumer Problem Solved**: Addresses specific insight from Stage 2
- [ ] **Brand Fit**: Leverages brand's existing resources or category
- [ ] **No Financial Claims**: Zero revenue, TAM, market share, ROI mentions
- [ ] **No Competitive Claims**: No "first to market", "no one else does this"
- [ ] **No Market Stats**: No invented percentages or unverified research
- [ ] **Boundary Disclosure**: Includes explicit statement of what's excluded

---

## Example Concepts

### Example 1: Task Unification (Bakery)
```json
{{
  "concept_name": "Le Guide St-Méthode (The Bread Finder)",
  "concept_statement": "A decision-support tool where consumers answer 3 questions and receive ONE St-Méthode bread recommendation",
  "mechanism": "Shelf-mounted QR code → 3-question quiz → Algorithm matches to product → Store location displayed",
  "why_it_works": "Unifies choice-simplification task with existing shelf resource, directly addressing consumer insight 'I'm overwhelmed by bread choices'. Reduces cognitive load at point of purchase.",
  "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
}}
```

### Example 2: Subtraction (Meal Kits)
```json
{{
  "concept_name": "Recipe-Free Meal Kits",
  "concept_statement": "Meal kits with pre-measured ingredients but NO recipe cards—guided by voice assistant only",
  "mechanism": "Box contains ingredients + QR code → Scan to connect to voice assistant → Step-by-step audio cooking guidance → No paper waste",
  "why_it_works": "Applies Subtraction by removing recipe cards (essential component). Addresses insight 'I want to feel present while cooking, not reading instructions'. Removes distraction of paper while maintaining guidance.",
  "boundary_disclosure": "This is a directional concept generated from trend analysis and systematic innovation techniques. It does NOT include: financial projections or ROI estimates, detailed implementation plans, market validation or customer research, or competitive claims beyond documented search results."
}}
```

---

## Common Mistakes to Avoid

1. **Too Detailed**: Avoid implementation specs like "We'll use AWS Lambda with Python 3.9..."
2. **Invented Stats**: Never say "This could capture 15% market share" or "Studies show..."
3. **Competitive Hallucination**: Don't claim "No brand does this" or "First to market"
4. **Business Plan**: Concepts aren't business plans—no go-to-market, pricing, or validation steps
5. **Missing Technique**: Every concept must clearly show the SIT/TRIZ technique application

---

## Final Reminder

Generate **3-5 concepts** total. Stay directional. Use ONLY provided data. Include boundary disclosure in EVERY concept.

Return ONLY the JSON object, no additional commentary.
