#!/usr/bin/env python3
"""
Integration Test: Stages 1-3 Pipeline (Input Processing → Trend Extraction → Universal Lessons)

This script tests the complete Stages 1-3 pipeline on all input documents
from the input manifest. It validates that the pipeline can successfully
process diverse input types (case studies, trend reports, spotted innovations)
and produce quality outputs at each stage.

Test Outputs:
- data/test-outputs/integration-test-stages-1-3/{input-id}/stage1/inspiration-analysis.md
- data/test-outputs/integration-test-stages-1-3/{input-id}/stage2/trend-analysis.md
- data/test-outputs/integration-test-stages-1-3/{input-id}/stage3/universal-lessons.md
- data/test-outputs/integration-test-stages-1-3/{input-id}/logs/pipeline.log
- data/test-outputs/integration-test-stages-1-3/test-summary.md

Quality Review:
After running this test, use docs/stage-1-3-quality-checklist.md to
manually review outputs for quality.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import pipeline components
from pipeline.stages.stage1_input_processing import create_stage1_chain
from pipeline.stages.stage2_signal_amplification import create_stage2_chain
from pipeline.stages.stage3_general_translation import create_stage3_chain
from pipeline.utils import load_input_document, setup_pipeline_logging


def load_input_manifest() -> List[Dict]:
    """Load all input documents from manifest.

    Returns:
        List of input document dictionaries

    Raises:
        FileNotFoundError: If manifest doesn't exist
        ValueError: If manifest is invalid
    """
    manifest_path = Path("data/input-manifest.yaml")

    if not manifest_path.exists():
        raise FileNotFoundError(f"Input manifest not found: {manifest_path}")

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)

    inputs = manifest.get('inputs', [])

    if not inputs:
        raise ValueError("No inputs found in manifest")

    logging.info(f"Loaded {len(inputs)} inputs from manifest")
    return inputs


def create_integration_test_output_dir(input_id: str) -> Path:
    """Create output directory for integration test.

    Directory structure:
    data/test-outputs/integration-test-stages-1-3/{input-id}/
        stage1/
        stage2/
        stage3/
        logs/

    Args:
        input_id: Input document ID

    Returns:
        Path to created output directory
    """
    base_dir = Path("data/test-outputs/integration-test-stages-1-3")
    output_dir = base_dir / input_id

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create stage directories
    for stage_num in range(1, 4):
        stage_dir = output_dir / f"stage{stage_num}"
        stage_dir.mkdir(exist_ok=True)

    # Create logs directory
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    logging.debug(f"Created output directory: {output_dir}")
    return output_dir


def run_stages_1_3(input_id: str, input_text: str, output_dir: Path) -> Dict[str, str]:
    """Run Stages 1-3 pipeline on input document.

    Args:
        input_id: Input document ID
        input_text: Input document text content
        output_dir: Output directory for this input

    Returns:
        Dictionary with stage1_output, stage2_output, stage3_output keys

    Raises:
        Exception: If any stage fails
    """
    logging.info(f"Starting Stages 1-3 pipeline for input: {input_id}")
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

        logging.info("=" * 80)
        logging.info(f"Pipeline completed successfully for input: {input_id}")
        logging.info("=" * 80)

        return results

    except Exception as e:
        logging.error(f"Pipeline failed for input {input_id}: {e}", exc_info=True)
        raise


def generate_test_summary(
    test_results: List[Dict],
    output_dir: Path,
    start_time: datetime,
    end_time: datetime
) -> None:
    """Generate test summary report.

    Args:
        test_results: List of test result dictionaries
        output_dir: Base output directory for integration test
        start_time: Test start timestamp
        end_time: Test end timestamp
    """
    duration = (end_time - start_time).total_seconds()
    success_count = sum(1 for result in test_results if result['status'] == 'success')
    failure_count = len(test_results) - success_count

    summary_file = output_dir / "test-summary.md"

    summary_content = f"""# Stages 1-3 Integration Test Summary

**Test Date:** {start_time.strftime("%Y-%m-%d %H:%M:%S")}
**Duration:** {duration:.2f} seconds
**Total Inputs:** {len(test_results)}
**Successful:** {success_count}
**Failed:** {failure_count}
**Success Rate:** {(success_count / len(test_results) * 100):.1f}%

## Test Results

