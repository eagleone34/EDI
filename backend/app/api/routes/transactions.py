from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

class Transaction(BaseModel):
    id: str
    filename: str
    po_number: str
    transaction_type: str
    status: str
    created_at: datetime
    formatted_date: str

@router.get("/", response_model=List[Transaction])
async def get_transactions(
    # In a real app, we would get the current user from the token
    # current_user: User = Depends(get_current_user)
):
    """
    Get list of USER transactions.
    Mocked for MVP to show UI capabilities instantly.
    """
    
    # Mock data
    now = datetime.now()
    
    transactions = [
        Transaction(
            id="txn_1",
            filename="ORDER_850_GOOGLE.edi",
            po_number="PO-459821",
            transaction_type="850",
            status="Completed",
            created_at=now - timedelta(minutes=5),
            formatted_date=(now - timedelta(minutes=5)).strftime("%b %d, %Y")
        ),
        Transaction(
            id="txn_2",
            filename="INVOICE_810_WALMART.edi",
            po_number="INV-998877",
            transaction_type="810",
            status="Completed",
            created_at=now - timedelta(days=1),
            formatted_date=(now - timedelta(days=1)).strftime("%b %d, %Y")
        ),
        Transaction(
            id="txn_3",
            filename="SHIP_856_AMAZON.edi",
            po_number="ASN-112233",
            transaction_type="856",
            status="Completed",
            created_at=now - timedelta(days=2),
            formatted_date=(now - timedelta(days=2)).strftime("%b %d, %Y")
        ),
        Transaction(
            id="txn_4",
            filename="ORDER_850_TARGET.edi",
            po_number="PO-776655",
            transaction_type="850",
            status="Processing",
            created_at=now - timedelta(minutes=1),
            formatted_date=(now - timedelta(minutes=1)).strftime("%b %d, %Y")
        ),
        Transaction(
            id="txn_5",
            filename="ACK_997_General.edi",
            po_number="ACK-0001",
            transaction_type="997",
            status="Completed",
            created_at=now - timedelta(days=5),
            formatted_date=(now - timedelta(days=5)).strftime("%b %d, %Y")
        ),
    ]
    
    return transactions
