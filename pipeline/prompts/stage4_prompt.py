"""
Stage 4: Brand Contextualization with Research Data

This module defines the prompt template for Stage 4 of the Innovation
Intelligence Pipeline. Stage 4 customizes universal lessons from Stage 3
for a specific brand using brand profile and comprehensive research data.
"""

from langchain.prompts import PromptTemplate


def get_prompt_template() -> PromptTemplate:
    """Get Stage 4 prompt template for brand contextualization.

    Returns:
        PromptTemplate configured for Stage 4 processing

    Example:
        >>> template = get_prompt_template()
        >>> chain = LLMChain(llm=llm, prompt=template)
    """

    template = """You are a brand innovation strategist specializing in translating universal innovation principles into brand-specific strategic insights.

BRAND PROFILE:
{brand_profile}

BRAND RESEARCH DATA:
{research_data}

STAGE 3 UNIVERSAL LESSONS (INPUT):
{stage3_output}

TASK:
Transform the universal lessons from Stage 3 into brand-specific strategic insights for this particular brand. Use the brand profile and comprehensive research data to deeply customize each lesson for this brand's unique context.

BRAND CONTEXTUALIZATION METHODOLOGY:
1. Review the brand profile to understand: positioning, products, target customers, strategic priorities
2. Review the comprehensive research data (8 sections covering innovations, strategy, market context, news)
3. For each universal lesson from Stage 3, ask:
   - How does this principle specifically apply to THIS brand's products and services?
   - How does this align with or challenge THIS brand's current strategic priorities?
   - What makes this relevant to THIS brand's target customers and market position?
   - How could THIS brand implement this given their capabilities and constraints?
4. Generate 5-7 brand-specific strategic insights that are actionable for THIS brand

CRITICAL BRAND-SPECIFICITY REQUIREMENT:
- INCLUDE specific references to this brand's products (from profile and research data)
- INCLUDE specific references to this brand's customers and market positioning
- INCLUDE specific references to this brand's strategic priorities and recent initiatives
- MAKE each insight actionable with concrete next steps for THIS brand
- CONNECT insights to this brand's competitive context and market trends
- REFERENCE recent innovations, news, or market signals specific to this brand

OUTPUT FORMAT:
Structure your analysis as markdown with the following sections:

# Brand-Specific Innovation Strategy

## Brand Context Summary

**Brand Overview:** [Synthesize brand profile and research data - what defines this brand's current position?]

**Strategic Priorities:** [What are this brand's key strategic priorities based on profile and research data?]

**Innovation Context:** [What recent innovations, market trends, or competitive dynamics are most relevant for this brand?]

**Target Customer Insights:** [Who are this brand's customers and what unique needs/preferences do they have?]

---

## Brand-Specific Strategic Insights

### 1. [Insight Title - Specific to This Brand]

**The Opportunity:** [Clear statement of the brand-specific opportunity derived from the universal lesson. Reference specific brand products, customers, or strategic priorities.]

**Why It Fits This Brand:** [Explain why this insight is particularly relevant for THIS brand given their positioning, products, customers, and strategic context. Reference research data.]

**Concrete Application:** [Specific, actionable next steps for THIS brand to implement this insight. Be concrete about products, channels, customer segments, etc.]

**Expected Impact:** [What business outcomes could THIS brand expect? Reference their strategic priorities and competitive context.]

**Relevant Context:** [Optional - cite specific recent innovations, news, or market signals from research data that support this insight]

---

### 2. [Insight Title - Specific to This Brand]

**The Opportunity:** [Brand-specific opportunity statement]

**Why It Fits This Brand:** [Relevance explanation with research references]

**Concrete Application:** [Actionable next steps for THIS brand]

**Expected Impact:** [Business outcomes for THIS brand]

**Relevant Context:** [Optional research data citations]

---

[Continue for 5-7 insights total]

## Strategic Synthesis

**Core Innovation Themes:** [What overarching innovation themes emerge for THIS brand? How do these insights work together to form a coherent strategy?]

**Differentiation Opportunities:** [Which insights offer the strongest potential for THIS brand to differentiate from competitors? Reference competitive context from research data.]

**Implementation Priorities:** [Given THIS brand's strategic priorities and capabilities, which insights should be prioritized? Why?]

**Risk Considerations:** [What risks or challenges should THIS brand consider when implementing these insights? Be specific to their context.]

BRAND-SPECIFIC QUALITY CRITERIA:
- **Deeply Customized**: Every insight references specific brand products, customers, or strategic priorities
- **Research-Grounded**: Insights leverage the comprehensive research data (innovations, strategy, market context, news)
- **Actionable**: Concrete next steps that THIS brand can take (not generic advice)
- **Strategic Fit**: Aligns with THIS brand's positioning and strategic priorities
- **Competitive Awareness**: Considers THIS brand's competitive context and market trends
- **Customer-Centric**: Addresses THIS brand's specific target customers and their needs

RESEARCH DATA INTEGRATION NOTES:
- The research data contains 8 comprehensive sections (~550-720 lines, 35-48KB)
- Leverage all sections: Brand Overview, Product Portfolio, Recent Innovations, Strategy, Customers, Sustainability, Competitive Context, Recent News
- Reference specific innovations, initiatives, or news items when they support your insights
- If research data is missing or limited, rely more heavily on brand profile structure

IMPORTANT:
- Generate exactly 5-7 brand-specific strategic insights (no more, no less)
- Each insight MUST reference specific brand products, customers, or strategic context
- Each insight MUST be actionable with concrete next steps for THIS brand
- Each insight MUST explain business impact for THIS brand specifically
- Leverage research data throughout to ground insights in brand reality
- Ensure output follows the exact markdown structure above
- This is the critical differentiation layer - quality and brand-specificity are paramount
"""

    return PromptTemplate(
        input_variables=["brand_profile", "research_data", "stage3_output"],
        template=template
    )
