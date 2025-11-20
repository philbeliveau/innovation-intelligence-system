"""
Innovation Pipeline Prompt Experimentation Lab
REAL LLM calls with editable prompts - NO MOCK DATA
"""

import gradio as gr
import json
import asyncio
from datetime import datetime
import PyPDF2
import os
from typing import Dict, List, Any
import sqlite3
import uuid
import httpx

# Default prompts that can be edited in the UI
DEFAULT_PROMPTS = {
    "stage_1": """Extract all emotional trends from this report.
For each trend, provide 4 abstraction levels:

L1 (Domain-Specific): CPG-actionable application
L2 (Industry-Specific): Category-level pattern
L3 (Cross-Domain): Transferable mechanism
L4 (Universal Principle): Fundamental dynamic

Also extract:
- Lifecycle stage (EMERGING/ACCELERATING/PEAKING)
- Current negative emotions (what consumers feel now)
- Aspirational positive emotions (what they want to feel)

Report text:
{report_text}

Output as JSON array with this structure:
[
    {{
        "trend_name": "...",
        "lifecycle_stage": "...",
        "emotional_drivers": {{
            "current_negative": [...],
            "aspirational_positive": [...]
        }},
        "abstraction_levels": {{
            "L1": "...",
            "L2": "...",
            "L3": "...",
            "L4": "..."
        }}
    }}
]""",

    "stage_2_json": """Given these trends and brand context, generate consumer insights using simple convergence.

Trends: {trends}
Brand Context: {brand_context}

Instructions:
1. Find pairs of trends that share emotional drivers
2. For each meaningful convergence, create a brand-specific insight
3. Each insight should address the brand's category challenges
4. Include functional, emotional, and social needs

Output as JSON array:
[
    {{
        "insight_statement": "...",
        "primary_trend": "...",
        "secondary_trend": "...",
        "convergence_rationale": "...",
        "consumer_needs": {{
            "functional": "...",
            "emotional": "...",
            "social": "..."
        }},
        "brand_relevance": "HIGH/MEDIUM/LOW",
        "lifecycle_strategy": "..."
    }}
]""",

    "stage_3": """Match this consumer insight to the most appropriate SIT technique.

Insight: {insight}
Brand Context: {brand_context}

SIT Techniques:
1. Subtraction: Remove essential component, force adaptation
2. Task Unification: Assign new task to existing resource
3. Multiplication: Copy component but change it
4. Attribute Dependency: Correlate previously independent attributes
5. Division: Divide and reorganize

Select the best technique and explain how to apply it specifically to this brand/category.

Output as JSON:
{{
    "primary_technique": "...",
    "application": "...",
    "cpg_example": "...",
    "feasibility": "HIGH/MEDIUM/LOW"
}}""",

    "stage_4": """Generate a directional concept based on this insight and technique.

Insight: {insight}
Technique: {technique}
Brand Context: {brand_context}
Creativity Level: {creativity_level}

Create a concept with:
1. Memorable name (3-5 words)
2. Clear tagline
3. Description of WHAT, WHO, WHY NOW, WHY THIS BRAND
4. No hallucination - don't claim market stats or competitive gaps

Output as JSON:
{{
    "concept_name": "...",
    "tagline": "...",
    "description": {{
        "what": "...",
        "who": "...",
        "why_now": "...",
        "why_this_brand": "..."
    }},
    "estimated_budget": "$40-60K",
    "timeline": "6-12 months"
}}"""
}

