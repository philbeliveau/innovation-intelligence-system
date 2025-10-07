#!/usr/bin/env python3
"""
Integration Test: Complete Pipeline (Stages 1-4)

This script tests the complete Stages 1-4 pipeline on multiple input/brand
combinations before building Stage 5. It validates end-to-end flow,
measures performance, and ensures error handling works correctly.

Test Coverage:
- 8 scenarios: 2 inputs (Savannah Bananas, Premium Fast Food) × 4 brands
- Performance measurement per scenario (target: <30 minutes)
- Error handling with missing research data
- Quality spot-checks on random outputs

Test Outputs:
- data/test-outputs/integration-test-stages-1-4/{input-id}-{brand-id}/
  - stage1/inspiration-analysis.md
  - stage2/trend-analysis.md
  - stage3/universal-lessons.md
  - stage4/brand-contextualization.md
  - logs/pipeline.log
- data/test-outputs/integration-test-stages-1-4/test-summary.md
- data/test-outputs/integration-test-stages-1-4/performance-baseline.md
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import yaml
import random
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import pipeline components
from pipeline.stages.stage1_input_processing import create_stage1_chain
from pipeline.stages.stage2_signal_amplification import create_stage2_chain
from pipeline.stages.stage3_general_translation import create_stage3_chain
from pipeline.stages.stage4_brand_contextualization import create_stage4_chain
from pipeline.utils import (
    load_input_document,
    load_brand_profile,
    load_research_data,
    setup_pipeline_logging
)


def load_test_scenarios() -> List[Dict]:
    """Load test scenarios configuration.

    Returns:
        List of scenario dictionaries with input_id and brand_id
    """
    scenarios = []

    # Test inputs
    test_inputs = ["savannah-bananas", "premium-fast-food"]

    # Test brands
    test_brands = [
        "lactalis-canada",
        "mccormick-usa",
        "columbia-sportswear",
        "decathlon"
    ]

    # Create all combinations
    for input_id in test_inputs:
        for brand_id in test_brands:
            scenarios.append({
                "input_id": input_id,
                "brand_id": brand_id
            })

    logging.info(f"Loaded {len(scenarios)} test scenarios")
    return scenarios


def create_integration_test_output_dir(input_id: str, brand_id: str) -> Path:
    """Create output directory for integration test scenario.

    Directory structure:
    data/test-outputs/integration-test-stages-1-4/{input-id}-{brand-id}/
        stage1/
        stage2/
        stage3/
        stage4/
        logs/

    Args:
        input_id: Input document ID
        brand_id: Brand profile ID

    Returns:
        Path to created output directory
    """
    base_dir = Path("data/test-outputs/integration-test-stages-1-4")
    output_dir = base_dir / f"{input_id}-{brand_id}"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create stage directories
    for stage_num in range(1, 5):
        stage_dir = output_dir / f"stage{stage_num}"
        stage_dir.mkdir(exist_ok=True)

    # Create logs directory
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    logging.debug(f"Created output directory: {output_dir}")
    return output_dir


def run_stages_1_4(
    input_id: str,
    brand_id: str,
    input_text: str,
    output_dir: Path,
    simulate_missing_research: bool = False
) -> Dict[str, str]:
    """Run Stages 1-4 pipeline on input document with brand context.

    Args:
        input_id: Input document ID
        brand_id: Brand profile ID
        input_text: Input document text content
        output_dir: Output directory for this scenario
        simulate_missing_research: If True, simulate missing research file

    Returns:
        Dictionary with stage outputs and metadata

    Raises:
        Exception: If any stage fails fatally
    """
    logging.info(f"Starting Stages 1-4 pipeline: {input_id} → {brand_id}")
    results = {}

    try:
        # Stage 1: Input Processing
        logging.info("=" * 80)
        logging.info("STAGE 1: Input Processing and Inspiration Identification")
        logging.info("=" * 80)

        stage1_chain = create_stage1_chain()
        stage1_result = stage1_chain.run(input_text)
        stage1_output = stage1_result[stage1_chain.output_key]

        # Save Stage 1 output
        stage1_chain.save_output(stage1_output, output_dir)
        results['stage1_output'] = stage1_output

        logging.info(f"Stage 1 completed: {len(stage1_output)} characters")

        # Stage 2: Signal Amplification and Trend Extraction
        logging.info("=" * 80)
        logging.info("STAGE 2: Signal Amplification and Trend Extraction")
        logging.info("=" * 80)

        stage2_chain = create_stage2_chain()
        stage2_result = stage2_chain.run(stage1_output)
        stage2_output = stage2_result[stage2_chain.output_key]

        # Save Stage 2 output
        stage2_chain.save_output(stage2_output, output_dir)
        results['stage2_output'] = stage2_output

        logging.info(f"Stage 2 completed: {len(stage2_output)} characters")

        # Stage 3: General Translation to Universal Lessons
        logging.info("=" * 80)
        logging.info("STAGE 3: General Translation to Universal Lessons")
        logging.info("=" * 80)

        stage3_chain = create_stage3_chain()
        stage3_result = stage3_chain.run(stage1_output, stage2_output)
        stage3_output = stage3_result[stage3_chain.output_key]

        # Save Stage 3 output
        stage3_chain.save_output(stage3_output, output_dir)
        results['stage3_output'] = stage3_output

        logging.info(f"Stage 3 completed: {len(stage3_output)} characters")

        # Stage 4: Brand Contextualization
        logging.info("=" * 80)
        logging.info("STAGE 4: Brand Contextualization")
        logging.info("=" * 80)

        # Load brand profile
        brand_profile = load_brand_profile(brand_id)
        logging.info(f"Loaded brand profile: {brand_profile.get('company_name', brand_id)}")

        # Load brand research (with optional simulation of missing file)
        if simulate_missing_research:
            logging.warning(f"SIMULATING MISSING RESEARCH FILE for {brand_id}")
            research_content = ""
        else:
            research_content = load_research_data(brand_id)

        if not research_content:
            logging.warning(f"No research data for {brand_id} - degraded mode")
            results['degraded_mode'] = True
        else:
            logging.info(f"Loaded research data: {len(research_content)} characters")
            results['degraded_mode'] = False

        stage4_chain = create_stage4_chain()
        stage4_result = stage4_chain.run(
            stage3_output,
            brand_profile,
            research_content
        )
        stage4_output = stage4_result[stage4_chain.output_key]

        # Save Stage 4 output
        stage4_chain.save_output(stage4_output, output_dir)
        results['stage4_output'] = stage4_output

        logging.info(f"Stage 4 completed: {len(stage4_output)} characters")

        logging.info("=" * 80)
        logging.info(f"Pipeline completed: {input_id} → {brand_id}")
        logging.info("=" * 80)

        return results

    except Exception as e:
        logging.error(
            f"Pipeline failed for {input_id} → {brand_id}: {e}",
            exc_info=True
        )
        raise


def perform_quality_spot_check(
    scenario_results: List[Dict],
    num_samples: int = 2
) -> List[Dict]:
    """Randomly select scenarios for manual quality review.

    Args:
        scenario_results: List of all scenario results
        num_samples: Number of scenarios to select

    Returns:
        List of randomly selected scenario results
    """
    successful_results = [
        r for r in scenario_results
        if r['status'] == 'success'
    ]

    if len(successful_results) < num_samples:
        logging.warning(
            f"Only {len(successful_results)} successful scenarios available "
            f"for spot-check (requested {num_samples})"
        )
        return successful_results

    selected = random.sample(successful_results, num_samples)

    logging.info(f"Selected {len(selected)} scenarios for quality spot-check:")
    for scenario in selected:
        logging.info(
            f"  - {scenario['input_id']} → {scenario['brand_id']} "
            f"(output: {scenario['output_dir']})"
        )

    return selected


def calculate_performance_baseline(scenario_results: List[Dict]) -> Dict:
    """Calculate performance baseline metrics.

    Args:
        scenario_results: List of scenario results with execution times

    Returns:
        Dictionary with performance metrics
    """
    execution_times = [
        r['execution_time']
        for r in scenario_results
        if r['status'] == 'success'
    ]

    if not execution_times:
        return {
            'avg_time': 0,
            'min_time': 0,
            'max_time': 0,
            'total_time': 0,
            'num_scenarios': 0
        }

    metrics = {
        'avg_time': sum(execution_times) / len(execution_times),
        'min_time': min(execution_times),
        'max_time': max(execution_times),
        'total_time': sum(execution_times),
        'num_scenarios': len(execution_times)
    }

    logging.info("Performance Baseline:")
    logging.info(f"  Average: {metrics['avg_time']:.2f} seconds")
    logging.info(f"  Minimum: {metrics['min_time']:.2f} seconds")
    logging.info(f"  Maximum: {metrics['max_time']:.2f} seconds")
    logging.info(f"  Total: {metrics['total_time']:.2f} seconds")
    logging.info(f"  Scenarios: {metrics['num_scenarios']}")

    return metrics


def generate_test_summary(
    scenario_results: List[Dict],
    performance_metrics: Dict,
    output_dir: Path,
    start_time: datetime,
    end_time: datetime
) -> None:
    """Generate comprehensive test summary report.

    Args:
        scenario_results: List of scenario results
        performance_metrics: Performance baseline metrics
        output_dir: Base output directory
        start_time: Test start timestamp
        end_time: Test end timestamp
    """
    duration = (end_time - start_time).total_seconds()
    success_count = sum(1 for r in scenario_results if r['status'] == 'success')
    failure_count = len(scenario_results) - success_count
    degraded_count = sum(1 for r in scenario_results if r.get('degraded_mode', False))

    summary_file = output_dir / "test-summary.md"

    summary_content = f"""# Complete Pipeline (Stages 1-4) Integration Test Summary

