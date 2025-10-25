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
from pipeline.utils import load_research_data
from app.prisma_client import PrismaAPIClient

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text content

    Raises:
        Exception: If PDF reading fails
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
        raise


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
    stage5_result: Dict[str, Any]
) -> None:
    """Call frontend webhook to notify pipeline completion.

    Args:
        run_id: Run identifier
        start_time: Pipeline start timestamp (from time.time())
        opportunities: List of opportunity cards with markdown
        stage1_result: Stage 1 output dictionary
        stage2_result: Stage 2 output dictionary
        stage3_result: Stage 3 output dictionary
        stage4_result: Stage 4 output dictionary
        stage5_result: Stage 5 output dictionary
    """
    frontend_url = os.getenv("FRONTEND_WEBHOOK_URL", "https://innovation-web-rho.vercel.app")
    webhook_secret = os.getenv("WEBHOOK_SECRET", "dev-secret-123")

    # Prepare completion payload
    completion_data = {
        "status": "COMPLETED",
        "completedAt": datetime.utcnow().isoformat() + "Z",
        "duration": int((time.time() - start_time) * 1000),  # milliseconds
        "opportunities": opportunities,
        "stageOutputs": {
            "stage1": stage1_result,
            "stage2": stage2_result,
            "stage3": stage3_result,
            "stage4": stage4_result,
            "stage5": stage5_result
        }
    }

    try:
        logger.info(f"[{run_id}] Calling completion webhook: {frontend_url}/api/pipeline/{run_id}/complete")

        response = requests.post(
            f"{frontend_url}/api/pipeline/{run_id}/complete",
            json=completion_data,
            headers={"X-Webhook-Secret": webhook_secret},
            timeout=30
        )

        if response.ok:
            logger.info(f"[{run_id}] Successfully notified frontend of completion")
        else:
            logger.error(
                f"[{run_id}] Webhook failed: {response.status_code} - {response.text}"
            )

    except requests.exceptions.Timeout:
        logger.error(f"[{run_id}] Webhook timeout after 30s")
    except requests.exceptions.RequestException as e:
        logger.error(f"[{run_id}] Failed to call completion webhook: {e}")
    except Exception as e:
        logger.error(f"[{run_id}] Unexpected error calling webhook: {e}")


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

        # Mark stage 1 as completed in Prisma
        prisma_client.mark_stage_complete(run_id, 1, stage1_result)

        # Extract stage1 output text for Stage 2
        stage1_output_text = stage1_result.get("stage1_output", "")

        # Stage 2: Signal Amplification
        logger.info(f"[{run_id}] Starting Stage 2: Signal Amplification")
        current_stage = 2
        prisma_client.mark_stage_processing(run_id, 2)

        stage2 = Stage2Chain()
        stage2_result = stage2.run(stage1_output_text)

        save_stage_output(run_id, 2, stage2_result)
        prisma_client.mark_stage_complete(run_id, 2, stage2_result)

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

        # Extract stage3 output text for Stage 4
        stage3_output_text = stage3_result.get("stage3_output", "")

        # Load research data for brand (returns empty string if missing)
        brand_id = brand_profile.get("brand_id", "unknown")
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
        prisma_client.mark_stage_complete(run_id, 5, stage5_result)

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
            stage5_result=stage5_result
        )

    except Exception as e:
        logger.error(f"Pipeline execution failed for run {run_id}: {str(e)}", exc_info=True)

        # Mark current stage as failed in Prisma (auto-marks PipelineRun as FAILED)
        prisma_client.mark_stage_failed(run_id, current_stage, str(e))

    finally:
        # Cleanup PDF
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                logger.info(f"Cleaned up PDF file: {pdf_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup PDF {pdf_path}: {e}")
