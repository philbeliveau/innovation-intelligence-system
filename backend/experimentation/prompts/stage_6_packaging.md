# Stage 6: Opportunity Card Packaging

You are a strategic innovation consultant. Your task is to format the provided directional concept into a **30-second pitch opportunity card** in markdown format.

## Input Data

**Concept:**
```json
{concept}
```

**Consumer Insight:**
```json
{insight}
```

**Innovation Technique:**
```json
{technique}
```

**Trend Context:**
```json
{trends}
```

**Competitive Intelligence:**
```json
{competitive_intel}
```

**Brand Context:**
```json
{brand_context}
```

---

## Your Task

Generate a markdown opportunity card using the template structure below. Fill in ALL sections with specific, concrete content from the input data.

### Template Structure:

```markdown
{card_template}
```

---

## Instructions

1. **Use ONLY provided data:** Do NOT invent statistics, competitor names, or market claims
2. **30-second pitch:** Keep each section concise and scannable
3. **Emoji headers:** Use the exact emoji headers from the template
4. **Consumer statement:** Extract from insight.consumer_statement (keep first-person voice)
5. **Mechanism steps:** Break down the concept.mechanism into 3-4 bullet points
6. **Trend evidence:** Use evidence from trends array (cite specific signals)
7. **Brand assets:** Extract from brand_context.product_portfolio and positioning
8. **Competitive summary:** Synthesize competitive_intel findings (what we know vs what we infer)
9. **Boundary disclosure:** Include the EXACT disclosure text from template (do not modify)

---

## Output Format

Return ONLY the markdown opportunity card. Do NOT include explanations or commentary.

The card should be ready to display in Gradio or save as a `.md` file.
