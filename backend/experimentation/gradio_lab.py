"""
Gradio Experimentation Lab - Production Interface
Story 11.1: Gradio Experimentation UI

Provides web interface for non-technical innovation researchers to:
- Upload trend reports (PDF, max 50MB)
- Select or configure brand profiles
- Run 7-stage extraction pipeline
- Review generated opportunity concepts
- Tag quality for few-shot learning
"""

import gradio as gr
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import PyPDF2
import yaml
import httpx
import os
import uuid

# Import few-shot storage (Story 11.3a)
# Note: This import will work once few_shot_manager.py is created in Story 11.3a
try:
    from backend.experimentation.few_shot_manager import FileSystemExampleStorage
except ImportError:
    # Graceful degradation if few_shot_manager not yet implemented
    FileSystemExampleStorage = None

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL")

class GradioLab:
    """Main Gradio experimentation interface"""

    def __init__(self):
        self.backend_url = BACKEND_API_URL
        self.brand_profiles_dir = Path("../../data/brand-profiles")

    def extract_pdf_text(self, pdf_file) -> Tuple[str, str]:
        """Extract text from PDF file with validation

        Args:
            pdf_file: Gradio File object

        Returns:
            Tuple of (extracted_text, status_message)

        Raises:
            Exception: If PDF parsing fails
        """
        if pdf_file is None:
            return "", "No file uploaded"

        try:
            # Validate file size (50MB limit)
            file_size = os.path.getsize(pdf_file.name)
            if file_size > 50 * 1024 * 1024:
                return "", f"Error: File too large: {file_size / (1024*1024):.1f}MB (max 50MB)"

            # Extract text using PyPDF2
            with open(pdf_file.name, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)

                text_parts = []
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())

                full_text = "\n\n".join(text_parts)

                if len(full_text.strip()) < 100:
                    return "", f"Warning: Extracted text too short ({len(full_text)} chars) - PDF may be image-based"

                return full_text, f"Success: Extracted {len(full_text)} characters from {num_pages} pages"

        except Exception as e:
            return "", f"Error: PDF extraction failed: {str(e)}"

    def load_available_brands(self) -> List[str]:
        """Load list of available brand profiles from YAML files

        Returns:
            List of brand names
        """
        brands = []

        if not self.brand_profiles_dir.exists():
            return ["Custom (Manual Entry)"]

        for yaml_file in self.brand_profiles_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    profile = yaml.safe_load(f)
                    brand_name = profile.get("brand_name", yaml_file.stem)
                    brands.append(brand_name)
            except Exception:
                continue

        brands.append("Custom (Manual Entry)")
        return sorted(brands)

    def load_brand_profile_from_yaml(self, brand_name: str) -> Tuple[str, str, str, str]:
        """Load brand profile from YAML file

        Args:
            brand_name: Brand name from dropdown

        Returns:
            Tuple of (company_name, industry, geography, product_portfolio)
        """
        if brand_name == "Custom (Manual Entry)":
            return "", "", "", ""

        # Search for matching YAML file
        for yaml_file in self.brand_profiles_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    profile = yaml.safe_load(f)

                    if profile.get("brand_name") == brand_name:
                        company_name = profile.get("brand_name", "")
                        industry = profile.get("industry", "")
                        geography = profile.get("country", "")
                        portfolio_list = profile.get("product_portfolio", [])
                        portfolio = "\n".join(portfolio_list) if isinstance(portfolio_list, list) else str(portfolio_list)

                        return company_name, industry, geography, portfolio

            except Exception:
                continue

        return "", "", "", f"Warning: Brand profile not found: {brand_name}"

    def load_brand_profile_from_file(self, yaml_file) -> Tuple[str, str, str, str, str]:
        """Load brand profile from uploaded YAML file

        Args:
            yaml_file: Gradio File object

        Returns:
            Tuple of (company_name, industry, geography, product_portfolio, status_message)
        """
        if yaml_file is None:
            return "", "", "", "", ""

        try:
            with open(yaml_file.name, 'r') as f:
                profile = yaml.safe_load(f)

            # Validate required fields
            required_fields = ["brand_name", "country", "industry", "product_portfolio"]
            missing_fields = [field for field in required_fields if field not in profile]

            if missing_fields:
                return "", "", "", "", f"Warning: Missing required fields: {', '.join(missing_fields)}"

            company_name = profile.get("brand_name", "")
            industry = profile.get("industry", "")
            geography = profile.get("country", "")
            portfolio_list = profile.get("product_portfolio", [])
            portfolio = "\n".join(portfolio_list) if isinstance(portfolio_list, list) else str(portfolio_list)

            return company_name, industry, geography, portfolio, f"Success: Loaded profile: {company_name}"

        except yaml.YAMLError as e:
            return "", "", "", "", f"Error: Invalid YAML format: {str(e)}"
        except Exception as e:
            return "", "", "", "", f"Error: Failed to load profile: {str(e)}"

    async def run_pipeline(
        self,
        pdf_text: str,
        brand_name: str,
        industry: str,
        geography: str,
        product_portfolio: str,
        progress=gr.Progress()
    ) -> Tuple[str, str, str, str, str, str, str, str]:
        """Execute 7-stage pipeline with real-time progress

        Args:
            pdf_text: Extracted PDF text
            brand_name: Company name
            industry: Industry sector
            geography: Geographic market
            product_portfolio: Product list
            progress: Gradio Progress tracker

        Returns:
            Tuple of (stage0, stage1, stage2, stage3, stage4, stage5, stage6, status_message)
        """

        # Validate inputs
        if not pdf_text or len(pdf_text.strip()) < 100:
            error_msg = "Error: Please upload a valid PDF document first"
            return "", "", "", "", "", "", "", error_msg

        if not brand_name or not industry or not geography:
            error_msg = "Error: Please fill in all required brand fields"
            return "", "", "", "", "", "", "", error_msg

        # Generate run ID
        run_id = str(uuid.uuid4())[:8]

        try:
            # Create brand profile dict
            brand_profile = {
                "brand_name": brand_name,
                "industry": industry,
                "country": geography,
                "product_portfolio": product_portfolio.split("\n") if product_portfolio else []
            }

            # Stage 0: Brand Enrichment (14%)
            progress(0.14, desc="🏢 Stage 0: Enriching brand profile...")
            stage0_output = await self._call_backend_stage(0, {
                "brand_profile": brand_profile
            })

            # Stage 1: Trend Decomposition (28%)
            progress(0.28, desc="🔍 Stage 1: Extracting trends...")
            stage1_output = await self._call_backend_stage(1, {
                "report_text": pdf_text,
                "brand_context": stage0_output
            })

            # Stage 2: Consumer Insights (42%)
            progress(0.42, desc="💡 Stage 2: Generating consumer insights...")
            stage2_output = await self._call_backend_stage(2, {
                "trends": stage1_output,
                "brand_context": stage0_output
            })

            # Stage 3: Technique Matching (57%)
            progress(0.57, desc="🎯 Stage 3: Matching innovation techniques...")
            stage3_output = await self._call_backend_stage(3, {
                "insights": stage2_output,
                "brand_context": stage0_output
            })

            # Stage 4: Concept Generation (71%)
            progress(0.71, desc="💎 Stage 4: Generating concepts...")
            stage4_output = await self._call_backend_stage(4, {
                "techniques": stage3_output,
                "brand_context": stage0_output
            })

            # Stage 5: Competitive Intelligence (85%)
            progress(0.85, desc="🔎 Stage 5: Searching competitive intel...")
            stage5_output = await self._call_backend_stage(5, {
                "concepts": stage4_output
            })

            # Stage 6: Opportunity Cards (100%)
            progress(1.0, desc="📋 Stage 6: Packaging opportunity cards...")
            stage6_output = await self._call_backend_stage(6, {
                "concepts": stage4_output,
                "competitive": stage5_output,
                "brand_context": stage0_output
            })

            # Format outputs
            stage0_json = json.dumps(stage0_output, indent=2)
            stage1_json = json.dumps(stage1_output, indent=2)
            stage2_json = json.dumps(stage2_output, indent=2)
            stage3_json = json.dumps(stage3_output, indent=2)
            stage4_json = json.dumps(stage4_output, indent=2)
            stage5_json = json.dumps(stage5_output, indent=2)

            # Stage 6 is markdown format
            stage6_markdown = stage6_output.get("markdown", str(stage6_output)) if isinstance(stage6_output, dict) else str(stage6_output)

            status_message = f"Success: Pipeline complete! Run ID: {run_id}"

            return (stage0_json, stage1_json, stage2_json, stage3_json,
                    stage4_json, stage5_json, stage6_markdown, status_message)

        except Exception as e:
            error_msg = f"Error: Pipeline failed: {str(e)}"
            return "", "", "", "", "", "", "", error_msg

    async def _call_backend_stage(self, stage_num: int, payload: Dict[str, Any]) -> Any:
        """Call backend API for specific pipeline stage

        Args:
            stage_num: Stage number (0-6)
            payload: Stage input data

        Returns:
            Stage output data

        Raises:
            Exception: If API call fails
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.backend_url}/pipeline/stage{stage_num}",
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Stage {stage_num} failed: {response.text}")

            return response.json()

    async def save_experiment(
        self,
        run_id: str,
        pdf_text: str,
        brand_profile: Dict[str, Any],
        stage_outputs: Dict[str, Any],
        stage_inputs: Dict[str, Any],
        prompts_used: Dict[str, str],
        quality_tag: str,
        notes: str
    ) -> str:
        """Save experiment to database (Story 11.3a: Auto-save integration)

        Args:
            run_id: Run identifier
            pdf_text: Original report text
            brand_profile: Brand configuration
            stage_outputs: All stage outputs
            stage_inputs: All stage inputs
            prompts_used: Prompts used for each stage
            quality_tag: Good/Needs Work/Failed
            notes: User notes

        Returns:
            Status message
        """
        try:
            # Call database save endpoint
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.backend_url}/experiments/save",
                    json={
                        "run_id": run_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "report_text": pdf_text,
                        "brand_profile": brand_profile,
                        "stage_outputs": stage_outputs,
                        "quality_tag": quality_tag.lower(),
                        "notes": notes
                    }
                )

                if response.status_code != 200:
                    return f"Error: Save failed: {response.text}"

                # Auto-export "Good" examples (Story 11.3a)
                if quality_tag == "Good":
                    saved_count, failed_count = await self._export_few_shot_examples(
                        run_id=run_id,
                        brand_context=brand_profile,
                        stage_outputs=stage_outputs,
                        stage_inputs=stage_inputs,
                        prompts_used=prompts_used
                    )

                    if failed_count > 0:
                        return f"Success: Experiment saved! Exported {saved_count} examples ({failed_count} failed)"
                    else:
                        return f"Success: Experiment saved and {saved_count} examples exported to few-shot library!"

                return f"Success: Experiment saved successfully!"

        except Exception as e:
            # Graceful error handling - don't break pipeline
            error_msg = f"Error: Save operation encountered issues: {str(e)}"
            print(f"SAVE ERROR: {error_msg}")
            return error_msg

    async def _export_few_shot_examples(
        self,
        run_id: str,
        brand_context: Dict[str, Any],
        stage_outputs: Dict[str, Any],
        stage_inputs: Dict[str, Any],
        prompts_used: Dict[str, str]
    ):
        """Export outputs to few-shot learning directory (Story 11.3a integration)

        Args:
            run_id: Run identifier
            brand_context: Brand profile used
            stage_outputs: All stage outputs
            stage_inputs: All stage inputs
            prompts_used: Prompts used for each stage
        """
        # Graceful degradation if few_shot_manager not available yet
        if FileSystemExampleStorage is None:
            return 0, 7  # 0 saved, 7 failed (all stages skipped)

        storage = FileSystemExampleStorage()

        saved_count = 0
        failed_count = 0

        for stage_num in range(7):
            stage_key = f"stage_{stage_num}"

            if stage_key not in stage_outputs:
                continue

            # Get stage-specific data
            output_data = stage_outputs[stage_key]
            input_data = stage_inputs.get(stage_key, {})
            prompt = prompts_used.get(stage_key, "")

            # Save using FileSystemExampleStorage
            success, msg = storage.save_example(
                stage=stage_num,
                run_id=run_id,
                brand_context=brand_context,
                input_data=input_data,
                output_data=output_data,
                prompt_used=prompt,
                quality_score="good"
            )

            if success:
                saved_count += 1
            else:
                failed_count += 1
                print(f"Failed to save stage {stage_num}: {msg}")

        return saved_count, failed_count

    def build_interface(self) -> gr.Blocks:
        """Build Gradio interface

        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(title="Innovation Intelligence Pipeline", theme='davehornik/Tealy') as demo:

            gr.Markdown("# Innovation Intelligence Experimentation Lab")
            gr.Markdown("Upload trend reports and generate innovation concepts for your brand")

            # Session state for caching (Story 11.3a: Added stage_inputs and prompts_used)
            cached_data = gr.State({
                "pdf_text": None,
                "pdf_filename": None,
                "brand_profile": None,
                "run_id": None,
                "stage_outputs": {},
                "stage_inputs": {},
                "prompts_used": {}
            })

            with gr.Row():
                # LEFT COLUMN - INPUTS
                with gr.Column(scale=1):
                    gr.Markdown("## 📤 Inputs")

                    # PDF Upload
                    trend_report = gr.File(
                        label="Trend Report PDF (max 50MB)",
                        file_types=[".pdf"],
                        file_count="single"
                    )
                    extraction_status = gr.Textbox(
                        label="Extraction Status",
                        interactive=False,
                        lines=2
                    )

                    gr.Markdown("### Brand Profile")

                    # Brand selection dropdown
                    brand_dropdown = gr.Dropdown(
                        choices=self.load_available_brands(),
                        label="Select Pre-configured Brand",
                        value=self.load_available_brands()[0] if self.load_available_brands() else None
                    )

                    # YAML upload
                    brand_yaml_upload = gr.File(
                        label="OR Upload Custom Brand Profile (YAML)",
                        file_types=[".yaml", ".yml"],
                        file_count="single"
                    )
                    yaml_upload_status = gr.Textbox(
                        label="Upload Status",
                        interactive=False,
                        lines=1
                    )

                    gr.Markdown("### Brand Details (Manual Entry)")

                    brand_name = gr.Textbox(
                        label="Company Name *",
                        placeholder="e.g., Lactalis Canada"
                    )
                    industry = gr.Textbox(
                        label="Industry *",
                        placeholder="e.g., Dairy/Food & Beverage"
                    )
                    geography = gr.Textbox(
                        label="Geography *",
                        placeholder="e.g., Canada"
                    )
                    product_portfolio = gr.TextArea(
                        label="Product Portfolio (one per line)",
                        placeholder="Milk (2%, whole, skim)\nCheese (cheddar, mozzarella)\nYogurt (Greek, regular)",
                        lines=5
                    )

                    run_button = gr.Button("Run Pipeline", variant="primary", size="lg")

                # RIGHT COLUMN - OUTPUTS
                with gr.Column(scale=2):
                    gr.Markdown("## Pipeline Outputs")

                    pipeline_status = gr.Textbox(
                        label="Pipeline Status",
                        interactive=False,
                        lines=2
                    )

                    with gr.Tabs():
                        with gr.Tab("Stage 0: Brand Context"):
                            stage0_output = gr.Code(
                                label="Enriched Brand Context (JSON)",
                                language="json",
                                lines=15
                            )

                        with gr.Tab("Stage 1: Trends"):
                            stage1_output = gr.Code(
                                label="Extracted Trends (JSON)",
                                language="json",
                                lines=15
                            )

                        with gr.Tab("Stage 2: Insights"):
                            stage2_output = gr.Code(
                                label="Consumer Insights (JSON)",
                                language="json",
                                lines=15
                            )

                        with gr.Tab("Stage 3: Techniques"):
                            stage3_output = gr.Code(
                                label="Innovation Techniques (JSON)",
                                language="json",
                                lines=15
                            )

                        with gr.Tab("Stage 4: Concepts"):
                            stage4_output = gr.Code(
                                label="Directional Concepts (JSON)",
                                language="json",
                                lines=15
                            )

                        with gr.Tab("Stage 5: Competitive"):
                            stage5_output = gr.Code(
                                label="Competitive Intelligence (JSON)",
                                language="json",
                                lines=15
                            )

                        with gr.Tab("Stage 6: Cards"):
                            stage6_output = gr.Markdown(
                                label="Opportunity Cards",
                                value="Run pipeline to generate opportunity cards..."
                            )

                    gr.Markdown("### Quality Assessment")

                    with gr.Row():
                        quality_tag = gr.Radio(
                            choices=["Good", "Needs Work", "Failed"],
                            label="Quality Tag",
                            value="Needs Work"
                        )

                    notes = gr.TextArea(
                        label="Notes (optional)",
                        placeholder="Add any observations or feedback...",
                        lines=3
                    )

                    save_button = gr.Button("Save Experiment", variant="secondary")
                    save_status = gr.Textbox(label="Save Status", interactive=False)

            # Event Listeners

            # PDF extraction on upload
            def extract_and_cache(pdf_file, state):
                if pdf_file is None:
                    return state, ""

                # Check cache
                if state["pdf_text"] and state["pdf_filename"] == pdf_file.name:
                    return state, f"Using cached PDF ({len(state['pdf_text'])} chars)"

                # Extract fresh
                text, status = self.extract_pdf_text(pdf_file)
                state["pdf_text"] = text
                state["pdf_filename"] = pdf_file.name
                return state, status

            trend_report.change(
                extract_and_cache,
                inputs=[trend_report, cached_data],
                outputs=[cached_data, extraction_status]
            )

            # Brand dropdown selection
            brand_dropdown.change(
                self.load_brand_profile_from_yaml,
                inputs=brand_dropdown,
                outputs=[brand_name, industry, geography, product_portfolio]
            )

            # YAML brand upload
            brand_yaml_upload.change(
                self.load_brand_profile_from_file,
                inputs=brand_yaml_upload,
                outputs=[brand_name, industry, geography, product_portfolio, yaml_upload_status]
            )

            # Pipeline execution (Story 11.3a: Update state with outputs)
            async def run_pipeline_wrapper(state, brand_name_val, industry_val, geography_val, portfolio_val):
                pdf_text = state.get("pdf_text", "")

                # Run pipeline
                stage0, stage1, stage2, stage3, stage4, stage5, stage6, status = await self.run_pipeline(
                    pdf_text, brand_name_val, industry_val, geography_val, portfolio_val
                )

                # Update state with results for later save
                state["run_id"] = str(uuid.uuid4())[:8]
                state["brand_profile"] = {
                    "brand_name": brand_name_val,
                    "industry": industry_val,
                    "country": geography_val,
                    "product_portfolio": portfolio_val.split("\n") if portfolio_val else []
                }
                state["stage_outputs"] = {
                    "stage_0": json.loads(stage0) if stage0 else {},
                    "stage_1": json.loads(stage1) if stage1 else {},
                    "stage_2": json.loads(stage2) if stage2 else {},
                    "stage_3": json.loads(stage3) if stage3 else {},
                    "stage_4": json.loads(stage4) if stage4 else {},
                    "stage_5": json.loads(stage5) if stage5 else {},
                    "stage_6": {"markdown": stage6} if stage6 else {}
                }
                # Note: stage_inputs and prompts_used would be populated by actual pipeline
                # For now, these are placeholders until backend integration is complete
                state["stage_inputs"] = {}
                state["prompts_used"] = {}

                return stage0, stage1, stage2, stage3, stage4, stage5, stage6, status

            run_button.click(
                run_pipeline_wrapper,
                inputs=[cached_data, brand_name, industry, geography, product_portfolio],
                outputs=[stage0_output, stage1_output, stage2_output, stage3_output,
                        stage4_output, stage5_output, stage6_output, pipeline_status]
            )

            # Save experiment (Story 11.3a: Pass stage_inputs and prompts_used)
            async def save_experiment_wrapper(state, quality, notes_text):
                run_id = state.get("run_id", str(uuid.uuid4())[:8])
                pdf_text = state.get("pdf_text", "")
                brand_profile = state.get("brand_profile", {})
                stage_outputs = state.get("stage_outputs", {})
                stage_inputs = state.get("stage_inputs", {})
                prompts_used = state.get("prompts_used", {})

                return await self.save_experiment(
                    run_id=run_id,
                    pdf_text=pdf_text,
                    brand_profile=brand_profile,
                    stage_outputs=stage_outputs,
                    stage_inputs=stage_inputs,
                    prompts_used=prompts_used,
                    quality_tag=quality,
                    notes=notes_text
                )

            save_button.click(
                save_experiment_wrapper,
                inputs=[cached_data, quality_tag, notes],
                outputs=save_status
            )

        return demo

    def launch(self, share=False):
        """Launch Gradio interface

        Args:
            share: Create public Gradio share link
        """
        demo = self.build_interface()
        demo.queue(
            max_size=10,
            default_concurrency_limit=3
        ).launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=share
        )


if __name__ == "__main__":
    lab = GradioLab()
    lab.launch(share=False)
