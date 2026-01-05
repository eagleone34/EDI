"""
Inbound Email Processing - Webhook endpoint for Resend inbound emails.

Receives EDI files via email, processes them through the conversion pipeline,
saves them to the user's account, and applies routing rules.
"""

import hashlib
import base64
import uuid
import tempfile
import os
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
import hmac

from app.core.config import settings
from app.services.email_service import email_service
from app.parsers import get_parser
from app.generators.pdf_generator import PDFGenerator
from app.generators.excel_generator import ExcelGenerator
from app.generators.html_generator import HTMLGenerator
from app.db import get_db_connection, get_cursor

router = APIRouter()


# ============================================================================
# Pydantic Models for Resend Inbound Webhook
# ============================================================================

class EmailAttachment(BaseModel):
    """Email attachment from Resend."""
    filename: str
    content_type: str
    content: str  # Base64 encoded


class EmailAddress(BaseModel):
    """Email address object from Resend."""
    address: str
    name: Optional[str] = None


class InboundEmailWebhook(BaseModel):
    """Resend inbound email webhook payload."""
    from_: EmailAddress = None
    to: List[EmailAddress] = []
    subject: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None
    attachments: List[EmailAttachment] = []
    
    class Config:
        populate_by_name = True
        # Handle 'from' as a field name
        fields = {'from_': 'from'}


class InboundEmailError(BaseModel):
    """Record of a failed inbound email processing."""
    id: str
    user_id: str
    sender_email: str
    filename: Optional[str]
    error_message: str
    created_at: datetime


# ============================================================================
# Helper Functions
# ============================================================================

def generate_inbound_email(user_id: str) -> str:
    """
    Generate a unique inbound email address for a user.
    Format: user_{short_hash}@readableedi.com
    """
    short_id = hashlib.sha256(user_id.encode()).hexdigest()[:8]
    domain = getattr(settings, 'INBOUND_EMAIL_DOMAIN', 'readableedi.com')
    return f"user_{short_id}@{domain}"


def lookup_user_by_inbound_email(inbound_email: str) -> Optional[dict]:
    """Look up user by their inbound email address."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        cur.execute(
            "SELECT id, email, name, inbound_email FROM users WHERE inbound_email = %s",
            (inbound_email.lower(),)
        )
        result = cur.fetchone()
        
        if result:
            return dict(result)
        return None
        
    except Exception as e:
        print(f"Error looking up user by inbound email: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_user_email_routes(user_id: str, transaction_type: str) -> List[str]:
    """Get email routing rules for a user and transaction type."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT email_addresses FROM email_routes 
            WHERE user_id = %s AND transaction_type = %s AND is_active = true
        """, (user_id, transaction_type))
        
        result = cur.fetchone()
        if result and result.get('email_addresses'):
            return result['email_addresses']
        return []
        
    except Exception as e:
        print(f"Error fetching email routes: {e}")
        return []
    finally:
        if conn:
            conn.close()


def save_inbound_error(user_id: str, sender_email: str, filename: Optional[str], error_message: str):
    """Save an inbound email processing error to the database."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        cur.execute("""
            INSERT INTO inbound_email_errors (id, user_id, sender_email, filename, error_message, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (str(uuid.uuid4()), user_id, sender_email, filename, error_message))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving inbound error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def save_document_to_supabase(
    user_id: str,
    filename: str,
    transaction_type: str,
    transaction_name: str,
    trading_partner: Optional[str],
    pdf_base64: Optional[str],
    excel_base64: Optional[str],
    html_content: Optional[str],
    transaction_count: int = 1,
    source: str = "email"
) -> Optional[str]:
    """Save converted document to Supabase documents table."""
    try:
        import os
        from supabase import create_client
        
        supabase_url = os.environ.get("SUPABASE_URL") or settings.SUPABASE_URL
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY") or settings.SUPABASE_SERVICE_KEY
        
        if not supabase_url or not supabase_key:
            print("Supabase credentials not configured")
            return None
        
        client = create_client(supabase_url, supabase_key)
        
        doc_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "filename": filename,
            "transaction_type": transaction_type,
            "transaction_name": transaction_name,
            "trading_partner": trading_partner,
            "transaction_count": transaction_count,
            "source": source,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Store base64 data URLs
        if pdf_base64:
            doc_data["pdf_url"] = f"data:application/pdf;base64,{pdf_base64}"
        if excel_base64:
            doc_data["excel_url"] = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64}"
        if html_content:
            html_b64 = base64.b64encode(html_content.encode()).decode()
            doc_data["html_url"] = f"data:text/html;base64,{html_b64}"
        
        result = client.table("documents").insert(doc_data).execute()
        
        if result.data:
            return result.data[0].get("id")
        return None
        
    except Exception as e:
        print(f"Error saving document to Supabase: {e}")
        return None


