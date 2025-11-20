"""Output Formatters for Pipeline Stages

Converts structured JSON outputs from each stage into human-readable markdown
for Gradio UI display.
"""

from typing import Dict, Any, List
from datetime import datetime


def format_stage1_to_markdown(stage1_output: Dict[str, Any]) -> str:
    """Format Stage 1 (Input Processing) output as markdown

    Args:
        stage1_output: Stage 1 structured output with extractedText and mechanisms

    Returns:
        Formatted markdown string
    """
    md_parts = []

    # Header
    md_parts.append("# Stage 1: Extraction\n")
    md_parts.append("*Input processing and mechanism extraction*\n")
    md_parts.append("\n")

    # Extracted Text Summary
    extracted_text = stage1_output.get("extractedText", "")
    if extracted_text:
        char_count = len(extracted_text)
        word_count = len(extracted_text.split())
        md_parts.append("## Document Statistics\n")
        md_parts.append("\n")
        md_parts.append(f"- **Characters**: {char_count:,}\n")
        md_parts.append(f"- **Words**: {word_count:,}\n")
        md_parts.append("\n")
        md_parts.append("### Preview\n")
        md_parts.append("\n")
        md_parts.append(f"> {extracted_text[:300].strip()}...\n")
        md_parts.append("\n")

    # Mechanisms
    mechanisms = stage1_output.get("mechanisms", [])
    if mechanisms:
        md_parts.append(f"## Extracted Mechanisms ({len(mechanisms)})\n")
        md_parts.append("\n")

        for idx, mechanism in enumerate(mechanisms, start=1):
            md_parts.append(f"### {idx}. **{mechanism.get('title', 'Untitled')}**\n")
            md_parts.append("\n")
            md_parts.append(f"{mechanism.get('description', '')}\n")
            md_parts.append("\n")

            # Technique
            technique = mechanism.get('technique')
            if technique:
                md_parts.append(f"**Technique**: `{technique}`\n")
                md_parts.append("\n")

            if idx < len(mechanisms):
                md_parts.append("---\n")
                md_parts.append("\n")

    return "".join(md_parts)


def format_stage2_to_markdown(stage2_output: Dict[str, Any]) -> str:
    """Format Stage 2 (Signal Amplification) output as markdown

    Args:
        stage2_output: Stage 2 structured output with signals

    Returns:
        Formatted markdown string
    """
    md_parts = []

    # Header
    md_parts.append("# Stage 2: Signals\n")
    md_parts.append("*Amplified trend signals from document*\n")
    md_parts.append("\n")

    # Signals
    signals = stage2_output.get("signals", [])
    if signals:
        md_parts.append(f"## Identified Signals ({len(signals)})\n")
        md_parts.append("\n")

        for idx, signal in enumerate(signals, start=1):
            md_parts.append(f"### {idx}. **{signal.get('title', 'Untitled Signal')}**\n")
            md_parts.append("\n")
            md_parts.append(f"{signal.get('description', '')}\n")
            md_parts.append("\n")

            # Strength/Evidence
            strength = signal.get('strength')
            if strength:
                md_parts.append(f"**Strength**: `{strength}`\n")
                md_parts.append("\n")

            evidence = signal.get('evidence', [])
            if evidence:
                md_parts.append("**Evidence**:\n")
                md_parts.append("\n")
                for item in evidence:
                    md_parts.append(f"- {item}\n")
                md_parts.append("\n")

            if idx < len(signals):
                md_parts.append("---\n")
                md_parts.append("\n")
    else:
        md_parts.append("*No signals extracted*\n")
        md_parts.append("\n")

    return "".join(md_parts)


def format_stage3_to_markdown(stage3_output: Dict[str, Any]) -> str:
    """Format Stage 3 (General Translation) output as markdown

    Args:
        stage3_output: Stage 3 structured output with insights

    Returns:
        Formatted markdown string
    """
    md_parts = []

    # Header
    md_parts.append("# Stage 3: Insights\n")
    md_parts.append("*Generalized consumer insights*\n")
    md_parts.append("\n")

    # Insights
    insights = stage3_output.get("insights", [])
    if insights:
        md_parts.append(f"## Consumer Insights ({len(insights)})\n")
        md_parts.append("\n")

        for idx, insight in enumerate(insights, start=1):
            md_parts.append(f"### {idx}. **{insight.get('title', 'Untitled Insight')}**\n")
            md_parts.append("\n")
            md_parts.append(f"{insight.get('insight', '')}\n")
            md_parts.append("\n")

            # Consumer need
            need = insight.get('consumer_need')
            if need:
                md_parts.append(f"**Consumer Need**\n")
                md_parts.append("\n")
                md_parts.append(f"> _{need}_\n")
                md_parts.append("\n")

            # Opportunity space
            opportunity = insight.get('opportunity')
            if opportunity:
                md_parts.append(f"**Opportunity Space**\n")
                md_parts.append("\n")
                md_parts.append(f"{opportunity}\n")
                md_parts.append("\n")

            if idx < len(insights):
                md_parts.append("---\n")
                md_parts.append("\n")
    else:
        md_parts.append("*No insights generated*\n")
        md_parts.append("\n")

    return "".join(md_parts)


