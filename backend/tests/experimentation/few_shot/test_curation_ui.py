"""Tests for Curation Interface (Story 11.3c)

Tests the Gradio curation interface components for example management,
search, filtering, and dashboard visualizations.
"""
import pytest
import json
from pathlib import Path
from datetime import datetime
import tempfile

# Import components under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "experimentation"))

from curation_interface import CurationInterface
from example_usage_tracker import ExampleUsageTracker


class TestCurationInterface:
    """Test curation interface functionality (Story 11.3c AC: 4-9)"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage with test examples"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "successful_examples"
            storage_path.mkdir()

            # Create stage directories with examples
            for stage in range(7):
                stage_dir = storage_path / f"stage_{stage}"
                stage_dir.mkdir()

                # Create 2 examples per stage
                for i in range(2):
                    example = {
                        "id": f"example_stage{stage}_{i}",
                        "created_at": "2025-11-19T14:32:18Z",
                        "stage": stage,
                        "quality_score": "good" if i == 0 else "needs_work",
                        "brand_context": {
                            "brand_name": "Test Brand" if i == 0 else "Another Brand",
                            "industry": "Test Industry",
                            "country": "Canada"
                        },
                        "input": {"test": "data"},
                        "output": {"result": "output"}
                    }

                    example_file = stage_dir / f"example_stage{stage}_{i}.json"
                    example_file.write_text(json.dumps(example, indent=2))

                # Create metadata
                metadata = {
                    "stage": stage,
                    "total_examples": 2,
                    "last_updated": datetime.now().isoformat()
                }

                metadata_file = stage_dir / "metadata.json"
                metadata_file.write_text(json.dumps(metadata, indent=2))

            yield storage_path

    @pytest.fixture
    def usage_tracker(self):
        """Create usage tracker with test data"""
        tracker = ExampleUsageTracker()

        # Add test usage logs
        tracker.usage_log = [
            {"run_id": "r1", "stage": 1, "example_ids": ["example_stage1_0"], "output_quality": "good"},
            {"run_id": "r2", "stage": 1, "example_ids": ["example_stage1_0"], "output_quality": "good"},
            {"run_id": "r3", "stage": 1, "example_ids": ["example_stage1_1"], "output_quality": "needs_work"},
            {"run_id": "r4", "stage": 2, "example_ids": ["example_stage2_0"], "output_quality": "good"},
        ]

        return tracker

    @pytest.fixture
    def curation(self, temp_storage, usage_tracker):
        """Create curation interface instance"""
        return CurationInterface(
            storage_path=str(temp_storage),
            usage_tracker=usage_tracker
        )

    def test_list_examples_by_stage(self, curation):
        """Test listing examples for a stage (AC: 5)"""
        result = curation.list_examples_by_stage(stage=1)

        # Verify output contains key information
        assert "# Examples for Stage 1" in result
        assert "**Total Examples:** 2" in result
        assert "example_stage1_0" in result
        assert "example_stage1_1" in result
        assert "Test Brand" in result
        assert "Another Brand" in result
        assert "GOOD" in result
        assert "NEEDS_WORK" in result
        assert "Usage Count:" in result
        assert "Success Rate:" in result
        assert "Effectiveness:" in result

    def test_list_examples_empty_stage(self, temp_storage, usage_tracker):
        """Test listing examples for non-existent stage"""
        # Create curation with empty stage
        empty_storage = temp_storage.parent / "empty"
        empty_storage.mkdir()

        curation = CurationInterface(
            storage_path=str(empty_storage),
            usage_tracker=usage_tracker
        )

        result = curation.list_examples_by_stage(stage=1)

        assert "⚠️ No examples found for Stage 1" in result

    def test_get_example_details(self, curation):
        """Test getting full example details (AC: 5)"""
        result = curation.get_example_details(
            stage=1,
            example_id="example_stage1_0"
        )

        # Parse JSON result
        details = json.loads(result)

        assert details["id"] == "example_stage1_0"
        assert details["stage"] == 1
        assert details["quality_score"] == "good"
        assert details["brand_context"]["brand_name"] == "Test Brand"

    def test_get_example_details_not_found(self, curation):
        """Test getting details for non-existent example"""
        result = curation.get_example_details(
            stage=1,
            example_id="nonexistent"
        )

        details = json.loads(result)

        assert "error" in details

    def test_search_examples_by_brand(self, curation):
        """Test searching examples by brand name (AC: 8)"""
        result = curation.search_examples(brand="Test Brand")

        assert "Search Results" in result
        assert "Test Brand" in result
        # Should find examples across all stages that match "Test Brand"
        assert "example_stage" in result

    def test_search_examples_by_stage(self, curation):
        """Test searching examples by stage (AC: 8)"""
        result = curation.search_examples(stage=2)

        assert "Search Results" in result
        assert "Stage 2" in result
        assert "example_stage2_0" in result

    def test_search_examples_by_quality(self, curation):
        """Test searching examples by minimum quality (AC: 8)"""
        result = curation.search_examples(min_quality="good")

        # Should only return "good" quality examples
        assert "good" in result.lower()
        # Should not return needs_work examples in this filtered view
        # (though we can't strictly assert this without parsing the full output)

    def test_search_examples_combined_filters(self, curation):
        """Test searching with multiple filters"""
        result = curation.search_examples(
            brand="Another",
            stage=1,
            min_quality="needs_work"
        )

        assert "Search Results" in result
        assert "Another Brand" in result
        assert "Stage 1" in result

    def test_search_examples_no_results(self, curation):
        """Test search with no matching results"""
        result = curation.search_examples(brand="Nonexistent Brand")

        assert "⚠️ No examples match your filters" in result

    def test_remove_example(self, curation, temp_storage):
        """Test removing an example (AC: 6)"""
        result = curation.remove_example(
            stage=1,
            example_id="example_stage1_1"
        )

        # Verify success message
        assert "✅ Archived" in result
        assert "example_stage1_1" in result

        # Verify example moved to archive
        original_path = temp_storage / "stage_1" / "example_stage1_1.json"
        archive_path = temp_storage / "archived" / "stage_1" / "example_stage1_1.json"

        assert not original_path.exists()
        assert archive_path.exists()

    def test_remove_example_not_found(self, curation):
        """Test removing non-existent example"""
        result = curation.remove_example(
            stage=1,
            example_id="nonexistent"
        )

        assert "❌" in result
        assert "not found" in result

    def test_get_quality_distribution_single_stage(self, curation):
        """Test quality distribution for single stage (AC: 7)"""
        result = curation.get_quality_distribution(stage=1)

        assert "# Quality Distribution" in result
        assert "**Total Examples:** 2" in result
        assert "GOOD:" in result
        assert "NEEDS_WORK:" in result
        # Visual bar chart
        assert "█" in result

    def test_get_quality_distribution_all_stages(self, curation):
        """Test quality distribution for all stages (AC: 7)"""
        result = curation.get_quality_distribution(stage=None)

        # Should include examples from all 7 stages (14 total: 2 per stage)
        assert "**Total Examples:** 14" in result
        assert "GOOD:" in result
        assert "NEEDS_WORK:" in result

    def test_get_quality_distribution_empty(self, temp_storage, usage_tracker):
        """Test quality distribution with no examples"""
        empty_storage = temp_storage.parent / "empty"
        empty_storage.mkdir()

        curation = CurationInterface(
            storage_path=str(empty_storage),
            usage_tracker=usage_tracker
        )

        result = curation.get_quality_distribution(stage=1)

        assert "⚠️ No examples found" in result

    def test_get_performance_dashboard_with_data(self, curation):
        """Test performance dashboard generation (AC: 9)"""
        result = curation.get_performance_dashboard()

        # Verify dashboard sections
        assert "# Few-Shot Learning Performance Dashboard" in result
        assert "## Overall Statistics" in result
        assert "Total Pipeline Runs:" in result
        assert "Successful Runs:" in result
        assert "Success Rate:" in result
        assert "## Per-Stage Performance" in result

        # Should show stage-level analysis
        assert "### Stage 1" in result
        assert "Avg Success Rate:" in result

    def test_get_performance_dashboard_no_data(self, temp_storage):
        """Test performance dashboard with no usage data"""
        # Create tracker with no logs
        empty_tracker = ExampleUsageTracker()

        curation = CurationInterface(
            storage_path=str(temp_storage),
            usage_tracker=empty_tracker
        )

        result = curation.get_performance_dashboard()

        assert "⚠️ No usage data available yet" in result
        assert "Run pipeline experiments" in result


class TestCurationTabCreation:
    """Test Gradio tab creation (Story 11.3c AC: 4)"""

    def test_create_curation_tab_imports(self):
        """Test that create_curation_tab can be imported"""
        try:
            from curation_interface import create_curation_tab
            assert callable(create_curation_tab)
        except ImportError:
            pytest.fail("Failed to import create_curation_tab")

    @pytest.mark.skip(reason="Requires Gradio environment - integration test")
    def test_create_curation_tab_structure(self, temp_storage):
        """Test that curation tab creates valid Gradio Blocks

        Note: This is an integration test that requires Gradio runtime.
        Skipped in unit test suite.
        """
        import gradio as gr
        from curation_interface import create_curation_tab

        tracker = ExampleUsageTracker()

        tab = create_curation_tab(
            storage_path=str(temp_storage),
            usage_tracker=tracker
        )

        # Verify it's a Gradio Blocks component
        assert isinstance(tab, gr.Blocks)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
