# Gradio Implementation Guide

## Overview

This guide provides detailed implementation patterns for building the Gradio experimentation UI for the Innovation Intelligence System. Extracted from Story 11.1 to keep implementation details separate from requirements.

**Target Story:** 11.1 - Gradio Experimentation UI
**Purpose:** Enable non-technical innovation researchers to run the 7-stage pipeline through a web interface

---

## Progress Tracking Pattern

Use Gradio's `gr.Progress()` component to show real-time pipeline execution status.

```python
import gradio as gr

async def run_pipeline(pdf_file, brand_profile, progress=gr.Progress()):
    """Execute pipeline with real-time progress updates"""

    # Stage 0: PDF Extraction
    progress(0, desc="📄 Extracting PDF text...")
    pdf_text = extract_pdf_text(pdf_file)

    # Stage 1: Brand Enrichment
    progress(0.14, desc="🏢 Stage 0: Enriching brand profile...")
    brand_context = await call_backend("/pipeline/stage0", brand_profile)

    # Stage 2: Trend Decomposition
    progress(0.28, desc="🔍 Stage 1: Extracting trends...")
    trends = await call_backend("/pipeline/stage1", pdf_text)

    # Stage 3: Consumer Insights
    progress(0.42, desc="💡 Stage 2: Generating consumer insights...")
    insights = await call_backend("/pipeline/stage2", trends, brand_context)

    # Stage 4: Technique Matching
    progress(0.57, desc="🎯 Stage 3: Matching innovation techniques...")
    techniques = await call_backend("/pipeline/stage3", insights)

    # Stage 5: Concept Generation
    progress(0.71, desc="💎 Stage 4: Generating concepts...")
    concepts = await call_backend("/pipeline/stage4", techniques)

    # Stage 6: Competitive Intelligence
    progress(0.85, desc="🔎 Stage 5: Searching competitive intel...")
    competitive = await call_backend("/pipeline/stage5", concepts)

    # Stage 7: Opportunity Cards
    progress(1.0, desc="📋 Stage 6: Packaging opportunity cards...")
    cards = await call_backend("/pipeline/stage6", concepts, competitive)

    return (brand_context, trends, insights, techniques, concepts, competitive, cards)
```

**Progress Intervals:**
- 0% - PDF extraction
- 14% - Stage 0 complete
- 28% - Stage 1 complete
- 42% - Stage 2 complete
- 57% - Stage 3 complete
- 71% - Stage 4 complete
- 85% - Stage 5 complete
- 100% - Stage 6 complete

---

## Session State Management

Cache expensive operations (PDF extraction, brand loading) to avoid redundant processing.

```python
import gradio as gr

# Initialize state
cached_data = gr.State({
    "pdf_text": None,
    "pdf_filename": None,
    "brand_profile": None,
    "last_run_outputs": None
})

def extract_and_cache(pdf_file, state):
    """Extract PDF only if not already cached"""

    # Check if already cached
    if state["pdf_text"] is not None and state["pdf_filename"] == pdf_file.name:
        return state, f"✅ Using cached PDF ({len(state['pdf_text'])} chars)"

    # Extract fresh
    pdf_text = extract_pdf_text(pdf_file)
    state["pdf_text"] = pdf_text
    state["pdf_filename"] = pdf_file.name

    return state, f"✅ Extracted PDF: {len(pdf_text)} characters"

def load_and_cache_brand(brand_name, state):
    """Load brand profile and cache"""

    if state["brand_profile"] is not None and state["brand_profile"]["name"] == brand_name:
        return state, state["brand_profile"]

    # Load from YAML
    profile = load_brand_yaml(f"data/brand-profiles/{brand_name}.yaml")
    state["brand_profile"] = profile

    return state, profile

# Wire up event listeners
trend_report.change(
    extract_and_cache,
    inputs=[trend_report, cached_data],
    outputs=[cached_data, extraction_status]
)

brand_dropdown.change(
    load_and_cache_brand,
    inputs=[brand_dropdown, cached_data],
    outputs=[cached_data, brand_profile_display]
)
```

