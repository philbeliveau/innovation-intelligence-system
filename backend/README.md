# FastAPI Backend - Innovation Intelligence System

Minimal FastAPI backend for running the CPG Innovation Intelligence Pipeline on Railway, independently from the Vercel-hosted frontend.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── routes.py        # API endpoint handlers (/run, /status, /health)
│   ├── models.py        # Pydantic request/response models
│   └── utils.py         # Helper functions (file cleanup, etc.)
├── pipeline/            # Copy of /pipeline (stages, prompts, utils)
│   ├── stages/          # 5-stage pipeline implementation
│   ├── prompts/         # LLM prompts for each stage
│   └── utils.py         # Pipeline utilities
├── data/
│   └── brand-profiles/  # Brand YAML configurations (4 files)
├── tmp/                 # Runtime temporary files (gitignored)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── README.md            # This file
```

## Local Development Setup

### 1. Prerequisites

- Python 3.11+
- pip (Python package manager)

### 2. Install Dependencies

Create a virtual environment and install requirements:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-sonnet-4.5
PORT=8000
VERCEL_BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
```

### 4. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The server will start at `http://localhost:8000`

### 5. Verify Installation

**Health Check:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"1.0.0"}
```

**API Documentation:**
Visit `http://localhost:8000/docs` to see the interactive OpenAPI documentation.

**Root Endpoint:**
```bash
curl http://localhost:8000/
# Expected: {"name":"Innovation Intelligence API","version":"1.0.0","docs":"/docs"}
```

## API Endpoints

### `GET /health`
Health check endpoint for Railway monitoring.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### `POST /run`
Start pipeline execution. **(PLACEHOLDER - returns 501 in v1.0)**

**Request Body:**
```json
{
  "blob_url": "https://blob.vercel-storage.com/...",
  "brand": "lactalis-canada",
  "run_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "status": "started",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Pipeline execution started"
}
```

### `GET /status/{run_id}`
Get pipeline execution status. **(PLACEHOLDER - returns 501 in v1.0)**

**Response:**
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "current_stage": 3,
  "progress": 60.0
}
```

## Testing

### Test Pipeline Imports

Verify pipeline code imports correctly:

```bash
cd backend
python -c "from pipeline.stages.stage1_input_processing import create_stage1_chain; print('✓ Pipeline imports work')"
```

### Test Brand Profile Loading

Verify brand YAML files are accessible:

```bash
python -c "import yaml; data = yaml.safe_load(open('data/brand-profiles/lactalis-canada.yaml')); print('✓ Brand profile loaded')"
```

### Run FastAPI Server

```bash
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Install dependencies with `pip install -r requirements.txt`

### `ImportError: cannot import name 'run_stage1'`

**Solution:** The pipeline uses `create_stage1_chain()` function, not `run_stage1()`. Check function names in `pipeline/stages/`.

### `FileNotFoundError: [Errno 2] No such file or directory: 'data/brand-profiles/...'`

**Solution:** Ensure you're running commands from the `/backend` directory. Brand profiles are at `backend/data/brand-profiles/`.

### `CORS errors` when calling from frontend

**Solution:** Update `allow_origins` in `app/main.py` to include your Vercel frontend URL.

## Deployment

See **Story 5.2: Railway Deployment Configuration** for deployment instructions.

## Development Status

**Version:** 1.0.0 (Story 5.1 - Backend Structure)

**Current Implementation:**
- ✅ Minimal FastAPI app with CORS
- ✅ Health check endpoint (`/health`)
- ✅ Placeholder endpoints (`/run`, `/status`) - return 501 Not Implemented
- ✅ Pipeline code copied and importable
- ✅ Brand profiles accessible

**Next Steps (Story 5.4):**
- Implement `/run` endpoint (download PDF, execute pipeline)
- Implement `/status` endpoint (read status.json from tmp/runs/)
- Add proper error handling and logging

## Architecture Notes

**Design Principles:**
1. **Minimal coupling** - Pipeline code copied, not refactored (architecture TBD)
2. **No database** - File-based state in `/tmp` for MVP
3. **No async workers** - Synchronous execution (Celery/Redis later if needed)
4. **Railway-ready** - Structured for Railway deployment (Story 5.2)

**Future Enhancements:**
- WebSocket support for real-time pipeline updates
- Async task queue (Celery) for background processing
- Database for persistent run history
- S3/Blob storage for pipeline outputs

## Railway Project

**Project Name:** `My-board-of-ideators`
**Frontend:** `innovation-web` (Vercel)
**Backend:** `backend/` (Railway) - this directory

---

**Last Updated:** 2025-10-21
**Story:** 5.1 - FastAPI Backend Directory Structure
**Author:** James (Dev Agent)
