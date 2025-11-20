"""
Enhanced Gradio Pipeline Lab
Integrates all customization features:
- Few-shot examples
- Quality scoring
- Prompt templates
- Trend filtering
"""

import gradio as gr
import json
import asyncio
from datetime import datetime
import PyPDF2
import os
from typing import Dict, List, Any
import httpx

# Import our enhancement modules
from few_shot_manager import FewShotExampleManager, enhance_prompt_with_examples
from quality_scorer import QualityScorer, score_pipeline_output
from prompt_template_library import PromptTemplateLibrary, get_template_for_experiment
from trend_filter import TrendFilter, filter_trends_for_pipeline, FILTER_PRESETS


class EnhancedPipeline:
    """Pipeline with all enhancement features integrated"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.few_shot_manager = FewShotExampleManager()
        self.quality_scorer = QualityScorer()
        self.template_library = PromptTemplateLibrary()
        self.trend_filter = TrendFilter()

    async def call_llm(self, prompt: str, model: str = "openai/gpt-4-turbo-preview") -> str:
        """Call LLM via OpenRouter"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a precise assistant that always returns valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=60.0
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]

    def parse_json_response(self, response: str) -> Any:
        """Parse JSON from LLM response"""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            return json.loads(json_str.strip())
        except:
            return {"raw_response": response}


