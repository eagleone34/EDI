"""
EDI 864 - Text Message Parser.
Free-form text communication between trading partners.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 864-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "06": "Confirmation",
    "11": "Response",
    "18": "Reissue",
    "22": "Information Copy",
}

MESSAGE_FUNCTION_CODES = {
    "CF": "Confirmation",
    "CG": "Change",
    "IN": "Inquiry",
    "NO": "Notice",
    "PR": "Problem",
    "RP": "Response",
    "RQ": "Request",
    "ST": "Status",
}

PARTY_TYPE_CODES = {
    "FR": "From (Sender)",
    "TO": "To (Recipient)",
    "40": "Receiver",
    "41": "Submitter",
}


class EDI864Parser(BaseEDIParser):
    """Parser for EDI 864 Text Message documents."""
    
    TRANSACTION_TYPE = "864"
    TRANSACTION_NAME = "Text Message"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 864 Text Message segments."""
        
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
        
        # Parse BMG (Beginning Segment for Text Message)
        bmg = self.get_segment_by_id(segments, "BMG")
        if bmg:
            elements = bmg["elements"]
            
            # BMG01 - Transaction Set Purpose Code
            if len(elements) > 0 and elements[0]:
                purpose = elements[0]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
            
            # BMG02 - Description
            if len(elements) > 1 and elements[1]:
                document.header["subject"] = elements[1]
            
            # BMG03 - Transaction Type Code
            if len(elements) > 2 and elements[2]:
                document.header["transaction_type_code"] = elements[2]
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                
                if qualifier == "097":  # Transaction Creation
                    document.header["message_date"] = self._format_date(date_value)
                    document.date = document.header["message_date"]
                else:
                    if "dates" not in document.header:
                        document.header["dates"] = {}
                    document.header["dates"][f"Date ({qualifier})"] = self._format_date(date_value)
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Extract sender and recipient
        for party in document.header.get("parties", []):
            if party.get("type_code") in ["FR", "41"]:
                document.header["from"] = party
            elif party.get("type_code") in ["TO", "40"]:
                document.header["to"] = party
        
        # Parse MIT (Message Identification) / MSG (Message Text) / MTX (Text)
        self._parse_messages(segments, document)
        
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
            
            # Look for PER (Contact)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "PER":
                    per = parsed_segments[i]
                    party["contact_name"] = per["elements"][1] if len(per["elements"]) > 1 else None
                    if len(per["elements"]) > 3:
                        party["contact_number"] = per["elements"][3]
                    break
            
            # Look for REF (Reference)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "REF":
                    ref = parsed_segments[i]
                    if len(ref["elements"]) >= 2:
                        if "references" not in party:
                            party["references"] = []
                        party["references"].append({
                            "qualifier": ref["elements"][0],
                            "value": ref["elements"][1],
                        })
            
            parties.append(party)
        
        return parties
    
    def _parse_messages(self, segments: list, document: EDIDocument) -> None:
        """Parse MIT/MSG/MTX message content."""
        
        # Parse all segments first since we need to look ahead
        parsed_segments = [self._parse_segment(s) for s in segments]
        
        # Find all MIT (Message Identification) segments
        mit_indices = []
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "MIT":
                mit_indices.append(i)
        
        messages = []
        
        if mit_indices:
            # Messages are structured in MIT loops
            for idx, mit_idx in enumerate(mit_indices):
                mit = parsed_segments[mit_idx]
                end_idx = mit_indices[idx + 1] if idx + 1 < len(mit_indices) else len(parsed_segments)
                
                message = {
                    "message_number": str(len(messages) + 1),
                }
                
                # MIT01 - Reference Identification
                if len(mit["elements"]) > 0 and mit["elements"][0]:
                    message["reference_id"] = mit["elements"][0]
                
                # MIT02 - Description (Subject)
                if len(mit["elements"]) > 1 and mit["elements"][1]:
                    message["subject"] = mit["elements"][1]
                
                # Collect message text from MSG/MTX segments
                text_parts = []
                for i in range(mit_idx + 1, end_idx):
                    seg = parsed_segments[i]
                    
                    if seg["id"] == "MSG":  # Message Text
                        if len(seg["elements"]) > 0 and seg["elements"][0]:
                            text_parts.append(seg["elements"][0])
                    
                    elif seg["id"] == "MTX":  # Text
                        # MTX01 - Note Reference Code
                        # MTX02 - Text
                        if len(seg["elements"]) > 1 and seg["elements"][1]:
                            text_parts.append(seg["elements"][1])
                        elif len(seg["elements"]) > 0 and seg["elements"][0]:
                            text_parts.append(seg["elements"][0])
                
                if text_parts:
                    message["text"] = "\n".join(text_parts)
                
                messages.append(message)
        else:
            # No MIT segments - collect all MSG/MTX directly
            text_parts = []
            for seg in parsed_segments:
                if seg["id"] == "MSG":
                    if len(seg["elements"]) > 0 and seg["elements"][0]:
                        text_parts.append(seg["elements"][0])
                elif seg["id"] == "MTX":
                    if len(seg["elements"]) > 1 and seg["elements"][1]:
                        text_parts.append(seg["elements"][1])
                    elif len(seg["elements"]) > 0 and seg["elements"][0]:
                        text_parts.append(seg["elements"][0])
            
            if text_parts:
                messages.append({
                    "message_number": "1",
                    "text": "\n".join(text_parts),
                })
        
        # Store messages
        document.header["messages"] = messages
        
        # Also add as line items for display consistency
        for msg in messages:
            line_item = {
                "line_number": msg.get("message_number", "1"),
                "subject": msg.get("subject"),
                "text": msg.get("text"),
                "reference_id": msg.get("reference_id"),
            }
            document.line_items.append(line_item)
        
        # Store combined message text in header
        if messages:
            all_text = []
            for msg in messages:
                if msg.get("subject"):
                    all_text.append(f"Subject: {msg['subject']}")
                if msg.get("text"):
                    all_text.append(msg["text"])
                all_text.append("")  # Separator
            document.header["full_message"] = "\n".join(all_text).strip()
        
        document.summary["total_messages"] = len(messages)
    
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
