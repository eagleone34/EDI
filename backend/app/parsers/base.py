"""
Base EDI Parser class.

All transaction-specific parsers inherit from this base class.
Supports parsing multiple transaction sets (ST/SE) from a single interchange.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class EDIDocument:
    """Parsed EDI document structure."""
    
    transaction_type: str
    transaction_name: str
    sender_id: Optional[str] = None
    receiver_id: Optional[str] = None
    control_number: Optional[str] = None
    date: Optional[str] = None
    header: Dict[str, Any] = None
    line_items: list = None
    summary: Dict[str, Any] = None
    raw_segments: list = None
    
    def __post_init__(self):
        if self.header is None:
            self.header = {}
        if self.line_items is None:
            self.line_items = []
        if self.summary is None:
            self.summary = {}
        if self.raw_segments is None:
            self.raw_segments = []


class BaseEDIParser(ABC):
    """
    Abstract base class for EDI parsers.
    
    Each transaction type (850, 810, etc.) has its own parser
    that inherits from this class.
    """
    
    # Override in subclasses
    TRANSACTION_TYPE: str = ""
    TRANSACTION_NAME: str = ""
    
    def __init__(self):
        self.segment_terminator = "~"
        self.element_separator = "*"
        self.sub_element_separator = ":"
    
    def parse(self, content: str) -> EDIDocument:
        """
        Parse EDI content into a structured document.
        Returns the FIRST transaction set found.
        
        Args:
            content: Raw EDI file content
            
        Returns:
            Parsed EDIDocument (first transaction set)
        """
        documents = self.parse_all(content)
        if documents:
            return documents[0]
        
        # Return empty document if no transaction sets found
        return EDIDocument(
            transaction_type=self.TRANSACTION_TYPE,
            transaction_name=self.TRANSACTION_NAME,
        )
    
    def parse_all(self, content: str) -> List[EDIDocument]:
        """
        Parse ALL transaction sets from an EDI interchange.
        
        An EDI file can contain multiple transaction sets (ST/SE loops).
        This method parses each one separately.
        
        Args:
            content: Raw EDI file content
            
        Returns:
            List of parsed EDIDocument objects
        """
        # Detect delimiters from ISA segment if present
        self._detect_delimiters(content)
        
        # Split into segments
        all_segments = self._split_segments(content)
        
        # Extract ISA/GS envelope data
        isa_data = self._extract_envelope_data(all_segments)
        
        # Split into transaction sets (ST to SE)
        transaction_sets = self._split_transaction_sets(all_segments)
        
        # Parse each transaction set
        documents = []
        for ts_segments in transaction_sets:
            # Combine envelope segments with transaction set for context
            full_segments = isa_data["envelope_segments"] + ts_segments
            document = self._parse_segments(full_segments)
            document.raw_segments = ts_segments
            
            # Apply envelope data if not already set
            if not document.sender_id:
                document.sender_id = isa_data.get("sender_id")
            if not document.receiver_id:
                document.receiver_id = isa_data.get("receiver_id")
            if not document.control_number:
                document.control_number = isa_data.get("control_number")
            if not document.date:
                document.date = isa_data.get("date")
                
            documents.append(document)
        
        return documents
    
    def _extract_envelope_data(self, segments: list) -> Dict[str, Any]:
        """Extract ISA/GS envelope data that applies to all transaction sets."""
        envelope_segments = []
        data = {}
        
        for seg in segments:
            parsed = self._parse_segment(seg)
            seg_id = parsed["id"]
            
            if seg_id == "ISA":
                envelope_segments.append(seg)
                elems = parsed["elements"]
                data["sender_id"] = elems[5].strip() if len(elems) > 5 else None
                data["receiver_id"] = elems[7].strip() if len(elems) > 7 else None
                data["control_number"] = elems[12].strip() if len(elems) > 12 else None
                # Date from ISA09
                if len(elems) > 8:
                    isa_date = elems[8].strip()
                    if len(isa_date) == 6:
                        data["date"] = f"20{isa_date[:2]}-{isa_date[2:4]}-{isa_date[4:6]}"
                        
            elif seg_id == "GS":
                envelope_segments.append(seg)
                elems = parsed["elements"]
                if len(elems) > 3:
                    gs_date = elems[3]
                    if len(gs_date) == 8:
                        data["date"] = f"{gs_date[:4]}-{gs_date[4:6]}-{gs_date[6:8]}"
            
            elif seg_id in ("GE", "IEA"):
                # Stop processing envelope after header
                break
            elif seg_id == "ST":
                # Stop at first transaction set
                break
        
        data["envelope_segments"] = envelope_segments
        return data
    
    def _split_transaction_sets(self, segments: list) -> List[List[str]]:
        """Split segments into individual transaction sets (ST to SE)."""
        transaction_sets = []
        current_ts = []
        in_transaction = False
        
        for seg in segments:
            parsed = self._parse_segment(seg)
            seg_id = parsed["id"]
            
            if seg_id == "ST":
                # Start of new transaction set
                in_transaction = True
                current_ts = [seg]
            elif seg_id == "SE":
                # End of transaction set
                if in_transaction:
                    current_ts.append(seg)
                    transaction_sets.append(current_ts)
                    current_ts = []
                    in_transaction = False
            elif in_transaction:
                current_ts.append(seg)
        
        return transaction_sets
    
    def _detect_delimiters(self, content: str) -> None:
        """Detect delimiters from the ISA segment."""
        content = content.strip()
        
        if content.startswith("ISA"):
            # Element separator is character at position 3
            self.element_separator = content[3]
            
            # Sub-element separator is at position 104
            if len(content) > 104:
                self.sub_element_separator = content[104]
            
            # Segment terminator is at position 105
            if len(content) > 105:
                self.segment_terminator = content[105]
    
    def _split_segments(self, content: str) -> list:
        """Split content into segments."""
        # Handle cases where newline is the terminator
        if self.segment_terminator in ["\n", "\r", "\r\n"]:
            segments = content.split(self.segment_terminator)
            # Remove empty strings from split
            return [s.strip() for s in segments if s.strip()]
            
        # Standard case: content might have formatting newlines to remove
        content = content.replace("\r\n", "").replace("\n", "").replace("\r", "")
        
        # Split by segment terminator
        segments = content.split(self.segment_terminator)
        
        # Clean up and filter empty segments
        segments = [s.strip() for s in segments if s.strip()]
        
        return segments
    
    def _parse_segment(self, segment: Union[str, Dict]) -> Dict[str, Any]:
        """Parse a single segment into elements."""
        if isinstance(segment, dict):
            return segment
            
        elements = segment.split(self.element_separator)
        return {
            "id": elements[0] if elements else "",
            "elements": elements[1:] if len(elements) > 1 else [],
        }
    
    @abstractmethod
    def _parse_segments(self, segments: list) -> EDIDocument:
        """
        Parse segments into a structured document.
        
        Must be implemented by subclasses.
        """
        pass
    
    def get_segment_by_id(self, segments: list, segment_id: str) -> Optional[Dict[str, Any]]:
        """Get the first segment matching the given ID."""
        for segment in segments:
            parsed = self._parse_segment(segment)
            if parsed["id"] == segment_id:
                return parsed
        return None
    
    def get_all_segments_by_id(self, segments: list, segment_id: str) -> list:
        """Get all segments matching the given ID."""
        result = []
        for segment in segments:
            parsed = self._parse_segment(segment)
            if parsed["id"] == segment_id:
                result.append(parsed)
        return result
