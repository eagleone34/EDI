"""
Email service using Resend for verification codes.
"""

import os
import random
import string
import base64
from typing import Optional
from datetime import datetime
from app.core.config import settings

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False


class EmailService:
    """Email service for sending verification codes via Resend."""
    
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.FROM_EMAIL
        self.from_name = "ReadableEDI"
        
        if self.api_key and RESEND_AVAILABLE:
            resend.api_key = self.api_key
    
    def generate_code(self) -> str:
        """Generate a 6-digit verification code."""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_verification_code(self, email: str, code: str) -> dict:
        """
        Send verification code to email.
        
        Returns:
            dict with success status and message
        """
        if not self.api_key:
            # Development mode - log code instead of sending
            print(f"[DEV MODE] Verification code for {email}: {code}")
            return {"success": True, "message": "Code sent (dev mode)", "dev_code": code}
        
        if not RESEND_AVAILABLE:
            return {"success": False, "message": "Email service not available"}
        
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f1f5f9;
            color: #334155;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .card {{
            background-color: #ffffff;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            text-align: center;
        }}
        .logo {{
            margin-bottom: 24px;
        }}
        .logo-text {{
            font-size: 24px;
            font-weight: 800;
            color: #1e40af;
            text-decoration: none;
            letter-spacing: -0.5px;
        }}
        h1 {{
            color: #1e293b;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 16px;
            margin-top: 0;
        }}
        p {{
            font-size: 16px;
            line-height: 1.6;
            color: #475569;
            margin-bottom: 24px;
        }}
        .code-container {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 1px solid #bfdbfe;
            border-radius: 12px;
            padding: 24px;
            margin: 32px 0;
            display: inline-block;
            min-width: 200px;
        }}
        .code {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 32px;
            font-weight: 700;
            color: #1e40af;
            letter-spacing: 8px;
        }}
        .footer {{
            margin-top: 32px;
            text-align: center;
            font-size: 13px;
            color: #94a3b8;
        }}
        .footer a {{
            color: #64748b;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="logo">
                <a href="https://readableedi.com" class="logo-text">ReadableEDI</a>
            </div>
            <h1>Verify your email</h1>
            <p>Use the following verification code to complete your login. This code will expire in 10 minutes.</p>
            
            <div class="code-container">
                <div class="code">{code}</div>
            </div>
            
            <p style="font-size: 14px; color: #64748b;">
                If you didn't request this code, you can safely ignore this email.
            </p>
        </div>
        <div class="footer">
            <p>
                &copy; {datetime.now().year} ReadableEDI. All rights reserved.<br>
                Secure EDI Conversion Platform
            </p>
        </div>
    </div>
</body>
</html>
"""
            
            response = resend.Emails.send({
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [email],
                "subject": f"Your ReadableEDI verification code: {code}",
                "html": html_content,
            })
            
            return {"success": True, "message": "Verification code sent", "id": response.get("id")}
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return {"success": False, "message": str(e)}
    
    def send_converted_document(
        self,
        to_emails: list,
        filename: str,
        transaction_type: str,
        transaction_name: str,
        pdf_base64: str = None,
        excel_base64: str = None,
        html_base64: str = None,
        trading_partner: str = None,
        formats: list = None,
    ) -> dict:
        """
        Send converted EDI document to recipients with attachments.
        
        Args:
            to_emails: List of recipient email addresses
            filename: Original filename
            transaction_type: EDI transaction type (e.g., "850")
            transaction_name: Human-readable name (e.g., "Purchase Order")
            pdf_base64: Base64-encoded PDF content
            excel_base64: Base64-encoded Excel content
            html_base64: Base64-encoded HTML content
            trading_partner: Trading partner name for reference
            formats: List of formats to include (pdf, excel, html)
        
        Returns:
            dict with success status and message
        """
        if not self.api_key:
            print(f"[DEV MODE] Would send document to: {to_emails}")
            return {"success": True, "message": "Email would be sent (dev mode)", "dev_code": "MOCK_EMAIL_ID"}
        
        if not RESEND_AVAILABLE:
            return {"success": False, "message": "Email service not available"}
        
        if not to_emails:
            return {"success": False, "message": "No recipients specified"}
        
        # Build subject
        subject = f"[{transaction_type}] {filename} - Converted Document"
        if trading_partner:
            subject = f"[{transaction_type}] {trading_partner} - {filename}"
        
        # Determine active formats
        has_pdf = bool(pdf_base64) and (not formats or "pdf" in formats)
        has_excel = bool(excel_base64) and (not formats or "excel" in formats)
        has_html = bool(html_base64) and (not formats or "html" in formats)
        
        # Build HTML body
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f1f5f9;">
    <div style="max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 24px; border-radius: 12px 12px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">ReadableEDI</h1>
            <p style="color: #93c5fd; margin: 8px 0 0;">Your converted document is ready</p>
        </div>
        
        <div style="padding: 24px; background: #ffffff; border: 1px solid #e2e8f0; border-top: none;">
            <h2 style="color: #1e293b; margin: 0 0 16px;">Document Details</h2>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; color: #64748b; width: 120px;">File:</td>
                    <td style="padding: 8px 0; color: #1e293b; font-weight: 500;">{filename}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748b;">Type:</td>
                    <td style="padding: 8px 0; color: #1e293b;">
                        <span style="background: #dbeafe; color: #1d4ed8; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">
                            EDI {transaction_type}
                        </span>
                        <span style="color: #64748b; margin-left: 8px;">{transaction_name}</span>
                    </td>
                </tr>
                {"<tr><td style='padding: 8px 0; color: #64748b;'>Customer:</td><td style='padding: 8px 0; color: #1e293b; font-weight: 500;'>" + trading_partner + "</td></tr>" if trading_partner else ""}
            </table>
            
            <p style="color: #64748b; margin: 24px 0 16px;">
                Your converted document is attached to this email. You can open it in your preferred application.
            </p>
            
            <div style="background: #f8fafc; border-radius: 8px; padding: 16px; margin: 16px 0;">
                <p style="margin: 0; color: #64748b; font-size: 14px;">
                    <strong>Attached files:</strong><br>
                    {"• PDF version<br>" if has_pdf else ""}
                    {"• Excel version<br>" if has_excel else ""}
                    {"• HTML version" if has_html else ""}
                </p>
            </div>
        </div>
        
        <div style="padding: 16px 24px; background: #f8fafc; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px; text-align: center;">
            <p style="color: #94a3b8; margin: 0; font-size: 12px;">
                Sent automatically by <a href="https://readableedi.com" style="color: #3b82f6;">ReadableEDI</a>
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        # Build attachments
        attachments = []
        base_filename = filename.rsplit(".", 1)[0] if "." in filename else filename
        
        if has_pdf:
            try:
                # Decode base64 to bytes list for Resend
                pdf_bytes = list(base64.b64decode(pdf_base64))
                attachments.append({
                    "filename": f"{base_filename}.pdf",
                    "content": pdf_bytes,
                })
            except Exception as e:
                print(f"Error decoding PDF attachment: {e}")
        
        if has_excel:
            try:
                # Decode base64 to bytes list for Resend
                excel_bytes = list(base64.b64decode(excel_base64))
                attachments.append({
                    "filename": f"{base_filename}.xlsx", 
                    "content": excel_bytes,
                })
            except Exception as e:
                print(f"Error decoding Excel attachment: {e}")
                
        if has_html:
            try:
                # Decode base64 to bytes list for Resend
                html_bytes = list(base64.b64decode(html_base64))
                attachments.append({
                    "filename": f"{base_filename}.html", 
                    "content": html_bytes,
                })
            except Exception as e:
                print(f"Error decoding HTML attachment: {e}")
        
        try:
            send_params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": to_emails if isinstance(to_emails, list) else [to_emails],
                "subject": subject,
                "html": html_content,
            }
            
            if attachments:
                send_params["attachments"] = attachments
            
            response = resend.Emails.send(send_params)
            
            return {
                "success": True, 
                "message": f"Email sent to {len(to_emails)} recipient(s)",
                "id": response.get("id"),
            }
            
        except Exception as e:
            print(f"Failed to send document email: {e}")
            return {"success": False, "message": str(e)}


# Singleton instance
email_service = EmailService()
