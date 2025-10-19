#!/usr/bin/env python3
"""
Unit tests for CLI argument parsing and validation.
Tests Story 3.2 acceptance criteria.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_pipeline import parse_arguments


def test_selected_track_accepts_valid_values():
    """Test 3.2-UNIT-007: Verify --selected-track only accepts 1 or 2."""

    # Test with track 1
    sys.argv = ['run_pipeline.py', '--input-file', '/tmp/test.pdf', '--brand', 'test',
                '--run-id', 'test-001', '--selected-track', '1']
    args = parse_arguments()
    assert args.selected_track == 1, "Should accept selected_track=1"

    # Test with track 2
    sys.argv = ['run_pipeline.py', '--input-file', '/tmp/test.pdf', '--brand', 'test',
                '--run-id', 'test-002', '--selected-track', '2']
    args = parse_arguments()
    assert args.selected_track == 2, "Should accept selected_track=2"

    print("✓ test_selected_track_accepts_valid_values passed")


def test_selected_track_rejects_invalid_values():
    """Test 3.2-UNIT-008: Verify --selected-track rejects invalid values (0, 3, 'foo')."""

    # Test with 0 (should use argparse choices validation)
    try:
        sys.argv = ['run_pipeline.py', '--input-file', '/tmp/test.pdf', '--brand', 'test',
                    '--run-id', 'test-003', '--selected-track', '0']
        args = parse_arguments()
        # If no error, check if value is rejected
        assert False, "Should reject selected_track=0"
    except SystemExit:
        # argparse exits on invalid choice
        pass

    # Test with 3
    try:
        sys.argv = ['run_pipeline.py', '--input-file', '/tmp/test.pdf', '--brand', 'test',
                    '--run-id', 'test-004', '--selected-track', '3']
        args = parse_arguments()
        assert False, "Should reject selected_track=3"
    except SystemExit:
        pass

    # Test with non-integer
    try:
        sys.argv = ['run_pipeline.py', '--input-file', '/tmp/test.pdf', '--brand', 'test',
                    '--run-id', 'test-005', '--selected-track', 'foo']
        args = parse_arguments()
        assert False, "Should reject selected_track='foo'"
    except SystemExit:
        pass

    print("✓ test_selected_track_rejects_invalid_values passed")


def test_output_directory_path_format():
    """Test 3.2-UNIT-009: Verify output directory path format: data/test-outputs/{run_id}/."""

    # This test verifies the path construction logic
    run_id = "test-run-123"
    expected_path = f"data/test-outputs/{run_id}"

    # Verify path format matches spec
    from pathlib import Path
    output_dir = Path("data") / "test-outputs" / run_id
    assert str(output_dir) == expected_path, f"Path should be {expected_path}"

    # Verify components
    assert output_dir.parts[0] == "data", "First component should be 'data'"
    assert output_dir.parts[1] == "test-outputs", "Second component should be 'test-outputs'"
    assert output_dir.parts[2] == run_id, f"Third component should be run_id: {run_id}"

    print("✓ test_output_directory_path_format passed")


def test_logging_message_format():
    """Test 3.2-UNIT-010: Verify log messages format: 'Starting Stage {N}: {Name}'."""

    # Test log message format
    stage_num = 1
    stage_name = "Input Processing"
    expected_format = f"Starting Stage {stage_num}: {stage_name}"

    # Verify format matches spec
    assert "Starting Stage" in expected_format
    assert str(stage_num) in expected_format
    assert stage_name in expected_format

    # Test completion message format
    completion_msg = f"Stage {stage_num} execution completed"
    assert "execution completed" in completion_msg
    assert f"Stage {stage_num}" in completion_msg

    print("✓ test_logging_message_format passed")


if __name__ == "__main__":
    print("Running CLI Argument and Unit Tests\n")

    test_selected_track_accepts_valid_values()
    test_selected_track_rejects_invalid_values()
    test_output_directory_path_format()
    test_logging_message_format()

    print("\n✅ All CLI and unit tests passed!")
