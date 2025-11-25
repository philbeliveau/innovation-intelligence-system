"""7-Stage Pipeline Orchestrator

Async pipeline execution framework with state persistence and webhook notifications.
Supports hot-swappable stage implementations.
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from backend.app.prisma_client import PrismaAPIClient
from backend.pipeline.utils import send_webhook_sync
from backend.experimentation.stages import (
    Stage0Enrichment,
    Stage1Decomposition,
    Stage2Insights,
    Stage3TechniqueMatching,
    Stage4ConceptGeneration,
    Stage5CompetitiveIntelligence,
    Stage6OpportunityCards
)
from backend.experimentation.schemas import (
    Stage0Output,
    Stage1Output,
    Stage2Output,
    Stage3Output,
    Stage4Output,
    Stage5Output,
    Stage6Output
)


logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates 7-stage pipeline execution with async support.

    Handles:
    - Async stage execution
    - State persistence to database
    - Webhook notifications
    - Error handling and retry logic
    - Resume from failure
    """

    def __init__(
        self,
        run_id: str,
        prisma_client: Optional[PrismaAPIClient] = None
    ):
        """Initialize orchestrator.

        Args:
            run_id: Unique run identifier
            prisma_client: Optional Prisma client (creates new if not provided)
        """
        self.run_id = run_id
        self.prisma_client = prisma_client or PrismaAPIClient()
        self.stage_outputs = {}
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY", "2"))

    async def execute_stage_with_retry(
        self,
        stage_num: int,
        stage_name: str,
        stage_func,
        *args,
        **kwargs
    ) -> Any:
        """Execute stage with exponential backoff retry.

        Args:
            stage_num: Stage number (0-6)
            stage_name: Human-readable stage name
            stage_func: Async stage function to execute
            *args: Positional arguments for stage function
            **kwargs: Keyword arguments for stage function

        Returns:
            Stage output

        Raises:
            Exception: If stage fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[{self.run_id}] Starting Stage {stage_num}: {stage_name} (attempt {attempt + 1}/{self.max_retries})")

                # Mark stage as processing
                self.prisma_client.mark_stage_processing(self.run_id, stage_num + 1)  # Prisma uses 1-indexed

                # Execute stage
                result = await stage_func(*args, **kwargs)

                logger.info(f"[{self.run_id}] Stage {stage_num} completed successfully")

                return result

            except Exception as e:
                wait_time = self.retry_delay ** attempt  # Exponential backoff
                logger.warning(
                    f"[{self.run_id}] Stage {stage_num} attempt {attempt + 1} failed: {e}. "
                    f"{'Retrying in ' + str(wait_time) + 's...' if attempt < self.max_retries - 1 else 'No more retries.'}"
                )

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    # Final failure
                    logger.error(f"[{self.run_id}] Stage {stage_num} failed after {self.max_retries} attempts")
                    raise

    def _get_stage_model(self, stage_num: int) -> str:
        """Get model configuration for specific stage from environment variables.

        Args:
            stage_num: Stage number (0-6)

        Returns:
            Model identifier (e.g., "anthropic/claude-3-5-sonnet-20240620")
        """
        stage_model_env = f"STAGE_{stage_num}_MODEL"
        default_model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-5-sonnet-20240620")
        return os.getenv(stage_model_env, default_model)

    async def run_pipeline(
        self,
        pdf_text: str,
        brand_profile: Dict[str, Any],
        enrichment_mode: str = "basic",
        source_report_name: str = "Unknown Report",
        custom_prompts: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute complete 7-stage pipeline.

        Args:
            pdf_text: Extracted PDF text content
            brand_profile: Brand profile YAML data
            enrichment_mode: Stage 0 enrichment mode ('basic' or 'perplexity_enriched')
            source_report_name: Name of source trend report (for Stage 6 cards)
            custom_prompts: Optional custom prompt templates by stage (Story 11.6.2)

        Returns:
            Dictionary with all stage outputs

        Raises:
            Exception: If any stage fails after retries
        """
        logger.info(f"[{self.run_id}] Starting 7-stage pipeline execution")
        start_time = datetime.utcnow()

        try:
            # Initialize pipeline stages in database
            self.prisma_client.initialize_pipeline_stages(self.run_id)

            # ============================================================
            # STAGE 0: Brand Profile Enrichment
            # ============================================================
            stage0 = Stage0Enrichment(enrichment_mode=enrichment_mode)

            stage0_output = await self.execute_stage_with_retry(
                stage_num=0,
                stage_name="Brand Enrichment",
                stage_func=stage0.run,
                brand_profile=brand_profile,
                custom_prompt_content=custom_prompts.get("stage_0") if custom_prompts else None
            )

            # Save stage 0 output
            self.stage_outputs["stage_0"] = stage0_output.dict()
            self.prisma_client.mark_stage_complete(self.run_id, 1, self.stage_outputs["stage_0"])  # Prisma uses 1-indexed

            # Send webhook
            webhook_payload = {
                "stageNumber": 0,
                "stageName": "Brand Enrichment",
                "status": "COMPLETE",
                "output": self.stage_outputs["stage_0"]
            }
            send_webhook_sync(self.run_id, "stage-update", webhook_payload)

            # ============================================================
            # STAGE 1: Trend Decomposition
            # ============================================================
            stage1 = Stage1Decomposition(temperature=0.3, max_tokens=8000)

            stage1_output = await self.execute_stage_with_retry(
                stage_num=1,
                stage_name="Trend Decomposition",
                stage_func=stage1.run,
                report_text=pdf_text,
                custom_prompt_content=custom_prompts.get("stage_1") if custom_prompts else None
            )

            # Save stage 1 output
            self.stage_outputs["stage_1"] = stage1_output.dict()
            self.prisma_client.mark_stage_complete(self.run_id, 2, self.stage_outputs["stage_1"])  # Prisma uses 1-indexed

            # Send webhook
            webhook_payload = {
                "stageNumber": 1,
                "stageName": "Trend Decomposition",
                "status": "COMPLETE",
                "output": {
                    "total_trends": stage1_output.total_trends_extracted,
                    "trends": [trend.dict() for trend in stage1_output.trends]
                }
            }
            send_webhook_sync(self.run_id, "stage-update", webhook_payload)

            # ============================================================
            # STAGE 2: Consumer Insights
            # ============================================================
            stage2 = Stage2Insights(temperature=0.5, max_tokens=6000)

            stage2_output = await self.execute_stage_with_retry(
                stage_num=2,
                stage_name="Consumer Insights",
                stage_func=stage2.run,
                stage1_output=stage1_output,
                stage0_output=stage0_output,
                custom_prompt_content=custom_prompts.get("stage_2") if custom_prompts else None
            )

            # Save stage 2 output
            self.stage_outputs["stage_2"] = stage2_output.dict()
            self.prisma_client.mark_stage_complete(self.run_id, 3, self.stage_outputs["stage_2"])  # Prisma uses 1-indexed

            # Send webhook
            webhook_payload = {
                "stageNumber": 2,
                "stageName": "Consumer Insights",
                "status": "COMPLETE",
                "output": {
                    "total_insights": len(stage2_output.insights),
                    "insights": [insight.dict() for insight in stage2_output.insights]
                }
            }
            send_webhook_sync(self.run_id, "stage-update", webhook_payload)

            # ============================================================
            # STAGE 3: Innovation Technique Matching
            # ============================================================
            from backend.experimentation.openrouter_client import OpenRouterClient
            openrouter_client = OpenRouterClient()

            stage3 = Stage3TechniqueMatching()
            stage3_output = await self.execute_stage_with_retry(
                stage_num=3,
                stage_name="Technique Matching",
                stage_func=stage3.execute,
                stage2_output=stage2_output,
                brand_context=stage0_output.brand_context.model_dump(),
                openrouter_client=openrouter_client,
                custom_prompt_content=custom_prompts.get("stage_3") if custom_prompts else None
            )

            self.stage_outputs["stage_3"] = stage3_output.model_dump()
            self.prisma_client.mark_stage_complete(self.run_id, 4, self.stage_outputs["stage_3"])
            webhook_payload = {
                "stageNumber": 3,
                "stageName": "Technique Matching",
                "status": "COMPLETE",
                "output": {"total_matches": len(stage3_output.matched_techniques)}
            }
            send_webhook_sync(self.run_id, "stage-update", webhook_payload)

            # ============================================================
            # STAGE 4: Directional Concept Generation
            # ============================================================
            stage4 = Stage4ConceptGeneration()
            stage4_output = await self.execute_stage_with_retry(
                stage_num=4,
                stage_name="Concept Generation",
                stage_func=stage4.execute,
                stage2_output=stage2_output,
                stage3_output=stage3_output,
                brand_context=stage0_output.brand_context.model_dump(),
                openrouter_client=openrouter_client,
                custom_prompt_content=custom_prompts.get("stage_4") if custom_prompts else None
            )

            self.stage_outputs["stage_4"] = stage4_output.model_dump()
            self.prisma_client.mark_stage_complete(self.run_id, 5, self.stage_outputs["stage_4"])
            webhook_payload = {
                "stageNumber": 4,
                "stageName": "Concept Generation",
                "status": "COMPLETE",
                "output": {"total_concepts": stage4_output.total_concepts}
            }
            send_webhook_sync(self.run_id, "stage-update", webhook_payload)

            # ============================================================
            # STAGE 5: Competitive Intelligence Search
            # ============================================================
            stage5 = Stage5CompetitiveIntelligence()
            stage5_output_dict = await self.execute_stage_with_retry(
                stage_num=5,
                stage_name="Competitive Intelligence",
                stage_func=stage5.execute,
                stage4_output=stage4_output,
                brand_context=stage0_output.brand_context.model_dump(),
                openrouter_client=openrouter_client,
                custom_prompt_content=custom_prompts.get("stage_5") if custom_prompts else None
            )

            self.stage_outputs["stage_5"] = stage5_output_dict
            self.prisma_client.mark_stage_complete(self.run_id, 6, self.stage_outputs["stage_5"])
            webhook_payload = {
                "stageNumber": 5,
                "stageName": "Competitive Intelligence",
                "status": "COMPLETE",
                "output": {
                    "search_enabled": stage5_output_dict["search_enabled"],
                    "total_queries": stage5_output_dict["total_queries_executed"]
                }
            }
            send_webhook_sync(self.run_id, "stage-update", webhook_payload)

            # ============================================================
            # STAGE 6: Opportunity Card Packaging
            # ============================================================
            stage6 = Stage6OpportunityCards()
            stage6_output = await self.execute_stage_with_retry(
                stage_num=6,
                stage_name="Opportunity Cards",
                stage_func=stage6.execute,
                stage1_output=stage1_output,
                stage2_output=stage2_output,
                stage3_output=stage3_output,
                stage4_output=stage4_output,
                stage5_output=stage5_output_dict,
                brand_context=stage0_output.brand_context.model_dump(),
                openrouter_client=openrouter_client,
                source_report_name=source_report_name,
                custom_prompt_content=custom_prompts.get("stage_6") if custom_prompts else None
            )

            self.stage_outputs["stage_6"] = stage6_output.model_dump()
            self.prisma_client.mark_stage_complete(self.run_id, 7, self.stage_outputs["stage_6"])
            webhook_payload = {
                "stageNumber": 6,
                "stageName": "Opportunity Cards",
                "status": "COMPLETE",
                "output": {"total_cards": stage6_output.total_cards}
            }
            send_webhook_sync(self.run_id, "stage-update", webhook_payload)

            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            logger.info(f"[{self.run_id}] Complete 7-stage pipeline finished in {duration_ms}ms")

            return {
                "run_id": self.run_id,
                "status": "COMPLETED",
                "completed_stages": [0, 1, 2, 3, 4, 5, 6],
                "stage_outputs": self.stage_outputs,
                "duration_ms": duration_ms
            }

        except Exception as e:
            logger.error(f"[{self.run_id}] Pipeline execution failed: {e}", exc_info=True)

            # Mark pipeline as failed in database
            from backend.app.pipeline_errors import classify_error, create_error_payload

            current_stage = len(self.stage_outputs) + 1
            error_code = classify_error(e, current_stage)
            error_payload = create_error_payload(
                run_id=self.run_id,
                stage=current_stage,
                error_code=error_code,
                error_message=str(e),
                exception=e
            )

            self.prisma_client.mark_stage_failed(
                self.run_id,
                current_stage,
                json.dumps(error_payload["error"], indent=2)
            )

            raise


    async def resume_from_checkpoint(self, last_completed_stage: int) -> Dict[str, Any]:
        """Resume pipeline from last completed stage.

        Args:
            last_completed_stage: Last successfully completed stage (0-6)

        Returns:
            Pipeline execution results

        Note:
            Not fully implemented in Story 11.2a (foundation only)
        """
        logger.info(f"[{self.run_id}] Resuming from stage {last_completed_stage + 1}")
        raise NotImplementedError("Resume from checkpoint not yet implemented")
