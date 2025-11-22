"""API Route Handlers

Implementation for pipeline execution and status endpoints.
"""
import os
import json
import logging
import time
from pathlib import Path
from threading import Thread
from typing import Dict, Any, Optional

import requests
import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.models import (
    RunPipelineRequest,
    RunPipelineResponse,
    PipelineStatus,
    HealthResponse,
    SaveExperimentRequest,
    SaveExperimentResponse,
    RenameExperimentRequest,
    RenameExperimentResponse
)
from app.pipeline_runner import execute_pipeline_background

logger = logging.getLogger(__name__)

router = APIRouter()


def generate_run_id() -> str:
    """Generate unique run ID in format run-{timestamp}-{random}"""
    import random
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    return f"run-{timestamp}-{random_suffix}"


def validate_blob_url(url: str) -> bool:
    """Validate blob URL is from Vercel Blob storage."""
    return url.startswith("https://") and "blob.vercel-storage.com" in url


def download_pdf_from_blob(blob_url: str, run_id: str) -> str:
    """Download PDF from Vercel Blob and save to /tmp.

    Args:
        blob_url: Vercel Blob URL
        run_id: Run identifier

    Returns:
        Path to downloaded PDF

    Raises:
        HTTPException: If download fails or file invalid
    """
    pdf_path = f"/tmp/{run_id}.pdf"

    try:
        logger.info(f"Downloading PDF from {blob_url}")
        response = requests.get(blob_url, timeout=30)
        response.raise_for_status()

        # Validate file size (max 25MB)
        content_length = len(response.content)
        if content_length > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="PDF file size exceeds 25MB limit"
            )

        # Save to temp file
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        logger.info(f"PDF downloaded successfully: {pdf_path} ({content_length} bytes)")
        return pdf_path

    except requests.RequestException as e:
        logger.error(f"Failed to download PDF from blob: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download PDF from Vercel Blob: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error saving PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF download: {str(e)}"
        )