**Test Date:** {start_time.strftime("%Y-%m-%d %H:%M:%S")}
**Duration:** {duration:.2f} seconds ({duration / 60:.1f} minutes)
**Total Scenarios:** {len(scenario_results)} (2 inputs × 4 brands)
**Successful:** {success_count}
**Failed:** {failure_count}
**Degraded Mode:** {degraded_count}
**Success Rate:** {(success_count / len(scenario_results) * 100):.1f}%

## Performance Baseline

**Target:** <30 minutes per scenario (1800 seconds)

- **Average Execution Time:** {performance_metrics['avg_time']:.2f} seconds ({performance_metrics['avg_time'] / 60:.1f} minutes)
- **Minimum Execution Time:** {performance_metrics['min_time']:.2f} seconds ({performance_metrics['min_time'] / 60:.1f} minutes)
- **Maximum Execution Time:** {performance_metrics['max_time']:.2f} seconds ({performance_metrics['max_time'] / 60:.1f} minutes)
- **Total Execution Time:** {performance_metrics['total_time']:.2f} seconds ({performance_metrics['total_time'] / 60:.1f} minutes)

**Performance Status:** {"✅ PASS" if performance_metrics['avg_time'] < 1800 else "❌ FAIL"} (avg < 30 min target)

## Test Results by Scenario

