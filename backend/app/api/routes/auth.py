"""
Authentication endpoints for email OTP login.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.services.email_service import email_service


router = APIRouter()

# In-memory storage for demo (replace with database in production)
verification_codes = {}
users = {}
pending_conversions = {}


class SendCodeRequest(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str
    conversion_id: Optional[str] = None


class SendCodeResponse(BaseModel):
    success: bool
    message: str
    dev_code: Optional[str] = None  # Only in development mode


class VerifyCodeResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    token: Optional[str] = None


class SaveConversionRequest(BaseModel):
    conversion_id: str
    user_token: str


@router.post("/send-code", response_model=SendCodeResponse)
async def send_verification_code(request: SendCodeRequest):
    """Send a 6-digit verification code to email."""
    email = request.email.lower()
    
    # Generate code
    code = email_service.generate_code()
    
    # Store code with expiration (10 minutes)
    verification_codes[email] = {
        "code": code,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "created_at": datetime.utcnow(),
    }
    
    # Send email
    result = email_service.send_verification_code(email, code)
    
    if result["success"]:
        response = SendCodeResponse(
            success=True,
            message="Verification code sent to your email"
        )
        # Include dev_code if in development mode
        if "dev_code" in result:
            response.dev_code = result["dev_code"]
        return response
    else:
        raise HTTPException(status_code=500, detail=result["message"])


@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code(request: VerifyCodeRequest):
    """Verify the 6-digit code and create/login user."""
    email = request.email.lower()
    
    # Check if code exists
    if email not in verification_codes:
        raise HTTPException(status_code=400, detail="No verification code found for this email")
    
    stored = verification_codes[email]
    
    # Check if expired
    if datetime.utcnow() > stored["expires_at"]:
        del verification_codes[email]
        raise HTTPException(status_code=400, detail="Verification code has expired")
    
    # Check if code matches
    if request.code != stored["code"]:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Code is valid - clean up
    del verification_codes[email]
    
    # Get or create user
    if email not in users:
        user_id = str(uuid.uuid4())
        users[email] = {
            "id": user_id,
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
            "conversion_count": 0,
        }
    else:
        user_id = users[email]["id"]
    
    # Create simple token (in production use JWT)
    token = str(uuid.uuid4())
    
    return VerifyCodeResponse(
        success=True,
        message="Email verified successfully",
        user_id=user_id,
        token=token
    )


@router.post("/store-pending")
async def store_pending_conversion(conversion_id: str, data: dict):
    """Store conversion data temporarily until user verifies email."""
    pending_conversions[conversion_id] = {
        "data": data,
        "created_at": datetime.utcnow(),
    }
    return {"success": True, "conversion_id": conversion_id}


@router.get("/pending/{conversion_id}")
async def get_pending_conversion(conversion_id: str):
    """Get stored pending conversion."""
    if conversion_id not in pending_conversions:
        raise HTTPException(status_code=404, detail="Conversion not found")
    return pending_conversions[conversion_id]["data"]