class RealPipeline:
    """Pipeline with REAL LLM calls"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

    async def call_llm(self, prompt: str, model: str = "openai/gpt-4-turbo-preview") -> str:
        """REAL LLM call via OpenRouter"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/innovation-pipeline",
                    "X-Title": "Innovation Pipeline Experimentation"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a precise assistant that always returns valid JSON when asked."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=60.0
            )

            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def run_stage(
        self,
        stage_name: str,
        prompt_template: str,
        variables: Dict[str, Any],
        model: str
    ) -> Any:
        """Run a single stage with given prompt - RETURNS REAL DATA"""

        # Format prompt with variables
        formatted_prompt = prompt_template
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            if placeholder in formatted_prompt:
                if isinstance(value, (dict, list)):
                    formatted_prompt = formatted_prompt.replace(
                        placeholder,
                        json.dumps(value, indent=2)
                    )
                else:
                    formatted_prompt = formatted_prompt.replace(
                        placeholder,
                        str(value)
                    )

        # REAL LLM call
        response = await self.call_llm(formatted_prompt, model)

        # Parse JSON response
        try:
            # Try to extract JSON from the response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response

            return json.loads(json_str.strip())
        except:
            # If JSON parsing fails, return the raw response
            return {"raw_response": response, "parsing_failed": True}

def extract_pdf_text(pdf_file):
    """Extract REAL text from uploaded PDF"""
    if pdf_file is None:
        raise ValueError("No PDF file uploaded")

    pdf_reader = PyPDF2.PdfReader(pdf_file.name)
    text = ""

    # Extract text from all pages (or limit for very large PDFs)
    max_pages = min(len(pdf_reader.pages), 50)  # Cap at 50 pages

    for i, page in enumerate(pdf_reader.pages[:max_pages]):
        text += f"\n--- Page {i+1} ---\n"
        text += page.extract_text()

    if not text.strip():
        raise ValueError("No text could be extracted from PDF")

    return text

