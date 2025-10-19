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
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
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
    load_brand_profile,
    load_research_data,
    setup_pipeline_logging,
    create_test_output_dir as utils_create_output_dir
)
from pipeline.stages.stage1_input_processing import create_stage1_chain
from pipeline.stages.stage2_signal_amplification import create_stage2_chain
from pipeline.stages.stage3_general_translation import create_stage3_chain
from pipeline.stages.stage4_brand_contextualization import create_stage4_chain
from pipeline.stages.stage5_opportunity_generation import create_stage5_chain

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


def execute_pipeline(
    input_id: str,
    brand_id: str,
    test_num: Optional[int] = None,
    total_tests: Optional[int] = None
) -> Tuple[bool, Dict[str, Any]]:
    """Execute pipeline for given input and brand combination.

    Args:
        input_id: Input document ID
        brand_id: Brand profile ID
        test_num: Optional test number for progress display (e.g., 5 of 24)
        total_tests: Optional total test count for progress display

    Returns:
        Tuple of (success: bool, metadata: dict with execution details)
    """
    start_time = time.time()
    stage_times = {}
    metadata = {
        'input_id': input_id,
        'brand_id': brand_id,
        'success': False,
        'error': None,
        'stage_times': stage_times,
        'total_time': 0,
        'opportunities_generated': 0,
        'output_dir': None
    }

    # Display progress header
    progress_prefix = ""
    if test_num and total_tests:
        progress_prefix = f"[Test {test_num}/{total_tests}] "
        logging.info(f"\n{progress_prefix}Starting: {input_id} → {brand_id}")
    else:
        logging.info(f"Executing pipeline for {input_id} + {brand_id}")

    try:
        # Create output directory using utils function
        output_dir = utils_create_output_dir(input_id, brand_id)
        metadata['output_dir'] = str(output_dir)
        logging.info(f"{progress_prefix}Output directory: {output_dir}")

        # Setup pipeline logging to file
        setup_pipeline_logging(output_dir)

        # Load input document
        logging.info(f"{progress_prefix}Loading input document: {input_id}")
        input_text = load_input_document(input_id)
        logging.info(f"{progress_prefix}Input document loaded: {len(input_text)} characters")

        # Stage 1: Input Processing and Inspiration Identification
        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}STAGE 1/5: Input Processing and Inspiration Identification")
        logging.info(f"{progress_prefix}{'=' * 60}")

        stage1_start = time.time()
        stage1_chain = create_stage1_chain()
        stage1_result = stage1_chain.run(input_text)
        stage1_output = stage1_result[stage1_chain.output_key]

        # Save Stage 1 output
        stage1_file = stage1_chain.save_output(stage1_output, output_dir)
        stage1_time = time.time() - stage1_start
        stage_times['stage1'] = stage1_time
        logging.info(f"{progress_prefix}Stage 1/5 complete ({stage1_time:.1f}s). Output: {stage1_file}")

        # Stage 2: Signal Amplification and Trend Extraction
        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}STAGE 2/5: Signal Amplification and Trend Extraction")
        logging.info(f"{progress_prefix}{'=' * 60}")

        stage2_start = time.time()
        stage2_chain = create_stage2_chain()
        stage2_result = stage2_chain.run(stage1_output)
        stage2_output = stage2_result[stage2_chain.output_key]

        # Save Stage 2 output
        stage2_file = stage2_chain.save_output(stage2_output, output_dir)
        stage2_time = time.time() - stage2_start
        stage_times['stage2'] = stage2_time
        logging.info(f"{progress_prefix}Stage 2/5 complete ({stage2_time:.1f}s). Output: {stage2_file}")

        # Stage 3: General Translation to Universal Lessons
        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}STAGE 3/5: General Translation to Universal Lessons")
        logging.info(f"{progress_prefix}{'=' * 60}")

        stage3_start = time.time()
        stage3_chain = create_stage3_chain()
        stage3_result = stage3_chain.run(stage1_output, stage2_output)
        stage3_output = stage3_result[stage3_chain.output_key]

        # Save Stage 3 output
        stage3_file = stage3_chain.save_output(stage3_output, output_dir)
        stage3_time = time.time() - stage3_start
        stage_times['stage3'] = stage3_time
        logging.info(f"{progress_prefix}Stage 3/5 complete ({stage3_time:.1f}s). Output: {stage3_file}")

        # Stage 4: Brand Contextualization with Research Data
        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}STAGE 4/5: Brand Contextualization with Research Data")
        logging.info(f"{progress_prefix}{'=' * 60}")

        stage4_start = time.time()
        # Load brand profile and research data
        logging.info(f"{progress_prefix}Loading brand profile: {brand_id}")
        brand_profile = load_brand_profile(brand_id)
        logging.info(f"{progress_prefix}Brand profile loaded: {brand_profile.get('company_name', 'N/A')}")

        logging.info(f"{progress_prefix}Loading research data: {brand_id}")
        research_data = load_research_data(brand_id)
        logging.info(f"{progress_prefix}Research data loaded: {len(research_data)} characters")

        stage4_chain = create_stage4_chain()
        stage4_result = stage4_chain.run(stage3_output, brand_profile, research_data)
        stage4_output = stage4_result[stage4_chain.output_key]

        # Save Stage 4 output
        stage4_file = stage4_chain.save_output(stage4_output, output_dir)
        stage4_time = time.time() - stage4_start
        stage_times['stage4'] = stage4_time
        logging.info(f"{progress_prefix}Stage 4/5 complete ({stage4_time:.1f}s). Output: {stage4_file}")

        # Stage 5: Opportunity Generation Chain
        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}STAGE 5/5: Opportunity Generation Chain")
        logging.info(f"{progress_prefix}{'=' * 60}")

        stage5_start = time.time()
        # Extract brand name from brand profile
        brand_name = brand_profile.get('company_name', brand_id)
        logging.info(f"{progress_prefix}Generating opportunities for brand: {brand_name}")
        logging.info(f"{progress_prefix}Based on input source: {input_id}")

        stage5_chain = create_stage5_chain()
        stage5_result = stage5_chain.run(stage4_output, brand_name, input_id)
        opportunities = stage5_result['opportunities']

        logging.info(f"{progress_prefix}Generated {len(opportunities)} opportunities")

        # Render opportunity cards using Jinja2 template
        opportunity_files = stage5_chain.render_opportunity_cards(
            opportunities, brand_name, input_id, output_dir
        )
        logging.info(f"{progress_prefix}Rendered {len(opportunity_files)} opportunity cards")

        # Generate summary file
        summary_file = stage5_chain.generate_summary_file(opportunities, output_dir)
        stage5_time = time.time() - stage5_start
        stage_times['stage5'] = stage5_time
        logging.info(f"{progress_prefix}Stage 5/5 complete ({stage5_time:.1f}s). Summary: {summary_file}")

        # Update metadata
        total_time = time.time() - start_time
        metadata['success'] = True
        metadata['total_time'] = total_time
        metadata['opportunities_generated'] = len(opportunities)

        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}Pipeline execution completed successfully (Stages 1-5)")
        logging.info(f"{progress_prefix}Total time: {total_time:.1f}s")
        logging.info(f"{progress_prefix}Output directory: {output_dir}")
        logging.info(f"{progress_prefix}Generated {len(opportunities)} innovation opportunities")
        logging.info(f"{progress_prefix}{'=' * 60}")
        return True, metadata

    except Exception as e:
        # Update metadata with error
        total_time = time.time() - start_time
        metadata['success'] = False
        metadata['error'] = str(e)
        metadata['total_time'] = total_time

        logging.error(f"{progress_prefix}Pipeline execution failed: {e}", exc_info=True)
        return False, metadata


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
    success, metadata = execute_pipeline(input_id, brand_id)
    return 0 if success else 1


