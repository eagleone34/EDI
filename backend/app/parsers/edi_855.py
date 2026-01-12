"""
EDI 855 - Purchase Order Acknowledgment Parser (Enhanced).
Comprehensive extraction of PO acknowledgment details.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 855-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "05": "Replace",
    "06": "Confirmation",
    "07": "Duplicate",
}

ACKNOWLEDGMENT_TYPE_CODES = {
    "AC": "Acknowledge - With Detail and Change",
    "AD": "Acknowledge - With Detail, No Change",
    "AE": "Acknowledge - With Exception Detail Only",
    "AK": "Acknowledge - No Detail or Change",
    "AT": "Accepted",
    "RD": "Reject with Detail",
    "RF": "Reject with Exception Detail Only",
    "RJ": "Rejected - No Detail",
    "RO": "Rejected with Counter Offer",
    "ZZ": "Mutually Defined",
}

LINE_ITEM_STATUS_CODES = {
    "IA": "Item Accepted",
    "IB": "Item Backordered",
    "IC": "Item Accepted - Changes Made",
    "ID": "Item Deleted",
    "IF": "Item On Hold",
    "IH": "Item on Hold, Incomplete Description",
    "IP": "Item Accepted - Price Changed",
    "IQ": "Item Accepted - Quantity Changed",
    "IR": "Item Rejected",
    "IS": "Item Accepted - Substitution Made",
    "IW": "Item on Hold - Waiver Required",
}

PARTY_TYPE_CODES = {
    "BY": "Buying Party (Purchaser)",
    "SE": "Selling Party",
    "ST": "Ship To",
    "VN": "Vendor",
    "SU": "Supplier",
}

PRODUCT_ID_QUALIFIERS = {
    "PI": "Purchaser's Item Code",
    "VN": "Vendor's (Seller's) Part Number",
    "UP": "U.P.C. Consumer Package Code",
    "UK": "UPC/EAN Shipping Container Code",
    "BP": "Buyer's Part Number",
    "MG": "Manufacturer's Part Number",
}


class EDI855Parser(BaseEDIParser):
    """Parser for EDI 855 Purchase Order Acknowledgment documents."""
    
    TRANSACTION_TYPE = "855"
    TRANSACTION_NAME = "Purchase Order Acknowledgment"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 855 Purchase Order Acknowledgment segments."""
        
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
        
        # Parse BAK (Beginning Segment for Purchase Order Acknowledgment)
        bak = self.get_segment_by_id(segments, "BAK")
        if bak:
            elements = bak["elements"]
            
            # BAK01 - Transaction Set Purpose Code
            if len(elements) > 0 and elements[0]:
                purpose = elements[0]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
            
            # BAK02 - Acknowledgment Type
            if len(elements) > 1 and elements[1]:
                ack_type = elements[1]
                document.header["acknowledgment_type_code"] = ack_type
                document.header["acknowledgment_type"] = ACKNOWLEDGMENT_TYPE_CODES.get(ack_type, ack_type)
            
            # BAK03 - Purchase Order Number
            if len(elements) > 2 and elements[2]:
                document.header["po_number"] = elements[2]
            
            # BAK04 - Purchase Order Date
            if len(elements) > 3 and elements[3]:
                document.header["po_date"] = self._format_date(elements[3])
                document.date = document.header["po_date"]
            
            # BAK06 - Request Reference Number
            if len(elements) > 5 and elements[5]:
                document.header["request_reference"] = elements[5]
            
            # BAK09 - Acknowledgment Date
            if len(elements) > 8 and elements[8]:
                document.header["acknowledgment_date"] = self._format_date(elements[8])
        
        # Parse CUR (Currency)
        cur = self.get_segment_by_id(segments, "CUR")
        if cur and len(cur["elements"]) > 1:
            document.header["currency"] = cur["elements"][1]
        
        # Parse REF (Reference Identification)
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                document.header["references"].append({
                    "qualifier": ref["elements"][0],
                    "value": ref["elements"][1],
                    "description": ref["elements"][2] if len(ref["elements"]) > 2 else None,
                })
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        date_qualifiers = {
            "002": "Delivery Requested",
            "010": "Requested Ship Date",
            "017": "Estimated Delivery Date",
            "037": "Ship Not Before",
            "038": "Ship Not Later Than",
        }
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                label = date_qualifiers.get(qualifier, f"Date ({qualifier})")
                document.header["dates"][label] = self._format_date(date_value)
                
                # Set estimated ship date specifically
                if qualifier in ["010", "017"]:
                    document.header["estimated_ship_date"] = self._format_date(date_value)
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Parse PO1/ACK line item loops
        self._parse_line_items(segments, document)
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
            if len(ctt["elements"]) > 1:
                document.summary["hash_total"] = ctt["elements"][1]
        
        return document
    
    def _parse_parties(self, segments: list) -> List[Dict]:
        """Parse party loops."""
        parties = []
        n1_segments = self.get_all_segments_by_id(segments, "N1")
        n3_segments = self.get_all_segments_by_id(segments, "N3")
        n4_segments = self.get_all_segments_by_id(segments, "N4")
        
        for i, n1 in enumerate(n1_segments):
            party_code = n1["elements"][0] if len(n1["elements"]) > 0 else None
            
            party = {
                "type_code": party_code,
                "type": PARTY_TYPE_CODES.get(party_code, party_code),
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
                "id_qualifier": n1["elements"][2] if len(n1["elements"]) > 2 else None,
                "id": n1["elements"][3] if len(n1["elements"]) > 3 else None,
            }
            
            # Add address if available
            if i < len(n3_segments):
                n3 = n3_segments[i]
                party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                party["address_line2"] = n3["elements"][1] if len(n3["elements"]) > 1 else None
            
            if i < len(n4_segments):
                n4 = n4_segments[i]
                party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
                party["country"] = n4["elements"][3] if len(n4["elements"]) > 3 else None
            
            parties.append(party)
        
        return parties
    
    def _parse_line_items(self, segments: list, document: EDIDocument) -> None:
        """Parse PO1/ACK line item loops."""
        
        # Parse all segments first since we need to look ahead
        parsed_segments = [self._parse_segment(s) for s in segments]
        
        # Find all PO1 segment indices
        po1_indices = []
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "PO1":
                po1_indices.append(i)
        
        for idx, po1_idx in enumerate(po1_indices):
            po1 = parsed_segments[po1_idx]
            
            # Determine loop end
            end_idx = po1_indices[idx + 1] if idx + 1 < len(po1_indices) else len(parsed_segments)
            
            line_item = {
                "line_number": po1["elements"][0] if len(po1["elements"]) > 0 else str(idx + 1),
                "quantity_ordered": po1["elements"][1] if len(po1["elements"]) > 1 else None,
                "unit": po1["elements"][2] if len(po1["elements"]) > 2 else None,
                "unit_price": po1["elements"][3] if len(po1["elements"]) > 3 else None,
            }
            
            # Calculate line total
            try:
                qty = float(line_item["quantity_ordered"]) if line_item["quantity_ordered"] else 0
                price = float(line_item["unit_price"]) if line_item["unit_price"] else 0
                line_item["total"] = round(qty * price, 2)
            except:
                line_item["total"] = None
            
            # Parse product IDs
            product_ids = {}
            i = 5
            while i + 1 < len(po1["elements"]):
                qualifier = po1["elements"][i] if i < len(po1["elements"]) else ""
                value = po1["elements"][i + 1] if i + 1 < len(po1["elements"]) else ""
                if qualifier and value:
                    label = PRODUCT_ID_QUALIFIERS.get(qualifier, qualifier)
                    product_ids[label] = value
                i += 2
            
            line_item["product_ids"] = product_ids
            line_item["product_id"] = next(iter(product_ids.values()), None) if product_ids else None
            
            # Look for PID (Product Description)
            for i in range(po1_idx + 1, min(end_idx, po1_idx + 10)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "PID":
                    pid = parsed_segments[i]
                    if len(pid["elements"]) > 4 and pid["elements"][4]:
                        line_item["description"] = pid["elements"][4]
                    break
            
            # Look for ACK (Line Item Acknowledgment)
            acknowledgments = []
            for i in range(po1_idx + 1, min(end_idx, po1_idx + 10)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "ACK":
                    ack = parsed_segments[i]
                    ack_entry = {}
                    
                    # ACK01 - Line Item Status Code
                    if len(ack["elements"]) > 0 and ack["elements"][0]:
                        status = ack["elements"][0]
                        ack_entry["status_code"] = status
                        ack_entry["status"] = LINE_ITEM_STATUS_CODES.get(status, status)
                    
                    # ACK02 - Quantity
                    if len(ack["elements"]) > 1 and ack["elements"][1]:
                        ack_entry["quantity_acknowledged"] = ack["elements"][1]
                    
                    # ACK03 - Unit of Measure
                    if len(ack["elements"]) > 2 and ack["elements"][2]:
                        ack_entry["unit"] = ack["elements"][2]
                    
                    # ACK04 - Date/Time Qualifier
                    if len(ack["elements"]) > 3 and ack["elements"][3]:
                        ack_entry["date_qualifier"] = ack["elements"][3]
                    
                    # ACK05 - Date
                    if len(ack["elements"]) > 4 and ack["elements"][4]:
                        ack_entry["ship_date"] = self._format_date(ack["elements"][4])
                    
                    acknowledgments.append(ack_entry)
            
            if acknowledgments:
                line_item["acknowledgments"] = acknowledgments
                # Set primary status
                line_item["status"] = acknowledgments[0].get("status")
                line_item["quantity_acknowledged"] = acknowledgments[0].get("quantity_acknowledged")
            
            document.line_items.append(line_item)
    
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
