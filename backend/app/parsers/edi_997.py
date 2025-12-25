"""
EDI 997 - Functional Acknowledgment Parser.
"""

from app.parsers.base import BaseEDIParser, EDIDocument


class EDI997Parser(BaseEDIParser):
    """Parser for EDI 997 Functional Acknowledgment documents."""
    
    TRANSACTION_TYPE = "997"
    TRANSACTION_NAME = "Functional Acknowledgment"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 997 Functional Acknowledgment segments."""
        
        document = EDIDocument(
            transaction_type=self.TRANSACTION_TYPE,
            transaction_name=self.TRANSACTION_NAME,
        )
        
        # Parse ISA
        isa = self.get_segment_by_id(segments, "ISA")
        if isa and len(isa["elements"]) >= 12:
            document.sender_id = isa["elements"][5].strip() if len(isa["elements"]) > 5 else None
            document.receiver_id = isa["elements"][7].strip() if len(isa["elements"]) > 7 else None
        
        # Parse AK1 (Functional Group Response Header)
        ak1 = self.get_segment_by_id(segments, "AK1")
        if ak1:
            document.header["functional_id"] = ak1["elements"][0] if len(ak1["elements"]) > 0 else None
            document.header["group_control_number"] = ak1["elements"][1] if len(ak1["elements"]) > 1 else None
        
        # Parse AK2 (Transaction Set Response Header) segments
        ak2_segments = self.get_all_segments_by_id(segments, "AK2")
        for ak2 in ak2_segments:
            line_item = {
                "transaction_set_id": ak2["elements"][0] if len(ak2["elements"]) > 0 else None,
                "control_number": ak2["elements"][1] if len(ak2["elements"]) > 1 else None,
            }
            document.line_items.append(line_item)
        
        # Parse AK5 (Transaction Set Response Trailer) segments
        ak5_segments = self.get_all_segments_by_id(segments, "AK5")
        document.header["transaction_responses"] = []
        for ak5 in ak5_segments:
            response = {
                "ack_code": ak5["elements"][0] if len(ak5["elements"]) > 0 else None,
                "error_code": ak5["elements"][1] if len(ak5["elements"]) > 1 else None,
            }
            document.header["transaction_responses"].append(response)
        
        # Parse AK9 (Functional Group Response Trailer)
        ak9 = self.get_segment_by_id(segments, "AK9")
        if ak9:
            document.summary["ack_code"] = ak9["elements"][0] if len(ak9["elements"]) > 0 else None
            document.summary["sets_included"] = ak9["elements"][1] if len(ak9["elements"]) > 1 else None
            document.summary["sets_received"] = ak9["elements"][2] if len(ak9["elements"]) > 2 else None
            document.summary["sets_accepted"] = ak9["elements"][3] if len(ak9["elements"]) > 3 else None
        
        return document
