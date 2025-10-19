#!/bin/bash
# Test 3.2-E2E-003: Verify batch mode backward compatibility
# This script tests that --batch mode still works after Story 3.2 modifications

set -e  # Exit on error

echo "================================================"
echo "E2E Test: Batch Mode Regression (3.2-E2E-003)"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
TEST_TIMEOUT=300  # 5 minutes max for batch mode
TEST_RUN_ID="e2e-batch-test-$(date +%s)"

echo "Test Configuration:"
echo "  - Timeout: ${TEST_TIMEOUT}s"
echo "  - Test Run ID: ${TEST_RUN_ID}"
echo ""

# Function to print test status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        exit 1
    fi
}

# Check if we're in the right directory
if [ ! -f "scripts/run_pipeline.py" ]; then
    echo -e "${RED}✗ FAIL${NC}: Must run from project root directory"
    exit 1
fi

# Determine Python command
# If venv is activated, use python; otherwise use absolute path to venv python
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_CMD="python"
    echo "Using Python from virtual environment: $VIRTUAL_ENV"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
    echo "Using Python from venv/bin/python"
else
    echo -e "${RED}✗ FAIL${NC}: Virtual environment not found. Please activate venv first."
    exit 1
fi

# Step 1: Verify batch mode argument exists in code
echo "Step 1: Verifying --batch argument exists in code..."
grep -q "'\-\-batch'" scripts/run_pipeline.py
print_status $? "Batch mode argument exists in source code"

# Step 2: Test batch mode with mocked LLM calls (dry run simulation)
# For actual regression test, we would run full batch, but that takes too long
# Instead, we verify the code path doesn't error on batch mode invocation
echo ""
echo "Step 2: Testing batch mode code path..."

# Create a minimal test to verify batch mode loads correctly
# We'll use Python to import and verify the batch function exists
$PYTHON_CMD << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.run_pipeline import run_batch, load_input_manifest, get_brand_ids

# Verify functions exist and are callable
assert callable(run_batch), "run_batch function should exist"
assert callable(load_input_manifest), "load_input_manifest function should exist"
assert callable(get_brand_ids), "get_brand_ids function should exist"

# Verify we can load manifest and brands
try:
    manifest = load_input_manifest()
    assert manifest is not None, "Manifest should load"
    assert 'inputs' in manifest, "Manifest should have inputs"

    brands = get_brand_ids()
    assert len(brands) > 0, "Should have at least one brand profile"

    print("✓ Batch mode functions are accessible and manifest/brands load correctly")
except Exception as e:
    print(f"✗ Error loading batch mode components: {e}")
    sys.exit(1)
EOF

print_status $? "Batch mode functions are callable and data loads"

# Step 3: Verify batch mode argument parsing
echo ""
echo "Step 3: Testing batch mode argument parsing..."

$PYTHON_CMD << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Mock sys.argv to test argument parsing
sys.argv = ['run_pipeline.py', '--batch', '--verbose']

from scripts.run_pipeline import parse_arguments

args = parse_arguments()
assert args.batch == True, "Batch flag should be True"
assert args.verbose == True, "Verbose flag should be True"

print("✓ Batch mode arguments parse correctly")
EOF

print_status $? "Batch mode argument parsing works"

# Step 4: Verify backward compatibility - old CLI modes still work
echo ""
echo "Step 4: Testing backward compatibility with --input and --brand modes..."

$PYTHON_CMD << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Test single run mode parsing
sys.argv = ['run_pipeline.py', '--input', 'test-input', '--brand', 'test-brand']

from scripts.run_pipeline import parse_arguments

args = parse_arguments()
assert args.input == 'test-input', "Input argument should be parsed"
assert args.brand == 'test-brand', "Brand argument should be parsed"
assert args.batch == False, "Batch should be False in single mode"

print("✓ Single run mode (--input/--brand) still works")
EOF

print_status $? "Single run mode backward compatibility verified"

# Step 5: Verify new web execution mode doesn't break batch
echo ""
echo "Step 5: Testing new web execution arguments don't conflict..."

$PYTHON_CMD << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Test web execution mode parsing
sys.argv = ['run_pipeline.py', '--input-file', '/tmp/test.pdf', '--brand', 'test-brand', '--run-id', 'run-123', '--selected-track', '1']

from scripts.run_pipeline import parse_arguments

