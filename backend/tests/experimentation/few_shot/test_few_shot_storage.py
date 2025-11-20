"""
Tests for Few-Shot Example Storage (Story 11.3a)

Tests the FileSystemExampleStorage class for saving, loading, and validating
few-shot learning examples.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Import the storage class
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "experimentation"))

from few_shot_manager import FileSystemExampleStorage, save_good_example_from_gradio


@pytest.fixture
def temp_storage_dir():
    """Create temporary storage directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def storage(temp_storage_dir):
    """Create FileSystemExampleStorage instance with temp directory"""
    return FileSystemExampleStorage(storage_path=temp_storage_dir)


@pytest.fixture
def sample_brand_context():
    """Sample brand context for testing"""
    return {
        "brand_name": "Test Brand",
        "industry": "Food & Beverage",
        "country": "Canada",
        "product_portfolio": ["Milk", "Cheese", "Yogurt"]
    }


@pytest.fixture
def sample_input_data():
    """Sample stage input data"""
    return {
        "report_text": "Sample trend report text...",
        "previous_stage_output": {}
    }


@pytest.fixture
def sample_output_data():
    """Sample stage output data"""
    return {
        "trends": [
            {
                "trend_id": "test_001",
                "name": "Test Trend",
                "lifecycle_stage": "EMERGING"
            }
        ]
    }


class TestFileSystemExampleStorage:
    """Tests for FileSystemExampleStorage class"""

    def test_initialization(self, storage, temp_storage_dir):
        """Test storage initialization creates directory"""
        assert storage.storage_path.exists()
        assert str(storage.storage_path) == temp_storage_dir

    def test_generate_example_id(self, storage):
        """Test unique example ID generation"""
        stage = 1
        brand_name = "Test Brand"

        # Generate two IDs
        id1 = storage.generate_example_id(stage, brand_name)
        id2 = storage.generate_example_id(stage, brand_name)

        # Should follow format: example_{timestamp}_{hash}
        assert id1.startswith("example_")
        assert id2.startswith("example_")

        # Should be unique (even if generated quickly)
        assert id1 != id2

    def test_save_example_success(
        self,
        storage,
        sample_brand_context,
        sample_input_data,
        sample_output_data
    ):
        """Test successful example save"""
        stage = 1
        run_id = "test_run_001"
        prompt = "Test prompt template"

        success, message = storage.save_example(
            stage=stage,
            run_id=run_id,
            brand_context=sample_brand_context,
            input_data=sample_input_data,
            output_data=sample_output_data,
            prompt_used=prompt,
            quality_score="good"
        )

        # Should succeed
        assert success is True
        assert "Example saved:" in message

        # Should create stage directory
        stage_dir = storage.storage_path / f"stage_{stage}"
        assert stage_dir.exists()

        # Should create example file
        example_files = list(stage_dir.glob("example_*.json"))
        assert len(example_files) == 1

        # Verify file contents
        with open(example_files[0], 'r') as f:
            saved_data = json.load(f)

        assert saved_data["stage"] == stage
        assert saved_data["quality_score"] == "good"
        assert saved_data["brand_context"] == sample_brand_context
        assert saved_data["input"] == sample_input_data
        assert saved_data["output"] == sample_output_data
        assert saved_data["prompt_used"] == prompt

    def test_save_example_validation(self, storage, sample_input_data, sample_output_data):
        """Test validation catches invalid brand context"""
        # Missing required fields
        invalid_brand_context = {
            "brand_name": "Test Brand"
            # Missing: industry, country, product_portfolio
        }

        success, message = storage.save_example(
            stage=1,
            run_id="test_run",
            brand_context=invalid_brand_context,
            input_data=sample_input_data,
            output_data=sample_output_data,
            prompt_used="Test prompt",
            quality_score="good"
        )

        # Should fail validation
        assert success is False
        assert "Validation error" in message or "Failed to save" in message

    def test_metadata_update(
        self,
        storage,
        sample_brand_context,
        sample_input_data,
        sample_output_data
    ):
        """Test metadata.json is updated correctly"""
        stage = 1

        # Save first example
        storage.save_example(
            stage=stage,
            run_id="run_001",
            brand_context=sample_brand_context,
            input_data=sample_input_data,
            output_data=sample_output_data,
            prompt_used="Test prompt",
            quality_score="good"
        )

        # Check metadata
        metadata = storage.get_stage_metadata(stage)
        assert metadata is not None
        assert metadata["stage"] == stage
        assert metadata["total_examples"] == 1
        assert metadata["usage_stats"]["examples_by_quality"]["good"] == 1
        assert metadata["last_updated"] is not None

        # Save second example
        storage.save_example(
            stage=stage,
            run_id="run_002",
            brand_context=sample_brand_context,
            input_data=sample_input_data,
            output_data=sample_output_data,
            prompt_used="Test prompt",
            quality_score="needs_work"
        )

        # Check updated metadata
        metadata = storage.get_stage_metadata(stage)
        assert metadata["total_examples"] == 2
        assert metadata["usage_stats"]["examples_by_quality"]["good"] == 1
        assert metadata["usage_stats"]["examples_by_quality"]["needs_work"] == 1

    def test_load_examples(
        self,
        storage,
        sample_brand_context,
        sample_input_data,
        sample_output_data
    ):
        """Test loading examples from stage directory"""
        stage = 1

        # Save multiple examples
        for i in range(3):
            storage.save_example(
                stage=stage,
                run_id=f"run_{i:03d}",
                brand_context=sample_brand_context,
                input_data=sample_input_data,
                output_data=sample_output_data,
                prompt_used="Test prompt",
                quality_score="good"
            )

        # Load examples
        examples = storage.load_examples(stage)

        # Should load all examples
        assert len(examples) == 3

        # Each should have required fields
        for example in examples:
            assert "id" in example
            assert "stage" in example
            assert "brand_context" in example
            assert "input" in example
            assert "output" in example
            assert "prompt_used" in example

    def test_load_examples_nonexistent_stage(self, storage):
        """Test loading from non-existent stage returns empty list"""
        examples = storage.load_examples(99)
        assert examples == []

    def test_error_handling_graceful_failure(self, storage):
        """Test error handling doesn't break pipeline"""
        # Pass invalid data that will cause an error
        success, message = storage.save_example(
            stage=1,
            run_id="test",
            brand_context=None,  # Invalid
            input_data={},
            output_data={},
            prompt_used="",
            quality_score="good"
        )

        # Should return False but not raise exception
        assert success is False
        assert "Failed to save" in message or "error" in message.lower()