def send_error_email(to_email: str, filename: str, error_message: str):
    """Send error notification email to sender."""
    try:
        import resend
        
        if not settings.RESEND_API_KEY:
            print(f"[DEV MODE] Would send error email to {to_email}")
            return
        
        resend.api_key = settings.RESEND_API_KEY
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f1f5f9;">
    <div style="max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #ef4444, #dc2626); padding: 24px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">ReadableEDI</h1>
            <p style="color: #fecaca; margin: 8px 0 0;">Error processing your EDI file</p>
        </div>
        
        <div style="padding: 24px; background: #ffffff; border: 1px solid #e2e8f0; border-top: none;">
            <h2 style="color: #1e293b; margin: 0 0 16px;">Processing Failed</h2>
            
            <p style="color: #64748b; margin-bottom: 16px;">
                We encountered an error while processing your EDI file.
            </p>
            
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                <p style="margin: 0 0 8px; color: #991b1b; font-weight: 600;">File: {filename}</p>
                <p style="margin: 0; color: #b91c1c; font-size: 14px;">{error_message}</p>
            </div>
            
            <p style="color: #64748b; margin: 0;">
                Please verify your file is a valid EDI document and try again. 
                You can also upload directly at <a href="https://readableedi.com" style="color: #3b82f6;">readableedi.com</a>
            </p>
        </div>
        
        <div style="padding: 16px 24px; background: #f8fafc; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px; text-align: center;">
            <p style="color: #94a3b8; margin: 0; font-size: 12px;">
                Sent by <a href="https://readableedi.com" style="color: #3b82f6;">ReadableEDI</a>
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        resend.Emails.send({
            "from": f"ReadableEDI <{settings.FROM_EMAIL}>",
            "to": [to_email],
            "subject": f"Error processing EDI file: {filename}",
            "html": html_content,
        })
        
    except Exception as e:
        print(f"Failed to send error email: {e}")


# ============================================================================
# Webhook Endpoints
# ============================================================================

TRANSACTION_TYPE_NAMES = {
    "850": "Purchase Order",
    "810": "Invoice",
    "812": "Credit/Debit Adjustment",
    "816": "Organizational Relationships",
    "820": "Payment Order/Remittance",
    "824": "Application Advice",
    "830": "Planning Schedule",
    "852": "Product Activity Data",
    "855": "PO Acknowledgment",
    "856": "Advance Ship Notice",
    "860": "PO Change Request",
    "861": "Receiving Advice",
    "864": "Text Message",
    "870": "Order Status Report",
    "875": "Grocery Products Invoice",
    "880": "Grocery Products PO",
    "997": "Functional Acknowledgment",
}