def run_stages_1_to_3(input_id: str) -> Dict[str, Any]:
    """Run Stages 1-3 (input-dependent only) and return outputs.

    Args:
        input_id: Input document ID

    Returns:
        Dictionary with stage outputs and timing
    """
    start_time = time.time()
    result = {
        'stage1_output': None,
        'stage2_output': None,
        'stage3_output': None,
        'stage_times': {},
        'input_text': None
    }

    logging.info(f"Running Stages 1-3 for input: {input_id}")

    # Load input document
    input_text = load_input_document(input_id)
    result['input_text'] = input_text
    logging.info(f"Input document loaded: {len(input_text)} characters")

    # Stage 1
    logging.info("STAGE 1/5: Input Processing and Inspiration Identification")
    stage1_start = time.time()
    stage1_chain = create_stage1_chain()
    stage1_result = stage1_chain.run(input_text)
    stage1_output = stage1_result[stage1_chain.output_key]
    result['stage1_output'] = stage1_output
    result['stage_times']['stage1'] = time.time() - stage1_start
    logging.info(f"Stage 1/5 complete ({result['stage_times']['stage1']:.1f}s)")

    # Stage 2
    logging.info("STAGE 2/5: Signal Amplification and Trend Extraction")
    stage2_start = time.time()
    stage2_chain = create_stage2_chain()
    stage2_result = stage2_chain.run(stage1_output)
    stage2_output = stage2_result[stage2_chain.output_key]
    result['stage2_output'] = stage2_output
    result['stage_times']['stage2'] = time.time() - stage2_start
    logging.info(f"Stage 2/5 complete ({result['stage_times']['stage2']:.1f}s)")

    # Stage 3
    logging.info("STAGE 3/5: General Translation to Universal Lessons")
    stage3_start = time.time()
    stage3_chain = create_stage3_chain()
    stage3_result = stage3_chain.run(stage1_output, stage2_output)
    stage3_output = stage3_result[stage3_chain.output_key]
    result['stage3_output'] = stage3_output
    result['stage_times']['stage3'] = time.time() - stage3_start
    logging.info(f"Stage 3/5 complete ({result['stage_times']['stage3']:.1f}s)")

    total_time = time.time() - start_time
    logging.info(f"✓ Stages 1-3 completed in {total_time:.1f}s")

    return result