"""

    for result in test_results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        summary_content += f"### {status_icon} {result['input_id']}\n\n"
        summary_content += f"- **Type:** {result['type']}\n"
        summary_content += f"- **Status:** {result['status']}\n"

        if result['status'] == 'success':
            summary_content += f"- **Stage 1 Output:** {result['stage1_length']} characters\n"
            summary_content += f"- **Stage 2 Output:** {result['stage2_length']} characters\n"
            summary_content += f"- **Stage 3 Output:** {result['stage3_length']} characters\n"
            summary_content += f"- **Output Directory:** `{result['output_dir']}`\n"
        else:
            summary_content += f"- **Error:** {result['error']}\n"

        summary_content += "\n"

    summary_content += f"""## Next Steps

1. **Manual Quality Review:**
   - Review outputs using `docs/stage-1-3-quality-checklist.md`
   - Assess each stage's output quality
   - Document quality issues and improvement opportunities

2. **Prompt Refinement:**
   - Based on quality review findings, refine prompts in:
     - `pipeline/prompts/stage1_prompt.py`
     - `pipeline/prompts/stage2_prompt.py`
     - `pipeline/prompts/stage3_prompt.py`

3. **Re-test:**
   - Run this test again with refined prompts
   - Compare results to initial test
   - Verify quality improvements

## Quality Target

**Success Metric:** 4 out of {len(test_results)} inputs ({80.0}%) should produce "good quality" outputs

---

*Generated by test_stages_1_3.py on {end_time.strftime("%Y-%m-%d %H:%M:%S")}*
"""

    summary_file.write_text(summary_content, encoding='utf-8')
    logging.info(f"Test summary saved: {summary_file}")


def main():
    """Run integration test on all inputs."""
    # Setup basic console logging for test orchestration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    start_time = datetime.now()
    test_results = []

    logging.info("=" * 80)
    logging.info("STAGES 1-3 INTEGRATION TEST")
    logging.info("=" * 80)
    logging.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("")

    try:
        # Load input manifest
        inputs = load_input_manifest()
        logging.info(f"Testing {len(inputs)} input documents\n")

        # Process each input
        for idx, input_doc in enumerate(inputs, 1):
            input_id = input_doc['id']
            input_type = input_doc.get('type', 'unknown')

            logging.info("=" * 80)
            logging.info(f"TEST {idx}/{len(inputs)}: {input_id}")
            logging.info("=" * 80)
            logging.info(f"Type: {input_type}")
            logging.info(f"Description: {input_doc.get('description', 'N/A')}")
            logging.info("")

            try:
                # Create output directory
                output_dir = create_integration_test_output_dir(input_id)

                # Setup logging for this pipeline run
                setup_pipeline_logging(output_dir, console_level=logging.INFO)

                # Load input document
                logging.info(f"Loading input document: {input_doc['file_path']}")
                input_text = load_input_document(input_id)
                logging.info(f"Input loaded: {len(input_text)} characters\n")

                # Run Stages 1-3 pipeline
                results = run_stages_1_3(input_id, input_text, output_dir)

                # Record success
                test_results.append({
                    'input_id': input_id,
                    'type': input_type,
                    'status': 'success',
                    'output_dir': str(output_dir.resolve().relative_to(Path.cwd())),
                    'stage1_length': len(results['stage1_output']),
                    'stage2_length': len(results['stage2_output']),
                    'stage3_length': len(results['stage3_output'])
                })

                logging.info(f"✅ Test {idx} completed successfully\n")

            except Exception as e:
                logging.error(f"❌ Test {idx} failed: {e}\n")

                # Record failure
                test_results.append({
                    'input_id': input_id,
                    'type': input_type,
                    'status': 'failed',
                    'error': str(e)
                })

                # Continue with next input
                continue

        # Generate test summary
        end_time = datetime.now()
        base_output_dir = Path("data/test-outputs/integration-test-stages-1-3")
        generate_test_summary(test_results, base_output_dir, start_time, end_time)

        logging.info("=" * 80)
        logging.info("INTEGRATION TEST COMPLETE")
        logging.info("=" * 80)
        logging.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Duration: {(end_time - start_time).total_seconds():.2f} seconds")
        logging.info(f"Results: {sum(1 for r in test_results if r['status'] == 'success')}/{len(test_results)} successful")
        logging.info("")
        logging.info("Next Steps:")
        logging.info("1. Review test summary: data/test-outputs/integration-test-stages-1-3/test-summary.md")
        logging.info("2. Perform quality review using: docs/stage-1-3-quality-checklist.md")
        logging.info("3. Refine prompts based on findings")
        logging.info("4. Re-run this test to verify improvements")
        logging.info("=" * 80)

        # Exit with appropriate code
        if sum(1 for r in test_results if r['status'] == 'failed') > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logging.error(f"Integration test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
