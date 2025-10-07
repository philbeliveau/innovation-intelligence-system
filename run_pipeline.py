#!/usr/bin/env python3
"""
Innovation Intelligence Pipeline - Main execution script.

This script orchestrates the complete pipeline from input processing
to opportunity generation.

Usage:
    # Single run
    python run_pipeline.py --input savannah-bananas --brand lactalis-canada

    # Batch mode (all combinations)
    python run_pipeline.py --batch

    # Verbose logging
    python run_pipeline.py --input savannah-bananas --brand lactalis-canada --verbose
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

try:
    import yaml
    from dotenv import load_dotenv
except ImportError:
    print("Error: Required packages not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

# Import pipeline components
from pipeline.utils import (
    load_input_document,
    setup_pipeline_logging,
    create_test_output_dir as utils_create_output_dir
)
from pipeline.stages.stage1_input_processing import create_stage1_chain
from pipeline.stages.stage2_signal_amplification import create_stage2_chain

# Load environment variables
load_dotenv()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level.

    Args:
        verbose: If True, set logging to DEBUG level, otherwise INFO
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_input_manifest(manifest_path: Path = Path("data/input-manifest.yaml")) -> Dict[str, Any]:
    """Load input document manifest.

    Args:
        manifest_path: Path to input manifest YAML file

    Returns:
        Dictionary containing input manifest data

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        ValueError: If manifest YAML is invalid
    """
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Input manifest not found: {manifest_path}\n"
            f"Expected location: data/input-manifest.yaml"
        )

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
            return manifest
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in input manifest: {e}")


def get_input_ids(manifest: Dict[str, Any]) -> List[str]:
    """Extract list of input IDs from manifest.

    Args:
        manifest: Input manifest dictionary

    Returns:
        List of input document IDs
    """
    return [input_doc['id'] for input_doc in manifest.get('inputs', [])]


def validate_input_id(input_id: str, manifest: Dict[str, Any]) -> bool:
    """Validate that input ID exists in manifest.

    Args:
        input_id: Input document ID to validate
        manifest: Input manifest dictionary

    Returns:
        True if input ID exists, False otherwise
    """
    valid_ids = get_input_ids(manifest)
    if input_id not in valid_ids:
        logging.error(f"Invalid input ID: '{input_id}'")
        logging.error(f"Valid input IDs: {', '.join(valid_ids)}")
        return False
    return True


def get_brand_ids(brand_profiles_dir: Path = Path("data/brand-profiles")) -> List[str]:
    """Get list of available brand profile IDs.

    Args:
        brand_profiles_dir: Directory containing brand profile YAML files

    Returns:
        List of brand profile IDs (filenames without .yaml extension)
    """
    if not brand_profiles_dir.exists():
        logging.error(f"Brand profiles directory not found: {brand_profiles_dir}")
        return []

    brand_files = list(brand_profiles_dir.glob("*.yaml"))
    return [f.stem for f in brand_files]


def validate_brand_id(brand_id: str, brand_profiles_dir: Path = Path("data/brand-profiles")) -> bool:
    """Validate that brand profile exists.

    Args:
        brand_id: Brand profile ID to validate
        brand_profiles_dir: Directory containing brand profile YAML files

    Returns:
        True if brand profile exists, False otherwise
    """
    brand_file = brand_profiles_dir / f"{brand_id}.yaml"

    if not brand_file.exists():
        logging.error(f"Brand profile not found: '{brand_id}'")
        logging.error(f"Expected file: {brand_file}")

        valid_brands = get_brand_ids(brand_profiles_dir)
        if valid_brands:
            logging.error(f"Valid brand IDs: {', '.join(valid_brands)}")
        else:
            logging.error("No brand profiles found in data/brand-profiles/")
        return False

    return True


def execute_pipeline(input_id: str, brand_id: str) -> bool:
    """Execute pipeline for given input and brand combination.

    Args:
        input_id: Input document ID
        brand_id: Brand profile ID

    Returns:
        True if execution successful, False otherwise
    """
    logging.info(f"Executing pipeline for {input_id} + {brand_id}")

    try:
        # Create output directory using utils function
        output_dir = utils_create_output_dir(input_id, brand_id)
        logging.info(f"Output directory: {output_dir}")

        # Setup pipeline logging to file
        setup_pipeline_logging(output_dir)

        # Load input document
        logging.info(f"Loading input document: {input_id}")
        input_text = load_input_document(input_id)
        logging.info(f"Input document loaded: {len(input_text)} characters")

        # Stage 1: Input Processing and Inspiration Identification
        logging.info("=" * 60)
        logging.info("STAGE 1: Input Processing and Inspiration Identification")
        logging.info("=" * 60)

        stage1_chain = create_stage1_chain()
        stage1_result = stage1_chain.run(input_text)
        stage1_output = stage1_result[stage1_chain.output_key]

        # Save Stage 1 output
        stage1_file = stage1_chain.save_output(stage1_output, output_dir)
        logging.info(f"Stage 1 complete. Output: {stage1_file}")

        # Stage 2: Signal Amplification and Trend Extraction
        logging.info("=" * 60)
        logging.info("STAGE 2: Signal Amplification and Trend Extraction")
        logging.info("=" * 60)

        stage2_chain = create_stage2_chain()
        stage2_result = stage2_chain.run(stage1_output)
        stage2_output = stage2_result[stage2_chain.output_key]

        # Save Stage 2 output
        stage2_file = stage2_chain.save_output(stage2_output, output_dir)
        logging.info(f"Stage 2 complete. Output: {stage2_file}")

        # TODO: Stages 3-5 implementation pending
        logging.info("Stages 3-5 not yet implemented")

        logging.info("=" * 60)
        logging.info(f"Pipeline execution completed successfully")
        logging.info(f"Output directory: {output_dir}")
        logging.info("=" * 60)
        return True

    except Exception as e:
        logging.error(f"Pipeline execution failed: {e}", exc_info=True)
        return False


def run_single(input_id: str, brand_id: str, manifest: Dict[str, Any]) -> int:
    """Run pipeline for single input-brand combination.

    Args:
        input_id: Input document ID
        brand_id: Brand profile ID
        manifest: Input manifest dictionary

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Validate inputs
    if not validate_input_id(input_id, manifest):
        return 1

    if not validate_brand_id(brand_id):
        return 1

    # Execute pipeline
    success = execute_pipeline(input_id, brand_id)
    return 0 if success else 1