def execute_pipeline_stages_4_5(
    input_id: str,
    brand_id: str,
    stages_123_result: Dict[str, Any],
    test_num: Optional[int] = None,
    total_tests: Optional[int] = None
) -> Tuple[bool, Dict[str, Any]]:
    """Execute Stages 4-5 using cached Stages 1-3 outputs.

    Args:
        input_id: Input document ID
        brand_id: Brand profile ID
        stages_123_result: Cached outputs from Stages 1-3
        test_num: Optional test number for progress display
        total_tests: Optional total test count for progress display

    Returns:
        Tuple of (success: bool, metadata: dict with execution details)
    """
    start_time = time.time()
    stage_times = stages_123_result['stage_times'].copy()
    metadata = {
        'input_id': input_id,
        'brand_id': brand_id,
        'success': False,
        'error': None,
        'stage_times': stage_times,
        'total_time': 0,
        'opportunities_generated': 0,
        'output_dir': None
    }

    progress_prefix = f"[Test {test_num}/{total_tests}] " if test_num and total_tests else ""

    try:
        # Create output directory
        output_dir = utils_create_output_dir(input_id, brand_id)
        metadata['output_dir'] = str(output_dir)
        logging.info(f"{progress_prefix}Output directory: {output_dir}")

        # Setup pipeline logging
        setup_pipeline_logging(output_dir)

        # Save cached Stages 1-3 outputs to the output directory
        stage1_output = stages_123_result['stage1_output']
        stage2_output = stages_123_result['stage2_output']
        stage3_output = stages_123_result['stage3_output']

        # Save Stage 1-3 outputs (from cache)
        stage1_chain = create_stage1_chain()
        stage1_chain.save_output(stage1_output, output_dir)

        stage2_chain = create_stage2_chain()
        stage2_chain.save_output(stage2_output, output_dir)

        stage3_chain = create_stage3_chain()
        stage3_chain.save_output(stage3_output, output_dir)

        logging.info(f"{progress_prefix}Stages 1-3 outputs saved (from cache)")

        # Stage 4: Brand Contextualization
        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}STAGE 4/5: Brand Contextualization with Research Data")
        logging.info(f"{progress_prefix}{'=' * 60}")

        stage4_start = time.time()
        brand_profile = load_brand_profile(brand_id)
        logging.info(f"{progress_prefix}Brand profile loaded: {brand_profile.get('company_name', 'N/A')}")

        research_data = load_research_data(brand_id)
        logging.info(f"{progress_prefix}Research data loaded: {len(research_data)} characters")

        stage4_chain = create_stage4_chain()
        stage4_result = stage4_chain.run(stage3_output, brand_profile, research_data)
        stage4_output = stage4_result[stage4_chain.output_key]

        stage4_file = stage4_chain.save_output(stage4_output, output_dir)
        stage4_time = time.time() - stage4_start
        stage_times['stage4'] = stage4_time
        logging.info(f"{progress_prefix}Stage 4/5 complete ({stage4_time:.1f}s). Output: {stage4_file}")

        # Stage 5: Opportunity Generation
        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}STAGE 5/5: Opportunity Generation Chain")
        logging.info(f"{progress_prefix}{'=' * 60}")

        stage5_start = time.time()
        brand_name = brand_profile.get('company_name', brand_id)
        logging.info(f"{progress_prefix}Generating opportunities for brand: {brand_name}")
        logging.info(f"{progress_prefix}Based on input source: {input_id}")

        stage5_chain = create_stage5_chain()
        stage5_result = stage5_chain.run(stage4_output, brand_name, input_id)
        opportunities = stage5_result['opportunities']

        logging.info(f"{progress_prefix}Generated {len(opportunities)} opportunities")

        opportunity_files = stage5_chain.render_opportunity_cards(
            opportunities, brand_name, input_id, output_dir
        )
        logging.info(f"{progress_prefix}Rendered {len(opportunity_files)} opportunity cards")

        summary_file = stage5_chain.generate_summary_file(opportunities, output_dir)
        stage5_time = time.time() - stage5_start
        stage_times['stage5'] = stage5_time
        logging.info(f"{progress_prefix}Stage 5/5 complete ({stage5_time:.1f}s). Summary: {summary_file}")

        # Update metadata
        total_time = time.time() - start_time
        metadata['success'] = True
        metadata['total_time'] = total_time
        metadata['opportunities_generated'] = len(opportunities)

        logging.info(f"{progress_prefix}{'=' * 60}")
        logging.info(f"{progress_prefix}Pipeline completed (Stages 4-5: {total_time:.1f}s)")
        logging.info(f"{progress_prefix}Generated {len(opportunities)} innovation opportunities")
        logging.info(f"{progress_prefix}{'=' * 60}")
        return True, metadata

    except Exception as e:
        total_time = time.time() - start_time
        metadata['success'] = False
        metadata['error'] = str(e)
        metadata['total_time'] = total_time

        logging.error(f"{progress_prefix}Stages 4-5 execution failed: {e}", exc_info=True)
        return False, metadata


