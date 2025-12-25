"""
Base EDI Parser class.

All transaction-specific parsers inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
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
        
        Args:
            content: Raw EDI file content
            
        Returns:
            Parsed EDIDocument
        """
        # Detect delimiters from ISA segment if present
        self._detect_delimiters(content)
        
        # Split into segments
        segments = self._split_segments(content)
        
        # Parse the document
        document = self._parse_segments(segments)
        document.raw_segments = segments
        
        return document
    
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
        # Clean up content
        content = content.replace("\r\n", "").replace("\n", "").replace("\r", "")
        
        # Split by segment terminator
        segments = content.split(self.segment_terminator)
        
        # Clean up and filter empty segments
        segments = [s.strip() for s in segments if s.strip()]
        
        return segments
    
    def _parse_segment(self, segment: str) -> Dict[str, Any]:
        """Parse a single segment into elements."""
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
