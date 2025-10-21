"""FastAPI Application Entry Point

Minimal FastAPI backend for Innovation Intelligence System.
Handles pipeline execution requests from frontend.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Innovation Intelligence API",
    description="Backend API for CPG Innovation Intelligence Pipeline",
    version="1.0.0"
)

# CORS middleware - allow Vercel frontend to call Railway backend
# NOTE: Wildcard patterns like "https://*.vercel.app" are NOT supported by CORS spec
# Railway deployment will need environment variable ALLOWED_ORIGINS for dynamic origins
allowed_origins = [
    "http://localhost:3000",  # Local dev
    "https://innovation-web.vercel.app"  # Production frontend
]

# Add environment-based origins (for Vercel preview deployments)
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins:
    allowed_origins.extend([origin.strip() for origin in env_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Innovation Intelligence API",
        "version": "1.0.0",
        "docs": "/docs"
    }
