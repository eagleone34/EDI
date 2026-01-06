"""
EDI file conversion API endpoints.
Supports multiple transaction sets in a single interchange.
"""

import os
import time
import tempfile
import base64
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import JSONResponse, Response
from typing import List, Optional

from app.parsers import get_parser
from app.generators.pdf_generator import PDFGenerator
from app.generators.excel_generator import ExcelGenerator
from app.generators.html_generator import HTMLGenerator

router = APIRouter()


@router.post("/")
async def convert_edi_file(
    file: UploadFile = File(...),
    formats: str = Form(default="pdf"),
    transaction_type: str = Form(default="850"),
    user_id: Optional[str] = Form(default=None),
):
    """
    Convert an EDI file to the specified formats.
    Handles multiple transaction sets in a single interchange.
    
    Args:
        file: The EDI file to convert
        formats: Comma-separated list of output formats (pdf, excel, html)
        transaction_type: EDI transaction type (850, 810, 856, 855, 997)
    
    Returns:
        Conversion result with base64-encoded files or download links
    """
    start_time = time.time()
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    allowed_extensions = [".edi", ".txt", ".x12", ".dat"]
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Parse formats
    format_list = [f.strip().lower() for f in formats.split(",")]
    allowed_formats = ["pdf", "excel", "html"]
    for fmt in format_list:
        if fmt not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format '{fmt}'. Allowed: {', '.join(allowed_formats)}"
            )
    
    # Validate transaction type - ALL 17 SUPPORTED TYPES
    allowed_types = [
        "810", "812", "816", "820", "824", "830", "850", "852",
        "855", "856", "860", "861", "864", "870", "875", "880", "997"
    ]
    if transaction_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transaction type '{transaction_type}'. Allowed: {', '.join(allowed_types)}")
    
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode("utf-8", errors="ignore")
        
        # STRICT DETECTION: Auto-detect from file content
        detected_type = detect_transaction_type(content_str)
        warning_message = None
        
        # STRICT: Fail if we cannot detect the transaction type
        if not detected_type:
            raise HTTPException(
                status_code=422,
                detail="Could not detect EDI transaction type. Ensure the file contains a valid ST segment (e.g., ST*850*0001)."
            )
        
        # STRICT: Fail if detected type is not supported
        if detected_type not in allowed_types:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported EDI transaction type '{detected_type}'. Supported types: {', '.join(allowed_types)}"
            )
        
        # Use detected type (auto-correct if user selected wrong type)
        actual_type = detected_type
        if detected_type != transaction_type:
            warning_message = (
                f"Document type mismatch: You selected {transaction_type}, "
                f"but file contains {detected_type}. Processed as {detected_type}."
            )
        
        # Get parser for the ACTUAL transaction type (auto-corrected if needed)
        parser = get_parser(actual_type)
        
        if not parser:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported EDI transaction type: {actual_type}"
            )
        
        # Parse ALL transaction sets from the file
        documents = parser.parse_all(content_str)
        
        if not documents:
            raise HTTPException(
                status_code=422,
                detail="No transaction sets found in the file"
            )
        
        # Generate outputs - combine all documents into single files
        outputs = {}
        
        # Fetch dynamic layout config - REQUIRED (no legacy fallback)
        # Pass user_id so users get their own layout if they have one
        from app.services.layout_service import LayoutService
        from app.generators.dynamic_generator import DynamicGenerator
        layout_config = LayoutService.get_active_layout(actual_type, user_id)
        
        # STRICT: Layout MUST exist - no legacy fallback
        if not layout_config:
            raise HTTPException(
                status_code=500,
                detail=f"No approved layout found for transaction type '{actual_type}'. Please contact support to add this layout."
            )
        
        dynamic_gen = DynamicGenerator(layout_config)
        
        if "pdf" in format_list:
            pdf_bytes = dynamic_gen.generate_pdf(documents)
            outputs["pdf"] = base64.b64encode(pdf_bytes).decode("utf-8")
        
        if "excel" in format_list:
            excel_bytes = dynamic_gen.generate_excel(documents)
            outputs["excel"] = base64.b64encode(excel_bytes).decode("utf-8")
        
        if "html" in format_list:
            html_gen = HTMLGenerator()
            combined_html = generate_combined_html(documents, html_gen, user_id)
            outputs["html"] = base64.b64encode(combined_html).decode("utf-8")
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        # Return info about all documents found
        doc_summaries = []
        for doc in documents:
            po_number = doc.header.get("po_number", "Unknown")
            line_count = len(doc.line_items)
            doc_summaries.append({
                "poNumber": po_number,
                "lineItems": line_count,
            })
        
        # Extract trading partner from parties (prioritize: BY=Buyer, ST=Ship To, VN=Vendor)
        trading_partner = None
        if documents and hasattr(documents[0], 'header'):
            parties = documents[0].header.get("parties", [])
            for party in parties:
                if party.get("type_code") in ["BY", "ST", "VN", "SE"]:
                    if party.get("name"):
                        trading_partner = party.get("name")
                        break
            # Fallback: use first party with a name
            if not trading_partner and parties:
                for party in parties:
                    if party.get("name"):
                        trading_partner = party.get("name")
                        break
            # If still no trading partner, try sender/receiver IDs
            if not trading_partner and documents[0].sender_id:
                trading_partner = documents[0].sender_id
        
        # Build response with mismatch detection info
        response_content = {
            "id": f"conv_{int(time.time() * 1000)}",
            "status": "success",
            "transactionType": documents[0].transaction_type,
            "transactionName": documents[0].transaction_name,
            "transactionCount": len(documents),
            "documents": doc_summaries,
            "processingTime": processing_time,
            "filename": file.filename,
            "outputs": outputs,
            "downloads": {
                fmt: f"/api/v1/convert/download?data={outputs[fmt][:50]}...&format={fmt}"
                for fmt in outputs.keys()
            },
            # Smart detection info
            "detectedType": detected_type,
            "selectedType": transaction_type,
            "typeMismatch": type_mismatch,
            # Trading partner info
            "tradingPartner": trading_partner,
        }
        
        # Add warning if there was a mismatch
        if warning_message:
            response_content["warning"] = warning_message
        
        return JSONResponse(
            status_code=200,
            content=response_content
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}"
        )


