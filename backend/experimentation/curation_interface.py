"""Curation Interface Components for Gradio (Story 11.3c)

Provides UI components for example management, usage analytics,
and performance dashboards.
"""
import json
import gradio as gr
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging

# Import dependencies
try:
    from .few_shot_manager import FewShotExampleManager
    from .example_selector import ExampleSelector
    from .example_usage_tracker import ExampleUsageTracker, CorrelationAnalyzer
except ImportError:
    from few_shot_manager import FewShotExampleManager
    from example_selector import ExampleSelector
    from example_usage_tracker import ExampleUsageTracker, CorrelationAnalyzer

logger = logging.getLogger(__name__)


class CurationInterface:
    """
    Gradio UI components for example curation and analytics.

    Story 11.3c AC: 4, 5, 6 - Curation interface with example management
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        usage_tracker: Optional[ExampleUsageTracker] = None
    ):
        """
        Initialize curation interface

        Args:
            storage_path: Path to successful_examples directory
            usage_tracker: ExampleUsageTracker instance (for analytics)
        """
        if storage_path is None:
            self.storage_path = Path(__file__).parent / "successful_examples"
        else:
            self.storage_path = Path(storage_path)

        self.usage_tracker = usage_tracker or ExampleUsageTracker()
        self.correlation_analyzer = CorrelationAnalyzer(str(self.storage_path))

    def list_examples_by_stage(self, stage: int) -> str:
        """
        List all examples for a stage with metadata

        Args:
            stage: Pipeline stage (0-6)

        Returns:
            Markdown-formatted list of examples

        Story 11.3c AC: 5 - Display examples by stage with usage statistics
        """
        stage_path = self.storage_path / f"stage_{stage}"

        if not stage_path.exists():
            return f"⚠️ No examples found for Stage {stage}"

        # Load metadata
        metadata_path = stage_path / "metadata.json"
        metadata = {}

        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

        # Load examples
        example_files = sorted(stage_path.glob("example_*.json"))

        if not example_files:
            return f"⚠️ No examples found for Stage {stage}"

        # Get usage stats
        usage_logs = self.usage_tracker.usage_log

        output = [f"# Examples for Stage {stage}\n"]
        output.append(f"**Total Examples:** {len(example_files)}\n")

        for example_file in example_files:
            with open(example_file, 'r') as f:
                example = json.load(f)

            example_id = example_file.stem

            # Calculate effectiveness
            effectiveness = self.correlation_analyzer.calculate_example_effectiveness(
                example_id,
                usage_logs
            )

            # Format display
            output.append(f"---\n")
            output.append(f"## {example_id}\n")
            output.append(f"**Created:** {example.get('created_at', 'Unknown')}\n")
            output.append(
                f"**Brand:** {example.get('brand_context', {}).get('brand_name', 'N/A')}\n"
            )
            output.append(
                f"**Quality:** {example.get('quality_score', 'unknown').upper()}\n"
            )
            output.append(f"**Usage Count:** {effectiveness['total_uses']}\n")
            output.append(
                f"**Success Rate:** {effectiveness['success_rate']:.1%}\n"
            )
            output.append(
                f"**Effectiveness:** {effectiveness['effectiveness_score']:.2f}\n"
            )

        return "\n".join(output)

    def get_example_details(self, stage: int, example_id: str) -> str:
        """
        Get full details for a specific example

        Args:
            stage: Pipeline stage (0-6)
            example_id: Example identifier

        Returns:
            JSON-formatted example details

        Story 11.3c AC: 5 - Example content preview
        """
        example_path = self.storage_path / f"stage_{stage}" / f"{example_id}.json"

        if not example_path.exists():
            return json.dumps({"error": f"Example {example_id} not found"}, indent=2)

        with open(example_path, 'r') as f:
            example = json.load(f)

        return json.dumps(example, indent=2)

    def search_examples(
        self,
        brand: Optional[str] = None,
        stage: Optional[int] = None,
        min_quality: Optional[str] = None
    ) -> str:
        """
        Search examples with filters

        Args:
            brand: Filter by brand name (partial match)
            stage: Filter by stage number
            min_quality: Minimum quality score ("good" | "needs_work")

        Returns:
            Markdown-formatted search results

        Story 11.3c AC: 8 - Example search and filtering
        """
        results = []

        # Determine which stages to search
        stages = [stage] if stage is not None else range(7)

        for s in stages:
            stage_path = self.storage_path / f"stage_{s}"

            if not stage_path.exists():
                continue

            for example_file in stage_path.glob("example_*.json"):
                with open(example_file, 'r') as f:
                    example = json.load(f)

                # Apply filters
                if brand:
                    example_brand = example.get("brand_context", {}).get("brand_name", "")
                    if brand.lower() not in example_brand.lower():
                        continue

                if min_quality:
                    quality_order = {"good": 2, "needs_work": 1, "failed": 0}
                    example_quality = example.get("quality_score", "failed")

                    if quality_order.get(example_quality, 0) < quality_order.get(min_quality, 0):
                        continue

                results.append({
                    "stage": s,
                    "example_id": example_file.stem,
                    "brand": example.get("brand_context", {}).get("brand_name", "N/A"),
                    "quality": example.get("quality_score", "unknown"),
                    "created_at": example.get("created_at", "Unknown")
                })

        if not results:
            return "⚠️ No examples match your filters"

        output = [f"# Search Results ({len(results)} examples)\n"]

        for result in results:
            output.append(
                f"- **Stage {result['stage']}** - {result['example_id']} "
                f"({result['brand']}, {result['quality']})\n"
            )

        return "\n".join(output)

    def remove_example(self, stage: int, example_id: str) -> str:
        """
        Remove an example from storage

        Args:
            stage: Pipeline stage (0-6)
            example_id: Example identifier

        Returns:
            Status message

        Story 11.3c AC: 6 - Implement review and removal workflow
        """
        example_path = self.storage_path / f"stage_{stage}" / f"{example_id}.json"

        if not example_path.exists():
            return f"❌ Example {example_id} not found in Stage {stage}"

        try:
            # Archive instead of delete (safety)
            archive_path = self.storage_path / "archived" / f"stage_{stage}"
            archive_path.mkdir(parents=True, exist_ok=True)

            example_path.rename(archive_path / f"{example_id}.json")

            logger.info(f"Archived example {example_id} from stage {stage}")

            return f"✅ Archived example {example_id} from Stage {stage}"

        except Exception as e:
            logger.error(f"Failed to remove example: {e}")
            return f"❌ Failed to remove example: {str(e)}"

    def get_quality_distribution(self, stage: Optional[int] = None) -> str:
        """
        Get quality score distribution for examples

        Args:
            stage: Optional stage filter

        Returns:
            Markdown-formatted distribution chart

        Story 11.3c AC: 7 - Visualize quality scores and usage trends
        """
        quality_counts = {"good": 0, "needs_work": 0, "failed": 0}

        stages = [stage] if stage is not None else range(7)

        for s in stages:
            stage_path = self.storage_path / f"stage_{s}"

            if not stage_path.exists():
                continue

            for example_file in stage_path.glob("example_*.json"):
                with open(example_file, 'r') as f:
                    example = json.load(f)

                quality = example.get("quality_score", "failed")
                if quality in quality_counts:
                    quality_counts[quality] += 1

        total = sum(quality_counts.values())

        if total == 0:
            return "⚠️ No examples found"

        output = ["# Quality Distribution\n"]
        output.append(f"**Total Examples:** {total}\n\n")

        for quality, count in quality_counts.items():
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 2)
            output.append(f"**{quality.upper()}:** {count} ({percentage:.1f}%) {bar}\n")

        return "\n".join(output)

    def get_performance_dashboard(self) -> str:
        """
        Generate performance dashboard with key metrics

        Returns:
            Markdown-formatted dashboard

        Story 11.3c AC: 9 - Show pipeline quality before/after few-shot learning
        """
        usage_logs = self.usage_tracker.usage_log

        if not usage_logs:
            return "⚠️ No usage data available yet. Run pipeline experiments to see analytics."

        output = ["# Few-Shot Learning Performance Dashboard\n"]

        # Overall statistics
        total_runs = len(usage_logs)
        good_runs = len([log for log in usage_logs if log.get("output_quality") == "good"])
        success_rate = (good_runs / total_runs) * 100 if total_runs > 0 else 0

        output.append(f"## Overall Statistics\n")
        output.append(f"- **Total Pipeline Runs:** {total_runs}\n")
        output.append(f"- **Successful Runs:** {good_runs}\n")
        output.append(f"- **Success Rate:** {success_rate:.1f}%\n\n")

        # Per-stage analysis
        output.append(f"## Per-Stage Performance\n")

        for stage in range(7):
            insights = self.correlation_analyzer.generate_insights(stage, usage_logs)

            if insights["total_examples"] > 0:
                output.append(f"### Stage {stage}\n")
                output.append(
                    f"- **Examples:** {insights['total_examples']}\n"
                )
                output.append(
                    f"- **Avg Success Rate:** {insights['avg_success_rate']:.1%}\n"
                )
                output.append(
                    f"- **Total Uses:** {insights['total_uses']}\n"
                )

                if insights["insights"]:
                    output.append(f"- **Insights:**\n")
                    for insight in insights["insights"]:
                        output.append(f"  - {insight}\n")

                output.append("\n")

        return "\n".join(output)


def create_curation_tab(
    storage_path: Optional[str] = None,
    usage_tracker: Optional[ExampleUsageTracker] = None
) -> gr.Blocks:
    """
    Create Gradio tab for example curation interface

    Args:
        storage_path: Path to successful_examples directory
        usage_tracker: ExampleUsageTracker instance

    Returns:
        Gradio Blocks component for curation interface

    Story 11.3c AC: 4 - Add Gradio tab for example management
    """
    curation = CurationInterface(storage_path, usage_tracker)

    with gr.Blocks() as curation_tab:
        gr.Markdown("# 📚 Example Curation & Analytics")

        with gr.Tabs():
            # Tab 1: Browse Examples
            with gr.Tab("Browse Examples"):
                gr.Markdown("## Browse examples by stage")

                stage_selector = gr.Slider(
                    minimum=0,
                    maximum=6,
                    step=1,
                    value=0,
                    label="Select Stage"
                )

                browse_button = gr.Button("Load Examples")
                browse_output = gr.Markdown()

                browse_button.click(
                    fn=curation.list_examples_by_stage,
                    inputs=[stage_selector],
                    outputs=[browse_output]
                )

            # Tab 2: Search Examples
            with gr.Tab("Search"):
                gr.Markdown("## Search examples with filters")

                with gr.Row():
                    search_brand = gr.Textbox(
                        label="Brand Name (partial match)",
                        placeholder="e.g., Lactalis"
                    )
                    search_stage = gr.Slider(
                        minimum=0,
                        maximum=6,
                        step=1,
                        value=0,
                        label="Stage (optional)"
                    )
                    search_quality = gr.Dropdown(
                        choices=["good", "needs_work", "failed"],
                        label="Minimum Quality",
                        value="good"
                    )

                search_button = gr.Button("Search")
                search_output = gr.Markdown()

                search_button.click(
                    fn=curation.search_examples,
                    inputs=[search_brand, search_stage, search_quality],
                    outputs=[search_output]
                )

            # Tab 3: Quality Distribution
            with gr.Tab("Quality Distribution"):
                gr.Markdown("## Example quality distribution")

                dist_stage_selector = gr.Slider(
                    minimum=0,
                    maximum=6,
                    step=1,
                    value=0,
                    label="Select Stage (or leave for all stages)"
                )

                dist_button = gr.Button("Show Distribution")
                dist_output = gr.Markdown()

                dist_button.click(
                    fn=curation.get_quality_distribution,
                    inputs=[dist_stage_selector],
                    outputs=[dist_output]
                )

            # Tab 4: Performance Dashboard
            with gr.Tab("Performance Dashboard"):
                gr.Markdown("## Few-shot learning impact analysis")

                dashboard_button = gr.Button("Refresh Dashboard")
                dashboard_output = gr.Markdown()

                dashboard_button.click(
                    fn=curation.get_performance_dashboard,
                    inputs=[],
                    outputs=[dashboard_output]
                )

                # Auto-load on tab open
                curation_tab.load(
                    fn=curation.get_performance_dashboard,
                    inputs=[],
                    outputs=[dashboard_output]
                )

    return curation_tab
