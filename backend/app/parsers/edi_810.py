"""
EDI 810 - Invoice Parser.
"""

from typing import Dict, Any
from app.parsers.base import BaseEDIParser, EDIDocument


class EDI810Parser(BaseEDIParser):
    """Parser for EDI 810 Invoice documents."""
    
    TRANSACTION_TYPE = "810"
    TRANSACTION_NAME = "Invoice"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 810 Invoice segments."""
        
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
        
        # Parse BIG (Beginning Segment for Invoice)
        big = self.get_segment_by_id(segments, "BIG")
        if big:
            document.header["invoice_date"] = big["elements"][0] if len(big["elements"]) > 0 else None
            document.header["invoice_number"] = big["elements"][1] if len(big["elements"]) > 1 else None
            document.header["po_date"] = big["elements"][2] if len(big["elements"]) > 2 else None
            document.header["po_number"] = big["elements"][3] if len(big["elements"]) > 3 else None
            document.date = document.header.get("invoice_date")
        
        # Parse N1 segments for parties
        n1_segments = self.get_all_segments_by_id(segments, "N1")
        document.header["parties"] = []
        for n1 in n1_segments:
            party = {
                "type": n1["elements"][0] if len(n1["elements"]) > 0 else None,
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
            }
            document.header["parties"].append(party)
        
        # Parse IT1 (Baseline Item Data) segments
        it1_segments = self.get_all_segments_by_id(segments, "IT1")
        for it1 in it1_segments:
            line_item = {
                "line_number": it1["elements"][0] if len(it1["elements"]) > 0 else None,
                "quantity_invoiced": it1["elements"][1] if len(it1["elements"]) > 1 else None,
                "unit": it1["elements"][2] if len(it1["elements"]) > 2 else None,
                "unit_price": it1["elements"][3] if len(it1["elements"]) > 3 else None,
                "product_id": it1["elements"][6] if len(it1["elements"]) > 6 else None,
            }
            document.line_items.append(line_item)
        
        # Parse TDS (Total Monetary Value Summary)
        tds = self.get_segment_by_id(segments, "TDS")
        if tds:
            document.summary["total_amount"] = tds["elements"][0] if len(tds["elements"]) > 0 else None
        
        # Parse CTT
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
        
        return document
