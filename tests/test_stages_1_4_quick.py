#!/usr/bin/env python3
"""
Quick Integration Test: Stages 1-4 (2 scenarios for validation)

Runs 2 scenarios quickly to validate end-to-end pipeline:
- savannah-bananas → lactalis-canada
- premium-fast-food → mccormick-usa
"""

import logging
import sys
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from test_stages_1_4_integration import (
    create_integration_test_output_dir,
    run_stages_1_4,
    calculate_performance_baseline,
    perform_quality_spot_check
)
from pipeline.utils import load_input_document, setup_pipeline_logging


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Quick test scenarios
    scenarios = [
        {"input_id": "savannah-bananas", "brand_id": "lactalis-canada"},
        {"input_id": "premium-fast-food", "brand_id": "mccormick-usa"}
    ]

    scenario_results = []
    start_time = datetime.now()

    logging.info("=" * 80)
    logging.info("QUICK INTEGRATION TEST (2 SCENARIOS)")
    logging.info("=" * 80)

    for idx, scenario in enumerate(scenarios, 1):
        input_id = scenario['input_id']
        brand_id = scenario['brand_id']

        logging.info(f"\nSCENARIO {idx}/2: {input_id} → {brand_id}")
        logging.info("=" * 80)

        scenario_start = time.time()

        try:
            output_dir = create_integration_test_output_dir(input_id, brand_id)
            setup_pipeline_logging(output_dir, console_level=logging.INFO)

            input_text = load_input_document(input_id)
            logging.info(f"Input loaded: {len(input_text)} characters\n")

            results = run_stages_1_4(input_id, brand_id, input_text, output_dir)

            scenario_end = time.time()
            execution_time = scenario_end - scenario_start

            scenario_results.append({
                'input_id': input_id,
                'brand_id': brand_id,
                'status': 'success',
                'execution_time': execution_time,
                'output_dir': str(output_dir.resolve().relative_to(Path.cwd())),
                'stage1_length': len(results['stage1_output']),
                'stage2_length': len(results['stage2_output']),
                'stage3_length': len(results['stage3_output']),
                'stage4_length': len(results['stage4_output']),
                'degraded_mode': results.get('degraded_mode', False)
            })

            logging.info(f"✅ Scenario {idx} completed in {execution_time:.2f}s\n")

        except Exception as e:
            scenario_end = time.time()
            execution_time = scenario_end - scenario_start

            logging.error(f"❌ Scenario {idx} failed: {e}\n")

            scenario_results.append({
                'input_id': input_id,
                'brand_id': brand_id,
                'status': 'failed',
                'execution_time': execution_time,
                'error': str(e)
            })

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logging.info("=" * 80)
    logging.info("QUICK TEST COMPLETE")
    logging.info("=" * 80)
    logging.info(f"Duration: {duration:.2f}s ({duration/60:.1f} min)")
    logging.info(f"Success: {sum(1 for r in scenario_results if r['status'] == 'success')}/2")

    metrics = calculate_performance_baseline(scenario_results)
    logging.info(f"\nAverage execution time: {metrics['avg_time']:.2f}s ({metrics['avg_time']/60:.1f} min)")
    logging.info(f"Target: <1800s (30 min) - {'✅ PASS' if metrics['avg_time'] < 1800 else '❌ FAIL'}")

    sys.exit(0 if all(r['status'] == 'success' for r in scenario_results) else 1)


if __name__ == "__main__":
    main()
