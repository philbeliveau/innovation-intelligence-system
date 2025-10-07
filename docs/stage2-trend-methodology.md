# Stage 2: Trend Extraction Methodology

## Overview

Stage 2 of the Innovation Intelligence Pipeline performs **signal amplification through trend extraction**. This stage analyzes the inspiration elements identified in Stage 1 to uncover underlying trends, patterns, and broader contextual signals that explain why these innovations are emerging or succeeding.

**Critical Constraint:** Stage 2 operates entirely offline, using only the information present in the input document as processed through Stage 1. No external data sources, social media feeds, or real-time trend databases are accessed.

## Methodology: Pattern Recognition from Document Content

### 1. Inspiration Analysis

Stage 2 receives the structured output from Stage 1, which contains 3-5 inspiration elements, each with:
- Description of the innovation/strategy/tactic
- Analysis of why it's interesting
- Potential applicability in other contexts

The Stage 2 chain analyzes these inspirations to identify:
- **Recurring themes:** Patterns that appear across multiple inspirations
- **Common mechanisms:** Similar approaches to solving problems or creating value
- **Shared contexts:** Industry conditions, consumer needs, or market dynamics mentioned in the inspirations

### 2. Trend Identification Process

Stage 2 identifies 3-5 underlying trends using this process:

**Step 1: Theme Extraction**
- Review all Stage 1 inspirations for repeated concepts, approaches, or contexts
- Identify what makes these inspirations successful or noteworthy
- Look for common threads that connect seemingly different innovations

**Step 2: Trend Categorization**
Each identified trend is categorized into one of four types:

| Category | Description | Example |
|----------|-------------|---------|
| **BEHAVIORAL** | Changes in consumer behavior, preferences, or decision-making | Shift from passive consumption to active participation |
| **TECHNOLOGICAL** | New technologies, digital tools, or technical capabilities | Mobile-first engagement platforms |
| **CULTURAL** | Shifts in values, social norms, or cultural expectations | Demand for authentic, personality-driven brands |
| **ECONOMIC** | Business model changes, pricing strategies, or economic factors | Value-based pricing over cost-plus models |

**Step 3: Evidence Tracing**
For each trend, the analysis must:
- Cite specific inspirations that demonstrate the trend
- Quote or reference concrete examples from the Stage 1 output
- Avoid introducing information not present in the input

**Step 4: Signal Strength Assessment**
Each trend receives a signal strength rating:

- **HIGH:** Trend is explicitly mentioned multiple times across inspirations, with clear supporting evidence
- **MEDIUM:** Trend is clearly implied by 2+ inspirations or explicitly mentioned once with strong context
- **LOW:** Trend is implied by a single inspiration or mentioned peripherally

### 3. Offline Analysis Methodology

**No External Data Sources:**
Stage 2 does NOT:
- Query social media APIs for trending topics
- Access real-time trend databases
- Fetch external market research reports
- Use the LLM's general knowledge to introduce trends not in the document

**Document-Derived Trends Only:**
Stage 2 DOES:
- Extract trends explicitly mentioned in the input document
- Identify patterns clearly implied by the documented innovations
- Analyze broader context when it's discussed in the inspirations
- Infer underlying drivers based solely on evidence in the Stage 1 output

**Quality Control:**
To prevent hallucination, the Stage 2 prompt includes:
- Explicit instructions to work only with Stage 1 content
- Requirements to cite specific inspirations for each trend
- A "Confidence Assessment" section where the LLM must acknowledge any uncertainty about derivation from document vs. general knowledge

## Output Structure

Stage 2 produces a structured markdown document with three sections:

### 1. Identified Trends

Each trend includes:
- **Trend Name & Category:** Descriptive title with categorization (BEHAVIORAL/TECHNOLOGICAL/CULTURAL/ECONOMIC)
- **Description:** Clear explanation of what is changing and why it matters
- **Evidence from Inspirations:** Specific references to which Stage 1 inspirations demonstrate this trend
- **Signal Strength:** Rating (HIGH/MEDIUM/LOW)
- **Rationale for Signal Strength:** Explanation of the rating based on evidence

### 2. Trend Context

This section provides:
- **Pattern Summary:** Overarching patterns across trends and how they relate
- **Strategic Implications:** What trends collectively suggest about market direction, consumer needs, or innovation opportunities
- **Confidence Assessment:** Transparency about trend derivation from document content vs. potential hallucination

### 3. Quality Validation

