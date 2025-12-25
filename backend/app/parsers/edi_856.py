"""
EDI 856 - Advance Ship Notice (ASN) Parser.
"""

from app.parsers.base import BaseEDIParser, EDIDocument


class EDI856Parser(BaseEDIParser):
    """Parser for EDI 856 Advance Ship Notice documents."""
    
    TRANSACTION_TYPE = "856"
    TRANSACTION_NAME = "Advance Ship Notice"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 856 ASN segments."""
        
        document = EDIDocument(
            transaction_type=self.TRANSACTION_TYPE,
            transaction_name=self.TRANSACTION_NAME,
        )
        
        # Parse ISA
        isa = self.get_segment_by_id(segments, "ISA")
        if isa and len(isa["elements"]) >= 12:
            document.sender_id = isa["elements"][5].strip() if len(isa["elements"]) > 5 else None
            document.receiver_id = isa["elements"][7].strip() if len(isa["elements"]) > 7 else None
        
        # Parse BSN (Beginning Segment for Ship Notice)
        bsn = self.get_segment_by_id(segments, "BSN")
        if bsn:
            document.header["purpose_code"] = bsn["elements"][0] if len(bsn["elements"]) > 0 else None
            document.header["shipment_id"] = bsn["elements"][1] if len(bsn["elements"]) > 1 else None
            document.header["date"] = bsn["elements"][2] if len(bsn["elements"]) > 2 else None
            document.header["time"] = bsn["elements"][3] if len(bsn["elements"]) > 3 else None
            document.date = document.header.get("date")
        
        # Parse HL (Hierarchical Level) segments
        hl_segments = self.get_all_segments_by_id(segments, "HL")
        document.header["hierarchy_levels"] = len(hl_segments)
        
        # Parse TD1 (Carrier Details - Quantity and Weight)
        td1 = self.get_segment_by_id(segments, "TD1")
        if td1:
            document.header["packaging_code"] = td1["elements"][0] if len(td1["elements"]) > 0 else None
            document.header["lading_quantity"] = td1["elements"][1] if len(td1["elements"]) > 1 else None
        
        # Parse TD5 (Carrier Details - Routing Sequence)
        td5 = self.get_segment_by_id(segments, "TD5")
        if td5:
            document.header["carrier_code"] = td5["elements"][2] if len(td5["elements"]) > 2 else None
            document.header["carrier_name"] = td5["elements"][4] if len(td5["elements"]) > 4 else None
        
        # Parse REF segments
        refs = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in refs:
            if len(ref["elements"]) >= 2:
                document.header["references"].append({
                    "qualifier": ref["elements"][0],
                    "value": ref["elements"][1],
                })
        
        # Parse SN1 (Item Detail - Shipment) segments
        sn1_segments = self.get_all_segments_by_id(segments, "SN1")
        for sn1 in sn1_segments:
            line_item = {
                "line_number": sn1["elements"][0] if len(sn1["elements"]) > 0 else None,
                "quantity_shipped": sn1["elements"][1] if len(sn1["elements"]) > 1 else None,
                "unit": sn1["elements"][2] if len(sn1["elements"]) > 2 else None,
            }
            document.line_items.append(line_item)
        
        return document
