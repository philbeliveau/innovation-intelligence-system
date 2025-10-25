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

    def initialize_pipeline_run(
        self,
        run_id: str,
        blob_url: str,
        brand_name: str,
        document_name: str = "document.pdf"
    ) -> bool:
        """Initialize PipelineRun record in database via API.

        This creates the PipelineRun record when backend is called directly
        (e.g., via MCP), bypassing the frontend.

        Args:
            run_id: Pipeline run identifier
            blob_url: Vercel Blob URL of PDF
            brand_name: Brand/company name
            document_name: Document filename

        Returns:
            True if initialization successful, False otherwise
        """
        url = f"{self.frontend_url}/api/pipeline/init"

        payload = {
            "runId": run_id,
            "blobUrl": blob_url,
            "brandName": brand_name,
            "documentName": document_name
        }

        try:
            logger.info(f"[{run_id}] Initializing PipelineRun in database via API")
            response = self.session.post(url, json=payload, timeout=30)

            if response.ok:
                logger.info(f"[{run_id}] Successfully initialized PipelineRun in database")
                return True
            else:
                logger.error(
                    f"[{run_id}] Failed to initialize PipelineRun: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"[{run_id}] Error initializing PipelineRun: {e}")
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

    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline run status from database via API.

        Args:
            run_id: Pipeline run identifier

        Returns:
            Dict with status and stageOutputs, or None if not found
        """
        url = f"{self.frontend_url}/api/pipeline/{run_id}/status"

        try:
            response = self.session.get(url, timeout=10)

            if response.ok:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"[{run_id}] Run not found in database")
                return None
            else:
                logger.error(
                    f"[{run_id}] Failed to get status: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"[{run_id}] Error getting run status: {e}")
            return None
