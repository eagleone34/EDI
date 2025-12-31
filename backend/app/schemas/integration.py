from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class IntegrationBase(BaseModel):
    name: str
    type: str = Field(..., description="Type of integration: sftp, gdrive, or onedrive")
    config: Dict[str, Any] = Field(..., description="Connection details (host, username, etc.)")

class IntegrationCreate(IntegrationBase):
    pass

class IntegrationUpdate(IntegrationBase):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class IntegrationResponse(IntegrationBase):
    id: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConnectionTestRequest(BaseModel):
    type: str
    config: Dict[str, Any]

class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
