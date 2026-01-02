"""
EDI Parsers module.

Provides parsers for various EDI transaction sets.
"""

from app.parsers.base import BaseEDIParser
from app.parsers.edi_850 import EDI850Parser
from app.parsers.edi_810 import EDI810Parser
from app.parsers.edi_812 import EDI812Parser
from app.parsers.edi_856 import EDI856Parser
from app.parsers.edi_855 import EDI855Parser
from app.parsers.edi_997 import EDI997Parser

__all__ = [
    "BaseEDIParser",
    "EDI850Parser",
    "EDI810Parser",
    "EDI812Parser",
    "EDI856Parser",
    "EDI855Parser",
    "EDI997Parser",
]


def get_parser(transaction_type: str) -> BaseEDIParser:
    """Get the appropriate parser for a transaction type."""
    parsers = {
        "850": EDI850Parser,
        "810": EDI810Parser,
        "812": EDI812Parser,
        "856": EDI856Parser,
        "855": EDI855Parser,
        "997": EDI997Parser,
    }
    
    parser_class = parsers.get(transaction_type)
    if not parser_class:
        raise ValueError(f"Unsupported transaction type: {transaction_type}")
    
    return parser_class()
