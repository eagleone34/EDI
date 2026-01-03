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
    print("WARN: Could not load db_config.py")

from app.api.routes.convert import generate_combined_html
from app.parsers.base import EDIDocument
from app.generators.html_generator import HTMLGenerator

def create_mock_doc(type_code, name, header_data, line_items=None):
    return EDIDocument(
        transaction_type=type_code,
        transaction_name=name,
        header=header_data,
        line_items=line_items or []
    )

def test_all_types():
    print("Starting Comprehensive Test Suite...")
    
    # Define Test Cases
    test_cases = [
        {
            "type": "812", "name": "Credit/Debit Adjustment",
            "header": {"credit_debit_number": "CD-812-TEST", "date": "2025-01-01"},
            "lines": [{"assigned_id": "ITEM-812", "adjustment_amount": "50.00"}],
            "expect_dynamic": True
        },
        {
            "type": "850", "name": "Purchase Order",
            "header": {"po_number": "PO-850-TEST", "po_date": "2025-02-01"},
            "lines": [{"product_id": "SKU-850", "quantity": "100", "unit_price": "10.00"}],
            "expect_dynamic": True
        },
        {
            "type": "810", "name": "Invoice",
            "header": {"po_number": "INV-810-TEST", "date": "2025-03-01"},
            "lines": [{"product_id": "SKU-810", "total": "200.00"}],
            "expect_dynamic": True
        },
        {
            "type": "855", "name": "PO Acknowledgment",
            "header": {"po_number": "PO-855-TEST", "ack_date": "2025-02-02"},
            "lines": [{"product_id": "SKU-855", "total": "100.00"}],
            "expect_dynamic": True
        },
        {
            "type": "856", "name": "Ship Notice",
            "header": {"po_number": "SH-856-TEST", "date": "2025-02-05"},
            "lines": [{"product_id": "SKU-856", "quantity": "50"}],
            "expect_dynamic": True
        },
        {
            "type": "997", "name": "Functional Acknowledgment",
            "header": {"po_number": "997-TEST", "status": "A"},
            "lines": [],
            "expect_dynamic": True
        },
        # --- NEW TYPES ---
        {"type": "816", "name": "Org Relationships", "header": {"ref_number": "ORG-816"}, "lines": [], "expect_dynamic": True},
        {"type": "820", "name": "Payment Remittance", "header": {"check_number": "CHK-820"}, "lines": [], "expect_dynamic": True},
        {"type": "824", "name": "App Advice", "header": {"control_number": "APP-824"}, "lines": [], "expect_dynamic": True},
        {"type": "830", "name": "Planning Schedule", "header": {"schedule_number": "SCH-830"}, "lines": [], "expect_dynamic": True},
        {"type": "852", "name": "Product Activity", "header": {"report_start": "2025-01-01"}, "lines": [], "expect_dynamic": True},
        {"type": "860", "name": "PO Change", "header": {"po_number": "PO-860"}, "lines": [], "expect_dynamic": True},
        {"type": "861", "name": "Receiving Advice", "header": {"receipt_number": "RCV-861"}, "lines": [], "expect_dynamic": True},
        {"type": "864", "name": "Text Message", "header": {"subject": "Urgent Info"}, "lines": [], "expect_dynamic": True},
        {"type": "870", "name": "Order Status", "header": {"report_id": "RPT-870"}, "lines": [], "expect_dynamic": True},
        {"type": "875", "name": "Grocery PO", "header": {"po_number": "GRO-875"}, "lines": [], "expect_dynamic": True},
        {"type": "880", "name": "Grocery Inv", "header": {"invoice_number": "INV-880"}, "lines": [], "expect_dynamic": True},

    ]
    
    dummy_gen = HTMLGenerator()
    results = []
    
    print(f"\nTesting {len(test_cases)} configurations...\n")
    
    for case in test_cases:
        t_type = case["type"]
        print(f"Testing {t_type} ({case['name']})...", end=" ")
        
        doc = create_mock_doc(t_type, case["name"], case["header"], case["lines"])
        
        try:
            html_bytes = generate_combined_html([doc], dummy_gen)
            html = html_bytes.decode('utf-8')
            
            # Checks
            has_premium = "nav-card" in html
            
            # Check for specific title format I defined in seed_all_layouts.py
            # e.g. 810 expects "Invoice #", 864 expects "Message #", etc.
            # This implicitly validates the correct config was loaded.
            
            has_data = list(case["header"].values())[0] in html
            
            status = "PASS"
            if not has_premium: status = "FAIL (Style Missing)"
            if not has_data: status = "FAIL (Data Missing)"
            
            # Special check for Configuration Missing error
            if "Configuration Missing" in html:
                 status = "FAIL (Config Missing Error)"
                 
            print(status)
            results.append({"type": t_type, "status": status, "style": has_premium, "data": has_data})
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append({"type": t_type, "status": "ERROR", "error": str(e)})

    # Summary
    print("\n--- Summary ---")
    failures = [r for r in results if r["status"] != "PASS"]
    if not failures:
        print("ALL TESTS PASSED ✅")
    else:
        print(f"{len(failures)} TESTS FAILED ❌")
        for f in failures:
            print(f"- {f['type']}: {f['status']}")

if __name__ == "__main__":
    test_all_types()
