#!/usr/bin/env python3
"""
Test script to start FastAPI backend with MCP for testing.
Loads env vars from .env.local and starts server.
"""
import os
import sys
from pathlib import Path

# Load .env.local
env_file = Path(__file__).parent.parent / ".env.local"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"Loaded: {key}")

# Start uvicorn
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