def generate_combined_output(documents: list, generator) -> bytes:
    """Generate combined output for multiple documents."""
    # For PDF generator, just use first doc for now
    # (multi-page PDF needs proper implementation)
    if documents:
        return generator.generate(documents[0])
    return b""


from app.services.layout_service import LayoutService
from app.generators.dynamic_generator import DynamicGenerator

def generate_combined_html(documents: list, generator: HTMLGenerator, user_id: Optional[str] = None) -> bytes:
    """Generate combined HTML for all documents with premium styling."""
    if not documents:
        return b""
        
    # Always use this premium generator, even for single documents
    
    # Get dynamic names from first document
    trans_name = documents[0].transaction_name
    trans_type = documents[0].transaction_type
    
    # Try to fetch dynamic layout config (user-specific if user_id provided, else SYSTEM)
    layout_config = LayoutService.get_active_layout(trans_type, user_id)
    
    # Full premium CSS (same as single doc generator)
    css = """
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #1e293b; font-size: 14px; line-height: 1.5; padding: 20px; min-height: 100vh; }
        .main-container { max-width: 1200px; margin: 0 auto; }
        .nav-card { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 24px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .nav-card h1 { font-size: 24px; color: #1e40af; margin-bottom: 16px; display: flex; align-items: center; gap: 12px; }
        .nav-links { display: flex; gap: 12px; flex-wrap: wrap; }
        .nav-link { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 12px 20px; border-radius: 10px; text-decoration: none; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s; display: inline-block; }
        .nav-link:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4); }
        .document-card { background: white; border-radius: 16px; overflow: hidden; margin-bottom: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .doc-header { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 20px 28px; display: flex; justify-content: space-between; align-items: center; }
        .doc-header h2 { font-size: 20px; font-weight: 600; }
        .doc-badge { background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; font-size: 12px; }
        .doc-content { padding: 28px; }
        .section { margin-bottom: 28px; }
        .section-title { font-size: 16px; font-weight: 600; color: #1e40af; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; margin-bottom: 16px; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
        .info-row { display: flex; padding: 12px 16px; background: #f8fafc; border-radius: 8px; margin-bottom: 8px; }
        .info-label { font-weight: 600; color: #64748b; min-width: 140px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
        .info-value { color: #1e293b; }
        .party-card { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 12px; }
        .party-type { font-size: 11px; font-weight: 700; color: #1e40af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        .party-name { font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px; }
        .party-address { color: #64748b; line-height: 1.6; }
        .parties-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
        .dates-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
        .date-item { background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-left: 4px solid #3b82f6; padding: 16px; border-radius: 0 12px 12px 0; }
        .date-label { font-size: 10px; font-weight: 700; color: #1e40af; text-transform: uppercase; letter-spacing: 0.5px; }
        .date-value { font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 4px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; border-radius: 12px; overflow: hidden; }
        th { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 14px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
        th:last-child, td:last-child { text-align: right; }
        td { padding: 14px 12px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
        tr:hover td { background: #f8fafc; }
        .item-desc { font-size: 12px; color: #64748b; margin-top: 4px; }
        .product-ids { font-size: 11px; color: #94a3b8; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; }
        .summary-card { background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border: 1px solid #86efac; border-radius: 12px; padding: 20px; text-align: center; }
        .summary-card.total { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); border-color: transparent; }
        .summary-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #059669; }
        .summary-card.total .summary-label { color: rgba(255,255,255,0.8); }
        .summary-value { font-size: 28px; font-weight: 700; color: #047857; margin-top: 4px; }
        .summary-card.total .summary-value { color: white; }
        .footer { text-align: center; padding: 24px; color: rgba(255,255,255,0.8); font-size: 12px; }
        .footer a { color: white; text-decoration: none; font-weight: 600; }
        .fields-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 24px; }
        .label { font-size: 12px; color: #64748b; margin-bottom: 4px; }
        .value { font-size: 14px; font-weight: 500; color: #0f172a; }
        .style-bold { font-weight: 700; }
        .style-highlight { color: #2563eb; font-weight: 600; }
        @media print { body { background: white; } .document-card { box-shadow: none; border: 1px solid #e2e8f0; } }
    """
    
    html_parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDI Conversion - {len(documents)} {trans_name}s</title>
    <style>{css}</style>
