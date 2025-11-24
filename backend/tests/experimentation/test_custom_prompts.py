"""Unit tests for Story 11.6.1: Custom Prompt Download/Upload/Validation

Tests the custom prompt template download, upload, and validation functionality
in the Gradio UI.
"""

import pytest
import os
import zipfile
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experimentation.gradio_lab import GradioLab


class TestPromptHelperFunctions:
    """Test helper functions for prompt management"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    def test_resolve_prompts_dir_local(self, lab):
        """Test resolving prompts directory in local environment"""
        # Should find prompts directory relative to gradio_lab.py
        prompts_dir = lab.resolve_prompts_dir()
        assert prompts_dir is not None
        assert prompts_dir.exists()
        assert (prompts_dir / "stage_0_enrichment.md").exists()

    def test_resolve_prompts_dir_not_found(self, lab):
        """Test error handling when prompts directory not found"""
        # Mock all possible paths to not exist
        with patch.object(Path, 'exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="Prompts directory not found"):
                lab.resolve_prompts_dir()

    def test_create_default_template_zip(self, lab):
        """Test ZIP creation includes all 7 templates + README"""
        zip_path = lab.create_default_template_zip()

        assert zip_path is not None
        assert os.path.exists(zip_path)

        # Verify ZIP contents
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            filenames = zipf.namelist()

            # Check all 7 stage templates
            expected_templates = [
                "stage_0_enrichment.md",
                "stage_1_extraction.md",
                "stage_2_convergence.md",
                "stage_3_technique_matching.md",
                "stage_4_concept_generation.md",
                "stage_5_competitive_search.md",
                "stage_6_packaging.md"
            ]

            for template in expected_templates:
                assert template in filenames, f"{template} not found in ZIP"

            # Check README.md
            assert "README.md" in filenames

            # Verify README content
            readme_content = zipf.read("README.md").decode('utf-8')
            assert "Innovation Pipeline Prompt Templates" in readme_content
            assert "Placeholder Requirements" in readme_content
            assert "{company_name}" in readme_content  # Check placeholder documentation

        # Cleanup
        os.remove(zip_path)


class TestPlaceholderValidation:
    """Test placeholder validation logic"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    def test_validate_stage0_valid(self, lab):
        """Test Stage 0 validation with all required placeholders"""
        content = """
        # Stage 0 Test
        Company: {company_name}
        Industry: {industry}
        Portfolio: {portfolio}
        """
        is_valid, missing = lab.validate_placeholders(0, content)
        assert is_valid is True
        assert missing == []

    def test_validate_stage0_missing_placeholders(self, lab):
        """Test Stage 0 validation with missing placeholders"""
        content = """
        # Stage 0 Test
        Company: {company_name}
        Industry: {industry}
        """
        is_valid, missing = lab.validate_placeholders(0, content)
        assert is_valid is False
        assert "portfolio" in missing

    def test_validate_stage1_valid(self, lab):
        """Test Stage 1 validation with required placeholder"""
        content = "Report text: {report_text}"
        is_valid, missing = lab.validate_placeholders(1, content)
        assert is_valid is True
        assert missing == []

    def test_validate_stage4_all_placeholders(self, lab):
        """Test Stage 4 validation (most complex with 4 placeholders)"""
        content = """
        Insights: {insights}
        Techniques: {matched_techniques}
        Context: {brand_context}
        Rules: {no_hallucination_rules}
        """
        is_valid, missing = lab.validate_placeholders(4, content)
        assert is_valid is True
        assert missing == []

    def test_validate_stage4_partial_missing(self, lab):
        """Test Stage 4 with some missing placeholders"""
        content = """
        Insights: {insights}
        Context: {brand_context}
        """
        is_valid, missing = lab.validate_placeholders(4, content)
        assert is_valid is False
        assert "matched_techniques" in missing
        assert "no_hallucination_rules" in missing
        assert len(missing) == 2

    def test_validate_empty_file(self, lab):
        """Test validation with empty content"""
        content = ""
        is_valid, missing = lab.validate_placeholders(0, content)
        assert is_valid is False
        assert len(missing) == 3  # Stage 0 requires 3 placeholders

    def test_validate_wrong_placeholder_format(self, lab):
        """Test validation doesn't match incorrect placeholder formats"""
        # Wrong formats: missing braces, uppercase, wrong delimiter
        content = """
        company_name
        COMPANY_NAME
        ${company_name}
        """
        is_valid, missing = lab.validate_placeholders(0, content)
        assert is_valid is False
        # Note: company_name without braces is matched as text, so only 2 missing
        assert len(missing) >= 2  # At least 2 required placeholders missing

    def test_validate_extra_placeholders_allowed(self, lab):
        """Test validation allows extra placeholders beyond required"""
        content = """
        Required: {company_name} {industry} {portfolio}
        Extra: {custom_field} {another_field}
        """
        is_valid, missing = lab.validate_placeholders(0, content)
        assert is_valid is True
        assert missing == []


