"""PDF Export Module

Converts markdown stage outputs into beautifully formatted PDF documents.
Uses markdown2 for markdown parsing and WeasyPrint for PDF generation.
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import tempfile

# Import PDF generation libraries
try:
    import markdown2
    from weasyprint import HTML, CSS
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF export libraries not available. Install with: pip install markdown2 weasyprint")


logger = logging.getLogger(__name__)


# CSS styling for beautiful PDFs
PDF_STYLES = """
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #2c3e50;
    font-size: 24pt;
    border-bottom: 3px solid #3498db;
    padding-bottom: 10px;
    margin-top: 20px;
}

h2 {
    color: #34495e;
    font-size: 18pt;
    margin-top: 18px;
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 6px;
}

h3 {
    color: #555;
    font-size: 14pt;
    margin-top: 14px;
}

h4 {
    color: #666;
    font-size: 12pt;
    margin-top: 12px;
}

code {
    background-color: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 10pt;
}

pre {
    background-color: #f8f8f8;
    padding: 15px;
    border-left: 4px solid #3498db;
    overflow-x: auto;
    border-radius: 4px;
}

pre code {
    background-color: transparent;
    padding: 0;
}

blockquote {
    border-left: 4px solid #95a5a6;
    padding-left: 15px;
    margin-left: 0;
    font-style: italic;
    color: #555;
}

ul, ol {
    margin-left: 20px;
}

li {
    margin-bottom: 6px;
}

strong {
    color: #2c3e50;
}

em {
    color: #7f8c8d;
}

hr {
    border: none;
    border-top: 2px solid #ecf0f1;
    margin: 20px 0;
}

/* Footer */
@page {
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #7f8c8d;
    }
}
"""


def generate_stage_pdf(
    stage_num: int,
    markdown_content: str,
    output_path: Optional[Path] = None,
    brand_name: str = "Unknown Brand"
) -> Path:
    """Generate PDF from markdown content for a specific stage.

    Args:
        stage_num: Stage number (0-6)
        markdown_content: Markdown-formatted stage output
        output_path: Optional output path (defaults to temp file)
        brand_name: Brand name for PDF header

    Returns:
        Path to generated PDF file

    Raises:
        ImportError: If PDF generation libraries not installed
        Exception: If PDF generation fails
    """
    if not PDF_AVAILABLE:
        raise ImportError(
            "PDF export libraries not available. "
            "Install with: pip install markdown2 weasyprint"
        )

    logger.info(f"Generating PDF for Stage {stage_num}")

    try:
        # CRITICAL: Ensure markdown_content is a string, not dict/JSON
        if not isinstance(markdown_content, str):
            logger.error(f"markdown_content is not a string (type={type(markdown_content)})")
            # Convert to JSON string as fallback
            import json
            markdown_content = f"```json\n{json.dumps(markdown_content, indent=2)}\n```"

        # Convert markdown to HTML
        html_content = markdown2.markdown(
            markdown_content,
            extras=["fenced-code-blocks", "tables", "break-on-newline"]
        )

        # Add header and metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stage_names = {
            0: "Brand Context",
            1: "Extraction",
            2: "Signals",
            3: "Insights",
            4: "Ideation",
            5: "Opportunity Cards",
            6: "Executive Summary"
        }
        stage_name = stage_names.get(stage_num, f"Stage {stage_num}")

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{brand_name} - {stage_name}</title>
        </head>
        <body>
            <div style="text-align: center; margin-bottom: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                <h1 style="margin: 0; color: #2c3e50;">{brand_name}</h1>
                <p style="margin: 5px 0; color: #7f8c8d; font-size: 14pt;">Stage {stage_num}: {stage_name}</p>
                <p style="margin: 5px 0; color: #95a5a6; font-size: 10pt;">Generated: {timestamp}</p>
            </div>
            {html_content}
        </body>
        </html>
        """

        # Determine output path
        if output_path is None:
            # Create temp file
            temp_dir = Path(tempfile.gettempdir()) / "innovation-pdfs"
            temp_dir.mkdir(exist_ok=True)
            output_path = temp_dir / f"stage_{stage_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate PDF
        html = HTML(string=full_html)
        css = CSS(string=PDF_STYLES)
        html.write_pdf(output_path, stylesheets=[css])

        logger.info(f"PDF generated successfully: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"PDF generation failed for Stage {stage_num}: {e}", exc_info=True)
        raise


def generate_all_stages_pdf(
    stage_markdowns: dict,
    output_path: Optional[Path] = None,
    brand_name: str = "Unknown Brand"
) -> Path:
    """Generate combined PDF with all pipeline stages.

    Args:
        stage_markdowns: Dict mapping stage numbers to markdown content
        output_path: Optional output path (defaults to temp file)
        brand_name: Brand name for PDF header

    Returns:
        Path to generated PDF file

    Raises:
        ImportError: If PDF generation libraries not installed
        Exception: If PDF generation fails
    """
    if not PDF_AVAILABLE:
        raise ImportError(
            "PDF export libraries not available. "
            "Install with: pip install markdown2 weasyprint"
        )

    logger.info("Generating combined PDF for all stages")

    try:
        # Combine all stages into single markdown
        combined_markdown = []

        for stage_num in sorted(stage_markdowns.keys()):
            markdown_content = stage_markdowns[stage_num]
            if markdown_content:
                # CRITICAL: Ensure markdown is a string, not dict
                if not isinstance(markdown_content, str):
                    logger.error(f"Stage {stage_num} markdown is not a string (type={type(markdown_content)})")
                    import json
                    markdown_content = f"```json\n{json.dumps(markdown_content, indent=2)}\n```"

                combined_markdown.append(markdown_content)
                combined_markdown.append("\n\n---\n\n")  # Page break separator

        full_markdown = "\n".join(combined_markdown)

        # Convert to HTML
        html_content = markdown2.markdown(
            full_markdown,
            extras=["fenced-code-blocks", "tables", "break-on-newline"]
        )

        # Add cover page
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{brand_name} - Innovation Intelligence Report</title>
        </head>
        <body>
            <div style="text-align: center; margin: 100px 0; padding: 40px;">
                <h1 style="font-size: 36pt; color: #2c3e50; margin-bottom: 20px;">{brand_name}</h1>
                <h2 style="font-size: 24pt; color: #3498db; margin-bottom: 30px;">Innovation Intelligence Report</h2>
                <p style="font-size: 14pt; color: #7f8c8d;">Complete Pipeline Analysis</p>
                <p style="font-size: 12pt; color: #95a5a6; margin-top: 50px;">Generated: {timestamp}</p>
            </div>
            <div style="page-break-after: always;"></div>
            {html_content}
        </body>
        </html>
        """

        # Determine output path
        if output_path is None:
            temp_dir = Path(tempfile.gettempdir()) / "innovation-pdfs"
            temp_dir.mkdir(exist_ok=True)
            output_path = temp_dir / f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate PDF
        html = HTML(string=full_html)
        css = CSS(string=PDF_STYLES)
        html.write_pdf(output_path, stylesheets=[css])

        logger.info(f"Combined PDF generated successfully: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Combined PDF generation failed: {e}", exc_info=True)
        raise
