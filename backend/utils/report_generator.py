"""
Full Report Generator for Innovation Intelligence System

Generates comprehensive markdown reports combining all 5 pipeline stage outputs.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def generate_full_report(
    run_id: str,
    company_name: str,
    document_name: str,
    stage_outputs: Dict[str, Any],
    opportunity_cards: List[Dict[str, Any]]
) -> str:
    """
    Generate comprehensive markdown report from all pipeline stages

    Args:
        run_id: Pipeline run identifier
        company_name: Company name from brand profile
        document_name: Source document name
        stage_outputs: Dict with keys stage1-stage4 containing stage outputs
        opportunity_cards: List of opportunity card objects

    Returns:
        Formatted markdown report string

    Raises:
        ValueError: If required data is missing
    """
    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        # Extract stage data with safe defaults
        stage1 = stage_outputs.get('stage1', {})
        stage2 = stage_outputs.get('stage2', {})
        stage3 = stage_outputs.get('stage3', {})

        extracted_text = stage1.get('extractedText', '')
        mechanisms = stage1.get('mechanisms', [])
        signals = stage2.get('signals', [])
        insights = stage3.get('insights', [])

        # Truncate extracted text for summary
        truncated_text = truncate_text(extracted_text, max_words=500)

        # Build report sections
        report = _build_header(company_name, document_name, timestamp, run_id)
        report += _build_toc()
        report += _build_summary(
            truncated_text,
            len(mechanisms),
            len(signals),
            len(insights),
            len(opportunity_cards)
        )
        report += _build_mechanisms_section(mechanisms)
        report += _build_signals_section(signals)
        report += _build_insights_section(insights)
        report += _build_opportunity_cards_section(opportunity_cards)
        report += _build_footer()

        return report

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise


def _build_header(company_name: str, document_name: str, timestamp: str, run_id: str) -> str:
    """Build report header with metadata"""
    return f"""# Innovation Intelligence Report

**Company:** {sanitize_markdown(company_name)}
**Document:** {sanitize_markdown(document_name)}
**Generated:** {timestamp}
**Run ID:** {run_id}

---

"""


def _build_toc() -> str:
    """Build table of contents"""
    return """## Table of Contents
1. [Document Analysis Summary](#document-analysis-summary)
2. [Key Mechanisms](#key-mechanisms)
3. [Innovation Signals](#innovation-signals)
4. [Transferable Insights](#transferable-insights)
5. [Opportunity Cards](#opportunity-cards)

---

"""


def _build_summary(
    truncated_text: str,
    mechanism_count: int,
    signal_count: int,
    insight_count: int,
    card_count: int
) -> str:
    """Build document analysis summary section"""
    return f"""## Document Analysis Summary

{sanitize_markdown(truncated_text)}

**Total Mechanisms Identified:** {mechanism_count}
**Total Signals Detected:** {signal_count}
**Total Insights Generated:** {insight_count}
**Total Opportunity Cards:** {card_count}

---

"""


def _build_mechanisms_section(mechanisms: List[Dict[str, Any]]) -> str:
    """Build key mechanisms section"""
    section = "## Key Mechanisms\n\n"

    if not mechanisms:
        section += "_No mechanisms identified_\n\n---\n\n"
        return section

    for i, mech in enumerate(mechanisms, 1):
        title = mech.get('title', 'Untitled')
        description = mech.get('description', 'No description')
        context = mech.get('context', 'No context provided')

        section += f"""### Mechanism {i}: {sanitize_markdown(title)}

**Description:** {sanitize_markdown(description)}

**Context:** {sanitize_markdown(context)}

---

"""

    return section


def _build_signals_section(signals: List[Dict[str, Any]]) -> str:
    """Build innovation signals section"""
    section = "## Innovation Signals\n\n"

    if not signals:
        section += "_No signals detected_\n\n---\n\n"
        return section

    for i, signal in enumerate(signals, 1):
        category = signal.get('category', 'Uncategorized')
        description = signal.get('description', 'No description')
        relevance = signal.get('relevance', 'Not specified')
        mechanism_source = signal.get('mechanismSource', 'N/A')

        section += f"""### Signal {i}: {sanitize_markdown(category)} - {sanitize_markdown(description)}

**Relevance:** {sanitize_markdown(relevance)}

**Source Mechanism:** {mechanism_source}

---

"""

    return section


def _build_insights_section(insights: List[Dict[str, Any]]) -> str:
    """Build transferable insights section"""
    section = "## Transferable Insights\n\n"

    if not insights:
        section += "_No insights generated_\n\n---\n\n"
        return section

    for i, insight in enumerate(insights, 1):
        title = insight.get('title', 'Untitled')
        description = insight.get('description', 'No description')
        transferability = insight.get('transferability', 'Unknown')
        sources = ', '.join(insight.get('signalSources', []))

        section += f"""### Insight {i}: {sanitize_markdown(title)}

**Description:** {sanitize_markdown(description)}

**Transferability:** {transferability}

**Source Signals:** {sources if sources else 'None specified'}

---

"""

    return section


def _build_opportunity_cards_section(opportunity_cards: List[Dict[str, Any]]) -> str:
    """Build opportunity cards section

    Note: Content is NOT sanitized because it's already formatted markdown
    from the opportunity generation stage.
    """
    section = "## Opportunity Cards\n\n"

    if not opportunity_cards:
        section += "_No opportunity cards created_\n\n---\n\n"
        return section

    for i, card in enumerate(opportunity_cards, 1):
        title = card.get('title', 'Untitled')
        # Get content/markdown - already formatted, don't sanitize
        content = card.get('content', card.get('markdown', 'No content'))

        section += f"""### Opportunity {i}: {sanitize_markdown(title)}

{content}

---

"""

    return section


def _build_footer() -> str:
    """Build report footer"""
    return "\n*Report generated by Innovation Intelligence System*\n"


def sanitize_markdown(text: str) -> str:
    """
    Sanitize text for safe markdown rendering
    Escapes special characters that could break formatting

    Args:
        text: Raw text to sanitize

    Returns:
        Sanitized text safe for markdown
    """
    if not text:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # Escape special markdown characters
    replacements = {
        '\\': '\\\\',
        '`': '\\`',
        '*': '\\*',
        '_': '\\_',
        '[': '\\[',
        ']': '\\]',
        '(': '\\(',
        ')': '\\)',
        '#': '\\#',
        '+': '\\+',
        '-': '\\-',
        '.': '\\.',
        '!': '\\!',
        '|': '\\|',
    }

    for char, escaped in replacements.items():
        text = text.replace(char, escaped)

    return text


def truncate_text(text: str, max_words: int = 500) -> str:
    """
    Truncate text to maximum word count

    Args:
        text: Text to truncate
        max_words: Maximum number of words to keep

    Returns:
        Truncated text with word count indicator
    """
    if not text:
        return ""

    words = text.split()
    if len(words) <= max_words:
        return text

    truncated = ' '.join(words[:max_words])
    return truncated + f"... (truncated, {len(words)} total words)"


def calculate_report_size(report: str) -> float:
    """
    Calculate report size in KB

    Args:
        report: Markdown report string

    Returns:
        Report size in kilobytes
    """
    return len(report.encode('utf-8')) / 1024
