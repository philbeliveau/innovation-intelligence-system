"""Utility Functions for Backend

Helper functions for file management, cleanup, etc.
"""
import os
import shutil
from pathlib import Path


def cleanup_temp_file(file_path: str) -> None:
    """
    Delete temporary file after processing

    Args:
        file_path: Path to file to delete
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log error but don't raise - cleanup failures shouldn't break pipeline
        print(f"Warning: Failed to cleanup {file_path}: {e}")


def cleanup_run_directory(run_id: str, keep_outputs: bool = True) -> None:
    """
    Clean up temporary files for a pipeline run

    Args:
        run_id: Run identifier
        keep_outputs: If True, only delete temp PDFs, not stage outputs
    """
    run_dir = Path(f"tmp/runs/{run_id}")
    if not run_dir.exists():
        return

    if keep_outputs:
        # Only delete downloaded PDFs
        pdf_path = run_dir / "input.pdf"
        cleanup_temp_file(str(pdf_path))
    else:
        # Delete entire run directory
        try:
            shutil.rmtree(run_dir)
        except Exception as e:
            print(f"Warning: Failed to cleanup run directory {run_id}: {e}")


def ensure_run_directory(run_id: str) -> Path:
    """
    Create run directory if it doesn't exist

    Args:
        run_id: Run identifier

    Returns:
        Path object for run directory
    """
    run_dir = Path(f"tmp/runs/{run_id}")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
