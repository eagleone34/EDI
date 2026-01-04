"""
EDI 861 - Receiving Advice/Acceptance Certificate Parser.
Notification of goods received with exceptions.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 861-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "05": "Replace",
}

ACTION_CODES = {
    "2": "Received",
    "3": "Inspection Complete",
    "4": "Received and Accepted",
    "5": "Partially Received",
    "6": "Rejected",
}

RECEIVING_CONDITION_CODES = {
    "01": "Good Condition",
    "02": "Damaged",
    "03": "Shortage",
    "04": "Overage",
    "05": "Wrong Item",
    "06": "Rejected",
    "07": "Returned",
}

PARTY_TYPE_CODES = {
    "SU": "Supplier",
    "SE": "Seller",
    "BY": "Buyer",
    "ST": "Ship To (Receiving Location)",
    "SF": "Ship From",
    "VN": "Vendor",
}


class EDI861Parser(BaseEDIParser):
    """Parser for EDI 861 Receiving Advice/Acceptance Certificate documents."""
    
    TRANSACTION_TYPE = "861"
    TRANSACTION_NAME = "Receiving Advice"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 861 Receiving Advice segments."""
        
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
        
        # Parse BRA (Beginning Segment for Receiving Advice)
        bra = self.get_segment_by_id(segments, "BRA")
        if bra:
            elements = bra["elements"]
            
            # BRA01 - Reference Identification (Receiving Advice Number)
            if len(elements) > 0 and elements[0]:
                document.header["receiving_advice_number"] = elements[0]
            
            # BRA02 - Date
            if len(elements) > 1 and elements[1]:
                document.header["date"] = self._format_date(elements[1])
                document.date = document.header["date"]
            
            # BRA03 - Transaction Set Purpose Code
            if len(elements) > 2 and elements[2]:
                purpose = elements[2]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
            
            # BRA04 - Receiving Advice Type Code
            if len(elements) > 3 and elements[3]:
                document.header["receiving_type_code"] = elements[3]
            
            # BRA05 - Time
            if len(elements) > 4 and elements[4]:
                document.header["time"] = elements[4]
            
            # BRA06 - Receiving Condition Code
            if len(elements) > 5 and elements[5]:
                condition = elements[5]
                document.header["condition_code"] = condition
                document.header["condition"] = RECEIVING_CONDITION_CODES.get(condition, condition)
            
            # BRA07 - Action Code
            if len(elements) > 6 and elements[6]:
                action = elements[6]
                document.header["action_code"] = action
                document.header["action"] = ACTION_CODES.get(action, action)
        
        # Parse REF (Reference Identification)
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                qualifier = ref["elements"][0]
                value = ref["elements"][1]
                
                ref_qualifiers = {
                    "PO": "Purchase Order Number",
                    "BM": "Bill of Lading",
                    "SI": "Shipper's ID",
                    "CN": "Carrier's Reference",
                    "IV": "Invoice Number",
                }
                
                document.header["references"].append({
                    "qualifier": qualifier,
                    "qualifier_desc": ref_qualifiers.get(qualifier, qualifier),
                    "value": value,
                })
                
                # Store common references
                if qualifier == "PO":
                    document.header["po_number"] = value
                elif qualifier == "BM":
                    document.header["bill_of_lading"] = value
        
        # Parse PRF (Purchase Order Reference)
        prf = self.get_segment_by_id(segments, "PRF")
        if prf:
            elements = prf["elements"]
            if len(elements) > 0 and elements[0]:
                document.header["po_number"] = elements[0]
            if len(elements) > 3 and elements[3]:
                document.header["po_date"] = self._format_date(elements[3])
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                
                date_qualifiers = {
                    "050": "Received Date",
                    "051": "Receipt Time",
                    "011": "Shipped Date",
                }
                
                label = date_qualifiers.get(qualifier, f"Date ({qualifier})")
                document.header["dates"][label] = self._format_date(date_value)
        
        # Parse TD1 (Carrier Details - Quantity and Weight)
        td1 = self.get_segment_by_id(segments, "TD1")
        if td1:
            elements = td1["elements"]
            document.header["packaging"] = {
                "packaging_code": elements[0] if len(elements) > 0 else None,
                "lading_quantity": elements[1] if len(elements) > 1 else None,
                "weight": elements[6] if len(elements) > 6 else None,
                "unit_of_measure": elements[7] if len(elements) > 7 else None,
            }
        
        # Parse TD5 (Carrier Details - Routing)
        td5 = self.get_segment_by_id(segments, "TD5")
        if td5:
            elements = td5["elements"]
            document.header["carrier"] = {
                "routing_sequence": elements[0] if len(elements) > 0 else None,
                "carrier_code": elements[2] if len(elements) > 2 else None,
                "transport_method": elements[3] if len(elements) > 3 else None,
                "routing": elements[4] if len(elements) > 4 else None,
            }
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Parse RCD (Receiving Conditions) line items
        self._parse_line_items(segments, document)
        
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
    
    def _parse_line_items(self, segments: list, document: EDIDocument) -> None:
        """Parse RCD (Receiving Conditions) segments."""
        
        rcd_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "RCD":
                rcd_indices.append(i)
        
        total_received = 0
        total_damaged = 0
        
        for idx, rcd_idx in enumerate(rcd_indices):
            rcd = segments[rcd_idx]
            end_idx = rcd_indices[idx + 1] if idx + 1 < len(rcd_indices) else len(segments)
            
            elements = rcd["elements"]
            
            line_item = {
                "line_number": str(idx + 1),
            }
            
            # RCD01 - Quantity in Question
            if len(elements) > 0 and elements[0]:
                line_item["quantity_in_question"] = elements[0]
            
            # RCD02 - Unit of Measure
            if len(elements) > 1 and elements[1]:
                line_item["unit"] = elements[1]
            
            # RCD03 - Receiving Condition Code
            if len(elements) > 2 and elements[2]:
                condition = elements[2]
                line_item["condition_code"] = condition
                line_item["condition"] = RECEIVING_CONDITION_CODES.get(condition, condition)
            
            # RCD05 - Quantity Received
            if len(elements) > 4 and elements[4]:
                try:
                    qty = float(elements[4])
                    line_item["quantity_received"] = qty
                    total_received += qty
                except:
                    line_item["quantity_received"] = elements[4]
            
            # RCD07 - Quantity Damaged
            if len(elements) > 6 and elements[6]:
                try:
                    qty = float(elements[6])
                    line_item["quantity_damaged"] = qty
                    total_damaged += qty
                except:
                    line_item["quantity_damaged"] = elements[6]
            
            # Look for LIN (Item Identification)
            for i in range(rcd_idx + 1, min(end_idx, rcd_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "LIN":
                    lin = segments[i]
                    
                    product_ids = {}
                    j = 1
                    while j + 1 < len(lin["elements"]):
                        qualifier = lin["elements"][j]
                        value = lin["elements"][j + 1] if j + 1 < len(lin["elements"]) else ""
                        if qualifier and value:
                            qual_names = {
                                "VP": "Vendor's Part Number",
                                "BP": "Buyer's Part Number",
                                "UP": "UPC",
                            }
                            label = qual_names.get(qualifier, qualifier)
                            product_ids[label] = value
                        j += 2
                    
                    line_item["product_ids"] = product_ids
                    line_item["product_id"] = next(iter(product_ids.values()), None)
                    break
            
            # Look for PID (Product Description)
            for i in range(rcd_idx + 1, min(end_idx, rcd_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "PID":
                    pid = segments[i]
                    if len(pid["elements"]) > 4 and pid["elements"][4]:
                        line_item["description"] = pid["elements"][4]
                    break
            
            document.line_items.append(line_item)
        
        # Summary
        document.summary["total_items"] = len(document.line_items)
        document.summary["total_quantity_received"] = total_received
        if total_damaged > 0:
            document.summary["total_quantity_damaged"] = total_damaged
    
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
