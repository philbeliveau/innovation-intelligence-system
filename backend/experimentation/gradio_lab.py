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
import tempfile

# Import few-shot storage (Story 11.3a)
# Note: This import will work once few_shot_manager.py is created in Story 11.3a
try:
    from backend.experimentation.few_shot_manager import FileSystemExampleStorage
except ImportError:
    # Graceful degradation if few_shot_manager not yet implemented
    FileSystemExampleStorage = None

# Import curation interface (Story 11.3c)
try:
    from curation_interface import create_curation_tab
    from example_usage_tracker import ExampleUsageTracker
except ImportError:
    # Graceful degradation
    create_curation_tab = None
    ExampleUsageTracker = None

# Import export and backup functionality (Story 11.4b)
try:
    from backend.app.prisma_client import PrismaAPIClient
    from backend.experimentation.export.json_export import export_to_json
    from backend.experimentation.export.csv_export import export_to_csv, export_experiments_summary
    from backend.experimentation.export.backup_manager import backup_experiments, archive_to_blob
except ImportError:
    # Graceful degradation
    PrismaAPIClient = None
    export_to_json = None
    export_to_csv = None
    export_experiments_summary = None
    backup_experiments = None
    archive_to_blob = None

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL")

class GradioLab:
    """Main Gradio experimentation interface"""

    def __init__(self):
        self.backend_url = BACKEND_API_URL
        self.brand_profiles_dir = Path("../../data/brand-profiles")

        # Initialize usage tracker for curation interface (Story 11.3c)
        if ExampleUsageTracker:
            self.usage_tracker = ExampleUsageTracker()
        else:
            self.usage_tracker = None

        # Initialize Prisma API client for export/backup (Story 11.4b)
        if PrismaAPIClient:
            self.prisma_client = PrismaAPIClient()
        else:
            self.prisma_client = None

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

            # Start pipeline via /run/local endpoint
            progress(0.05, desc="🚀 Starting pipeline...")
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.backend_url}/run/local",
                    json={
                        "pdf_text": pdf_text,
                        "brand_profile": brand_profile,
                        "run_id": run_id
                    }
                )

                if response.status_code != 200:
                    raise Exception(f"Failed to start pipeline: {response.text}")

                result = response.json()
                actual_run_id = result["run_id"]

            # Poll /status endpoint for progress
            stage_outputs = {}
            max_polls = 300  # 300 * 2s = 10 minutes max
            poll_count = 0

            while poll_count < max_polls:
                await asyncio.sleep(2)  # Poll every 2 seconds
                poll_count += 1

                async with httpx.AsyncClient(timeout=30.0) as client:
                    status_response = await client.get(
                        f"{self.backend_url}/status/{actual_run_id}"
                    )

                    if status_response.status_code != 200:
                        raise Exception(f"Failed to get status: {status_response.text}")

                    status = status_response.json()

                # Update progress based on current stage
                current_stage = status.get("current_stage", 0)
                stage_progress = [0.05, 0.20, 0.35, 0.50, 0.65, 0.80, 0.95]
                if current_stage < len(stage_progress):
                    progress(stage_progress[current_stage], desc=f"🔄 Stage {current_stage}...")

                # Check if pipeline is complete
                if status["status"] == "complete":
                    # Extract stage outputs
                    stages = status.get("stages", {})
                    for stage_key, stage_info in stages.items():
                        if stage_info.get("output"):
                            stage_outputs[stage_key] = stage_info["output"]
                    break

                elif status["status"] == "failed":
                    error_msg = status.get("error", "Pipeline failed with unknown error")
                    raise Exception(error_msg)

            if poll_count >= max_polls:
                raise Exception("Pipeline timeout: execution took longer than 10 minutes")

            # Format outputs for display (prefer markdown over JSON)
            def get_stage_display(stage_key: str) -> str:
                """Get markdown or JSON fallback for stage display"""
                if stage_key not in stage_outputs:
                    return ""

                stage_data = stages.get(stage_key, {})

                # Prefer markdown if available
                if "markdown" in stage_data:
                    return stage_data["markdown"]

                # Fallback to formatted JSON
                output = stage_data.get("output", {})
                if output:
                    return f"```json\n{json.dumps(output, indent=2)}\n```"

                return ""

            stage0 = get_stage_display("0")
            stage1 = get_stage_display("1")
            stage2 = get_stage_display("2")
            stage3 = get_stage_display("3")
            stage4 = get_stage_display("4")
            stage5 = get_stage_display("5")
            stage6 = get_stage_display("6")

            status_message = f"✅ Success: Pipeline complete! Run ID: {actual_run_id}"

            return (stage0, stage1, stage2, stage3, stage4, stage5, stage6, status_message)

        except Exception as e:
            error_msg = f"Error: Pipeline failed: {str(e)}"
            return "", "", "", "", "", "", "", error_msg


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

    async def export_experiments_json(
        self,
        quality_filter: Optional[str] = None,
        brand_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[str, str]:
        """Export experiments to JSON format (Story 11.4b)

        Args:
            quality_filter: Filter by quality tag
            brand_filter: Filter by brand name
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)

        Returns:
            Tuple of (file_path, status_message)
        """
        if not self.prisma_client or not export_to_json:
            return "", "Export functionality not available (PrismaAPIClient not initialized)"

        try:
            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"/tmp/experiments_export_{timestamp}.json"

            # Export to JSON (using PrismaAPIClient HTTP wrapper)
            result_path = await export_to_json(
                prisma_client=self.prisma_client,
                output_path=output_path,
                quality_tag=quality_filter.lower() if quality_filter and quality_filter != "All" else None,
                brand_name=brand_filter if brand_filter and brand_filter != "All" else None,
                start_date=start_date if start_date else None,
                end_date=end_date if end_date else None
            )

            return result_path, f"Success: Exported to {Path(result_path).name}"

        except ValueError as e:
            return "", f"No experiments found with given filters"
        except Exception as e:
            return "", f"Export failed: {str(e)}"

    async def export_experiments_csv(
        self,
        quality_filter: Optional[str] = None,
        brand_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[str, str]:
        """Export experiments to CSV format (Story 11.4b)

        Args:
            quality_filter: Filter by quality tag
            brand_filter: Filter by brand name
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)

        Returns:
            Tuple of (file_path, status_message)
        """
        if not self.prisma_client or not export_to_csv:
            return "", "Export functionality not available (PrismaAPIClient not initialized)"

        try:
            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"/tmp/experiments_export_{timestamp}.csv"

            # Export to CSV (using PrismaAPIClient HTTP wrapper)
            result_path = await export_to_csv(
                prisma_client=self.prisma_client,
                output_path=output_path,
                quality_tag=quality_filter.lower() if quality_filter and quality_filter != "All" else None,
                brand_name=brand_filter if brand_filter and brand_filter != "All" else None,
                start_date=start_date if start_date else None,
                end_date=end_date if end_date else None
            )

            return result_path, f"Success: Exported to {Path(result_path).name}"

        except ValueError as e:
            return "", f"No experiments found with given filters"
        except Exception as e:
            return "", f"Export failed: {str(e)}"

    async def create_backup(self) -> Tuple[str, str]:
        """Create manual backup of all experiments (Story 11.4b)

        Returns:
            Tuple of (file_path, status_message)
        """
        if not self.prisma_client or not backup_experiments:
            return "", "Backup functionality not available (PrismaAPIClient not initialized)"

        try:
            # Create compressed backup (using PrismaAPIClient HTTP wrapper)
            backup_path = await backup_experiments(
                prisma_client=self.prisma_client,
                backup_name=None,  # Auto-generate name
                compress=True
            )

            # Try to upload to Vercel Blob if token available
            blob_url = None
            if archive_to_blob and os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN"):
                try:
                    blob_url = await archive_to_blob(backup_path)
                except Exception as e:
                    print(f"Blob upload failed: {e}")

            status_msg = f"Success: Backup created at {Path(backup_path).name}"
            if blob_url:
                status_msg += f"\nUploaded to Vercel Blob: {blob_url}"

            return backup_path, status_msg

        except ValueError as e:
            return "", f"No experiments to backup"
        except Exception as e:
            return "", f"Backup failed: {str(e)}"

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
                            stage0_output = gr.Markdown(
                                value="Run pipeline to generate brand context..."
                            )

                        with gr.Tab("Stage 1: Extraction"):
                            stage1_output = gr.Markdown(
                                value="Run pipeline to extract mechanisms..."
                            )

                        with gr.Tab("Stage 2: Signals"):
                            stage2_output = gr.Markdown(
                                value="Run pipeline to identify signals..."
                            )

                        with gr.Tab("Stage 3: Insights"):
                            stage3_output = gr.Markdown(
                                value="Run pipeline to generate insights..."
                            )

                        with gr.Tab("Stage 4: Ideation"):
                            stage4_output = gr.Markdown(
                                value="Run pipeline to create preliminary concepts..."
                            )

                        with gr.Tab("Stage 5: Opportunity Cards"):
                            stage5_output = gr.Markdown(
                                value="Run pipeline to generate opportunity cards..."
                            )

                        with gr.Tab("Stage 6: Export"):
                            stage6_output = gr.Markdown(
                                value="Run pipeline to export results..."
                            )

                        # Story 11.3c: Add curation interface tab
                        if create_curation_tab:
                            with gr.Tab("📚 Example Curation"):
                                # Create curation interface
                                curation_content = create_curation_tab(
                                    storage_path=str(Path(__file__).parent / "successful_examples"),
                                    usage_tracker=self.usage_tracker
                                )
                                # Note: curation_content is a gr.Blocks that renders inside this tab

                        # Story 11.4b: Add data management tab
                        with gr.Tab("💾 Data Management"):
                            gr.Markdown("## Export & Backup")
                            gr.Markdown("Export experiments to JSON/CSV or create database backups")

                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### Export Filters")
                                    export_quality = gr.Dropdown(
                                        choices=["All", "Good", "Needs Work", "Failed"],
                                        label="Quality Tag Filter",
                                        value="All"
                                    )
                                    export_brand = gr.Dropdown(
                                        choices=["All"] + self.load_available_brands(),
                                        label="Brand Filter",
                                        value="All"
                                    )
                                    export_start_date = gr.Textbox(
                                        label="Start Date (ISO format, optional)",
                                        placeholder="2025-11-01T00:00:00Z"
                                    )
                                    export_end_date = gr.Textbox(
                                        label="End Date (ISO format, optional)",
                                        placeholder="2025-11-30T23:59:59Z"
                                    )

                                with gr.Column():
                                    gr.Markdown("### Export Actions")
                                    export_json_btn = gr.Button("📄 Export to JSON", variant="primary")
                                    export_csv_btn = gr.Button("📊 Export to CSV", variant="primary")
                                    gr.Markdown("---")
                                    gr.Markdown("### Backup")
                                    backup_btn = gr.Button("💾 Create Full Backup", variant="secondary")

                            export_file = gr.File(label="Download Export/Backup")
                            export_status = gr.Textbox(label="Status", interactive=False, lines=3)

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
                # Stage outputs are now markdown strings, not JSON
                state["run_id"] = str(uuid.uuid4())[:8]
                state["brand_profile"] = {
                    "brand_name": brand_name_val,
                    "industry": industry_val,
                    "country": geography_val,
                    "product_portfolio": portfolio_val.split("\n") if portfolio_val else []
                }
                state["stage_outputs"] = {
                    "stage_0": {"markdown": stage0} if stage0 else {},
                    "stage_1": {"markdown": stage1} if stage1 else {},
                    "stage_2": {"markdown": stage2} if stage2 else {},
                    "stage_3": {"markdown": stage3} if stage3 else {},
                    "stage_4": {"markdown": stage4} if stage4 else {},
                    "stage_5": {"markdown": stage5} if stage5 else {},
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

            # Export and Backup event listeners (Story 11.4b)
            async def export_json_wrapper(quality, brand, start, end):
                file_path, status = await self.export_experiments_json(
                    quality_filter=quality,
                    brand_filter=brand,
                    start_date=start if start else None,
                    end_date=end if end else None
                )
                return file_path, status

            async def export_csv_wrapper(quality, brand, start, end):
                file_path, status = await self.export_experiments_csv(
                    quality_filter=quality,
                    brand_filter=brand,
                    start_date=start if start else None,
                    end_date=end if end else None
                )
                return file_path, status

            async def backup_wrapper():
                file_path, status = await self.create_backup()
                return file_path, status

            export_json_btn.click(
                export_json_wrapper,
                inputs=[export_quality, export_brand, export_start_date, export_end_date],
                outputs=[export_file, export_status]
            )

            export_csv_btn.click(
                export_csv_wrapper,
                inputs=[export_quality, export_brand, export_start_date, export_end_date],
                outputs=[export_file, export_status]
            )

            backup_btn.click(
                backup_wrapper,
                inputs=[],
                outputs=[export_file, export_status]
            )

        return demo

    def launch(self, share=False):
        """Launch Gradio interface

        Args:
            share: Create public Gradio share link
        """
        demo = self.build_interface()

        # Configure queue and launch
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
