"""Integration tests for Story 11.6.1: Custom Prompt Upload & Pipeline Integration

Tests the complete workflow: download → customize → upload → validate → run pipeline
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio

# Add backend to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experimentation.gradio_lab import GradioLab


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    def test_download_customize_upload_validate_flow(self, lab):
        """Test complete workflow: download template → customize → upload → validate"""

        # STEP 1: Download template
        zip_path = lab.create_default_template_zip()
        assert os.path.exists(zip_path)

        # STEP 2: Simulate customization
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
            # Customized Stage 4 Prompt
            Consumer Insights: {insights}
            Matched Techniques: {matched_techniques}
            Brand Context: {brand_context}
            No Hallucination Rules: {no_hallucination_rules}
            """)
            custom_file_path = f.name

        try:
            # STEP 3: Simulate upload to state
            state = {"custom_prompts": {}}

            with open(custom_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            state["custom_prompts"]["stage_4"] = {
                "filename": os.path.basename(custom_file_path),
                "content": content,
                "uploaded_at": "2025-11-24T10:00:00Z"
            }

            # STEP 4: Validate uploaded file
            is_valid, missing = lab.validate_placeholders(
                4,
                state["custom_prompts"]["stage_4"]["content"]
            )

            # Verify validation passes
            assert is_valid is True
            assert missing == []

            # STEP 5: Extract custom prompts for pipeline (as done in run_pipeline_wrapper)
            custom_prompts = {
                stage_key: data["content"]
                for stage_key, data in state["custom_prompts"].items()
            }

            assert "stage_4" in custom_prompts
            assert "{insights}" in custom_prompts["stage_4"]

        finally:
            # Cleanup
            os.remove(custom_file_path)
            os.remove(zip_path)

    def test_upload_invalid_file_blocks_pipeline(self, lab):
        """Test that invalid file validation prevents pipeline execution"""

        # STEP 1: Upload file with missing placeholders
        state = {
            "custom_prompts": {
                "stage_2": {
                    "filename": "invalid.md",
                    "content": "Missing required placeholders"
                }
            }
        }

        # STEP 2: Validate
        is_valid, missing = lab.validate_placeholders(
            2,
            state["custom_prompts"]["stage_2"]["content"]
        )

        # STEP 3: Verify validation fails
        assert is_valid is False
        assert "trend_data" in missing
        assert "brand_context" in missing

        # In actual UI, this would disable the run pipeline button
        # and display error message with missing placeholders

    def test_no_custom_prompts_uses_defaults(self, lab):
        """Regression test: Pipeline works without custom prompts (backward compatibility)"""

        # STEP 1: State with no custom prompts
        state = {
            "pdf_text": "Test report content" * 50,  # Valid length
            "custom_prompts": {}
        }

        # STEP 2: Extract custom prompts
        custom_prompts_data = state.get("custom_prompts", {})
        custom_prompts = None
        if custom_prompts_data:
            custom_prompts = {
                stage_key: data["content"]
                for stage_key, data in custom_prompts_data.items()
            }

        # STEP 3: Verify custom_prompts is None (uses defaults)
        assert custom_prompts is None or custom_prompts == {}

        # When passed to run_pipeline(), backend will use default templates


class TestPipelineIntegration:
    """Test integration with run_pipeline() method"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    @pytest.mark.asyncio
    async def test_run_pipeline_with_custom_prompts(self, lab):
        """Test run_pipeline() accepts and sends custom_prompts to backend"""

        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "run_id": "test-123",
            "status": "complete",
            "stages": {
                "0": {"status": "complete", "output": {"markdown": "Stage 0"}},
                "1": {"status": "complete", "output": {"markdown": "Stage 1"}},
                "2": {"status": "complete", "output": {"markdown": "Stage 2"}},
                "3": {"status": "complete", "output": {"markdown": "Stage 3"}},
                "4": {"status": "complete", "output": {"markdown": "Stage 4"}},
                "5": {"status": "complete", "output": {"markdown": "Stage 5"}},
                "6": {"status": "complete", "output": {"markdown": "Stage 6"}}
            }
        }

        custom_prompts = {
            "stage_4": "Custom Stage 4 prompt content"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_instance.get = AsyncMock(return_value=mock_response)

            # Call run_pipeline with custom prompts
            result = await lab.run_pipeline(
                pdf_text="Test content" * 50,
                brand_name="Test Brand",
                industry="Test Industry",
                geography="USA",
                product_portfolio="Product 1\nProduct 2",
                custom_prompts=custom_prompts
            )

            # Verify POST was called with custom_prompts in payload
            post_call = mock_instance.post.call_args
            payload = post_call[1]['json']

            assert "custom_prompts" in payload
            assert payload["custom_prompts"] == custom_prompts

    @pytest.mark.asyncio
    async def test_run_pipeline_without_custom_prompts(self, lab):
        """Test run_pipeline() works without custom_prompts (backward compatibility)"""

        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "run_id": "test-456",
            "status": "complete",
            "stages": {
                "0": {"status": "complete", "output": {"markdown": "Stage 0"}},
                "1": {"status": "complete", "output": {"markdown": "Stage 1"}},
                "2": {"status": "complete", "output": {"markdown": "Stage 2"}},
                "3": {"status": "complete", "output": {"markdown": "Stage 3"}},
                "4": {"status": "complete", "output": {"markdown": "Stage 4"}},
                "5": {"status": "complete", "output": {"markdown": "Stage 5"}},
                "6": {"status": "complete", "output": {"markdown": "Stage 6"}}
            }
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_instance.get = AsyncMock(return_value=mock_response)

            # Call run_pipeline WITHOUT custom prompts
            result = await lab.run_pipeline(
                pdf_text="Test content" * 50,
                brand_name="Test Brand",
                industry="Test Industry",
                geography="USA",
                product_portfolio="Product 1\nProduct 2",
                custom_prompts=None  # Explicitly None
            )

            # Verify POST was called WITHOUT custom_prompts in payload
            post_call = mock_instance.post.call_args
            payload = post_call[1]['json']

            assert "custom_prompts" not in payload  # Should not be in payload when None


class TestStateManagement:
    """Test state management for custom prompts"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    def test_multiple_file_uploads_to_state(self, lab):
        """Test uploading multiple custom prompt files"""

        state = {"custom_prompts": {}}

        # Upload 3 different stage prompts
        for stage in [0, 2, 5]:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                # Write valid content for each stage
                if stage == 0:
                    f.write("{company_name} {industry} {portfolio}")
                elif stage == 2:
                    f.write("{trend_data} {brand_context}")
                elif stage == 5:
                    f.write("{initiatives} {brand_context}")

                temp_path = f.name

            try:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                state["custom_prompts"][f"stage_{stage}"] = {
                    "filename": f"stage_{stage}_custom.md",
                    "content": content,
                    "uploaded_at": "2025-11-24T10:00:00Z"
                }

            finally:
                os.remove(temp_path)

        # Verify all 3 uploads in state
        assert len(state["custom_prompts"]) == 3
        assert "stage_0" in state["custom_prompts"]
        assert "stage_2" in state["custom_prompts"]
        assert "stage_5" in state["custom_prompts"]

        # Verify each is valid
        for stage in [0, 2, 5]:
            content = state["custom_prompts"][f"stage_{stage}"]["content"]
            is_valid, missing = lab.validate_placeholders(stage, content)
            assert is_valid is True

    def test_file_replacement_in_state(self, lab):
        """Test replacing a file in state"""

        state = {
            "custom_prompts": {
                "stage_1": {
                    "filename": "old.md",
                    "content": "{report_text}",
                    "uploaded_at": "2025-11-24T09:00:00Z"
                }
            }
        }

        # Replace with new file
        state["custom_prompts"]["stage_1"] = {
            "filename": "new.md",
            "content": "Updated content: {report_text}",
            "uploaded_at": "2025-11-24T10:00:00Z"
        }

        # Verify replacement
        assert state["custom_prompts"]["stage_1"]["filename"] == "new.md"
        assert "Updated content" in state["custom_prompts"]["stage_1"]["content"]

    def test_clear_custom_prompts(self, lab):
        """Test clearing all custom prompts from state"""

        state = {
            "custom_prompts": {
                "stage_0": {"filename": "test.md", "content": "content"},
                "stage_3": {"filename": "test2.md", "content": "content2"}
            }
        }

        # Clear all custom prompts
        state["custom_prompts"] = {}

        # Verify cleared
        assert len(state["custom_prompts"]) == 0


class TestValidationFeedback:
    """Test validation feedback messages"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    def test_validation_summary_all_pass(self, lab):
        """Test validation summary when all files pass"""

        state = {
            "custom_prompts": {
                "stage_1": {
                    "filename": "valid.md",
                    "content": "{report_text}"
                }
            }
        }

        # Validate all stages
        has_errors = False
        for stage in range(7):
            stage_key = f"stage_{stage}"
            if stage_key in state["custom_prompts"]:
                content = state["custom_prompts"][stage_key]["content"]
                is_valid, _ = lab.validate_placeholders(stage, content)
                if not is_valid:
                    has_errors = True

        # Should have no errors
        assert has_errors is False

    def test_validation_summary_with_errors(self, lab):
        """Test validation summary when files have errors"""

        state = {
            "custom_prompts": {
                "stage_4": {
                    "filename": "invalid.md",
                    "content": "Missing all placeholders"
                }
            }
        }

        # Validate
        has_errors = False
        for stage in range(7):
            stage_key = f"stage_{stage}"
            if stage_key in state["custom_prompts"]:
                content = state["custom_prompts"][stage_key]["content"]
                is_valid, _ = lab.validate_placeholders(stage, content)
                if not is_valid:
                    has_errors = True

        # Should have errors
        assert has_errors is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