def generate_batch_summary(
    results: List[Dict[str, Any]],
    success_count: int,
    failure_count: int,
    total_tests: int,
    batch_total_time: float,
    retry_mode: bool = False
) -> None:
    """Generate batch execution summary report.

    Args:
        results: List of execution metadata dictionaries
        success_count: Number of successful executions
        failure_count: Number of failed executions
        total_tests: Total number of test scenarios
        batch_total_time: Total batch execution time in seconds
        retry_mode: Whether this was a retry execution
    """
    summary_file = Path("data/test-outputs/batch-summary.md")
    summary_file.parent.mkdir(parents=True, exist_ok=True)

    # Calculate statistics
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
    avg_time_per_scenario = batch_total_time / total_tests if total_tests > 0 else 0

    # Calculate average stage times
    stage_times = {'stage1': [], 'stage2': [], 'stage3': [], 'stage4': [], 'stage5': []}
    total_opportunities = 0

    for result in results:
        if result['success']:
            total_opportunities += result.get('opportunities_generated', 0)
            for stage, time_val in result.get('stage_times', {}).items():
                stage_times[stage].append(time_val)

    avg_stage_times = {
        stage: sum(times) / len(times) if times else 0
        for stage, times in stage_times.items()
    }

    # Generate markdown report
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Batch Execution Summary\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Execution Mode:** {'Retry Failed Scenarios' if retry_mode else 'Full Batch'}\n\n")

        f.write("## Overall Statistics\n\n")
        f.write(f"- **Total Scenarios:** {total_tests}\n")
        f.write(f"- **Successful:** {success_count} ({success_rate:.1f}%)\n")
        f.write(f"- **Failed:** {failure_count}\n")
        f.write(f"- **Total Execution Time:** {batch_total_time:.1f}s ({batch_total_time/60:.1f} minutes)\n")
        f.write(f"- **Average Time per Scenario:** {avg_time_per_scenario:.1f}s\n")
        f.write(f"- **Total Opportunities Generated:** {total_opportunities}\n\n")

        f.write("## Stage Performance\n\n")
        f.write("Average execution time per stage:\n\n")
        f.write("| Stage | Average Time (s) | Description |\n")
        f.write("|-------|------------------|-------------|\n")
        f.write(f"| Stage 1 | {avg_stage_times.get('stage1', 0):.1f}s | Input Processing |\n")
        f.write(f"| Stage 2 | {avg_stage_times.get('stage2', 0):.1f}s | Signal Amplification |\n")
        f.write(f"| Stage 3 | {avg_stage_times.get('stage3', 0):.1f}s | General Translation |\n")
        f.write(f"| Stage 4 | {avg_stage_times.get('stage4', 0):.1f}s | Brand Contextualization |\n")
        f.write(f"| Stage 5 | {avg_stage_times.get('stage5', 0):.1f}s | Opportunity Generation |\n\n")

        f.write("## Detailed Results\n\n")
        f.write("| # | Input ID | Brand ID | Status | Time (s) | Opportunities | Output Dir |\n")
        f.write("|---|----------|----------|--------|----------|---------------|------------|\n")

        for idx, result in enumerate(results, start=1):
            status = "✅ Success" if result['success'] else "❌ Failed"
            input_id = result.get('input_id', 'N/A')
            brand_id = result.get('brand_id', 'N/A')
            total_time = result.get('total_time', 0)
            opportunities = result.get('opportunities_generated', 0)
            output_dir = Path(result.get('output_dir', '')).name if result.get('output_dir') else 'N/A'

            f.write(f"| {idx} | {input_id} | {brand_id} | {status} | {total_time:.1f}s | {opportunities} | {output_dir} |\n")

        f.write("\n## Failed Scenarios\n\n")
        if failure_count > 0:
            f.write("The following scenarios failed:\n\n")
            for idx, result in enumerate(results, start=1):
                if not result['success']:
                    f.write(f"### Test {idx}: {result.get('input_id', 'N/A')} → {result.get('brand_id', 'N/A')}\n\n")
                    f.write(f"**Error:** {result.get('error', 'Unknown error')}\n\n")
                    if result.get('output_dir'):
                        f.write(f"**Output Directory:** {result['output_dir']}\n\n")
        else:
            f.write("No failed scenarios. All tests passed! 🎉\n\n")

        f.write("## Success Rate Analysis\n\n")
        if success_rate >= 95:
            f.write("✅ **SUCCESS**: Achieved ≥95% success rate (Target: ≥23/24 scenarios)\n\n")
        else:
            f.write(f"⚠️ **WARNING**: Success rate ({success_rate:.1f}%) below target 95%\n\n")

    logging.info(f"Batch summary report generated: {summary_file}")


