from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import paramiko
import io

from app.core.db import get_db
from app.models.integration import Integration
from app.schemas.integration import IntegrationCreate, IntegrationResponse, ConnectionTestRequest, ConnectionTestResponse

router = APIRouter()

# -----------------------------------------------------------------------------
# Helper: Test SFTP Connection
# -----------------------------------------------------------------------------
def test_sftp_connection(config: dict) -> bool:
    """Try to connect to an SFTP server using Paramiko."""
    host = config.get("host")
    port = int(config.get("port", 22))
    username = config.get("username")
    password = config.get("password")
    
    # Validation
    if not host or not username:
        raise ValueError("Host and Username are required.")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port=port, username=username, password=password, timeout=10)
        sftp = ssh.open_sftp()
        sftp.listdir(".") # Try to list directory to verify permissions
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        raise ValueError(f"Connection failed: {str(e)}")


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.post("/test", response_model=ConnectionTestResponse)
def test_connection(request: ConnectionTestRequest):
    """Test a connection config without saving it."""
    if request.type != "sftp":
        return ConnectionTestResponse(success=False, message="Only SFTP is supported currently.")

    try:
        test_sftp_connection(request.config)
        return ConnectionTestResponse(success=True, message="Successfully connected to SFTP server!")
    except ValueError as e:
        return ConnectionTestResponse(success=False, message=str(e))
    except Exception as e:
        return ConnectionTestResponse(success=False, message=f"Unexpected error: {str(e)}")


@router.post("/", response_model=IntegrationResponse)
def create_integration(
    integration: IntegrationCreate, 
    db: Session = Depends(get_db)
):
    """Save a new integration."""
    # TODO: Get real user_id from auth (Hardcoded for MVP)
    user_id = "test-user-id" 

    db_integration = Integration(
        user_id=user_id,
        name=integration.name,
        type=integration.type,
        config=integration.config # In a real app, encrypt this field!
    )
    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)
    return db_integration

@router.get("/", response_model=List[IntegrationResponse])
def list_integrations(db: Session = Depends(get_db)):
    """List all integrations for the user."""
    user_id = "test-user-id"
    return db.query(Integration).filter(Integration.user_id == user_id).all()