args = parse_arguments()
assert args.input_file == '/tmp/test.pdf', "input_file should be parsed"
assert args.run_id == 'run-123', "run_id should be parsed"
assert args.selected_track == 1, "selected_track should be parsed"
assert args.batch == False, "Batch should be False in web mode"

print("✓ Web execution mode arguments parse correctly")
EOF

print_status $? "Web execution mode doesn't conflict with batch mode"

# Step 6: Verify --retry-failed flag exists
echo ""
echo "Step 6: Verifying --retry-failed argument exists in code..."
grep -q "'\-\-retry-failed'" scripts/run_pipeline.py
print_status $? "Retry-failed argument exists in source code"

# Step 7: Test 3.2-E2E-002 - Verify JSON file created at stage1/inspirations.json
echo ""
echo "Step 7: Testing JSON file creation at stage1/inspirations.json (3.2-E2E-002)..."

$PYTHON_CMD << 'EOF'
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from unittest.mock import Mock
from pipeline.stages.stage1_input_processing import Stage1Chain

# Create test chain
stage1_chain = Mock(spec=Stage1Chain)
stage1_chain.save_output = Stage1Chain.save_output.__get__(stage1_chain)
stage1_chain._parse_tracks = Stage1Chain._parse_tracks.__get__(stage1_chain)
stage1_chain._empty_track = Stage1Chain._empty_track.__get__(stage1_chain)

# Create temp output dir
import tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    output_dir = Path(tmpdir)

    sample_output = """## Track 1: Test Track
Track 1 content.

## Track 2: Second Track
Track 2 content."""

    stage1_chain.save_output(sample_output, output_dir, selected_track=1)

    # Verify JSON file created at correct location
    json_file = output_dir / "stage1" / "inspirations.json"
    assert json_file.exists(), f"JSON file should exist at {json_file}"

    # Verify content is valid JSON
    import json
    with open(json_file, 'r') as f:
        data = json.load(f)

    assert "selected_track" in data, "JSON should have selected_track"
    assert "track_1" in data, "JSON should have track_1"
    assert "track_2" in data, "JSON should have track_2"

    print("✓ JSON file created at stage1/inspirations.json")
EOF

print_status $? "JSON file creation at correct path verified"

# Step 8: Check that batch mode summary generation still works
echo ""
echo "Step 8: Testing batch summary generation (unit level)..."

$PYTHON_CMD << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.run_pipeline import generate_batch_summary

# Create mock results
mock_results = [
    {
        'input_id': 'test-1',
        'brand_id': 'brand-1',
        'success': True,
        'error': None,
        'stage_times': {'stage1': 10.0, 'stage2': 12.0, 'stage3': 15.0, 'stage4': 20.0, 'stage5': 25.0},
        'total_time': 82.0,
        'opportunities_generated': 5,
        'output_dir': 'data/test-outputs/test-1-brand-1'
    }
]

# Generate summary
try:
    generate_batch_summary(
        results=mock_results,
        success_count=1,
        failure_count=0,
        total_tests=1,
        batch_total_time=82.0,
        retry_mode=False
    )

    # Check summary file was created
    summary_file = Path('data/test-outputs/batch-summary.md')
    assert summary_file.exists(), "Summary file should be created"

    # Check content
    content = summary_file.read_text()
    assert 'Batch Execution Summary' in content, "Summary should have header"
    assert 'test-1' in content, "Summary should mention test input"

    print("✓ Batch summary generation works correctly")

except Exception as e:
    print(f"✗ Error generating batch summary: {e}")
    sys.exit(1)
EOF

print_status $? "Batch summary generation works"

# Final summary
echo ""
echo "================================================"
echo -e "${GREEN}✅ ALL BATCH MODE REGRESSION TESTS PASSED${NC}"
echo "================================================"
echo ""
echo "Summary:"
echo "  ✓ Batch mode CLI argument exists"
echo "  ✓ Batch mode functions are callable"
echo "  ✓ Argument parsing works correctly"
echo "  ✓ Backward compatibility maintained (--input/--brand)"
echo "  ✓ New web execution mode doesn't conflict"
echo "  ✓ Retry-failed flag exists"
echo "  ✓ JSON file created at stage1/inspirations.json (3.2-E2E-002)"
echo "  ✓ Batch summary generation works"
echo ""
echo "Note: This is a code-level regression test. For full E2E validation,"
echo "run an actual batch execution with: python scripts/run_pipeline.py --batch"
echo ""

exit 0