def load_brand_profile(brand_id: str) -> Dict[str, Any]:
    """Load brand profile from YAML file.

    Args:
        brand_id: Brand identifier (e.g., 'lactalis-canada')

    Returns:
        Brand profile data

    Raises:
        HTTPException: If brand not found or YAML malformed
    """
    # Look in both backend/data and /data (for local dev vs Railway)
    possible_paths = [
        Path(__file__).parent.parent / "data" / "brand-profiles" / f"{brand_id}.yaml",
        Path("/app/data/brand-profiles") / f"{brand_id}.yaml"
    ]

    yaml_path = None
    for path in possible_paths:
        if path.exists():
            yaml_path = path
            break

    if not yaml_path:
        logger.error(f"Brand profile not found: {brand_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Brand '{brand_id}' not found"
        )

    try:
        with open(yaml_path, "r") as f:
            brand_profile = yaml.safe_load(f)

        # Validate required fields
        required_fields = ["company_name", "portfolio", "positioning"]
        missing_fields = [field for field in required_fields if field not in brand_profile]

        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Brand profile missing required fields: {', '.join(missing_fields)}"
            )

        logger.info(f"Loaded brand profile for {brand_id}")
        return brand_profile

    except yaml.YAMLError as e:
        logger.error(f"Malformed YAML for brand {brand_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Malformed brand profile YAML: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error loading brand profile {brand_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading brand profile: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, operation_id="health_check")
async def health_check():
    """Health check endpoint for Railway monitoring

    Returns 'ok' if all required environment variables are present AND
    frontend webhook URL is reachable, 'degraded' otherwise.
    """
    required_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "LLM_MODEL",
        "VERCEL_BLOB_READ_WRITE_TOKEN"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    # Test frontend connectivity
    frontend_url = os.getenv("FRONTEND_WEBHOOK_URL", "https://innovation-web-rho.vercel.app")
    frontend_reachable = False

    try:
        # Try to ping frontend health endpoint with 5s timeout
        response = requests.get(f"{frontend_url}/api/health", timeout=5)
        frontend_reachable = response.ok
        if not frontend_reachable:
            logger.warning(f"Frontend health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Frontend not reachable at {frontend_url}: {e}")

    # Status is degraded if env vars missing OR frontend unreachable
    status = "degraded" if (missing_vars or not frontend_reachable) else "ok"

    details = {}
    if missing_vars:
        details["missing_env_vars"] = missing_vars
    if not frontend_reachable:
        details["frontend_status"] = "unreachable"
        details["frontend_url"] = frontend_url

    return HealthResponse(status=status, version="1.0.0", details=details if details else None)


class RunPipelineLocalRequest(BaseModel):
    """Request model for local development - accepts PDF text directly"""
    pdf_text: str = Field(..., description="Extracted PDF text content")
    brand_profile: Dict[str, Any] = Field(..., description="Brand profile dict")
    run_id: Optional[str] = Field(None, description="Optional run ID")


@router.post("/run/local", response_model=RunPipelineResponse, operation_id="run_pipeline_local")
async def run_pipeline_local(request: RunPipelineLocalRequest):
    """
    Start pipeline execution (LOCAL DEVELOPMENT ONLY)

    Accepts PDF text and brand profile directly instead of blob URL.
    Used by Gradio experimentation UI.
    """
    # Use frontend-provided run_id or generate new one
    run_id = request.run_id or generate_run_id()
    logger.info(f"[LOCAL] Pipeline run_id: {run_id}")

    # Save PDF text to temp file
    run_dir = Path("/tmp/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = run_dir / "input.txt"
    with open(pdf_path, "w") as f:
        f.write(request.pdf_text)

    logger.info(f"[LOCAL] Saved PDF text to {pdf_path}")

    # Use provided brand profile directly
    brand_profile = request.brand_profile
    logger.info(f"[LOCAL] Using brand profile: {brand_profile.get('brand_name', 'Unknown')}")

    # Create initial status file before starting background thread
    status_file = run_dir / "status.json"
    initial_status = {
        "run_id": run_id,
        "status": "running",
        "current_stage": 0,
        "stages": {},
        "brand_id": brand_profile.get("brand_name", "unknown"),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with open(status_file, "w") as f:
        json.dump(initial_status, f, indent=2)

    logger.info(f"[LOCAL] Created initial status file: {status_file}")

    # Start background execution with pre-extracted text
    thread = Thread(
        target=execute_pipeline_background,
        args=(run_id, str(pdf_path), brand_profile, request.pdf_text),
        daemon=True
    )
    thread.start()

    logger.info(f"[LOCAL] Started pipeline execution for run {run_id}")

    return RunPipelineResponse(run_id=run_id, status="running")


@router.post("/run", response_model=RunPipelineResponse, operation_id="run_pipeline")
async def run_pipeline(request: RunPipelineRequest):
    """
    Start pipeline execution

    Accepts blob URL and brand ID, downloads PDF, and executes
    5-stage pipeline in background.

    If run_id is provided by frontend, use it (prevents race condition).
    """
    # Validate blob URL
    if not validate_blob_url(request.blob_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid blob URL. Must be HTTPS URL from blob.vercel-storage.com"
        )

    # Use frontend-provided run_id or generate new one
    run_id = request.run_id or generate_run_id()
    logger.info(f"Pipeline run_id: {run_id} {'(frontend-provided)' if request.run_id else '(backend-generated)'}")

    # Download PDF
    pdf_path = download_pdf_from_blob(request.blob_url, run_id)

    # Load brand profile
    brand_profile = load_brand_profile(request.brand_id)

    # Start background execution
    thread = Thread(
        target=execute_pipeline_background,
        args=(run_id, pdf_path, brand_profile),
        daemon=True
    )
    thread.start()

    logger.info(f"Started pipeline execution for run {run_id}")

    return RunPipelineResponse(run_id=run_id, status="running")


@router.get("/status/{run_id}", response_model=PipelineStatus, operation_id="get_status")
async def get_status(run_id: str):
    """
    Get pipeline execution status

    Returns current status including stage progress and outputs.
    """
    status_file = Path("/tmp/runs") / run_id / "status.json"

    if not status_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found"
        )

    try:
        with open(status_file, "r") as f:
            status_data = json.load(f)

        return PipelineStatus(**status_data)

    except json.JSONDecodeError as e:
        logger.error(f"Corrupted status file for run {run_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Status file corrupted"
        )
    except Exception as e:
        logger.error(f"Error reading status for run {run_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading status: {str(e)}"
        )


# ============================================
# MCP Development & Debug Tools
# ============================================

@router.get("/brands", operation_id="list_brands")
async def list_brands():
    """List all available brand profiles for pipeline execution

    Returns list of brand IDs that can be used with run_pipeline.
    """
    # Look in both backend/data and /data (for local dev vs Railway)
    possible_paths = [
        Path(__file__).parent.parent / "data" / "brand-profiles",
        Path("/app/data/brand-profiles")
    ]

    brand_dir = None
    for path in possible_paths:
        if path.exists():
            brand_dir = path
            break

    if not brand_dir:
        return {"brands": [], "count": 0}

    brands = []
    for yaml_file in brand_dir.glob("*.yaml"):
        brand_id = yaml_file.stem
        brands.append(brand_id)

    return {
        "brands": sorted(brands),
        "count": len(brands)
    }


@router.get("/brands/{brand_id}", operation_id="get_brand_profile")
async def get_brand_profile_endpoint(brand_id: str):
    """Get detailed brand profile configuration by ID

    Returns the full brand profile YAML data including company_name,
    portfolio, positioning, and other configuration.
    """
    # Reuse existing load_brand_profile() helper
    brand_profile = load_brand_profile(brand_id)

    return {
        "brand_id": brand_id,
        "profile": brand_profile
    }


@router.get("/config/env-check", operation_id="check_environment")
async def check_environment():
    """Check which environment variables are configured

    Verifies presence of required environment variables without
    exposing their values. Useful for deployment validation.
    """
    required_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "LLM_MODEL",
        "VERCEL_BLOB_READ_WRITE_TOKEN"
    ]

    optional_vars = [
        "WEBHOOK_SECRET",
        "FRONTEND_WEBHOOK_URL"
    ]

    configured = []
    missing = []
    warnings = []

    # Check required vars
    for var in required_vars:
        value = os.getenv(var)
        if value:
            configured.append(var)
        else:
            missing.append(var)

    # Check optional vars
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            configured.append(var)
        else:
            warnings.append(f"{var} not set (optional)")

    return {
        "configured": configured,
        "missing": missing,
        "warnings": warnings,
        "status": "ok" if not missing else "incomplete"
    }


@router.get("/debug/runs", operation_id="list_all_runs")
async def list_all_runs(limit: int = 20):
    """List all pipeline runs with status

    Returns recent pipeline executions for debugging and monitoring.
    Useful for checking pipeline history and finding run IDs.
    """
    runs_dir = Path("/tmp/runs")

    if not runs_dir.exists():
        return {"runs": [], "count": 0}

    runs = []

    # Get all run directories
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir():
            continue

        run_id = run_dir.name
        status_file = run_dir / "status.json"

        if status_file.exists():
            try:
                with open(status_file, "r") as f:
                    status_data = json.load(f)

                runs.append({
                    "run_id": run_id,
                    "status": status_data.get("status", "unknown"),
                    "current_stage": status_data.get("current_stage", 0),
                    "brand_id": status_data.get("brand_id", "unknown"),
                    "created_at": status_data.get("created_at", None)
                })
            except Exception as e:
                logger.warning(f"Could not read status for {run_id}: {e}")
                runs.append({
                    "run_id": run_id,
                    "status": "error_reading_status",
                    "error": str(e)
                })

    # Sort by creation time (newest first)
    runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Limit results
    runs = runs[:limit]

    return {
        "runs": runs,
        "count": len(runs),
        "limit": limit
    }


@router.get("/debug/runs/{run_id}/stage/{stage_num}", operation_id="get_stage_output")
async def get_stage_output(run_id: str, stage_num: int):
    """Get raw output from specific pipeline stage

    Returns the complete output JSON from a specific stage,
    useful for debugging stage failures and inspecting intermediate results.
    """
    if stage_num < 1 or stage_num > 5:
        raise HTTPException(
            status_code=400,
            detail="Stage number must be between 1 and 5"
        )

    run_dir = Path("/tmp/runs") / run_id

    if not run_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found"
        )

    # Look for stage output file
    stage_file = run_dir / f"stage{stage_num}_output.json"

    if not stage_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Stage {stage_num} output not found for run '{run_id}'. Stage may not have completed yet."
        )

    try:
        with open(stage_file, "r") as f:
            stage_data = json.load(f)

        return {
            "run_id": run_id,
            "stage": stage_num,
            "output": stage_data
        }

    except json.JSONDecodeError as e:
        logger.error(f"Corrupted stage output for {run_id}/stage{stage_num}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Stage {stage_num} output file corrupted"
        )
    except Exception as e:
        logger.error(f"Error reading stage output {run_id}/stage{stage_num}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading stage output: {str(e)}"
        )