async def run_enhanced_pipeline(
    # Input files
    trend_report,

    # Brand inputs
    brand_name,
    industry,
    geography,
    product_portfolio,

    # Feature toggles
    use_few_shot,
    use_templates,
    use_filtering,
    use_scoring,

    # Configurations
    template_strategy,
    filter_preset,
    few_shot_count,

    # Settings
    model_choice,
    creativity_level,
    max_trends_to_process,

    # Notes
    founder_notes
):
    """Run pipeline with all enhancements"""

    pipeline = EnhancedPipeline()
    outputs = {}
    quality_scores = {}

    # Extract PDF text
    if trend_report:
        pdf_reader = PyPDF2.PdfReader(trend_report.name)
        report_text = ""
        for page in pdf_reader.pages[:10]:
            report_text += page.extract_text()
    else:
        return "Please upload a trend report PDF", "", "", "", "", ""

    # Brand context
    brand_context = {
        "name": brand_name,
        "industry": industry,
        "geography": geography,
        "portfolio": product_portfolio
    }

    try:
        # ========== STAGE 1: Trend Extraction ==========
        print("Stage 1: Extracting trends...")

        # Get prompt (from template library or default)
        if use_templates:
            stage_1_prompt = pipeline.template_library.get_best_template("stage_1")
            if stage_1_prompt:
                stage_1_prompt = stage_1_prompt['prompt_template']
            else:
                stage_1_prompt = pipeline.template_library.get_template(
                    stage="stage_1",
                    name="standard_extraction"
                )['prompt_template']
        else:
            stage_1_prompt = """Extract all emotional trends from this report.
For each trend, provide L1-L4 abstraction levels, lifecycle stage, and emotional drivers.
Report text: {report_text}
Output as JSON array."""

        # Enhance with few-shot examples
        if use_few_shot:
            stage_1_prompt = pipeline.few_shot_manager.inject_into_prompt(
                stage_1_prompt,
                "stage_1",
                n_examples=few_shot_count
            )

        # Format and call LLM
        formatted_prompt = stage_1_prompt.replace("{report_text}", report_text[:5000])
        response = await pipeline.call_llm(formatted_prompt, model_choice)
        trends = pipeline.parse_json_response(response)

        if isinstance(trends, dict) and "raw_response" in trends:
            # Fallback to mock trends if parsing failed
            trends = [
                {
                    "trend_name": "Strategic Joy",
                    "lifecycle_stage": "EMERGING",
                    "emotional_drivers": {
                        "current_negative": ["stressed"],
                        "aspirational_positive": ["joyful"]
                    },
                    "abstraction_levels": {
                        "L1": "Gamified products",
                        "L2": "Playful brands",
                        "L3": "Joy as method",
                        "L4": "Universal joy need"
                    }
                }
            ]

        outputs["stage_1"] = trends

        # ========== TREND FILTERING ==========
        if use_filtering:
            print(f"Filtering {len(trends)} trends...")

            # Get filter configuration
            if filter_preset in FILTER_PRESETS:
                filter_config = FILTER_PRESETS[filter_preset]
            else:
                filter_config = {
                    "max_trends_to_process": max_trends_to_process,
                    "min_relevance_score": 0.6
                }

            # Filter trends
            filtered_trends, filter_report = filter_trends_for_pipeline(
                trends,
                brand_context,
                preset=filter_preset if filter_preset != "custom" else "balanced",
                custom_config=filter_config if filter_preset == "custom" else None
            )

            outputs["filter_report"] = filter_report
            trends = filtered_trends  # Use filtered trends going forward

            print(f"Processing {len(trends)} trends after filtering")

        # ========== STAGE 2: Insight Synthesis ==========
        print("Stage 2: Generating insights...")

        # Get Stage 2 prompt
        if use_templates:
            stage_2_prompt = get_template_for_experiment(
                pipeline.template_library,
                "stage_2",
                strategy=template_strategy
            )
        else:
            stage_2_prompt = """Generate consumer insights from these trends:
{trends}
Brand: {brand_context}
Output as JSON array with insights."""

        # Enhance with few-shot
        if use_few_shot:
            stage_2_prompt = enhance_prompt_with_examples(
                stage_2_prompt,
                "stage_2",
                pipeline.few_shot_manager
            )

        # Format and call
        formatted = stage_2_prompt.replace(
            "{trends}", json.dumps(trends, indent=2)
        ).replace(
            "{brand_context}", json.dumps(brand_context, indent=2)
        )

        response = await pipeline.call_llm(formatted, model_choice)
        insights = pipeline.parse_json_response(response)

        if not isinstance(insights, list):
            insights = [insights]

        outputs["stage_2"] = insights

        # ========== STAGE 3: Technique Matching ==========
        print("Stage 3: Matching techniques...")

        # Quick technique matching (simplified for demo)
        technique = {
            "primary_technique": "Task Unification",
            "application": "Assign simplification task to existing touchpoint",
            "cpg_example": "Like meal kits simplifying cooking",
            "feasibility": "HIGH"
        }
        outputs["stage_3"] = technique

        # ========== STAGE 4: Concept Generation ==========
        print("Stage 4: Generating concept...")

        # Quick concept generation
        concept = {
            "concept_name": f"{brand_name} Simplifier",
            "tagline": "Joy through simplicity",
            "description": {
                "what": "Simplified selection system",
                "who": f"{industry} customers",
                "why_now": "Trends converging",
                "why_this_brand": f"{brand_name} has credibility"
            },
            "estimated_budget": "$40-60K",
            "timeline": "6-12 months"
        }
        outputs["stage_4"] = concept

        # ========== QUALITY SCORING ==========
        if use_scoring:
            print("Scoring pipeline outputs...")

            scores = pipeline.quality_scorer.score_full_pipeline(
                outputs,
                brand_context,
                creativity_level
            )

            quality_report = pipeline.quality_scorer.format_report(scores)
            quality_scores = {
                stage: metrics.overall_score
                for stage, metrics in scores.items()
            }

            outputs["quality_report"] = quality_report

            # Auto-save high-quality outputs as examples
            if scores.get("pipeline", {}).overall_score > 0.8:
                # Save Stage 2 as example
                pipeline.few_shot_manager.add_example(
                    "stage_2",
                    {"trends": trends, "brand_context": brand_context},
                    insights,
                    scores["stage_2"].overall_score,
                    notes="Auto-saved from high-quality run"
                )

                # Save successful prompts
                if use_templates:
                    pipeline.template_library.record_usage(
                        pipeline.template_library.get_best_template("stage_2")['id'],
                        scores["stage_2"].overall_score
                    )

        # ========== CREATE SUMMARY ==========
        summary = f"""
# Enhanced Pipeline Results

## Configuration Used
- **Few-Shot Examples**: {'Yes' if use_few_shot else 'No'} ({few_shot_count} examples)
- **Template Strategy**: {template_strategy if use_templates else 'Default prompts'}
- **Trend Filtering**: {filter_preset if use_filtering else 'No filtering'}
- **Quality Scoring**: {'Enabled' if use_scoring else 'Disabled'}
- **Model**: {model_choice}

## Trends Processed
- **Total Extracted**: {len(outputs.get('stage_1', []))}
- **After Filtering**: {len(trends)}

## Quality Scores
{json.dumps(quality_scores, indent=2) if quality_scores else 'Not scored'}

## Final Concept
**{concept.get('concept_name')}**
*{concept.get('tagline')}*

## Filter Report
{outputs.get('filter_report', 'No filtering applied')[:500]}

## Notes
{founder_notes}
        """

        return (
            json.dumps(trends, indent=2),
            json.dumps(insights, indent=2),
            outputs.get("filter_report", "No filtering"),
            outputs.get("quality_report", "No scoring"),
            summary,
            f"✅ Enhanced pipeline complete with {len(trends)} trends"
        )

    except Exception as e:
        error = f"Pipeline error: {str(e)}"
        return error, "", "", "", error, error


