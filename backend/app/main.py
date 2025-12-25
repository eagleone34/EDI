"""
EDI.email - Backend API

FastAPI application for EDI file conversion to PDF, Excel, and HTML formats.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="EDI.email API",
    description="Transform EDI files into human-readable formats (PDF, Excel, HTML)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "name": "EDI.email API",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


# TODO: Register routers
# from app.api.routes import convert, auth, routing
# app.include_router(convert.router, prefix="/api/v1/convert", tags=["convert"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(routing.router, prefix="/api/v1/routing", tags=["routing"])