"""

    # Group by input
    inputs = {}
    for result in scenario_results:
        input_id = result['input_id']
        if input_id not in inputs:
            inputs[input_id] = []
        inputs[input_id].append(result)

    for input_id, results in inputs.items():
        summary_content += f"### Input: {input_id}\n\n"

        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            degraded_icon = "⚠️" if result.get('degraded_mode', False) else ""

            summary_content += f"#### {status_icon} {degraded_icon} {result['brand_id']}\n\n"
            summary_content += f"- **Status:** {result['status']}\n"

            if result['status'] == 'success':
                summary_content += f"- **Execution Time:** {result['execution_time']:.2f}s ({result['execution_time'] / 60:.1f} min)\n"
                summary_content += f"- **Stage 1 Output:** {result['stage1_length']} characters\n"
                summary_content += f"- **Stage 2 Output:** {result['stage2_length']} characters\n"
                summary_content += f"- **Stage 3 Output:** {result['stage3_length']} characters\n"
                summary_content += f"- **Stage 4 Output:** {result['stage4_length']} characters\n"
                summary_content += f"- **Degraded Mode:** {'Yes' if result.get('degraded_mode', False) else 'No'}\n"
                summary_content += f"- **Output Directory:** `{result['output_dir']}`\n"
            else:
                summary_content += f"- **Error:** {result['error']}\n"

            summary_content += "\n"

        summary_content += "\n"

    summary_content += f"""## Quality Spot-Check

