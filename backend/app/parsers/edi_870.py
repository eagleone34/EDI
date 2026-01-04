"""
EDI 870 - Order Status Report Parser.
Report status of orders, forecasts, or requisitions.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 870-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "05": "Replace",
    "11": "Response",
}

STATUS_REPORT_CODES = {
    "A": "Accepted",
    "C": "Complete",
    "D": "Dispatched",
    "I": "In Process",
    "N": "Not Available",
    "O": "Open",
    "P": "Partial",
    "R": "Rejected",
    "S": "Shipped",
    "X": "Canceled",
}

ITEM_STATUS_CODES = {
    "AC": "Accepted",
    "AR": "At Risk",
    "BO": "Backordered",
    "CA": "Canceled",
    "CM": "Complete",
    "DR": "Delivery Rescheduled",
    "IA": "Item Accepted",
    "IB": "Item Backordered",
    "IP": "In Process",
    "IR": "Item Rejected",
    "OH": "On Hold",
    "OP": "Open",
    "PA": "Partially Shipped",
    "RC": "Received",
    "RS": "Rescheduled",
    "SD": "Shipped",
    "SP": "Shipped Partial",
}

PARTY_TYPE_CODES = {
    "BY": "Buyer",
    "SE": "Seller",
    "ST": "Ship To",
    "SF": "Ship From",
    "VN": "Vendor",
}


class EDI870Parser(BaseEDIParser):
    """Parser for EDI 870 Order Status Report documents."""
    
    TRANSACTION_TYPE = "870"
    TRANSACTION_NAME = "Order Status Report"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 870 Order Status Report segments."""
        
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
        
        # Parse BSR (Beginning Segment for Order Status Report)
        bsr = self.get_segment_by_id(segments, "BSR")
        if bsr:
            elements = bsr["elements"]
            
            # BSR01 - Status Report Code
            if len(elements) > 0 and elements[0]:
                code = elements[0]
                document.header["status_report_code"] = code
                document.header["status_report"] = STATUS_REPORT_CODES.get(code, code)
            
            # BSR02 - Reference Identification
            if len(elements) > 1 and elements[1]:
                document.header["report_id"] = elements[1]
            
            # BSR03 - Date
            if len(elements) > 2 and elements[2]:
                document.header["report_date"] = self._format_date(elements[2])
                document.date = document.header["report_date"]
            
            # BSR04 - Action Code
            if len(elements) > 3 and elements[3]:
                document.header["action_code"] = elements[3]
            
            # BSR05 - Time
            if len(elements) > 4 and elements[4]:
                document.header["report_time"] = elements[4]
            
            # BSR06 - Transaction Set Purpose Code
            if len(elements) > 5 and elements[5]:
                purpose = elements[5]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
        
        # Parse REF (Reference Identification)
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                qualifier = ref["elements"][0]
                value = ref["elements"][1]
                
                ref_qualifiers = {
                    "PO": "Purchase Order Number",
                    "CO": "Customer Order Number",
                    "VN": "Vendor Order Number",
                    "IV": "Invoice Number",
                }
                
                document.header["references"].append({
                    "qualifier": qualifier,
                    "qualifier_desc": ref_qualifiers.get(qualifier, qualifier),
                    "value": value,
                })
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Parse HL (Hierarchical Level) / PRF / ISR loops
        self._parse_status_items(segments, document)
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
        
        return document
    
    def _parse_parties(self, segments: list) -> List[Dict]:
        """Parse party information."""
        parties = []
        
        n1_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "N1":
                n1_indices.append(i)
        
        for idx, n1_idx in enumerate(n1_indices):
            n1 = segments[n1_idx]
            end_idx = n1_indices[idx + 1] if idx + 1 < len(n1_indices) else len(segments)
            
            party_code = n1["elements"][0] if len(n1["elements"]) > 0 else None
            
            party = {
                "type_code": party_code,
                "type": PARTY_TYPE_CODES.get(party_code, party_code),
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
                "id_qualifier": n1["elements"][2] if len(n1["elements"]) > 2 else None,
                "id": n1["elements"][3] if len(n1["elements"]) > 3 else None,
            }
            
            # Look for N3/N4
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments):
                    if segments[i]["id"] == "N3":
                        n3 = segments[i]
                        party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                    elif segments[i]["id"] == "N4":
                        n4 = segments[i]
                        party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                        party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                        party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
            
            parties.append(party)
        
        return parties
    
    def _parse_status_items(self, segments: list, document: EDIDocument) -> None:
        """Parse HL/PRF/ISR loops for order status items."""
        
        # Find PRF (Purchase Order Reference) segments
        prf_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "PRF":
                prf_indices.append(i)
        
        # If no PRF, try ISR (Item Status Report) segments
        isr_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "ISR":
                isr_indices.append(i)
        
        status_counts = {}
        
        if prf_indices:
            for idx, prf_idx in enumerate(prf_indices):
                prf = segments[prf_idx]
                end_idx = prf_indices[idx + 1] if idx + 1 < len(prf_indices) else len(segments)
                
                line_item = {
                    "line_number": str(len(document.line_items) + 1),
                }
                
                # PRF01 - PO Number
                if len(prf["elements"]) > 0 and prf["elements"][0]:
                    line_item["po_number"] = prf["elements"][0]
                
                # PRF04 - PO Date
                if len(prf["elements"]) > 3 and prf["elements"][3]:
                    line_item["po_date"] = self._format_date(prf["elements"][3])
                
                # Look for ISR within this loop
                for i in range(prf_idx + 1, min(end_idx, prf_idx + 15)):
                    if i < len(segments) and segments[i]["id"] == "ISR":
                        isr = segments[i]
                        elements = isr["elements"]
                        
                        # ISR01 - Item Status Code
                        if len(elements) > 0 and elements[0]:
                            status = elements[0]
                            line_item["status_code"] = status
                            line_item["status"] = ITEM_STATUS_CODES.get(status, status)
                            status_counts[line_item["status"]] = status_counts.get(line_item["status"], 0) + 1
                        
                        # ISR02 - Quantity
                        if len(elements) > 1 and elements[1]:
                            line_item["quantity"] = elements[1]
                        
                        # ISR03 - Date
                        if len(elements) > 2 and elements[2]:
                            line_item["status_date"] = self._format_date(elements[2])
                        
                        break
                
                # Look for QTY (Quantity Information)
                for i in range(prf_idx + 1, min(end_idx, prf_idx + 15)):
                    if i < len(segments) and segments[i]["id"] == "QTY":
                        qty = segments[i]
                        elements = qty["elements"]
                        
                        qty_qualifiers = {
                            "01": "Ordered",
                            "02": "Shipped",
                            "21": "Backordered",
                            "39": "Open",
                        }
                        
                        if len(elements) >= 2:
                            qual = elements[0]
                            val = elements[1]
                            
                            if "quantities" not in line_item:
                                line_item["quantities"] = {}
                            
                            label = qty_qualifiers.get(qual, qual)
                            line_item["quantities"][label] = val
                
                # Look for PID (Product Description)
                for i in range(prf_idx + 1, min(end_idx, prf_idx + 15)):
                    if i < len(segments) and segments[i]["id"] == "PID":
                        pid = segments[i]
                        if len(pid["elements"]) > 4 and pid["elements"][4]:
                            line_item["description"] = pid["elements"][4]
                        break
                
                document.line_items.append(line_item)
        
        elif isr_indices:
            # ISR segments without PRF wrapper
            for idx, isr_idx in enumerate(isr_indices):
                isr = segments[isr_idx]
                elements = isr["elements"]
                
                line_item = {
                    "line_number": str(len(document.line_items) + 1),
                }
                
                # ISR01 - Item Status Code
                if len(elements) > 0 and elements[0]:
                    status = elements[0]
                    line_item["status_code"] = status
                    line_item["status"] = ITEM_STATUS_CODES.get(status, status)
                    status_counts[line_item["status"]] = status_counts.get(line_item["status"], 0) + 1
                
                # ISR02 - Quantity
                if len(elements) > 1 and elements[1]:
                    line_item["quantity"] = elements[1]
                
                # ISR03 - Date
                if len(elements) > 2 and elements[2]:
                    line_item["status_date"] = self._format_date(elements[2])
                
                document.line_items.append(line_item)
        
        # Summary
        document.summary["total_items"] = len(document.line_items)
        document.summary["status_breakdown"] = status_counts
    
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
