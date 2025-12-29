"""
Email service using Resend for verification codes.
"""

import os
import random
import string
from typing import Optional

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False


class EmailService:
    """Email service for sending verification codes via Resend."""
    
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY", "")
        self.from_email = os.getenv("FROM_EMAIL", "hello@readableedi.com")
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
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background-color: #f8fafc;">
    <div style="max-width: 480px; margin: 40px auto; padding: 40px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <h1 style="color: #1e40af; margin-bottom: 24px; font-size: 24px; text-align: center;">
            ReadableEDI
        </h1>
        <p style="color: #1e293b; font-size: 16px; margin-bottom: 8px;">
            Your verification code is:
        </p>
        <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
            <span style="font-size: 36px; font-weight: 700; letter-spacing: 8px; color: white;">
                {code}
            </span>
        </div>
        <p style="color: #64748b; font-size: 14px; margin-top: 24px;">
            This code expires in 10 minutes. If you didn't request this, you can safely ignore this email.
        </p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 32px 0;">
        <p style="color: #94a3b8; font-size: 12px; text-align: center;">
            ReadableEDI — Transform EDI files into readable formats<br>
            <a href="https://readableedi.com" style="color: #3b82f6;">readableedi.com</a>
        </p>
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
