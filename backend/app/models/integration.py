from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import uuid

from app.models.base_class import Base

class Integration(Base):
    """
    Stores connection details for external systems (SFTP, Google Drive, etc.).
    """
    __tablename__ = "integrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True) # ID of the user who owns this
    name = Column(String(100), nullable=False) # e.g. "My SFTP Server"
    type = Column(String(20), nullable=False) # "sftp", "gdrive", "onedrive"
    
    # Encrypted JSON containing host, username, password, tokens
    config = Column(JSON, nullable=True) 
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    rules = relationship("RoutingRule", back_populates="integration", cascade="all, delete-orphan")


class RoutingRule(Base):
    """
    Rules for routing converted files to specific integrations.
    """
    __tablename__ = "routing_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    integration_id = Column(String(36), ForeignKey("integrations.id"), nullable=False)
    
    # Trigger condition
    transaction_type = Column(String(10), nullable=False) # e.g. "850", "ALL"
    
    # Destination path
    # e.g. "/inbound/orders/{date}"
    destination_path = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    integration = relationship("Integration", back_populates="rules")