**Cache Invalidation:**
- New PDF upload → clear `pdf_text` and `pdf_filename`
- Brand change → clear `brand_profile`
- New run → preserve cache for re-runs with same inputs

---

## Pre-loaded Examples

Provide demo-ready configurations for quick testing.

```python
import gradio as gr

# Define example configurations
examples = [
    [
        "data/trend-reports/WGSN-FC27-Emotions.pdf",  # PDF file
        "Lactalis Canada",                             # Brand name
        "Dairy & Food Products",                       # Industry
        "Canada",                                      # Geography
        "Milk (2%, whole, skim)\nCheese (cheddar, mozzarella, brie)\nYogurt (Greek, regular, probiotic)"  # Portfolio
    ],
    [
        "data/trend-reports/WGSN-FC27-Emotions.pdf",
        "Decathlon",
        "Sporting Goods Retail",
        "Global",
        "Outdoor gear\nCycling equipment\nFitness apparel\nCamping supplies"
    ],
    [
        "data/trend-reports/Mintel-2025-CPG.pdf",
        "Colombia Sportswear",
        "Outdoor Apparel",
        "USA",
        "Jackets (waterproof, insulated)\nFootwear (hiking boots, trail runners)\nAccessories (hats, gloves, backpacks)"
    ],
    [
        "data/trend-reports/Mintel-2025-CPG.pdf",
        "McCormick USA",
        "Spices & Seasonings",
        "USA",
        "Ground spices\nSpice blends\nSeasoning packets\nExtract & flavorings"
    ]
]

# Add to interface
gr.Examples(
    examples=examples,
    inputs=[
        trend_report_upload,
        brand_name_textbox,
        industry_textbox,
        geography_textbox,
        product_portfolio_textarea
    ],
    label="📚 Demo Examples - Click to Load"
)
```

**Notes:**
- Verify PDF files exist in `/data/trend-reports/` before launch
- Examples should represent diverse industries and geographies
- Update if brand profiles change

---

## Auto-Populate Brand Profiles

Automatically fill form fields when user selects brand from dropdown.

```python
import yaml
from pathlib import Path

def load_brand_profile(brand_name):
    """Load brand profile from YAML and return form field values"""

    # Handle "Custom" option
    if brand_name == "Custom (Manual Entry)":
        return "", "", "", ""

    # Load YAML file
    profile_path = Path(f"data/brand-profiles/{brand_name.lower().replace(' ', '-')}.yaml")

    if not profile_path.exists():
        return "", "", "", f"⚠️ Profile not found: {brand_name}"

    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)

    # Extract fields
    company_name = profile.get("brand_name", "")
    industry = profile.get("industry", "")
    geography = profile.get("country", "")
    portfolio = "\n".join(profile.get("product_portfolio", []))

    return company_name, industry, geography, portfolio

# Wire up event listener
brand_dropdown.change(
    load_brand_profile,
    inputs=brand_dropdown,
    outputs=[brand_name_textbox, industry_textbox, geography_textbox, product_portfolio_textarea]
)
```

**Dropdown Options:**
```python
brand_options = [
    "Lactalis Canada",
    "Decathlon",
    "Colombia Sportswear",
    "McCormick USA",
    "Custom (Manual Entry)"
]
```

---

## Streaming Outputs (Optional)

Yield intermediate results as each stage completes for real-time feedback.

```python
async def run_pipeline_streaming(pdf_file, brand_profile):
    """Stream outputs as each stage completes"""

    # Stage 0
    brand_context = await call_stage_0(brand_profile)
    yield (
        json.dumps(brand_context, indent=2),  # Stage 0
        "",  # Stage 1
        "",  # Stage 2
        "",  # Stage 3
        "",  # Stage 4
        "",  # Stage 5
        "",  # Stage 6
        "✅ Stage 0 complete"  # Status
    )

    # Stage 1
    trends = await call_stage_1(pdf_text)
    yield (
        json.dumps(brand_context, indent=2),
        json.dumps(trends, indent=2),  # Stage 1
        "",
        "",
        "",
        "",
        "",
        "✅ Stage 1 complete"
    )

    # ... continue for all stages

    # Final yield
    yield (
        json.dumps(brand_context, indent=2),
        json.dumps(trends, indent=2),
        json.dumps(insights, indent=2),
        json.dumps(techniques, indent=2),
        json.dumps(concepts, indent=2),
        json.dumps(competitive, indent=2),
        opportunity_cards_md,  # Markdown for Stage 6
        "✅ Pipeline complete!"
    )

# Enable queue for streaming
demo.queue().launch()
```

