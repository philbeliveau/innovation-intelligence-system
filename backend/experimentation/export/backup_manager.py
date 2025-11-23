"""Backup and archival management for experiment data.

Provides functionality for:
- Manual backup of all experiments to Vercel Blob
- Archival of old experiments before deletion
- Backup verification and restore capabilities
"""

import os
import gzip
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


async def backup_experiments(
    prisma_client: Any,
    backup_name: Optional[str] = None,
    compress: bool = True
) -> str:
    """Create a full backup of all experiments to local file.

    Args:
        prisma_client: PrismaAPIClient instance
        backup_name: Optional custom backup name (default: timestamp-based)
        compress: If True, compress backup with gzip (default: True)

    Returns:
        Path to backup file

    Raises:
        ValueError: If no experiments found
        IOError: If backup creation fails
    """
    # Generate backup filename
    if backup_name is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"experiments_backup_{timestamp}"

    extension = ".json.gz" if compress else ".json"
    backup_path = f"/tmp/{backup_name}{extension}"

    logger.info(f"Creating backup of all experiments: {backup_path}")

    # Retrieve all experiments
    result = prisma_client.get_experiments(page=1, page_size=1000)

    if not result or not result.get("experiments"):
        raise ValueError("No experiments found to backup")

    experiments = result["experiments"]

    # Build backup data
    backup_data = {
        "backup_metadata": {
            "backup_date": datetime.now().isoformat(),
            "total_experiments": len(experiments),
            "compressed": compress,
            "version": "1.0"
        },
        "experiments": experiments
    }

    # Write backup
    try:
        json_str = json.dumps(backup_data, indent=2, ensure_ascii=False)

        if compress:
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                f.write(json_str)
        else:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(json_str)

        file_size = os.path.getsize(backup_path)
        logger.info(
            f"Successfully created backup: {backup_path} "
            f"({len(experiments)} experiments, {file_size / 1024:.1f} KB)"
        )

        return backup_path

    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise IOError(f"Failed to create backup: {e}")


async def archive_to_blob(
    backup_file_path: str,
    blob_path: Optional[str] = None
) -> str:
    """Upload backup file to Vercel Blob storage.

    Args:
        backup_file_path: Path to backup file to upload
        blob_path: Optional custom blob path (default: backups/{filename})

    Returns:
        Blob URL of uploaded file

    Raises:
        ValueError: If VERCEL_BLOB_READ_WRITE_TOKEN not set
        IOError: If upload fails
    """
    from vercel_blob import put

    token = os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")
    if not token:
        raise ValueError(
            "VERCEL_BLOB_READ_WRITE_TOKEN environment variable not set"
        )

    # Generate blob path if not provided
    if blob_path is None:
        filename = Path(backup_file_path).name
        blob_path = f"backups/{filename}"

    logger.info(f"Uploading backup to Vercel Blob: {blob_path}")

    try:
        with open(backup_file_path, 'rb') as f:
            blob_url = put(blob_path, f.read(), token=token)

        logger.info(f"Successfully uploaded backup to: {blob_url}")
        return blob_url

    except Exception as e:
        logger.error(f"Failed to upload backup to Vercel Blob: {e}")
        raise IOError(f"Failed to upload backup to Vercel Blob: {e}")


async def archive_old_experiments(
    prisma_client: Any,
    cutoff_date: str,
    upload_to_blob: bool = True
) -> Dict[str, Any]:
    """Archive experiments older than cutoff date before deletion.

    Args:
        prisma_client: PrismaAPIClient instance
        cutoff_date: ISO format date (experiments before this date are archived)
        upload_to_blob: If True, upload archive to Vercel Blob (default: True)

    Returns:
        Dict with archive_path, blob_url (if uploaded), and experiment_count

    Raises:
        ValueError: If no old experiments found
    """
    logger.info(f"Archiving experiments older than {cutoff_date}")

    # Retrieve old experiments
    result = prisma_client.get_experiments(
        end_date=cutoff_date,
        page=1,
        page_size=1000
    )

    if not result or not result.get("experiments"):
        raise ValueError(f"No experiments found older than {cutoff_date}")

    experiments = result["experiments"]
    experiment_count = len(experiments)

    # Create archive
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f"archive_before_{cutoff_date}_{timestamp}"
    archive_path = await backup_experiments(
        prisma_client=prisma_client,
        backup_name=archive_name,
        compress=True
    )

    archive_info = {
        "archive_path": archive_path,
        "experiment_count": experiment_count,
        "cutoff_date": cutoff_date,
        "blob_url": None
    }

    # Upload to blob if requested
    if upload_to_blob:
        try:
            blob_url = await archive_to_blob(archive_path)
            archive_info["blob_url"] = blob_url
        except Exception as e:
            logger.warning(f"Failed to upload archive to blob: {e}")

    logger.info(
        f"Archived {experiment_count} experiments to {archive_path}"
    )

    return archive_info


