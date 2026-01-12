"""
Email API routes for sending converted documents.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx

from app.services.email_service import email_service
from app.core.config import settings

router = APIRouter()


class SendEmailRequest(BaseModel):
    """Request model for sending email."""
    to_emails: List[str]
    filename: str
    transaction_type: str
    transaction_name: str
    pdf_base64: Optional[str] = None
    excel_base64: Optional[str] = None
    html_base64: Optional[str] = None
    trading_partner: Optional[str] = None
    document_id: Optional[str] = None
    formats: Optional[List[str]] = None


class EmailRouteCheckRequest(BaseModel):
    """Request for checking email routes and auto-sending."""
    user_id: str
    transaction_type: str
    filename: str
    transaction_name: str
    pdf_base64: Optional[str] = None
    excel_base64: Optional[str] = None
    html_base64: Optional[str] = None
    trading_partner: Optional[str] = None
    document_id: Optional[str] = None
    formats: Optional[List[str]] = None


@router.post("/send")
async def send_email(request: SendEmailRequest):
    """
    Send converted document to specified recipients.
    
    This endpoint is called from the frontend when user clicks "Email" on a document.
    """
    if not request.to_emails:
        raise HTTPException(status_code=400, detail="No recipients specified")
    
    # Validate emails
    for email in request.to_emails:
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail=f"Invalid email: {email}")
    
    # FETCH MISSING CONTENT (Fix for empty emails)
    # If base64 is missing but document_id exists, fetch from database/storage
    if request.document_id and settings.SUPABASE_URL:
        # Check what we need based on requested formats (default to PDF if no formats specified)
        needed_formats = request.formats or ["pdf"]
        
        need_pdf = "pdf" in needed_formats and not request.pdf_base64
        need_excel = "excel" in needed_formats and not request.excel_base64
        need_html = "html" in needed_formats and not request.html_base64
        
        if need_pdf or need_excel or need_html:
            try:
                async with httpx.AsyncClient() as client:
                    # 1. Get URLs from Database
                    doc_resp = await client.get(
                        f"{settings.SUPABASE_URL}/rest/v1/documents",
                        headers={
                            "apikey": settings.SUPABASE_SERVICE_KEY,
                            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                        },
                        params={"id": f"eq.{request.document_id}", "select": "pdf_url,excel_url,html_url"}
                    )
                    
                    if doc_resp.status_code == 200:
                        docs = doc_resp.json()
                        if docs and docs[0]:
                            doc = docs[0]
                            
                            # Helper to get base64 from URL (Data URI or HTTP)
                            async def get_content(url):
                                if not url: return None
                                if "base64," in url:
                                    return url.split("base64,")[1]
                                # If it's a storage URL (http), download it
                                if url.startswith("http"):
                                    try:
                                        print(f"Downloading attachment from: {url}")
                                        file_resp = await client.get(url)
                                        if file_resp.status_code == 200:
                                            return base64.b64encode(file_resp.content).decode("utf-8")
                                    except Exception as dl_err:
                                        print(f"Failed to download attachment: {dl_err}")
                                return None

                            if need_pdf:
                                request.pdf_base64 = await get_content(doc.get("pdf_url"))
                            
                            if need_excel:
                                request.excel_base64 = await get_content(doc.get("excel_url"))
                                
                            if need_html:
                                request.html_base64 = await get_content(doc.get("html_url"))
                                
            except Exception as e:
                print(f"Failed to fetch document content: {e}")

    result = email_service.send_converted_document(
        to_emails=request.to_emails,
        filename=request.filename,
        transaction_type=request.transaction_type,
        transaction_name=request.transaction_name,
        pdf_base64=request.pdf_base64,
        excel_base64=request.excel_base64,
        html_base64=request.html_base64,
        trading_partner=request.trading_partner,
        formats=request.formats,
    )
    
    if result.get("success"):
        return {
            "status": "success",
            "message": result.get("message"),
            "email_id": result.get("id"),
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("message", "Failed to send email"))


@router.post("/auto-send")
async def auto_send_based_on_routes(request: EmailRouteCheckRequest):
    """
    Check email routes for the user and transaction type, then auto-send if configured.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        return {"status": "skipped", "message": "Supabase not configured"}
    
    try:
        # Query Supabase for email routes
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/rest/v1/email_routes",
                headers={
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json",
                },
                params={
                    "user_id": f"eq.{request.user_id}",
                    "transaction_type": f"eq.{request.transaction_type}",
                    "is_active": "eq.true",
                    "select": "id,email_addresses,formats",  # Request formats too
                },
            )
            
            if response.status_code != 200:
                print(f"Failed to fetch email routes: {response.status_code}")
                return {"status": "error", "message": "Failed to fetch email routes"}
            
            routes = response.json()
            
            if not routes:
                return {"status": "no_routes", "message": "No email routes configured for this transaction type"}
            
            # Process each route individually (since formats might differ per route/recipient group)
            # For simplicity in V1, we'll merge recipients and take the UNION of formats
            
            all_recipients = []
            all_formats = set()
            
            for route in routes:
                addresses = route.get("email_addresses", [])
                route_formats = route.get("formats", ["pdf"]) # Default to PDF
                
                if isinstance(addresses, list):
                    all_recipients.extend(addresses)
                if isinstance(route_formats, list):
                    all_formats.update(route_formats)
            
            if not all_recipients:
                return {"status": "no_recipients", "message": "No email addresses in routes"}
            
            # Remove duplicates
            all_recipients = list(set(all_recipients))
            formats_list = list(all_formats) if all_formats else ["pdf"]
            
            # Send the email
            result = email_service.send_converted_document(
                to_emails=all_recipients,
                filename=request.filename,
                transaction_type=request.transaction_type,
                transaction_name=request.transaction_name,
                pdf_base64=request.pdf_base64,
                excel_base64=request.excel_base64,
                html_base64=request.html_base64,
                trading_partner=request.trading_partner,
                formats=formats_list,
            )
            
            if result.get("success"):
                # Log to Supabase
                try:
                    from datetime import datetime
                    logs = []
                    for route in routes:
                        for email in route.get("email_addresses", []):
                            logs.append({
                                "user_id": request.user_id,
                                "route_id": route.get("id"),
                                "document_id": request.document_id,
                                "recipient_email": email,
                                "status": "sent",
                                "sent_at": datetime.now().isoformat()
                            })
                    
                    if logs:
                        await client.post(
                            f"{settings.SUPABASE_URL}/rest/v1/email_logs",
                            headers={
                                "apikey": settings.SUPABASE_SERVICE_KEY,
                                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                                "Content-Type": "application/json",
                                "Prefer": "return=minimal"
                            },
                            json=logs
                        )
                except Exception as log_err:
                    print(f"Failed to log emails: {log_err}")

                return {
                    "status": "sent",
                    "message": f"Auto-sent to {len(all_recipients)} recipient(s)",
                    "recipients": all_recipients,
                    "email_id": result.get("id"),
                }
            else:
                return {
                    "status": "error",
                    "message": result.get("message", "Failed to send"),
                }
                
    except Exception as e:
        print(f"Error in auto-send: {e}")
        return {"status": "error", "message": f"{str(e)}"}


@router.get("/health")
async def email_health():
    """Check if email service is configured."""
    return {
        "resend_configured": bool(settings.RESEND_API_KEY),
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY),
        "from_email": settings.FROM_EMAIL,
    }