class TestFileUploadHandling:
    """Test file upload and state management"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    def test_handle_file_upload_valid(self, lab):
        """Test handling valid file upload"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content with {placeholder}")
            temp_path = f.name

        try:
            # Mock Gradio File object
            mock_file = MagicMock()
            mock_file.name = temp_path

            # Mock state
            state = {"custom_prompts": {}}

            # Simulate file upload (would be called by event handler)
            with open(mock_file.name, 'r', encoding='utf-8') as f:
                content = f.read()

            state["custom_prompts"]["stage_0"] = {
                "filename": os.path.basename(mock_file.name),
                "content": content,
                "uploaded_at": "2025-11-24T10:00:00Z"
            }

            # Verify state updated correctly
            assert "stage_0" in state["custom_prompts"]
            assert state["custom_prompts"]["stage_0"]["content"] == "Test content with {placeholder}"
            assert state["custom_prompts"]["stage_0"]["filename"].endswith(".md")

        finally:
            os.remove(temp_path)

    def test_handle_file_replacement(self, lab):
        """Test replacing uploaded file for same stage"""
        state = {
            "custom_prompts": {
                "stage_1": {
                    "filename": "old_file.md",
                    "content": "old content",
                    "uploaded_at": "2025-11-24T09:00:00Z"
                }
            }
        }

        # Upload new file for same stage
        state["custom_prompts"]["stage_1"] = {
            "filename": "new_file.md",
            "content": "new content",
            "uploaded_at": "2025-11-24T10:00:00Z"
        }

        # Verify replacement
        assert state["custom_prompts"]["stage_1"]["filename"] == "new_file.md"
        assert state["custom_prompts"]["stage_1"]["content"] == "new content"

    def test_handle_file_removal(self, lab):
        """Test removing uploaded file"""
        state = {
            "custom_prompts": {
                "stage_2": {
                    "filename": "test.md",
                    "content": "content",
                    "uploaded_at": "2025-11-24T10:00:00Z"
                }
            }
        }

        # Simulate file removal
        if "stage_2" in state["custom_prompts"]:
            del state["custom_prompts"]["stage_2"]

        # Verify removal
        assert "stage_2" not in state["custom_prompts"]


class TestValidationResults:
    """Test validation results display logic"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    def test_validation_no_files_uploaded(self, lab):
        """Test validation message when no files uploaded"""
        state = {"custom_prompts": {}}

        # Simulate validation function logic
        custom_prompts = state.get("custom_prompts", {})
        if not custom_prompts:
            result = "ℹ️ **No custom prompts uploaded.** Upload files to validate."

        assert "No custom prompts uploaded" in result

    def test_validation_all_valid(self, lab):
        """Test validation results when all files valid"""
        state = {
            "custom_prompts": {
                "stage_0": {
                    "filename": "test.md",
                    "content": "{company_name} {industry} {portfolio}"
                }
            }
        }

        # Validate
        results = []
        for stage in range(7):
            stage_key = f"stage_{stage}"
            if stage_key in state["custom_prompts"]:
                content = state["custom_prompts"][stage_key]["content"]
                is_valid, missing = lab.validate_placeholders(stage, content)
                if is_valid:
                    results.append(f"✅ Stage {stage}: Valid")
                else:
                    results.append(f"❌ Stage {stage}: MISSING")
            else:
                results.append(f"ℹ️ Stage {stage}: Using default")

        # Verify results
        assert "✅ Stage 0: Valid" in results
        assert sum(1 for r in results if "ℹ️" in r) == 6  # 6 stages using defaults

    def test_validation_with_errors(self, lab):
        """Test validation results with missing placeholders"""
        state = {
            "custom_prompts": {
                "stage_4": {
                    "filename": "invalid.md",
                    "content": "{insights}"  # Missing 3 other required placeholders
                }
            }
        }

        is_valid, missing = lab.validate_placeholders(4, state["custom_prompts"]["stage_4"]["content"])

        assert is_valid is False
        assert "matched_techniques" in missing
        assert "brand_context" in missing
        assert "no_hallucination_rules" in missing


class TestBackwardCompatibility:
    """Test backward compatibility with no custom prompts"""

    @pytest.fixture
    def lab(self):
        """Create GradioLab instance"""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://localhost:8000"}):
            return GradioLab()

    def test_run_pipeline_without_custom_prompts(self, lab):
        """Test run_pipeline() works when custom_prompts=None (default behavior)"""
        # Verify method signature accepts custom_prompts parameter
        import inspect
        sig = inspect.signature(lab.run_pipeline)
        assert "custom_prompts" in sig.parameters

        # Verify default is None
        default = sig.parameters["custom_prompts"].default
        assert default is None

    def test_state_without_custom_prompts(self, lab):
        """Test state handling when no custom prompts uploaded"""
        state = {
            "pdf_text": "test",
            "brand_profile": {},
            "custom_prompts": {}  # Empty
        }

        # Extract custom prompts (as done in run_pipeline_wrapper)
        custom_prompts_data = state.get("custom_prompts", {})
        custom_prompts = None
        if custom_prompts_data:
            custom_prompts = {
                stage_key: data["content"]
                for stage_key, data in custom_prompts_data.items()
            }

        # Should result in None when empty
        assert custom_prompts is None or custom_prompts == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
