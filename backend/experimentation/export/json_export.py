"""JSON export functionality for experiment data.

Exports complete experiment data including all JSONB fields in unmodified format.
Supports single or bulk export with filtering by date range and quality tag.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


async def export_to_json(
    prisma_client: Any,
    output_path: str,
    quality_tag: Optional[str] = None,
    brand_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pipeline_version: Optional[str] = None
) -> str:
    """Export experiments to JSON file.

    Args:
        prisma_client: PrismaAPIClient instance
        output_path: Path to output JSON file
        quality_tag: Optional quality filter ("good", "needs_work", "failed")
        brand_name: Optional brand name filter
        start_date: Optional date range start (ISO format)
        end_date: Optional date range end (ISO format)
        pipeline_version: Optional pipeline version filter

    Returns:
        Path to exported file

    Raises:
        ValueError: If no experiments found with given filters
        IOError: If file write fails
    """
    logger.info(
        f"Exporting experiments to JSON: {output_path} "
        f"(filters: quality={quality_tag}, brand={brand_name}, "
        f"start={start_date}, end={end_date}, version={pipeline_version})"
    )

    # Retrieve experiments with filters
    result = prisma_client.get_experiments(
        quality_tag=quality_tag,
        brand_name=brand_name,
        start_date=start_date,
        end_date=end_date,
        pipeline_version=pipeline_version,
        page=1,
        page_size=1000  # Large limit for bulk export
    )

    if not result or not result.get("experiments"):
        raise ValueError("No experiments found with given filters")

    experiments = result["experiments"]
    pagination = result.get("pagination", {})

    # Build export data structure
    export_data = {
        "export_metadata": {
            "export_date": datetime.now().isoformat(),
            "total_experiments": len(experiments),
            "filters_applied": {
                "quality_tag": quality_tag,
                "brand_name": brand_name,
                "start_date": start_date,
                "end_date": end_date,
                "pipeline_version": pipeline_version
            },
            "pagination": pagination
        },
        "experiments": _serialize_experiments(experiments)
    }

    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Successfully exported {len(experiments)} experiments to {output_path}"
        )
        return str(output_file)

    except Exception as e:
        logger.error(f"Failed to write JSON export: {e}")
        raise IOError(f"Failed to write JSON export: {e}")


def _serialize_experiments(experiments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert experiment records to JSON-serializable format.

    Args:
        experiments: List of experiment records from API

    Returns:
        List of serialized experiment dicts
    """
    serialized = []

    for exp in experiments:
        serialized_exp = {
            "run_id": exp.get("runId"),
            "timestamp": exp.get("timestamp"),
            "report_name": exp.get("reportName"),
            "report_text": exp.get("reportText"),
            "brand_profile": exp.get("brandProfile", {}),
            "stage_outputs": exp.get("stageOutputs", {}),
            "quality_tag": exp.get("qualityTag"),
            "experiment_notes": exp.get("experimentNotes"),
            "pipeline_version": exp.get("pipelineVersion"),
            "execution_time_seconds": exp.get("executionTimeSeconds"),
            "token_usage": exp.get("tokenUsage"),
            "cost_usd": float(exp.get("costUsd")) if exp.get("costUsd") else None,
            "created_at": exp.get("createdAt"),
            "updated_at": exp.get("updatedAt")
        }
        serialized.append(serialized_exp)

    return serialized


def export_single_experiment(
    experiment: Dict[str, Any],
    output_path: str
) -> str:
    """Export a single experiment to JSON file.

    Args:
        experiment: Single experiment record
        output_path: Path to output JSON file

    Returns:
        Path to exported file
    """
    logger.info(f"Exporting single experiment {experiment.get('runId')} to {output_path}")

    export_data = {
        "export_metadata": {
            "export_date": datetime.now().isoformat(),
            "total_experiments": 1,
            "experiment_run_id": experiment.get("runId")
        },
        "experiment": _serialize_experiments([experiment])[0]
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Successfully exported experiment to {output_path}")
    return str(output_file)
