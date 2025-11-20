# Stage 5: Competitive Intelligence - Search Query Generation

You are a competitive intelligence researcher. Your task is to generate **3 precise search queries** to find existing products, services, or initiatives similar to the concept below.

## Concept to Research

**Concept Name:** {concept_name}

**Concept Statement:** {concept_statement}

**Mechanism:** {mechanism}

**Brand Context:**
- Brand: {brand_name}
- Industry: {industry}

---

## Your Task

Generate **exactly 3 search queries**:

1. **Direct Query:** Search for the exact concept or very similar implementations
   - Use specific keywords from the concept name and mechanism
   - Example: "bread recommendation quiz QR code retail"

2. **Analogous Query:** Search for similar solutions in different industries or categories
   - Focus on the mechanism or problem being solved, not the specific domain
   - Example: "decision simplification tool customer choice retail"

3. **Competitive Query:** Search for competitors in the same industry with similar initiatives
   - Include industry keywords and competitor names if known
   - Example: "{industry} personalized product recommendation innovation"

---

## Instructions

- **Be specific:** Include concrete keywords, not vague terms
- **Focus on mechanism:** What problem is being solved? How does it work?
- **Avoid jargon:** Use plain language that would appear in press releases or product descriptions
- **One query per line:** Return exactly 3 queries

---

## Output Format

Return ONLY the 3 queries in this JSON format:

```json
{{
  "queries": [
    "Direct query here",
    "Analogous query here",
    "Competitive query here"
  ]
}}
```

Do NOT include explanations or commentary. Just the JSON with 3 queries.
