"""
EDI 860 - Purchase Order Change Request Parser.
Request changes to existing purchase orders.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 860-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "05": "Replace",
}

CHANGE_TYPE_CODES = {
    "AI": "Add",
    "CA": "Changes All Items",
    "CT": "Change Order Total Only",
    "DI": "Delete Item",
    "PC": "Price Change",
    "QC": "Quantity Change",
    "QI": "Quantity Increase",
    "QD": "Quantity Decrease",
    "RD": "Request Delivery Date Change",
    "RZ": "Reinstate",
    "ZZ": "Mutually Defined",
}

PARTY_TYPE_CODES = {
    "BY": "Buying Party (Purchaser)",
    "SE": "Selling Party",
    "ST": "Ship To",
    "BT": "Bill To",
    "VN": "Vendor",
}

PRODUCT_ID_QUALIFIERS = {
    "PI": "Purchaser's Item Code",
    "VN": "Vendor's (Seller's) Part Number",
    "UP": "U.P.C. Consumer Package Code",
    "BP": "Buyer's Part Number",
}


class EDI860Parser(BaseEDIParser):
    """Parser for EDI 860 Purchase Order Change Request documents."""
    
    TRANSACTION_TYPE = "860"
    TRANSACTION_NAME = "Purchase Order Change Request"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 860 PO Change Request segments."""
        
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
        
        # Parse BCH (Beginning Segment for Purchase Order Change)
        bch = self.get_segment_by_id(segments, "BCH")
        if bch:
            elements = bch["elements"]
            
            # BCH01 - Transaction Set Purpose Code
            if len(elements) > 0 and elements[0]:
                purpose = elements[0]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
            
            # BCH02 - Purchase Order Type Code
            if len(elements) > 1 and elements[1]:
                document.header["po_type_code"] = elements[1]
            
            # BCH03 - Purchase Order Number
            if len(elements) > 2 and elements[2]:
                document.header["po_number"] = elements[2]
            
            # BCH04 - Release Number
            if len(elements) > 3 and elements[3]:
                document.header["release_number"] = elements[3]
            
            # BCH05 - Change Order Sequence Number
            if len(elements) > 4 and elements[4]:
                document.header["change_sequence"] = elements[4]
            
            # BCH06 - Date (Change Request Date)
            if len(elements) > 5 and elements[5]:
                document.header["change_date"] = self._format_date(elements[5])
                document.date = document.header["change_date"]
        
        # Parse REF (Reference Identification)
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                document.header["references"].append({
                    "qualifier": ref["elements"][0],
                    "value": ref["elements"][1],
                })
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                date_qualifiers = {
                    "002": "Requested Delivery",
                    "010": "Requested Ship Date",
                    "004": "Original PO Date",
                }
                label = date_qualifiers.get(qualifier, f"Date ({qualifier})")
                document.header["dates"][label] = self._format_date(date_value)
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Parse POC (Line Item Change) segments
        self._parse_line_items(segments, document)
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
        
        return document
    
    def _parse_parties(self, segments: list) -> List[Dict]:
        """Parse party information."""
        parties = []
        
        # Parse all segments first since we need to look ahead
        parsed_segments = [self._parse_segment(s) for s in segments]
        
        n1_indices = []
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "N1":
                n1_indices.append(i)
        
        for idx, n1_idx in enumerate(n1_indices):
            n1 = parsed_segments[n1_idx]
            end_idx = n1_indices[idx + 1] if idx + 1 < len(n1_indices) else len(parsed_segments)
            
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
                if i < len(parsed_segments):
                    if parsed_segments[i]["id"] == "N3":
                        n3 = parsed_segments[i]
                        party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                    elif parsed_segments[i]["id"] == "N4":
                        n4 = parsed_segments[i]
                        party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                        party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                        party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
            
            parties.append(party)
        
        return parties
    
    def _parse_line_items(self, segments: list, document: EDIDocument) -> None:
        """Parse POC (Line Item Change) segments."""
        
        # Parse all segments first since we need to look ahead
        parsed_segments = [self._parse_segment(s) for s in segments]
        
        poc_indices = []
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "POC":
                poc_indices.append(i)
        
        for idx, poc_idx in enumerate(poc_indices):
            poc = parsed_segments[poc_idx]
            end_idx = poc_indices[idx + 1] if idx + 1 < len(poc_indices) else len(parsed_segments)
            
            elements = poc["elements"]
            
            line_item = {
                "line_number": elements[0] if len(elements) > 0 else str(idx + 1),
            }
            
            # POC02 - Line Item Change Type
            if len(elements) > 1 and elements[1]:
                change_type = elements[1]
                line_item["change_type_code"] = change_type
                line_item["change_type"] = CHANGE_TYPE_CODES.get(change_type, change_type)
            
            # POC03 - Quantity Ordered (new quantity)
            if len(elements) > 2 and elements[2]:
                line_item["new_quantity"] = elements[2]
            
            # POC04 - Quantity Left to Receive
            if len(elements) > 3 and elements[3]:
                line_item["quantity_remaining"] = elements[3]
            
            # POC05 - Unit of Measure
            if len(elements) > 4 and elements[4]:
                line_item["unit"] = elements[4]
            
            # POC06 - Unit Price
            if len(elements) > 5 and elements[5]:
                try:
                    line_item["unit_price"] = float(elements[5])
                except:
                    line_item["unit_price"] = elements[5]
            
            # Parse product IDs from POC (starting at element 8)
            product_ids = {}
            i = 8
            while i + 1 < len(elements):
                qualifier = elements[i]
                value = elements[i + 1] if i + 1 < len(elements) else ""
                if qualifier and value:
                    label = PRODUCT_ID_QUALIFIERS.get(qualifier, qualifier)
                    product_ids[label] = value
                i += 2
            
            line_item["product_ids"] = product_ids
            line_item["product_id"] = next(iter(product_ids.values()), None)
            
            # Look for PID (Product Description)
            for i in range(poc_idx + 1, min(end_idx, poc_idx + 10)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "PID":
                    pid = parsed_segments[i]
                    if len(pid["elements"]) > 4 and pid["elements"][4]:
                        line_item["description"] = pid["elements"][4]
                    break
            
            # Look for QTY (Quantity) changes
            for i in range(poc_idx + 1, min(end_idx, poc_idx + 10)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "QTY":
                    qty = parsed_segments[i]
                    elements = qty["elements"]
                    
                    qty_qualifiers = {
                        "01": "Original Quantity",
                        "52": "New Quantity",
                        "83": "Quantity Decrease",
                        "84": "Quantity Increase",
                    }
                    
                    if len(elements) >= 2:
                        qual = elements[0]
                        val = elements[1]
                        label = qty_qualifiers.get(qual, qual)
                        
                        if "quantities" not in line_item:
                            line_item["quantities"] = {}
                        line_item["quantities"][label] = val
            
            document.line_items.append(line_item)
        
        # Summary by change type
        change_counts = {}
        for item in document.line_items:
            ct = item.get("change_type", "Unknown")
            change_counts[ct] = change_counts.get(ct, 0) + 1
        
        document.summary["changes_by_type"] = change_counts
        document.summary["total_changes"] = len(document.line_items)
    
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
