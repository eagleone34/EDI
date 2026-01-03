import os
import sys

# Setup path to backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load DB config
try:
    from db_config import set_db_env
    set_db_env()
    print("Loaded DB config")
except ImportError:
    pass

from app.api.routes.convert import generate_combined_html
from app.parsers.base import EDIDocument
from app.generators.html_generator import HTMLGenerator

def test_integration():
    print("Testing generate_combined_html integration...")
    
    # CASE 1: 812 Document (Should be Dynamic)
    print("\n--- Test Case 1: 812 Document (Dynamic) ---")
    doc_812 = EDIDocument(
        transaction_type="812",
        transaction_name="Credit/Debit Adjustment",
        header={"credit_debit_number": "CD-INTEG-1", "date": "2025-01-01", "po_number": "PO-TEST"}, # Combined header data
        line_items=[{"assigned_id": "DYN-ITEM", "adjustment_amount": "100.00"}]
    )
    
    # We pass a dummy generator because generate_combined_html requires it in signature
    # but might not use it if dynamic path is taken
    dummy_gen = HTMLGenerator()
    
    html_812 = generate_combined_html([doc_812], dummy_gen).decode('utf-8')
    
    # Check for Dynamic Artifacts
    if "nav-card" in html_812:
        print("PASS: Premium styling applied.")
    else:
        print("FAIL: Premium styling missing.")
        
    # Check for data
    if "CD-INTEG-1" in html_812:
        print("PASS: Data found.")
    else:
        print("FAIL: Data missing.")
        
    # Check if it hit the dynamic path (by checking if 'Item ID' column header exists which is unique to encoded layout)
    if "Item ID" in html_812:
        print("PASS: Dynamic Layout Used (Found 'Item ID' header).")
    else:
        print("FAIL: Dynamic Layout NOT Used (Missing 'Item ID').")


    # CASE 2: 997 Document (Should be Legacy)
    print("\n--- Test Case 2: 997 Document (Legacy Fallback) ---")
    doc_997 = EDIDocument(
        transaction_type="997",
        transaction_name="Functional Ack",
        header={"control_number": "997-001", "status": "Accepted"},
        line_items=[]
    )
    
    html_997 = generate_combined_html([doc_997], dummy_gen).decode('utf-8')
    
    if "nav-card" in html_997:
        print("PASS: Premium styling available for legacy too.")
        
    # Check for legacy specific artifacts (e.g. build_summary_section uses 'summary-card')
    if "summary-card" in html_997:
         print("PASS: Legacy Fallback Used (Found 'summary-card').")
    else:
         print("WARN: 'summary-card' not found, maybe 997 has no summary or different layout.")
         
    print("\nIntegration Test Complete.")

if __name__ == "__main__":
    test_integration()
