"""
EDI 812 - Credit/Debit Adjustment Parser.
"""

from typing import Dict, Any
from app.parsers.base import BaseEDIParser, EDIDocument


class EDI812Parser(BaseEDIParser):
    """Parser for EDI 812 Credit/Debit Adjustment documents."""
    
    TRANSACTION_TYPE = "812"
    TRANSACTION_NAME = "Credit/Debit Adjustment"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 812 Credit/Debit Adjustment segments."""
        
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
        
        # Parse BAK/BGN (Beginning Segment for Credit/Debit Adjustment)
        # Some implementations use BCD (Beginning Credit/Debit Adjustment) instead of BAK/BGN
        bcd = self.get_segment_by_id(segments, "BCD")
        if bcd:
            document.header["adjustment_date"] = bcd["elements"][0] if len(bcd["elements"]) > 0 else None
            document.header["credit_debit_number"] = bcd["elements"][1] if len(bcd["elements"]) > 1 else None
            # Element 2 is often the adjustment reason code
            document.header["transaction_type_code"] = bcd["elements"][2] if len(bcd["elements"]) > 2 else None
            document.header["po_number"] = bcd["elements"][3] if len(bcd["elements"]) > 3 else None
            document.date = document.header.get("adjustment_date")
        
        # Try BGN as alternative
        if not bcd:
            bgn = self.get_segment_by_id(segments, "BGN")
            if bgn:
                document.header["transaction_purpose"] = bgn["elements"][0] if len(bgn["elements"]) > 0 else None
                document.header["credit_debit_number"] = bgn["elements"][1] if len(bgn["elements"]) > 1 else None
                document.header["adjustment_date"] = bgn["elements"][2] if len(bgn["elements"]) > 2 else None
                document.date = document.header.get("adjustment_date")
        
        # Parse REF segments for references
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                ref_data = {
                    "type": ref["elements"][0],
                    "value": ref["elements"][1] if len(ref["elements"]) > 1 else None,
                    "description": ref["elements"][2] if len(ref["elements"]) > 2 else None,
                }
                document.header["references"].append(ref_data)
                # Check for invoice reference
                if ref["elements"][0] == "IV" or ref["elements"][0] == "IN":
                    document.header["invoice_number"] = ref["elements"][1]
                elif ref["elements"][0] == "PO":
                    document.header["po_number"] = ref["elements"][1]
        
        # Parse N1 segments for parties
        n1_segments = self.get_all_segments_by_id(segments, "N1")
        document.header["parties"] = []
        
        # Map party type codes to readable names for 812
        party_type_map = {
            "BY": "Buyer",
            "SE": "Seller", 
            "VN": "Vendor",
            "ST": "Ship To",
            "BT": "Bill To",
            "RI": "Remit To",
            "SF": "Ship From",
        }
        
        for n1 in n1_segments:
            party_code = n1["elements"][0] if len(n1["elements"]) > 0 else None
            party = {
                "type_code": party_code,
                "type": party_type_map.get(party_code, party_code),
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
                "id_qualifier": n1["elements"][2] if len(n1["elements"]) > 2 else None,
                "id": n1["elements"][3] if len(n1["elements"]) > 3 else None,
            }
            document.header["parties"].append(party)
        
        # Parse CDD (Credit/Debit Adjustment Detail) segments - specific to 812
        cdd_segments = self.get_all_segments_by_id(segments, "CDD")
        for cdd in cdd_segments:
            line_item = {
                "adjustment_reason": cdd["elements"][0] if len(cdd["elements"]) > 0 else None,
                "credit_debit_indicator": cdd["elements"][1] if len(cdd["elements"]) > 1 else None,  # C=Credit, D=Debit
                "adjustment_category": cdd["elements"][2] if len(cdd["elements"]) > 2 else None,
                "quantity": cdd["elements"][3] if len(cdd["elements"]) > 3 else None,
                "unit_price": cdd["elements"][4] if len(cdd["elements"]) > 4 else None,
                "adjustment_amount": cdd["elements"][5] if len(cdd["elements"]) > 5 else None,
            }
            document.line_items.append(line_item)
        
        # Parse IT1 segments as fallback (some 812s use IT1 like invoices)
        if not cdd_segments:
            it1_segments = self.get_all_segments_by_id(segments, "IT1")
            for it1 in it1_segments:
                line_item = {
                    "line_number": it1["elements"][0] if len(it1["elements"]) > 0 else None,
                    "quantity": it1["elements"][1] if len(it1["elements"]) > 1 else None,
                    "unit": it1["elements"][2] if len(it1["elements"]) > 2 else None,
                    "unit_price": it1["elements"][3] if len(it1["elements"]) > 3 else None,
                    "product_id": it1["elements"][6] if len(it1["elements"]) > 6 else None,
                }
                document.line_items.append(line_item)
        
        # Parse SAC (Service, Allowance, Charge) segments - common in 812
        sac_segments = self.get_all_segments_by_id(segments, "SAC")
        document.header["adjustments"] = []
        for sac in sac_segments:
            adjustment = {
                "allowance_charge_indicator": sac["elements"][0] if len(sac["elements"]) > 0 else None,  # A=Allowance, C=Charge
                "service_code": sac["elements"][1] if len(sac["elements"]) > 1 else None,
                "agency_code": sac["elements"][2] if len(sac["elements"]) > 2 else None,
                "amount": sac["elements"][4] if len(sac["elements"]) > 4 else None,
                "description": sac["elements"][14] if len(sac["elements"]) > 14 else None,
            }
            document.header["adjustments"].append(adjustment)
        
        # Parse TDS (Total Monetary Value Summary)
        tds = self.get_segment_by_id(segments, "TDS")
        if tds:
            # TDS values are often in cents, divide by 100
            try:
                total_cents = int(tds["elements"][0]) if len(tds["elements"]) > 0 else 0
                document.summary["total_amount"] = total_cents / 100
            except (ValueError, IndexError):
                document.summary["total_amount"] = tds["elements"][0] if len(tds["elements"]) > 0 else None
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
        
        return document
