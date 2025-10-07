"""
Stage 2: Signal Amplification and Trend Extraction

This module defines the prompt template for Stage 2 of the Innovation
Intelligence Pipeline. Stage 2 extracts underlying trends and patterns
from Stage 1 inspiration elements.
"""

from langchain.prompts import PromptTemplate


def get_prompt_template() -> PromptTemplate:
    """Get Stage 2 prompt template for trend extraction.

    Returns:
        PromptTemplate configured for Stage 2 processing

    Example:
        >>> template = get_prompt_template()
        >>> chain = LLMChain(llm=llm, prompt=template)
    """

    template = """You are an innovation analyst analyzing inspiration elements to identify underlying trends and patterns.

STAGE 1 INSPIRATIONS (INPUT):
{stage1_output}

TASK:
Analyze the inspirations from Stage 1 to extract deeper trend patterns. Your goal is to identify 3-5 underlying trends that explain WHY these inspirations are emerging or succeeding.

CRITICAL CONSTRAINTS:
- Work ONLY with information present in the Stage 1 inspirations above
- DO NOT introduce trends from your general knowledge
- Extract trends that are explicitly mentioned or clearly implied in the document content
- If industry context or broader trends are mentioned in the inspirations, extract them
- Be conservative: only identify trends you can directly trace back to the input

ANALYSIS METHODOLOGY:
1. Review all Stage 1 inspirations for recurring themes and patterns
2. Identify underlying drivers: What consumer behavior shifts, industry movements, or emerging needs explain these inspirations?
3. Extract any broader context mentioned in the inspirations (industry trends, market shifts, cultural changes)
4. Categorize each trend into one of these types:
   - BEHAVIORAL: Changes in consumer behavior, preferences, or decision-making
   - TECHNOLOGICAL: New technologies, digital tools, or technical capabilities
   - CULTURAL: Shifts in values, social norms, or cultural expectations
   - ECONOMIC: Business model changes, pricing strategies, or economic factors

OUTPUT FORMAT:
Structure your analysis as markdown with the following sections:

# Identified Trends

## Trend 1: [Trend Name] (Category: [BEHAVIORAL/TECHNOLOGICAL/CULTURAL/ECONOMIC])
**Description:** [Clear explanation of the trend - what is changing and why it matters]
**Evidence from Inspirations:** [Specific references to which Stage 1 inspirations demonstrate this trend]
**Signal Strength:** [HIGH/MEDIUM/LOW]
**Rationale for Signal Strength:** [Explain why you rated it this way based on the evidence]

## Trend 2: [Trend Name] (Category: [BEHAVIORAL/TECHNOLOGICAL/CULTURAL/ECONOMIC])
**Description:** [Clear explanation of the trend]
**Evidence from Inspirations:** [Specific references to Stage 1 inspirations]
**Signal Strength:** [HIGH/MEDIUM/LOW]
**Rationale for Signal Strength:** [Explain rating]

[Continue for 3-5 trends total]

# Trend Context

**Pattern Summary:** [What overarching patterns emerge across these trends? How do they relate to each other?]

**Strategic Implications:** [What do these trends collectively suggest about market direction, consumer needs, or innovation opportunities?]

**Confidence Assessment:** [How confident are you that these trends are derived from the document content versus general knowledge? Note any concerns about potential hallucination.]

SIGNAL STRENGTH GUIDELINES:
- HIGH: Trend is explicitly mentioned multiple times across inspirations, with clear supporting evidence
- MEDIUM: Trend is clearly implied by 2+ inspirations or explicitly mentioned once with strong context
- LOW: Trend is implied by a single inspiration or mentioned peripherally

QUALITY OVER QUANTITY:
- Aim for 3-4 trends with MEDIUM or HIGH signal strength
- Each trend should be supported by:
  * Multiple inspirations (preferred), OR
  * Multiple pieces of evidence from a single inspiration, OR
  * Clear pattern visible across different inspiration aspects
- Do NOT force a 4th or 5th trend if evidence is thin
- Better to have 3 strong, well-supported trends than 5 weak ones
- Only include LOW signal strength trends if they represent particularly significant patterns

EVIDENCE REQUIREMENTS BY SIGNAL STRENGTH:
- HIGH: 2+ explicit inspirations OR extensive evidence from 1 inspiration
- MEDIUM: 1 strong inspiration with multiple supporting details
- LOW: 1 inspiration with limited supporting context (use sparingly - only if highly significant)

IMPORTANT:
- Identify 3-4 high-quality trends (prefer quality over hitting a specific count)
- Each trend MUST be traceable to specific content in Stage 1 inspirations
- Be explicit about which inspirations support each trend
- Categorize every trend (BEHAVIORAL, TECHNOLOGICAL, CULTURAL, or ECONOMIC)
- Assign signal strength (HIGH, MEDIUM, LOW) with clear rationale
- Avoid LOW signal strength trends unless absolutely necessary
- In Confidence Assessment, be honest about derivation from document vs. general knowledge
"""

    return PromptTemplate(
        input_variables=["stage1_output"],
        template=template
    )