The output structure enables manual review by:
- Making evidence traceability explicit (every trend must cite inspirations)
- Requiring signal strength rationale (prevents unsupported claims)
- Including confidence assessment (LLM acknowledges uncertainty)

## Examples of Trend Extraction

### Example 1: Savannah Bananas Baseball Team

**Stage 1 Inspirations Might Include:**
1. Entertainment-first approach to traditional sports
2. Social media-driven fan engagement
3. Premium pricing through scarcity and experience design
4. Personality-driven brand vs. traditional team identity

**Stage 2 Trend Extraction:**

**Trend 1: Experiential Entertainment Over Traditional Competition (CULTURAL)**
- **Evidence:** Inspirations #1 and #3 both emphasize creating memorable experiences rather than focusing solely on game outcomes
- **Signal Strength:** HIGH - Multiple inspirations explicitly discuss this shift
- **Implications:** Consumers increasingly value unique experiences over traditional product/service delivery

**Trend 2: Creator Economy Mechanics in Established Industries (TECHNOLOGICAL/ECONOMIC)**
- **Evidence:** Inspiration #2 describes social media-first engagement strategy; #4 highlights personality-driven branding similar to influencer marketing
- **Signal Strength:** MEDIUM - Pattern is clearly implied across inspirations but not explicitly labeled as "creator economy"
- **Implications:** Traditional businesses can adopt creator economy principles (personality, authenticity, community) to compete

## Implementation Notes

### LLM Configuration

- **Model:** Claude 3.5 Sonnet (via OpenRouter)
- **Temperature:** 0.4 (slightly higher than Stage 1 to encourage pattern recognition while maintaining rigor)
- **Max Tokens:** 3000 (sufficient for 3-5 detailed trend analyses)

### Integration with Stage 1

Stage 2 receives `stage1_output` as a text input containing the complete markdown-formatted Stage 1 analysis. The chain processes this entire document to extract trends.

### Output Persistence

Stage 2 output is saved to: `{output_dir}/stage2/trend-analysis.md`

This enables:
- Manual review of trend extraction quality
- Traceability between Stage 1 inspirations and Stage 2 trends
- Input for Stage 3 (General Translation)

## Validation and Quality Assurance

### Manual Review Checklist

After Stage 2 execution, reviewers should verify:

1. **Trend Derivation:**
   - [ ] Each trend can be traced to specific Stage 1 inspirations
   - [ ] No trends appear to be introduced from general knowledge
   - [ ] Evidence citations are specific and accurate

2. **Categorization:**
   - [ ] Every trend has a category (BEHAVIORAL/TECHNOLOGICAL/CULTURAL/ECONOMIC)
   - [ ] Categories are appropriate for the trend descriptions

3. **Signal Strength:**
   - [ ] Signal strength ratings have clear rationales
   - [ ] Ratings align with the evidence provided

4. **Output Completeness:**
   - [ ] 3-5 trends identified (not more, not less)
   - [ ] All required sections present (Identified Trends, Trend Context)
   - [ ] Confidence Assessment addresses potential hallucination concerns

### Known Limitations

**Hallucination Risk:**
Despite explicit instructions, LLMs may occasionally introduce trends from their general knowledge rather than strictly deriving them from the document. Manual review is essential.

**Pattern Recognition Constraints:**
If the input document discusses only a single innovation (one Stage 1 inspiration), Stage 2 may struggle to identify multiple trends. Best results occur with 3-5 diverse inspirations.

**Trend Granularity:**
The methodology aims for mid-level trends (neither too specific nor too broad). Overly specific trends may not generalize well in Stage 3; overly broad trends may lack actionable insights.

## Future Enhancements

Potential improvements to Stage 2 methodology:

1. **Confidence Scoring:** Quantitative confidence scores (0-1) for each trend based on evidence strength
2. **Trend Relationships:** Explicit mapping of how trends relate to each other (complementary, conflicting, sequential)
3. **Domain Tagging:** Tag trends by industry domain to aid Stage 4 brand contextualization
4. **Automated Validation:** Programmatic checks for evidence citation completeness before manual review

---

**Version:** 1.0
**Last Updated:** Story 2.2 Implementation
**Related Documents:**
- `docs/architecture.md` - Overall pipeline architecture
- `docs/prd.md` - Product requirements and Stage 2 specifications
- `pipeline/prompts/stage2_prompt.py` - Stage 2 prompt template implementation
