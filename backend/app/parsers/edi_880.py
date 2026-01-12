"""
EDI 880 - Grocery Products Invoice Parser.
Grocery industry invoice format.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 880-specific codes
PARTY_TYPE_CODES = {
    "BY": "Buyer",
    "SE": "Seller",
    "ST": "Ship To",
    "BT": "Bill To",
    "VN": "Vendor",
    "RI": "Remit To",
}

ALLOWANCE_CHARGE_CODES = {
    "A": "Allowance",
    "C": "Charge",
}


class EDI880Parser(BaseEDIParser):
    """Parser for EDI 880 Grocery Products Invoice documents."""
    
    TRANSACTION_TYPE = "880"
    TRANSACTION_NAME = "Grocery Products Invoice"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 880 Grocery Products Invoice segments."""
        
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
        
        # Parse G01 (Invoice Identification)
        g01 = self.get_segment_by_id(segments, "G01")
        if g01:
            elements = g01["elements"]
            
            # G0101 - Date (Invoice Date)
            if len(elements) > 0 and elements[0]:
                document.header["invoice_date"] = self._format_date(elements[0])
                document.date = document.header["invoice_date"]
            
            # G0102 - Invoice Number
            if len(elements) > 1 and elements[1]:
                document.header["invoice_number"] = elements[1]
            
            # G0103 - Date (PO Date)
            if len(elements) > 2 and elements[2]:
                document.header["po_date"] = self._format_date(elements[2])
            
            # G0104 - Purchase Order Number
            if len(elements) > 3 and elements[3]:
                document.header["po_number"] = elements[3]
            
            # G0105 - Date (Ship Date)
            if len(elements) > 4 and elements[4]:
                document.header["ship_date"] = self._format_date(elements[4])
            
            # G0107 - Vendor Order Number
            if len(elements) > 6 and elements[6]:
                document.header["vendor_order_number"] = elements[6]
        
        # Fallback: Parse BIG if G01 not present
        big = self.get_segment_by_id(segments, "BIG")
        if big and not document.header.get("invoice_number"):
            elements = big["elements"]
            if len(elements) > 0 and elements[0]:
                document.header["invoice_date"] = self._format_date(elements[0])
                document.date = document.header["invoice_date"]
            if len(elements) > 1 and elements[1]:
                document.header["invoice_number"] = elements[1]
            if len(elements) > 3 and elements[3]:
                document.header["po_number"] = elements[3]
        
        # Parse REF (Reference Identification)
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                document.header["references"].append({
                    "qualifier": ref["elements"][0],
                    "value": ref["elements"][1],
                })
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Extract specific parties
        for party in document.header.get("parties", []):
            if party.get("type_code") == "SE":
                document.header["seller"] = party
            elif party.get("type_code") == "BY":
                document.header["buyer"] = party
            elif party.get("type_code") == "ST":
                document.header["ship_to"] = party
        
        # Parse G17/IT1 (Line Item Detail - Invoice)
        self._parse_line_items(segments, document)
        
        # Parse G31 (Total Invoice Quantity)
        g31 = self.get_segment_by_id(segments, "G31")
        if g31:
            elements = g31["elements"]
            if len(elements) > 0 and elements[0]:
                document.summary["total_quantity"] = elements[0]
            if len(elements) > 1 and elements[1]:
                document.summary["unit_of_measure"] = elements[1]
            if len(elements) > 2 and elements[2]:
                document.summary["total_weight"] = elements[2]
            if len(elements) > 4 and elements[4]:
                document.summary["total_volume"] = elements[4]
        
        # Parse G33 (Total Dollars Summary)
        g33 = self.get_segment_by_id(segments, "G33")
        if g33:
            elements = g33["elements"]
            if len(elements) > 0 and elements[0]:
                try:
                    document.summary["total_invoice_amount"] = float(elements[0])
                except:
                    document.summary["total_invoice_amount"] = elements[0]
        
        # Fallback: Parse TDS (Total Monetary Value Summary)
        tds = self.get_segment_by_id(segments, "TDS")
        if tds and not document.summary.get("total_invoice_amount"):
            elements = tds["elements"]
            if len(elements) > 0 and elements[0]:
                try:
                    total_cents = int(elements[0])
                    document.summary["total_invoice_amount"] = total_cents / 100
                except:
                    document.summary["total_invoice_amount"] = elements[0]
        
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
            
            # Look for N2 (Additional Name)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "N2":
                    n2 = parsed_segments[i]
                    if len(n2["elements"]) > 0 and n2["elements"][0]:
                        party["additional_name"] = n2["elements"][0]
                    break
            
            # Look for N3/N4
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(parsed_segments):
                    if parsed_segments[i]["id"] == "N3":
                        n3 = parsed_segments[i]
                        party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                        party["address_line2"] = n3["elements"][1] if len(n3["elements"]) > 1 else None
                    elif parsed_segments[i]["id"] == "N4":
                        n4 = parsed_segments[i]
                        party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                        party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                        party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
                        party["country"] = n4["elements"][3] if len(n4["elements"]) > 3 else None
            
            parties.append(party)
        
        return parties
    
    def _parse_line_items(self, segments: list, document: EDIDocument) -> None:
        """Parse G17/IT1 line item loops for grocery invoice."""
        
        # Parse all segments first since we need to look ahead
        parsed_segments = [self._parse_segment(s) for s in segments]
        
        # Try G17 first (grocery-specific)
        g17_indices = []
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "G17":
                g17_indices.append(i)
        
        total_amount = 0
        
        if g17_indices:
            for idx, g17_idx in enumerate(g17_indices):
                g17 = parsed_segments[g17_idx]
                end_idx = g17_indices[idx + 1] if idx + 1 < len(g17_indices) else len(parsed_segments)
                
                elements = g17["elements"]
                
                line_item = {
                    "line_number": str(idx + 1),
                }
                
                # G1701 - Quantity Invoiced
                if len(elements) > 0 and elements[0]:
                    line_item["quantity"] = elements[0]
                
                # G1702 - Unit of Measure
                if len(elements) > 1 and elements[1]:
                    line_item["unit"] = elements[1]
                
                # G1703 - Item List Cost
                if len(elements) > 2 and elements[2]:
                    try:
                        line_item["unit_price"] = float(elements[2])
                    except:
                        line_item["unit_price"] = elements[2]
                
                # G1704 - UPC Case Code
                if len(elements) > 3 and elements[3]:
                    line_item["upc_case_code"] = elements[3]
                
                # G1705-G1710 - Product IDs
                product_ids = {}
                if len(elements) > 4 and elements[4]:
                    qual = elements[4]
                    if len(elements) > 5 and elements[5]:
                        qual_names = {
                            "UP": "UPC",
                            "UK": "UPC/EAN",
                            "VP": "Vendor's Part Number",
                        }
                        product_ids[qual_names.get(qual, qual)] = elements[5]
                
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
                
                # Look for G19 (Quantity/Price Differences)
                for i in range(g17_idx + 1, min(end_idx, g17_idx + 10)):
                    if i < len(parsed_segments) and parsed_segments[i]["id"] == "G19":
                        g19 = parsed_segments[i]
                        elements = g19["elements"]
                        
                        if len(elements) > 0 and elements[0]:
                            line_item["quantity_difference"] = elements[0]
                        if len(elements) > 2 and elements[2]:
                            line_item["price_difference"] = elements[2]
                        break
                
                # Look for G72 (Allowance or Charge)
                allowances_charges = []
                for i in range(g17_idx + 1, min(end_idx, g17_idx + 10)):
                    if i < len(parsed_segments) and parsed_segments[i]["id"] == "G72":
                        g72 = parsed_segments[i]
                        elements = g72["elements"]
                        
                        entry = {}
                        if len(elements) > 0:
                            entry["type"] = ALLOWANCE_CHARGE_CODES.get(elements[0], elements[0])
                        if len(elements) > 5:
                            try:
                                entry["amount"] = float(elements[5])
                            except:
                                entry["amount"] = elements[5]
                        
                        allowances_charges.append(entry)
                
                if allowances_charges:
                    line_item["allowances_charges"] = allowances_charges
                
                document.line_items.append(line_item)
        else:
            # Fallback to IT1 (standard invoice format)
            it1_indices = []
            for i, seg in enumerate(parsed_segments):
                if seg["id"] == "IT1":
                    it1_indices.append(i)
            
            for idx, it1_idx in enumerate(it1_indices):
                it1 = parsed_segments[it1_idx]
                end_idx = it1_indices[idx + 1] if idx + 1 < len(it1_indices) else len(parsed_segments)
                
                elements = it1["elements"]
                
                line_item = {
                    "line_number": elements[0] if len(elements) > 0 else str(idx + 1),
                    "quantity": elements[1] if len(elements) > 1 else None,
                    "unit": elements[2] if len(elements) > 2 else None,
                    "unit_price": elements[3] if len(elements) > 3 else None,
                }
                
                # Calculate line total
                try:
                    qty = float(line_item.get("quantity", 0))
                    price = float(line_item.get("unit_price", 0))
                    line_item["total"] = round(qty * price, 2)
                    total_amount += line_item["total"]
                except:
                    pass
                
                # Parse product IDs
                product_ids = {}
                i = 5
                while i + 1 < len(elements):
                    qualifier = elements[i]
                    value = elements[i + 1] if i + 1 < len(elements) else ""
                    if qualifier and value:
                        qual_names = {
                            "UP": "UPC",
                            "VP": "Vendor's Part Number",
                        }
                        product_ids[qual_names.get(qualifier, qualifier)] = value
                    i += 2
                
                line_item["product_ids"] = product_ids
                line_item["product_id"] = next(iter(product_ids.values()), None)
                
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
