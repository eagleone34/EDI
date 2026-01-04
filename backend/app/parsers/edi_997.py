"""
EDI 997 - Functional Acknowledgment Parser (Enhanced).
Complete acknowledgment details with error reporting.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 997-specific codes
ACKNOWLEDGMENT_STATUS_CODES = {
    "A": "Accepted",
    "E": "Accepted, But Errors Were Noted",
    "M": "Rejected, Message Authentication Code (MAC) Failed",
    "P": "Partially Accepted",
    "R": "Rejected",
    "W": "Rejected, Assurance Failed Validity Tests",
    "X": "Rejected, Content After Decryption Could Not Be Analyzed",
}

TRANSACTION_SET_STATUS_CODES = {
    "A": "Accepted",
    "E": "Accepted, But Errors Were Noted",
    "M": "Rejected, Message Authentication Code (MAC) Failed",
    "P": "Partially Accepted",
    "R": "Rejected",
    "W": "Rejected, Assurance Failed Validity Tests",
    "X": "Rejected, Content After Decryption Could Not Be Analyzed",
}

SEGMENT_ERROR_CODES = {
    "1": "Unrecognized Segment ID",
    "2": "Unexpected Segment",
    "3": "Mandatory Segment Missing",
    "4": "Loop Occurs Over Maximum Times",
    "5": "Segment Exceeds Maximum Use",
    "6": "Segment Not in Defined Transaction Set",
    "7": "Segment Not in Proper Sequence",
    "8": "Segment Has Data Element Errors",
}

DATA_ELEMENT_ERROR_CODES = {
    "1": "Mandatory Data Element Missing",
    "2": "Conditional Required Data Element Missing",
    "3": "Too Many Data Elements",
    "4": "Data Element Too Short",
    "5": "Data Element Too Long",
    "6": "Invalid Character in Data Element",
    "7": "Invalid Code Value",
    "8": "Invalid Date",
    "9": "Invalid Time",
    "10": "Exclusion Condition Violated",
}

FUNCTIONAL_ID_CODES = {
    "PO": "Purchase Order (850)",
    "PR": "Purchase Order Acknowledgment (855)",
    "SH": "Ship Notice/Manifest (856)",
    "IN": "Invoice (810)",
    "FA": "Functional Acknowledgment (997)",
    "PS": "Planning Schedule (830)",
    "RS": "Order Status (870)",
    "RC": "Receiving Advice (861)",
    "CD": "Credit/Debit Adjustment (812)",
    "PC": "Purchase Order Change (860)",
}


class EDI997Parser(BaseEDIParser):
    """Parser for EDI 997 Functional Acknowledgment documents."""
    
    TRANSACTION_TYPE = "997"
    TRANSACTION_NAME = "Functional Acknowledgment"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 997 Functional Acknowledgment segments."""
        
        document = EDIDocument(
            transaction_type=self.TRANSACTION_TYPE,
            transaction_name=self.TRANSACTION_NAME,
        )
        
        # Parse ISA
        isa = self.get_segment_by_id(segments, "ISA")
        if isa and len(isa["elements"]) >= 12:
            document.sender_id = isa["elements"][5].strip() if len(isa["elements"]) > 5 else None
            document.receiver_id = isa["elements"][7].strip() if len(isa["elements"]) > 7 else None
            document.control_number = isa["elements"][12].strip() if len(isa["elements"]) > 12 else None
            
            # Extract date
            if len(isa["elements"]) > 8:
                date_str = isa["elements"][8].strip()
                if len(date_str) == 6:
                    document.date = f"20{date_str[:2]}/{date_str[2:4]}/{date_str[4:6]}"
        
        # Parse AK1 (Functional Group Response Header)
        ak1 = self.get_segment_by_id(segments, "AK1")
        if ak1:
            elements = ak1["elements"]
            
            # AK101 - Functional Identifier Code
            if len(elements) > 0 and elements[0]:
                func_id = elements[0]
                document.header["functional_id_code"] = func_id
                document.header["functional_id"] = FUNCTIONAL_ID_CODES.get(func_id, func_id)
            
            # AK102 - Group Control Number
            if len(elements) > 1 and elements[1]:
                document.header["group_control_number"] = elements[1]
            
            # AK103 - Version/Release/Industry Code
            if len(elements) > 2 and elements[2]:
                document.header["version"] = elements[2]
        
        # Parse AK2/AK3/AK4/AK5 loops (Transaction Set Response)
        self._parse_transaction_responses(segments, document)
        
        # Parse AK9 (Functional Group Response Trailer)
        ak9 = self.get_segment_by_id(segments, "AK9")
        if ak9:
            elements = ak9["elements"]
            
            # AK901 - Functional Group Acknowledge Code
            if len(elements) > 0 and elements[0]:
                status = elements[0]
                document.header["acknowledgment_code"] = status
                document.header["acknowledgment_status"] = ACKNOWLEDGMENT_STATUS_CODES.get(status, status)
            
            # AK902 - Number of Transaction Sets Included
            if len(elements) > 1 and elements[1]:
                document.summary["sets_included"] = elements[1]
            
            # AK903 - Number of Received Transaction Sets
            if len(elements) > 2 and elements[2]:
                document.summary["sets_received"] = elements[2]
            
            # AK904 - Number of Accepted Transaction Sets
            if len(elements) > 3 and elements[3]:
                document.summary["sets_accepted"] = elements[3]
            
            # Calculate rejected
            try:
                received = int(document.summary.get("sets_received", 0))
                accepted = int(document.summary.get("sets_accepted", 0))
                document.summary["sets_rejected"] = received - accepted
            except:
                pass
            
            # AK905-AK909 - Error codes
            error_codes = []
            for i in range(4, min(len(elements), 9)):
                if elements[i]:
                    error_codes.append(elements[i])
            
            if error_codes:
                document.summary["group_error_codes"] = error_codes
        
        return document
    
    def _parse_transaction_responses(self, segments: list, document: EDIDocument) -> None:
        """Parse AK2/AK3/AK4/AK5 loops for transaction set responses."""
        
        # Find all AK2 segment indices
        ak2_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "AK2":
                ak2_indices.append(i)
        
        for idx, ak2_idx in enumerate(ak2_indices):
            ak2 = segments[ak2_idx]
            
            # Determine loop end
            end_idx = ak2_indices[idx + 1] if idx + 1 < len(ak2_indices) else len(segments)
            
            transaction = {
                "transaction_set_id": ak2["elements"][0] if len(ak2["elements"]) > 0 else None,
                "control_number": ak2["elements"][1] if len(ak2["elements"]) > 1 else None,
            }
            
            # Map transaction set ID
            ts_id = transaction.get("transaction_set_id")
            ts_names = {
                "810": "Invoice",
                "812": "Credit/Debit Adjustment",
                "850": "Purchase Order",
                "855": "PO Acknowledgment",
                "856": "Ship Notice",
                "830": "Planning Schedule",
                "860": "PO Change",
                "861": "Receiving Advice",
                "870": "Order Status",
                "997": "Functional Acknowledgment",
            }
            transaction["transaction_name"] = ts_names.get(ts_id, ts_id)
            
            # Collect errors from AK3/AK4
            segment_errors = []
            element_errors = []
            
            for i in range(ak2_idx + 1, end_idx):
                seg = segments[i]
                
                if seg["id"] == "AK3":  # Segment Error
                    elements = seg["elements"]
                    error = {
                        "segment_id": elements[0] if len(elements) > 0 else None,
                        "segment_position": elements[1] if len(elements) > 1 else None,
                        "loop_id": elements[2] if len(elements) > 2 else None,
                    }
                    
                    if len(elements) > 3 and elements[3]:
                        error_code = elements[3]
                        error["error_code"] = error_code
                        error["error_description"] = SEGMENT_ERROR_CODES.get(error_code, error_code)
                    
                    segment_errors.append(error)
                
                elif seg["id"] == "AK4":  # Data Element Error
                    elements = seg["elements"]
                    error = {
                        "position": elements[0] if len(elements) > 0 else None,
                        "element_reference": elements[1] if len(elements) > 1 else None,
                    }
                    
                    if len(elements) > 2 and elements[2]:
                        error_code = elements[2]
                        error["error_code"] = error_code
                        error["error_description"] = DATA_ELEMENT_ERROR_CODES.get(error_code, error_code)
                    
                    if len(elements) > 3 and elements[3]:
                        error["bad_value"] = elements[3]
                    
                    element_errors.append(error)
                
                elif seg["id"] == "AK5":  # Transaction Set Response Trailer
                    elements = seg["elements"]
                    
                    if len(elements) > 0 and elements[0]:
                        status = elements[0]
                        transaction["status_code"] = status
                        transaction["status"] = TRANSACTION_SET_STATUS_CODES.get(status, status)
                    
                    # Error codes
                    ts_error_codes = []
                    for j in range(1, min(len(elements), 6)):
                        if elements[j]:
                            ts_error_codes.append(elements[j])
                    
                    if ts_error_codes:
                        transaction["error_codes"] = ts_error_codes
            
            if segment_errors:
                transaction["segment_errors"] = segment_errors
            if element_errors:
                transaction["element_errors"] = element_errors
            
            # Add as line item for display
            line_item = {
                "line_number": str(len(document.line_items) + 1),
                "transaction_set": transaction.get("transaction_set_id"),
                "transaction_name": transaction.get("transaction_name"),
                "control_number": transaction.get("control_number"),
                "status": transaction.get("status"),
                "status_code": transaction.get("status_code"),
                "error_count": len(segment_errors) + len(element_errors),
            }
            
            if segment_errors:
                line_item["segment_errors"] = segment_errors
            if element_errors:
                line_item["element_errors"] = element_errors
            
            document.line_items.append(line_item)
        
        # Summary counts
        accepted = sum(1 for item in document.line_items if item.get("status_code") == "A")
        rejected = sum(1 for item in document.line_items if item.get("status_code") == "R")
        with_errors = sum(1 for item in document.line_items if item.get("status_code") == "E")
        
        if document.line_items:
            document.summary["transactions_acknowledged"] = len(document.line_items)
            document.summary["accepted"] = accepted
            document.summary["rejected"] = rejected
            document.summary["accepted_with_errors"] = with_errors
