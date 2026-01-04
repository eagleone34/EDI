"""
EDI 852 - Product Activity Data Parser.
Sales, inventory, and product movement data.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 852-specific codes
REPORT_TYPE_CODES = {
    "DX": "Demand",
    "IC": "Inventory Control",
    "IS": "Inventory Status",
    "PD": "Point of Sale Detail",
    "PS": "Product Sales",
    "SA": "Stock Adjustment",
    "SR": "Sales Report",
}

ACTIVITY_CODES = {
    "QS": "Quantity Sold",
    "QA": "Quantity on Hand",
    "QO": "Quantity on Order",
    "QC": "Quantity Committed",
    "QR": "Quantity Received",
    "QT": "Quantity Transferred",
    "QP": "Quantity in Process",
}

DATE_QUALIFIERS = {
    "090": "Report Start Date",
    "091": "Report End Date",
    "007": "Effective Date",
}

PARTY_TYPE_CODES = {
    "SU": "Supplier",
    "SE": "Seller",
    "BY": "Buyer",
    "ST": "Ship To",
    "WH": "Warehouse",
}


class EDI852Parser(BaseEDIParser):
    """Parser for EDI 852 Product Activity Data documents."""
    
    TRANSACTION_TYPE = "852"
    TRANSACTION_NAME = "Product Activity Data"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 852 Product Activity Data segments."""
        
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
        
        # Parse XQ (Reporting Date/Action)
        xq = self.get_segment_by_id(segments, "XQ")
        if xq:
            elements = xq["elements"]
            
            # XQ01 - Report Type Code
            if len(elements) > 0 and elements[0]:
                rtype = elements[0]
                document.header["report_type_code"] = rtype
                document.header["report_type"] = REPORT_TYPE_CODES.get(rtype, rtype)
            
            # XQ02 - Date (Report Date)
            if len(elements) > 1 and elements[1]:
                document.header["report_date"] = self._format_date(elements[1])
                document.date = document.header["report_date"]
            
            # XQ03 - Assigned Identification
            if len(elements) > 2 and elements[2]:
                document.header["report_id"] = elements[2]
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                label = DATE_QUALIFIERS.get(qualifier, f"Date ({qualifier})")
                document.header["dates"][label] = self._format_date(date_value)
                
                # Store report period
                if qualifier == "090":
                    document.header["report_start_date"] = self._format_date(date_value)
                elif qualifier == "091":
                    document.header["report_end_date"] = self._format_date(date_value)
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Parse LIN/QTY/ZA loops (Product Activity Detail)
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
            
            # Look for N4 (Geographic Location)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments) and segments[i]["id"] == "N4":
                    n4 = segments[i]
                    party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                    party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                    party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
                    break
            
            parties.append(party)
        
        return parties
    
    def _parse_line_items(self, segments: list, document: EDIDocument) -> None:
        """Parse LIN/QTY/ZA loops for product activity."""
        
        lin_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "LIN":
                lin_indices.append(i)
        
        total_sold = 0
        total_on_hand = 0
        
        for idx, lin_idx in enumerate(lin_indices):
            lin = segments[lin_idx]
            end_idx = lin_indices[idx + 1] if idx + 1 < len(lin_indices) else len(segments)
            
            line_item = {
                "line_number": lin["elements"][0] if len(lin["elements"]) > 0 else str(idx + 1),
            }
            
            # Parse product IDs from LIN
            product_ids = {}
            i = 1
            while i + 1 < len(lin["elements"]):
                qualifier = lin["elements"][i]
                value = lin["elements"][i + 1] if i + 1 < len(lin["elements"]) else ""
                if qualifier and value:
                    qual_names = {
                        "UP": "UPC",
                        "UK": "UPC/EAN",
                        "EN": "EAN",
                        "VP": "Vendor's Part Number",
                        "BP": "Buyer's Part Number",
                        "PI": "Purchaser's Item Code",
                    }
                    label = qual_names.get(qualifier, qualifier)
                    product_ids[label] = value
                i += 2
            
            line_item["product_ids"] = product_ids
            line_item["product_id"] = product_ids.get("UPC") or next(iter(product_ids.values()), None)
            
            # Look for PID (Product Description)
            for i in range(lin_idx + 1, min(end_idx, lin_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "PID":
                    pid = segments[i]
                    if len(pid["elements"]) > 4 and pid["elements"][4]:
                        line_item["description"] = pid["elements"][4]
                    break
            
            # Parse QTY (Quantity Information) segments
            quantities = {}
            for i in range(lin_idx + 1, end_idx):
                if i < len(segments) and segments[i]["id"] == "QTY":
                    qty = segments[i]
                    elements = qty["elements"]
                    
                    if len(elements) >= 2:
                        qualifier = elements[0]
                        value = elements[1]
                        
                        label = ACTIVITY_CODES.get(qualifier, qualifier)
                        try:
                            quantities[label] = float(value)
                        except:
                            quantities[label] = value
                        
                        # Track totals
                        if qualifier == "QS":
                            try:
                                total_sold += float(value)
                            except:
                                pass
                        elif qualifier == "QA":
                            try:
                                total_on_hand += float(value)
                            except:
                                pass
            
            if quantities:
                line_item["quantities"] = quantities
                line_item["quantity_sold"] = quantities.get("Quantity Sold")
                line_item["quantity_on_hand"] = quantities.get("Quantity on Hand")
            
            # Parse CTP (Pricing Information)
            for i in range(lin_idx + 1, min(end_idx, lin_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "CTP":
                    ctp = segments[i]
                    elements = ctp["elements"]
                    
                    if len(elements) > 2 and elements[2]:
                        try:
                            line_item["unit_price"] = float(elements[2])
                        except:
                            line_item["unit_price"] = elements[2]
                    break
            
            # Calculate sales amount if we have price and quantity
            if line_item.get("quantity_sold") and line_item.get("unit_price"):
                try:
                    line_item["sales_amount"] = round(
                        float(line_item["quantity_sold"]) * float(line_item["unit_price"]), 2
                    )
                except:
                    pass
            
            # Parse AMT (Monetary Amount)
            for i in range(lin_idx + 1, min(end_idx, lin_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "AMT":
                    amt = segments[i]
                    if len(amt["elements"]) >= 2:
                        try:
                            line_item["monetary_amount"] = float(amt["elements"][1])
                        except:
                            line_item["monetary_amount"] = amt["elements"][1]
                    break
            
            document.line_items.append(line_item)
        
        # Summary
        document.summary["total_items"] = len(document.line_items)
        if total_sold > 0:
            document.summary["total_quantity_sold"] = total_sold
        if total_on_hand > 0:
            document.summary["total_quantity_on_hand"] = total_on_hand
    
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
