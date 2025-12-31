"""
Email service using Resend for verification codes.
"""

import os
import random
import string
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


# Singleton instance
email_service = EmailService()
