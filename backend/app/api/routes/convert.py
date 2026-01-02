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
    
    # Validate transaction type
    allowed_types = ["850", "810", "812", "856", "855", "997"]
    if transaction_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transaction type '{transaction_type}'. Allowed: {', '.join(allowed_types)}"
        )
    
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode("utf-8", errors="ignore")
        
        # SMART DETECTION: Auto-detect the actual document type from the file
        detected_type = detect_transaction_type(content_str)
        type_mismatch = detected_type != transaction_type
        warning_message = None
        
        # If mismatch detected, use the CORRECT parser automatically
        actual_type = detected_type if detected_type in allowed_types else transaction_type
        
        if type_mismatch and detected_type in allowed_types:
            warning_message = (
                f"Document type mismatch detected! You selected {transaction_type}, "
                f"but the file contains {detected_type} documents. "
                f"We've automatically processed it as {detected_type} for accurate results."
            )
        elif type_mismatch:
            # Detected type not supported, fall back to user selection
            actual_type = transaction_type
            warning_message = (
                f"Could not auto-detect a supported document type. "
                f"Processing as {transaction_type} as selected."
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
        
        if "pdf" in format_list:
            pdf_gen = PDFGenerator()
            # Generate multi-page PDF with all documents
            pdf_bytes = pdf_gen.generate_all(documents)
            outputs["pdf"] = base64.b64encode(pdf_bytes).decode("utf-8")
        
        if "excel" in format_list:
            excel_gen = ExcelGenerator()
            # Generate multi-sheet Excel with all documents
            excel_bytes = excel_gen.generate_all(documents)
            outputs["excel"] = base64.b64encode(excel_bytes).decode("utf-8")
        
        if "html" in format_list:
            html_gen = HTMLGenerator()
            combined_html = generate_combined_html(documents, html_gen)
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


def generate_combined_html(documents: list, generator: HTMLGenerator) -> bytes:
    """Generate combined HTML for all documents with premium styling."""
    if len(documents) == 1:
        return generator.generate(documents[0])
    
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
        @media print { body { background: white; } .document-card { box-shadow: none; border: 1px solid #e2e8f0; } }
    """
    
    html_parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDI Conversion - {len(documents)} Purchase Orders</title>
    <style>{css}</style>
</head>
<body>
<div class="main-container">
    <div class="nav-card">
        <h1>📦 {len(documents)} Purchase Orders Found</h1>
        <div class="nav-links">
"""]
    
    # Navigation links
    for i, doc in enumerate(documents, 1):
        po_num = doc.header.get("po_number", f"Document {i}")
        html_parts.append(f'            <a href="#doc-{i}" class="nav-link">PO #{po_num}</a>')
    
    html_parts.append("""        </div>
    </div>
""")
    
    # Generate each document
    for i, doc in enumerate(documents, 1):
        po_num = doc.header.get("po_number", f"Document {i}")
        
        html_parts.append(f"""
    <div class="document-card" id="doc-{i}">
        <div class="doc-header">
            <h2>Purchase Order</h2>
            <span class="doc-badge">{i} of {len(documents)} — PO #{po_num}</span>
        </div>
        <div class="doc-content">
""")
        
        # Order Information section
        html_parts.append(build_order_info_section(doc))
        
        # Parties section
        html_parts.append(build_parties_section(doc))
        
        # Dates section
        html_parts.append(build_dates_section(doc))
        
        # Terms section (Payment Terms, FOB)
        html_parts.append(build_terms_section(doc))
        
        # Line Items table
        html_parts.append(build_line_items_section(doc))
        
        # Summary section
        html_parts.append(build_summary_section(doc))
        
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


def build_order_info_section(doc) -> str:
    """Build order information HTML section."""
    rows = []
    
    if doc.header.get("po_number"):
        rows.append(f'<div class="info-row"><span class="info-label">PO Number</span><span class="info-value"><strong>{doc.header["po_number"]}</strong></span></div>')
    if doc.header.get("po_date"):
        rows.append(f'<div class="info-row"><span class="info-label">PO Date</span><span class="info-value">{doc.header["po_date"]}</span></div>')
    if doc.header.get("purpose"):
        rows.append(f'<div class="info-row"><span class="info-label">Purpose</span><span class="info-value">{doc.header["purpose"]}</span></div>')
    if doc.header.get("order_type"):
        rows.append(f'<div class="info-row"><span class="info-label">Order Type</span><span class="info-value">{doc.header["order_type"]}</span></div>')
    if doc.sender_id:
        rows.append(f'<div class="info-row"><span class="info-label">Sender ID</span><span class="info-value">{doc.sender_id}</span></div>')
    if doc.receiver_id:
        rows.append(f'<div class="info-row"><span class="info-label">Receiver ID</span><span class="info-value">{doc.receiver_id}</span></div>')
    
    refs = doc.header.get("references", [])
    for ref in refs[:3]:
        if ref.get("value"):
            rows.append(f'<div class="info-row"><span class="info-label">{ref.get("type", "Ref")}</span><span class="info-value">{ref["value"]}</span></div>')
    
    if not rows:
        return ""
    
    return f"""
            <div class="section">
                <div class="section-title">Order Information</div>
                <div class="info-grid">{"".join(rows)}</div>
            </div>
"""


def build_parties_section(doc) -> str:
    """Build parties/addresses HTML section."""
    parties = doc.header.get("parties", [])
    if not parties:
        return ""
    
    cards = []
    for party in parties:
        name = party.get("name", "Unknown")
        party_type = party.get("type", party.get("type_code", ""))
        
        address_lines = []
        if party.get("address_line1"):
            address_lines.append(party["address_line1"])
        if party.get("address_line2"):
            address_lines.append(party["address_line2"])
        
        city_state_zip = []
        if party.get("city"):
            city_state_zip.append(party["city"])
        if party.get("state"):
            city_state_zip.append(party["state"])
        if party.get("zip"):
            city_state_zip.append(party["zip"])
        
        if city_state_zip:
            address_lines.append(", ".join(city_state_zip[:2]) + (" " + city_state_zip[2] if len(city_state_zip) > 2 else ""))
        
        address_html = "<br>".join(address_lines) if address_lines else ""
        
        cards.append(f'''
                    <div class="party-card">
                        <div class="party-type">{party_type}</div>
                        <div class="party-name">{name}</div>
                        <div class="party-address">{address_html}</div>
                    </div>''')
    
    return f"""
            <div class="section">
                <div class="section-title">Parties & Addresses</div>
                <div class="parties-grid">{"".join(cards)}</div>
            </div>
"""


def build_dates_section(doc) -> str:
    """Build dates HTML section."""
    dates = doc.header.get("dates", {})
    if not dates:
        return ""
    
    items = []
    for label, value in dates.items():
        items.append(f'''
                    <div class="date-item">
                        <div class="date-label">{label}</div>
                        <div class="date-value">{value}</div>
                    </div>''')
    
    return f"""
            <div class="section">
                <div class="section-title">Key Dates</div>
                <div class="dates-grid">{"".join(items)}</div>
            </div>
"""


def build_terms_section(doc) -> str:
    """Build terms HTML section (Payment Terms, FOB, etc.)."""
    items = []
    
    # Payment Terms
    payment_terms = doc.header.get("payment_terms")
    if payment_terms:
        items.append(f'''
                    <div class="term-item">
                        <div class="term-label">Payment Terms</div>
                        <div class="term-value">{payment_terms}</div>
                    </div>''')
    
    # FOB
    fob = doc.header.get("fob")
    if fob:
        fob_text = fob if isinstance(fob, str) else str(fob)
        fob_location = doc.header.get("fob_location")
        if fob_location:
            fob_text += f" — {fob_location}"
        items.append(f'''
                    <div class="term-item">
                        <div class="term-label">F.O.B.</div>
                        <div class="term-value">{fob_text}</div>
                    </div>''')
    
    if not items:
        return ""
    
    terms_css = '''
        <style>
            .terms-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
            .term-item { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; padding: 16px; border-radius: 0 12px 12px 0; }
            .term-label { font-size: 10px; font-weight: 700; color: #b45309; text-transform: uppercase; letter-spacing: 0.5px; }
            .term-value { font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 4px; }
        </style>
    '''
    
    return f"""
            {terms_css}
            <div class="section">
                <div class="section-title">Terms & Instructions</div>
                <div class="terms-grid">{"".join(items)}</div>
            </div>
"""


def build_line_items_section(doc) -> str:
    """Build line items table HTML section with detailed product info."""
    if not doc.line_items:
        return ""
    
    rows = []
    for idx, item in enumerate(doc.line_items):
        product_id = item.get("product_id", "—")
        description = item.get("description", "")
        
        unit_price = item.get("unit_price", "—")
        try:
            unit_price = f"${float(unit_price):,.2f}"
        except (ValueError, TypeError):
            pass
        
        total = item.get("total", "")
        if total:
            total = f"${float(total):,.2f}"
        else:
            total = "—"
        
        # Build product IDs details section
        product_ids = item.get("product_ids", {})
        details_html = ""
        if product_ids:
            detail_items = []
            for id_type, id_value in product_ids.items():
                if id_value:
                    detail_items.append(f'<span class="id-item"><span class="id-type">{id_type}:</span> {id_value}</span>')
            
            if detail_items:
                details_html = f'''
                        <div class="item-details">
                            <div class="details-toggle" onclick="this.parentElement.classList.toggle('expanded')">
                                ▶ Additional Details ({len(detail_items)} identifiers)
                            </div>
                            <div class="details-content">
                                {"".join(detail_items)}
                            </div>
                        </div>'''
        
        desc_html = f'<div class="item-desc">{description}</div>' if description else ""
        
        rows.append(f'''
                        <tr>
                            <td>{item.get("line_number", "—")}</td>
                            <td>
                                <strong>{product_id}</strong>
                                {desc_html}
                                {details_html}
                            </td>
                            <td>{item.get("quantity", "—")}</td>
                            <td>{item.get("unit", "—")}</td>
                            <td>{unit_price}</td>
                            <td>{total}</td>
                        </tr>''')
    
    # Add CSS for expandable details
    details_css = '''
        <style>
            .item-details { margin-top: 8px; font-size: 12px; }
            .details-toggle { cursor: pointer; color: #3b82f6; font-weight: 500; display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: #f0f9ff; border-radius: 4px; transition: all 0.2s; }
            .details-toggle:hover { background: #dbeafe; }
            .item-details.expanded .details-toggle { color: #1e40af; }
            .item-details.expanded .details-toggle::before { content: "▼"; margin-right: 4px; }
            .details-content { display: none; margin-top: 8px; padding: 12px; background: #f8fafc; border-radius: 8px; border-left: 3px solid #3b82f6; }
            .item-details.expanded .details-content { display: block; }
            .id-item { display: block; padding: 4px 0; border-bottom: 1px solid #e2e8f0; }
            .id-item:last-child { border-bottom: none; }
            .id-type { font-weight: 600; color: #64748b; min-width: 140px; display: inline-block; }
        </style>
    '''
    
    return f"""
            {details_css}
            <div class="section">
                <div class="section-title">Line Items ({len(doc.line_items)} items)</div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 60px;">Line</th>
                                <th>Product</th>
                                <th style="width: 80px;">Qty</th>
                                <th style="width: 60px;">Unit</th>
                                <th style="width: 100px;">Unit Price</th>
                                <th style="width: 100px;">Total</th>
                            </tr>
                        </thead>
                        <tbody>{"".join(rows)}</tbody>
                    </table>
                </div>
            </div>
"""


def build_summary_section(doc) -> str:
    """Build summary HTML section."""
    cards = []
    
    if doc.summary.get("total_line_items"):
        cards.append(f'''
                    <div class="summary-card">
                        <div class="summary-label">Line Items</div>
                        <div class="summary-value">{doc.summary["total_line_items"]}</div>
                    </div>''')
    
    total = doc.summary.get("total_amount") or doc.summary.get("calculated_total")
    if total:
        cards.append(f'''
                    <div class="summary-card total">
                        <div class="summary-label">Total Amount</div>
                        <div class="summary-value">${total:,.2f}</div>
                    </div>''')
    
    if not cards:
        return ""
    
    return f"""
            <div class="section">
                <div class="section-title">Summary</div>
                <div class="summary-grid">{"".join(cards)}</div>
            </div>
"""


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
    
    return "850"  # Default to Purchase Order


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
