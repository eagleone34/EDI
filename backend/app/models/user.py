"""
User model for ReadableEDI.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """User model for storing user accounts."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)  # UUID
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    conversion_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=True)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "conversion_count": self.conversion_count,
        }


class VerificationCode(Base):
    """Verification codes for passwordless email auth."""
    
    __tablename__ = "verification_codes"
    
    id = Column(String(36), primary_key=True)  # UUID
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(6), nullable=False)  # 6-digit code
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class Conversion(Base):
    """Conversion records for users."""
    
    __tablename__ = "conversions"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), nullable=True)  # Can be null for guest conversions
    filename = Column(String(255), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # e.g., "850"
    transaction_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Note: Actual file data stored separately or in S3
