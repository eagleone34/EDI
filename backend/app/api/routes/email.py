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
    trading_partner: Optional[str] = None
    document_id: Optional[str] = None


class EmailRouteCheckRequest(BaseModel):
    """Request for checking email routes and auto-sending."""
    user_id: str
    transaction_type: str
    filename: str
    transaction_name: str
    pdf_base64: Optional[str] = None
    excel_base64: Optional[str] = None
    trading_partner: Optional[str] = None
    document_id: Optional[str] = None


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
    
    result = email_service.send_converted_document(
        to_emails=request.to_emails,
        filename=request.filename,
        transaction_type=request.transaction_type,
        transaction_name=request.transaction_name,
        pdf_base64=request.pdf_base64,
        excel_base64=request.excel_base64,
        trading_partner=request.trading_partner,
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
    
    This is called after conversion to check if the user has email routing set up
    for this transaction type and automatically send to configured recipients.
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
                    "select": "email_addresses",
                },
            )
            
            if response.status_code != 200:
                print(f"Failed to fetch email routes: {response.status_code}")
                return {"status": "error", "message": "Failed to fetch email routes"}
            
            routes = response.json()
            
            if not routes:
                return {"status": "no_routes", "message": "No email routes configured for this transaction type"}
            
            # Collect all email addresses from matching routes
            all_recipients = []
            for route in routes:
                addresses = route.get("email_addresses", [])
                if isinstance(addresses, list):
                    all_recipients.extend(addresses)
            
            if not all_recipients:
                return {"status": "no_recipients", "message": "No email addresses in routes"}
            
            # Remove duplicates
            all_recipients = list(set(all_recipients))
            
            # Send the email
            result = email_service.send_converted_document(
                to_emails=all_recipients,
                filename=request.filename,
                transaction_type=request.transaction_type,
                transaction_name=request.transaction_name,
                pdf_base64=request.pdf_base64,
                excel_base64=request.excel_base64,
                trading_partner=request.trading_partner,
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
        return {"status": "error", "message": f"{str(e)} (URL: {settings.SUPABASE_URL})"}


@router.get("/health")
async def email_health():
    """Check if email service is configured."""
    return {
        "resend_configured": bool(settings.RESEND_API_KEY),
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY),
        "from_email": settings.FROM_EMAIL,
    }
