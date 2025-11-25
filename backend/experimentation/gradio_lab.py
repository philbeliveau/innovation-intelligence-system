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
from datetime import datetime, timezone
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
    # Try HF Spaces flat structure first (all files in same directory)
    from few_shot_manager import FileSystemExampleStorage
    print("[IMPORT] ✓ Successfully imported FileSystemExampleStorage (HF Spaces flat structure)")
except ImportError:
    try:
        # Fallback to nested structure (local development)
        from backend.experimentation.few_shot_manager import FileSystemExampleStorage
        print("[IMPORT] ✓ Successfully imported FileSystemExampleStorage (nested structure)")
    except ImportError:
        # Graceful degradation if few_shot_manager not yet implemented
        FileSystemExampleStorage = None
        print("[IMPORT] ✗ WARNING: few_shot_manager not available - few-shot export will be skipped")
        print("[IMPORT] ✗ 'Good' quality experiments will save to database but NOT export examples")

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

# Import PDF export functionality
try:
    from export.pdf_export import generate_stage_pdf, generate_all_stages_pdf
    PDF_EXPORT_AVAILABLE = True
except ImportError:
    # Graceful degradation
    generate_stage_pdf = None
    generate_all_stages_pdf = None
    PDF_EXPORT_AVAILABLE = False

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL")

