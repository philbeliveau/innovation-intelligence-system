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
Carefully review the input document and extract the TWO most compelling inspiration tracks. These are the top 2 most impactful insights that could drive innovation strategies.

For each track, provide:
- A descriptive title (concise but meaningful)
- A 2-3 sentence summary explaining what makes this insight valuable

OUTPUT FORMAT:
Structure your response EXACTLY as follows:

## Track 1: [Give it a descriptive title]

[Write 2-3 sentences summarizing the first main inspiration or pattern you identify. Focus on what makes this insight actionable and valuable for innovation work.]

## Track 2: [Give it a descriptive title]

[Write 2-3 sentences summarizing the second main inspiration or pattern you identify. Focus on what makes this insight actionable and valuable for innovation work.]

CRITICAL REQUIREMENTS:
- Extract EXACTLY 2 tracks (no more, no less)
- Use the EXACT format shown above with "## Track 1:" and "## Track 2:" headers
- Keep summaries focused and concise (2-3 sentences each)
- These top 2 tracks will be displayed in a vertical pipeline UI and used for all subsequent analysis stages
- Do NOT include additional tracks beyond these two
"""

    return PromptTemplate(
        input_variables=["input_text"],
        template=template
    )
