"""
ReadableEDI - Backend API

FastAPI application for EDI file conversion to PDF, Excel, and HTML formats.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="ReadableEDI API",
    description="Transform EDI files into human-readable formats (PDF, Excel, HTML)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

from app.core.db import init_db

@app.on_event("startup")
def on_startup():
    init_db()

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
        "name": "ReadableEDI API",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


# Register routers
from app.api.routes import convert, auth, routing, transactions, integrations, email, layouts, users, inbound_email
app.include_router(convert.router, prefix="/api/v1/convert", tags=["convert"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(routing.router, prefix="/api/v1/routing", tags=["routing"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(email.router, prefix="/api/v1/email", tags=["email"])
app.include_router(layouts.router, prefix="/api/v1/layouts", tags=["layouts"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(inbound_email.router, prefix="/api/v1/inbound", tags=["inbound"])

