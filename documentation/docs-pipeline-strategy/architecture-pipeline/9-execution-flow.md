# 9. Execution Flow

## 9.1 Main Execution Script

```python
# run_pipeline.py

import argparse
import logging
from pathlib import Path
from datetime import datetime

from pipeline.chains import create_pipeline
from pipeline.utils import (
    load_input_document,
    load_brand_profile,
    load_research_data,
    create_output_directory,
    setup_logging
)

def main():
    parser = argparse.ArgumentParser(description="Innovation Intelligence Pipeline")
    parser.add_argument("--input", help="Input document ID (from input-manifest.yaml)")
    parser.add_argument("--brand", help="Brand profile ID (without .yaml extension)")
    parser.add_argument("--batch", action="store_true", help="Run all 20 test scenarios")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.batch:
        run_batch_tests(args.verbose)
    elif args.input and args.brand:
        run_single_test(args.input, args.brand, args.verbose)
    else:
        parser.print_help()
        exit(1)

def run_single_test(input_id, brand_id, verbose=False):
    """Execute pipeline for single input/brand combination."""

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = create_output_directory(input_id, brand_id, timestamp)

    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(output_dir / "logs", log_level)

    logging.info(f"Starting pipeline: {input_id} + {brand_id}")

    try:
        # Load inputs
        input_doc = load_input_document(input_id)
        brand_profile = load_brand_profile(brand_id)
        research_data = load_research_data(brand_id)

        # Create and execute pipeline
        pipeline = create_pipeline(output_dir)

        results = pipeline({
            "input_document": input_doc,
            "brand_profile": brand_profile,
            "research_data": research_data,
            "brand_id": brand_id,
            "input_id": input_id
        })

        logging.info(f"Pipeline completed successfully")
        logging.info(f"Results saved to: {output_dir}")

        return results

    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise

def run_batch_tests(verbose=False):
    """Execute all 20 test scenarios (5 inputs × 4 brands)."""

    from pipeline.utils import load_input_manifest

    manifest = load_input_manifest()
    brands = ["lactalis-canada", "mccormick-usa", "columbia-sportswear", "decathlon"]

    results = []
    total_tests = len(manifest["inputs"]) * len(brands)

    print(f"Starting batch execution: {total_tests} tests")

    for i, input_item in enumerate(manifest["inputs"], 1):
        for j, brand_id in enumerate(brands, 1):
            test_num = (i - 1) * len(brands) + j
            print(f"\n[{test_num}/{total_tests}] Running: {input_item['id']} + {brand_id}")

            try:
                result = run_single_test(input_item["id"], brand_id, verbose)
                results.append({
                    "input": input_item["id"],
                    "brand": brand_id,
                    "status": "success",
                    "output_dir": result["output_dir"]
                })
            except Exception as e:
                logging.error(f"Test failed: {input_item['id']} + {brand_id}: {str(e)}")
                results.append({
                    "input": input_item["id"],
                    "brand": brand_id,
                    "status": "failed",
                    "error": str(e)
                })

    # Generate batch summary
    generate_batch_summary(results)

    print(f"\nBatch execution complete: {sum(1 for r in results if r['status'] == 'success')}/{total_tests} successful")

if __name__ == "__main__":
    main()
```

## 9.2 Execution Commands

**Single Test:**
```bash
python run_pipeline.py --input savannah-bananas --brand lactalis-canada
```

**Batch Execution:**
```bash
python run_pipeline.py --batch
```

**Debug Mode:**
```bash
python run_pipeline.py --input savannah-bananas --brand lactalis-canada --verbose
```

## 9.3 Execution Time Expectations

| Operation | Expected Time |
|-----------|--------------|
| Single test (all 5 stages) | 5-10 minutes |
| Batch execution (20 tests) | 100-200 minutes (1.5-3.5 hours) |
| Stage 1-3 (per test) | 2-4 minutes |
| Stage 4 (per test) | 1-2 minutes |
| Stage 5 (per test) | 2-4 minutes |

**Rationale:** Sequential LLM API calls with ~30-60 second latency per stage.

---
