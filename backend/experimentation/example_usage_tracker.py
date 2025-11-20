"""Example Usage Tracker (Story 11.3c)

Tracks which few-shot examples are used during pipeline execution
and correlates them with output quality scores.

Database: Uses PrismaAPIClient to persist usage data via Next.js API.
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ExampleUsageTracker:
    """
    Tracks example usage and correlates with quality scores.

    Story 11.3c AC: 1, 2 - Usage metrics and database storage
    """

    def __init__(self, prisma_client=None):
        """
        Initialize usage tracker

        Args:
            prisma_client: PrismaAPIClient instance for database operations
        """
        self.prisma_client = prisma_client
        self.usage_log = []  # In-memory buffer before database write

    async def track_usage(
        self,
        run_id: str,
        stage: int,
        example_ids: List[str],
        output_quality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track which examples were used in a pipeline run

        Args:
            run_id: Pipeline run identifier
            stage: Stage number (0-6)
            example_ids: List of example IDs used
            output_quality: Quality score ("good" | "needs_work" | "failed")

        Returns:
            Usage record with metadata

        Story 11.3c AC: 1, 2
        """
        usage_record = {
            "run_id": run_id,
            "stage": stage,
            "example_ids": example_ids,
            "output_quality": output_quality,
            "used_at": datetime.utcnow().isoformat(),
            "example_count": len(example_ids)
        }

        # Add to in-memory buffer
        self.usage_log.append(usage_record)

        # Persist to database via Prisma API if available
        if self.prisma_client:
            try:
                await self._persist_to_database(usage_record)
                logger.info(
                    f"Tracked {len(example_ids)} examples for run {run_id} stage {stage}"
                )
            except Exception as e:
                logger.error(f"Failed to persist usage tracking: {e}")

        return usage_record

    async def _persist_to_database(self, usage_record: Dict[str, Any]) -> None:
        """
        Persist usage record to database via Prisma API

        Note: This requires a new API endpoint on Next.js side:
        POST /api/example-usage

        Story 11.3c AC: 2 - Database storage via PrismaAPIClient
        """
        if not self.prisma_client:
            logger.warning("PrismaAPIClient not available - skipping database write")
            return

        # For now, log the intent - actual API endpoint needs to be created
        logger.info(f"Would persist to database: {usage_record}")

        # TODO: Implement when Next.js API endpoint exists
        # await self.prisma_client.create_example_usage(usage_record)

    def get_usage_stats(
        self,
        example_id: Optional[str] = None,
        stage: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics for examples

        Args:
            example_id: Filter by specific example
            stage: Filter by pipeline stage

        Returns:
            Usage statistics dictionary

        Story 11.3c AC: 1 - Usage metrics
        """
        filtered_logs = self.usage_log

        # Apply filters
        if example_id:
            filtered_logs = [
                log for log in filtered_logs
                if example_id in log["example_ids"]
            ]

        if stage is not None:
            filtered_logs = [
                log for log in filtered_logs
                if log["stage"] == stage
            ]

        # Calculate statistics
        total_uses = len(filtered_logs)

        quality_counts = {
            "good": 0,
            "needs_work": 0,
            "failed": 0,
            "unknown": 0
        }

        for log in filtered_logs:
            quality = log.get("output_quality")
            if quality in quality_counts:
                quality_counts[quality] += 1
            else:
                quality_counts["unknown"] += 1

        success_rate = (
            quality_counts["good"] / total_uses
            if total_uses > 0 else 0.0
        )

        return {
            "total_uses": total_uses,
            "quality_distribution": quality_counts,
            "success_rate": success_rate,
            "filtered_by": {
                "example_id": example_id,
                "stage": stage
            }
        }

    def clear_log(self) -> None:
        """Clear in-memory usage log (useful for testing)"""
        self.usage_log = []


class CorrelationAnalyzer:
    """
    Analyzes correlation between examples and output quality.

    Story 11.3c AC: 3 - Correlation analysis
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize correlation analyzer

        Args:
            storage_path: Path to successful_examples directory
        """
        if storage_path is None:
            self.storage_path = Path(__file__).parent / "successful_examples"
        else:
            self.storage_path = Path(storage_path)

    def calculate_example_effectiveness(
        self,
        example_id: str,
        usage_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate effectiveness score for an example

        Effectiveness = (successful_uses / total_uses) × usage_frequency_weight

        Args:
            example_id: Example identifier
            usage_logs: List of usage records from tracker

        Returns:
            Effectiveness metrics

        Story 11.3c AC: 3 - Identify examples that improve quality scores
        """
        # Filter logs for this example
        relevant_logs = [
            log for log in usage_logs
            if example_id in log.get("example_ids", [])
        ]

        total_uses = len(relevant_logs)

        if total_uses == 0:
            return {
                "example_id": example_id,
                "total_uses": 0,
                "successful_uses": 0,
                "success_rate": 0.0,
                "effectiveness_score": 0.0
            }

        # Count successful uses
        successful_uses = len([
            log for log in relevant_logs
            if log.get("output_quality") == "good"
        ])

        success_rate = successful_uses / total_uses

        # Weight by usage frequency (popular examples get higher scores)
        usage_frequency_weight = min(total_uses / 10.0, 1.0)

        effectiveness_score = success_rate * (0.7 + 0.3 * usage_frequency_weight)

        return {
            "example_id": example_id,
            "total_uses": total_uses,
            "successful_uses": successful_uses,
            "success_rate": success_rate,
            "effectiveness_score": effectiveness_score,
            "usage_frequency_weight": usage_frequency_weight
        }

    def get_top_performers(
        self,
        stage: int,
        usage_logs: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top-performing examples for a stage

        Args:
            stage: Pipeline stage (0-6)
            usage_logs: List of usage records
            top_n: Number of top examples to return

        Returns:
            List of top performers sorted by effectiveness

        Story 11.3c AC: 3 - Identify which examples improve quality scores
        """
        # Load all examples for stage
        stage_path = self.storage_path / f"stage_{stage}"

        if not stage_path.exists():
            return []

        example_files = list(stage_path.glob("example_*.json"))

        # Calculate effectiveness for each example
        effectiveness_scores = []

        for example_file in example_files:
            example_id = example_file.stem

            effectiveness = self.calculate_example_effectiveness(
                example_id,
                usage_logs
            )

            effectiveness_scores.append(effectiveness)

        # Sort by effectiveness score (descending)
        effectiveness_scores.sort(
            key=lambda x: x["effectiveness_score"],
            reverse=True
        )

        return effectiveness_scores[:top_n]

    def generate_insights(
        self,
        stage: int,
        usage_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate insights on best-performing examples

        Args:
            stage: Pipeline stage (0-6)
            usage_logs: List of usage records

        Returns:
            Insights dictionary with recommendations

        Story 11.3c AC: 3 - Generate insights on best-performing examples
        """
        top_performers = self.get_top_performers(stage, usage_logs, top_n=10)

        if not top_performers:
            return {
                "stage": stage,
                "total_examples": 0,
                "top_performers": [],
                "insights": ["No examples found for this stage"]
            }

        # Calculate stage-level statistics
        avg_success_rate = sum(
            p["success_rate"] for p in top_performers
        ) / len(top_performers)

        total_uses = sum(p["total_uses"] for p in top_performers)

        insights = []

        # Generate insights
        if avg_success_rate > 0.8:
            insights.append(
                f"Stage {stage} has strong examples with {avg_success_rate:.1%} "
                f"average success rate"
            )
        elif avg_success_rate < 0.5:
            insights.append(
                f"Stage {stage} examples need improvement - only {avg_success_rate:.1%} "
                f"success rate"
            )

        # Identify underutilized high-performers
        underutilized = [
            p for p in top_performers
            if p["success_rate"] > 0.8 and p["total_uses"] < 5
        ]

        if underutilized:
            insights.append(
                f"{len(underutilized)} high-quality examples are underutilized "
                f"(< 5 uses) - consider promoting them"
            )

        return {
            "stage": stage,
            "total_examples": len(top_performers),
            "avg_success_rate": avg_success_rate,
            "total_uses": total_uses,
            "top_performers": top_performers[:5],
            "insights": insights
        }
