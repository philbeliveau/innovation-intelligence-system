# Implementation Guide: Making the Gradio Lab Functional

## The Problem

The `gradio_pipeline_lab.py` is just a UI skeleton. It doesn't actually run your pipeline - it shows mock data.

## What You Actually Need to Build

### 1. The Real Pipeline Functions

Each stage needs multiple implementations that can be swapped:

```python
# Stage 2 Example - YOU need to write these
async def stage_2_json_convergence(trends, brand_context):
    """
    ACTUAL IMPLEMENTATION NEEDED:
    1. Enumerate all trend pairs (n choose 2)
    2. Find shared emotional drivers
    3. Call LLM to generate insights from convergences
    4. Return structured insights
    """
    # This is where your REAL logic goes
    convergences = find_convergences(trends)

    prompt = build_insight_prompt(convergences, brand_context)

    response = await llm_client.call(prompt)

    insights = parse_insights(response)

    return insights
```

### 2. The Stage Registry (Hot-Swapping)

```python
# This connects stage names to actual functions
STAGE_REGISTRY = {
    "stage_2": {
        "json_convergence": stage_2_json_convergence,  # Your actual function
        "graph_reasoning": stage_2_graph_reasoning,     # Your actual function
        "hybrid": stage_2_hybrid                        # Your actual function
    }
}

# When user selects "json_convergence" in Gradio:
selected_function = STAGE_REGISTRY["stage_2"]["json_convergence"]
result = await selected_function(trends, brand_context)
```

### 3. Connect Gradio to Real Pipeline

In `gradio_pipeline_lab.py`, replace the mock section:

```python
# REPLACE THIS MOCK:
trends = [
    {"trend_name": "Strategic Joy", ...}  # Mock data
]

# WITH THIS REAL CALL:
from backend.experimentation.pipeline_integration import StageRegistry

registry = StageRegistry()
stage_1_func = registry.get_stage_function("stage_1", stage_1_version)
trends = await stage_1_func(report_text)  # Real extraction
```

## Implementation Steps

### Step 1: Start with ONE Stage

Pick Stage 2 (most interesting for experimentation):

1. Write `stage_2_json_convergence()` with real LLM calls
2. Write `stage_2_graph_reasoning()` with different approach
3. Test switching between them in Gradio

### Step 2: Add Quality Scoring

```python
def score_stage_2_output(insights):
    """Score the quality of insights"""
    scores = {
        "convergence_quality": len(insights) / 5.0,  # More insights = better
        "brand_relevance": check_brand_mentioned(insights),
        "lifecycle_alignment": check_lifecycle_strategy(insights),
    }
    return scores
```

### Step 3: Add Real LLM Integration

```python
from openai import AsyncOpenAI

class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

    async def call(self, prompt, model="gpt-4"):
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

## What the Gradio UI Actually Does

The Gradio interface (`gradio_pipeline_lab.py`) provides:

1. **User Interface**: Dropdowns, file upload, text inputs
2. **Experiment Tracking**: Saves configurations and outputs
3. **Comparison Views**: A/B testing layout
4. **Notes System**: Founder can add observations

But it needs YOU to provide:

1. **The actual stage functions** (in `pipeline_integration.py`)
2. **The LLM prompts** for each stage
3. **The parsing logic** to handle LLM responses
4. **The quality scoring** to measure outputs

## Quick Test Without Full Implementation

If you want to test the UI flow without implementing everything:

1. Use `gradio_simple_demo.py` - it has basic mock logic
2. Focus on implementing just Stage 2 variations
3. Keep other stages as mock data
4. This lets you test the concept of hot-swapping

## The Value of This Approach

Once implemented, your founder can:

- Select "JSON convergence" → Run → See Output A
- Select "Graph reasoning" → Run → See Output B
- Compare quality scores
- Add notes: "Graph is 2x slower but finds better insights"
- Save successful configurations
- Apply winning config to production

## Next Immediate Steps

1. **Get LLM client working** with your OpenRouter API key
2. **Implement ONE version** of Stage 2 (json_convergence)
3. **Connect it** to Gradio interface
4. **Test** with real WGSN PDF
5. **Then add** alternative versions for comparison

## File Structure

```
backend/experimentation/
├── gradio_pipeline_lab.py       # UI only (needs connection)
├── pipeline_integration.py      # Real implementations (YOU BUILD THIS)
├── llm_client.py                # LLM calls (YOU BUILD THIS)
├── quality_scoring.py           # Scoring logic (YOU BUILD THIS)
└── stage_prompts/
    ├── stage_1_prompts.py       # Your actual prompts
    ├── stage_2_prompts.py       # Your actual prompts
    └── ...
```

## Why This Separation?

- **UI is done** - Gradio interface is ready
- **Logic is separate** - You can focus on pipeline logic
- **Hot-swappable** - Easy to add new versions
- **Testable** - Each stage function can be unit tested
- **Reusable** - Same functions can be used in production later