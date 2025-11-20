"""Tests for Example Usage Tracking and Correlation Analysis (Story 11.3c)

Tests the usage tracking, correlation analysis, and performance metrics
for few-shot learning system.
"""
import pytest
import json
from pathlib import Path
from datetime import datetime
import tempfile
import os

# Import components under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "experimentation"))

from example_usage_tracker import ExampleUsageTracker, CorrelationAnalyzer


class TestExampleUsageTracker:
    """Test usage tracking functionality (Story 11.3c AC: 1, 2)"""

    @pytest.fixture
    def tracker(self):
        """Create tracker instance for testing"""
        return ExampleUsageTracker(prisma_client=None)

    @pytest.mark.asyncio
    async def test_track_usage_basic(self, tracker):
        """Test basic usage tracking"""
        # Track example usage
        usage_record = await tracker.track_usage(
            run_id="test-run-001",
            stage=1,
            example_ids=["example_20251119_a3f8b2", "example_20251119_c7d1e9"],
            output_quality="good"
        )

        # Verify record structure
        assert usage_record["run_id"] == "test-run-001"
        assert usage_record["stage"] == 1
        assert len(usage_record["example_ids"]) == 2
        assert usage_record["output_quality"] == "good"
        assert "used_at" in usage_record
        assert usage_record["example_count"] == 2

        # Verify in-memory log
        assert len(tracker.usage_log) == 1

    @pytest.mark.asyncio
    async def test_track_multiple_usages(self, tracker):
        """Test tracking multiple pipeline runs"""
        # Track 3 runs
        await tracker.track_usage("run-001", 1, ["ex1"], "good")
        await tracker.track_usage("run-002", 1, ["ex1", "ex2"], "needs_work")
        await tracker.track_usage("run-003", 2, ["ex3"], "good")

        assert len(tracker.usage_log) == 3

    def test_get_usage_stats_all(self, tracker):
        """Test getting overall usage statistics"""
        # Add test data
        tracker.usage_log = [
            {"run_id": "r1", "stage": 1, "example_ids": ["ex1"], "output_quality": "good"},
            {"run_id": "r2", "stage": 1, "example_ids": ["ex1"], "output_quality": "good"},
            {"run_id": "r3", "stage": 1, "example_ids": ["ex2"], "output_quality": "needs_work"},
            {"run_id": "r4", "stage": 2, "example_ids": ["ex3"], "output_quality": "failed"},
        ]

        # Get all stats
        stats = tracker.get_usage_stats()

        assert stats["total_uses"] == 4
        assert stats["quality_distribution"]["good"] == 2
        assert stats["quality_distribution"]["needs_work"] == 1
        assert stats["quality_distribution"]["failed"] == 1
        assert stats["success_rate"] == 0.5  # 2/4

    def test_get_usage_stats_filtered_by_example(self, tracker):
        """Test filtering stats by example ID"""
        tracker.usage_log = [
            {"run_id": "r1", "stage": 1, "example_ids": ["ex1"], "output_quality": "good"},
            {"run_id": "r2", "stage": 1, "example_ids": ["ex1"], "output_quality": "good"},
            {"run_id": "r3", "stage": 1, "example_ids": ["ex2"], "output_quality": "needs_work"},
        ]

        # Filter for ex1
        stats = tracker.get_usage_stats(example_id="ex1")

        assert stats["total_uses"] == 2
        assert stats["quality_distribution"]["good"] == 2
        assert stats["success_rate"] == 1.0  # 2/2
        assert stats["filtered_by"]["example_id"] == "ex1"

    def test_get_usage_stats_filtered_by_stage(self, tracker):
        """Test filtering stats by stage"""
        tracker.usage_log = [
            {"run_id": "r1", "stage": 1, "example_ids": ["ex1"], "output_quality": "good"},
            {"run_id": "r2", "stage": 1, "example_ids": ["ex2"], "output_quality": "good"},
            {"run_id": "r3", "stage": 2, "example_ids": ["ex3"], "output_quality": "needs_work"},
        ]

        # Filter for stage 1
        stats = tracker.get_usage_stats(stage=1)

        assert stats["total_uses"] == 2
        assert stats["quality_distribution"]["good"] == 2
        assert stats["filtered_by"]["stage"] == 1

    def test_clear_log(self, tracker):
        """Test clearing usage log"""
        tracker.usage_log = [{"test": "data"}]

        tracker.clear_log()

        assert len(tracker.usage_log) == 0


