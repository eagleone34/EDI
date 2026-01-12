#!/usr/bin/env python3
"""Start script for Railway deployment."""
import os
import uvicorn
from migrations.migrate_formats import run_migration

if __name__ == "__main__":
    # Run database migrations
    run_migration()

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