async def verify_backup(backup_file_path: str) -> Dict[str, Any]:
    """Verify backup file integrity and return metadata.

    Args:
        backup_file_path: Path to backup file

    Returns:
        Dict with backup metadata and validation results

    Raises:
        IOError: If backup file cannot be read
        ValueError: If backup file is invalid
    """
    logger.info(f"Verifying backup: {backup_file_path}")

    try:
        # Determine if compressed
        is_compressed = backup_file_path.endswith('.gz')

        # Read backup
        if is_compressed:
            with gzip.open(backup_file_path, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
        else:
            with open(backup_file_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

        # Validate structure
        required_keys = ["backup_metadata", "experiments"]
        missing_keys = [k for k in required_keys if k not in backup_data]

        if missing_keys:
            raise ValueError(f"Invalid backup: missing keys {missing_keys}")

        metadata = backup_data["backup_metadata"]
        experiments = backup_data["experiments"]

        # Verify experiment count
        stated_count = metadata.get("total_experiments")
        actual_count = len(experiments)

        if stated_count != actual_count:
            logger.warning(
                f"Experiment count mismatch: metadata says {stated_count}, "
                f"found {actual_count}"
            )

        verification_result = {
            "valid": True,
            "backup_date": metadata.get("backup_date"),
            "total_experiments": actual_count,
            "compressed": is_compressed,
            "file_size_kb": os.path.getsize(backup_file_path) / 1024,
            "warnings": []
        }

        if stated_count != actual_count:
            verification_result["warnings"].append(
                f"Experiment count mismatch: {stated_count} vs {actual_count}"
            )

        logger.info(
            f"Backup verification complete: {actual_count} experiments, "
            f"{verification_result['file_size_kb']:.1f} KB"
        )

        return verification_result

    except Exception as e:
        logger.error(f"Backup verification failed: {e}")
        raise


async def restore_from_backup(
    prisma_client: Any,
    backup_file_path: str,
    skip_existing: bool = True
) -> Dict[str, Any]:
    """Restore experiments from backup file.

    Args:
        prisma_client: PrismaAPIClient instance
        backup_file_path: Path to backup file
        skip_existing: If True, skip experiments that already exist (default: True)

    Returns:
        Dict with restore statistics (restored_count, skipped_count, failed_count)

    Raises:
        IOError: If backup file cannot be read
        ValueError: If backup file is invalid
    """
    logger.info(f"Restoring experiments from backup: {backup_file_path}")

    # Verify backup first
    verification = await verify_backup(backup_file_path)
    if not verification["valid"]:
        raise ValueError("Backup verification failed")

    # Read backup
    is_compressed = backup_file_path.endswith('.gz')
    if is_compressed:
        with gzip.open(backup_file_path, 'rt', encoding='utf-8') as f:
            backup_data = json.load(f)
    else:
        with open(backup_file_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

    experiments = backup_data["experiments"]

    # Restore statistics
    stats = {
        "total_in_backup": len(experiments),
        "restored_count": 0,
        "skipped_count": 0,
        "failed_count": 0,
        "errors": []
    }

    for exp in experiments:
        try:
            run_id = exp.get("runId")

            # Check if experiment already exists
            if skip_existing:
                existing = prisma_client.get_experiments(
                    run_id=run_id,
                    page=1,
                    page_size=1
                )
                if existing and existing.get("experiments"):
                    logger.debug(f"Skipping existing experiment: {run_id}")
                    stats["skipped_count"] += 1
                    continue

            # Save experiment
            success = prisma_client.save_experiment(
                run_id=run_id,
                brand_profile=exp.get("brandProfile", {}),
                stage_outputs=exp.get("stageOutputs", {}),
                report_text=exp.get("reportText"),
                report_name=exp.get("reportName"),
                quality_tag=exp.get("qualityTag"),
                notes=exp.get("experimentNotes"),
                execution_time=exp.get("executionTimeSeconds"),
                token_usage=exp.get("tokenUsage"),
                cost_usd=exp.get("costUsd"),
                pipeline_version=exp.get("pipelineVersion", "1.0")
            )

            if success:
                stats["restored_count"] += 1
            else:
                stats["failed_count"] += 1
                stats["errors"].append(f"Failed to restore {run_id}")

        except Exception as e:
            stats["failed_count"] += 1
            error_msg = f"Error restoring {exp.get('runId', 'unknown')}: {e}"
            stats["errors"].append(error_msg)
            logger.error(error_msg)

    logger.info(
        f"Restore complete: {stats['restored_count']} restored, "
        f"{stats['skipped_count']} skipped, {stats['failed_count']} failed"
    )

    return stats