@router.post("/webhook")
async def process_inbound_email(request: Request):
    """
    Process inbound email from Resend webhook.
    
    Flow:
    1. Parse email and extract attachments
    2. Look up user by inbound email address
    3. Process each EDI attachment through conversion pipeline
    4. Save documents to user's account
    5. Apply routing rules and send to configured recipients
    6. On error: notify sender and log in dashboard
    """
    try:
        # Parse webhook payload
        body = await request.json()
        
        print(f"Received webhook: {body.get('type', 'unknown')}")
        
        # Resend wraps email data in a 'data' object with event 'type' at root
        if 'data' in body and body.get('type') == 'email.received':
            email_data = body['data']
        else:
            # Fallback for direct payload
            email_data = body
        
        # Handle the 'from' field mapping
        if 'from' in email_data:
            from_value = email_data.pop('from')
            # Handle string format "email" or dict format {"address": "email"}
            if isinstance(from_value, str):
                email_data['from_'] = EmailAddress(address=from_value)
            elif isinstance(from_value, dict):
                email_data['from_'] = EmailAddress(**from_value)
            else:
                email_data['from_'] = None
        
        # Handle 'to' field - could be list of strings or list of dicts
        if 'to' in email_data:
            to_list = email_data['to']
            converted_to = []
            for t in to_list:
                if isinstance(t, str):
                    converted_to.append(EmailAddress(address=t))
                elif isinstance(t, dict):
                    converted_to.append(EmailAddress(**t))
            email_data['to'] = converted_to
        
        payload = InboundEmailWebhook(**email_data)
        
        # Get recipient email (the user's inbound address)
        if not payload.to:
            raise HTTPException(status_code=400, detail="No recipient address")
        
        inbound_email = payload.to[0].address.lower()
        sender_email = payload.from_.address if payload.from_ else "unknown@unknown.com"
        
        print(f"Processing email to: {inbound_email} from: {sender_email}")
        
        # Look up user
        user = lookup_user_by_inbound_email(inbound_email)
        if not user:
            print(f"No user found for inbound email: {inbound_email}")
            # Don't reveal user existence - just accept and ignore
            return {"status": "accepted", "message": "Email processed"}
        
        user_id = user["id"]
        
        # Process each attachment
        processed_count = 0
        errors = []
        
        for attachment in payload.attachments:
            filename = attachment.filename
            
            try:
                # Decode attachment content
                content_bytes = base64.b64decode(attachment.content)
                content = content_bytes.decode('utf-8', errors='ignore')
                
                # Detect transaction type
                from app.api.routes.convert import detect_transaction_type
                transaction_type = detect_transaction_type(content)
                
                if not transaction_type or transaction_type == "UNKNOWN":
                    raise ValueError(f"Could not detect EDI transaction type in {filename}")
                
                # Get parser
                parser = get_parser(transaction_type)
                if not parser:
                    raise ValueError(f"No parser available for transaction type: {transaction_type}")
                
                # Parse EDI content
                documents = parser.parse(content)
                if not documents:
                    raise ValueError(f"No valid transactions found in {filename}")
                
                # Generate outputs
                pdf_generator = PDFGenerator()
                excel_generator = ExcelGenerator()
                html_generator = HTMLGenerator()
                
                # Generate PDF
                pdf_bytes = pdf_generator.generate(documents[0] if len(documents) == 1 else documents)
                pdf_base64 = base64.b64encode(pdf_bytes).decode() if pdf_bytes else None
                
                # Generate Excel
                excel_bytes = excel_generator.generate(documents[0] if len(documents) == 1 else documents)
                excel_base64 = base64.b64encode(excel_bytes).decode() if excel_bytes else None
                
                # Generate HTML
                html_content = html_generator.generate(documents[0] if len(documents) == 1 else documents)
                
                # Extract trading partner from first document
                trading_partner = None
                if documents:
                    first_doc = documents[0] if isinstance(documents, list) else documents
                    if hasattr(first_doc, 'get'):
                        trading_partner = first_doc.get("trading_partner") or first_doc.get("sender_name")
                
                transaction_name = TRANSACTION_TYPE_NAMES.get(transaction_type, f"EDI {transaction_type}")
                
                # Save document to user's account
                doc_id = save_document_to_supabase(
                    user_id=user_id,
                    filename=filename,
                    transaction_type=transaction_type,
                    transaction_name=transaction_name,
                    trading_partner=trading_partner,
                    pdf_base64=pdf_base64,
                    excel_base64=excel_base64,
                    html_content=html_content,
                    transaction_count=len(documents) if isinstance(documents, list) else 1,
                    source="email"
                )
                
                # Apply routing rules
                route_emails = get_user_email_routes(user_id, transaction_type)
                if route_emails:
                    email_service.send_converted_document(
                        to_emails=route_emails,
                        filename=filename,
                        transaction_type=transaction_type,
                        transaction_name=transaction_name,
                        pdf_base64=pdf_base64,
                        excel_base64=excel_base64,
                        trading_partner=trading_partner,
                    )
                
                processed_count += 1
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error processing attachment {filename}: {error_msg}")
                errors.append({"filename": filename, "error": error_msg})
                
                # Save error to database for dashboard visibility
                save_inbound_error(user_id, sender_email, filename, error_msg)
                
                # Send error email to sender
                send_error_email(sender_email, filename, error_msg)
        
        # If no attachments, check if EDI content is in email body
        if not payload.attachments and payload.text:
            try:
                content = payload.text
                from app.api.routes.convert import detect_transaction_type
                transaction_type = detect_transaction_type(content)
                
                if transaction_type and transaction_type != "UNKNOWN":
                    # Process body as EDI
                    parser = get_parser(transaction_type)
                    if parser:
                        documents = parser.parse(content)
                        if documents:
                            # Generate outputs
                            pdf_generator = PDFGenerator()
                            pdf_bytes = pdf_generator.generate(documents[0] if len(documents) == 1 else documents)
                            pdf_base64 = base64.b64encode(pdf_bytes).decode() if pdf_bytes else None
                            
                            excel_generator = ExcelGenerator()
                            excel_bytes = excel_generator.generate(documents[0] if len(documents) == 1 else documents)
                            excel_base64 = base64.b64encode(excel_bytes).decode() if excel_bytes else None
                            
                            html_generator = HTMLGenerator()
                            html_content = html_generator.generate(documents[0] if len(documents) == 1 else documents)
                            
                            transaction_name = TRANSACTION_TYPE_NAMES.get(transaction_type, f"EDI {transaction_type}")
                            
                            doc_id = save_document_to_supabase(
                                user_id=user_id,
                                filename="email_body.edi",
                                transaction_type=transaction_type,
                                transaction_name=transaction_name,
                                trading_partner=None,
                                pdf_base64=pdf_base64,
                                excel_base64=excel_base64,
                                html_content=html_content,
                                source="email"
                            )
                            
                            # Apply routing rules
                            route_emails = get_user_email_routes(user_id, transaction_type)
                            if route_emails:
                                email_service.send_converted_document(
                                    to_emails=route_emails,
                                    filename="email_body.edi",
                                    transaction_type=transaction_type,
                                    transaction_name=transaction_name,
                                    pdf_base64=pdf_base64,
                                    excel_base64=excel_base64,
                                )
                            
                            processed_count += 1
                            
            except Exception as e:
                print(f"Error processing email body as EDI: {e}")
        
        return {
            "status": "success",
            "processed": processed_count,
            "errors": errors if errors else None,
        }
        
    except Exception as e:
        print(f"Inbound email webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors")
async def get_inbound_errors(user_id: str, limit: int = 20):
    """Get inbound email processing errors for a user."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT id, sender_email, filename, error_message, created_at
            FROM inbound_email_errors
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        results = cur.fetchall()
        return {"errors": [dict(r) for r in results]}
        
    except Exception as e:
        print(f"Error fetching inbound errors: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
