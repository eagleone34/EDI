from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class LayoutField(BaseModel):
    """Refers to a single data field to display."""
    key: str  # The key in the parsed data dict (e.g., "po_number")
    label: str # The user-facing label (e.g., "Purchase Order #")
    type: str = "text" # text, date, currency, number, status
    style: Optional[str] = None # bold, highlight, etc.
    format_string: Optional[str] = None # For dates/numbers
    visible: bool = True

class LayoutColumn(BaseModel):
    """Defines a column in a table (like Line Items)."""
    key: str
    label: str
    width: Optional[str] = None
    type: str = "text"
    format_string: Optional[str] = None
    style: Optional[str] = None
    visible: bool = True

class LayoutDetail(BaseModel): # Assuming BaseModel as LayoutSummary is not defined
    config_json: 'LayoutConfig' # Forward reference
    is_personal: bool = False

class LayoutSection(BaseModel):
    """A visual grouping of fields (e.g., 'Order Information')."""
    id: str  # unique id for the section
    title: str
    type: str = "fields" # 'fields', 'table', 'grid'
    visible: bool = True
    
    # For 'fields' type
    fields: List[LayoutField] = []
    
    # For 'table' type
    columns: List[LayoutColumn] = []
    data_source_key: Optional[str] = None # e.g., "line_items"

    # Styling
    background_color: Optional[str] = None

class LayoutConfig(BaseModel):
    """The complete configuration for a transaction type's HTML output."""
    title_format: str = "{name} #{ref_number}" # e.g., "Purchase Order #123456"
    
    # Global styles
    theme_color: str = "blue" # blue, green, purple
    
    # Defines the order and content of sections
    sections: List[LayoutSection]
    
    class Config:
        from_attributes = True