</head>
<body>
<div class="main-container">
    <div class="nav-card">
        <h1>📦 {len(documents)} {trans_name}{'s' if len(documents) != 1 else ''} Found</h1>
        <div class="nav-links">
"""]
    
    # Navigation links
    for i, doc in enumerate(documents, 1):
        po_num = doc.header.get("po_number") or doc.header.get("credit_debit_number") or f"Document {i}"
        html_parts.append(f'            <a href="#doc-{i}" class="nav-link">#{po_num}</a>')
    
    html_parts.append("""        </div>
    </div>
""")
    
    # Generate each document
    for i, doc in enumerate(documents, 1):
        ref_num = doc.header.get("po_number") or doc.header.get("credit_debit_number") or f"Document {i}"
        
        html_parts.append(f"""
    <div class="document-card" id="doc-{i}">
        <div class="doc-header">
            <h2>{doc.transaction_name}</h2>
            <span class="doc-badge">{i} of {len(documents)} — {doc.transaction_type} #{ref_num}</span>
        </div>
        <div class="doc-content">
""")
        
        # Check if we have a dynamic layout for this type
        if layout_config:
            # Use data-driven generator
            dynamic_gen = DynamicGenerator(layout_config)
            html_parts.append(dynamic_gen.render_content(doc))
        else:
            # Fallback for missing configurations
            html_parts.append(f"""
                <div class="section">
                    <div class="section-title">Configuration Missing</div>
                    <div style="padding: 20px; text-align: center; color: #ef4444; background: #fee2e2; border-radius: 8px;">
                        <strong>Error:</strong> No active layout configuration found for transaction type <strong>{doc.transaction_type}</strong>.
                        <br>Please configure a layout in the Admin Dashboard.
                    </div>
                </div>
            """)
        
        html_parts.append("""        </div>
    </div>
""")
    
    # Footer
    html_parts.append("""
    <div class="footer">
        Generated by <a href="https://readableedi.com">ReadableEDI</a> — Transform EDI files into readable formats
    </div>
</div>
</body>
</html>""")
    
    return "\n".join(html_parts).encode('utf-8')


def detect_transaction_type(content: str) -> str:
    """Detect the EDI transaction type from content."""
    # Look for ST segment which contains transaction type
    lines = content.replace("\n", "~").replace("\r", "").split("~")
    
    for line in lines:
        line = line.strip()
        if line.startswith("ST"):
            # ST*850*0001 -> transaction type is 850
            parts = line.split("*")
            if len(parts) >= 2:
                return parts[1]
    
    # STRICT: Do NOT default to 850 - return None to force explicit error
    return None


@router.get("/{conversion_id}")
async def get_conversion_status(conversion_id: str):
    """Get the status of a conversion."""
    return {
        "id": conversion_id,
        "status": "completed",
        "message": "Conversion completed"
    }


@router.get("/download")
async def download_file(
    data: str = Query(...),
    format: str = Query(...)
):
    """Download a converted file."""
    try:
        # Decode base64 data
        file_bytes = base64.b64decode(data)
        
        content_types = {
            "pdf": "application/pdf",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "html": "text/html"
        }
        
        extensions = {
            "pdf": ".pdf",
            "excel": ".xlsx",
            "html": ".html"
        }
        
        return Response(
            content=file_bytes,
            media_type=content_types.get(format, "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename=converted{extensions.get(format, '')}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid download data: {str(e)}")
