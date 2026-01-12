"""
EDI 816 - Organizational Relationships Parser.
Defines organizational hierarchies and relationships.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 816-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "05": "Replace",
    "22": "Information Copy",
}

ENTITY_TYPE_CODES = {
    "1": "Person",
    "2": "Non-Person Entity",
    "3": "Unknown",
}

RELATIONSHIP_CODES = {
    "01": "Parent Company",
    "02": "Subsidiary",
    "03": "Division",
    "04": "Branch",
    "05": "Department",
    "06": "Affiliate",
    "07": "Partner",
    "08": "Agent",
    "09": "Representative",
}

PARTY_TYPE_CODES = {
    "01": "Reporting Party",
    "02": "Subject Party",
    "41": "Submitter",
    "EN": "Entity Name",
    "OC": "Original Creditor",
}


class EDI816Parser(BaseEDIParser):
    """Parser for EDI 816 Organizational Relationships documents."""
    
    TRANSACTION_TYPE = "816"
    TRANSACTION_NAME = "Organizational Relationships"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 816 Organizational Relationships segments."""
        
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
        
        # Parse BGN (Beginning Segment)
        bgn = self.get_segment_by_id(segments, "BGN")
        if bgn:
            elements = bgn["elements"]
            
            # BGN01 - Transaction Set Purpose Code
            if len(elements) > 0 and elements[0]:
                purpose = elements[0]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
            
            # BGN02 - Reference Identification
            if len(elements) > 1 and elements[1]:
                document.header["reference_id"] = elements[1]
            
            # BGN03 - Date
            if len(elements) > 2 and elements[2]:
                document.header["date"] = self._format_date(elements[2])
                document.date = document.header["date"]
            
            # BGN04 - Time
            if len(elements) > 3 and elements[3]:
                document.header["time"] = elements[3]
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                document.header["dates"][f"Date ({qualifier})"] = self._format_date(date_value)
        
        # Parse HL (Hierarchical Level) loops for organizational structure
        self._parse_hierarchy(segments, document)
        
        # Parse N1 (Name) segments outside of HL loops
        n1_segments = self.get_all_segments_by_id(segments, "N1")
        if n1_segments:
            document.header["parties"] = []
            for n1 in n1_segments:
                party = {
                    "type_code": n1["elements"][0] if len(n1["elements"]) > 0 else None,
                    "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
                    "id_qualifier": n1["elements"][2] if len(n1["elements"]) > 2 else None,
                    "id": n1["elements"][3] if len(n1["elements"]) > 3 else None,
                }
                document.header["parties"].append(party)
        
        return document
    
    def _parse_hierarchy(self, segments: list, document: EDIDocument) -> None:
        """Parse HL loops for organizational hierarchy."""
        
        # Parse all segments first since we need to look ahead
        parsed_segments = [self._parse_segment(s) for s in segments]
        
        hl_indices = []
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "HL":
                hl_indices.append(i)
        
        organizations = []
        
        for idx, hl_idx in enumerate(hl_indices):
            hl = parsed_segments[hl_idx]
            end_idx = hl_indices[idx + 1] if idx + 1 < len(hl_indices) else len(parsed_segments)
            
            org = {
                "hl_id": hl["elements"][0] if len(hl["elements"]) > 0 else None,
                "parent_id": hl["elements"][1] if len(hl["elements"]) > 1 else None,
                "level_code": hl["elements"][2] if len(hl["elements"]) > 2 else None,
            }
            
            # Parse segments within this HL loop
            for i in range(hl_idx + 1, end_idx):
                seg = parsed_segments[i]
                
                if seg["id"] == "NX1":  # Entity
                    elements = seg["elements"]
                    entity_type = elements[0] if len(elements) > 0 else None
                    org["entity_type_code"] = entity_type
                    org["entity_type"] = ENTITY_TYPE_CODES.get(entity_type, entity_type)
                    org["entity_id"] = elements[1] if len(elements) > 1 else None
                
                elif seg["id"] == "NM1":  # Individual/Organizational Name
                    elements = seg["elements"]
                    org["entity_type_qual"] = elements[0] if len(elements) > 0 else None
                    org["entity_type"] = elements[1] if len(elements) > 1 else None
                    org["name_last"] = elements[2] if len(elements) > 2 else None
                    org["name_first"] = elements[3] if len(elements) > 3 else None
                    org["name_middle"] = elements[4] if len(elements) > 4 else None
                    org["id_qualifier"] = elements[7] if len(elements) > 7 else None
                    org["id"] = elements[8] if len(elements) > 8 else None
                
                elif seg["id"] == "N1":  # Name (in HL loop)
                    elements = seg["elements"]
                    org["party_type"] = elements[0] if len(elements) > 0 else None
                    org["name"] = elements[1] if len(elements) > 1 else None
                    org["id_qualifier"] = elements[2] if len(elements) > 2 else None
                    org["id"] = elements[3] if len(elements) > 3 else None
                
                elif seg["id"] == "N3":  # Address
                    elements = seg["elements"]
                    org["address_line1"] = elements[0] if len(elements) > 0 else None
                    org["address_line2"] = elements[1] if len(elements) > 1 else None
                
                elif seg["id"] == "N4":  # Geographic Location
                    elements = seg["elements"]
                    org["city"] = elements[0] if len(elements) > 0 else None
                    org["state"] = elements[1] if len(elements) > 1 else None
                    org["zip"] = elements[2] if len(elements) > 2 else None
                    org["country"] = elements[3] if len(elements) > 3 else None
                
                elif seg["id"] == "REF":  # Reference
                    elements = seg["elements"]
                    if "references" not in org:
                        org["references"] = []
                    org["references"].append({
                        "qualifier": elements[0] if len(elements) > 0 else None,
                        "value": elements[1] if len(elements) > 1 else None,
                    })
            
            organizations.append(org)
            
            # Also add as line item for display
            line_item = {
                "line_number": str(len(document.line_items) + 1),
                "hl_id": org.get("hl_id"),
                "parent_id": org.get("parent_id"),
                "name": org.get("name") or f"{org.get('name_first', '')} {org.get('name_last', '')}".strip(),
                "entity_type": org.get("entity_type"),
                "id": org.get("id"),
                "city": org.get("city"),
                "state": org.get("state"),
            }
            document.line_items.append(line_item)
        
        document.header["organizations"] = organizations
        document.summary["total_organizations"] = len(organizations)
    
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