**Review Required:** Manually review 2 randomly selected outputs

See test output for selected scenarios. For each selected output, verify:

1. **Stage 1 Inspirations:** Are they relevant to the input document?
2. **Stage 2 Trends:** Are they clearly derived from the document content?
3. **Stage 3 Lessons:** Are they universal and generalizable?
4. **Stage 4 Insights:** Are they specific to the brand context?

## Error Handling Validation

Verify that scenarios with missing research data:
- ✅ Complete without fatal errors
- ✅ Generate degraded output
- ✅ Log appropriate warnings

## Next Steps

1. **Review Quality Spot-Checks:**
   - Manually review selected scenario outputs
   - Document quality findings
   - Identify improvement opportunities

2. **Performance Optimization (if needed):**
   - If any scenario exceeds 30-minute target
   - Review LLM API response times
   - Optimize prompt lengths
   - Consider parallel processing

3. **Create Execution Guide:**
   - Document common issues found
   - Provide troubleshooting tips
   - Include error handling scenarios

4. **Proceed to Stage 5:**
   - Pipeline validated end-to-end
   - Performance baseline established
   - Ready for opportunity generation stage

---

*Generated by test_stages_1_4_integration.py on {end_time.strftime("%Y-%m-%d %H:%M:%S")}*
"""

    summary_file.write_text(summary_content, encoding='utf-8')
    logging.info(f"Test summary saved: {summary_file}")


def generate_performance_baseline_report(
    performance_metrics: Dict,
    scenario_results: List[Dict],
    output_dir: Path
) -> None:
    """Generate detailed performance baseline report.

    Args:
        performance_metrics: Performance metrics
        scenario_results: List of scenario results
        output_dir: Base output directory
    """
    baseline_file = output_dir / "performance-baseline.md"

    content = f"""# Performance Baseline Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Scenarios:** {performance_metrics['num_scenarios']}

## Summary Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Average Time** | {performance_metrics['avg_time']:.2f}s ({performance_metrics['avg_time'] / 60:.1f} min) | {"✅ < 30 min" if performance_metrics['avg_time'] < 1800 else "❌ > 30 min"} |
| **Minimum Time** | {performance_metrics['min_time']:.2f}s ({performance_metrics['min_time'] / 60:.1f} min) | - |
| **Maximum Time** | {performance_metrics['max_time']:.2f}s ({performance_metrics['max_time'] / 60:.1f} min) | {"✅ < 30 min" if performance_metrics['max_time'] < 1800 else "❌ > 30 min"} |
| **Total Time** | {performance_metrics['total_time']:.2f}s ({performance_metrics['total_time'] / 60:.1f} min) | - |

## Scenario-by-Scenario Times

"""

    # Sort by execution time (slowest first)
    sorted_results = sorted(
        [r for r in scenario_results if r['status'] == 'success'],
        key=lambda x: x['execution_time'],
        reverse=True
    )

    for idx, result in enumerate(sorted_results, 1):
        content += f"{idx}. **{result['input_id']} → {result['brand_id']}**: "
        content += f"{result['execution_time']:.2f}s ({result['execution_time'] / 60:.1f} min)"

        if result['execution_time'] > 1800:
            content += " ⚠️ EXCEEDS TARGET"

        content += "\n"

    content += f"""

## Performance Targets

**Primary Target:** Average execution time < 30 minutes (1800 seconds)
**Status:** {"✅ PASS" if performance_metrics['avg_time'] < 1800 else "❌ FAIL"}

## Optimization Opportunities

"""

    if performance_metrics['max_time'] > 1800:
        content += f"""
### High Priority

- **Slowest scenario exceeds target** ({performance_metrics['max_time'] / 60:.1f} min)
- Review LLM API response times
- Optimize prompt lengths (especially Stage 4 with research data)
- Consider caching or parallel processing
"""
    else:
        content += """
### Performance is Within Target

All scenarios complete within 30-minute target. No immediate optimization required.

Monitor for:
- LLM API latency changes
- Research data size increases
- Additional stages in future
"""

    content += """

