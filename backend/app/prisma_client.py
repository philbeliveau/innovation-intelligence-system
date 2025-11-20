"""Prisma HTTP API Client

Client for Python backend to interact with Next.js Prisma API endpoints.
Replaces file-based status management with database writes via HTTP.
"""
import os
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0  # seconds
MAX_RETRY_DELAY = 10.0  # seconds


class PrismaAPIClient:
    """HTTP client for interacting with Next.js Prisma API endpoints."""

    def __init__(self):
        """Initialize Prisma API client with environment configuration."""
        self.frontend_url = os.getenv(
            "FRONTEND_WEBHOOK_URL",
            "https://innovation-web-rho.vercel.app"
        )
        self.webhook_secret = os.getenv("WEBHOOK_SECRET")

        if not self.webhook_secret:
            logger.warning(
                "WEBHOOK_SECRET not set - API calls will fail authentication"
            )

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-Webhook-Secret": self.webhook_secret or ""
        })

    def update_stage_status(
        self,
        run_id: str,
        stage_number: int,
        stage_name: str,
        status: str,
        output: Optional[str] = None,
        completed_at: Optional[str] = None
    ) -> bool:
        """Update stage status in Prisma via Next.js API.

        Args:
            run_id: Pipeline run identifier
            stage_number: Stage number (1-5)
            stage_name: Stage name (e.g., "Input Processing")
            status: Status - "PROCESSING", "COMPLETED", "FAILED", "CANCELLED"
            output: Stage output data (JSON string or markdown)
            completed_at: ISO timestamp (optional, auto-generated if COMPLETED)

        Returns:
            True if update successful, False otherwise
        """
        url = f"{self.frontend_url}/api/pipeline/{run_id}/stage-update"

        payload = {
            "stageNumber": stage_number,
            "stageName": stage_name,
            "status": status,
            "output": output or "",
        }

        # Add completion timestamp if provided
        if completed_at:
            payload["completedAt"] = completed_at
        elif status == "COMPLETED":
            payload["completedAt"] = datetime.utcnow().isoformat() + "Z"

        # Retry logic with exponential backoff
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(
                    f"[{run_id}] Updating stage {stage_number} to {status} via Prisma API (attempt {attempt + 1}/{MAX_RETRIES})"
                )

                response = self.session.post(url, json=payload, timeout=30)

                if response.ok:
                    logger.info(
                        f"[{run_id}] Successfully updated stage {stage_number} in Prisma"
                    )
                    return True
                else:
                    logger.error(
                        f"[{run_id}] Prisma API error: {response.status_code} - {response.text}"
                    )
                    # Don't retry on 4xx client errors (except 429 rate limit)
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        logger.error(f"[{run_id}] Client error, not retrying")
                        return False

            except requests.exceptions.Timeout:
                logger.error(f"[{run_id}] Prisma API timeout after 30s")
            except requests.exceptions.RequestException as e:
                logger.error(f"[{run_id}] Failed to call Prisma API: {e}")
            except Exception as e:
                logger.error(f"[{run_id}] Unexpected error calling Prisma API: {e}")

            # If not the last attempt, wait before retrying
            if attempt < MAX_RETRIES - 1:
                delay = min(INITIAL_RETRY_DELAY * (2 ** attempt), MAX_RETRY_DELAY)
                logger.warning(
                    f"[{run_id}] Retrying stage {stage_number} update in {delay:.1f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"[{run_id}] Failed to update stage {stage_number} after {MAX_RETRIES} attempts"
                )

        return False

    def initialize_pipeline_stages(self, run_id: str) -> bool:
        """Initialize all 5 stages as PROCESSING (stage 1) / pending (2-5).

        This is called at pipeline start to set up initial stage tracking.

        Args:
            run_id: Pipeline run identifier

        Returns:
            True if initialization successful, False otherwise
        """
        stage_names = {
            1: "Input Processing",
            2: "Signal Amplification",
            3: "General Translation",
            4: "Brand Contextualization",
            5: "Opportunity Generation"
        }

        success = True

        # Initialize stage 1 as PROCESSING
        if not self.update_stage_status(
            run_id=run_id,
            stage_number=1,
            stage_name=stage_names[1],
            status="PROCESSING",
            output=""
        ):
            success = False

        logger.info(f"[{run_id}] Initialized pipeline stages in Prisma")
        return success

    def mark_stage_complete(
        self,
        run_id: str,
        stage_number: int,
        output_data: Any
    ) -> bool:
        """Mark a stage as completed with output data.

        Args:
            run_id: Pipeline run identifier
            stage_number: Stage number (1-5)
            output_data: Stage output (will be JSON-stringified if dict)

        Returns:
            True if update successful, False otherwise
        """
        import json

        stage_names = {
            1: "Input Processing",
            2: "Signal Amplification",
            3: "General Translation",
            4: "Brand Contextualization",
            5: "Opportunity Generation"
        }

        # Convert output to JSON string if it's a dict
        if isinstance(output_data, dict):
            output_str = json.dumps(output_data, indent=2)
        else:
            output_str = str(output_data)

        return self.update_stage_status(
            run_id=run_id,
            stage_number=stage_number,
            stage_name=stage_names.get(stage_number, f"Stage {stage_number}"),
            status="COMPLETED",
            output=output_str
        )

    def mark_stage_failed(
        self,
        run_id: str,
        stage_number: int,
        error_message: str
    ) -> bool:
        """Mark a stage as failed with error message.

        Args:
            run_id: Pipeline run identifier
            stage_number: Stage number (1-5)
            error_message: Error description

        Returns:
            True if update successful, False otherwise
        """
        stage_names = {
            1: "Input Processing",
            2: "Signal Amplification",
            3: "General Translation",
            4: "Brand Contextualization",
            5: "Opportunity Generation"
        }

        return self.update_stage_status(
            run_id=run_id,
            stage_number=stage_number,
            stage_name=stage_names.get(stage_number, f"Stage {stage_number}"),
            status="FAILED",
            output=error_message
        )

    def mark_stage_processing(
        self,
        run_id: str,
        stage_number: int
    ) -> bool:
        """Mark a stage as currently processing.

        Args:
            run_id: Pipeline run identifier
            stage_number: Stage number (1-5)

        Returns:
            True if update successful, False otherwise
        """
        stage_names = {
            1: "Input Processing",
            2: "Signal Amplification",
            3: "General Translation",
            4: "Brand Contextualization",
            5: "Opportunity Generation"
        }

        return self.update_stage_status(
            run_id=run_id,
            stage_number=stage_number,
            stage_name=stage_names.get(stage_number, f"Stage {stage_number}"),
            status="PROCESSING",
            output=""
        )

    def save_experiment(
        self,
        run_id: str,
        brand_profile: Dict[str, Any],
        stage_outputs: Dict[str, Any],
        report_text: Optional[str] = None,
        report_name: Optional[str] = None,
        quality_tag: Optional[str] = None,
        notes: Optional[str] = None,
        execution_time: Optional[int] = None,
        token_usage: Optional[Dict[str, Any]] = None,
        cost_usd: Optional[float] = None,
        pipeline_version: str = "1.0"
    ) -> bool:
        """Save complete pipeline experiment to database via Next.js API.

        Args:
            run_id: Unique run identifier
            brand_profile: Brand context dict
            stage_outputs: All stage outputs (dict with stage_0 to stage_6)
            report_text: Full PDF text (optional)
            report_name: Original filename (optional)
            quality_tag: "good" | "needs_work" | "failed" (optional)
            notes: User notes (optional)
            execution_time: Total seconds (optional)
            token_usage: Token tracking dict (optional)
            cost_usd: Estimated cost (optional)
            pipeline_version: Pipeline version (default: "1.0")

        Returns:
            True if save successful, False otherwise
        """
        url = f"{self.frontend_url}/api/experiments"

        payload = {
            "runId": run_id,
            "brandProfile": brand_profile,
            "stageOutputs": stage_outputs,
            "reportText": report_text,
            "reportName": report_name,
            "qualityTag": quality_tag,
            "experimentNotes": notes,
            "executionTimeSeconds": execution_time,
            "tokenUsage": token_usage,
            "costUsd": cost_usd,
            "pipelineVersion": pipeline_version
        }

        try:
            logger.info(f"[{run_id}] Saving experiment to database via API")
            response = self.session.post(url, json=payload, timeout=30)

            if response.ok:
                logger.info(f"[{run_id}] Successfully saved experiment")
                return True
            else:
                logger.error(
                    f"[{run_id}] Failed to save experiment: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"[{run_id}] Error saving experiment: {e}")
            return False

    def get_experiments(
        self,
        quality_tag: Optional[str] = None,
        brand_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        pipeline_version: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "timestamp_desc"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve experiments from database with filtering and pagination.

        Args:
            quality_tag: Filter by quality ("good", "needs_work", "failed")
            brand_name: Filter by brand name
            start_date: Filter by timestamp >= start_date (ISO format)
            end_date: Filter by timestamp <= end_date (ISO format)
            pipeline_version: Filter by pipeline version
            page: Page number (default: 1)
            page_size: Results per page (default: 20, max: 100)
            order_by: Sort order ("timestamp_desc", "timestamp_asc", "cost_desc")

        Returns:
            Dict with experiments and pagination info, or None if error
        """
        url = f"{self.frontend_url}/api/experiments"

        params = {
            "page": page,
            "pageSize": page_size,
            "orderBy": order_by
        }

        if quality_tag:
            params["qualityTag"] = quality_tag
        if brand_name:
            params["brandName"] = brand_name
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if pipeline_version:
            params["pipelineVersion"] = pipeline_version

        try:
            logger.info(f"Retrieving experiments with filters: {params}")
            response = self.session.get(url, params=params, timeout=30)

            if response.ok:
                data = response.json()
                logger.info(
                    f"Retrieved {len(data.get('experiments', []))} experiments "
                    f"(page {page}/{data.get('pagination', {}).get('totalPages', '?')})"
                )
                return data
            else:
                logger.error(
                    f"Failed to retrieve experiments: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Error retrieving experiments: {e}")
            return None
