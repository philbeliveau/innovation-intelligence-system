"""
Stage 1: Input Processing and Inspiration Identification

This module defines the prompt template for Stage 1 of the Innovation
Intelligence Pipeline. Stage 1 extracts key inspiration elements from
input documents.
"""

from langchain.prompts import PromptTemplate


def get_prompt_template() -> PromptTemplate:
    """Get Stage 1 prompt template for inspiration identification.

    Returns:
        PromptTemplate configured for Stage 1 processing

    Example:
        >>> template = get_prompt_template()
        >>> chain = LLMChain(llm=llm, prompt=template)
    """

    template = """You are an innovation analyst reviewing an input document to identify key inspiration elements that could inform innovation strategies.

INPUT DOCUMENT:
{input_text}

TASK:
Carefully review the input document and extract the most valuable inspiration elements. Identify 3-5 key inspirations (innovations, strategies, or successful tactics) that stand out.

For each inspiration element, analyze:
- WHAT IT IS: Clear description of the innovation, strategy, or tactic
- WHY IT'S INTERESTING: What makes this noteworthy or remarkable
- POTENTIAL APPLICABILITY: How this insight could be applied in other contexts

OUTPUT FORMAT:
Structure your analysis as markdown with the following sections:

# Document Overview
[Provide a brief 2-3 sentence summary of the input document, its main topic, and overall context]

# Key Inspirations

## 1. [Inspiration Title]
**What it is:** [Clear description]
**Why it's interesting:** [What makes it noteworthy]
**Potential applicability:** [How it could be applied elsewhere]

## 2. [Inspiration Title]
**What it is:** [Clear description]
**Why it's interesting:** [What makes it noteworthy]
**Potential applicability:** [How it could be applied elsewhere]

[Continue for 3-5 inspirations total]

# Context Notes
[Summarize the overall significance of these inspirations. What patterns emerge? What makes this collection of insights valuable for innovation work?]

IMPORTANT:
- Extract exactly 3-5 inspirations (no more, no less)
- Be specific and concrete in descriptions
- Focus on actionable insights, not just interesting facts
- Ensure output follows the exact markdown structure above
"""

    return PromptTemplate(
        input_variables=["input_text"],
        template=template
    )