**Note:** Streaming requires `demo.queue()` to be enabled.

---

## Experiment History Dataframe

Display recent runs with interactive selection to reload outputs.

```python
import gradio as gr
import pandas as pd

def load_experiment_history():
    """Fetch recent experiments from database"""

    experiments = prisma_client.get_experiments(limit=20, order_by="timestamp DESC")

    # Format as dataframe
    df = pd.DataFrame([
        {
            "Run ID": exp["run_id"][:8],  # Short ID
            "Timestamp": exp["timestamp"].strftime("%Y-%m-%d %H:%M"),
            "Brand": exp["brand_profile"]["name"],
            "Quality": exp["quality_tag"].upper(),
            "Stages": f"{exp['stages_completed']}/7"
        }
        for exp in experiments
    ])

    return df

def reload_experiment(df_selection):
    """Reload experiment when row clicked"""

    if df_selection is None or len(df_selection) == 0:
        return ("", "", "", "", "", "", "")

    # Get run_id from selected row
    row_index = df_selection[0]
    run_id = df_selection["Run ID"].iloc[row_index]

    # Fetch full experiment
    experiment = prisma_client.get_experiment_by_run_id(run_id)
    outputs = experiment["stage_outputs"]

    return (
        json.dumps(outputs["stage_0"], indent=2),
        json.dumps(outputs["stage_1"], indent=2),
        json.dumps(outputs["stage_2"], indent=2),
        json.dumps(outputs["stage_3"], indent=2),
        json.dumps(outputs["stage_4"], indent=2),
        json.dumps(outputs["stage_5"], indent=2),
        outputs["stage_6"]  # Markdown
    )

# Create dataframe component
with gr.Tab("📊 Experiment History"):
    refresh_btn = gr.Button("🔄 Refresh History")
    experiments_df = gr.Dataframe(
        value=load_experiment_history(),
        headers=["Run ID", "Timestamp", "Brand", "Quality", "Stages"],
        interactive=True,
        row_count=(10, "dynamic")
    )

    # Wire up events
    refresh_btn.click(load_experiment_history, outputs=experiments_df)
    experiments_df.select(
        reload_experiment,
        inputs=experiments_df,
        outputs=[stage0_output, stage1_output, stage2_output, stage3_output,
                 stage4_output, stage5_output, stage6_output]
    )
```

---

## Queue Configuration for Production

Enable concurrent pipeline executions with queue management.

```python
import gradio as gr

demo.queue(
    max_size=10,  # Max 10 users in queue
    default_concurrency_limit=3,  # Max 3 pipelines running simultaneously
    status_update_rate="auto"  # Auto-adjust status update frequency
).launch(
    server_name="0.0.0.0",  # Bind to all interfaces
    server_port=7860,
    share=False  # Set to True for public Gradio link
)
```

**Production Settings:**
- `max_size=10`: Limit queue to prevent resource exhaustion
- `default_concurrency_limit=3`: Balance throughput vs server load
- `status_update_rate="auto"`: Optimize network traffic

---

## Complete Interface Layout Example