# ============================================
# Experiment Storage (Gradio Integration)
# ============================================

@router.post("/experiments/save", response_model=SaveExperimentResponse, operation_id="save_experiment")
async def save_experiment(request: SaveExperimentRequest):
    """Save experiment data from Gradio UI to PostgreSQL database

    Stores experiment results with quality tagging for later retrieval
    and few-shot learning. Uses direct PostgreSQL connection for Gradio-only mode.

    Args:
        request: Experiment data including run_id, outputs, quality tag

    Returns:
        Success status and experiment ID
    """
    try:
        import psycopg2
        import psycopg2.extras
        import json
        from datetime import datetime, timezone

        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(
                status_code=500,
                detail="DATABASE_URL not configured"
            )

        # Generate experiment ID
        experiment_id = f"exp-{int(time.time())}-{request.run_id[:8]}"

        # Connect to PostgreSQL and save experiment
        conn = psycopg2.connect(database_url)
        try:
            with conn.cursor() as cur:
                # Insert into Experiment table
                # Schema: id, runId, reportText, reportName, brandProfile (JSONB),
                #         stageOutputs (JSONB), qualityTag, experimentNotes, pipelineVersion, createdAt
                cur.execute("""
                    INSERT INTO "Experiment" (
                        id, "runId", "reportText", "reportName", "brandProfile",
                        "stageOutputs", "qualityTag", "experimentNotes",
                        "pipelineVersion", "createdAt"
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    experiment_id,
                    request.run_id,
                    request.report_text,
                    None,  # reportName
                    json.dumps(request.brand_profile),  # JSONB
                    json.dumps(request.stage_outputs),  # JSONB
                    request.quality_tag,
                    request.notes,
                    "1.0",  # pipelineVersion
                    datetime.now(timezone.utc)
                ))

                conn.commit()
                saved_id = cur.fetchone()[0]

            logger.info(f"Saved experiment {saved_id} to PostgreSQL with quality tag '{request.quality_tag}'")

            return SaveExperimentResponse(
                success=True,
                message=f"Experiment saved to database with tag '{request.quality_tag}'",
                experiment_id=saved_id
            )

        finally:
            conn.close()

    except psycopg2.Error as db_error:
        logger.error(f"PostgreSQL error saving experiment: {db_error}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(db_error)}"
        )
    except Exception as e:
        logger.error(f"Failed to save experiment to database: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save experiment: {str(e)}"
        )


@router.get("/experiments/list", operation_id="list_experiments")
async def list_experiments(
    quality_tag: Optional[str] = None,
    brand_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pipeline_version: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    order_by: str = "timestamp_desc"
):
    """List experiments from database with filtering and pagination

    Direct PostgreSQL query for Gradio UI.

    Args:
        quality_tag: Filter by quality (good/needs_work/failed)
        brand_name: Filter by brand name
        start_date: Filter by timestamp >= start_date (ISO format)
        end_date: Filter by timestamp <= end_date (ISO format)
        pipeline_version: Filter by pipeline version
        page: Page number (default: 1)
        page_size: Results per page (default: 20, max: 100)
        order_by: Sort order (timestamp_desc/timestamp_asc/cost_desc)

    Returns:
        List of experiments with pagination metadata
    """
    try:
        import psycopg2
        import psycopg2.extras
        import json

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(status_code=500, detail="DATABASE_URL not configured")

        # Build WHERE clause
        where_clauses = []
        params = []

        if quality_tag:
            where_clauses.append('"quality_tag" = %s')
            params.append(quality_tag)

        if pipeline_version:
            where_clauses.append('"pipeline_version" = %s')
            params.append(pipeline_version)

        if start_date:
            where_clauses.append('"timestamp" >= %s')
            params.append(start_date)

        if end_date:
            where_clauses.append('"timestamp" <= %s')
            params.append(end_date)

        if brand_name:
            where_clauses.append('"brand_profile"::jsonb->>\'brand_name\' = %s')
            params.append(brand_name)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Build ORDER BY clause
        order_sql = '"timestamp" DESC'
        if order_by == "timestamp_asc":
            order_sql = '"timestamp" ASC'
        elif order_by == "cost_desc":
            order_sql = '"cost_usd" DESC NULLS LAST'

        # Calculate pagination
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size

        conn = psycopg2.connect(database_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Get total count
                count_sql = f'SELECT COUNT(*) FROM "Experiment" {where_sql}'
                cur.execute(count_sql, params)
                total = cur.fetchone()['count']

                # Get experiments
                query_sql = f'''
                    SELECT * FROM "Experiment"
                    {where_sql}
                    ORDER BY {order_sql}
                    LIMIT %s OFFSET %s
                '''
                cur.execute(query_sql, params + [page_size, offset])
                experiments = cur.fetchall()

                return {
                    "experiments": experiments,
                    "pagination": {
                        "page": page,
                        "pageSize": page_size,
                        "total": total,
                        "totalPages": (total + page_size - 1) // page_size
                    }
                }

        finally:
            conn.close()

    except psycopg2.Error as db_error:
        logger.error(f"PostgreSQL error listing experiments: {db_error}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        logger.error(f"Failed to list experiments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list experiments: {str(e)}")


@router.get("/experiments/{experiment_id}", operation_id="get_experiment_by_id")
async def get_experiment_by_id(experiment_id: str):
    """Get a single experiment by ID

    Direct PostgreSQL query for Gradio UI.

    Args:
        experiment_id: Experiment UUID or short ID (first 8 chars)

    Returns:
        Complete experiment data including all fields
    """
    try:
        import psycopg2
        import psycopg2.extras

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(status_code=500, detail="DATABASE_URL not configured")

        conn = psycopg2.connect(database_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Support both full UUID and short ID (first 8 chars)
                if len(experiment_id) == 8:
                    cur.execute('SELECT * FROM "Experiment" WHERE "id" LIKE %s LIMIT 1', (f'{experiment_id}%',))
                else:
                    cur.execute('SELECT * FROM "Experiment" WHERE "id" = %s', (experiment_id,))

                experiment = cur.fetchone()

                if not experiment:
                    raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")

                return dict(experiment)

        finally:
            conn.close()

    except HTTPException:
        raise
    except psycopg2.Error as db_error:
        logger.error(f"PostgreSQL error getting experiment {experiment_id}: {db_error}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        logger.error(f"Failed to get experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get experiment: {str(e)}")


@router.put("/experiments/{experiment_id}/rename", operation_id="rename_experiment")
async def rename_experiment(experiment_id: str, request: RenameExperimentRequest):
    """Rename an experiment

    Updates the experimentNotes field with a custom name prefix.

    Args:
        experiment_id: Experiment UUID or short ID
        request: New name for the experiment

    Returns:
        Success status and updated experiment ID
    """
    try:
        import psycopg2

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(status_code=500, detail="DATABASE_URL not configured")

        conn = psycopg2.connect(database_url)
        try:
            with conn.cursor() as cur:
                # Get current notes
                if len(experiment_id) == 8:
                    cur.execute('SELECT "experiment_notes", "id" FROM "Experiment" WHERE "id" LIKE %s LIMIT 1', (f'{experiment_id}%',))
                else:
                    cur.execute('SELECT "experiment_notes", "id" FROM "Experiment" WHERE "id" = %s', (experiment_id,))

                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")

                current_notes, full_id = row

                # Remove existing [NAME: ...] prefix if present
                notes_without_prefix = (current_notes or "").replace(r'^\[NAME: .*?\]\s*', '', 1) if current_notes else ""

                # Add new name prefix
                updated_notes = f"[NAME: {request.new_name}] {notes_without_prefix}".strip()

                # Update experiment
                cur.execute('UPDATE "Experiment" SET "experiment_notes" = %s WHERE "id" = %s', (updated_notes, full_id))
                conn.commit()

                logger.info(f"Renamed experiment {full_id} to '{request.new_name}'")

                return RenameExperimentResponse(
                    success=True,
                    message=f"Experiment renamed to '{request.new_name}'",
                    experiment_id=full_id
                )

        finally:
            conn.close()

    except HTTPException:
        raise
    except psycopg2.Error as db_error:
        logger.error(f"PostgreSQL error renaming experiment {experiment_id}: {db_error}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        logger.error(f"Failed to rename experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rename experiment: {str(e)}")


@router.delete("/experiments/{experiment_id}", operation_id="delete_experiment")
async def delete_experiment(experiment_id: str):
    """Delete an experiment

    Permanently removes experiment from database.

    Args:
        experiment_id: Experiment UUID or short ID

    Returns:
        Success status
    """
    try:
        import psycopg2

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(status_code=500, detail="DATABASE_URL not configured")

        conn = psycopg2.connect(database_url)
        try:
            with conn.cursor() as cur:
                # Get full ID first
                if len(experiment_id) == 8:
                    cur.execute('SELECT "id" FROM "Experiment" WHERE "id" LIKE %s LIMIT 1', (f'{experiment_id}%',))
                else:
                    cur.execute('SELECT "id" FROM "Experiment" WHERE "id" = %s', (experiment_id,))

                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")

                full_id = row[0]

                # Delete experiment
                cur.execute('DELETE FROM "Experiment" WHERE "id" = %s', (full_id,))
                conn.commit()

                logger.info(f"Deleted experiment {full_id}")

                from app.models import DeleteExperimentResponse
                return DeleteExperimentResponse(
                    success=True,
                    message="Experiment deleted successfully",
                    experiment_id=full_id
                )

        finally:
            conn.close()

    except HTTPException:
        raise
    except psycopg2.Error as db_error:
        logger.error(f"PostgreSQL error deleting experiment {experiment_id}: {db_error}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        logger.error(f"Failed to delete experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete experiment: {str(e)}")