def run_batch(manifest: Dict[str, Any], retry_failed: bool = False) -> int:
    """Run pipeline for all input-brand combinations with optimized caching.

    Optimization: Stages 1-3 only depend on input document, so we cache them
    per input and only run Stages 4-5 for each brand combination.

    Args:
        manifest: Input manifest dictionary
        retry_failed: If True, only retry previously failed scenarios

    Returns:
        Exit code (0 for success, 1 if any failures)
    """
    batch_start_time = time.time()
    input_ids = get_input_ids(manifest)
    brand_ids = get_brand_ids()

    if not input_ids:
        logging.error("No input documents found in manifest")
        return 1

    if not brand_ids:
        logging.error("No brand profiles found in data/brand-profiles/")
        return 1

    total_tests = len(input_ids) * len(brand_ids)
    logging.info(f"\n{'='*70}")
    logging.info(f"BATCH EXECUTION START (OPTIMIZED)")
    logging.info(f"Mode: {'RETRY FAILED' if retry_failed else 'FULL BATCH'}")
    logging.info(f"Inputs: {len(input_ids)}, Brands: {len(brand_ids)}, Total: {total_tests}")
    logging.info(f"Optimization: Stages 1-3 cached per input (run {len(input_ids)}x, not {total_tests}x)")
    logging.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"{'='*70}\n")

    # Cache for Stages 1-3 outputs per input
    input_cache = {}

    # Track execution results
    results = []
    success_count = 0
    failure_count = 0
    failed_scenarios = []
    test_num = 0

    # Process each input through Stages 1-3 once, then apply to all brands
    for input_id in input_ids:
        logging.info(f"\n{'='*70}")
        logging.info(f"PROCESSING INPUT: {input_id}")
        logging.info(f"Will apply to {len(brand_ids)} brands: {', '.join(brand_ids)}")
        logging.info(f"{'='*70}\n")

        # Run Stages 1-3 once for this input
        try:
            stages_123_result = run_stages_1_to_3(input_id)
            input_cache[input_id] = stages_123_result
            logging.info(f"✓ Stages 1-3 cached for {input_id}")
        except Exception as e:
            logging.error(f"✗ Failed to process Stages 1-3 for {input_id}: {e}")
            # Mark all brand combinations for this input as failed
            for brand_id in brand_ids:
                test_num += 1
                failed_scenarios.append({
                    'input_id': input_id,
                    'brand_id': brand_id,
                    'error': f"Stages 1-3 failed: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                })
                failure_count += 1
                results.append({
                    'input_id': input_id,
                    'brand_id': brand_id,
                    'success': False,
                    'error': f"Stages 1-3 failed: {str(e)}",
                    'stage_times': {},
                    'total_time': 0,
                    'opportunities_generated': 0,
                    'output_dir': None
                })
            continue

        # Now run Stages 4-5 for each brand using cached Stages 1-3 output
        for brand_id in brand_ids:
            test_num += 1
            logging.info(f"\n{'='*70}")
            logging.info(f"TEST {test_num}/{total_tests}: {input_id} → {brand_id}")
            logging.info(f"{'='*70}")

            try:
                success, metadata = execute_pipeline_stages_4_5(
                    input_id,
                    brand_id,
                    stages_123_result,
                    test_num,
                    total_tests
                )

                results.append(metadata)

                if success:
                    success_count += 1
                else:
                    failure_count += 1
                    failed_scenarios.append({
                        'input_id': input_id,
                        'brand_id': brand_id,
                        'error': metadata.get('error', 'Unknown error'),
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                logging.error(f"✗ Failed: {input_id} + {brand_id}: {e}")
                failure_count += 1
                failed_scenarios.append({
                    'input_id': input_id,
                    'brand_id': brand_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                results.append({
                    'input_id': input_id,
                    'brand_id': brand_id,
                    'success': False,
                    'error': str(e),
                    'stage_times': {},
                    'total_time': 0,
                    'opportunities_generated': 0,
                    'output_dir': None
                })

    batch_end_time = time.time()
    batch_total_time = batch_end_time - batch_start_time

    # Generate batch summary report
    generate_batch_summary(
        results=results,
        success_count=success_count,
        failure_count=failure_count,
        total_tests=total_tests,
        batch_total_time=batch_total_time,
        retry_mode=retry_failed
    )

    # Save failed scenarios for retry
    if failed_scenarios:
        failed_scenarios_file.parent.mkdir(parents=True, exist_ok=True)
        with open(failed_scenarios_file, 'w', encoding='utf-8') as f:
            yaml.dump({
                'failed_scenarios': failed_scenarios,
                'timestamp': datetime.now().isoformat(),
                'total_failed': len(failed_scenarios)
            }, f, default_flow_style=False)
        logging.info(f"\nFailed scenarios saved to: {failed_scenarios_file}")

    # Display final summary
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
    logging.info(f"\n{'='*70}")
    logging.info(f"BATCH EXECUTION COMPLETE")
    logging.info(f"{'='*70}")
    logging.info(f"Total scenarios: {total_tests}")
    logging.info(f"Successful: {success_count} ({success_rate:.1f}%)")
    logging.info(f"Failed: {failure_count}")
    logging.info(f"Total time: {batch_total_time:.1f}s ({batch_total_time/60:.1f}m)")
    logging.info(f"Average per scenario: {batch_total_time/total_tests:.1f}s")
    logging.info(f"Batch summary: data/test-outputs/batch-summary.md")
    logging.info(f"{'='*70}\n")

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

    # Retry failed scenarios flag
    parser.add_argument(
        '--retry-failed',
        action='store_true',
        help='Retry only failed scenarios from previous batch execution. Must be used with --batch.'
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
        # Validate retry-failed flag
        if args.retry_failed and not args.batch:
            logging.error("Error: --retry-failed must be used with --batch")
            logging.error("Run with --help for usage information")
            return 1

        # Load input manifest
        manifest = load_input_manifest()

        # Determine execution mode
        if args.batch:
            # Batch mode
            mode = "BATCH (RETRY FAILED)" if args.retry_failed else "BATCH"
            logging.info(f"Execution mode: {mode}")
            return run_batch(manifest, retry_failed=args.retry_failed)
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
