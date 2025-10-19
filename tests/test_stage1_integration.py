#!/usr/bin/env python3
"""
Integration tests for Stage 1 JSON output and parameter flow.
Tests Story 3.2 integration requirements.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.stages.stage1_input_processing import Stage1Chain


def test_selected_track_parameter_flows_to_save_output():
    """Test 3.2-INT-002: Verify selected_track parameter flows to save_output()."""
    # Create a minimal Stage1Chain instance without full initialization
    # We only need to test save_output(), not the LLM chain
    stage1_chain = Mock(spec=Stage1Chain)
    stage1_chain.save_output = Stage1Chain.save_output.__get__(stage1_chain)
    stage1_chain._parse_tracks = Stage1Chain._parse_tracks.__get__(stage1_chain)
    stage1_chain._empty_track = Stage1Chain._empty_track.__get__(stage1_chain)

    # Use temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        # Sample LLM output with 2 tracks
        sample_output = """## Track 1: Customer-Centric Innovation

Organizations that excel in customer-centric innovation prioritize deep user research and co-creation. They build products based on actual needs rather than assumptions.

## Track 2: Technology-Driven Disruption

Technology leaders leverage emerging technologies like AI and blockchain to create fundamentally new value propositions and business models."""

        # Test with selected_track=1
        stage1_chain.save_output(sample_output, output_dir, selected_track=1)

        json_file_1 = output_dir / "stage1" / "inspirations.json"
        assert json_file_1.exists(), "JSON file should be created"

        with open(json_file_1, 'r') as f:
            data_1 = json.load(f)

        assert data_1["selected_track"] == 1, "selected_track should be 1"
        assert isinstance(data_1["selected_track"], int), "selected_track must be integer"

        # Test with selected_track=2
        with tempfile.TemporaryDirectory() as tmpdir2:
            output_dir_2 = Path(tmpdir2)
            stage1_chain.save_output(sample_output, output_dir_2, selected_track=2)

            json_file_2 = output_dir_2 / "stage1" / "inspirations.json"
            assert json_file_2.exists(), "JSON file should be created"

            with open(json_file_2, 'r') as f:
                data_2 = json.load(f)

            assert data_2["selected_track"] == 2, "selected_track should be 2"
            assert isinstance(data_2["selected_track"], int), "selected_track must be integer"

    print("✓ test_selected_track_parameter_flows_to_save_output passed")


def test_default_selected_track():
    """Test that selected_track defaults to 1 when not provided."""
    stage1_chain = Mock(spec=Stage1Chain)
    stage1_chain.save_output = Stage1Chain.save_output.__get__(stage1_chain)
    stage1_chain._parse_tracks = Stage1Chain._parse_tracks.__get__(stage1_chain)
    stage1_chain._empty_track = Stage1Chain._empty_track.__get__(stage1_chain)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        sample_output = """## Track 1: Innovation Title
Track 1 content.

## Track 2: Second Track
Track 2 content."""

        # Call without selected_track parameter (should default to 1)
        stage1_chain.save_output(sample_output, output_dir)

        json_file = output_dir / "stage1" / "inspirations.json"
        with open(json_file, 'r') as f:
            data = json.load(f)

        assert data["selected_track"] == 1, "selected_track should default to 1"
        assert isinstance(data["selected_track"], int)

    print("✓ test_default_selected_track passed")


def test_json_file_structure_complete():
    """Test that JSON file has all required fields."""
    stage1_chain = Mock(spec=Stage1Chain)
    stage1_chain.save_output = Stage1Chain.save_output.__get__(stage1_chain)
    stage1_chain._parse_tracks = Stage1Chain._parse_tracks.__get__(stage1_chain)
    stage1_chain._empty_track = Stage1Chain._empty_track.__get__(stage1_chain)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        sample_output = """## Track 1: First Innovation
First track summary.

## Track 2: Second Innovation
Second track summary."""

        stage1_chain.save_output(sample_output, output_dir, selected_track=1)

        json_file = output_dir / "stage1" / "inspirations.json"
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Validate all required fields exist
        required_fields = ["selected_track", "track_1", "track_2", "completed_at"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Validate track structure
        for track_key in ["track_1", "track_2"]:
            track = data[track_key]
            assert "title" in track, f"{track_key} missing title"
            assert "summary" in track, f"{track_key} missing summary"
            assert "icon_url" in track, f"{track_key} missing icon_url"
            assert isinstance(track["title"], str)
            assert isinstance(track["summary"], str)
            assert isinstance(track["icon_url"], str)

    print("✓ test_json_file_structure_complete passed")


def test_markdown_file_also_created():
    """Test that both markdown and JSON files are created."""
    stage1_chain = Mock(spec=Stage1Chain)
    stage1_chain.save_output = Stage1Chain.save_output.__get__(stage1_chain)
    stage1_chain._parse_tracks = Stage1Chain._parse_tracks.__get__(stage1_chain)
    stage1_chain._empty_track = Stage1Chain._empty_track.__get__(stage1_chain)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        sample_output = """## Track 1: Innovation
Content here."""

        stage1_chain.save_output(sample_output, output_dir, selected_track=1)

        # Check both files exist
        markdown_file = output_dir / "stage1" / "inspiration-analysis.md"
        json_file = output_dir / "stage1" / "inspirations.json"

        assert markdown_file.exists(), "Markdown file should be created"
        assert json_file.exists(), "JSON file should be created"

        # Verify markdown content
        markdown_content = markdown_file.read_text()
        assert "Track 1" in markdown_content

    print("✓ test_markdown_file_also_created passed")


if __name__ == "__main__":
    print("Running Stage 1 Integration Tests\n")

    test_selected_track_parameter_flows_to_save_output()
    test_default_selected_track()
    test_json_file_structure_complete()
    test_markdown_file_also_created()

    print("\n✅ All integration tests passed!")
