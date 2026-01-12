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
    "810": {
        # Invoice Information
        "BIG01": {"key": "invoice_date", "description": "Invoice Date"},
        "BIG02": {"key": "invoice_number", "description": "Invoice Number"},
        "BIG03": {"key": "po_date", "description": "PO Date"},
        "BIG04": {"key": "po_number", "description": "Purchase Order Number"},
        "BIG07": {"key": "transaction_type_code", "description": "Transaction Type Code"},
        "CUR01": {"key": "currency", "description": "Currency Code"},
        "ITD12": {"key": "payment_terms", "description": "Payment Terms Description"},
        # References (table)
        "REF01": {"key": "type", "description": "Reference Qualifier"},
        "REF02": {"key": "value", "description": "Reference Value"},
        "REF02_DP": {"key": "department_number", "description": "Department Number"},
        "REF02_IA": {"key": "internal_vendor_number", "description": "Internal Vendor Number"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N301": {"key": "address_line1", "description": "Address Line 1"},
        "N401": {"key": "city", "description": "City Name"},
        "N402": {"key": "state", "description": "State/Province Code"},
        "N403": {"key": "zip", "description": "Postal Code"},
        "N1_BY": {"key": "buying_party", "description": "Buying Party"},
        "N1_SE": {"key": "selling_party", "description": "Selling Party"},
        "N1_ST": {"key": "ship_to", "description": "Ship To"},
        "N1_RI": {"key": "remit_to", "description": "Remit To"},
        # Line Items (table)
        "IT101": {"key": "line_number", "description": "Line Item Number"},
        "IT107": {"key": "product_id", "description": "Product ID"},
        "PID05": {"key": "description", "description": "Product Description"},
        "IT102": {"key": "quantity", "description": "Quantity Invoiced"},
        "IT103": {"key": "unit", "description": "Unit of Measure"},
        "IT104": {"key": "unit_price", "description": "Unit Price"},
        "CALC": {"key": "total", "description": "Line Total (Calculated)"},
        # Summary
        "CTT01": {"key": "total_line_items", "description": "Total Line Items"},
        "TDS01": {"key": "total_amount", "description": "Total Amount Due"},
    },
    "812": {
        # Memo Information (header fields)
        "BCD01": {"key": "adjustment_date", "description": "Transaction Date"},
        "BCD02": {"key": "credit_debit_number", "description": "Credit/Debit Memo Number"},
        "BCD03": {"key": "transaction_handling_desc", "description": "Handling Code"},
        "BCD04": {"key": "amount", "description": "Total Amount"},
        "BCD05": {"key": "credit_debit_flag_desc", "description": "Credit/Debit Flag"},
        "BCD06": {"key": "secondary_date", "description": "Invoice Date"},
        "BCD07": {"key": "invoice_number", "description": "Invoice Number"},
        "BCD09": {"key": "po_number", "description": "PO Number"},
        "BCD10": {"key": "purpose", "description": "Purpose"},
        "BCD11": {"key": "transaction_type_desc", "description": "Transaction Type"},
        "CUR02": {"key": "currency", "description": "Currency Code"},
        # Contact Information
        "PER02": {"key": "contact_name", "description": "Contact Name"},
        "PER04": {"key": "comm_number", "description": "Contact Phone"},
        # Entities & Parties (table - from header.parties)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N301": {"key": "address_line1", "description": "Address Line 1"},
        "N401": {"key": "city", "description": "City Name"},
        "N402": {"key": "state", "description": "State/Province Code"},
        "N403": {"key": "zip", "description": "Postal Code"},
        # Adjustment Details (table - line items from CDD segments)
        "CDD01": {"key": "adjustment_reason", "description": "Adjustment Reason"},
        "CDD02": {"key": "credit_debit_type", "description": "Credit/Debit Type"},
        "CDD03": {"key": "assigned_id", "description": "Assigned ID"},
        "CDD04": {"key": "adjustment_amount", "description": "Adjustment Amount"},
        "CDD05": {"key": "quantity", "description": "Quantity"},
        "CDD06": {"key": "unit", "description": "Unit of Measure"},
        "CDD08": {"key": "unit_price", "description": "Unit Price"},
        "LIN02": {"key": "product_id", "description": "Product ID"},
        "PID05": {"key": "description", "description": "Product Description"},
        "MSG01": {"key": "message", "description": "Message Text"},
        # Summary
        "CTT01": {"key": "total_line_items", "description": "Total Line Items"},
        "TDS01": {"key": "total_amount", "description": "Total Amount"},
    },
    "816": {
        # Document Information
        "BGN01": {"key": "purpose", "description": "Transaction Purpose"},
        "BGN02": {"key": "reference_id", "description": "Reference ID"},
        "BGN03": {"key": "date", "description": "Transaction Date"},
        # Organizational Hierarchy (table)
        "HL01": {"key": "hl_id", "description": "Hierarchy Level ID"},
        "HL02": {"key": "parent_id", "description": "Parent Hierarchy ID"},
        "HL03": {"key": "level", "description": "Hierarchy Level Code"},
        "NX101": {"key": "entity_type", "description": "Entity Identifier Code"},
        "NX102": {"key": "entity_id", "description": "Entity ID Number"},
        "NM102": {"key": "name", "description": "Organization/Person Name"},
        "NM109": {"key": "id", "description": "Identification Number"},
        "N101": {"key": "type", "description": "Entity Type Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party ID"},
    },
    "820": {
        # Payment Information
        "TRN02": {"key": "trace_number", "description": "Trace Number"},
        "BPR16": {"key": "payment_date", "description": "Payment/EFT Date"},
        "BPR02": {"key": "payment_amount", "description": "Payment Amount"},
        "BPR04": {"key": "payment_method", "description": "Payment Method Code"},
        "BPR03": {"key": "credit_debit", "description": "Credit/Debit Flag"},
        "BPR01": {"key": "transaction_handling", "description": "Transaction Handling Code"},
        "TRN03": {"key": "originator_id", "description": "Originator ID"},
        # Payer & Payee (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N1_PR": {"key": "payer", "description": "Payer"},
        "N1_PE": {"key": "payee", "description": "Payee"},
        # Remittance Details (table)
        "RMR02": {"key": "invoice_number", "description": "Invoice Number"},
        "RMR04": {"key": "original_amount", "description": "Original Invoice Amount"},
        "RMR05": {"key": "amount_paid", "description": "Amount Paid"},
        "RMR06": {"key": "balance_due", "description": "Balance Due"},
        "ADX01": {"key": "adjustment_reason", "description": "Adjustment Reason Code"},
        "ADX02": {"key": "adjustment_amount", "description": "Adjustment Amount"},
    },
    "824": {
        # Advice Information
        "BGN01": {"key": "purpose", "description": "Transaction Purpose"},
        "BGN02": {"key": "reference_id", "description": "Reference ID"},
        "BGN03": {"key": "date", "description": "Transaction Date"},
        # Status Summary
        "OTI01": {"key": "acknowledgment_status", "description": "Acknowledgment Status"},
        "CALC_ACC": {"key": "total_accepted", "description": "Total Accepted"},
        "CALC_REJ": {"key": "total_rejected", "description": "Total Rejected"},
        "CALC_ERR": {"key": "total_errors", "description": "Total Errors"},
        # Transaction Status (table)
        "OTI10": {"key": "transaction_set_id", "description": "Transaction Set ID"},
        "OTI03": {"key": "reference_id", "description": "Original Reference ID"},
        "OTI08": {"key": "group_control_number", "description": "Group Control Number"},
        "OTI09": {"key": "transaction_control_number", "description": "Transaction Control Number"},
        "OTI_STATUS": {"key": "status", "description": "Transaction Status"},
        "TED01": {"key": "error_code", "description": "Error Condition Code"},
        "TED02": {"key": "error_message", "description": "Error Message"},
    },
    "830": {
        # Schedule Information
        "BFR02": {"key": "schedule_id", "description": "Schedule ID Number"},
        "BFR06": {"key": "schedule_date", "description": "Schedule Date"},
        "BFR04": {"key": "schedule_type", "description": "Schedule Type Code"},
        "BFR01": {"key": "purpose", "description": "Transaction Purpose"},
        "BFR07": {"key": "horizon_start", "description": "Horizon Start Date"},
        "BFR08": {"key": "horizon_end", "description": "Horizon End Date"},
        "BFR03": {"key": "release_number", "description": "Release Number"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        # Forecast Items (table)
        "LIN_LINE": {"key": "line_number", "description": "Line Item Number"},
        "LIN02": {"key": "product_id", "description": "Product ID Code"},
        "PID05": {"key": "description", "description": "Product Description"},
        "FST01": {"key": "total_forecast_quantity", "description": "Total Forecast Quantity"},
        "FST02": {"key": "qualifier", "description": "Forecast Qualifier"},
        "FST04": {"key": "date", "description": "Forecast Date"},
        "UIT01": {"key": "unit", "description": "Unit of Measure"},
        "SHP02": {"key": "ship_quantity", "description": "Ship Quantity"},
        "SHP04": {"key": "ship_date", "description": "Ship Date"},
    },
    "850": {
        # Document Information
        "BEG01": {"key": "purpose", "description": "Transaction Purpose Code"},
        "BEG02": {"key": "order_type", "description": "PO Type Code"},
        "BEG03": {"key": "po_number", "description": "Purchase Order Number"},
        "BEG05": {"key": "po_date", "description": "PO Date"},
        # Contact Information
        "PER01": {"key": "contact_function", "description": "Contact Function Code"},
        "PER02": {"key": "contact_name", "description": "Contact Name"},
        "PER04": {"key": "contact_number", "description": "Contact Phone"},
        # Reference Information (table)
        "REF01": {"key": "type", "description": "Reference Qualifier"},
        "REF02": {"key": "value", "description": "Reference Value"},
        "REF02_DP": {"key": "department_number", "description": "Department Number"},
        "REF02_IA": {"key": "internal_vendor_number", "description": "Internal Vendor Number"},
        # F.O.B. Related Instructions
        "FOB01": {"key": "fob", "description": "Shipment Method of Payment"},
        "FOB03": {"key": "fob_location", "description": "F.O.B. Location Description"},
        # Sales Requirements
        "CS01": {"key": "sales_requirement", "description": "Sales Requirement Code"},
        # Terms of Sale
        "ITD12": {"key": "payment_terms", "description": "Payment Terms Description"},
        "CUR01": {"key": "currency", "description": "Currency Code"},
        # Date/Time Reference
        "DTM02_002": {"key": "delivery_requested", "description": "Delivery Requested Date"},
        "DTM02_010": {"key": "requested_ship_date", "description": "Requested Ship Date"},
        "DTM02_037": {"key": "ship_not_before", "description": "Ship Not Before Date"},
        "DTM02_038": {"key": "ship_not_later", "description": "Ship Not Later Than Date"},
        # Carrier Details (Quantity/Weight)
        "TD102": {"key": "commodity_code_qualifier", "description": "Commodity Code Qualifier"},
        "TD103": {"key": "commodity_code", "description": "Commodity Code"},
        "TD106": {"key": "weight", "description": "Weight"},
        "TD107": {"key": "weight_unit", "description": "Weight Unit"},
        # Carrier Details (Routing)
        "TD504": {"key": "transport_method", "description": "Transportation Method"},
        "TD502": {"key": "carrier", "description": "SCAC Carrier Code"},
        "TD505": {"key": "routing", "description": "Routing Instructions"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N301": {"key": "address_line1", "description": "Address Line 1"},
        "N401": {"key": "city", "description": "City Name"},
        "N402": {"key": "state", "description": "State/Province Code"},
        "N403": {"key": "zip", "description": "Postal Code"},
        "N1_BY": {"key": "buyer", "description": "Buyer"},
        "N1_ST": {"key": "ship_to", "description": "Ship To"},
        "N1_VN": {"key": "vendor", "description": "Vendor"},
        "N1_BT": {"key": "bill_to", "description": "Bill To"},
        # Line Item Information (table)
        "PO101": {"key": "line_number", "description": "Line Item Number"},
        "PO107_UP": {"key": "upc", "description": "UPC Consumer Package Code"},
        "PO107_PI": {"key": "product_id", "description": "Purchaser's Item Code"},
        "PO107_VN": {"key": "vendor_style", "description": "Vendor's Item Number"},
        "PO107_SK": {"key": "sku", "description": "SKU Number"},
        "PID05": {"key": "description", "description": "Product Description"},
        "PO401": {"key": "pack", "description": "Pack Quantity"},
        "PO102": {"key": "quantity", "description": "Quantity Ordered"},
        "PO103": {"key": "unit", "description": "Unit of Measure"},
        "PO104": {"key": "unit_price", "description": "Unit Price"},
        "CALC": {"key": "total", "description": "Line Total (Calculated)"},
        # Summary
        "CTT01": {"key": "total_line_items", "description": "Total Line Items"},
        "CTT02": {"key": "calculated_total", "description": "Calculated Total Amount"},
    },
    "852": {
        # Report Information
        "XQ01": {"key": "report_type", "description": "Report Type Code"},
        "XQ02": {"key": "report_date", "description": "Report Date"},
        "XQ03": {"key": "report_id", "description": "Report ID"},
        "DTM02_090": {"key": "report_start_date", "description": "Report Start Date"},
        "DTM02_091": {"key": "report_end_date", "description": "Report End Date"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        # Activity Items (table)
        "LIN_LINE": {"key": "line_number", "description": "Line Item Number"},
        "LIN02": {"key": "product_id", "description": "Product ID Code"},
        "PID05": {"key": "description", "description": "Product Description"},
        "QTY02_QS": {"key": "quantity_sold", "description": "Quantity Sold"},
        "QTY02_QA": {"key": "quantity_on_hand", "description": "Quantity on Hand"},
        "CTP03": {"key": "unit_price", "description": "Unit Price"},
        "AMT02": {"key": "sales_amount", "description": "Sales Amount"},
        "UIT01": {"key": "unit", "description": "Unit of Measure"},
        "CALC": {"key": "total", "description": "Line Total (Calculated)"},
    },
    "855": {
        # Acknowledgment Information
        "BAK01": {"key": "purpose_code", "description": "Transaction Purpose"},
        "BAK02": {"key": "acknowledgment_type", "description": "Acknowledgment Type"},
        "BAK03": {"key": "po_number", "description": "PO Number"},
        "BAK04": {"key": "po_date", "description": "PO Date"},
        "BAK09": {"key": "acknowledgment_date", "description": "Acknowledgment Date"},
        "DTM02_010": {"key": "estimated_ship_date", "description": "Estimated Ship Date"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N301": {"key": "address_line1", "description": "Address Line 1"},
        "N401": {"key": "city", "description": "City Name"},
        "N402": {"key": "state", "description": "State/Province Code"},
        "N403": {"key": "zip", "description": "Postal Code"},
        "N1_BY": {"key": "buyer", "description": "Buyer"},
        "N1_ST": {"key": "ship_to", "description": "Ship To"},
        "N1_SE": {"key": "seller", "description": "Seller"},
        # Line Items (table)
        "PO101": {"key": "line_number", "description": "Line Item Number"},
        "PO107": {"key": "product_id", "description": "Product ID"},
        "PID05": {"key": "description", "description": "Product Description"},
        "PO102": {"key": "quantity", "description": "Quantity Ordered"},
        "PO103": {"key": "unit", "description": "Unit of Measure"},
        "PO104": {"key": "unit_price", "description": "Unit Price"},
        "ACK01": {"key": "status", "description": "Line Item Status"},
        "ACK02": {"key": "quantity_acknowledged", "description": "Quantity Acknowledged"},
        "ACK05": {"key": "ship_date", "description": "Ship Date"},
        # Summary
        "CTT01": {"key": "total_line_items", "description": "Total Line Items"},
    },
    "856": {
        # Shipment Information
        "BSN01": {"key": "purpose_code", "description": "Transaction Purpose"},
        "BSN02": {"key": "shipment_id", "description": "Shipment Identification"},
        "BSN03": {"key": "shipment_date", "description": "Shipment Date"},
        "BSN04": {"key": "shipment_time", "description": "Shipment Time"},
        # Carrier Details
        "TD101": {"key": "lading_quantity", "description": "Lading Quantity"},
        "TD106": {"key": "weight", "description": "Weight"},
        "TD302": {"key": "equipment_number", "description": "Equipment Number"},
        "TD308": {"key": "seal_number", "description":": Seal Number"},
        "TD502": {"key": "carrier_code", "description": "SCAC Carrier Code"},
        "TD504": {"key": "transport_method", "description": "Transport Method"},
        "TD505": {"key": "routing", "description": "Routing"},
        # References
        "REF01": {"key": "type", "description": "Reference Qualifier"},
        "REF02": {"key": "value", "description": "Reference Value"},
        "REF02_CN": {"key": "pro_number", "description": "PRO Number"},
        "REF02_BM": {"key": "bill_of_lading", "description": "Bill of Lading"},
        "REF02_PK": {"key": "tracking_number", "description": "Tracking Number"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N301": {"key": "address_line1", "description": "Address Line 1"},
        "N401": {"key": "city", "description": "City Name"},
        "N402": {"key": "state", "description": "State/Province Code"},
        "N403": {"key": "zip", "description": "Postal Code"},
        "N1_SF": {"key": "ship_from", "description": "Ship From"},
        "N1_ST": {"key": "ship_to", "description": "Ship To"},
        # Hierarchy / Item Details
        "HL01": {"key": "hl_id", "description": "Hierarchy Level ID"},
        "HL03": {"key": "level", "description": "Hierarchy Level"},
        "PRF01": {"key": "po_number", "description": "PO Number"},
        "LIN02": {"key": "product_id", "description": "Product ID"},
        "PID05": {"key": "description", "description": "Product Description"},
        "SN102": {"key": "quantity_shipped", "description": "Quantity Shipped"},
        "MAN02": {"key": "sscc", "description": "SSCC/UCC-128"},
        # Summary
        "CTT01": {"key": "total_line_items", "description": "Total Line Items"},
    },
    "860": {
        # Change Request Information
        "BCH01": {"key": "purpose", "description": "Transaction Purpose"},
        "BCH02": {"key": "po_type_code", "description": "PO Type Code"},
        "BCH03": {"key": "po_number", "description": "Purchase Order Number"},
        "BCH05": {"key": "change_sequence", "description": "Change Sequence Number"},
        "BCH06": {"key": "change_date", "description": "Change Request Date"},
        "DTM02_002": {"key": "requested_delivery", "description": "Requested Delivery Date"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N1_BY": {"key": "buyer", "description": "Buyer"},
        "N1_ST": {"key": "ship_to", "description": "Ship To"},
        # Change Items (table)
        "POC01": {"key": "line_number", "description": "Line Item Number"},
        "POC02": {"key": "change_type", "description": "Change Type Code"},
        "LIN02": {"key": "product_id", "description": "Product ID"},
        "PID05": {"key": "description", "description": "Product Description"},
        "POC03": {"key": "new_quantity", "description": "New Quantity"},
        "POC05": {"key": "unit", "description": "Unit of Measure"},
        "POC06": {"key": "unit_price", "description": "Unit Price"},
        "CALC": {"key": "total", "description": "Line Total (Calculated)"},
        # Summary
        "CTT01": {"key": "total_line_items", "description": "Total Line Items"},
    },
    "861": {
        # Receipt Information
        "BRA01": {"key": "receiving_advice_number", "description": "Receiving Advice Number"},
        "BRA02": {"key": "date", "description": "Receipt Date"},
        "BRA03": {"key": "purpose", "description": "Transaction Purpose"},
        "BRA06": {"key": "condition", "description": "Receiving Condition Code"},
        "BRA07": {"key": "action", "description": "Action Code"},
        "REF02_PO": {"key": "po_number", "description": "PO Number"},
        "REF02_BM": {"key": "bill_of_lading", "description": "Bill of Lading"},
        "TD106": {"key": "weight", "description": "Weight"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N1_SF": {"key": "ship_from", "description": "Ship From"},
        "N1_ST": {"key": "ship_to", "description": "Ship To"},
        # Receipt Items (table)
        "RCD_LINE": {"key": "line_number", "description": "Line Item Number"},
        "LIN02": {"key": "product_id", "description": "Product ID"},
        "PID05": {"key": "description", "description": "Product Description"},
        "RCD05": {"key": "quantity_received", "description": "Quantity Received"},
        "RCD07": {"key": "quantity_damaged", "description": "Quantity Damaged"},
        "RCD01": {"key": "quantity_in_question", "description": "Quantity in Question"},
        "RCD03": {"key": "condition", "description": "Item Condition Code"},
        "UIT01": {"key": "unit", "description": "Unit of Measure"},
        # Summary
        "CTT01": {"key": "total_line_items", "description": "Total Line Items"},
    },
    "864": {
        # Message Information
        "BMG01": {"key": "purpose", "description": "Transaction Purpose"},
        "BMG02": {"key": "subject", "description": "Message Subject"},
        "DTM02_097": {"key": "date", "description": "Message Date"},
        "MIT01": {"key": "reference_id", "description": "Message Reference ID"},
        # Parties
        "N1_FR": {"key": "from", "description": "Sender"},
        "N1_TO": {"key": "to", "description": "Recipient"},
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        # Message Content
        "MSG01": {"key": "text", "description": "Message Text"},
        "MTX02": {"key": "content", "description": "Text Content"},
    },
    "870": {
        # Report Information
        "BSR01": {"key": "status_report", "description": "Status Report Code"},
        "BSR02": {"key": "report_id", "description": "Report ID"},
        "BSR03": {"key": "report_date", "description": "Report Date"},
        "BSR06": {"key": "purpose", "description": "Transaction Purpose"},
        "PRF01": {"key": "po_number", "description": "PO Number"},
        "PRF04": {"key": "po_date", "description": "PO Date"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        # Status Items (table)
        "ISR_LINE": {"key": "line_number", "description": "Line Item Number"},
        "LIN02": {"key": "product_id", "description": "Product ID"},
        "PID05": {"key": "description", "description": "Product Description"},
        "ISR01": {"key": "status", "description": "Item Status Code"},
        "ISR02": {"key": "quantity", "description": "Quantity"},
        "ISR03": {"key": "status_date", "description": "Status Date"},
        "QTY02_01": {"key": "quantity_ordered", "description": "Quantity Ordered"},
        "QTY02_02": {"key": "quantity_shipped", "description": "Quantity Shipped"},
        "UIT01": {"key": "unit", "description": "Unit of Measure"},
    },
    "875": {
        # Order Information
        "G5001": {"key": "order_status_code", "description": "Order Status Code"},
        "G5002": {"key": "po_date", "description": "PO Date"},
        "G5003": {"key": "po_number", "description": "PO Number"},
        "G5004": {"key": "ship_date", "description": "Ship Date"},
        "G5006": {"key": "order_type", "description": "Order Type"},
        "G6102": {"key": "contact_name", "description": "Contact Name"},
        "G6202_02": {"key": "delivery_date", "description": "Delivery Date"},
        "G6601": {"key": "shipment_type", "description": "Shipment Type"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N301": {"key": "address_line1", "description": "Address Line 1"},
        "N1_BY": {"key": "buyer", "description": "Buyer"},
        "N1_ST": {"key": "ship_to", "description": "Ship To"},
        "N1_VN": {"key": "vendor", "description": "Vendor"},
        # Line Items (table)
        "G68_LINE": {"key": "line_number", "description": "Line Item Number"},
        "G6804": {"key": "product_id", "description": "UPC Case Code"},
        "G6901": {"key": "description", "description": "Product Description"},
        "G6801": {"key": "quantity", "description": "Quantity Ordered"},
        "CALC_UNIT": {"key": "unit", "description": "Unit of Measure"},
        "G6803": {"key": "unit_price", "description": "Unit Price"},
        "CALC": {"key": "total", "description": "Line Total (Calculated)"},
        # Summary
        "G7601": {"key": "total_line_items", "description": "Total Line Items"},
        "G7602": {"key": "total_quantity", "description": "Total Quantity"},
        "G7605": {"key": "total_amount", "description": "Total Amount"},
    },
    "880": {
        # Invoice Information
        "G0101": {"key": "invoice_date", "description": "Invoice Date"},
        "G0102": {"key": "invoice_number", "description": "Invoice Number"},
        "G0103": {"key": "po_date", "description": "PO Date"},
        "G0104": {"key": "po_number", "description": "PO Number"},
        "G0105": {"key": "ship_date", "description": "Ship Date"},
        "G0107": {"key": "vendor_order_number", "description": "Vendor Order Number"},
        # Entities & Parties (table)
        "N101": {"key": "type", "description": "Entity Identifier Code"},
        "N102": {"key": "name", "description": "Party Name"},
        "N104": {"key": "id", "description": "Party Identification Code"},
        "N301": {"key": "address_line1", "description": "Address Line 1"},
        "N1_SE": {"key": "seller", "description": "Seller"},
        "N1_BY": {"key": "buyer", "description": "Buyer"},
        "N1_ST": {"key": "ship_to", "description": "Ship To"},
        # Line Items (table)
        "G17_LINE": {"key": "line_number", "description": "Line Item Number"},
        "G1704": {"key": "product_id", "description": "UPC Case Code"},
        "G20_DESC": {"key": "description", "description": "Product Description"},
        "G1701": {"key": "quantity", "description": "Quantity Invoiced"},
        "CALC_UNIT": {"key": "unit", "description": "Unit of Measure"},
        "G1703": {"key": "unit_price", "description": "Unit Price"},
        "CALC": {"key": "total", "description": "Line Total (Calculated)"},
        # Summary
        "G3101": {"key": "total_line_items", "description": "Total Line Items"},
        "G3102": {"key": "total_quantity", "description": "Total Quantity"},
        "G3301": {"key": "total_invoice_amount", "description": "Total Invoice Amount"},
    },
    "997": {
        # Acknowledgment Summary
        "AK101": {"key": "functional_id_code", "description": "Functional Identifier Code"},
        "AK102": {"key": "group_control_number", "description": "Group Control Number"},
        "AK103": {"key": "version", "description": "Version/Release Code"},
        "AK901": {"key": "acknowledgment_status", "description": "Group Acknowledgment Status"},
        "AK902": {"key": "sets_included", "description": "Number of Sets Included"},
        "AK903": {"key": "sets_received", "description": "Number of Sets Received"},
        "AK904": {"key": "sets_accepted", "description": "Number of Sets Accepted"},
        # Transaction Details (table)
        "AK201": {"key": "transaction_set_id", "description": "Transaction Set Identifier"},
        "AK202": {"key": "control_number", "description": "Transaction Control Number"},
        "AK501": {"key": "status", "description": "Transaction Set Status"},
        # Error Details
        "AK301": {"key": "segment_id", "description": "Error Segment ID"},
        "AK302": {"key": "segment_position", "description": "Segment Position in Set"},
        "AK304": {"key": "segment_error", "description": "Segment Error Code"},
        "AK401": {"key": "element_position", "description": "Element Position"},
        "AK403": {"key": "element_error", "description": "Data Element Error"},
        "AK404": {"key": "bad_value", "description": "Bad Data Value"},
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