def format_stage4_to_markdown(stage4_output: Dict[str, Any]) -> str:
    """Format Stage 4 (Brand Contextualization) output as markdown

    Args:
        stage4_output: Stage 4 structured output with brand-specific preliminary concepts

    Returns:
        Formatted markdown string
    """
    md_parts = []

    # Header
    md_parts.append("# Stage 4: Ideation\n")
    md_parts.append("*Brand-contextualized preliminary concepts*\n")
    md_parts.append("\n")

    # Preliminary concepts
    preliminary = stage4_output.get("preliminary", [])
    if preliminary:
        md_parts.append(f"## Preliminary Concepts ({len(preliminary)})\n")
        md_parts.append("\n")

        for idx, concept in enumerate(preliminary, start=1):
            md_parts.append(f"### {idx}. **{concept.get('title', 'Untitled Concept')}**\n")
            md_parts.append("\n")
            md_parts.append(f"{concept.get('description', '')}\n")
            md_parts.append("\n")

            # Brand fit
            brand_fit = concept.get('brand_fit')
            if brand_fit:
                md_parts.append(f"**Brand Fit**\n")
                md_parts.append("\n")
                md_parts.append(f"{brand_fit}\n")
                md_parts.append("\n")

            # Mechanism
            mechanism = concept.get('mechanism')
            if mechanism:
                md_parts.append(f"**Mechanism**\n")
                md_parts.append("\n")
                md_parts.append(f"> {mechanism}\n")
                md_parts.append("\n")

            # Feasibility
            feasibility = concept.get('feasibility')
            if feasibility:
                md_parts.append(f"**Feasibility**\n")
                md_parts.append("\n")
                md_parts.append(f"{feasibility}\n")
                md_parts.append("\n")

            if idx < len(preliminary):
                md_parts.append("---\n")
                md_parts.append("\n")
    else:
        md_parts.append("*No preliminary concepts generated*\n")
        md_parts.append("\n")

    return "".join(md_parts)


def format_stage5_to_markdown(stage5_output: Dict[str, Any]) -> str:
    """Format Stage 5 (Opportunity Generation) output as markdown

    Args:
        stage5_output: Stage 5 structured output with opportunities

    Returns:
        Formatted markdown string
    """
    md_parts = []

    # Header
    md_parts.append("# Stage 5: Opportunity Cards\n")
    md_parts.append("*Retail-ready innovation opportunities*\n")
    md_parts.append("\n")

    # Opportunities
    opportunities = stage5_output.get("opportunities", [])
    if opportunities:
        md_parts.append(f"## Generated Opportunities ({len(opportunities)})\n")
        md_parts.append("\n")

        for idx, opp in enumerate(opportunities, start=1):
            # Use markdown field if available, otherwise build from fields
            if 'markdown' in opp:
                md_parts.append(opp['markdown'])
                if idx < len(opportunities):
                    md_parts.append("\n")
                    md_parts.append("---\n")
                    md_parts.append("\n")
            else:
                # Fallback: build from structured fields
                md_parts.append(f"### {idx}. **{opp.get('title', 'Untitled Opportunity')}**\n")
                md_parts.append("\n")

                innovation_type = opp.get('innovation_type', 'Unknown')
                md_parts.append(f"**Type**: `{innovation_type}`\n")
                md_parts.append("\n")

                description = opp.get('description', '')
                if description:
                    md_parts.append(f"#### Description\n")
                    md_parts.append("\n")
                    md_parts.append(f"{description}\n")
                    md_parts.append("\n")

                # Actionability items
                action_items = opp.get('actionability_items', [])
                if action_items:
                    md_parts.append(f"#### Next Steps\n")
                    md_parts.append("\n")
                    for item in action_items:
                        md_parts.append(f"- {item}\n")
                    md_parts.append("\n")

                # Visual description
                visual = opp.get('visual_description')
                if visual:
                    md_parts.append(f"#### Visual\n")
                    md_parts.append("\n")
                    md_parts.append(f"> _{visual}_\n")
                    md_parts.append("\n")

                # Follow-up prompts
                prompts = opp.get('follow_up_prompts', [])
                if prompts:
                    md_parts.append(f"#### Follow-up Questions\n")
                    md_parts.append("\n")
                    for i, prompt in enumerate(prompts, start=1):
                        md_parts.append(f"{i}. {prompt}\n")
                    md_parts.append("\n")

                # Retail metrics
                metrics = opp.get('retail_metrics')
                if metrics:
                    md_parts.append(f"#### Retail Metrics\n")
                    md_parts.append("\n")
                    md_parts.append(f"```\n{metrics}\n```\n")
                    md_parts.append("\n")

                if idx < len(opportunities):
                    md_parts.append("---\n")
                    md_parts.append("\n")
    else:
        md_parts.append("*No opportunities generated*\n")
        md_parts.append("\n")

    return "".join(md_parts)


def format_stage_output(stage_num: int, stage_output: Dict[str, Any]) -> str:
    """Route stage output to appropriate formatter

    Args:
        stage_num: Stage number (1-5)
        stage_output: Structured stage output dictionary

    Returns:
        Formatted markdown string
    """
    formatters = {
        1: format_stage1_to_markdown,
        2: format_stage2_to_markdown,
        3: format_stage3_to_markdown,
        4: format_stage4_to_markdown,
        5: format_stage5_to_markdown,
    }

    formatter = formatters.get(stage_num)
    if formatter:
        return formatter(stage_output)
    else:
        # Fallback to JSON for unknown stages
        import json
        return f"# Stage {stage_num}\n\n```json\n{json.dumps(stage_output, indent=2)}\n```"
