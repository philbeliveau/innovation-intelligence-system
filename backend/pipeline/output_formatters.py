"""Output Formatters for Pipeline Stages

Converts structured JSON outputs from each stage into human-readable markdown
for Gradio UI display.
"""

from typing import Dict, Any, List
from datetime import datetime


def format_stage0_to_markdown(stage0_output: Dict[str, Any]) -> str:
    """Format Stage 0 (Brand Context) output as markdown

    Args:
        stage0_output: Stage 0 structured output with brand profile data

    Returns:
        Formatted markdown string
    """
    md_parts = []

    # Header
    md_parts.append("# Stage 0: Brand Context\n")
    md_parts.append("*Brand profile and market positioning*\n")
    md_parts.append("\n")

    # Company Overview
    company_name = stage0_output.get("company_name", "Unknown Brand")
    industry = stage0_output.get("industry", "Not specified")
    geography = stage0_output.get("geography", "Not specified")

    md_parts.append("## Company Overview\n")
    md_parts.append("\n")
    md_parts.append(f"**Brand Name**: {company_name}\n")
    md_parts.append(f"**Industry**: {industry}\n")
    md_parts.append(f"**Geography**: {geography}\n")
    md_parts.append("\n")

    # Product Portfolio
    portfolio = stage0_output.get("product_portfolio", "")
    if portfolio:
        md_parts.append("## Product Portfolio\n")
        md_parts.append("\n")
        md_parts.append(f"{portfolio}\n")
        md_parts.append("\n")

    # Positioning (optional)
    positioning = stage0_output.get("positioning", "")
    if positioning:
        md_parts.append("## Brand Positioning\n")
        md_parts.append("\n")
        md_parts.append(f"{positioning}\n")
        md_parts.append("\n")

    # Target Customers (optional)
    target_customers = stage0_output.get("target_customers", "")
    if target_customers:
        md_parts.append("## Target Customers\n")
        md_parts.append("\n")
        md_parts.append(f"{target_customers}\n")
        md_parts.append("\n")

    # Recent Innovations (optional)
    recent_innovations = stage0_output.get("recent_innovations", "")
    if recent_innovations:
        md_parts.append("## Recent Innovations\n")
        md_parts.append("\n")
        md_parts.append(f"{recent_innovations}\n")
        md_parts.append("\n")

    return "".join(md_parts)


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
            # Use markdown field if available AND it's a string
            if 'markdown' in opp and isinstance(opp['markdown'], str):
                # Valid markdown field exists
                md_parts.append(opp['markdown'])
                if idx < len(opportunities):
                    md_parts.append("\n")
                    md_parts.append("---\n")
                    md_parts.append("\n")
            else:
                # Fallback: build from structured fields (or markdown was not a string)
                if 'markdown' in opp and not isinstance(opp['markdown'], str):
                    import logging
                    logging.warning(f"Stage 5 opportunity {idx} markdown field is not a string (type={type(opp['markdown'])})")
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


def format_stage6_to_markdown(stage6_output: Dict[str, Any]) -> str:
    """Format Stage 6 (Executive Summary) output as markdown

    Args:
        stage6_output: Stage 6 structured output with scorecard and summary

    Returns:
        Formatted markdown string
    """
    md_parts = []

    # Header
    title = stage6_output.get("title", "Innovation Intelligence Report")
    generated_at = stage6_output.get("generated_at", "")

    md_parts.append(f"# {title}\n")
    md_parts.append(f"*Generated: {generated_at}*\n")
    md_parts.append("\n")

    # Scorecard
    scorecard = stage6_output.get("scorecard", {})
    if scorecard:
        md_parts.append("## Pipeline Scorecard\n")
        md_parts.append("\n")

        brand_name = scorecard.get("brand_name", "Unknown Brand")
        md_parts.append(f"**Brand**: {brand_name}\n")
        md_parts.append("\n")

        # Pipeline Stats
        stats = scorecard.get("pipeline_stats", {})
        if stats:
            md_parts.append("### Pipeline Metrics\n")
            md_parts.append("\n")
            md_parts.append(f"- **Mechanisms Extracted**: {stats.get('mechanisms_extracted', 0)}\n")
            md_parts.append(f"- **Signals Identified**: {stats.get('signals_identified', 0)}\n")
            md_parts.append(f"- **Insights Generated**: {stats.get('insights_generated', 0)}\n")
            md_parts.append(f"- **Preliminary Concepts**: {stats.get('preliminary_concepts', 0)}\n")
            md_parts.append(f"- **Final Opportunities**: {stats.get('final_opportunities', 0)}\n")
            md_parts.append("\n")

        # Top Opportunities
        top_opps = scorecard.get("top_opportunities", [])
        if top_opps:
            md_parts.append("### Top Opportunities\n")
            md_parts.append("\n")

            for opp in top_opps:
                rank = opp.get("rank", 0)
                title = opp.get("title", "Untitled")
                opp_type = opp.get("type", "Unknown")
                summary = opp.get("summary", "")

                md_parts.append(f"#### {rank}. {title}\n")
                md_parts.append(f"**Type**: {opp_type}\n")
                md_parts.append(f"\n{summary}\n")
                md_parts.append("\n")

    # Methodology
    methodology = stage6_output.get("methodology", {})
    if methodology:
        md_parts.append("## Methodology\n")
        md_parts.append("\n")
        md_parts.append("This report was generated using a 7-stage innovation intelligence pipeline:\n")
        md_parts.append("\n")

        for stage_key, stage_desc in methodology.items():
            stage_num = stage_key.replace("stage_", "")
            md_parts.append(f"- **Stage {stage_num}**: {stage_desc}\n")
        md_parts.append("\n")

    # Next Steps
    next_steps = stage6_output.get("next_steps", [])
    if next_steps:
        md_parts.append("## Recommended Next Steps\n")
        md_parts.append("\n")

        for idx, step in enumerate(next_steps, start=1):
            md_parts.append(f"{idx}. {step}\n")
        md_parts.append("\n")

    return "".join(md_parts)


def format_stage_output(stage_num: int, stage_output: Dict[str, Any]) -> str:
    """Route stage output to appropriate formatter

    Args:
        stage_num: Stage number (0-6)
        stage_output: Structured stage output dictionary or string

    Returns:
        Formatted markdown string
    """
    import json

    # Handle string outputs (fallback for stages returning text instead of dicts)
    if isinstance(stage_output, str):
        return f"# Stage {stage_num}\n\n{stage_output}"

    formatters = {
        0: format_stage0_to_markdown,
        1: format_stage1_to_markdown,
        2: format_stage2_to_markdown,
        3: format_stage3_to_markdown,
        4: format_stage4_to_markdown,
        5: format_stage5_to_markdown,
        6: format_stage6_to_markdown,
    }

    formatter = formatters.get(stage_num)
    if formatter:
        return formatter(stage_output)
    else:
        # Fallback to JSON for unknown stages
        return f"# Stage {stage_num}\n\n```json\n{json.dumps(stage_output, indent=2)}\n```"
