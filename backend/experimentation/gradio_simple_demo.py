"""
Simplified Demo Version - Can Run Immediately
Replace mock functions with actual pipeline calls
"""

import gradio as gr
import json
from datetime import datetime
import PyPDF2

def extract_pdf_text(pdf_file):
    """Extract text from uploaded PDF"""
    if pdf_file is None:
        return "No file uploaded - using demo text"

    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file.name)
        text = ""
        for page in pdf_reader.pages[:5]:  # First 5 pages for demo
            text += page.extract_text()
        return text[:2000]  # First 2000 chars for display
    except:
        return "Error reading PDF - using demo text"

def run_simple_pipeline(
    trend_report,
    brand_name,
    industry,
    stage_2_method,
    creativity_level,
    founder_notes
):
    """Simplified pipeline for immediate testing"""

    # Extract report text
    report_text = extract_pdf_text(trend_report)

    # Mock Stage 1: Trend Extraction
    trends = {
        "trends_extracted": [
            {
                "name": "Strategic Joy",
                "lifecycle": "EMERGING",
                "L1": "CPG products that gamify healthy eating",
                "L3": "Pleasure activism: reframe obligation as choice"
            },
            {
                "name": "Witherwill",
                "lifecycle": "ACCELERATING",
                "L1": "Minimalist packaging",
                "L3": "Simplification as self-care"
            }
        ],
        "report_preview": report_text[:200] + "..."
    }

    # Mock Stage 2: Insight Synthesis (varies by method)
    if stage_2_method == "json_convergence":
        insight = f"{brand_name} customers want simplicity with joy (JSON method)"
        processing_time = "0.5 seconds"
    else:
        insight = f"{brand_name} customers seek multi-dimensional simplicity (Graph method)"
        processing_time = "2.3 seconds"

    # Mock Stage 4: Concept Generation (varies by creativity)
    if creativity_level < 0.5:
        concept = f"Simple {industry} Selection Guide"
        boldness = "Conservative"
    else:
        concept = f"AI-Powered {industry} Curator"
        boldness = "Disruptive"

    # Generate opportunity card
    opportunity_card = f"""
# Opportunity Card: {concept}

**Brand**: {brand_name}
**Industry**: {industry}

## Consumer Insight
{insight}

## Concept
{concept} - A {boldness.lower()} approach to address consumer needs.

## Innovation Mechanism
- **Method Used**: {stage_2_method}
- **Creativity Level**: {creativity_level:.1%}
- **Processing Time**: {processing_time}

## Trends Identified
- Strategic Joy (EMERGING)
- Witherwill (ACCELERATING)

## Founder Notes
{founder_notes if founder_notes else "No notes added"}

---
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
    """

    return (
        json.dumps(trends, indent=2),
        insight,
        opportunity_card
    )

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🧪 Innovation Pipeline - Quick Demo
    Upload any trend report PDF and experiment with different settings
    """)

    with gr.Row():
        # Left Column: Inputs
        with gr.Column(scale=1):
            gr.Markdown("### Inputs")

            report = gr.File(
                label="📄 Upload Trend Report (PDF)",
                file_types=[".pdf"]
            )

            brand = gr.Textbox(
                label="Brand Name",
                value="Boulangerie St-Méthode"
            )

            industry = gr.Textbox(
                label="Industry",
                value="Bakery"
            )

            gr.Markdown("### Configuration")

            method = gr.Radio(
                ["json_convergence", "graph_reasoning"],
                label="Stage 2: Convergence Method",
                value="json_convergence",
                info="JSON is faster, Graph finds deeper patterns"
            )

            creativity = gr.Slider(
                0, 1, 0.7,
                label="Concept Creativity",
                info="0 = Safe, 1 = Bold"
            )

            notes = gr.Textbox(
                label="📝 Your Notes",
                placeholder="What are you testing? What do you want to see?",
                lines=3
            )

            run_btn = gr.Button("🚀 Run Pipeline", variant="primary")

        # Right Column: Outputs
        with gr.Column(scale=2):
            gr.Markdown("### Outputs")

            with gr.Tabs():
                with gr.TabItem("Trends"):
                    trends_output = gr.JSON()

                with gr.TabItem("Insight"):
                    insight_output = gr.Textbox(lines=3)

                with gr.TabItem("Opportunity Card"):
                    card_output = gr.Markdown()

    # Connect button
    run_btn.click(
        fn=run_simple_pipeline,
        inputs=[report, brand, industry, method, creativity, notes],
        outputs=[trends_output, insight_output, card_output]
    )

    gr.Markdown("""
    ---
    ### Notes
    - This is a demo version with mock pipeline stages
    - Upload any PDF to see text extraction working
    - Try different Stage 2 methods to see how outputs change
    - Adjust creativity slider to see concept variations
    """)

if __name__ == "__main__":
    demo.launch(share=True)