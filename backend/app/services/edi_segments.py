"""
EDI Segment Mappings

Maps raw EDI segment codes to parsed field keys for each transaction type.
This allows the UI to show users which EDI segment corresponds to each field.
"""

# EDI_SEGMENT_MAP structure:
# {
#   "transaction_type": {
#       "segment_code": {
#           "key": "parsed_field_name",
#           "description": "Human-readable description"
#       }
#   }
# }

EDI_SEGMENT_MAP = {
    "812": {
        "BIG01": {"key": "credit_debit_number", "description": "Credit/Debit Memo Number"},
        "BIG02": {"key": "date", "description": "Transaction Date"},
        "REF02": {"key": "purchase_order_number", "description": "PO Reference Number"},
        "N102": {"key": "vendor_name", "description": "Vendor/Seller Name"},
        "N104": {"key": "buyer_name", "description": "Buyer Name"},
        "ITD01": {"key": "terms_type", "description": "Terms Type Code"},
        "TDS01": {"key": "total_amount", "description": "Total Monetary Amount"},
        "IT101": {"key": "assigned_id", "description": "Line Item Identifier"},
        "IT102": {"key": "quantity", "description": "Quantity"},
        "IT104": {"key": "unit_price", "description": "Unit Price"},
        "PID05": {"key": "description", "description": "Product Description"},
    },
    "810": {
        "BIG01": {"key": "invoice_date", "description": "Invoice Date"},
        "BIG02": {"key": "invoice_number", "description": "Invoice Number"},
        "BIG03": {"key": "po_date", "description": "PO Date"},
        "BIG04": {"key": "po_number", "description": "Purchase Order Number"},
        "N102": {"key": "vendor_name", "description": "Vendor/Seller Name"},
        "N104": {"key": "buyer_name", "description": "Buyer Name"},
        "TDS01": {"key": "total_amount", "description": "Total Amount Due"},
        "IT101": {"key": "line_number", "description": "Line Number"},
        "IT102": {"key": "quantity_invoiced", "description": "Quantity Invoiced"},
        "IT104": {"key": "unit_price", "description": "Unit Price"},
    },
    "850": {
        "BEG01": {"key": "transaction_set_purpose", "description": "Transaction Purpose"},
        "BEG02": {"key": "po_type", "description": "PO Type Code"},
        "BEG03": {"key": "po_number", "description": "Purchase Order Number"},
        "BEG05": {"key": "po_date", "description": "PO Date"},
        "REF02": {"key": "vendor_number", "description": "Vendor Reference"},
        "N102": {"key": "ship_to_name", "description": "Ship To Name"},
        "N301": {"key": "address_line1", "description": "Address Line 1"},
        "N401": {"key": "city", "description": "City"},
        "N402": {"key": "state", "description": "State"},
        "N403": {"key": "zip_code", "description": "Postal Code"},
        "PO101": {"key": "quantity_ordered", "description": "Quantity Ordered"},
        "PO102": {"key": "unit_of_measure", "description": "Unit of Measure"},
        "PO104": {"key": "unit_price", "description": "Unit Price"},
    },
    "855": {
        "BAK01": {"key": "transaction_purpose", "description": "Transaction Purpose"},
        "BAK02": {"key": "ack_type", "description": "Acknowledgment Type"},
        "BAK03": {"key": "po_number", "description": "PO Number"},
        "BAK04": {"key": "po_date", "description": "PO Date"},
        "ACK01": {"key": "line_item_status", "description": "Line Status Code"},
        "ACK02": {"key": "quantity_acknowledged", "description": "Quantity"},
    },
    "856": {
        "BSN01": {"key": "transaction_purpose", "description": "Transaction Purpose"},
        "BSN02": {"key": "shipment_id", "description": "Shipment Identification"},
        "BSN03": {"key": "shipment_date", "description": "Shipment Date"},
        "BSN04": {"key": "shipment_time", "description": "Shipment Time"},
        "TD501": {"key": "carrier_code", "description": "Carrier Code"},
        "TD502": {"key": "routing", "description": "Routing"},
        "REF02": {"key": "pro_number", "description": "PRO Number"},
        "HL03": {"key": "hierarchy_level", "description": "Hierarchy Level Code"},
        "SN101": {"key": "marked_quantity", "description": "Marked Quantity"},
    },
    "997": {
        "AK101": {"key": "functional_id", "description": "Functional ID Code"},
        "AK102": {"key": "group_control_number", "description": "Group Control Number"},
        "AK501": {"key": "transaction_status", "description": "Transaction Status"},
        "AK901": {"key": "ack_status", "description": "Acknowledgment Status"},
    },
}

# Provide default mappings for other types
DEFAULT_SEGMENTS = {
    "REF02": {"key": "reference_number", "description": "Reference Number"},
    "DTM02": {"key": "date_time", "description": "Date/Time"},
    "N102": {"key": "name", "description": "Name"},
    "N302": {"key": "address", "description": "Address"},
    "N403": {"key": "postal_code", "description": "Postal Code"},
    "PER04": {"key": "contact_number", "description": "Contact Number"},
}


def get_segments_for_type(type_code: str) -> dict:
    """Get segment mappings for a transaction type."""
    return EDI_SEGMENT_MAP.get(type_code, DEFAULT_SEGMENTS)


def get_all_available_keys(type_code: str) -> list:
    """Get list of available data keys for a transaction type."""
    segments = get_segments_for_type(type_code)
    return [info["key"] for info in segments.values()]


def get_segment_for_key(type_code: str, key: str) -> str | None:
    """Find the EDI segment code for a given data key."""
    segments = get_segments_for_type(type_code)
    for segment_code, info in segments.items():
        if info["key"] == key:
            return segment_code
    return None
