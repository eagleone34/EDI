"""
Database migrations module.
Contains functions to update database configurations on startup.
"""

import json
import logging

logger = logging.getLogger(__name__)

# Comprehensive LayoutConfig for each transaction type
LAYOUT_CONFIGS = {
    "810": {
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
        "theme_color": "#dc2626",
        "sections": [
            {
                "id": "memo_info",
                "title": "Memo Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "credit_debit_number", "label": "Memo #", "type": "text", "visible": True, "style": "bold"},
                    {"key": "date", "label": "Date", "type": "date", "visible": True},
                    {"key": "credit_flag", "label": "Type", "type": "text", "visible": True},
                    {"key": "amount", "label": "Amount", "type": "currency", "visible": True, "style": "bold"},
                    {"key": "original_invoice_number", "label": "Original Invoice", "type": "text", "visible": True},
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
                "id": "adjustments",
                "title": "Adjustments",
                "type": "table",
                "visible": True,
                "data_source_key": "adjustments",
                "fields": [],
                "columns": [
                    {"key": "reason", "label": "Reason", "type": "text", "visible": True},
                    {"key": "amount", "label": "Amount", "type": "currency", "visible": True},
                    {"key": "type", "label": "Type", "type": "text", "visible": True},
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
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "visible": True},
                ]
            }
        ]
    },
    "816": {
        "title_format": "{name} - {ref_number}",
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
                ]
            }
        ]
    },
    "820": {
        "title_format": "{name} - {ref_number}",
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
                ]
            }
        ]
    },
    "824": {
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
        "theme_color": "#2563eb",
        "sections": [
            {
                "id": "order_info",
                "title": "Document Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "po_number", "label": "PO Number", "type": "text", "visible": True, "style": "bold"},
                    {"key": "po_date", "label": "PO Date", "type": "date", "visible": True},
                    {"key": "purpose", "label": "Purpose", "type": "text", "visible": True},
                    {"key": "order_type", "label": "Order Type", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "contact_info",
                "title": "Contact Information",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "contact_function", "label": "Contact Role", "type": "text", "visible": True},
                    {"key": "contact_name", "label": "Contact Name", "type": "text", "visible": True, "style": "bold"},
                    {"key": "contact_number", "label": "Telephone", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "references",
                "title": "Reference Information",
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
                "id": "fob_info",
                "title": "F.O.B. Related Instructions",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "fob", "label": "Shipment Method of Payment", "type": "text", "visible": True},
                    {"key": "fob_location", "label": "F.O.B. Location", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "sales_req",
                "title": "Sales Requirements",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "sales_requirement", "label": "Sales Requirement", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "terms",
                "title": "Terms of Sale",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "payment_terms", "label": "Payment Terms", "type": "text", "visible": True},
                    {"key": "currency", "label": "Currency", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "dates",
                "title": "Date/Time Reference",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "delivery_requested", "label": "Delivery Requested", "type": "date", "visible": True},
                    {"key": "requested_ship_date", "label": "Requested Ship Date", "type": "date", "visible": True},
                    {"key": "ship_not_before", "label": "Ship Not Before", "type": "date", "visible": True},
                    {"key": "ship_not_later", "label": "Ship Not Later Than", "type": "date", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "carrier_details",
                "title": "Carrier Details (Quantity and Weight)",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "commodity_code_qualifier", "label": "Commodity Code Qualifier", "type": "text", "visible": True},
                    {"key": "commodity_code", "label": "Commodity Code", "type": "text", "visible": True},
                    {"key": "weight", "label": "Weight", "type": "text", "visible": True},
                    {"key": "weight_unit", "label": "Weight Unit", "type": "text", "visible": True},
                ],
                "columns": []
            },
            {
                "id": "routing",
                "title": "Carrier Details (Routing)",
                "type": "fields",
                "visible": True,
                "fields": [
                    {"key": "transport_method", "label": "Transportation Method", "type": "text", "visible": True},
                    {"key": "carrier", "label": "Carrier", "type": "text", "visible": True},
                    {"key": "routing", "label": "Routing", "type": "text", "visible": True},
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
                "title": "Line Item Information",
                "type": "table",
                "visible": True,
                "data_source_key": "line_items",
                "fields": [],
                "columns": [
                    {"key": "line_number", "label": "Line", "type": "text", "visible": True},
                    {"key": "upc", "label": "UPC", "type": "text", "visible": True},
                    {"key": "product_id", "label": "Purchaser's Item", "type": "text", "visible": True},
                    {"key": "vendor_style", "label": "Vendor Style", "type": "text", "visible": True},
                    {"key": "sku", "label": "SKU", "type": "text", "visible": True},
                    {"key": "description", "label": "Description", "type": "text", "visible": True},
                    {"key": "pack", "label": "Pack", "type": "text", "visible": True},
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
                    {"key": "calculated_total", "label": "Total Amount", "type": "currency", "visible": True, "style": "bold"},
                ],
                "columns": []
            }
        ]
    },
    "852": {
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name}",
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
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
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
        "title_format": "{name} - {ref_number}",
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
            }
        ]
    },
    "997": {
        "title_format": "{name}",
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


def run_layout_migrations(conn, cur):
    """
    Update layout configurations for all 17 EDI transaction types.
    Called during app startup to ensure layouts are up-to-date.
    """
    updated_count = 0
    
    for type_code, config in LAYOUT_CONFIGS.items():
        try:
            # Update the system layout (user_id IS NULL) with PRODUCTION status
            cur.execute("""
                UPDATE layout_versions 
                SET config_json = %s, updated_at = NOW()
                WHERE transaction_type_code = %s 
                AND user_id IS NULL 
                AND status = 'PRODUCTION'
            """, (json.dumps(config), type_code))
            
            rows_affected = cur.rowcount
            
            # If no PRODUCTION layout, try updating DRAFT
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
                logger.info(f"Updated {type_code} layout configuration")
                updated_count += 1
                
        except Exception as e:
            logger.warning(f"Failed to update {type_code} layout: {e}")
    
    conn.commit()
    logger.info(f"Layout migration complete: {updated_count}/{len(LAYOUT_CONFIGS)} layouts updated")
    return updated_count


def run_schema_migrations(conn, cur):
    """
    Run critical schema migrations that might have been missed.
    Called during app startup.
    """
    try:
        logging.info("Running schema migrations...")

        # 0. Create documents table (CRITICAL)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                filename VARCHAR(255) NOT NULL,
                transaction_type VARCHAR(50),
                transaction_name VARCHAR(100),
                trading_partner VARCHAR(255),
                transaction_count INTEGER DEFAULT 1,
                source VARCHAR(50) DEFAULT 'web',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                pdf_url TEXT,
                excel_url TEXT,
                html_url TEXT
            );
        """)
        
        # 1. Add inbound_email to users
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS inbound_email VARCHAR(255) UNIQUE;
        """)
        
        # 2. Create inbound_email_errors
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inbound_email_errors (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                sender_email VARCHAR(255) NOT NULL,
                filename VARCHAR(255),
                error_message TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # 3. Create email_routes (CRITICAL FIX)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS email_routes (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                transaction_type VARCHAR(50) NOT NULL,
                email_addresses TEXT[] NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, transaction_type)
            );
        """)
        
        # 4. Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_inbound_email ON users(inbound_email);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_email_routes_lookup ON email_routes(user_id, transaction_type);")
        
        # 5. Add source column to documents (Fix for PGRST204)
        cur.execute("""
            ALTER TABLE documents 
            ADD COLUMN IF NOT EXISTS source VARCHAR(50) DEFAULT 'web';
        """)
        
        # Notify PostgREST to reload schema cache
        cur.execute("NOTIFY pgrst, 'reload schema';")
        
        conn.commit()
        logging.info("Schema migrations completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Schema migration failed: {e}")
        conn.rollback()
        return False