class TestCorrelationAnalyzer:
    """Test correlation analysis functionality (Story 11.3c AC: 3)"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "successful_examples"
            storage_path.mkdir()

            # Create stage directories
            for stage in range(7):
                stage_dir = storage_path / f"stage_{stage}"
                stage_dir.mkdir()

            yield storage_path

    @pytest.fixture
    def analyzer(self, temp_storage):
        """Create analyzer instance with temp storage"""
        return CorrelationAnalyzer(storage_path=str(temp_storage))

    def test_calculate_example_effectiveness_no_uses(self, analyzer):
        """Test effectiveness calculation with no usage"""
        usage_logs = []

        effectiveness = analyzer.calculate_example_effectiveness(
            "example_test_001",
            usage_logs
        )

        assert effectiveness["example_id"] == "example_test_001"
        assert effectiveness["total_uses"] == 0
        assert effectiveness["successful_uses"] == 0
        assert effectiveness["success_rate"] == 0.0
        assert effectiveness["effectiveness_score"] == 0.0

    def test_calculate_example_effectiveness_perfect_success(self, analyzer):
        """Test effectiveness with 100% success rate"""
        usage_logs = [
            {"run_id": "r1", "example_ids": ["ex1"], "output_quality": "good"},
            {"run_id": "r2", "example_ids": ["ex1"], "output_quality": "good"},
            {"run_id": "r3", "example_ids": ["ex1"], "output_quality": "good"},
        ]

        effectiveness = analyzer.calculate_example_effectiveness("ex1", usage_logs)

        assert effectiveness["total_uses"] == 3
        assert effectiveness["successful_uses"] == 3
        assert effectiveness["success_rate"] == 1.0
        # Score = 1.0 * (0.7 + 0.3 * min(3/10, 1)) = 1.0 * (0.7 + 0.09) = 0.79
        assert effectiveness["effectiveness_score"] == pytest.approx(0.79, rel=0.01)

    def test_calculate_example_effectiveness_partial_success(self, analyzer):
        """Test effectiveness with partial success rate"""
        usage_logs = [
            {"run_id": "r1", "example_ids": ["ex1"], "output_quality": "good"},
            {"run_id": "r2", "example_ids": ["ex1"], "output_quality": "needs_work"},
            {"run_id": "r3", "example_ids": ["ex1"], "output_quality": "failed"},
            {"run_id": "r4", "example_ids": ["ex1"], "output_quality": "good"},
        ]

        effectiveness = analyzer.calculate_example_effectiveness("ex1", usage_logs)

        assert effectiveness["total_uses"] == 4
        assert effectiveness["successful_uses"] == 2
        assert effectiveness["success_rate"] == 0.5
        # Score = 0.5 * (0.7 + 0.3 * min(4/10, 1)) = 0.5 * (0.7 + 0.12) = 0.41
        assert effectiveness["effectiveness_score"] == pytest.approx(0.41, rel=0.01)

    def test_calculate_example_effectiveness_high_frequency_boost(self, analyzer):
        """Test that high usage frequency boosts effectiveness score"""
        usage_logs = [
            {"run_id": f"r{i}", "example_ids": ["ex1"], "output_quality": "good"}
            for i in range(15)  # 15 uses
        ]

        effectiveness = analyzer.calculate_example_effectiveness("ex1", usage_logs)

        assert effectiveness["total_uses"] == 15
        assert effectiveness["usage_frequency_weight"] == 1.0  # maxed out at 10+ uses
        # Score = 1.0 * (0.7 + 0.3 * 1.0) = 1.0
        assert effectiveness["effectiveness_score"] == 1.0

    def test_get_top_performers_empty_stage(self, analyzer, temp_storage):
        """Test top performers for empty stage"""
        usage_logs = []

        top_performers = analyzer.get_top_performers(
            stage=1,
            usage_logs=usage_logs,
            top_n=5
        )

        assert len(top_performers) == 0

    def test_get_top_performers_with_examples(self, analyzer, temp_storage):
        """Test top performers with real examples"""
        # Create test examples
        stage_dir = temp_storage / "stage_1"

        for i, (example_id, success_count) in enumerate([
            ("example_high", 8),
            ("example_med", 5),
            ("example_low", 2)
        ]):
            example_file = stage_dir / f"{example_id}.json"
            example_file.write_text(json.dumps({
                "id": example_id,
                "quality_score": "good"
            }))

        # Create usage logs
        usage_logs = []
        for i in range(8):
            usage_logs.append({"run_id": f"r{i}", "example_ids": ["example_high"], "output_quality": "good"})
        for i in range(5):
            usage_logs.append({"run_id": f"r{i+8}", "example_ids": ["example_med"], "output_quality": "good"})
        for i in range(2):
            usage_logs.append({"run_id": f"r{i+13}", "example_ids": ["example_low"], "output_quality": "good"})

        top_performers = analyzer.get_top_performers(
            stage=1,
            usage_logs=usage_logs,
            top_n=5
        )

        # Verify sorting by effectiveness
        assert len(top_performers) == 3
        assert top_performers[0]["example_id"] == "example_high"
        assert top_performers[1]["example_id"] == "example_med"
        assert top_performers[2]["example_id"] == "example_low"

    def test_generate_insights_no_examples(self, analyzer):
        """Test insights generation with no examples"""
        usage_logs = []

        insights = analyzer.generate_insights(stage=1, usage_logs=usage_logs)

        assert insights["stage"] == 1
        assert insights["total_examples"] == 0
        assert "No examples found" in insights["insights"][0]

    def test_generate_insights_strong_examples(self, analyzer, temp_storage):
        """Test insights with strong performing examples"""
        # Create high-quality examples
        stage_dir = temp_storage / "stage_1"

        for i in range(5):
            example_file = stage_dir / f"example_{i}.json"
            example_file.write_text(json.dumps({
                "id": f"example_{i}",
                "quality_score": "good"
            }))

        # High success rate usage logs
        usage_logs = []
        for i in range(5):
            for j in range(10):
                usage_logs.append({
                    "run_id": f"r{i}_{j}",
                    "example_ids": [f"example_{i}"],
                    "output_quality": "good"  # 100% success
                })

        insights = analyzer.generate_insights(stage=1, usage_logs=usage_logs)

        assert insights["stage"] == 1
        assert insights["avg_success_rate"] > 0.8
        assert any("strong examples" in insight for insight in insights["insights"])

    def test_generate_insights_weak_examples(self, analyzer, temp_storage):
        """Test insights with poor performing examples"""
        stage_dir = temp_storage / "stage_1"

        for i in range(3):
            example_file = stage_dir / f"example_{i}.json"
            example_file.write_text(json.dumps({
                "id": f"example_{i}",
                "quality_score": "needs_work"
            }))

        # Low success rate usage logs
        usage_logs = []
        for i in range(3):
            for j in range(10):
                quality = "good" if j < 3 else "failed"  # 30% success rate
                usage_logs.append({
                    "run_id": f"r{i}_{j}",
                    "example_ids": [f"example_{i}"],
                    "output_quality": quality
                })

        insights = analyzer.generate_insights(stage=1, usage_logs=usage_logs)

        assert insights["avg_success_rate"] < 0.5
        assert any("need improvement" in insight for insight in insights["insights"])

    def test_generate_insights_underutilized_examples(self, analyzer, temp_storage):
        """Test insights identify underutilized high-performers"""
        stage_dir = temp_storage / "stage_1"

        # Create 1 high-quality example with low usage
        example_file = stage_dir / "example_hidden_gem.json"
        example_file.write_text(json.dumps({
            "id": "example_hidden_gem",
            "quality_score": "good"
        }))

        # Low usage but high success
        usage_logs = [
            {"run_id": "r1", "example_ids": ["example_hidden_gem"], "output_quality": "good"},
            {"run_id": "r2", "example_ids": ["example_hidden_gem"], "output_quality": "good"},
        ]

        insights = analyzer.generate_insights(stage=1, usage_logs=usage_logs)

        # Should identify underutilized example
        assert any("underutilized" in insight for insight in insights["insights"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
