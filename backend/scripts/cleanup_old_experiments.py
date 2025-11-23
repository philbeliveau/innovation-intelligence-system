#!/usr/bin/env python3
"""Cleanup script for old experiments with archival support.

This script removes experiments older than the configured retention period.
Archives are automatically created before deletion and uploaded to Vercel Blob.

Usage:
    python cleanup_old_experiments.py [--dry-run] [--retention-days DAYS] [--no-archive]

Environment Variables:
    EXPERIMENT_RETENTION_DAYS: Number of days to retain experiments (default: 90)
    VERCEL_BLOB_READ_WRITE_TOKEN: Token for Vercel Blob uploads
    FRONTEND_WEBHOOK_URL: Next.js API URL for database access
    WEBHOOK_SECRET: Authentication secret for API calls
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.prisma_client import PrismaAPIClient
from experimentation.export.backup_manager import archive_old_experiments

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def cleanup_old_experiments(
    retention_days: int,
    dry_run: bool = False,
    archive_before_delete: bool = True
):
    """Delete experiments older than retention period.

    Args:
        retention_days: Number of days to retain experiments
        dry_run: If True, only show what would be deleted (don't actually delete)
        archive_before_delete: If True, archive before deletion

    Returns:
        Dict with cleanup statistics
    """
    logger.info(
        f"Starting cleanup process (retention: {retention_days} days, "
        f"dry_run: {dry_run}, archive: {archive_before_delete})"
    )

    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    cutoff_iso = cutoff_date.isoformat()

    logger.info(f"Cutoff date: {cutoff_iso} (deleting experiments before this date)")

    # Initialize Prisma client
    prisma_client = PrismaAPIClient()

    # Find old experiments
    result = prisma_client.get_experiments(
        end_date=cutoff_iso,
        page=1,
        page_size=1000
    )

    if not result or not result.get("experiments"):
        logger.info("No experiments found older than retention period")
        return {
            "found": 0,
            "archived": 0,
            "deleted": 0,
            "errors": []
        }

    experiments = result["experiments"]
    experiment_count = len(experiments)

    logger.info(f"Found {experiment_count} experiments to delete")

    stats = {
        "found": experiment_count,
        "archived": 0,
        "deleted": 0,
        "errors": [],
        "archive_path": None,
        "blob_url": None
    }

    if dry_run:
        logger.info("[DRY RUN] Would delete the following experiments:")
        for exp in experiments:
            logger.info(
                f"  - {exp.get('runId')} "
                f"(brand: {exp.get('brandProfile', {}).get('brand_name', 'Unknown')}, "
                f"date: {exp.get('timestamp')})"
            )
        logger.info(f"[DRY RUN] Total: {experiment_count} experiments")
        return stats

    # Archive before deletion if requested
    if archive_before_delete:
        try:
            logger.info("Creating archive before deletion...")
            archive_info = await archive_old_experiments(
                prisma_client=prisma_client,
                cutoff_date=cutoff_iso,
                upload_to_blob=True
            )

            stats["archived"] = archive_info["experiment_count"]
            stats["archive_path"] = archive_info["archive_path"]
            stats["blob_url"] = archive_info.get("blob_url")

            logger.info(
                f"Successfully archived {stats['archived']} experiments to "
                f"{stats['archive_path']}"
            )
            if stats["blob_url"]:
                logger.info(f"Uploaded archive to: {stats['blob_url']}")

        except Exception as e:
            error_msg = f"Failed to create archive: {e}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            logger.warning("Aborting deletion due to archive failure")
            return stats

    # Delete old experiments
    logger.info("Deleting old experiments...")

    # Note: The PrismaAPIClient doesn't have a delete method yet
    # This would need to be implemented in the Next.js API
    # For now, we'll log a warning
    logger.warning(
        "Delete functionality not yet implemented in PrismaAPIClient. "
        "Please use the Next.js admin interface to delete archived experiments."
    )

    stats["errors"].append(
        "Delete API endpoint not implemented - manual deletion required"
    )

    return stats


def main():
    """Main entry point for cleanup script."""
    parser = argparse.ArgumentParser(
        description="Cleanup old experiments with archival support"
    )
    parser.add_argument(
        '--retention-days',
        type=int,
        default=int(os.getenv('EXPERIMENT_RETENTION_DAYS', '90')),
        help='Number of days to retain experiments (default: 90 or EXPERIMENT_RETENTION_DAYS)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--no-archive',
        action='store_true',
        help='Skip archival before deletion (not recommended)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate environment variables
    required_vars = ['FRONTEND_WEBHOOK_URL', 'WEBHOOK_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)

    if not args.no_archive and not os.getenv('VERCEL_BLOB_READ_WRITE_TOKEN'):
        logger.warning(
            "VERCEL_BLOB_READ_WRITE_TOKEN not set - archive will be local only"
        )

    # Run cleanup
    try:
        stats = asyncio.run(cleanup_old_experiments(
            retention_days=args.retention_days,
            dry_run=args.dry_run,
            archive_before_delete=not args.no_archive
        ))

        # Print summary
        logger.info("=" * 60)
        logger.info("CLEANUP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Experiments found:    {stats['found']}")
        logger.info(f"Experiments archived: {stats['archived']}")
        logger.info(f"Experiments deleted:  {stats['deleted']}")

        if stats.get('archive_path'):
            logger.info(f"Archive path:         {stats['archive_path']}")
        if stats.get('blob_url'):
            logger.info(f"Blob URL:             {stats['blob_url']}")

        if stats['errors']:
            logger.info(f"Errors:               {len(stats['errors'])}")
            for error in stats['errors']:
                logger.error(f"  - {error}")

        logger.info("=" * 60)

        # Exit with error code if there were errors
        if stats['errors']:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
