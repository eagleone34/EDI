"""
EDI 850 - Purchase Order Parser.
"""

from typing import Dict, Any
from app.parsers.base import BaseEDIParser, EDIDocument


class EDI850Parser(BaseEDIParser):
    """Parser for EDI 850 Purchase Order documents."""
    
    TRANSACTION_TYPE = "850"
    TRANSACTION_NAME = "Purchase Order"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 850 Purchase Order segments."""
        
        document = EDIDocument(
            transaction_type=self.TRANSACTION_TYPE,
            transaction_name=self.TRANSACTION_NAME,
        )
        
        # Parse ISA (Interchange Control Header)
        isa = self.get_segment_by_id(segments, "ISA")
        if isa and len(isa["elements"]) >= 12:
            document.sender_id = isa["elements"][5].strip() if len(isa["elements"]) > 5 else None
            document.receiver_id = isa["elements"][7].strip() if len(isa["elements"]) > 7 else None
            document.control_number = isa["elements"][12].strip() if len(isa["elements"]) > 12 else None
        
        # Parse GS (Functional Group Header)
        gs = self.get_segment_by_id(segments, "GS")
        if gs and len(gs["elements"]) >= 4:
            document.date = gs["elements"][3] if len(gs["elements"]) > 3 else None
        
        # Parse BEG (Beginning Segment for Purchase Order)
        beg = self.get_segment_by_id(segments, "BEG")
        if beg:
            document.header["purpose_code"] = beg["elements"][0] if len(beg["elements"]) > 0 else None
            document.header["type_code"] = beg["elements"][1] if len(beg["elements"]) > 1 else None
            document.header["po_number"] = beg["elements"][2] if len(beg["elements"]) > 2 else None
            document.header["po_date"] = beg["elements"][4] if len(beg["elements"]) > 4 else None
        
        # Parse REF segments (Reference Information)
        refs = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in refs:
            if len(ref["elements"]) >= 2:
                document.header["references"].append({
                    "qualifier": ref["elements"][0],
                    "value": ref["elements"][1],
                })
        
        # Parse N1 (Name) segments for parties
        n1_segments = self.get_all_segments_by_id(segments, "N1")
        document.header["parties"] = []
        for n1 in n1_segments:
            party = {
                "type": n1["elements"][0] if len(n1["elements"]) > 0 else None,
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
            }
            document.header["parties"].append(party)
        
        # Parse PO1 (Line Item) segments
        po1_segments = self.get_all_segments_by_id(segments, "PO1")
        for po1 in po1_segments:
            line_item = {
                "line_number": po1["elements"][0] if len(po1["elements"]) > 0 else None,
                "quantity": po1["elements"][1] if len(po1["elements"]) > 1 else None,
                "unit": po1["elements"][2] if len(po1["elements"]) > 2 else None,
                "unit_price": po1["elements"][3] if len(po1["elements"]) > 3 else None,
                "product_id": po1["elements"][6] if len(po1["elements"]) > 6 else None,
            }
            document.line_items.append(line_item)
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
            document.summary["hash_total"] = ctt["elements"][1] if len(ctt["elements"]) > 1 else None
        
        return document
