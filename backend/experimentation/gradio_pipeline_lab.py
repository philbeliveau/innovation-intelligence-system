"""
Innovation Pipeline Experimentation Lab
Following the 7-stage pipeline from simplified.md documentation
With file upload, notes, and full experimentation capabilities
"""

import gradio as gr
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
from pathlib import Path
import PyPDF2
import sqlite3
import uuid

# Import your pipeline stages (adjust imports based on your structure)
# from backend.pipeline.stages import (
#     stage_0_enrich, stage_1_decompose, stage_2_synthesize,
#     stage_3_match, stage_4_generate, stage_5_validate, stage_6_package
# )

# Initialize SQLite for experiment storage
def init_database():
    conn = sqlite3.connect('experiments.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            brand_profile TEXT,
            report_filename TEXT,
            stage_config TEXT,
            outputs TEXT,
            founder_notes TEXT,
            quality_scores TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Stage version registry following simplified.md architecture
STAGE_VERSIONS = {
    "stage_0": {
        "perplexity_enriched": "Full Perplexity search enrichment (slower, more complete)",
        "basic": "Basic enrichment without external search (faster)",
        "manual": "Manual enrichment with user-provided context"
    },
    "stage_1": {
        "multilevel_L1_L4": "Full L1-L4 abstraction ladder extraction",
        "basic_extraction": "Simple trend extraction without abstraction levels",
        "detailed_evidence": "Extraction with supporting evidence and quotes"
    },
    "stage_2": {
        "json_convergence": "Option A: JSON-based convergence (recommended for Phase 1)",
        "graph_reasoning": "Option B: Graph-based multi-hop reasoning (Phase 2)",
        "hybrid": "Start with JSON, escalate to graph if needed"
    },
    "stage_3": {
        "sit_only": "SIT techniques only (5 patterns)",
        "sit_triz": "SIT + TRIZ (45 patterns)",
        "full_frameworks": "SIT + TRIZ + Doblin (55 patterns)"
    },
    "stage_4": {
        "conservative": "Safe, incremental concepts",
        "balanced": "Mix of safe and bold concepts",
        "disruptive": "Bold, category-challenging concepts"
    },
    "stage_5": {
        "basic_search": "Quick competitive search",
        "comprehensive": "Deep competitive intelligence with analogous categories",
        "skip": "Skip competitive validation (faster)"
    },
    "stage_6": {
        "standard": "Standard opportunity card format",
        "executive": "Executive summary format",
        "detailed": "Detailed with full traceability"
    }
}

def extract_pdf_text(pdf_file):
    """Extract text from uploaded PDF"""
    if pdf_file is None:
        return None

    pdf_reader = PyPDF2.PdfReader(pdf_file.name)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def save_experiment(experiment_data: Dict):
    """Save experiment with founder notes to database"""
    conn = sqlite3.connect('experiments.db')
    c = conn.cursor()

    experiment_id = str(uuid.uuid4())
    c.execute('''
        INSERT INTO experiments VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        experiment_id,
        datetime.now().isoformat(),
        json.dumps(experiment_data['brand_profile']),
        experiment_data['report_filename'],
        json.dumps(experiment_data['stage_config']),
        json.dumps(experiment_data['outputs']),
        experiment_data['founder_notes'],
        json.dumps(experiment_data['quality_scores'])
    ))

    conn.commit()
    conn.close()
    return experiment_id

def load_experiment(experiment_id: str):
    """Load a previous experiment"""
    conn = sqlite3.connect('experiments.db')
    c = conn.cursor()
    c.execute('SELECT * FROM experiments WHERE id = ?', (experiment_id,))
    result = c.fetchone()
    conn.close()

    if result:
        return {
            'id': result[0],
            'timestamp': result[1],
            'brand_profile': json.loads(result[2]),
            'report_filename': result[3],
            'stage_config': json.loads(result[4]),
            'outputs': json.loads(result[5]),
            'founder_notes': result[6],
            'quality_scores': json.loads(result[7])
        }
    return None

def get_experiment_history():
    """Get list of all experiments"""
    conn = sqlite3.connect('experiments.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, timestamp, report_filename, founder_notes
        FROM experiments
        ORDER BY timestamp DESC
        LIMIT 20
    ''')
    results = c.fetchall()
    conn.close()

    return [(f"{r[1][:10]} - {r[2]} - {r[3][:50] if r[3] else 'No notes'}", r[0])
            for r in results]

async def run_pipeline_experiment(
    # File inputs
    trend_report,

    # Brand Profile (Stage 0 inputs)
    brand_name,
    industry,
    geography,
    product_portfolio,

    # Stage configurations
    stage_0_version,
    stage_1_version,
    stage_2_version,
    stage_3_version,
    stage_4_version,
    stage_5_version,
    stage_6_version,

    # Experiment controls
    show_intermediate_outputs,
    save_experiment_flag,
    founder_notes
):
    """
    Run the complete 7-stage pipeline with selected configurations
    Following simplified.md architecture
    """

    results = {
        "timestamp": datetime.now().isoformat(),
        "configuration": {
            "stage_0": stage_0_version,
            "stage_1": stage_1_version,
            "stage_2": stage_2_version,
            "stage_3": stage_3_version,
            "stage_4": stage_4_version,
            "stage_5": stage_5_version,
            "stage_6": stage_6_version
        },
        "outputs": {}
    }

    try:
        # Extract PDF text
        report_text = extract_pdf_text(trend_report) if trend_report else "Demo report text"
        report_filename = trend_report.name if trend_report else "demo_report.pdf"

        # Stage 0: Brand Profile Enrichment
        brand_profile = {
            "brand_name": brand_name,
            "industry": industry,
            "geography": geography,
            "product_portfolio": product_portfolio
        }

        # Mock implementation - replace with actual stage calls
        enriched_brand = {
            "brand_name": brand_name,
            "enriched_context": {
                "category": {"sku_count_estimate": "200-300 SKUs"},
                "positioning": {"emotional_territory": "functional"},
                "competitors": {"direct": ["Competitor A", "Competitor B"]},
                "confidence_scores": {"category_context": 0.85}
            }
        }
        results["outputs"]["stage_0"] = enriched_brand

        # Stage 1: Multi-Trend Decomposition
        trends = [
            {
                "trend_name": "Strategic Joy",
                "lifecycle_stage": "EMERGING",
                "abstraction_levels": {
                    "L1": "CPG products that gamify healthy eating",
                    "L2": "Food/beverage brands using playfulness",
                    "L3": "Pleasure activism: reframe obligation as choice",
                    "L4": "Joy as strategic business tool"
                }
            },
            {
                "trend_name": "Witherwill",
                "lifecycle_stage": "ACCELERATING",
                "abstraction_levels": {
                    "L1": "Minimalist bread packaging",
                    "L2": "Food brands reducing choice architecture",
                    "L3": "Simplification as self-care",
                    "L4": "Restraint as luxury"
                }
            }
        ]
        results["outputs"]["stage_1"] = trends

        # Stage 2: Consumer Insight Synthesis
        insights = [
            {
                "insight_statement": "Bread buyers overwhelmed by choice want purchasing to feel like rediscovering childhood simplicity",
                "convergence_pattern": {
                    "primary_trend": "Witherwill",
                    "secondary_trend": "Strategic Joy",
                    "lifecycle_combination": "ACCELERATING + EMERGING"
                }
            }
        ]
        results["outputs"]["stage_2"] = insights

        # Stage 3: Technique Library Matching
        techniques = [
            {
                "matched_techniques": {
                    "sit": {
                        "primary_technique": "Task Unification",
                        "application": "Assign simplification task to packaging/shelf"
                    },
                    "doblin": {
                        "types_activated": ["Product Performance", "Service", "Brand"],
                        "defensibility_score": "MEDIUM"
                    }
                }
            }
        ]
        results["outputs"]["stage_3"] = techniques

        # Stage 4: Directional Concept Generation
        concepts = [
            {
                "concept_name": "Le Guide St-Méthode",
                "concept_tagline": "Rediscover bread joy without choice overwhelm",
                "directional_concept_description": {
                    "what": "In-aisle curated selection tool",
                    "who": "Overwhelmed shoppers",
                    "why_now": "Witherwill trend is ACCELERATING"
                }
            }
        ]
        results["outputs"]["stage_4"] = concepts

        # Stage 5: Competitive Intelligence
        competitive = {
            "competitive_validation": {
                "direct_competitors_found": [],
                "analogous_competitors_found": ["Winc (wine curation)"],
                "competitive_assessment": {"landscape": "OPEN"}
            }
        }
        results["outputs"]["stage_5"] = competitive

        # Stage 6: Opportunity Card Packaging
        opportunity_cards = """
## Opportunity Card: Le Guide St-Méthode

**Tagline:** Rediscover bread joy without choice overwhelm

### Strategic Fit
- **Consumer Insight:** Bread buyers overwhelmed by 47 SKUs want simplicity
- **Trend Convergence:** Witherwill (ACCELERATING) + Strategic Joy (EMERGING)
- **Lifecycle Stage:** ACCELERATING
- **Strategic Posture:** VALIDATE (fast-follower, proven demand)

### Concept Overview
In-aisle curated selection tool that simplifies bread buying through QR code + shelf signage.

### Innovation Mechanism
- **Primary Technique:** SIT Task Unification
- **Defensibility:** MEDIUM (3 Doblin types)

### Investment Required
- **Estimated Budget:** $40K - $60K for 3-store pilot
- **Timeline:** 6 months (pilot + validation)
        """
        results["outputs"]["stage_6"] = opportunity_cards

        # Calculate quality scores
        quality_scores = {
            "convergence_quality": 0.85,
            "brand_relevance": 0.90,
            "concept_clarity": 0.88,
            "feasibility": 0.75,
            "overall": 0.85
        }
        results["quality_scores"] = quality_scores

        # Save experiment if requested
        if save_experiment_flag:
            experiment_data = {
                "brand_profile": brand_profile,
                "report_filename": report_filename,
                "stage_config": results["configuration"],
                "outputs": results["outputs"],
                "founder_notes": founder_notes,
                "quality_scores": quality_scores
            }
            exp_id = save_experiment(experiment_data)
            results["experiment_id"] = exp_id

        # Format outputs based on view preference
        if show_intermediate_outputs:
            return (
                json.dumps(trends, indent=2),  # Stage 1 output
                json.dumps(insights, indent=2),  # Stage 2 output
                json.dumps(concepts, indent=2),  # Stage 4 output
                opportunity_cards,  # Final cards
                json.dumps(quality_scores, indent=2),  # Scores
                f"Experiment saved with ID: {results.get('experiment_id', 'Not saved')}"
            )
        else:
            return (
                "",  # Empty for hidden outputs
                "",
                "",
                opportunity_cards,
                json.dumps(quality_scores, indent=2),
                f"Pipeline complete. Notes saved." if founder_notes else "Pipeline complete."
            )

    except Exception as e:
        error_msg = f"Error in pipeline: {str(e)}"
        return error_msg, "", "", "", "", error_msg

def compare_experiments(exp_id_1, exp_id_2):
    """Compare two experiments side by side"""
    exp1 = load_experiment(exp_id_1)
    exp2 = load_experiment(exp_id_2)

    if not exp1 or not exp2:
        return "Experiment not found"

    comparison = pd.DataFrame({
        'Metric': ['Convergence Quality', 'Brand Relevance', 'Concept Clarity', 'Feasibility', 'Overall'],
        'Experiment 1': list(exp1['quality_scores'].values()),
        'Experiment 2': list(exp2['quality_scores'].values()),
        'Difference': [
            exp2['quality_scores']['convergence_quality'] - exp1['quality_scores']['convergence_quality'],
            exp2['quality_scores']['brand_relevance'] - exp1['quality_scores']['brand_relevance'],
            exp2['quality_scores']['concept_clarity'] - exp1['quality_scores']['concept_clarity'],
            exp2['quality_scores']['feasibility'] - exp1['quality_scores']['feasibility'],
            exp2['quality_scores']['overall'] - exp1['quality_scores']['overall']
        ]
    })

    return comparison

# Initialize database
init_database()

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Innovation Pipeline Lab") as demo:

    gr.Markdown("""
    # 🧪 Innovation Intelligence Pipeline Experimentation Lab
    ### 7-Stage Pipeline Following simplified.md Architecture
    Test different configurations, upload any trend report, and add notes for tracking insights.
    """)

    with gr.Tabs():

        # TAB 1: Main Experimentation
        with gr.TabItem("🚀 Pipeline Experimentation"):
            with gr.Row():

                # LEFT COLUMN: Inputs & Configuration
                with gr.Column(scale=1):
                    gr.Markdown("### 📄 Report Input")
                    trend_report = gr.File(
                        label="Upload Trend Report (PDF)",
                        file_types=[".pdf"],
                        value=None
                    )

                    gr.Markdown("### 🏢 Brand Profile")
                    brand_name = gr.Textbox(
                        label="Brand Name",
                        value="Boulangerie St-Méthode",
                        placeholder="Enter brand name"
                    )
                    industry = gr.Textbox(
                        label="Industry",
                        value="CPG - Bakery",
                        placeholder="e.g., CPG - Dairy, CPG - Snacks"
                    )
                    geography = gr.Textbox(
                        label="Geography",
                        value="North America",
                        placeholder="e.g., North America, Europe"
                    )
                    product_portfolio = gr.Textbox(
                        label="Product Portfolio",
                        value="25 SKUs, healthy bread focus",
                        placeholder="Brief description of products",
                        lines=2
                    )

                    gr.Markdown("### ⚙️ Stage Configuration")

                    with gr.Accordion("Stage 0: Brand Enrichment", open=False):
                        stage_0 = gr.Radio(
                            choices=list(STAGE_VERSIONS["stage_0"].keys()),
                            value="basic",
                            label="Enrichment Method",
                            info="How to enrich brand context"
                        )
                        gr.Markdown(f"<small>{STAGE_VERSIONS['stage_0']['basic']}</small>")

                    with gr.Accordion("Stage 1: Trend Decomposition", open=False):
                        stage_1 = gr.Radio(
                            choices=list(STAGE_VERSIONS["stage_1"].keys()),
                            value="multilevel_L1_L4",
                            label="Extraction Method",
                            info="How to extract trends from report"
                        )

                    with gr.Accordion("Stage 2: Insight Synthesis", open=True):
                        stage_2 = gr.Radio(
                            choices=list(STAGE_VERSIONS["stage_2"].keys()),
                            value="json_convergence",
                            label="Convergence Method",
                            info="How to find trend convergence",
                            interactive=True
                        )
                        gr.Markdown("💡 **Recommended**: JSON convergence for Phase 1")

                    with gr.Accordion("Stage 3: Technique Matching", open=False):
                        stage_3 = gr.Radio(
                            choices=list(STAGE_VERSIONS["stage_3"].keys()),
                            value="sit_only",
                            label="Framework Selection"
                        )

                    with gr.Accordion("Stage 4: Concept Generation", open=True):
                        stage_4 = gr.Radio(
                            choices=list(STAGE_VERSIONS["stage_4"].keys()),
                            value="balanced",
                            label="Creativity Level"
                        )

                    with gr.Accordion("Stage 5: Competitive Intel", open=False):
                        stage_5 = gr.Radio(
                            choices=list(STAGE_VERSIONS["stage_5"].keys()),
                            value="basic_search",
                            label="Validation Depth"
                        )

                    with gr.Accordion("Stage 6: Packaging", open=False):
                        stage_6 = gr.Radio(
                            choices=list(STAGE_VERSIONS["stage_6"].keys()),
                            value="standard",
                            label="Output Format"
                        )

                    gr.Markdown("### 📝 Founder Notes")
                    founder_notes = gr.Textbox(
                        label="Add Your Notes & Observations",
                        placeholder="What worked? What didn't? Ideas for improvement...",
                        lines=4
                    )

                    gr.Markdown("### 🎛️ Controls")
                    show_intermediate = gr.Checkbox(
                        label="Show All Stage Outputs",
                        value=True,
                        info="See intermediate results from each stage"
                    )
                    save_experiment = gr.Checkbox(
                        label="Save This Experiment",
                        value=True,
                        info="Save for later comparison"
                    )

                    run_btn = gr.Button(
                        "🚀 Run Pipeline",
                        variant="primary",
                        size="lg"
                    )

                # RIGHT COLUMN: Outputs
                with gr.Column(scale=2):
                    gr.Markdown("### 📊 Pipeline Outputs")

                    with gr.Tabs():
                        with gr.TabItem("Stage 1: Trends"):
                            stage_1_output = gr.JSON(
                                label="Extracted Trends with L1-L4 Abstraction"
                            )

                        with gr.TabItem("Stage 2: Insights"):
                            stage_2_output = gr.JSON(
                                label="Consumer Insights from Convergence"
                            )

                        with gr.TabItem("Stage 4: Concepts"):
                            stage_4_output = gr.JSON(
                                label="Directional Concepts"
                            )

                        with gr.TabItem("Final Cards"):
                            final_output = gr.Markdown(
                                label="Opportunity Cards"
                            )

                        with gr.TabItem("Quality Scores"):
                            scores_output = gr.JSON(
                                label="Quality Metrics"
                            )

                    status_msg = gr.Textbox(
                        label="Status",
                        interactive=False
                    )

            # Connect the run button
            run_btn.click(
                fn=run_pipeline_experiment,
                inputs=[
                    trend_report, brand_name, industry, geography, product_portfolio,
                    stage_0, stage_1, stage_2, stage_3, stage_4, stage_5, stage_6,
                    show_intermediate, save_experiment, founder_notes
                ],
                outputs=[
                    stage_1_output, stage_2_output, stage_4_output,
                    final_output, scores_output, status_msg
                ]
            )

        # TAB 2: A/B Testing
        with gr.TabItem("🔬 A/B Testing"):
            gr.Markdown("### Compare Different Stage Configurations")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("**Configuration A**")
                    a_stage2 = gr.Radio(
                        ["json_convergence", "graph_reasoning", "hybrid"],
                        label="Stage 2 Method",
                        value="json_convergence"
                    )
                    a_stage4 = gr.Radio(
                        ["conservative", "balanced", "disruptive"],
                        label="Stage 4 Creativity",
                        value="conservative"
                    )

                with gr.Column():
                    gr.Markdown("**Configuration B**")
                    b_stage2 = gr.Radio(
                        ["json_convergence", "graph_reasoning", "hybrid"],
                        label="Stage 2 Method",
                        value="graph_reasoning"
                    )
                    b_stage4 = gr.Radio(
                        ["conservative", "balanced", "disruptive"],
                        label="Stage 4 Creativity",
                        value="disruptive"
                    )

            compare_btn = gr.Button("Run Both Configurations", variant="primary")

            with gr.Row():
                output_a = gr.Markdown(label="Config A Output")
                output_b = gr.Markdown(label="Config B Output")

            comparison_table = gr.Dataframe(
                label="Quality Comparison"
            )

        # TAB 3: Experiment History
        with gr.TabItem("📚 History & Notes"):
            gr.Markdown("### Previous Experiments")

            refresh_btn = gr.Button("🔄 Refresh History")

            experiment_dropdown = gr.Dropdown(
                label="Select Experiment to Review",
                choices=get_experiment_history(),
                interactive=True
            )

            load_btn = gr.Button("Load Selected Experiment")

            loaded_config = gr.JSON(label="Configuration Used")
            loaded_notes = gr.Textbox(label="Founder Notes", lines=5)
            loaded_scores = gr.JSON(label="Quality Scores")
            loaded_output = gr.Markdown(label="Final Output")

            def load_selected_experiment(experiment_choice):
                if not experiment_choice:
                    return {}, "", {}, ""

                exp_id = experiment_choice[1] if isinstance(experiment_choice, tuple) else experiment_choice
                exp = load_experiment(exp_id)

                if exp:
                    return (
                        exp['stage_config'],
                        exp['founder_notes'] or "No notes",
                        exp['quality_scores'],
                        exp['outputs'].get('stage_6', 'No output')
                    )
                return {}, "", {}, ""

            load_btn.click(
                fn=load_selected_experiment,
                inputs=[experiment_dropdown],
                outputs=[loaded_config, loaded_notes, loaded_scores, loaded_output]
            )

            refresh_btn.click(
                fn=lambda: gr.Dropdown(choices=get_experiment_history()),
                outputs=[experiment_dropdown]
            )

        # TAB 4: Documentation
        with gr.TabItem("📖 Documentation"):
            gr.Markdown("""
            ## Pipeline Stages (from simplified.md)

            ### Stage 0: Brand Profile Enrichment
            - Transform minimal brand input (4 fields) into enriched context
            - Options: Perplexity search, basic, or manual enrichment

            ### Stage 1: Multi-Trend Decomposition
            - Extract trends from report with L1-L4 abstraction levels
            - L1: Domain-specific (CPG-actionable)
            - L2: Industry-specific (category patterns)
            - L3: Cross-domain (transferable mechanisms)
            - L4: Universal principles

            ### Stage 2: Consumer Insight Synthesis
            - **JSON Convergence (Recommended)**: Simple pairwise trend comparison
            - **Graph Reasoning**: Complex multi-hop discovery (Phase 2)
            - **Hybrid**: Start simple, escalate if needed

            ### Stage 3: Technique Library Matching
            - Match insights to innovation patterns:
            - SIT: 5 systematic inventive techniques
            - TRIZ: 40 inventive principles
            - Doblin: 10 types of innovation

            ### Stage 4: Directional Concept Generation
            - Generate brand-specific concepts from insights + techniques
            - Conservative: Safe, incremental
            - Balanced: Mix of safe and bold
            - Disruptive: Category-challenging

            ### Stage 5: Competitive Intelligence
            - Search-based validation (never claims "zero competition")
            - Direct, analogous, and competitive searches

            ### Stage 6: Opportunity Card Packaging
            - Format concepts into decision-ready artifacts
            - 30-second pitch structure
            - No-hallucination boundaries

            ## Quality Metrics

            - **Convergence Quality**: How well trends connect (0-1)
            - **Brand Relevance**: Fit with brand positioning (0-1)
            - **Concept Clarity**: How clear the concept is (0-1)
            - **Feasibility**: Implementation practicality (0-1)
            - **Overall**: Weighted average (0-1)
            """)

# Launch the interface
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Creates public URL for founder
        debug=True,
        # auth=("founder", "innovation2025")  # Optional authentication
    )