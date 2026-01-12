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

def seed_layouts():
    """Seed/update layout configurations on startup."""
    try:
        from app.db import get_db_connection, get_cursor
        import json
        
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # 812 Layout with correct field names matching parser output
        layout_812 = {
            "title_format": "Credit/Debit Adjustment #{credit_debit_number}",
            "theme_color": "#dc2626",
            "sections": [
                {
                    "id": "memo_info",
                    "title": "Memo Information",
                    "type": "fields",
                    "visible": True,
                    "fields": [
                        {"key": "credit_debit_number", "label": "Memo #", "type": "text", "visible": True, "style": "bold"},
                        {"key": "adjustment_date", "label": "Date", "type": "date", "visible": True},
                        {"key": "credit_debit_flag_desc", "label": "Type", "type": "text", "visible": True},
                        {"key": "amount", "label": "Amount", "type": "currency", "visible": True, "style": "bold"},
                        {"key": "invoice_number", "label": "Original Invoice", "type": "text", "visible": True},
                        {"key": "currency", "label": "Currency", "type": "text", "visible": True},
                    ],
                    "columns": []
                },
                {
                    "id": "parties",
                    "title": "Entities & Parties",
                    "type": "table",
                    "visible": True,
                    "data_source_key": "parties",
                    "fields": [],
                    "columns": [
                        {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                        {"key": "name", "label": "Name", "type": "text", "visible": True},
                        {"key": "id", "label": "ID", "type": "text", "visible": True},
                    ]
                },
                {
                    "id": "line_items",
                    "title": "Line Items",
                    "type": "table",
                    "visible": True,
                    "data_source_key": "line_items",
                    "fields": [],
                    "columns": [
                        {"key": "line_number", "label": "#", "type": "text", "visible": True},
                        {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                        {"key": "adjustment_reason", "label": "Reason", "type": "text", "visible": True},
                        {"key": "quantity", "label": "Qty", "type": "number", "visible": True},
                        {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                        {"key": "adjustment_amount", "label": "Amount", "type": "currency", "visible": True},
                        {"key": "credit_debit_type", "label": "Type", "type": "text", "visible": True},
                    ]
                },
                {
                    "id": "summary",
                    "title": "Summary",
                    "type": "fields",
                    "visible": True,
                    "fields": [
                        {"key": "total_line_items", "label": "Total Line Items", "type": "number", "visible": True},
                        {"key": "total_amount", "label": "Total Amount", "type": "currency", "visible": True, "style": "bold"},
                    ],
                    "columns": []
                }
            ]
        }
        
        # Update existing 812 SYSTEM layout
        cur.execute("""
            UPDATE layout_versions 
            SET config_json = %s, updated_at = NOW()
            WHERE transaction_type_code = '812' 
              AND user_id IS NULL 
              AND status = 'PRODUCTION'
        """, (json.dumps(layout_812),))
        
        if cur.rowcount == 0:
            # Insert if not exists
            cur.execute("""
                INSERT INTO layout_versions 
                (transaction_type_code, version_number, status, config_json, is_active, created_by)
                VALUES ('812', 1, 'PRODUCTION', %s, true, 'system')
            """, (json.dumps(layout_812),))
        
        conn.commit()
        conn.close()
        print("✓ Layout 812 seeded successfully")
    except Exception as e:
        print(f"Layout seeding error (non-fatal): {e}")

@app.on_event("startup")
def on_startup():
    init_db()
    seed_layouts()

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
from app.api.routes import convert, auth, routing, transactions, integrations, email, layouts, users, inbound_email, admin
app.include_router(convert.router, prefix="/api/v1/convert", tags=["convert"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(routing.router, prefix="/api/v1/routing", tags=["routing"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(email.router, prefix="/api/v1/email", tags=["email"])
app.include_router(layouts.router, prefix="/api/v1/layouts", tags=["layouts"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(inbound_email.router, prefix="/api/v1/inbound", tags=["inbound"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