class GradioLab:
    """Main Gradio experimentation interface"""

    def __init__(self):
        self.backend_url = BACKEND_API_URL

        # Support multiple deployment environments
        # HF Spaces: /app/data/brand-profiles
        # Railway: backend/experimentation relative paths
        # Local: ../../data/brand-profiles
        possible_paths = [
            Path("/app/data/brand-profiles"),  # HF Spaces absolute
            Path("../../data/brand-profiles"),  # Local relative
            Path("../data/brand-profiles"),     # Alternative relative
            Path("data/brand-profiles"),        # Current dir relative
        ]

        self.brand_profiles_dir = None
        for path in possible_paths:
            if path.exists():
                self.brand_profiles_dir = path
                break

        if self.brand_profiles_dir is None:
            self.brand_profiles_dir = Path("../../data/brand-profiles")  # Fallback

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

    def resolve_prompts_dir(self) -> Path:
        """Resolve prompts directory across deployment environments

        Returns:
            Path: Resolved prompts directory

        Raises:
            FileNotFoundError: If prompts directory cannot be found
        """
        possible_paths = [
            Path("/app/experimentation/prompts"),       # HF Spaces absolute
            Path("prompts"),                             # Local (same dir as gradio_lab.py)
            Path("backend/experimentation/prompts"),    # Project root
            Path("../prompts"),                          # Alternative relative
        ]
        for path in possible_paths:
            if path.exists():
                return path
        raise FileNotFoundError("Prompts directory not found")

    def create_default_template_zip(self) -> str:
        """Create ZIP file containing all 7 default prompt templates + README

        Returns:
            str: Path to generated ZIP file
        """
        import zipfile
        from datetime import datetime

        prompts_dir = self.resolve_prompts_dir()

        # Create temporary ZIP file
        zip_path = f"/tmp/prompt_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add 7 stage templates
            for i in range(7):
                template_files = {
                    0: "stage_0_enrichment.md",
                    1: "stage_1_extraction.md",
                    2: "stage_2_convergence.md",
                    3: "stage_3_technique_matching.md",
                    4: "stage_4_concept_generation.md",
                    5: "stage_5_competitive_search.md",
                    6: "stage_6_packaging.md"
                }

                template_path = prompts_dir / template_files[i]
                if template_path.exists():
                    zipf.write(template_path, template_files[i])

            # Add README.md with placeholder documentation
            readme_content = """# Innovation Pipeline Prompt Templates

## Overview

This ZIP contains the 7 default prompt templates used by the Innovation Intelligence System pipeline.

## Placeholder Requirements

Each stage requires specific placeholders to be present in the prompt template:

| Stage | Required Placeholders |
|-------|-----------------------|
| Stage 0 | `{company_name}`, `{industry}`, `{portfolio}` |
| Stage 1 | `{report_text}` |
| Stage 2 | `{trend_data}`, `{brand_context}` |
| Stage 3 | `{insights}`, `{brand_resources}` |
| Stage 4 | `{insights}`, `{matched_techniques}`, `{brand_context}`, `{no_hallucination_rules}` |
| Stage 5 | `{initiatives}`, `{brand_context}` |
| Stage 6 | `{all_stage_outputs}` |

## Usage

1. Modify the `.md` files with your custom prompt engineering
2. Ensure required placeholders remain in the text (e.g., `{insights}`, `{brand_context}`)
3. Upload modified files via the "Custom Prompts" tab in the UI
4. Validate placeholders before running the pipeline

## Placeholder Format

Placeholders use curly braces with lowercase snake_case: `{placeholder_name}`

Example: `{brand_context}`, `{insights}`, `{matched_techniques}`

---

**Generated:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
"""
            zipf.writestr("README.md", readme_content)

        return zip_path

    def validate_placeholders(self, stage: int, file_content: str) -> Tuple[bool, List[str]]:
        """Validate that uploaded prompt file contains required placeholders

        Args:
            stage: Stage number (0-6)
            file_content: Content of uploaded .md file

        Returns:
            Tuple of (is_valid, missing_placeholders)
        """
        import re

        # Define required placeholders per stage
        required_placeholders = {
            0: ["company_name", "industry", "portfolio"],
            1: ["report_text"],
            2: ["trend_data", "brand_context"],
            3: ["insights", "brand_resources"],
            4: ["insights", "matched_techniques", "brand_context", "no_hallucination_rules"],
            5: ["initiatives", "brand_context"],
            6: ["all_stage_outputs"]
        }

        required = required_placeholders.get(stage, [])

        # Extract all placeholders from content using regex
        found_placeholders = set(re.findall(r'\{([a-z_]+)\}', file_content))

        # Check for missing placeholders
        missing = [p for p in required if p not in found_placeholders]

        return len(missing) == 0, missing

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

    async def fetch_saved_experiments(
        self,
        quality_filter: Optional[str] = None,
        brand_filter: Optional[str] = None,
        limit: int = 20
    ) -> List[List[str]]:
        """Fetch saved experiments from Railway database

        Args:
            quality_filter: Filter by quality tag (good/needs work/failed/all)
            brand_filter: Filter by brand name
            limit: Max number of experiments to return

        Returns:
            List of experiment rows [id, brand, date, quality] for Dataframe display
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Build request parameters
            params = {"limit": limit}
            if quality_filter and quality_filter.lower() != "all":
                params["quality_tag"] = quality_filter.lower()
            if brand_filter and brand_filter != "All":
                params["brand_name"] = brand_filter

            request_url = f"{self.backend_url}/experiments/list"
            logger.info(f"[FETCH_EXPERIMENTS] Request: {request_url} with params: {params}")
            print(f"[FETCH_EXPERIMENTS] Fetching experiments from {request_url}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(request_url, params=params)

                logger.info(f"[FETCH_EXPERIMENTS] Response status: {response.status_code}")
                print(f"[FETCH_EXPERIMENTS] Response status: {response.status_code}")

                if response.status_code != 200:
                    error_msg = f"Backend returned {response.status_code}: {response.text[:200]}"
                    logger.error(f"[FETCH_EXPERIMENTS] {error_msg}")
                    print(f"[FETCH_EXPERIMENTS] ERROR: {error_msg}")
                    return []

                # Parse response - CRITICAL FIX: Extract "experiments" array from response
                data = response.json()
                logger.info(f"[FETCH_EXPERIMENTS] Response keys: {list(data.keys())}")
                print(f"[FETCH_EXPERIMENTS] Response contains: {list(data.keys())}")

                # Extract experiments array from response object
                experiments = data.get("experiments", [])
                pagination = data.get("pagination", {})

                total_count = pagination.get("total", len(experiments))
                logger.info(f"[FETCH_EXPERIMENTS] Found {len(experiments)} experiments (total: {total_count})")
                print(f"[FETCH_EXPERIMENTS] Found {len(experiments)} experiments (total DB count: {total_count})")

                if len(experiments) == 0:
                    logger.warning("[FETCH_EXPERIMENTS] No experiments found in database")
                    print("[FETCH_EXPERIMENTS] WARNING: Database returned 0 experiments")
                    return []

                # Format for Gradio Dataframe
                rows = []
                for idx, exp in enumerate(experiments):
                    try:
                        # Log first experiment structure for debugging
                        if idx == 0:
                            logger.info(f"[FETCH_EXPERIMENTS] First experiment keys: {list(exp.keys())}")
                            print(f"[FETCH_EXPERIMENTS] Sample experiment structure: {list(exp.keys())}")

                        # Extract brand name from brandProfile JSONB field (camelCase in Experiment table)
                        brand_profile = exp.get("brandProfile", {})
                        brand_name = brand_profile.get("brand_name", "Unknown") if isinstance(brand_profile, dict) else "Unknown"

                        # Extract timestamp from createdAt field (camelCase in Experiment table)
                        timestamp = exp.get("createdAt") or exp.get("timestamp") or ""
                        date_str = timestamp[:10] if timestamp else "N/A"

                        # Extract quality tag from qualityTag field (camelCase in Experiment table)
                        quality = exp.get("qualityTag") or "N/A"
                        quality_display = quality.capitalize() if quality and quality != "N/A" else "N/A"

                        # Extract ID (first 8 chars for display)
                        exp_id = exp.get("id", "")[:8]

                        rows.append([exp_id, brand_name, date_str, quality_display])

                    except Exception as row_error:
                        logger.error(f"[FETCH_EXPERIMENTS] Error parsing experiment {idx}: {row_error}")
                        print(f"[FETCH_EXPERIMENTS] ERROR parsing experiment {idx}: {row_error}")
                        continue

                logger.info(f"[FETCH_EXPERIMENTS] Successfully formatted {len(rows)} rows for display")
                print(f"[FETCH_EXPERIMENTS] ✓ Returning {len(rows)} experiments to UI")
                return rows

        except httpx.HTTPError as http_err:
            error_msg = f"HTTP error fetching experiments: {http_err}"
            logger.error(f"[FETCH_EXPERIMENTS] {error_msg}")
            print(f"[FETCH_EXPERIMENTS] HTTP ERROR: {error_msg}")
            return []
        except json.JSONDecodeError as json_err:
            error_msg = f"Invalid JSON response: {json_err}"
            logger.error(f"[FETCH_EXPERIMENTS] {error_msg}")
            print(f"[FETCH_EXPERIMENTS] JSON ERROR: {error_msg}")
            return []
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
            logger.error(f"[FETCH_EXPERIMENTS] {error_msg}", exc_info=True)
            print(f"[FETCH_EXPERIMENTS] UNEXPECTED ERROR: {error_msg}")
            import traceback
            print(traceback.format_exc())
            return []

    async def load_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Load full experiment data by ID

        Args:
            experiment_id: UUID or short ID of experiment

        Returns:
            Complete experiment data or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.backend_url}/experiments/{experiment_id}"
                )

                if response.status_code != 200:
                    return None

                return response.json()

        except Exception as e:
            print(f"Failed to load experiment: {e}")
            return None

    async def rename_experiment(self, experiment_id: str, new_name: str) -> str:
        """Rename an experiment

        Args:
            experiment_id: UUID or short ID of experiment
            new_name: New name for the experiment

        Returns:
            Status message
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{self.backend_url}/experiments/{experiment_id}/rename",
                    json={"new_name": new_name}
                )

                if response.status_code == 200:
                    return f"✅ Renamed to '{new_name}'"
                elif response.status_code == 404:
                    return f"❌ Experiment {experiment_id} not found"
                else:
                    return f"❌ Rename failed: {response.text}"

        except Exception as e:
            return f"❌ Error: {str(e)}"

    async def delete_experiment(self, experiment_id: str) -> str:
        """Delete an experiment

        Args:
            experiment_id: UUID or short ID of experiment

        Returns:
            Status message
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.backend_url}/experiments/{experiment_id}"
                )

                if response.status_code == 200:
                    return f"✅ Experiment deleted successfully"
                elif response.status_code == 404:
                    return f"❌ Experiment {experiment_id} not found"
                else:
                    return f"❌ Delete failed: {response.text}"

        except Exception as e:
            return f"❌ Error: {str(e)}"

    async def run_pipeline(
        self,
        pdf_text: str,
        brand_name: str,
        industry: str,
        geography: str,
        product_portfolio: str,
        progress=gr.Progress(),
        custom_prompts: Optional[Dict[str, str]] = None
    ) -> Tuple[str, str, str, str, str, str, str, str]:
        """Execute 7-stage pipeline with real-time progress

        Args:
            pdf_text: Extracted PDF text
            brand_name: Company name
            industry: Industry sector
            geography: Geographic market
            product_portfolio: Product list
            progress: Gradio Progress tracker
            custom_prompts: Optional dict mapping stage keys to custom prompt content

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
                # Build payload with optional custom_prompts
                payload = {
                    "pdf_text": pdf_text,
                    "brand_profile": brand_profile,
                    "run_id": run_id
                }
                if custom_prompts:
                    payload["custom_prompts"] = custom_prompts

                response = await client.post(
                    f"{self.backend_url}/run/local",
                    json=payload
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
                # Get stage data from status response
                stage_data = stages.get(stage_key, {})

                if not stage_data:
                    return ""

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
        import logging
        logger = logging.getLogger(__name__)

        try:
            logger.info(f"[SAVE_EXPERIMENT] Starting save for run {run_id} with quality tag '{quality_tag}'")
            print(f"[SAVE_EXPERIMENT] Saving experiment {run_id} (quality: {quality_tag})...")

            # Call database save endpoint
            async with httpx.AsyncClient(timeout=30.0) as client:
                save_payload = {
                    "run_id": run_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "report_text": pdf_text,
                    "brand_profile": brand_profile,
                    "stage_outputs": stage_outputs,
                    "quality_tag": quality_tag.lower(),
                    "notes": notes
                }

                logger.info(f"[SAVE_EXPERIMENT] Sending to backend: {self.backend_url}/experiments/save")
                print(f"[SAVE_EXPERIMENT] Sending to database...")

                response = await client.post(
                    f"{self.backend_url}/experiments/save",
                    json=save_payload
                )

                logger.info(f"[SAVE_EXPERIMENT] Backend response status: {response.status_code}")

                if response.status_code != 200:
                    error_msg = f"Error: Save failed: {response.text}"
                    logger.error(f"[SAVE_EXPERIMENT] {error_msg}")
                    print(f"[SAVE_EXPERIMENT] ✗ {error_msg}")
                    return error_msg

                logger.info(f"[SAVE_EXPERIMENT] ✓ Database save successful")
                print(f"[SAVE_EXPERIMENT] ✓ Saved to database")

                # Auto-export "Good" examples (Story 11.3a)
                logger.info(f"[SAVE_EXPERIMENT] Checking quality tag for few-shot export: '{quality_tag}' == 'Good'?")
                if quality_tag == "Good":
                    logger.info("[SAVE_EXPERIMENT] Quality is 'Good' - triggering few-shot export")
                    print("[SAVE_EXPERIMENT] Quality marked as 'Good' - exporting examples...")

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
                else:
                    logger.info(f"[SAVE_EXPERIMENT] Quality is '{quality_tag}' (not 'Good') - skipping few-shot export")
                    print(f"[SAVE_EXPERIMENT] Quality '{quality_tag}' - no few-shot export needed")

                return f"Success: Experiment saved successfully!"

        except httpx.HTTPError as http_err:
            error_msg = f"Error: HTTP error during save: {str(http_err)}"
            logger.error(f"[SAVE_EXPERIMENT] {error_msg}", exc_info=True)
            print(f"[SAVE_EXPERIMENT] ✗ {error_msg}")
            return error_msg
        except Exception as e:
            # Graceful error handling - don't break pipeline
            error_msg = f"Error: Save operation encountered issues: {str(e)}"
            logger.error(f"[SAVE_EXPERIMENT] {error_msg}", exc_info=True)
            print(f"[SAVE_EXPERIMENT] ✗ {error_msg}")
            import traceback
            print(traceback.format_exc())
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
        import logging
        logger = logging.getLogger(__name__)

        # Graceful degradation if few_shot_manager not available yet
        if FileSystemExampleStorage is None:
            error_msg = f"[FEW_SHOT] FileSystemExampleStorage not available - skipping export for run {run_id}"
            print(error_msg)
            logger.warning(error_msg)
            return 0, 7  # 0 saved, 7 failed (all stages skipped)

        logger.info(f"[FEW_SHOT] Starting few-shot export for run {run_id}")
        print(f"[FEW_SHOT] Exporting 'Good' quality examples for run {run_id}...")

        storage = FileSystemExampleStorage()

        saved_count = 0
        failed_count = 0

        for stage_num in range(7):
            stage_key = f"stage_{stage_num}"

            if stage_key not in stage_outputs:
                logger.debug(f"[FEW_SHOT] Stage {stage_num} not found in outputs, skipping")
                continue

            # Get stage-specific data
            output_data = stage_outputs[stage_key]
            input_data = stage_inputs.get(stage_key, {})
            prompt = prompts_used.get(stage_key, "")

            logger.info(f"[FEW_SHOT] Saving example for stage {stage_num}...")
            print(f"[FEW_SHOT] Saving stage {stage_num} example...")

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
                logger.info(f"[FEW_SHOT] ✓ Stage {stage_num} saved successfully")
                print(f"[FEW_SHOT] ✓ Stage {stage_num} example saved")
            else:
                failed_count += 1
                error_msg = f"[FEW_SHOT] ✗ Failed to save stage {stage_num}: {msg}"
                logger.error(error_msg)
                print(error_msg)

        summary_msg = f"[FEW_SHOT] Export complete: {saved_count} succeeded, {failed_count} failed"
        logger.info(summary_msg)
        print(summary_msg)

        return saved_count, failed_count

    async def export_experiments_json(
        self,
        quality_filter: Optional[str] = None,
        brand_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[Optional[str], str]:
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
            return None, "Export functionality not available (PrismaAPIClient not initialized)"

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
            return None, f"No experiments found with given filters"
        except Exception as e:
            return None, f"Export failed: {str(e)}"

    async def export_experiments_csv(
        self,
        quality_filter: Optional[str] = None,
        brand_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[Optional[str], str]:
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
            return None, "Export functionality not available (PrismaAPIClient not initialized)"

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
            return None, f"No experiments found with given filters"
        except Exception as e:
            return None, f"Export failed: {str(e)}"

    def generate_stage_pdf_file(
        self,
        stage_num: int,
        markdown_content: str,
        brand_name: str
    ) -> Optional[str]:
        """Generate PDF for a specific stage.

        Args:
            stage_num: Stage number (0-6)
            markdown_content: Markdown content to convert
            brand_name: Brand name for PDF header

        Returns:
            Path to generated PDF file or None if failed
        """
        if not PDF_EXPORT_AVAILABLE or not markdown_content:
            return None

        try:
            pdf_path = generate_stage_pdf(
                stage_num=stage_num,
                markdown_content=markdown_content,
                brand_name=brand_name
            )
            return str(pdf_path)
        except Exception as e:
            print(f"PDF generation failed for Stage {stage_num}: {e}")
            return None

    def generate_all_stages_pdf_file(
        self,
        stage_markdowns: Dict[int, str],
        brand_name: str
    ) -> Optional[str]:
        """Generate combined PDF with all pipeline stages.

        Args:
            stage_markdowns: Dict mapping stage numbers to markdown content
            brand_name: Brand name for PDF header

        Returns:
            Path to generated PDF file or None if failed
        """
        if not PDF_EXPORT_AVAILABLE:
            return None

        try:
            pdf_path = generate_all_stages_pdf(
                stage_markdowns=stage_markdowns,
                brand_name=brand_name
            )
            return str(pdf_path)
        except Exception as e:
            print(f"Combined PDF generation failed: {e}")
            return None

    async def create_backup(self) -> Tuple[Optional[str], str]:
        """Create manual backup of all experiments (Story 11.4b)

        Returns:
            Tuple of (file_path, status_message)
        """
        if not self.prisma_client or not backup_experiments:
            return None, "Backup functionality not available (PrismaAPIClient not initialized)"

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
            return None, f"No experiments to backup"
        except Exception as e:
            return None, f"Backup failed: {str(e)}"

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
                "prompts_used": {},
                "custom_prompts": {}
            })

            # COLLAPSIBLE SIDEBAR - SAVED EXPERIMENTS (at top level, not inside Row)
            with gr.Sidebar():
                gr.Markdown("## 📚 Saved Runs")
                gr.Markdown("Access your previous experiments")

                # Filters
                with gr.Accordion("🔍 Filters", open=True):
                    sidebar_quality_filter = gr.Dropdown(
                        choices=["All", "Good", "Needs Work", "Failed"],
                        value="All",
                        label="Quality Tag"
                    )
                    sidebar_brand_filter = gr.Dropdown(
                        choices=["All"] + [b for b in self.load_available_brands() if b != "Custom (Manual Entry)"],
                        value="All",
                        label="Brand"
                    )
                    refresh_experiments_btn = gr.Button("🔄 Refresh List", size="sm")

                # Experiments list
                experiments_list = gr.Dataframe(
                    headers=["ID", "Brand", "Date", "Quality"],
                    datatype=["str", "str", "str", "str"],
                    label="Recent Experiments",
                    interactive=False,
                    wrap=True,
                    max_height=300
                )

                # Load controls
                selected_experiment_id = gr.Textbox(
                    label="Experiment ID",
                    placeholder="Copy ID from list above",
                    lines=1
                )

                with gr.Row():
                    load_experiment_btn = gr.Button("📥 Load", variant="primary", scale=2)
                    rename_experiment_btn = gr.Button("✏️ Rename", variant="secondary", scale=1)
                    delete_experiment_btn = gr.Button("🗑️ Delete", variant="stop", scale=1)

                # Rename controls (initially hidden)
                with gr.Group(visible=False) as rename_group:
                    rename_input = gr.Textbox(
                        label="New Name",
                        placeholder="Enter new name for experiment",
                        lines=1
                    )
                    with gr.Row():
                        confirm_rename_btn = gr.Button("✅ Confirm", variant="primary", size="sm")
                        cancel_rename_btn = gr.Button("❌ Cancel", variant="secondary", size="sm")

                load_status = gr.Textbox(
                    label="Status",
                    interactive=False,
                    lines=2
                )

            # MAIN CONTENT AREA
            with gr.Row():
                with gr.Column(scale=3):
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
                                    download_stage0_btn = gr.Button("📥 Download PDF", size="sm")
                                    stage0_pdf_file = gr.File(label="Stage 0 PDF", visible=False)

                                with gr.Tab("Stage 1: Extraction"):
                                    stage1_output = gr.Markdown(
                                        value="Run pipeline to extract mechanisms..."
                                    )
                                    download_stage1_btn = gr.Button("📥 Download PDF", size="sm")
                                    stage1_pdf_file = gr.File(label="Stage 1 PDF", visible=False)

                                with gr.Tab("Stage 2: Signals"):
                                    stage2_output = gr.Markdown(
                                        value="Run pipeline to identify signals..."
                                    )
                                    download_stage2_btn = gr.Button("📥 Download PDF", size="sm")
                                    stage2_pdf_file = gr.File(label="Stage 2 PDF", visible=False)

                                with gr.Tab("Stage 3: Insights"):
                                    stage3_output = gr.Markdown(
                                        value="Run pipeline to generate insights..."
                                    )
                                    download_stage3_btn = gr.Button("📥 Download PDF", size="sm")
                                    stage3_pdf_file = gr.File(label="Stage 3 PDF", visible=False)

                                with gr.Tab("Stage 4: Ideation"):
                                    stage4_output = gr.Markdown(
                                        value="Run pipeline to create preliminary concepts..."
                                    )
                                    download_stage4_btn = gr.Button("📥 Download PDF", size="sm")
                                    stage4_pdf_file = gr.File(label="Stage 4 PDF", visible=False)

                                with gr.Tab("Stage 5: Opportunity Cards"):
                                    stage5_output = gr.Markdown(
                                        value="Run pipeline to generate opportunity cards..."
                                    )
                                    download_stage5_btn = gr.Button("📥 Download PDF", size="sm")
                                    stage5_pdf_file = gr.File(label="Stage 5 PDF", visible=False)

                                with gr.Tab("Stage 6: Executive Summary"):
                                    stage6_output = gr.Markdown(
                                        value="Run pipeline to generate executive summary..."
                                    )
                                    download_stage6_btn = gr.Button("📥 Download PDF", size="sm")
                                    stage6_pdf_file = gr.File(label="Stage 6 PDF", visible=False)

                                with gr.Tab("📦 Download All"):
                                    gr.Markdown("### Download Complete Report")
                                    gr.Markdown("Generate a single PDF containing all pipeline stages")
                                    download_all_btn = gr.Button("📥 Download Full Report PDF", variant="primary")
                                    all_stages_pdf_file = gr.File(label="Full Report PDF")

                                # Story 11.3c: Add curation interface tab
                                if create_curation_tab:
                                    with gr.Tab("📚 Example Curation"):
                                        # Create curation interface
                                        curation_content = create_curation_tab(
                                            storage_path=str(Path(__file__).parent / "successful_examples"),
                                            usage_tracker=self.usage_tracker
                                        )
                                        # Note: curation_content is a gr.Blocks that renders inside this tab

                                # Story 11.6.1: Custom Prompts tab
                                with gr.Tab("📂 Custom Prompts"):
                                    gr.Markdown("## 📂 Custom Prompt Templates")
                                    gr.Markdown("Download default templates, customize them, and upload for pipeline execution")

                                    # DOWNLOAD SECTION
                                    with gr.Accordion("📥 Download Templates", open=True):
                                        gr.Markdown("### Download Individual Templates")

                                        with gr.Row():
                                            download_stage0_tmpl_btn = gr.Button("📥 Stage 0", size="sm")
                                            download_stage1_tmpl_btn = gr.Button("📥 Stage 1", size="sm")
                                            download_stage2_tmpl_btn = gr.Button("📥 Stage 2", size="sm")
                                            download_stage3_tmpl_btn = gr.Button("📥 Stage 3", size="sm")

                                        with gr.Row():
                                            download_stage4_tmpl_btn = gr.Button("📥 Stage 4", size="sm")
                                            download_stage5_tmpl_btn = gr.Button("📥 Stage 5", size="sm")
                                            download_stage6_tmpl_btn = gr.Button("📥 Stage 6", size="sm")
                                            download_all_tmpl_btn = gr.Button("📦 Download ALL (ZIP)", variant="primary", size="sm")

                                        # File outputs for downloads
                                        stage0_tmpl_file = gr.File(label="Stage 0 Template", visible=False)
                                        stage1_tmpl_file = gr.File(label="Stage 1 Template", visible=False)
                                        stage2_tmpl_file = gr.File(label="Stage 2 Template", visible=False)
                                        stage3_tmpl_file = gr.File(label="Stage 3 Template", visible=False)
                                        stage4_tmpl_file = gr.File(label="Stage 4 Template", visible=False)
                                        stage5_tmpl_file = gr.File(label="Stage 5 Template", visible=False)
                                        stage6_tmpl_file = gr.File(label="Stage 6 Template", visible=False)
                                        all_tmpl_zip_file = gr.File(label="All Templates (ZIP)", visible=False)

                                    # UPLOAD SECTION
                                    with gr.Accordion("📤 Upload Custom Prompts", open=True):
                                        gr.Markdown("### Upload Customized Templates (Optional)")
                                        gr.Markdown("ℹ️ **Help:** Leave blank to use default prompt. Max 1MB per file.")

                                        # 7 file upload components
                                        custom_prompt_stage0 = gr.File(
                                            label="Stage 0 Custom Prompt (optional)",
                                            file_types=[".md"],
                                            file_count="single"
                                        )
                                        custom_prompt_stage1 = gr.File(
                                            label="Stage 1 Custom Prompt (optional)",
                                            file_types=[".md"],
                                            file_count="single"
                                        )
                                        custom_prompt_stage2 = gr.File(
                                            label="Stage 2 Custom Prompt (optional)",
                                            file_types=[".md"],
                                            file_count="single"
                                        )
                                        custom_prompt_stage3 = gr.File(
                                            label="Stage 3 Custom Prompt (optional)",
                                            file_types=[".md"],
                                            file_count="single"
                                        )
                                        custom_prompt_stage4 = gr.File(
                                            label="Stage 4 Custom Prompt (optional)",
                                            file_types=[".md"],
                                            file_count="single"
                                        )
                                        custom_prompt_stage5 = gr.File(
                                            label="Stage 5 Custom Prompt (optional)",
                                            file_types=[".md"],
                                            file_count="single"
                                        )
                                        custom_prompt_stage6 = gr.File(
                                            label="Stage 6 Custom Prompt (optional)",
                                            file_types=[".md"],
                                            file_count="single"
                                        )

                                        # Validation button and results
                                        validate_prompts_btn = gr.Button("✅ Validate Uploaded Prompts", variant="primary")
                                        validation_results = gr.Markdown(value="Upload files and click validate to check placeholders")

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

            # SIDEBAR EVENT HANDLERS

            # Refresh experiments list
            async def refresh_experiments_list(quality, brand):
                """Refresh experiments list based on filters"""
                return await self.fetch_saved_experiments(
                    quality_filter=quality,
                    brand_filter=brand,
                    limit=20
                )

            refresh_experiments_btn.click(
                refresh_experiments_list,
                inputs=[sidebar_quality_filter, sidebar_brand_filter],
                outputs=experiments_list
            )

            sidebar_quality_filter.change(
                refresh_experiments_list,
                inputs=[sidebar_quality_filter, sidebar_brand_filter],
                outputs=experiments_list
            )

            sidebar_brand_filter.change(
                refresh_experiments_list,
                inputs=[sidebar_quality_filter, sidebar_brand_filter],
                outputs=experiments_list
            )

            # Load experiment when button clicked
            async def load_saved_experiment(exp_id, state):
                """Load complete experiment and populate UI"""
                if not exp_id or len(exp_id) < 3:
                    return (
                        state, "", "", "", "",
                        "", "", "", "", "", "", "",
                        "Error: Please enter a valid experiment ID"
                    )

                # Fetch full experiment data
                experiment = await self.load_experiment(exp_id)

                if not experiment:
                    return (
                        state, "", "", "", "",
                        "", "", "", "", "", "", "",
                        f"Error: Experiment {exp_id} not found"
                    )

                # Extract data (camelCase fields from Experiment table)
                brand_profile = experiment.get("brandProfile", {})
                stage_outputs = experiment.get("stageOutputs", {})

                # Update state
                state["pdf_text"] = experiment.get("reportText", "")
                state["brand_profile"] = brand_profile
                state["run_id"] = experiment.get("runId", "")
                state["stage_outputs"] = stage_outputs

                # Extract brand fields
                brand_name_val = brand_profile.get("brand_name", "")
                industry_val = brand_profile.get("industry", "")
                geography_val = brand_profile.get("country", "")
                portfolio_list = brand_profile.get("product_portfolio", [])
                portfolio_val = "\n".join(portfolio_list) if isinstance(portfolio_list, list) else ""

                # Extract stage markdown
                stage0 = stage_outputs.get("stage_0", {}).get("markdown", "")
                stage1 = stage_outputs.get("stage_1", {}).get("markdown", "")
                stage2 = stage_outputs.get("stage_2", {}).get("markdown", "")
                stage3 = stage_outputs.get("stage_3", {}).get("markdown", "")
                stage4 = stage_outputs.get("stage_4", {}).get("markdown", "")
                stage5 = stage_outputs.get("stage_5", {}).get("markdown", "")
                stage6 = stage_outputs.get("stage_6", {}).get("markdown", "")

                status_msg = f"✅ Loaded experiment {exp_id[:8]} - {brand_name_val}"

                return (
                    state,
                    brand_name_val, industry_val, geography_val, portfolio_val,
                    stage0, stage1, stage2, stage3, stage4, stage5, stage6,
                    status_msg
                )

            load_experiment_btn.click(
                load_saved_experiment,
                inputs=[selected_experiment_id, cached_data],
                outputs=[
                    cached_data,
                    brand_name, industry, geography, product_portfolio,
                    stage0_output, stage1_output, stage2_output, stage3_output,
                    stage4_output, stage5_output, stage6_output,
                    load_status
                ]
            )

            # Auto-refresh experiments list on demo load
            demo.load(
                refresh_experiments_list,
                inputs=[sidebar_quality_filter, sidebar_brand_filter],
                outputs=experiments_list
            )

            # RENAME AND DELETE HANDLERS

            # Show rename input when rename button clicked
            def show_rename_ui():
                return gr.update(visible=True)

            rename_experiment_btn.click(
                show_rename_ui,
                outputs=rename_group
            )

            # Hide rename input when cancel clicked
            def hide_rename_ui():
                return gr.update(visible=False), ""

            cancel_rename_btn.click(
                hide_rename_ui,
                outputs=[rename_group, rename_input]
            )

            # Confirm rename
            async def confirm_rename(exp_id, new_name, quality_filter, brand_filter):
                if not exp_id or not new_name:
                    return (
                        gr.update(visible=False),
                        "",
                        "❌ Error: Please provide both experiment ID and new name",
                        await self.fetch_saved_experiments(quality_filter, brand_filter, 20)
                    )

                status_msg = await self.rename_experiment(exp_id, new_name)

                # Refresh experiments list
                updated_list = await self.fetch_saved_experiments(quality_filter, brand_filter, 20)

                return (
                    gr.update(visible=False),  # Hide rename group
                    "",  # Clear rename input
                    status_msg,  # Show status
                    updated_list  # Refresh list
                )

            confirm_rename_btn.click(
                confirm_rename,
                inputs=[selected_experiment_id, rename_input, sidebar_quality_filter, sidebar_brand_filter],
                outputs=[rename_group, rename_input, load_status, experiments_list]
            )

            # Delete experiment
            async def confirm_delete(exp_id, quality_filter, brand_filter):
                if not exp_id:
                    return (
                        "❌ Error: Please provide experiment ID",
                        await self.fetch_saved_experiments(quality_filter, brand_filter, 20)
                    )

                status_msg = await self.delete_experiment(exp_id)

                # Refresh experiments list and clear selection
                updated_list = await self.fetch_saved_experiments(quality_filter, brand_filter, 20)

                return status_msg, updated_list, ""

            delete_experiment_btn.click(
                confirm_delete,
                inputs=[selected_experiment_id, sidebar_quality_filter, sidebar_brand_filter],
                outputs=[load_status, experiments_list, selected_experiment_id]
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

                # Extract custom prompts from state (Story 11.6.1)
                custom_prompts_data = state.get("custom_prompts", {})
                custom_prompts = None
                if custom_prompts_data:
                    # Convert to dict of content strings only (exclude metadata)
                    custom_prompts = {
                        stage_key: data["content"]
                        for stage_key, data in custom_prompts_data.items()
                    }

                # Run pipeline
                stage0, stage1, stage2, stage3, stage4, stage5, stage6, status = await self.run_pipeline(
                    pdf_text, brand_name_val, industry_val, geography_val, portfolio_val,
                    custom_prompts=custom_prompts
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

                # Extract stage inputs and prompts from backend for few-shot learning
                # This captures the actual pipeline execution metadata needed for training examples
                stage_inputs = {}
                prompts_used = {}

                try:
                    # Get run_id from status response (embedded in message)
                    run_id_from_status = None
                    if "Run ID:" in status:
                        run_id_from_status = status.split("Run ID:")[-1].strip()

                    if run_id_from_status:
                        # Query backend /status endpoint to get full pipeline metadata
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            status_response = await client.get(
                                f"{self.backend_url}/status/{run_id_from_status}"
                            )

                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                stages = status_data.get("stages", {})

                                # Extract inputs and prompts from each stage
                                for stage_key, stage_info in stages.items():
                                    # Try to extract input data
                                    input_data = None
                                    for input_key in ["input", "input_data", "input_text", "inputs"]:
                                        if input_key in stage_info:
                                            input_data = stage_info[input_key]
                                            break

                                    # Fallback: populate known stage inputs
                                    if not input_data:
                                        if stage_key == "0":
                                            input_data = state["brand_profile"]
                                        elif stage_key == "1":
                                            input_data = {"pdf_text": pdf_text[:1000]}  # First 1000 chars

                                    if input_data:
                                        stage_inputs[f"stage_{stage_key}"] = input_data

                                    # Try to extract prompt template
                                    prompt = None
                                    if "prompt" in stage_info:
                                        prompt = stage_info["prompt"]
                                    elif "metadata" in stage_info and isinstance(stage_info["metadata"], dict):
                                        prompt = stage_info["metadata"].get("prompt")

                                    if prompt:
                                        prompts_used[f"stage_{stage_key}"] = prompt

                except Exception as e:
                    print(f"Warning: Failed to extract stage metadata: {e}")

                # Fallback: ensure at least stage 0 and 1 have input data
                if "stage_0" not in stage_inputs:
                    stage_inputs["stage_0"] = state["brand_profile"]
                if "stage_1" not in stage_inputs:
                    stage_inputs["stage_1"] = {"pdf_text": pdf_text[:1000]}

                state["stage_inputs"] = stage_inputs
                state["prompts_used"] = prompts_used

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

            # PDF Download Event Handlers
            def download_stage_pdf(stage_num, state):
                """Generate PDF for specific stage"""
                if state is None:
                    return None

                brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
                stage_key = f"stage_{stage_num}"
                markdown = state.get("stage_outputs", {}).get(stage_key, {}).get("markdown", "")

                if not markdown:
                    return None

                pdf_path = self.generate_stage_pdf_file(stage_num, markdown, brand_name)
                return pdf_path

            # Wire up individual stage downloads
            download_stage0_btn.click(
                lambda s: download_stage_pdf(0, s),
                inputs=[cached_data],
                outputs=[stage0_pdf_file]
            )

            download_stage1_btn.click(
                lambda s: download_stage_pdf(1, s),
                inputs=[cached_data],
                outputs=[stage1_pdf_file]
            )

            download_stage2_btn.click(
                lambda s: download_stage_pdf(2, s),
                inputs=[cached_data],
                outputs=[stage2_pdf_file]
            )

            download_stage3_btn.click(
                lambda s: download_stage_pdf(3, s),
                inputs=[cached_data],
                outputs=[stage3_pdf_file]
            )

            download_stage4_btn.click(
                lambda s: download_stage_pdf(4, s),
                inputs=[cached_data],
                outputs=[stage4_pdf_file]
            )

            download_stage5_btn.click(
                lambda s: download_stage_pdf(5, s),
                inputs=[cached_data],
                outputs=[stage5_pdf_file]
            )

            download_stage6_btn.click(
                lambda s: download_stage_pdf(6, s),
                inputs=[cached_data],
                outputs=[stage6_pdf_file]
            )

            # Download all stages combined
            def download_all_stages_pdf(state):
                """Generate combined PDF with all stages"""
                if state is None:
                    return None

                brand_name = state.get("brand_profile", {}).get("brand_name", "Unknown Brand")
                stage_outputs = state.get("stage_outputs", {})

                # Collect markdown from all stages
                markdowns = {}
                for i in range(7):
                    stage_key = f"stage_{i}"
                    markdown = stage_outputs.get(stage_key, {}).get("markdown", "")
                    if markdown:
                        markdowns[i] = markdown

                if not markdowns:
                    return None

                pdf_path = self.generate_all_stages_pdf_file(markdowns, brand_name)
                return pdf_path

            download_all_btn.click(
                download_all_stages_pdf,
                inputs=[cached_data],
                outputs=[all_stages_pdf_file]
            )

            # Story 11.6.1: Custom Prompts event handlers

            # Download individual template handlers
            def download_single_template(stage: int) -> str:
                """Download a single prompt template file"""
                try:
                    prompts_dir = self.resolve_prompts_dir()
                    template_files = {
                        0: "stage_0_enrichment.md",
                        1: "stage_1_extraction.md",
                        2: "stage_2_convergence.md",
                        3: "stage_3_technique_matching.md",
                        4: "stage_4_concept_generation.md",
                        5: "stage_5_competitive_search.md",
                        6: "stage_6_packaging.md"
                    }
                    template_path = prompts_dir / template_files[stage]
                    if template_path.exists():
                        return str(template_path)
                    else:
                        return None
                except Exception as e:
                    print(f"Error downloading stage {stage} template: {e}")
                    return None

            download_stage0_tmpl_btn.click(lambda: download_single_template(0), outputs=stage0_tmpl_file)
            download_stage1_tmpl_btn.click(lambda: download_single_template(1), outputs=stage1_tmpl_file)
            download_stage2_tmpl_btn.click(lambda: download_single_template(2), outputs=stage2_tmpl_file)
            download_stage3_tmpl_btn.click(lambda: download_single_template(3), outputs=stage3_tmpl_file)
            download_stage4_tmpl_btn.click(lambda: download_single_template(4), outputs=stage4_tmpl_file)
            download_stage5_tmpl_btn.click(lambda: download_single_template(5), outputs=stage5_tmpl_file)
            download_stage6_tmpl_btn.click(lambda: download_single_template(6), outputs=stage6_tmpl_file)

            # Download all templates as ZIP
            def download_all_templates() -> str:
                """Download all templates as ZIP"""
                try:
                    zip_path = self.create_default_template_zip()
                    return zip_path
                except Exception as e:
                    print(f"Error creating template ZIP: {e}")
                    return None

            download_all_tmpl_btn.click(download_all_templates, outputs=all_tmpl_zip_file)

            # File upload handlers - store content in cached_data
            def handle_file_upload(file, stage: int, state):
                """Handle custom prompt file upload and store in state"""
                if file is None:
                    # Clear this stage if file removed
                    if f"stage_{stage}" in state.get("custom_prompts", {}):
                        del state["custom_prompts"][f"stage_{stage}"]
                    return state

                try:
                    # Validate file size (1MB limit)
                    file_size = os.path.getsize(file.name)
                    if file_size > 1_000_000:
                        print(f"Error: File too large for stage {stage} ({file_size / 1024:.1f}KB, max 1MB)")
                        return state

                    # Read file content
                    with open(file.name, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Store in state
                    if "custom_prompts" not in state:
                        state["custom_prompts"] = {}

                    from datetime import datetime
                    state["custom_prompts"][f"stage_{stage}"] = {
                        "filename": os.path.basename(file.name),
                        "content": content,
                        "uploaded_at": datetime.now().isoformat()
                    }

                    return state
                except Exception as e:
                    print(f"Error reading uploaded file for stage {stage}: {e}")
                    return state

            custom_prompt_stage0.change(lambda f, s: handle_file_upload(f, 0, s), inputs=[custom_prompt_stage0, cached_data], outputs=cached_data)
            custom_prompt_stage1.change(lambda f, s: handle_file_upload(f, 1, s), inputs=[custom_prompt_stage1, cached_data], outputs=cached_data)
            custom_prompt_stage2.change(lambda f, s: handle_file_upload(f, 2, s), inputs=[custom_prompt_stage2, cached_data], outputs=cached_data)
            custom_prompt_stage3.change(lambda f, s: handle_file_upload(f, 3, s), inputs=[custom_prompt_stage3, cached_data], outputs=cached_data)
            custom_prompt_stage4.change(lambda f, s: handle_file_upload(f, 4, s), inputs=[custom_prompt_stage4, cached_data], outputs=cached_data)
            custom_prompt_stage5.change(lambda f, s: handle_file_upload(f, 5, s), inputs=[custom_prompt_stage5, cached_data], outputs=cached_data)
            custom_prompt_stage6.change(lambda f, s: handle_file_upload(f, 6, s), inputs=[custom_prompt_stage6, cached_data], outputs=cached_data)

            # Validation handler
            def validate_uploaded_prompts(state):
                """Validate all uploaded prompt files for required placeholders"""
                custom_prompts = state.get("custom_prompts", {})

                if not custom_prompts:
                    return "ℹ️ **No custom prompts uploaded.** Upload files to validate."

                results = []
                has_errors = False

                for stage in range(7):
                    stage_key = f"stage_{stage}"

                    if stage_key in custom_prompts:
                        # File uploaded - validate it
                        filename = custom_prompts[stage_key]["filename"]
                        content = custom_prompts[stage_key]["content"]

                        is_valid, missing = self.validate_placeholders(stage, content)

                        if is_valid:
                            results.append(f"✅ **Stage {stage}:** Valid ({filename})")
                        else:
                            has_errors = True
                            missing_str = ", ".join([f"`{{{p}}}`" for p in missing])
                            results.append(f"❌ **Stage {stage}:** MISSING placeholders: {missing_str} ({filename})")
                    else:
                        # No file uploaded - using default
                        results.append(f"ℹ️ **Stage {stage}:** Using default prompt (no file uploaded)")

                # Add summary
                if has_errors:
                    summary = "\n\n⚠️ **VALIDATION FAILED:** Fix missing placeholders before running pipeline.\n\n"
                else:
                    summary = "\n\n✅ **VALIDATION PASSED:** All uploaded prompts contain required placeholders.\n\n"

                return summary + "\n".join(results)

            validate_prompts_btn.click(
                validate_uploaded_prompts,
                inputs=[cached_data],
                outputs=validation_results
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

            # TODO: Add export UI controls (Story 11.4b)
            # async def backup_wrapper():
            #     file_path, status = await self.create_backup()
            #     return file_path, status
            #
            # export_json_btn.click(
            #     export_json_wrapper,
            #     inputs=[export_quality, export_brand, export_start_date, export_end_date],
            #     outputs=[export_file, export_status]
            # )
            #
            # export_csv_btn.click(
            #     export_csv_wrapper,
            #     inputs=[export_quality, export_brand, export_start_date, export_end_date],
            #     outputs=[export_file, export_status]
            # )
            #
            # backup_btn.click(
            #     backup_wrapper,
            #     inputs=[],
            #     outputs=[export_file, export_status]
            # )

        return demo

    def launch(self, share=False):
        """Launch Gradio interface

        Args:
            share: Create public Gradio share link
        """
        demo = self.build_interface()

        # Detect HuggingFace Spaces environment
        is_hf_space = os.getenv("SPACE_ID") is not None

        # Configure queue and launch
        demo.queue(
            max_size=10,
            default_concurrency_limit=3
        ).launch(
            server_name="0.0.0.0",
            server_port=int(os.getenv("PORT", 7860)),
            share=share or is_hf_space
        )


if __name__ == "__main__":
    lab = GradioLab()
    lab.launch(share=False)
