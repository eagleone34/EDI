"""
EDI 875 - Grocery Products Purchase Order Parser.
Grocery industry purchase order format.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 875-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "05": "Replace",
}

ORDER_TYPE_CODES = {
    "SA": "Stand-Alone Order",
    "RL": "Release",
    "NE": "New Order",
    "RO": "Rush Order",
    "DS": "Drop Ship",
}

PARTY_TYPE_CODES = {
    "BY": "Buyer",
    "SE": "Seller",
    "ST": "Ship To",
    "BT": "Bill To",
    "VN": "Vendor",
    "WH": "Warehouse",
}

ALLOWANCE_CHARGE_CODES = {
    "A": "Allowance",
    "C": "Charge",
}


class EDI875Parser(BaseEDIParser):
    """Parser for EDI 875 Grocery Products Purchase Order documents."""
    
    TRANSACTION_TYPE = "875"
    TRANSACTION_NAME = "Grocery Products Purchase Order"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 875 Grocery Products Purchase Order segments."""
        
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
        
        # Parse G50 (Purchase Order Identification)
        g50 = self.get_segment_by_id(segments, "G50")
        if g50:
            elements = g50["elements"]
            
            # G5001 - Order Status Code
            if len(elements) > 0 and elements[0]:
                document.header["order_status_code"] = elements[0]
            
            # G5002 - Date (PO Date)
            if len(elements) > 1 and elements[1]:
                document.header["po_date"] = self._format_date(elements[1])
                document.date = document.header["po_date"]
            
            # G5003 - Purchase Order Number
            if len(elements) > 2 and elements[2]:
                document.header["po_number"] = elements[2]
            
            # G5004 - Date (Ship Date)
            if len(elements) > 3 and elements[3]:
                document.header["ship_date"] = self._format_date(elements[3])
            
            # G5006 - Purchase Order Type Code
            if len(elements) > 5 and elements[5]:
                order_type = elements[5]
                document.header["order_type_code"] = order_type
                document.header["order_type"] = ORDER_TYPE_CODES.get(order_type, order_type)
        
        # Parse N9 (Reference Identification)
        n9_segments = self.get_all_segments_by_id(segments, "N9")
        document.header["references"] = []
        for n9 in n9_segments:
            if len(n9["elements"]) >= 2:
                document.header["references"].append({
                    "qualifier": n9["elements"][0],
                    "value": n9["elements"][1],
                    "description": n9["elements"][2] if len(n9["elements"]) > 2 else None,
                })
        
        # Parse G61 (Contact)
        g61_segments = self.get_all_segments_by_id(segments, "G61")
        document.header["contacts"] = []
        for g61 in g61_segments:
            if len(g61["elements"]) >= 2:
                contact = {
                    "function_code": g61["elements"][0],
                    "name": g61["elements"][1],
                }
                if len(g61["elements"]) > 2:
                    contact["comm_type"] = g61["elements"][2]
                if len(g61["elements"]) > 3:
                    contact["comm_number"] = g61["elements"][3]
                document.header["contacts"].append(contact)
        
        # Parse G62 (Date/Time)
        g62_segments = self.get_all_segments_by_id(segments, "G62")
        document.header["dates"] = {}
        for g62 in g62_segments:
            if len(g62["elements"]) >= 2:
                qualifier = g62["elements"][0]
                date_value = g62["elements"][1]
                
                date_qualifiers = {
                    "02": "Delivery Date",
                    "10": "Requested Ship Date",
                    "11": "Ship Not Before",
                    "12": "Ship Not After",
                }
                
                label = date_qualifiers.get(qualifier, f"Date ({qualifier})")
                document.header["dates"][label] = self._format_date(date_value)
        
        # Parse NTE (Note/Special Instruction)
        nte_segments = self.get_all_segments_by_id(segments, "NTE")
        notes = []
        for nte in nte_segments:
            if len(nte["elements"]) > 1 and nte["elements"][1]:
                notes.append(nte["elements"][1])
        if notes:
            document.header["notes"] = notes
        
        # Parse G66 (Transportation Instructions)
        g66 = self.get_segment_by_id(segments, "G66")
        if g66:
            elements = g66["elements"]
            document.header["transportation"] = {
                "shipment_type": elements[0] if len(elements) > 0 else None,
                "routing_code": elements[1] if len(elements) > 1 else None,
                "carrier_code": elements[2] if len(elements) > 2 else None,
                "method_code": elements[3] if len(elements) > 3 else None,
            }
        
        # Parse G23 (Terms of Sale)
        g23 = self.get_segment_by_id(segments, "G23")
        if g23:
            elements = g23["elements"]
            document.header["terms_of_sale"] = {
                "terms_type": elements[0] if len(elements) > 0 else None,
                "terms_basis": elements[1] if len(elements) > 1 else None,
                "discount_percent": elements[2] if len(elements) > 2 else None,
                "discount_days": elements[4] if len(elements) > 4 else None,
                "net_days": elements[6] if len(elements) > 6 else None,
            }
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Parse G68/G69/G70/G72 (Line Item Detail)
        self._parse_line_items(segments, document)
        
        # Parse G76 (Total Purchase Order)
        g76 = self.get_segment_by_id(segments, "G76")
        if g76:
            elements = g76["elements"]
            if len(elements) > 0 and elements[0]:
                document.summary["total_quantity"] = elements[0]
            if len(elements) > 1 and elements[1]:
                document.summary["unit_of_measure"] = elements[1]
            if len(elements) > 2 and elements[2]:
                document.summary["weight"] = elements[2]
            if len(elements) > 4 and elements[4]:
                try:
                    document.summary["total_amount"] = float(elements[4])
                except:
                    document.summary["total_amount"] = elements[4]
        
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
        """Parse G68/G69/G70/G72 line item loops."""
        
        g68_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "G68":
                g68_indices.append(i)
        
        total_amount = 0
        
        for idx, g68_idx in enumerate(g68_indices):
            g68 = segments[g68_idx]
            end_idx = g68_indices[idx + 1] if idx + 1 < len(g68_indices) else len(segments)
            
            elements = g68["elements"]
            
            line_item = {
                "line_number": str(idx + 1),
            }
            
            # G6801 - Quantity Ordered
            if len(elements) > 0 and elements[0]:
                line_item["quantity"] = elements[0]
            
            # G6802 - Unit of Measure
            if len(elements) > 1 and elements[1]:
                line_item["unit"] = elements[1]
            
            # G6803 - Item List Cost (Unit Price)
            if len(elements) > 2 and elements[2]:
                try:
                    line_item["unit_price"] = float(elements[2])
                except:
                    line_item["unit_price"] = elements[2]
            
            # G6804 - UPC Case Code
            if len(elements) > 3 and elements[3]:
                line_item["upc_case_code"] = elements[3]
            
            # G6805-G6808 - Product IDs
            product_ids = {}
            if len(elements) > 4 and elements[4]:
                qual = elements[4]
                if len(elements) > 5 and elements[5]:
                    qual_names = {
                        "UP": "UPC",
                        "UK": "UPC/EAN",
                        "VP": "Vendor's Part Number",
                        "BP": "Buyer's Part Number",
                    }
                    product_ids[qual_names.get(qual, qual)] = elements[5]
            
            if len(elements) > 6 and elements[6]:
                qual = elements[6]
                if len(elements) > 7 and elements[7]:
                    qual_names = {
                        "UP": "UPC",
                        "VP": "Vendor's Part Number",
                    }
                    product_ids[qual_names.get(qual, qual)] = elements[7]
            
            line_item["product_ids"] = product_ids
            line_item["product_id"] = product_ids.get("UPC") or next(iter(product_ids.values()), None)
            
            # Calculate line total
            try:
                qty = float(line_item.get("quantity", 0))
                price = float(line_item.get("unit_price", 0))
                line_item["total"] = round(qty * price, 2)
                total_amount += line_item["total"]
            except:
                pass
            
            # Look for G69 (Description)
            for i in range(g68_idx + 1, min(end_idx, g68_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "G69":
                    g69 = segments[i]
                    if len(g69["elements"]) > 0 and g69["elements"][0]:
                        line_item["description"] = g69["elements"][0]
                    break
            
            # Look for G70 (Line Item Detail - Miscellaneous)
            for i in range(g68_idx + 1, min(end_idx, g68_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "G70":
                    g70 = segments[i]
                    if len(g70["elements"]) > 0 and g70["elements"][0]:
                        line_item["pack"] = g70["elements"][0]
                    if len(g70["elements"]) > 1 and g70["elements"][1]:
                        line_item["size"] = g70["elements"][1]
                    break
            
            # Look for G72 (Allowance or Charge)
            allowances_charges = []
            for i in range(g68_idx + 1, min(end_idx, g68_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "G72":
                    g72 = segments[i]
                    elements = g72["elements"]
                    
                    entry = {}
                    if len(elements) > 0:
                        entry["type"] = ALLOWANCE_CHARGE_CODES.get(elements[0], elements[0])
                    if len(elements) > 1:
                        entry["method"] = elements[1]
                    if len(elements) > 5:
                        try:
                            entry["amount"] = float(elements[5])
                        except:
                            entry["amount"] = elements[5]
                    
                    allowances_charges.append(entry)
            
            if allowances_charges:
                line_item["allowances_charges"] = allowances_charges
            
            document.line_items.append(line_item)
        
        # Summary
        document.summary["total_line_items"] = len(document.line_items)
        if total_amount > 0:
            document.summary["calculated_total"] = round(total_amount, 2)
    
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
