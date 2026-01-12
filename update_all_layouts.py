"""
Comprehensive Layout Configuration Update Script.
Updates LayoutConfig JSON for all 17 EDI transaction types with proper dynamic sections.
"""

import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.db import get_db_connection, get_cursor

# Comprehensive LayoutConfig for each transaction type
LAYOUT_CONFIGS = {
    "810": {
        "title_format": "Invoice #{invoice_number}",
        "theme_color": "#2563eb",
        "sections": [
            {
                "id": "invoice_info",
                "title": "Invoice Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "invoice_number", "label": "Invoice #", "type": "text", "visible": True, "style": "bold"},
                    {"key": "invoice_date", "label": "Invoice Date", "type": "date", "visible": True},
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True},
                    {"key": "po_date", "label": "PO Date", "type": "date", "visible": True},
                    {"key": "transaction_type_code", "label": "Transaction Type", "type": "text", "visible": True},
                    {"key": "currency", "label": "Currency", "type": "text", "visible": True},
                    {"key": "payment_terms", "label": "Payment Terms", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "references",
                "title": "References",
                "type": "table",
                "visible": True,
                "data_source_key": "references",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Reference Type", "type": "text", "visible": True},
                    {"key": "value", "label": "Reference Value", "type": "text", "visible": True},
                ]
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                    {"key": "address_line1", "label": "Address", "type": "text", "visible": True},
                    {"key": "city", "label": "City", "type": "text", "visible": True},
                    {"key": "state", "label": "State", "type": "text", "visible": True},
                    {"key": "zip", "label": "ZIP", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Line Items",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "quantity", "label": "Qty", "type": "number", "visible": True},
                    {"key": "unit", "label": "Unit", "type": "text", "visible": True},
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                    {"key": "total", "label": "Total", "type": "currency", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Invoice Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_line_items", "label": "Total Line Items", "type": "number", "visible": True},
                    {"key": "total_amount", "label": "Total Amount", "type": "currency", "visible": True, "style": "bold"},
                ],
                "columns": []
            }
        ]
    },
    "812": {
        "title_format": "Credit/Debit Adjustment #{credit_debit_number}",
        "theme_color": "#dc2626",
        "sections": [
            {
                "id": "memo_info",
                "title": "Memo Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "credit_debit_number", "label": "Memo #", "type": "text", "visible": True, "style": "bold"},
                    {"key": "adjustment_date", "label": "Date", "type": "date", "visible": True},
                    {"key": "credit_debit_flag_desc", "label": "Type", "type": "text", "visible": True},
                    {"key": "amount", "label": "Amount", "type": "currency", "visible": True, "style": "bold"},
                    {"key": "invoice_number", "label": "Original Invoice", "type": "text", "visible": True},
                    {"key": "currency", "label": "Currency", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Line Items",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "adjustment_reason", "label": "Reason", "type": "text", "visible": True},
                    {"key": "quantity", "label": "Qty", "type": "number", "visible": True},
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                    {"key": "adjustment_amount", "label": "Amount", "type": "currency", "visible": True},
                    {"key": "credit_debit_type", "label": "Type", "type": "text", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_line_items", "label": "Total Line Items", "type": "number", "visible": True},
                    {"key": "total_amount", "label": "Total Amount", "type": "currency", "visible": True, "style": "bold"},
                ],
                "columns": []
            }
        ]
    },
    "816": {
        "title_format": "Organizational Relationships #{reference_id}",
        "theme_color": "#7c3aed",
        "sections": [
            {
                "id": "header_info",
                "title": "Document Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "reference_id", "label": "Reference ID", "type": "text", "visible": True, "style": "bold"},
                    {"key": "date", "label": "Date", "type": "date", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "hierarchy",
                "title": "Organizational Hierarchy",
                "type": "table",
                "visible": True,
                "data_source_key": "hierarchy",
                "fields": [],
                "columns": [
                    {"key": "level", "label": "Level", "type": "text", "visible": True},
                    {"key": "entity_type", "label": "Entity Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                    {"key": "address", "label": "Address", "type": "text", "visible": True},
                ]
            }
        ]
    },
    "820": {
        "title_format": "Payment Order #{trace_number}",
        "theme_color": "#059669",
        "sections": [
            {
                "id": "payment_info",
                "title": "Payment Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "trace_number", "label": "Trace #", "type": "text", "visible": True, "style": "bold"},
                    {"key": "payment_date", "label": "Payment Date", "type": "date", "visible": True},
                    {"key": "payment_amount", "label": "Amount", "type": "currency", "visible": True, "style": "bold"},
                    {"key": "payment_method", "label": "Method", "type": "text", "visible": True},
                    {"key": "credit_debit", "label": "Credit/Debit", "type": "text", "visible": True},
                    {"key": "currency", "label": "Currency", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Payer & Payee",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Role", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                    {"key": "address_line1", "label": "Address", "type": "text", "visible": True},
                ]
            },
            {
                "id": "remittance",
                "title": "Remittance Details",
                "type": "table",
                "visible": True,
                "data_source_key": "remittance_details",
                "fields": [],
                "columns": [
                    {"key": "invoice_number", "label": "Invoice #", "type": "text", "visible": True},
                    {"key": "original_amount", "label": "Invoice Amount", "type": "currency", "visible": True},
                    {"key": "amount_paid", "label": "Amount Paid", "type": "currency", "visible": True},
                    {"key": "balance_due", "label": "Balance Due", "type": "currency", "visible": True},
                    {"key": "adjustment_amount", "label": "Adjustment", "type": "currency", "visible": True},
                ]
            }
        ]
    },
    "824": {
        "title_format": "Application Advice #{reference_id}",
        "theme_color": "#ea580c",
        "sections": [
            {
                "id": "header_info",
                "title": "Advice Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "reference_id", "label": "Reference ID", "type": "text", "visible": True, "style": "bold"},
                    {"key": "date", "label": "Date", "type": "date", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "summary",
                "title": "Status Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_accepted", "label": "Accepted", "type": "number", "visible": True},
                    {"key": "total_rejected", "label": "Rejected", "type": "number", "visible": True},
                    {"key": "total_errors", "label": "Errors", "type": "number", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "transactions",
                "title": "Transaction Status",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "transaction_set_id", "label": "Transaction", "type": "text", "visible": True},
                    {"key": "status", "label": "Status", "type": "status", "visible": True},
                    {"key": "reference_id", "label": "Reference", "type": "text", "visible": True},
                    {"key": "error_message", "label": "Error", "type": "text", "visible": True},
                ]
            }
        ]
    },
    "830": {
        "title_format": "Planning Schedule #{schedule_id}",
        "theme_color": "#0891b2",
        "sections": [
            {
                "id": "schedule_info",
                "title": "Schedule Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "schedule_id", "label": "Schedule ID", "type": "text", "visible": True, "style": "bold"},
                    {"key": "schedule_date", "label": "Schedule Date", "type": "date", "visible": True},
                    {"key": "schedule_type", "label": "Schedule Type", "type": "text", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                    {"key": "horizon_start", "label": "Horizon Start", "type": "date", "visible": True},
                    {"key": "horizon_end", "label": "Horizon End", "type": "date", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Forecast Items",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "total_forecast_quantity", "label": "Total Forecast Qty", "type": "number", "visible": True},
                    {"key": "unit", "label": "Unit", "type": "text", "visible": True},
                ]
            }
        ]
    },
    "850": {
        "title_format": "Purchase Order #{po_number}",
        "theme_color": "#2563eb",
        "sections": [
            {
                "id": "order_info",
                "title": "Order Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True, "style": "bold"},
                    {"key": "po_date", "label": "PO Date", "type": "date", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                    {"key": "order_type", "label": "Order Type", "type": "text", "visible": True},
                    {"key": "currency", "label": "Currency", "type": "text", "visible": True},
                    {"key": "payment_terms", "label": "Payment Terms", "type": "text", "visible": True},
                    {"key": "fob", "label": "FOB", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "dates",
                "title": "Key Dates",
                "type": "fields",
                "visible": True,
                "data_source_key": "dates",
                "fields": [
                    {"key": "Delivery Requested", "label": "Delivery Requested", "type": "date", "visible": True},
                    {"key": "Requested Ship Date", "label": "Requested Ship Date", "type": "date", "visible": True},
                    {"key": "Ship Not Before", "label": "Ship Not Before", "type": "date", "visible": True},
                    {"key": "Ship Not Later Than", "label": "Ship Not Later Than", "type": "date", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                    {"key": "address_line1", "label": "Address", "type": "text", "visible": True},
                    {"key": "city", "label": "City", "type": "text", "visible": True},
                    {"key": "state", "label": "State", "type": "text", "visible": True},
                    {"key": "zip", "label": "ZIP", "type": "text", "visible": True},
                    {"key": "contact_name", "label": "Contact", "type": "text", "visible": True},
                    {"key": "contact_number", "label": "Phone", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Line Items",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "quantity", "label": "Qty", "type": "number", "visible": True},
                    {"key": "unit", "label": "Unit", "type": "text", "visible": True},
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                    {"key": "total", "label": "Total", "type": "currency", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Order Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_line_items", "label": "Total Line Items", "type": "number", "visible": True},
                    {"key": "total_amount", "label": "Total Amount", "type": "currency", "visible": True, "style": "bold"},
                ],
                "columns": []
            }
        ]
    },
    "852": {
        "title_format": "Product Activity Report #{report_id}",
        "theme_color": "#8b5cf6",
        "sections": [
            {
                "id": "report_info",
                "title": "Report Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "report_id", "label": "Report ID", "type": "text", "visible": True, "style": "bold"},
                    {"key": "report_date", "label": "Report Date", "type": "date", "visible": True},
                    {"key": "report_type", "label": "Report Type", "type": "text", "visible": True},
                    {"key": "report_start_date", "label": "Period Start", "type": "date", "visible": True},
                    {"key": "report_end_date", "label": "Period End", "type": "date", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Product Activity",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "quantity_sold", "label": "Qty Sold", "type": "number", "visible": True},
                    {"key": "quantity_on_hand", "label": "Qty On Hand", "type": "number", "visible": True},
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                    {"key": "sales_amount", "label": "Sales Amount", "type": "currency", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_items", "label": "Total Items", "type": "number", "visible": True},
                    {"key": "total_quantity_sold", "label": "Total Qty Sold", "type": "number", "visible": True},
                    {"key": "total_quantity_on_hand", "label": "Total Qty On Hand", "type": "number", "visible": True},
                ],
                "columns": []
            }
        ]
    },
    "855": {
        "title_format": "PO Acknowledgment #{po_number}",
        "theme_color": "#16a34a",
        "sections": [
            {
                "id": "ack_info",
                "title": "Acknowledgment Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True, "style": "bold"},
                    {"key": "po_date", "label": "PO Date", "type": "date", "visible": True},
                    {"key": "acknowledgment_date", "label": "Acknowledgment Date", "type": "date", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                    {"key": "acknowledgment_type", "label": "Acknowledgment Type", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                    {"key": "address_line1", "label": "Address", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Line Item Acknowledgments",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "quantity_ordered", "label": "Qty Ordered", "type": "number", "visible": True},
                    {"key": "acknowledgment_status", "label": "Status", "type": "status", "visible": True},
                    {"key": "quantity_acknowledged", "label": "Qty Acknowledged", "type": "number", "visible": True},
                    {"key": "ship_date", "label": "Ship Date", "type": "date", "visible": True},
                ]
            }
        ]
    },
    "856": {
        "title_format": "Advance Ship Notice #{shipment_id}",
        "theme_color": "#0284c7",
        "sections": [
            {
                "id": "shipment_info",
                "title": "Shipment Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "shipment_id", "label": "Shipment ID", "type": "text", "visible": True, "style": "bold"},
                    {"key": "shipment_date", "label": "Ship Date", "type": "date", "visible": True},
                    {"key": "shipment_time", "label": "Ship Time", "type": "text", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "carrier_info",
                "title": "Carrier & Routing",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "carrier_code", "label": "Carrier", "type": "text", "visible": True},
                    {"key": "routing", "label": "Routing", "type": "text", "visible": True},
                    {"key": "transport_method", "label": "Transport Method", "type": "text", "visible": True},
                    {"key": "pro_number", "label": "PRO Number", "type": "text", "visible": True},
                    {"key": "bill_of_lading", "label": "Bill of Lading", "type": "text", "visible": True},
                    {"key": "tracking_number", "label": "Tracking Number", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Ship From / Ship To",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                    {"key": "address_line1", "label": "Address", "type": "text", "visible": True},
                    {"key": "city", "label": "City", "type": "text", "visible": True},
                    {"key": "state", "label": "State", "type": "text", "visible": True},
                    {"key": "zip", "label": "ZIP", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Shipped Items",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "quantity_shipped", "label": "Qty Shipped", "type": "number", "visible": True},
                    {"key": "unit", "label": "Unit", "type": "text", "visible": True},
                    {"key": "sscc", "label": "SSCC", "type": "text", "visible": True},
                ]
            }
        ]
    },
    "860": {
        "title_format": "PO Change Request #{po_number}",
        "theme_color": "#d97706",
        "sections": [
            {
                "id": "change_info",
                "title": "Change Request Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True, "style": "bold"},
                    {"key": "change_date", "label": "Change Date", "type": "date", "visible": True},
                    {"key": "change_sequence", "label": "Change Sequence", "type": "text", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Line Item Changes",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "change_type", "label": "Change Type", "type": "status", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "new_quantity", "label": "New Qty", "type": "number", "visible": True},
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Change Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_changes", "label": "Total Changes", "type": "number", "visible": True},
                ],
                "columns": []
            }
        ]
    },
    "861": {
        "title_format": "Receiving Advice #{receiving_advice_number}",
        "theme_color": "#0d9488",
        "sections": [
            {
                "id": "receipt_info",
                "title": "Receipt Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "receiving_advice_number", "label": "Receiving Advice #", "type": "text", "visible": True, "style": "bold"},
                    {"key": "date", "label": "Receipt Date", "type": "date", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                    {"key": "condition", "label": "Condition", "type": "status", "visible": True},
                    {"key": "action", "label": "Action", "type": "text", "visible": True},
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True},
                    {"key": "bill_of_lading", "label": "Bill of Lading", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Received Items",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "quantity_received", "label": "Qty Received", "type": "number", "visible": True},
                    {"key": "quantity_damaged", "label": "Qty Damaged", "type": "number", "visible": True},
                    {"key": "condition", "label": "Condition", "type": "status", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Receipt Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_items", "label": "Total Items", "type": "number", "visible": True},
                    {"key": "total_quantity_received", "label": "Total Qty Received", "type": "number", "visible": True},
                    {"key": "total_quantity_damaged", "label": "Total Qty Damaged", "type": "number", "visible": True},
                ],
                "columns": []
            }
        ]
    },
    "864": {
        "title_format": "Text Message",
        "theme_color": "#64748b",
        "sections": [
            {
                "id": "message_info",
                "title": "Message Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "subject", "label": "Subject", "type": "text", "visible": True, "style": "bold"},
                    {"key": "message_date", "label": "Date", "type": "date", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "From / To",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Role", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                ]
            },
            {
                "id": "message_content",
                "title": "Message Content",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "full_message", "label": "Message", "type": "text", "visible": True},
                ],
                "columns": []
            }
        ]
    },
    "870": {
        "title_format": "Order Status Report #{report_id}",
        "theme_color": "#6366f1",
        "sections": [
            {
                "id": "report_info",
                "title": "Report Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "report_id", "label": "Report ID", "type": "text", "visible": True, "style": "bold"},
                    {"key": "report_date", "label": "Report Date", "type": "date", "visible": True},
                    {"key": "status_report", "label": "Overall Status", "type": "status", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Order Status Detail",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True},
                    {"key": "status", "label": "Status", "type": "status", "visible": True},
                    {"key": "quantity", "label": "Quantity", "type": "number", "visible": True},
                    {"key": "status_date", "label": "Status Date", "type": "date", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                ]
            }
        ]
    },
    "875": {
        "title_format": "Grocery PO #{po_number}",
        "theme_color": "#15803d",
        "sections": [
            {
                "id": "order_info",
                "title": "Order Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True, "style": "bold"},
                    {"key": "po_date", "label": "PO Date", "type": "date", "visible": True},
                    {"key": "ship_date", "label": "Ship Date", "type": "date", "visible": True},
                    {"key": "order_type", "label": "Order Type", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                    {"key": "address_line1", "label": "Address", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Line Items",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "quantity", "label": "Qty", "type": "number", "visible": True},
                    {"key": "unit", "label": "Unit", "type": "text", "visible": True},
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                    {"key": "total", "label": "Total", "type": "currency", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Order Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_line_items", "label": "Total Line Items", "type": "number", "visible": True},
                    {"key": "total_quantity", "label": "Total Quantity", "type": "number", "visible": True},
                    {"key": "total_amount", "label": "Total Amount", "type": "currency", "visible": True, "style": "bold"},
                ],
                "columns": []
            }
        ]
    },
    "880": {
        "title_format": "Grocery Invoice #{invoice_number}",
        "theme_color": "#b91c1c",
        "sections": [
            {
                "id": "invoice_info",
                "title": "Invoice Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "invoice_number", "label": "Invoice #", "type": "text", "visible": True, "style": "bold"},
                    {"key": "invoice_date", "label": "Invoice Date", "type": "date", "visible": True},
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True},
                    {"key": "po_date", "label": "PO Date", "type": "date", "visible": True},
                    {"key": "ship_date", "label": "Ship Date", "type": "date", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "parties",
                "title": "Entities & Parties",
                "type": "table",
                "visible": True,
                "data_source_key": "parties",
                "fields": [],
                "columns": [
                    {"key": "type", "label": "Party Type", "type": "text", "visible": True},
                    {"key": "name", "label": "Name", "type": "text", "visible": True},
                    {"key": "id", "label": "ID", "type": "text", "visible": True},
                    {"key": "address_line1", "label": "Address", "type": "text", "visible": True},
                ]
            },
            {
                "id": "line_items",
                "title": "Line Items",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "#", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Product ID", "type": "text", "visible": True},
                    {"key": "quantity", "label": "Qty", "type": "number", "visible": True},
                    {"key": "unit", "label": "Unit", "type": "text", "visible": True},
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                    {"key": "total", "label": "Total", "type": "currency", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Invoice Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_line_items", "label": "Total Line Items", "type": "number", "visible": True},
                    {"key": "total_quantity", "label": "Total Quantity", "type": "number", "visible": True},
                    {"key": "total_invoice_amount", "label": "Total Amount", "type": "currency", "visible": True, "style": "bold"},
                ],
                "columns": []
            }
        ]
    },
    "997": {
        "title_format": "Functional Acknowledgment",
        "theme_color": "#475569",
        "sections": [
            {
                "id": "ack_info",
                "title": "Acknowledgment Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "functional_id_code", "label": "Functional ID", "type": "text", "visible": True, "style": "bold"},
                    {"key": "group_control_number", "label": "Group Control #", "type": "text", "visible": True},
                    {"key": "version", "label": "Version", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "group_status",
                "title": "Group Status",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "group_status", "label": "Status", "type": "status", "visible": True},
                    {"key": "sets_included", "label": "Sets Included", "type": "number", "visible": True},
                    {"key": "sets_received", "label": "Sets Received", "type": "number", "visible": True},
                    {"key": "sets_accepted", "label": "Sets Accepted", "type": "number", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "line_items",
                "title": "Transaction Set Responses",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "transaction_set_id", "label": "Transaction Set", "type": "text", "visible": True},
                    {"key": "control_number", "label": "Control #", "type": "text", "visible": True},
                    {"key": "status", "label": "Status", "type": "status", "visible": True},
                    {"key": "error_count", "label": "Errors", "type": "number", "visible": True},
                ]
            },
            {
                "id": "summary",
                "title": "Summary",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "total_accepted", "label": "Accepted", "type": "number", "visible": True},
                    {"key": "total_rejected", "label": "Rejected", "type": "number", "visible": True},
                    {"key": "total_errors", "label": "Total Errors", "type": "number", "visible": True},
                ],
                "columns": []
            }
        ]
    }
}


def update_all_layouts():
    """Update layout configurations for all 17 transaction types."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        updated_count = 0
        
        for type_code, config in LAYOUT_CONFIGS.items():
            # Update the system layout (user_id IS NULL) with PRODUCTION status
            cur.execute("""
                UPDATE layout_versions 
                SET config_json = %s, updated_at = NOW()
                WHERE transaction_type_code = %s 
                AND user_id IS NULL 
                AND status = 'PRODUCTION'
            """, (json.dumps(config), type_code))
            
            rows_affected = cur.rowcount
            
            # If no PRODUCTION layout, try DRAFT
            if rows_affected == 0:
                cur.execute("""
                    UPDATE layout_versions 
                    SET config_json = %s, updated_at = NOW()
                    WHERE transaction_type_code = %s 
                    AND user_id IS NULL 
                    AND status = 'DRAFT'
                """, (json.dumps(config), type_code))
                rows_affected = cur.rowcount
            
            # If still no layout, try any system layout
            if rows_affected == 0:
                cur.execute("""
                    UPDATE layout_versions 
                    SET config_json = %s, updated_at = NOW()
                    WHERE transaction_type_code = %s 
                    AND user_id IS NULL
                    ORDER BY version_number DESC
                    LIMIT 1
                """, (json.dumps(config), type_code))
                rows_affected = cur.rowcount
            
            if rows_affected > 0:
                print(f"✓ Updated {type_code} layout")
                updated_count += 1
            else:
                print(f"✗ No layout found for {type_code}")
        
        conn.commit()
        print(f"\nTotal updated: {updated_count}/{len(LAYOUT_CONFIGS)}")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("Updating layout configurations for all 17 EDI transaction types...")
    print("=" * 60)
    update_all_layouts()
    print("=" * 60)
    print("Done!")