def run_batch(manifest: Dict[str, Any]) -> int:
    """Run pipeline for all input-brand combinations.

    Args:
        manifest: Input manifest dictionary

    Returns:
        Exit code (0 for success, 1 if any failures)
    """
    input_ids = get_input_ids(manifest)
    brand_ids = get_brand_ids()

    if not input_ids:
        logging.error("No input documents found in manifest")
        return 1

    if not brand_ids:
        logging.error("No brand profiles found in data/brand-profiles/")
        return 1

    total_combinations = len(input_ids) * len(brand_ids)
    logging.info(f"Batch mode: Processing {len(input_ids)} inputs × {len(brand_ids)} brands = {total_combinations} combinations")

    success_count = 0
    failure_count = 0

    for input_id in input_ids:
        for brand_id in brand_ids:
            logging.info(f"\n{'='*60}")
            logging.info(f"Processing: {input_id} + {brand_id}")
            logging.info(f"{'='*60}")

            success = execute_pipeline(input_id, brand_id)

            if success:
                success_count += 1
            else:
                failure_count += 1

    logging.info(f"\n{'='*60}")
    logging.info(f"Batch execution complete")
    logging.info(f"Successful: {success_count}/{total_combinations}")
    logging.info(f"Failed: {failure_count}/{total_combinations}")
    logging.info(f"{'='*60}")

    return 0 if failure_count == 0 else 1


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Innovation Intelligence Pipeline - Process input documents to generate brand-specific innovation opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single run
  %(prog)s --input savannah-bananas --brand lactalis-canada

  # Batch mode (process all input-brand combinations)
  %(prog)s --batch

  # Enable verbose logging
  %(prog)s --input savannah-bananas --brand lactalis-canada --verbose

  # Batch mode with verbose logging
  %(prog)s --batch --verbose

For more information, see: docs/architecture.md
        """
    )

    # Single run arguments
    parser.add_argument(
        '--input',
        type=str,
        help='Input document ID (from data/input-manifest.yaml). Required for single run.'
    )

    parser.add_argument(
        '--brand',
        type=str,
        help='Brand profile ID (YAML filename without extension from data/brand-profiles/). Required for single run.'
    )

    # Batch mode flag
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Run pipeline for all input-brand combinations. Overrides --input and --brand.'
    )

    # Verbose logging flag
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG level) logging'
    )

    return parser.parse_args()


def main() -> int:
    """Main pipeline execution.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    setup_logging(args.verbose)

    logging.info("Innovation Intelligence Pipeline - Starting")

    try:
        # Load input manifest
        manifest = load_input_manifest()

        # Determine execution mode
        if args.batch:
            # Batch mode
            logging.info("Execution mode: BATCH")
            return run_batch(manifest)
        else:
            # Single run mode - validate required arguments
            if not args.input or not args.brand:
                logging.error("Error: --input and --brand are required for single run mode")
                logging.error("Use --batch for batch mode, or provide both --input and --brand")
                logging.error("Run with --help for usage information")
                return 1

            logging.info("Execution mode: SINGLE RUN")
            return run_single(args.input, args.brand, manifest)

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logging.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
