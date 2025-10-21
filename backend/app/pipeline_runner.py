"""Pipeline Background Execution Logic

Handles background execution of the 5-stage innovation pipeline.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from pypdf import PdfReader

from pipeline.stages.stage1_input_processing import Stage1Chain
from pipeline.stages.stage2_signal_amplification import Stage2Chain
from pipeline.stages.stage3_general_translation import Stage3Chain
from pipeline.stages.stage4_brand_contextualization import Stage4Chain
from pipeline.stages.stage5_opportunity_generation import Stage5Chain
from pipeline.utils import load_research_data

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
    """Get output directory for a run."""
    output_dir = Path("/tmp/runs") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def initialize_status(run_id: str) -> None:
    """Initialize status.json with all stages pending."""
    status = {
        "run_id": run_id,
        "status": "running",
        "current_stage": 1,
        "stages": {
            "1": {"status": "pending"},
            "2": {"status": "pending"},
            "3": {"status": "pending"},
            "4": {"status": "pending"},
            "5": {"status": "pending"}
        },
        "error": None
    }

    output_dir = get_output_dir(run_id)
    status_file = output_dir / "status.json"

    with open(status_file, "w") as f:
        json.dump(status, f, indent=2)

    logger.info(f"Initialized status for run {run_id}")


def update_stage_status(
    run_id: str,
    stage_num: int,
    status: str,
    output: Dict[str, Any] = None,
    error: str = None
) -> None:
    """Update status for a specific stage.

    Args:
        run_id: Run identifier
        stage_num: Stage number (1-5)
        status: Stage status ("pending", "running", "complete", "failed")
        output: Stage output data (optional)
        error: Error message (optional)
    """
    output_dir = get_output_dir(run_id)
    status_file = output_dir / "status.json"

    # Read current status
    with open(status_file, "r") as f:
        current_status = json.load(f)

    # Update stage info
    stage_key = str(stage_num)
    stage_info = current_status["stages"][stage_key]

    stage_info["status"] = status

    if status == "running":
        stage_info["started_at"] = datetime.utcnow().isoformat() + "Z"
    elif status in ["complete", "failed"]:
        stage_info["completed_at"] = datetime.utcnow().isoformat() + "Z"

    if output:
        stage_info["output"] = output

    # Update overall status
    current_status["current_stage"] = stage_num

    if status == "failed":
        current_status["status"] = "failed"
        current_status["error"] = error
    elif stage_num == 5 and status == "complete":
        current_status["status"] = "complete"

    # Write updated status
    with open(status_file, "w") as f:
        json.dump(current_status, f, indent=2)

    logger.info(f"Updated stage {stage_num} status to {status} for run {run_id}")


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


def execute_pipeline_background(
    run_id: str,
    pdf_path: str,
    brand_profile: Dict[str, Any]
) -> None:
    """Execute the 5-stage pipeline in background.

    Args:
        run_id: Unique run identifier
        pdf_path: Path to PDF file
        brand_profile: Brand profile data from YAML
    """
    logger.info(f"Starting pipeline execution for run {run_id}")

    try:
        # Initialize status
        initialize_status(run_id)

        # Extract text from PDF
        logger.info(f"[{run_id}] Extracting text from PDF")
        input_text = extract_text_from_pdf(pdf_path)

        # Stage 1: Input Processing
        logger.info(f"[{run_id}] Starting Stage 1: Input Processing")
        update_stage_status(run_id, 1, "running")

        stage1 = Stage1Chain()
        stage1_result = stage1.run(input_text)

        # Save raw output
        save_stage_output(run_id, 1, stage1_result)

        # Transform for API
        stage1_output = transform_stage1_output(stage1_result)
        update_stage_status(run_id, 1, "complete", output=stage1_output)

        # Extract stage1 output text for Stage 2
        stage1_output_text = stage1_result.get("stage1_output", "")

        # Stage 2: Signal Amplification
        logger.info(f"[{run_id}] Starting Stage 2: Signal Amplification")
        update_stage_status(run_id, 2, "running")

        stage2 = Stage2Chain()
        stage2_result = stage2.run(stage1_output_text)

        save_stage_output(run_id, 2, stage2_result)
        update_stage_status(run_id, 2, "complete")

        # Extract stage2 output text for Stage 3
        stage2_output_text = stage2_result.get("stage2_output", "")

        # Stage 3: General Translation
        logger.info(f"[{run_id}] Starting Stage 3: General Translation")
        update_stage_status(run_id, 3, "running")

        stage3 = Stage3Chain()
        stage3_result = stage3.run(stage1_output_text, stage2_output_text)

        save_stage_output(run_id, 3, stage3_result)
        update_stage_status(run_id, 3, "complete")

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
        update_stage_status(run_id, 4, "running")

        stage4 = Stage4Chain()
        stage4_result = stage4.run(stage3_output_text, brand_profile, research_data)

        save_stage_output(run_id, 4, stage4_result)
        update_stage_status(run_id, 4, "complete")

        # Extract stage4 output text for Stage 5
        stage4_output_text = stage4_result.get("stage4_output", "")

        # Stage 5: Opportunity Generation
        logger.info(f"[{run_id}] Starting Stage 5: Opportunity Generation")
        update_stage_status(run_id, 5, "running")

        stage5 = Stage5Chain()
        stage5_result = stage5.run(stage4_output_text, brand_profile)

        save_stage_output(run_id, 5, stage5_result)
        update_stage_status(run_id, 5, "complete")

        logger.info(f"Pipeline execution completed successfully for run {run_id}")

    except Exception as e:
        logger.error(f"Pipeline execution failed for run {run_id}: {str(e)}", exc_info=True)

        # Get current stage from status
        try:
            output_dir = get_output_dir(run_id)
            status_file = output_dir / "status.json"
            with open(status_file, "r") as f:
                current_status = json.load(f)
            current_stage = current_status.get("current_stage", 1)
        except:
            current_stage = 1

        # Mark as failed
        update_stage_status(run_id, current_stage, "failed", error=str(e))

    finally:
        # Cleanup PDF
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                logger.info(f"Cleaned up PDF file: {pdf_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup PDF {pdf_path}: {e}")
