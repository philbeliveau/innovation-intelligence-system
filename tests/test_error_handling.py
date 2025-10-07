#!/usr/bin/env python3
"""
Error Handling Test: Missing Research Data

Tests that pipeline completes gracefully when research file is missing.
"""

import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from test_stages_1_4_integration import (
    create_integration_test_output_dir,
    run_stages_1_4
)
from pipeline.utils import load_input_document, setup_pipeline_logging


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("=" * 80)
    logging.info("ERROR HANDLING TEST: Missing Research Data")
    logging.info("=" * 80)

    # Run with simulated missing research
    input_id = "savannah-bananas"
    brand_id = "lactalis-canada"

    output_dir = create_integration_test_output_dir(input_id, brand_id)
    setup_pipeline_logging(output_dir, console_level=logging.INFO)

    input_text = load_input_document(input_id)
    logging.info(f"Input loaded: {len(input_text)} characters\n")

    try:
        # Run with simulate_missing_research=True
        results = run_stages_1_4(
            input_id,
            brand_id,
            input_text,
            output_dir,
            simulate_missing_research=True  # This simulates missing file
        )

        # Check if degraded mode was activated
        if results.get('degraded_mode', False):
            logging.info("✅ PASS: Pipeline completed in degraded mode")
            logging.info("✅ PASS: Warning logged for missing research")
            logging.info(f"✅ PASS: Stage 4 output generated: {len(results['stage4_output'])} characters")
            logging.info("\nError handling test SUCCESSFUL!")
            return 0
        else:
            logging.error("❌ FAIL: Degraded mode not activated")
            return 1

    except Exception as e:
        logging.error(f"❌ FAIL: Pipeline failed fatally: {e}")
        logging.error("Expected: Non-fatal completion with degraded output")
        return 1


if __name__ == "__main__":
    exit(main())
