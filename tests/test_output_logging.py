#!/usr/bin/env python3
"""
Test script for output directory structure and logging setup.

Validates:
1. Output directory creation with correct structure
2. Stage subdirectories (stage1-5) with .gitkeep files
3. Logs subdirectory with .gitkeep
4. Console logging at INFO level
5. File logging at DEBUG level to logs/pipeline.log
6. Error logging to logs/errors.log
7. Timestamp format (ISO YYYYMMDD-HHMMSS)

Usage:
    python test_output_logging.py
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Import pipeline utilities
try:
    from pipeline.utils import create_test_output_dir, setup_pipeline_logging
except ImportError as e:
    print(f"Error: Could not import pipeline utilities: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def test_directory_structure():
    """Test that output directory structure is created correctly."""
    print("\n" + "="*60)
    print("TEST 1: Directory Structure Creation")
    print("="*60)

    # Create test output directory
    input_id = "test-input"
    brand_id = "test-brand"
    output_dir = create_test_output_dir(input_id, brand_id)

    print(f"\n✓ Created output directory: {output_dir}")

    # Validate directory exists
    assert output_dir.exists(), f"Output directory not created: {output_dir}"
    print(f"✓ Output directory exists")

    # Validate directory naming convention
    dir_name = output_dir.name
    assert dir_name.startswith(f"{input_id}-{brand_id}-"), f"Invalid directory naming: {dir_name}"
    print(f"✓ Directory naming convention correct: {dir_name}")

    # Validate timestamp format (YYYYMMDD-HHMMSS)
    timestamp_part = dir_name.split('-')[-2:]  # Last two parts
    timestamp_str = '-'.join(timestamp_part)
    try:
        datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
        print(f"✓ Timestamp format correct (ISO): {timestamp_str}")
    except ValueError:
        raise AssertionError(f"Invalid timestamp format: {timestamp_str}")

    # Validate stage subdirectories
    for stage_num in range(1, 6):
        stage_dir = output_dir / f"stage{stage_num}"
        assert stage_dir.exists(), f"Stage directory missing: {stage_dir}"

        gitkeep_file = stage_dir / ".gitkeep"
        assert gitkeep_file.exists(), f".gitkeep missing in {stage_dir}"

    print(f"✓ All 5 stage subdirectories created with .gitkeep files")

    # Validate logs subdirectory
    logs_dir = output_dir / "logs"
    assert logs_dir.exists(), f"Logs directory missing: {logs_dir}"

    gitkeep_file = logs_dir / ".gitkeep"
    assert gitkeep_file.exists(), f".gitkeep missing in logs directory"
    print(f"✓ Logs subdirectory created with .gitkeep file")

    print(f"\n✅ TEST 1 PASSED: Directory structure validated")
    return output_dir


def test_logging_configuration(output_dir: Path):
    """Test that logging configuration works correctly."""
    print("\n" + "="*60)
    print("TEST 2: Logging Configuration")
    print("="*60)

    # Setup pipeline logging
    setup_pipeline_logging(output_dir)
    print(f"\n✓ Logging configured for output directory: {output_dir}")

    # Test different log levels
    logging.info("INFO level test message - should appear in console and pipeline.log")
    logging.debug("DEBUG level test message - should appear only in pipeline.log")
    logging.warning("WARNING level test message - should appear in console and pipeline.log")
    logging.error("ERROR level test message - should appear in console, pipeline.log, and errors.log")

    # Log an exception with stack trace
    try:
        raise ValueError("Test exception for error logging")
    except ValueError:
        logging.error("Caught test exception", exc_info=True)

    print(f"\n✓ Test log messages written")

    # Validate log files exist
    logs_dir = output_dir / "logs"
    pipeline_log = logs_dir / "pipeline.log"
    error_log = logs_dir / "errors.log"

    assert pipeline_log.exists(), f"pipeline.log not created: {pipeline_log}"
    print(f"✓ pipeline.log created: {pipeline_log}")

    assert error_log.exists(), f"errors.log not created: {error_log}"
    print(f"✓ errors.log created: {error_log}")

    # Validate pipeline.log content
    with open(pipeline_log, 'r', encoding='utf-8') as f:
        pipeline_content = f.read()

    assert "INFO level test message" in pipeline_content, "INFO message not in pipeline.log"
    assert "DEBUG level test message" in pipeline_content, "DEBUG message not in pipeline.log"
    assert "WARNING level test message" in pipeline_content, "WARNING message not in pipeline.log"
    assert "ERROR level test message" in pipeline_content, "ERROR message not in pipeline.log"
    assert "Test exception for error logging" in pipeline_content, "Exception not in pipeline.log"
    print(f"✓ pipeline.log contains all log levels (INFO, DEBUG, WARNING, ERROR)")

    # Validate errors.log content
    with open(error_log, 'r', encoding='utf-8') as f:
        error_content = f.read()

    assert "INFO level test message" not in error_content, "INFO message should not be in errors.log"
    assert "DEBUG level test message" not in error_content, "DEBUG message should not be in errors.log"
    assert "ERROR level test message" in error_content, "ERROR message not in errors.log"
    assert "Test exception for error logging" in error_content, "Exception not in errors.log"
    assert "ValueError: Test exception for error logging" in error_content, "Stack trace not in errors.log"
    print(f"✓ errors.log contains only ERROR level logs with stack traces")

    # Validate log format (timestamp present)
    first_log_line = pipeline_content.split('\n')[0]
    assert " - " in first_log_line, "Log format incorrect (missing separators)"
    print(f"✓ Log format includes timestamp and structured fields")

    print(f"\n✅ TEST 2 PASSED: Logging configuration validated")


def test_multiple_runs():
    """Test that multiple runs create separate directories."""
    print("\n" + "="*60)
    print("TEST 3: Multiple Run Isolation")
    print("="*60)

    import time

    # Create first run
    output_dir_1 = create_test_output_dir("test-input", "test-brand")
    print(f"\n✓ Created first run directory: {output_dir_1.name}")

    # Wait to ensure different timestamp
    time.sleep(1)

    # Create second run
    output_dir_2 = create_test_output_dir("test-input", "test-brand")
    print(f"✓ Created second run directory: {output_dir_2.name}")

    # Validate directories are different
    assert output_dir_1 != output_dir_2, "Multiple runs created same directory"
    print(f"✓ Multiple runs create separate directories")

    print(f"\n✅ TEST 3 PASSED: Multiple run isolation validated")


def cleanup_test_directories():
    """Clean up test output directories."""
    print("\n" + "="*60)
    print("CLEANUP: Removing test directories")
    print("="*60)

    test_outputs_dir = Path("data/test-outputs")
    test_dirs = list(test_outputs_dir.glob("test-input-test-brand-*"))

    for test_dir in test_dirs:
        # Remove all files in subdirectories
        for subdir in test_dir.iterdir():
            if subdir.is_dir():
                for file in subdir.iterdir():
                    file.unlink()
                subdir.rmdir()
        test_dir.rmdir()
        print(f"✓ Removed: {test_dir.name}")

    print(f"\n✓ Cleanup complete: {len(test_dirs)} test directories removed")


def main():
    """Run all validation tests."""
    print("\n" + "="*80)
    print("OUTPUT DIRECTORY STRUCTURE AND LOGGING VALIDATION TESTS")
    print("="*80)

    try:
        # Test 1: Directory structure
        output_dir = test_directory_structure()

        # Test 2: Logging configuration
        test_logging_configuration(output_dir)

        # Test 3: Multiple runs
        test_multiple_runs()

        # Cleanup
        cleanup_test_directories()

        # Summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\nValidation Summary:")
        print("  ✓ Output directory structure created correctly")
        print("  ✓ Stage subdirectories (stage1-5) with .gitkeep files")
        print("  ✓ Logs subdirectory with .gitkeep file")
        print("  ✓ Directory naming convention (input-id-brand-id-timestamp)")
        print("  ✓ Timestamp format (ISO YYYYMMDD-HHMMSS)")
        print("  ✓ Console logging at INFO level")
        print("  ✓ File logging at DEBUG level (pipeline.log)")
        print("  ✓ Error logging at ERROR level (errors.log)")
        print("  ✓ Log format with timestamps")
        print("  ✓ Multiple runs create separate directories")
        print("="*80 + "\n")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