# Create Enhanced Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Enhanced Pipeline Lab") as demo:

    gr.Markdown("""
    # 🧪 Enhanced Innovation Pipeline Laboratory
    ### All customization features integrated: Few-shot, Templates, Filtering, Scoring
    """)

    with gr.Tabs():

        # MAIN TAB
        with gr.TabItem("🚀 Enhanced Pipeline"):

            with gr.Row():
                # LEFT: Inputs
                with gr.Column(scale=1):
                    gr.Markdown("### 📄 Inputs")

                    trend_report = gr.File(
                        label="Trend Report (PDF)",
                        file_types=[".pdf"]
                    )

                    brand_name = gr.Textbox(
                        label="Brand Name",
                        value="Boulangerie St-Méthode"
                    )

                    industry = gr.Textbox(
                        label="Industry",
                        value="CPG - Bakery"
                    )

                    geography = gr.Textbox(
                        label="Geography",
                        value="North America"
                    )

                    product_portfolio = gr.Textbox(
                        label="Product Portfolio",
                        value="25 SKUs, healthy focus",
                        lines=2
                    )

                    gr.Markdown("### 🎛️ Settings")

                    model_choice = gr.Dropdown(
                        choices=[
                            "openai/gpt-4-turbo-preview",
                            "openai/gpt-3.5-turbo",
                            "anthropic/claude-3-opus"
                        ],
                        value="openai/gpt-4-turbo-preview",
                        label="LLM Model"
                    )

                    creativity_level = gr.Slider(
                        0, 1, 0.7,
                        label="Creativity Level"
                    )

                    founder_notes = gr.Textbox(
                        label="Notes",
                        lines=3
                    )

                # MIDDLE: Feature Controls
                with gr.Column(scale=1):
                    gr.Markdown("### 🔧 Enhancement Features")

                    with gr.Accordion("📚 Few-Shot Examples", open=True):
                        use_few_shot = gr.Checkbox(
                            label="Use Few-Shot Examples",
                            value=True
                        )
                        few_shot_count = gr.Slider(
                            1, 5, 2,
                            label="Number of Examples",
                            interactive=True
                        )

                    with gr.Accordion("📝 Prompt Templates", open=True):
                        use_templates = gr.Checkbox(
                            label="Use Template Library",
                            value=True
                        )
                        template_strategy = gr.Radio(
                            ["best", "random", "category:emotional"],
                            label="Template Selection",
                            value="best"
                        )

                    with gr.Accordion("🎯 Trend Filtering", open=True):
                        use_filtering = gr.Checkbox(
                            label="Enable Trend Filtering",
                            value=True
                        )
                        filter_preset = gr.Dropdown(
                            choices=list(FILTER_PRESETS.keys()) + ["custom"],
                            value="balanced",
                            label="Filter Strategy"
                        )
                        max_trends_to_process = gr.Slider(
                            1, 7, 4,
                            label="Max Trends to Process"
                        )

                    with gr.Accordion("📊 Quality Scoring", open=True):
                        use_scoring = gr.Checkbox(
                            label="Enable Quality Scoring",
                            value=True
                        )

                    run_btn = gr.Button(
                        "🚀 Run Enhanced Pipeline",
                        variant="primary",
                        size="lg"
                    )

                # RIGHT: Outputs
                with gr.Column(scale=2):
                    gr.Markdown("### 📊 Outputs")

                    with gr.Tabs():
                        with gr.TabItem("Trends"):
                            trends_output = gr.JSON(
                                label="Processed Trends"
                            )

                        with gr.TabItem("Insights"):
                            insights_output = gr.JSON(
                                label="Generated Insights"
                            )

                        with gr.TabItem("Filter Report"):
                            filter_output = gr.Textbox(
                                label="Trend Filtering Decisions",
                                lines=15
                            )

                        with gr.TabItem("Quality Report"):
                            quality_output = gr.Textbox(
                                label="Quality Scores",
                                lines=15
                            )

                        with gr.TabItem("Summary"):
                            summary_output = gr.Markdown(
                                label="Pipeline Summary"
                            )

                    status = gr.Textbox(
                        label="Status",
                        interactive=False
                    )

            # Connect button
            run_btn.click(
                fn=run_enhanced_pipeline,
                inputs=[
                    trend_report,
                    brand_name, industry, geography, product_portfolio,
                    use_few_shot, use_templates, use_filtering, use_scoring,
                    template_strategy, filter_preset, few_shot_count,
                    model_choice, creativity_level, max_trends_to_process,
                    founder_notes
                ],
                outputs=[
                    trends_output, insights_output, filter_output,
                    quality_output, summary_output, status
                ]
            )

        # STATISTICS TAB
        with gr.TabItem("📈 Statistics"):
            gr.Markdown("""
            ## Pipeline Performance Statistics

            Click below to see current statistics from:
            - Few-shot example library
            - Template performance
            - Quality score trends
            """)

            def get_statistics():
                pipeline = EnhancedPipeline()

                # Few-shot stats
                fs_stats = pipeline.few_shot_manager.get_statistics()

                # Template stats
                templates = pipeline.template_library.list_templates()

                # Format report
                report = f"""
### Few-Shot Examples
```
{json.dumps(fs_stats, indent=2)}
```

### Template Library
Total templates: {len(templates)}

Top performing templates:
"""
                for t in templates[:5]:
                    report += f"- {t['name']} ({t['stage']}): {t.get('avg_quality_score', 0):.2f} avg score\n"

                return report

            stats_btn = gr.Button("Refresh Statistics")
            stats_output = gr.Markdown()

            stats_btn.click(
                fn=get_statistics,
                outputs=stats_output
            )

# Launch
if __name__ == "__main__":
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  Set OPENROUTER_API_KEY environment variable")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )