"""Pipeline Background Execution Logic

Handles background execution of the 5-stage innovation pipeline.

Now uses Prisma API client to write status updates to database
instead of file-based status.json management.
"""
import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import requests
from pypdf import PdfReader

from pipeline.stages.stage1_input_processing import Stage1Chain
from pipeline.stages.stage2_signal_amplification import Stage2Chain
from pipeline.stages.stage3_general_translation import Stage3Chain
from pipeline.stages.stage4_brand_contextualization import Stage4Chain
from pipeline.stages.stage5_opportunity_generation import Stage5Chain
from pipeline.utils import load_research_data, send_webhook_sync
from app.prisma_client import PrismaAPIClient
from app.pipeline_errors import (
    PipelineErrorCode,
    create_error_payload,
    classify_error
)
from utils.report_generator import generate_full_report, calculate_report_size

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text content

    Raises:
        Exception: If PDF reading fails (wrapped with PipelineErrorCode context)
    """
    try:
        reader = PdfReader(pdf_path)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text()

        logger.info(f"Extracted {len(text_content)} characters from PDF")
        return text_content

    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        # Re-raise with context so it can be classified as PDF_PARSE_ERROR
        raise Exception(f"PDF parsing failed: {str(e)}") from e


def get_output_dir(run_id: str) -> Path:
    """Get output directory for a run.

    Note: Now only used for saving stage output files locally.
    Status tracking is done via Prisma API.
    """
    output_dir = Path("/tmp/runs") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_stage_output(run_id: str, stage_num: int, output: Any) -> None:
    """Save stage output to JSON file."""
    output_dir = get_output_dir(run_id)
    output_file = output_dir / f"stage_{stage_num}_output.json"

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Saved stage {stage_num} output for run {run_id}")


def transform_stage1_output(stage1_result: Dict[str, Any]) -> Dict[str, str]:
    """Transform Stage 1 output to match API schema.

    Converts pipeline output format to frontend-expected format:
    - inspiration_1_title
    - inspiration_1_content
    - inspiration_2_title
    - inspiration_2_content
    """
    # Extract inspirations from stage1 output
    # Assuming stage1_result has structure like:
    # {"inspirations": [{"title": "...", "content": "..."}, ...]}

    inspirations = stage1_result.get("inspirations", [])

    result = {}

    if len(inspirations) >= 1:
        result["inspiration_1_title"] = inspirations[0].get("title", "")
        result["inspiration_1_content"] = inspirations[0].get("content", "")

    if len(inspirations) >= 2:
        result["inspiration_2_title"] = inspirations[1].get("title", "")
        result["inspiration_2_content"] = inspirations[1].get("content", "")

    return result


def convert_opportunities_to_markdown(opportunities: list) -> list:
    """Convert opportunity dictionaries to include markdown content.

    Args:
        opportunities: List of opportunity dictionaries with structured fields

    Returns:
        List of opportunities with added 'markdown' field containing full content
    """
    opportunities_with_markdown = []

    for idx, opp in enumerate(opportunities, start=1):
        # Extract fields
        title = opp.get('title', f'Opportunity {idx}')
        description = opp.get('description', '')
        actionability_items = opp.get('actionability_items', [])
        visual_description = opp.get('visual_description', '')
        follow_up_prompts = opp.get('follow_up_prompts', [])
        innovation_type = opp.get('innovation_type', 'innovation')

        # Build markdown content
        markdown_parts = []

        # Frontmatter
        markdown_parts.append('---')
        markdown_parts.append(f'opportunity_id: opp-{idx:02d}')
        markdown_parts.append(f'tags: {innovation_type}')
        markdown_parts.append('---')
        markdown_parts.append('')

        # Title
        markdown_parts.append(f'# {title}')
        markdown_parts.append('')

        # Description
        if description:
            markdown_parts.append('## Description')
            markdown_parts.append('')
            markdown_parts.append(description)
            markdown_parts.append('')

        # Actionability
        if actionability_items:
            markdown_parts.append('## Actionability')
            markdown_parts.append('')
            for item in actionability_items:
                markdown_parts.append(f'- {item}')
            markdown_parts.append('')

        # Visual
        if visual_description:
            markdown_parts.append('## Visual')
            markdown_parts.append('')
            markdown_parts.append(f'*{visual_description}*')
            markdown_parts.append('')

        # Follow-up Prompts
        if follow_up_prompts:
            markdown_parts.append('## Follow-up Prompts')
            markdown_parts.append('')
            for i, prompt in enumerate(follow_up_prompts, start=1):
                markdown_parts.append(f'{i}. {prompt}')
            markdown_parts.append('')

        markdown_content = '\n'.join(markdown_parts)

        # Create new opportunity dict with markdown
        opp_with_markdown = {
            **opp,  # Keep all original fields
            'markdown': markdown_content,
            'number': idx  # Add card number for frontend
        }

        opportunities_with_markdown.append(opp_with_markdown)

    return opportunities_with_markdown


def call_completion_webhook(
    run_id: str,
    start_time: float,
    opportunities: list,
    stage1_result: Dict[str, Any],
    stage2_result: Dict[str, Any],
    stage3_result: Dict[str, Any],
    stage4_result: Dict[str, Any],
    stage5_result: Dict[str, Any],
    company_name: str,
    document_name: str
) -> None:
    """Call frontend webhook to notify pipeline completion with retry logic.

    Args:
        run_id: Run identifier
        start_time: Pipeline start timestamp (from time.time())
        opportunities: List of opportunity cards with markdown and all required fields
        stage1_result: Stage 1 output dictionary
        stage2_result: Stage 2 output dictionary
        stage3_result: Stage 3 output dictionary
        stage4_result: Stage 4 output dictionary
        stage5_result: Stage 5 output dictionary
        company_name: Company/brand name for report header
        document_name: Source document name for report header
    """
    frontend_url = os.getenv("FRONTEND_WEBHOOK_URL", "https://innovation-web-rho.vercel.app")
    webhook_secret = os.getenv("WEBHOOK_SECRET", "dev-secret-123")

    # Ensure opportunities have all required fields
    # Field mapping: 'markdown' → 'fullContent' for frontend
    enhanced_opportunities = []
    for opp in opportunities:
        enhanced_opp = {
            "id": opp.get("id", ""),
            "number": opp.get("number", 0),
            "title": opp.get("title", ""),
            "summary": opp.get("description", "")[:200],  # First 200 chars as summary
            "fullContent": opp.get("markdown", ""),  # Rename markdown → fullContent
            "heroImageUrl": opp.get("heroImageUrl"),  # May be None
        }
        enhanced_opportunities.append(enhanced_opp)

    # Generate full report markdown
    full_report_markdown = None
    try:
        report_start = time.time()

        stage_outputs = {
            "stage1": stage1_result,
            "stage2": stage2_result,
            "stage3": stage3_result,
            "stage4": stage4_result
        }

        full_report_markdown = generate_full_report(
            run_id=run_id,
            company_name=company_name,
            document_name=document_name,
            stage_outputs=stage_outputs,
            opportunity_cards=opportunities
        )

        report_duration = time.time() - report_start
        report_size_kb = calculate_report_size(full_report_markdown)

        logger.info(
            f"[{run_id}] Full report generated: {report_size_kb:.2f} KB "
            f"in {report_duration:.2f}s"
        )

        # Validate report size
        if report_size_kb > 100:
            logger.warning(
                f"[{run_id}] Report size ({report_size_kb:.2f} KB) exceeds 100KB limit"
            )

    except Exception as e:
        logger.error(
            f"[{run_id}] Report generation failed: {e}. "
            "Continuing without report.",
            exc_info=True
        )
        # Continue without report - don't block pipeline completion

    # Prepare completion payload
    completion_data = {
        "status": "COMPLETED",
        "completedAt": datetime.utcnow().isoformat() + "Z",
        "duration": int((time.time() - start_time) * 1000),  # milliseconds
        "opportunities": enhanced_opportunities,
        "fullReportMarkdown": full_report_markdown,
        "stageOutputs": {
            "stage1": stage1_result,
            "stage2": stage2_result,
            "stage3": stage3_result,
            "stage4": stage4_result,
            "stage5": stage5_result
        }
    }

    # Retry logic with exponential backoff
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(
                f"[{run_id}] Calling completion webhook (attempt {attempt}/{max_attempts}): "
                f"{frontend_url}/api/pipeline/{run_id}/complete"
            )

            response = requests.post(
                f"{frontend_url}/api/pipeline/{run_id}/complete",
                json=completion_data,
                headers={"X-Webhook-Secret": webhook_secret},
                timeout=30
            )

            if response.ok:
                logger.info(f"[{run_id}] Successfully notified frontend of completion")
                return  # Success, exit function

            logger.warning(
                f"[{run_id}] Webhook attempt {attempt} failed: "
                f"{response.status_code} - {response.text}"
            )

        except requests.exceptions.Timeout:
            logger.warning(f"[{run_id}] Webhook attempt {attempt} timeout after 30s")
        except requests.exceptions.RequestException as e:
            logger.warning(f"[{run_id}] Webhook attempt {attempt} error: {e}")
        except Exception as e:
            logger.warning(f"[{run_id}] Webhook attempt {attempt} unexpected error: {e}")

        # Exponential backoff: 1s, 2s, 4s
        if attempt < max_attempts:
            wait_time = 2 ** (attempt - 1)
            logger.info(f"[{run_id}] Waiting {wait_time}s before retry...")
            time.sleep(wait_time)

    # All attempts failed
    logger.error(
        f"[{run_id}] Failed to notify frontend after {max_attempts} attempts. "
        "Opportunities are saved in database but frontend may not be updated."
    )


def execute_pipeline_background(
    run_id: str,
    pdf_path: str,
    brand_profile: Dict[str, Any]
) -> None:
    """Execute the 5-stage pipeline in background.

    Now uses Prisma API client to write status updates to database.

    Args:
        run_id: Unique run identifier
        pdf_path: Path to PDF file
        brand_profile: Brand profile data from YAML
    """
    logger.info(f"Starting pipeline execution for run {run_id}")
    start_time = time.time()  # Track pipeline duration

    # Initialize Prisma API client
    prisma_client = PrismaAPIClient()
    current_stage = 1  # Track stage for error handling

    try:
        # Initialize pipeline stages in Prisma (stage 1 = PROCESSING)
        prisma_client.initialize_pipeline_stages(run_id)

        # Extract text from PDF
        logger.info(f"[{run_id}] Extracting text from PDF")
        input_text = extract_text_from_pdf(pdf_path)

        # Stage 1: Input Processing
        logger.info(f"[{run_id}] Starting Stage 1: Input Processing")
        current_stage = 1
        # Already marked as PROCESSING in initialize_pipeline_stages

        stage1 = Stage1Chain()
        stage1_result = stage1.run(input_text)

        # Save raw output locally
        save_stage_output(run_id, 1, stage1_result)

        # Flatten Stage 1 output for Prisma (move structured fields to top level)
        stage1_output_for_prisma = stage1_result.get("stage1_output", {})
        if isinstance(stage1_output_for_prisma, dict):
            # If stage1_output is a dict with structured fields, flatten it
            flattened_output = {
                **stage1_output_for_prisma,  # Spread all structured fields to top level
                "input_text": stage1_result.get("input_text", ""),
                "raw_text": stage1_result.get("raw_text", "")
            }
        else:
            # If stage1_output is a string (old format), keep original structure
            flattened_output = stage1_result

        # Mark stage 1 as completed in Prisma with flattened structure
        prisma_client.mark_stage_complete(run_id, 1, flattened_output)

        # Send Stage 1 webhook with output
        webhook_payload = {
            "stageNumber": 1,
            "stageName": "Extraction",
            "status": "COMPLETE",
            "output": {
                "extractedText": flattened_output.get("extractedText", ""),
                "mechanisms": flattened_output.get("mechanisms", [])
            }
        }
        send_webhook_sync(run_id, "stage-update", webhook_payload)

        # Extract stage1 output text for Stage 2
        # Stage 2 needs the raw LLM output, not the structured fields
        # Use raw_text if available (original LLM output), otherwise fall back to stage1_output
        stage1_output_text = stage1_result.get("raw_text")

        if not stage1_output_text:
            # Fallback: if no raw_text, use stage1_output
            stage1_output_for_stage2 = stage1_result.get("stage1_output")
            if isinstance(stage1_output_for_stage2, dict):
                # Convert dict to JSON string as last resort
                import json
                stage1_output_text = json.dumps(stage1_output_for_stage2, indent=2)
            else:
                stage1_output_text = stage1_output_for_stage2 or ""

        # Stage 2: Signal Amplification
        logger.info(f"[{run_id}] Starting Stage 2: Signal Amplification")
        current_stage = 2
        prisma_client.mark_stage_processing(run_id, 2)

        stage2 = Stage2Chain()
        stage2_result = stage2.run(stage1_output_text)

        save_stage_output(run_id, 2, stage2_result)
        prisma_client.mark_stage_complete(run_id, 2, stage2_result)

        # Send Stage 2 webhook with output
        webhook_payload = {
            "stageNumber": 2,
            "stageName": "Signals",
            "status": "COMPLETE",
            "output": {
                "signals": stage2_result.get("signals", [])
            }
        }
        send_webhook_sync(run_id, "stage-update", webhook_payload)

        # Extract stage2 output text for Stage 3
        stage2_output_text = stage2_result.get("stage2_output", "")

        # Stage 3: General Translation
        logger.info(f"[{run_id}] Starting Stage 3: General Translation")
        current_stage = 3
        prisma_client.mark_stage_processing(run_id, 3)

        stage3 = Stage3Chain()
        stage3_result = stage3.run(stage1_output_text, stage2_output_text)

        save_stage_output(run_id, 3, stage3_result)
        prisma_client.mark_stage_complete(run_id, 3, stage3_result)

        # Send Stage 3 webhook with output
        webhook_payload = {
            "stageNumber": 3,
            "stageName": "Insights",
            "status": "COMPLETE",
            "output": {
                "insights": stage3_result.get("insights", [])
            }
        }
        send_webhook_sync(run_id, "stage-update", webhook_payload)

        # Extract stage3 output text for Stage 4
        stage3_output_text = stage3_result.get("stage3_output", "")

        # Load research data for brand (returns empty string if missing)
        # Note: YAML files use 'brand_name' field, convert to filename format
        brand_name = brand_profile.get("brand_name", "Unknown")
        brand_id = brand_name.lower().replace(" ", "-")
        research_data = load_research_data(brand_id)
        if not research_data:
            logger.warning(f"No research data found for brand {brand_id}, using empty string")
            research_data = ""

        # Stage 4: Brand Contextualization
        logger.info(f"[{run_id}] Starting Stage 4: Brand Contextualization")
        current_stage = 4
        prisma_client.mark_stage_processing(run_id, 4)

        stage4 = Stage4Chain()
        stage4_result = stage4.run(stage3_output_text, brand_profile, research_data)

        save_stage_output(run_id, 4, stage4_result)
        prisma_client.mark_stage_complete(run_id, 4, stage4_result)

        # Send Stage 4 webhook with output
        webhook_payload = {
            "stageNumber": 4,
            "stageName": "Ideation",
            "status": "COMPLETE",
            "output": {
                "preliminary": stage4_result.get("preliminary", [])
            }
        }
        send_webhook_sync(run_id, "stage-update", webhook_payload)

        # Extract stage4 output text for Stage 5
        stage4_output_text = stage4_result.get("stage4_output", "")

        # Extract brand name and input source for Stage 5
        brand_name = brand_profile.get("company_name", "Unknown Brand")
        input_source = Path(pdf_path).stem  # Get filename without extension

        # Stage 5: Opportunity Generation
        logger.info(f"[{run_id}] Starting Stage 5: Opportunity Generation")
        current_stage = 5
        prisma_client.mark_stage_processing(run_id, 5)

        stage5 = Stage5Chain()
        stage5_result = stage5.run(stage4_output_text, brand_name, input_source)

        save_stage_output(run_id, 5, stage5_result)

        # Extract opportunities and convert to markdown format for frontend
        raw_opportunities = stage5_result.get("opportunities", [])
        opportunities_with_markdown = convert_opportunities_to_markdown(raw_opportunities)
        opportunities_output = {"opportunities": opportunities_with_markdown}

        # Mark stage 5 as completed (auto-marks PipelineRun as COMPLETED)
        # Save opportunities_output (with markdown) instead of stage5_result
        prisma_client.mark_stage_complete(run_id, 5, opportunities_output)

        logger.info(f"Pipeline execution completed successfully for run {run_id}")

        # Call completion webhook to notify frontend
        call_completion_webhook(
            run_id=run_id,
            start_time=start_time,
            opportunities=opportunities_with_markdown,
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            stage3_result=stage3_result,
            stage4_result=stage4_result,
            stage5_result=stage5_result,
            company_name=brand_name,
            document_name=input_source
        )

    except Exception as e:
        logger.error(f"Pipeline execution failed for run {run_id}: {str(e)}", exc_info=True)

        # Classify error and create standardized error payload
        error_code = classify_error(e, current_stage)
        error_payload = create_error_payload(
            run_id=run_id,
            stage=current_stage,
            error_code=error_code,
            error_message=str(e),
            exception=e
        )

        # Log standardized error
        logger.error(f"[{run_id}] Error classified as {error_code.value}: {error_payload}")

        # Mark current stage as failed in Prisma with detailed error info
        import json
        prisma_client.mark_stage_failed(
            run_id,
            current_stage,
            json.dumps(error_payload["error"], indent=2)
        )

    finally:
        # Cleanup PDF
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                logger.info(f"Cleaned up PDF file: {pdf_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup PDF {pdf_path}: {e}")
