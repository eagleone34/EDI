"""
EDI 855 - Purchase Order Acknowledgment Parser.
"""

from app.parsers.base import BaseEDIParser, EDIDocument


class EDI855Parser(BaseEDIParser):
    """Parser for EDI 855 Purchase Order Acknowledgment documents."""
    
    TRANSACTION_TYPE = "855"
    TRANSACTION_NAME = "Purchase Order Acknowledgment"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 855 PO Acknowledgment segments."""
        
        document = EDIDocument(
            transaction_type=self.TRANSACTION_TYPE,
            transaction_name=self.TRANSACTION_NAME,
        )
        
        # Parse ISA
        isa = self.get_segment_by_id(segments, "ISA")
        if isa and len(isa["elements"]) >= 12:
            document.sender_id = isa["elements"][5].strip() if len(isa["elements"]) > 5 else None
            document.receiver_id = isa["elements"][7].strip() if len(isa["elements"]) > 7 else None
        
        # Parse BAK (Beginning Segment for Purchase Order Acknowledgment)
        bak = self.get_segment_by_id(segments, "BAK")
        if bak:
            document.header["ack_type"] = bak["elements"][0] if len(bak["elements"]) > 0 else None
            document.header["purpose_code"] = bak["elements"][1] if len(bak["elements"]) > 1 else None
            document.header["po_number"] = bak["elements"][2] if len(bak["elements"]) > 2 else None
            document.header["po_date"] = bak["elements"][3] if len(bak["elements"]) > 3 else None
            document.date = document.header.get("po_date")
        
        # Parse N1 segments
        n1_segments = self.get_all_segments_by_id(segments, "N1")
        document.header["parties"] = []
        for n1 in n1_segments:
            party = {
                "type": n1["elements"][0] if len(n1["elements"]) > 0 else None,
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
            }
            document.header["parties"].append(party)
        
        # Parse PO1 segments
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
        
        # Parse ACK (Line Item Acknowledgment) segments
        ack_segments = self.get_all_segments_by_id(segments, "ACK")
        document.header["acknowledgments"] = []
        for ack in ack_segments:
            ack_item = {
                "status": ack["elements"][0] if len(ack["elements"]) > 0 else None,
                "quantity": ack["elements"][1] if len(ack["elements"]) > 1 else None,
            }
            document.header["acknowledgments"].append(ack_item)
        
        return document
