import os
import sys

# Setup path to backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from db_config import set_db_env
    set_db_env()
    print("Loaded DB config from db_config.py (Public URL)")
except ImportError:
    pass

# Load env - reuse logic or rely on seed_config if we kept it, but best to load properly
from dotenv import load_dotenv
env_path = os.path.join(os.getcwd(), 'local.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

from app.services.layout_service import LayoutService
from app.generators.dynamic_generator import DynamicGenerator
from dataclasses import dataclass, field
from typing import Dict, Any, List

# Mock EDIDocument structure
@dataclass
class EDIDocument:
    transaction_type: str
    transaction_name: str
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    header: Dict[str, Any] = field(default_factory=dict)

def test_generation():
    print("Testing Dynamic Generation...")
    
    # Mock an 812 document
    doc = EDIDocument(
        transaction_type="812",
        transaction_name="Credit/Debit Adjustment",
        parsed_data={
            "credit_debit_number": "CD-999",
            "date": "2025-01-02",
            "amount": "500.00",
            "po_number": "PO-12345"
        },
        line_items=[
            {
                "line_number": "1",
                "assigned_id": "ITEM-001",
                "adjustment_reason": "Damaged",
                "quantity": "10",
                "unit_price": "50.00",
                "adjustment_amount": "500.00"
            }
        ],
        header={"credit_debit_number": "CD-999"}
    )
    
    # 1. Fetch Config
    print("Fetching 812 layout from DB...")
    config = LayoutService.get_active_layout("812")
    if not config:
        print("ERROR: No active layout found for 812!")
        return
        
    print(f"Layout found: {config.title_format}")
    
    # 2. Generate
    print("Generating HTML...")
    generator = DynamicGenerator(config)
    html_content = generator.render_content(doc)
    
    print("Generation Successful!")
    print(f"HTML Length: {len(html_content)} chars")
    print("Snippet:")
    print(html_content[:200] + "...")
    
    # Verify content
    if "CD-999" in html_content and "ITEM-001" in html_content:
        print("PASS: Data found in HTML")
    else:
        print("FAIL: Data missing from HTML")

if __name__ == "__main__":
    test_generation()
