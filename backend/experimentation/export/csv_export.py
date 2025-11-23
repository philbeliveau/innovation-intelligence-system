"""CSV export functionality for experiment data.

Exports experiments in flattened CSV format suitable for spreadsheet analysis.
JSONB fields are either flattened to key columns or stored as JSON strings.
"""

import csv
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


async def export_to_csv(
    prisma_client: Any,
    output_path: str,
    quality_tag: Optional[str] = None,
    brand_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pipeline_version: Optional[str] = None,
    include_full_outputs: bool = False
) -> str:
    """Export experiments to CSV file with flattened structure.

    Args:
        prisma_client: PrismaAPIClient instance
        output_path: Path to output CSV file
        quality_tag: Optional quality filter ("good", "needs_work", "failed")
        brand_name: Optional brand name filter
        start_date: Optional date range start (ISO format)
        end_date: Optional date range end (ISO format)
        pipeline_version: Optional pipeline version filter
        include_full_outputs: If True, include full stage_outputs as JSON string

    Returns:
        Path to exported file

    Raises:
        ValueError: If no experiments found with given filters
        IOError: If file write fails
    """
    logger.info(
        f"Exporting experiments to CSV: {output_path} "
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

    # Define CSV columns (flattened structure)
    fieldnames = _get_csv_fieldnames(include_full_outputs)

    # Create output directory if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for exp in experiments:
                row = _flatten_experiment_to_row(exp, include_full_outputs)
                writer.writerow(row)

        logger.info(
            f"Successfully exported {len(experiments)} experiments to {output_path}"
        )
        return str(output_file)

    except Exception as e:
        logger.error(f"Failed to write CSV export: {e}")
        raise IOError(f"Failed to write CSV export: {e}")


def _get_csv_fieldnames(include_full_outputs: bool) -> List[str]:
    """Get CSV column headers.

    Args:
        include_full_outputs: If True, include stage_outputs_json column

    Returns:
        List of column names
    """
    base_fields = [
        'run_id',
        'timestamp',
        'brand_name',
        'industry',
        'country',
        'product_portfolio_count',
        'quality_tag',
        'execution_time_seconds',
        'total_input_tokens',
        'total_output_tokens',
        'total_tokens',
        'cost_usd',
        'pipeline_version',
        'report_name',
        'notes',
        'created_at',
        'updated_at'
    ]

    if include_full_outputs:
        base_fields.append('stage_outputs_json')

    return base_fields


def _flatten_experiment_to_row(
    exp: Dict[str, Any],
    include_full_outputs: bool
) -> Dict[str, Any]:
    """Flatten experiment record to CSV row.

    Args:
        exp: Experiment record from API
        include_full_outputs: If True, include full stage_outputs as JSON

    Returns:
        Flattened dict suitable for CSV row
    """
    # Extract brand profile fields
    brand_profile = exp.get("brandProfile", {})
    brand_name = brand_profile.get("brand_name", "")
    industry = brand_profile.get("industry", "")
    country = brand_profile.get("country", "")
    product_portfolio = brand_profile.get("product_portfolio", [])
    product_count = len(product_portfolio) if isinstance(product_portfolio, list) else 0

    # Extract token usage
    token_usage = exp.get("tokenUsage", {})
    total_input = token_usage.get("total_input_tokens", 0) if token_usage else 0
    total_output = token_usage.get("total_output_tokens", 0) if token_usage else 0
    total_tokens = total_input + total_output

    # Build base row
    row = {
        'run_id': exp.get("runId", ""),
        'timestamp': exp.get("timestamp", ""),
        'brand_name': brand_name,
        'industry': industry,
        'country': country,
        'product_portfolio_count': product_count,
        'quality_tag': exp.get("qualityTag", ""),
        'execution_time_seconds': exp.get("executionTimeSeconds", 0) or 0,
        'total_input_tokens': total_input,
        'total_output_tokens': total_output,
        'total_tokens': total_tokens,
        'cost_usd': float(exp.get("costUsd")) if exp.get("costUsd") else 0.0,
        'pipeline_version': exp.get("pipelineVersion", ""),
        'report_name': exp.get("reportName", ""),
        'notes': exp.get("experimentNotes", ""),
        'created_at': exp.get("createdAt", ""),
        'updated_at': exp.get("updatedAt", "")
    }

    # Optionally include full stage outputs
    if include_full_outputs:
        stage_outputs = exp.get("stageOutputs", {})
        row['stage_outputs_json'] = json.dumps(stage_outputs, ensure_ascii=False)

    return row


def export_experiments_summary(
    prisma_client: Any,
    output_path: str
) -> str:
    """Export summary statistics of all experiments to CSV.

    Creates a high-level summary with aggregated metrics by brand, quality, etc.

    Args:
        prisma_client: PrismaAPIClient instance
        output_path: Path to output CSV file

    Returns:
        Path to exported file
    """
    logger.info(f"Exporting experiments summary to {output_path}")

    # Get all experiments
    result = prisma_client.get_experiments(page=1, page_size=1000)

    if not result or not result.get("experiments"):
        raise ValueError("No experiments found")

    experiments = result["experiments"]

    # Aggregate by brand
    brand_stats = _aggregate_by_brand(experiments)

    # Write summary CSV
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        'brand_name',
        'total_experiments',
        'good_count',
        'needs_work_count',
        'failed_count',
        'avg_execution_time',
        'avg_cost_usd',
        'total_cost_usd'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for brand_name, stats in brand_stats.items():
            writer.writerow({
                'brand_name': brand_name,
                'total_experiments': stats['total'],
                'good_count': stats['good'],
                'needs_work_count': stats['needs_work'],
                'failed_count': stats['failed'],
                'avg_execution_time': round(stats['avg_time'], 2),
                'avg_cost_usd': round(stats['avg_cost'], 4),
                'total_cost_usd': round(stats['total_cost'], 4)
            })

    logger.info(f"Successfully exported summary to {output_path}")
    return str(output_file)


def _aggregate_by_brand(experiments: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Aggregate experiment statistics by brand.

    Args:
        experiments: List of experiment records

    Returns:
        Dict mapping brand_name to aggregated statistics
    """
    brand_stats = {}

    for exp in experiments:
        brand_name = exp.get("brandProfile", {}).get("brand_name", "Unknown")

        if brand_name not in brand_stats:
            brand_stats[brand_name] = {
                'total': 0,
                'good': 0,
                'needs_work': 0,
                'failed': 0,
                'total_time': 0,
                'total_cost': 0.0
            }

        stats = brand_stats[brand_name]
        stats['total'] += 1

        # Count by quality
        quality = exp.get("qualityTag")
        if quality == "good":
            stats['good'] += 1
        elif quality == "needs_work":
            stats['needs_work'] += 1
        elif quality == "failed":
            stats['failed'] += 1

        # Sum execution time and cost
        exec_time = exp.get("executionTimeSeconds", 0)
        if exec_time:
            stats['total_time'] += exec_time

        cost = exp.get("costUsd")
        if cost:
            stats['total_cost'] += float(cost)

    # Calculate averages
    for brand_name, stats in brand_stats.items():
        total = stats['total']
        stats['avg_time'] = stats['total_time'] / total if total > 0 else 0
        stats['avg_cost'] = stats['total_cost'] / total if total > 0 else 0

    return brand_stats