def save_experiment(data: Dict) -> str:
    """Save REAL experiment data"""
    conn = sqlite3.connect('pipeline_experiments.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            brand_profile TEXT,
            prompts TEXT,
            outputs TEXT,
            notes TEXT,
            model TEXT
        )
    ''')

    exp_id = str(uuid.uuid4())
    c.execute(
        "INSERT INTO experiments VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            exp_id,
            datetime.now().isoformat(),
            json.dumps(data.get('brand_profile', {})),
            json.dumps(data['prompts']),
            json.dumps(data['outputs']),
            data.get('notes', ''),
            data.get('model', 'gpt-4')
        )
    )

    conn.commit()
    conn.close()
    return exp_id

async def run_full_pipeline(
    # File input
    trend_report,

    # Brand inputs
    brand_name,
    industry,
    geography,
    product_portfolio,

    # Prompts for each stage
    prompt_stage_1,
    prompt_stage_2,
    prompt_stage_3,
    prompt_stage_4,

    # Settings
    model_choice,
    creativity_level,

    # Meta
    founder_notes
):
    """Run pipeline with REAL LLM calls and REAL data"""

    pipeline = RealPipeline()
    outputs = {}

    # Extract REAL PDF text
    try:
        report_text = extract_pdf_text(trend_report)
    except Exception as e:
        return f"PDF Error: {str(e)}", "", "", "", "", f"Failed to read PDF: {str(e)}"

    # REAL brand context
    brand_context = {
        "name": brand_name,
        "industry": industry,
        "geography": geography,
        "portfolio": product_portfolio
    }

    try:
        # ========== STAGE 1: REAL Trend Extraction ==========
        print(f"Running Stage 1 with {model_choice}...")

        # Use first 5000 chars of PDF to avoid token limits
        stage_1_output = await pipeline.run_stage(
            "stage_1",
            prompt_stage_1,
            {"report_text": report_text[:5000]},
            model_choice
        )
        outputs["stage_1"] = stage_1_output

        # Check if we got valid trends
        if isinstance(stage_1_output, list):
            trends = stage_1_output
        elif isinstance(stage_1_output, dict) and "trends" in stage_1_output:
            trends = stage_1_output["trends"]
        else:
            return "Stage 1 failed to extract trends", json.dumps(stage_1_output), "", "", "", "Pipeline stopped at Stage 1"

        # ========== STAGE 2: REAL Insight Synthesis ==========
        print(f"Running Stage 2 with {len(trends)} trends...")

        stage_2_output = await pipeline.run_stage(
            "stage_2",
            prompt_stage_2,
            {
                "trends": trends,
                "brand_context": brand_context
            },
            model_choice
        )
        outputs["stage_2"] = stage_2_output

        # Extract insights
        if isinstance(stage_2_output, list):
            insights = stage_2_output
        elif isinstance(stage_2_output, dict) and "insights" in stage_2_output:
            insights = stage_2_output["insights"]
        else:
            insights = [stage_2_output]

        # ========== STAGE 3: REAL Technique Matching ==========
        print("Running Stage 3...")

        first_insight = insights[0] if insights else {"insight_statement": "No insight generated"}

        stage_3_output = await pipeline.run_stage(
            "stage_3",
            prompt_stage_3,
            {
                "insight": first_insight,
                "brand_context": brand_context
            },
            model_choice
        )
        outputs["stage_3"] = stage_3_output

        # ========== STAGE 4: REAL Concept Generation ==========
        print("Running Stage 4...")

        stage_4_output = await pipeline.run_stage(
            "stage_4",
            prompt_stage_4,
            {
                "insight": first_insight,
                "technique": stage_3_output,
                "brand_context": brand_context,
                "creativity_level": creativity_level
            },
            model_choice
        )
        outputs["stage_4"] = stage_4_output

        # Create REAL opportunity card from REAL outputs
        concept_name = stage_4_output.get("concept_name", "Unnamed Concept")
        tagline = stage_4_output.get("tagline", "")
        description = stage_4_output.get("description", {})

        opportunity_card = f"""
# Opportunity Card: {concept_name}

**Tagline:** {tagline}

## Consumer Insight
{first_insight.get('insight_statement', 'No insight statement')}

## Concept Details
- **What:** {description.get('what', 'Not specified')}
- **Who:** {description.get('who', 'Not specified')}
- **Why Now:** {description.get('why_now', 'Not specified')}
- **Why This Brand:** {description.get('why_this_brand', 'Not specified')}

## Innovation Mechanism
**Technique:** {stage_3_output.get('primary_technique', 'Not specified')}
**Application:** {stage_3_output.get('application', 'Not specified')}

## Investment
- **Budget:** {stage_4_output.get('estimated_budget', '$40-60K')}
- **Timeline:** {stage_4_output.get('timeline', '6-12 months')}

## Pipeline Configuration
- **Model:** {model_choice}
- **Creativity Level:** {creativity_level:.0%}
- **Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Founder Notes
{founder_notes if founder_notes else "No notes added"}
        """

        # Save REAL experiment
        exp_data = {
            "brand_profile": brand_context,
            "prompts": {
                "stage_1": prompt_stage_1,
                "stage_2": prompt_stage_2,
                "stage_3": prompt_stage_3,
                "stage_4": prompt_stage_4
            },
            "outputs": outputs,
            "notes": founder_notes,
            "model": model_choice
        }
        exp_id = save_experiment(exp_data)

        return (
            json.dumps(trends, indent=2),
            json.dumps(insights, indent=2),
            json.dumps(stage_3_output, indent=2),
            json.dumps(stage_4_output, indent=2),
            opportunity_card,
            f"✅ Pipeline complete! Experiment ID: {exp_id[:8]}"
        )

    except Exception as e:
        error_msg = f"Pipeline error: {str(e)}"
        print(f"Error: {error_msg}")
        return (
            error_msg,
            json.dumps(outputs.get("stage_1", {})),
            json.dumps(outputs.get("stage_2", {})),
            json.dumps(outputs.get("stage_3", {})),
            "",
            error_msg
        )

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Prompt Lab") as demo:

    gr.Markdown("""
    # 🧪 Innovation Pipeline Prompt Laboratory
    ### REAL LLM calls with editable prompts - Test on actual trend reports
    """)

    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        gr.Markdown("""
        ⚠️ **Warning:** OPENROUTER_API_KEY not found in environment variables.
        Set it before running: `export OPENROUTER_API_KEY=your_key_here`
        """)

    with gr.Tabs():

        # TAB 1: Main Pipeline
        with gr.TabItem("🚀 Pipeline Runner"):

            with gr.Row():
                # LEFT: Inputs
                with gr.Column(scale=1):
                    gr.Markdown("### 📄 Inputs")

                    trend_report = gr.File(
                        label="Upload REAL Trend Report (PDF)",
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
                        value="25 SKUs, healthy bread focus",
                        lines=2
                    )

                    gr.Markdown("### ⚙️ Settings")

                    model_choice = gr.Dropdown(
                        choices=[
                            "openai/gpt-4-turbo-preview",
                            "openai/gpt-4",
                            "openai/gpt-3.5-turbo",
                            "anthropic/claude-3-opus",
                            "anthropic/claude-3-sonnet"
                        ],
                        value="openai/gpt-4-turbo-preview",
                        label="LLM Model (via OpenRouter)"
                    )

                    creativity_level = gr.Slider(
                        0, 1, 0.7,
                        label="Stage 4 Creativity",
                        info="0 = Conservative, 1 = Disruptive"
                    )

                    founder_notes = gr.Textbox(
                        label="📝 Notes",
                        placeholder="What worked? What didn't?",
                        lines=3
                    )

                    run_btn = gr.Button(
                        "🚀 Run REAL Pipeline",
                        variant="primary",
                        size="lg"
                    )

                # MIDDLE: Editable Prompts
                with gr.Column(scale=2):
                    gr.Markdown("### ✏️ Edit Prompts (Changes affect real LLM calls)")

                    with gr.Accordion("Stage 1: Trend Extraction", open=False):
                        prompt_stage_1 = gr.Textbox(
                            value=DEFAULT_PROMPTS["stage_1"],
                            lines=15,
                            label="This prompt extracts trends from your PDF"
                        )

                    with gr.Accordion("Stage 2: Insight Synthesis", open=True):
                        prompt_stage_2 = gr.Textbox(
                            value=DEFAULT_PROMPTS["stage_2_json"],
                            lines=15,
                            label="This prompt generates insights from trends"
                        )

                    with gr.Accordion("Stage 3: Technique Matching", open=False):
                        prompt_stage_3 = gr.Textbox(
                            value=DEFAULT_PROMPTS["stage_3"],
                            lines=15,
                            label="This prompt selects innovation techniques"
                        )

                    with gr.Accordion("Stage 4: Concept Generation", open=False):
                        prompt_stage_4 = gr.Textbox(
                            value=DEFAULT_PROMPTS["stage_4"],
                            lines=15,
                            label="This prompt creates the final concept"
                        )

                # RIGHT: Real Outputs
                with gr.Column(scale=2):
                    gr.Markdown("### 📊 REAL Pipeline Outputs")

                    with gr.Tabs():
                        with gr.TabItem("Stage 1: Trends"):
                            trends_output = gr.JSON(label="Extracted Trends")

                        with gr.TabItem("Stage 2: Insights"):
                            insights_output = gr.JSON(label="Generated Insights")

                        with gr.TabItem("Stage 3: Technique"):
                            technique_output = gr.JSON(label="Selected Technique")

                        with gr.TabItem("Stage 4: Concept"):
                            concept_output = gr.JSON(label="Generated Concept")

                        with gr.TabItem("Final Card"):
                            card_output = gr.Markdown(label="Opportunity Card")

                    status = gr.Textbox(label="Pipeline Status", interactive=False)

            # Connect run button
            run_btn.click(
                fn=run_full_pipeline,
                inputs=[
                    trend_report,
                    brand_name, industry, geography, product_portfolio,
                    prompt_stage_1, prompt_stage_2, prompt_stage_3, prompt_stage_4,
                    model_choice, creativity_level,
                    founder_notes
                ],
                outputs=[
                    trends_output, insights_output, technique_output,
                    concept_output, card_output, status
                ]
            )

# Launch
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )