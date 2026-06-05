from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.api import api_router
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get frontend directory path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(os.path.dirname(backend_dir), "frontend")

# API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static files - single mount point for all frontend files
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")