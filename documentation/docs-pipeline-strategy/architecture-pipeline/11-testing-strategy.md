# 11. Testing Strategy

## 11.1 Test Types

1. **Unit Tests** - Test individual stage chains in isolation
2. **Integration Tests** - Test stage sequences (1-3, 1-4, full pipeline)
3. **Data Validation Tests** - Verify YAML/JSON loading and schema validation
4. **Manual Quality Tests** - Human review using scoring rubrics

## 11.2 Unit Test Example

```python
# tests/test_stage1.py

import pytest
from pathlib import Path
from pipeline.stages.stage1_input_processing import create_chain, save_output
from langchain_openai import ChatOpenAI
from unittest.mock import Mock

def test_stage1_chain_creation():
    """Test Stage 1 chain can be created."""
    llm = Mock(spec=ChatOpenAI)
    chain = create_chain(llm)

    assert chain is not None
    assert chain.output_key == "stage1_output"

def test_stage1_with_mock_input():
    """Test Stage 1 with mock input document."""
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm.return_value = "# Document Overview\nTest output..."

    chain = create_chain(mock_llm)
    result = chain({"input_document": "Mock PDF content about innovation..."})

    assert "stage1_output" in result
    assert len(result["stage1_output"]) > 0

def test_stage1_output_saving(tmp_path):
    """Test Stage 1 output is saved correctly."""
    output_content = "# Document Overview\nTest output..."
    save_output(output_content, tmp_path)

    saved_file = tmp_path / "stage1" / "inspiration-analysis.md"
    assert saved_file.exists()
    assert saved_file.read_text() == output_content
```

## 11.3 Integration Test Example

```python
# tests/test_stages_1_3.py

import pytest
from pipeline.chains import create_pipeline
from pipeline.utils import load_input_document

def test_stages_1_3_integration(tmp_path):
    """Test Stages 1-3 execute successfully in sequence."""

    # Load test input
    input_doc = load_input_document("savannah-bananas")

    # Create pipeline (Stages 1-3 only)
    pipeline = create_pipeline(tmp_path, stages=[1, 2, 3])

    # Execute
    results = pipeline({"input_document": input_doc})

    # Verify outputs exist
    assert (tmp_path / "stage1" / "inspiration-analysis.md").exists()
    assert (tmp_path / "stage2" / "trend-analysis.md").exists()
    assert (tmp_path / "stage3" / "universal-lessons.md").exists()

    # Verify outputs have content
    stage3_content = (tmp_path / "stage3" / "universal-lessons.md").read_text()
    assert "Universal Lessons" in stage3_content
    assert len(stage3_content) > 500  # Non-trivial content
```

## 11.4 Manual Quality Tests

**Quality Checklists:**
- `docs/stage-1-3-quality-checklist.md` - Review inspiration/trend/lesson quality
- `docs/differentiation-rubric.md` - Assess Stage 4 brand differentiation (70%+ unique)
- `docs/opportunity-quality-rubric.md` - Score final opportunities (novelty, actionability, relevance, specificity)

**Manual Test Execution:**
1. Run integration test: `python tests/test_stages_1_3.py`
2. Review outputs using checklist
3. Document quality issues in test results
4. Refine prompts based on findings
5. Re-test and verify improvements

---
