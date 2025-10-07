"""
Stage 5: Opportunity Generation Chain

This module defines the prompt template and structured output parser for Stage 5
of the Innovation Intelligence Pipeline. Stage 5 generates exactly 5 distinct,
actionable innovation opportunities from brand-specific insights.
"""

from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


def get_output_parser() -> StructuredOutputParser:
    """Get structured output parser for 5 opportunity cards.

    Returns:
        StructuredOutputParser configured to extract 5 opportunities

    Example:
        >>> parser = get_output_parser()
        >>> opportunities = parser.parse(llm_output)
        >>> print(len(opportunities['opportunities']))  # Should be 5
    """

    response_schemas = [
        ResponseSchema(
            name="opportunities",
            description="Array of exactly 5 innovation opportunities",
            type="array"
        )
    ]

    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return parser


def get_prompt_template() -> PromptTemplate:
    """Get Stage 5 prompt template for opportunity generation.

    Returns:
        PromptTemplate configured for Stage 5 processing

    Example:
        >>> template = get_prompt_template()
        >>> chain = LLMChain(llm=llm, prompt=template)
    """

    parser = get_output_parser()
    format_instructions = parser.get_format_instructions()

    template = """You are an innovation strategist who generates actionable, brand-specific innovation opportunities from strategic insights.

BRAND-SPECIFIC INSIGHTS (FROM STAGE 4):
{stage4_output}

BRAND: {brand_name}
INPUT SOURCE: {input_source}

TASK:
Generate exactly 5 distinct, actionable innovation opportunities based on the brand-specific insights from Stage 4. Each opportunity should be ready for immediate consideration by the innovation team.

OPPORTUNITY GENERATION METHODOLOGY:
1. Review all brand-specific strategic insights from Stage 4
2. Identify the most compelling innovation directions for this brand
3. Generate exactly 5 opportunities that span different innovation types
4. Ensure each opportunity is distinct (not variations of the same idea)
5. Make each opportunity immediately actionable with concrete next steps
6. Provide customer value and business impact for each opportunity

INNOVATION TYPE DIVERSITY REQUIREMENT:
Your 5 opportunities MUST span these different innovation types:
- Product innovation (new or enhanced products)
- Service innovation (new or enhanced services/experiences)
- Marketing innovation (new marketing approaches, campaigns, positioning)
- Experience innovation (customer touchpoints, retail, digital experiences)
- Partnership innovation (collaborations, co-branding, ecosystem plays)

CRITICAL OPPORTUNITY REQUIREMENTS:
Each opportunity MUST:
✓ Address specific brand needs identified in Stage 4 insights
✓ Leverage insights from the original input source
✓ Be implementable (not science fiction or distant future speculation)
✓ Provide clear customer value proposition
✓ Include concrete, actionable next steps (3-5 specific actions)
✓ Be distinct from other opportunities (not just variations)

OUTPUT STRUCTURE FOR EACH OPPORTUNITY:
For each of the 5 opportunities, provide:

**title**: [Compelling, specific title for this innovation opportunity - max 10 words]

**innovation_type**: [One of: Product, Service, Marketing, Experience, Partnership]

**description**: [2-3 paragraph description covering:
  - Paragraph 1: What is the opportunity? What specific innovation is being proposed?
  - Paragraph 2: Why does this matter for this brand and their customers? What problem does it solve or value does it create?
  - Paragraph 3: How does this leverage the insights from Stage 4? What makes this feasible and compelling now?]

**actionability_items**: [Array of 3-5 concrete next steps, each as a bullet point. Must be specific actions like:
  - "Conduct customer research with [specific segment] to validate [specific hypothesis]"
  - "Partner with [type of company] to develop [specific capability]"
  - "Prototype [specific feature/product] using [specific approach]"
  NOT vague like "Do research" or "Find partners"]

**visual_description**: [1-2 sentence description of a suggested visual/image that would represent this opportunity. Be specific about what the image should show to bring the opportunity to life.]

**follow_up_prompts**: [Array of 2-3 thought-provoking questions that help the innovation team explore this opportunity deeper. Questions should prompt strategic thinking like:
  - "How might we adapt this for [specific customer segment or use case]?"
  - "What would success look like in 6 months vs 18 months?"
  - "Which partners could accelerate this and what value would we exchange?"]

DIVERSITY AND DISTINCTNESS REQUIREMENTS:
- Each opportunity must be fundamentally different (not "mobile app version" vs "web version" of same idea)
- Opportunities should span different innovation types (see list above)
- Opportunities should vary in timeframe (some quick wins, some longer-term bets)
- Opportunities should address different customer needs or business objectives
- Avoid creating multiple opportunities that are just different flavors of the same concept

QUALITY CRITERIA:
- **Specific**: References specific brand products, customer segments, or strategic priorities
- **Actionable**: Has concrete next steps that can be initiated within 30 days
- **Valuable**: Clear customer value proposition and business impact
- **Feasible**: Can be implemented with reasonable resources (not requiring impossible technology or partnerships)
- **Distinct**: Each opportunity is fundamentally different from the others
- **Creative**: Demonstrates innovative thinking beyond obvious extensions of current offerings

{format_instructions}

IMPORTANT:
- Generate EXACTLY 5 opportunities (no more, no less)
- Ensure innovation type diversity across the 5 opportunities
- Each opportunity must be distinct and not a variation of another
- Each opportunity must have 3-5 actionability items
- Each opportunity must have 2-3 follow-up prompts
- Use the exact JSON structure specified in the format instructions
- This is the core value delivery of the pipeline - quality is paramount
"""

    return PromptTemplate(
        input_variables=["stage4_output", "brand_name", "input_source"],
        template=template,
        partial_variables={"format_instructions": format_instructions}
    )