class TestGradioIntegration:
    """Tests for Gradio integration helper function"""

    def test_save_good_example_from_gradio(
        self,
        temp_storage_dir,
        sample_brand_context,
        sample_input_data,
        sample_output_data
    ):
        """Test helper function for Gradio integration"""
        success, message = save_good_example_from_gradio(
            stage=1,
            run_id="gradio_test_001",
            brand_context=sample_brand_context,
            input_data=sample_input_data,
            output_data=sample_output_data,
            prompt_used="Test prompt",
            storage_path=temp_storage_dir
        )

        # Should succeed
        assert success is True
        assert "Example saved:" in message

        # Verify file was created
        stage_dir = Path(temp_storage_dir) / "stage_1"
        example_files = list(stage_dir.glob("example_*.json"))
        assert len(example_files) == 1


class TestMultipleStages:
    """Tests for handling multiple pipeline stages"""

    def test_save_examples_across_stages(
        self,
        storage,
        sample_brand_context,
        sample_input_data,
        sample_output_data
    ):
        """Test saving examples to different stages"""
        # Save to stages 0-6
        for stage in range(7):
            success, _ = storage.save_example(
                stage=stage,
                run_id=f"run_stage_{stage}",
                brand_context=sample_brand_context,
                input_data=sample_input_data,
                output_data=sample_output_data,
                prompt_used=f"Stage {stage} prompt",
                quality_score="good"
            )
            assert success is True

        # Verify all stage directories created
        for stage in range(7):
            stage_dir = storage.storage_path / f"stage_{stage}"
            assert stage_dir.exists()

            # Verify metadata exists
            metadata = storage.get_stage_metadata(stage)
            assert metadata is not None
            assert metadata["total_examples"] == 1

    def test_stage_isolation(
        self,
        storage,
        sample_brand_context,
        sample_input_data,
        sample_output_data
    ):
        """Test examples saved to one stage don't affect others"""
        # Save to stage 1
        storage.save_example(
            stage=1,
            run_id="run_001",
            brand_context=sample_brand_context,
            input_data=sample_input_data,
            output_data=sample_output_data,
            prompt_used="Test prompt",
            quality_score="good"
        )

        # Stage 1 should have examples
        stage1_examples = storage.load_examples(1)
        assert len(stage1_examples) == 1

        # Stage 2 should be empty
        stage2_examples = storage.load_examples(2)
        assert len(stage2_examples) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
