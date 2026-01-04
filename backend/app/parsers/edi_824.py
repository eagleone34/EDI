"""
EDI 824 - Application Advice Parser.
Accept/reject transactions with error details.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 824-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "11": "Response",
}

APPLICATION_ACK_CODES = {
    "TA": "Transaction Set Accept",
    "TR": "Transaction Set Reject",
    "TE": "Transaction Set Accept with Errors",
    "TP": "Transaction Set Partially Accepted",
}

REPORT_TYPE_CODES = {
    "CO": "Confirmation",
    "DR": "Detail Report",
    "ER": "Error Report",
    "NO": "Notice",
    "RJ": "Rejection",
    "SD": "Status Detail",
    "SR": "Status Report",
}

ERROR_CONDITION_CODES = {
    "001": "Authorization Required",
    "002": "Invalid Record",
    "003": "Missing Data",
    "004": "Duplicate Record",
    "005": "Date Error",
    "006": "Invalid Code Value",
    "007": "Reference Not Found",
    "008": "Quantity Error",
    "009": "Price Error",
    "ZZZ": "Mutually Defined",
}


class EDI824Parser(BaseEDIParser):
    """Parser for EDI 824 Application Advice documents."""
    
    TRANSACTION_TYPE = "824"
    TRANSACTION_NAME = "Application Advice"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 824 Application Advice segments."""
        
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
        
        # Parse BGN (Beginning Segment)
        bgn = self.get_segment_by_id(segments, "BGN")
        if bgn:
            elements = bgn["elements"]
            
            # BGN01 - Transaction Set Purpose Code
            if len(elements) > 0 and elements[0]:
                purpose = elements[0]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
            
            # BGN02 - Reference Identification
            if len(elements) > 1 and elements[1]:
                document.header["reference_id"] = elements[1]
            
            # BGN03 - Date
            if len(elements) > 2 and elements[2]:
                document.header["date"] = self._format_date(elements[2])
                document.date = document.header["date"]
            
            # BGN04 - Time
            if len(elements) > 3 and elements[3]:
                document.header["time"] = elements[3]
        
        # Parse N1 (Party Identification)
        n1_segments = self.get_all_segments_by_id(segments, "N1")
        document.header["parties"] = []
        for n1 in n1_segments:
            party = {
                "type_code": n1["elements"][0] if len(n1["elements"]) > 0 else None,
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
                "id_qualifier": n1["elements"][2] if len(n1["elements"]) > 2 else None,
                "id": n1["elements"][3] if len(n1["elements"]) > 3 else None,
            }
            document.header["parties"].append(party)
        
        # Parse OTI (Original Transaction Identification)
        oti_segments = self.get_all_segments_by_id(segments, "OTI")
        
        for oti in oti_segments:
            elements = oti["elements"]
            
            line_item = {
                "line_number": str(len(document.line_items) + 1),
            }
            
            # OTI01 - Application Acknowledgment Code
            if len(elements) > 0 and elements[0]:
                code = elements[0]
                line_item["acknowledgment_code"] = code
                line_item["acknowledgment_status"] = APPLICATION_ACK_CODES.get(code, code)
            
            # OTI02 - Reference Identification Qualifier
            if len(elements) > 1 and elements[1]:
                line_item["reference_qualifier"] = elements[1]
            
            # OTI03 - Reference Identification
            if len(elements) > 2 and elements[2]:
                line_item["reference_id"] = elements[2]
            
            # OTI04 - Application Sender's Code
            if len(elements) > 3 and elements[3]:
                line_item["sender_code"] = elements[3]
            
            # OTI05 - Application Receiver's Code
            if len(elements) > 4 and elements[4]:
                line_item["receiver_code"] = elements[4]
            
            # OTI06 - Date
            if len(elements) > 5 and elements[5]:
                line_item["date"] = self._format_date(elements[5])
            
            # OTI07 - Time
            if len(elements) > 6 and elements[6]:
                line_item["time"] = elements[6]
            
            # OTI08 - Group Control Number
            if len(elements) > 7 and elements[7]:
                line_item["group_control_number"] = elements[7]
            
            # OTI09 - Transaction Set Control Number
            if len(elements) > 8 and elements[8]:
                line_item["transaction_control_number"] = elements[8]
            
            # OTI10 - Transaction Set Identifier Code
            if len(elements) > 9 and elements[9]:
                ts_id = elements[9]
                line_item["transaction_set_id"] = ts_id
                ts_names = {
                    "810": "Invoice",
                    "850": "Purchase Order",
                    "855": "PO Acknowledgment",
                    "856": "Ship Notice",
                    "820": "Remittance Advice",
                }
                line_item["transaction_set_name"] = ts_names.get(ts_id, ts_id)
            
            document.line_items.append(line_item)
        
        # Parse TED (Technical Error Description)
        ted_segments = self.get_all_segments_by_id(segments, "TED")
        errors = []
        for ted in ted_segments:
            elements = ted["elements"]
            error = {}
            
            # TED01 - Application Error Condition Code
            if len(elements) > 0 and elements[0]:
                code = elements[0]
                error["error_code"] = code
                error["error_description"] = ERROR_CONDITION_CODES.get(code, code)
            
            # TED02 - Free-Form Message
            if len(elements) > 1 and elements[1]:
                error["message"] = elements[1]
            
            errors.append(error)
        
        if errors:
            document.header["errors"] = errors
            # Associate errors with line items if possible
            if document.line_items and len(errors) == len(document.line_items):
                for i, item in enumerate(document.line_items):
                    item["error"] = errors[i]
        
        # Parse NTE (Note/Special Instruction)
        nte_segments = self.get_all_segments_by_id(segments, "NTE")
        notes = []
        for nte in nte_segments:
            if len(nte["elements"]) > 1 and nte["elements"][1]:
                notes.append(nte["elements"][1])
            elif len(nte["elements"]) > 0 and nte["elements"][0]:
                notes.append(nte["elements"][0])
        
        if notes:
            document.header["notes"] = notes
        
        # Summary
        accepted = sum(1 for item in document.line_items if item.get("acknowledgment_code") == "TA")
        rejected = sum(1 for item in document.line_items if item.get("acknowledgment_code") == "TR")
        with_errors = sum(1 for item in document.line_items if item.get("acknowledgment_code") == "TE")
        
        document.summary["total_transactions"] = len(document.line_items)
        document.summary["accepted"] = accepted
        document.summary["rejected"] = rejected
        document.summary["accepted_with_errors"] = with_errors
        document.summary["total_errors"] = len(errors)
        
        return document
    
    def _format_date(self, date_str: str) -> str:
        """Format date from YYYYMMDD to readable format."""
        if not date_str or len(date_str) < 8:
            return date_str
        try:
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{month}/{day}/{year}"
        except:
            return date_str