```python
import gradio as gr

with gr.Blocks(title="Innovation Intelligence Pipeline") as demo:

    gr.Markdown("# 🔬 Innovation Intelligence Experimentation Lab")
    gr.Markdown("Upload trend reports and generate innovation concepts for your brand")

    cached_data = gr.State({"pdf_text": None, "brand_profile": None})

    with gr.Row():
        with gr.Column(scale=1):
            # INPUT SECTION
            gr.Markdown("## 📤 Inputs")

            trend_report = gr.File(
                label="Trend Report PDF (max 50MB)",
                file_types=[".pdf"],
                file_count="single"
            )
            extraction_status = gr.Textbox(label="Extraction Status", interactive=False)

            gr.Markdown("### Brand Profile")
            brand_dropdown = gr.Dropdown(
                choices=["Lactalis Canada", "Decathlon", "Colombia Sportswear",
                         "McCormick USA", "Custom (Manual Entry)"],
                label="Select Brand",
                value="Lactalis Canada"
            )

            brand_name = gr.Textbox(label="Company Name")
            industry = gr.Textbox(label="Industry")
            geography = gr.Textbox(label="Geography")
            product_portfolio = gr.TextArea(label="Product Portfolio", lines=5)

            run_button = gr.Button("▶️ Run Pipeline", variant="primary")

        with gr.Column(scale=2):
            # OUTPUT SECTION
            gr.Markdown("## 📊 Pipeline Outputs")

            with gr.Tabs():
                with gr.Tab("Stage 0: Brand Context"):
                    stage0_output = gr.JSON(label="Enriched Brand Context")

                with gr.Tab("Stage 1: Trends"):
                    stage1_output = gr.JSON(label="Extracted Trends")

                with gr.Tab("Stage 2: Insights"):
                    stage2_output = gr.JSON(label="Consumer Insights")

                with gr.Tab("Stage 3: Techniques"):
                    stage3_output = gr.JSON(label="Innovation Techniques")

                with gr.Tab("Stage 4: Concepts"):
                    stage4_output = gr.JSON(label="Directional Concepts")

                with gr.Tab("Stage 5: Competitive"):
                    stage5_output = gr.JSON(label="Competitive Intelligence")

                with gr.Tab("Stage 6: Cards"):
                    stage6_output = gr.Markdown(label="Opportunity Cards")

            # QUALITY TAGGING
            gr.Markdown("### Quality Assessment")
            quality_tag = gr.Radio(
                choices=["Good", "Needs Work", "Failed"],
                label="Quality Tag"
            )
            notes = gr.TextArea(label="Notes", lines=3)
            save_button = gr.Button("💾 Save Experiment")

    # Event listeners
    trend_report.change(extract_and_cache, [trend_report, cached_data], [cached_data, extraction_status])
    brand_dropdown.change(load_brand_profile, brand_dropdown, [brand_name, industry, geography, product_portfolio])

    run_button.click(
        run_pipeline,
        inputs=[trend_report, brand_name, industry, geography, product_portfolio],
        outputs=[stage0_output, stage1_output, stage2_output, stage3_output,
                 stage4_output, stage5_output, stage6_output]
    )

    save_button.click(
        save_experiment,
        inputs=[trend_report, brand_name, quality_tag, notes, stage0_output,
                stage1_output, stage2_output, stage3_output, stage4_output,
                stage5_output, stage6_output],
        outputs=gr.Textbox(label="Save Status")
    )

demo.queue(max_size=10, default_concurrency_limit=3).launch(server_port=7860)
```

---

## Environment Variables

```bash
# Gradio Configuration
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SHARE=false  # Set to true for public link
GRADIO_ANALYTICS_ENABLED=false

# Backend Integration
BACKEND_API_URL=http://localhost:8000
OPENROUTER_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@host:5432/db
```

---

## Testing Checklist

- [ ] PDF upload accepts files up to 50MB
- [ ] Brand dropdown loads all 4 profiles correctly
- [ ] Manual entry works when "Custom" selected
- [ ] Auto-populate fills all fields on brand selection
- [ ] Progress bar updates at each stage
- [ ] All 7 output tabs display correctly
- [ ] Quality tagging saves to database
- [ ] "Good" examples exported to `/backend/experimentation/successful_examples/`
- [ ] Experiment history loads and row selection works
- [ ] Error messages display for PDF parsing failures
- [ ] Error messages display for API failures
- [ ] Cache prevents redundant PDF extraction

---

## References

- **Gradio Documentation**: https://gradio.app/docs
- **Story 11.1**: `/docs/stories/11.1.gradio-experimentation-ui.md`
- **Backend API**: `/backend/app/routes.py`
- **Brand Profiles**: `/data/brand-profiles/*.yaml`