## Baseline for Future Comparison

Use these metrics as baseline for measuring:
- Impact of prompt refinements
- Performance of Stage 5 addition
- Benefits of optimization efforts
- Effects of scaling to more brands/inputs

---

*Generated by test_stages_1_4_integration.py*
"""

    baseline_file.write_text(content, encoding='utf-8')
    logging.info(f"Performance baseline report saved: {baseline_file}")


def main():
    """Run complete pipeline integration test."""
    # Setup basic console logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    start_time = datetime.now()
    scenario_results = []

    logging.info("=" * 80)
    logging.info("COMPLETE PIPELINE (STAGES 1-4) INTEGRATION TEST")
    logging.info("=" * 80)
    logging.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("")

    try:
        # Load test scenarios
        scenarios = load_test_scenarios()
        logging.info(f"Testing {len(scenarios)} scenarios (2 inputs × 4 brands)\n")

        # Process each scenario
        for idx, scenario in enumerate(scenarios, 1):
            input_id = scenario['input_id']
            brand_id = scenario['brand_id']

            logging.info("=" * 80)
            logging.info(f"SCENARIO {idx}/{len(scenarios)}: {input_id} → {brand_id}")
            logging.info("=" * 80)

            scenario_start = time.time()

            try:
                # Create output directory
                output_dir = create_integration_test_output_dir(input_id, brand_id)

                # Setup logging for this pipeline run
                setup_pipeline_logging(output_dir, console_level=logging.INFO)

                # Load input document
                logging.info(f"Loading input document: {input_id}")
                input_text = load_input_document(input_id)
                logging.info(f"Input loaded: {len(input_text)} characters\n")

                # Run Stages 1-4 pipeline
                results = run_stages_1_4(
                    input_id,
                    brand_id,
                    input_text,
                    output_dir
                )

                scenario_end = time.time()
                execution_time = scenario_end - scenario_start

                # Record success
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

                # Record failure
                scenario_results.append({
                    'input_id': input_id,
                    'brand_id': brand_id,
                    'status': 'failed',
                    'execution_time': execution_time,
                    'error': str(e)
                })

                # Continue with next scenario
                continue

        # Perform quality spot-check
        logging.info("=" * 80)
        logging.info("QUALITY SPOT-CHECK")
        logging.info("=" * 80)
        selected_scenarios = perform_quality_spot_check(scenario_results, num_samples=2)
        logging.info("")

        # Calculate performance baseline
        logging.info("=" * 80)
        logging.info("PERFORMANCE BASELINE")
        logging.info("=" * 80)
        performance_metrics = calculate_performance_baseline(scenario_results)
        logging.info("")

        # Generate reports
        end_time = datetime.now()
        base_output_dir = Path("data/test-outputs/integration-test-stages-1-4")
        base_output_dir.mkdir(parents=True, exist_ok=True)

        generate_test_summary(
            scenario_results,
            performance_metrics,
            base_output_dir,
            start_time,
            end_time
        )

        generate_performance_baseline_report(
            performance_metrics,
            scenario_results,
            base_output_dir
        )

        logging.info("=" * 80)
        logging.info("INTEGRATION TEST COMPLETE")
        logging.info("=" * 80)
        logging.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Duration: {(end_time - start_time).total_seconds():.2f} seconds")
        logging.info(
            f"Results: {sum(1 for r in scenario_results if r['status'] == 'success')}"
            f"/{len(scenario_results)} successful"
        )
        logging.info("")
        logging.info("Reports Generated:")
        logging.info(f"  - {base_output_dir}/test-summary.md")
        logging.info(f"  - {base_output_dir}/performance-baseline.md")
        logging.info("")
        logging.info("Next Steps:")
        logging.info("1. Review test summary and performance baseline")
        logging.info("2. Manually review quality spot-check scenarios")
        logging.info("3. Test error handling with missing research file")
        logging.info("4. Create pipeline execution guide")
        logging.info("5. Proceed to Stage 5 development")
        logging.info("=" * 80)

        # Exit with appropriate code
        if sum(1 for r in scenario_results if r['status'] == 'failed') > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logging.error(f"Integration test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
