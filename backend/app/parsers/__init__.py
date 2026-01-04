"""
EDI Parsers module.

Provides parsers for various EDI transaction sets.
"""

from app.parsers.base import BaseEDIParser
from app.parsers.edi_810 import EDI810Parser
from app.parsers.edi_812 import EDI812Parser
from app.parsers.edi_816 import EDI816Parser
from app.parsers.edi_820 import EDI820Parser
from app.parsers.edi_824 import EDI824Parser
from app.parsers.edi_830 import EDI830Parser
from app.parsers.edi_850 import EDI850Parser
from app.parsers.edi_852 import EDI852Parser
from app.parsers.edi_855 import EDI855Parser
from app.parsers.edi_856 import EDI856Parser
from app.parsers.edi_860 import EDI860Parser
from app.parsers.edi_861 import EDI861Parser
from app.parsers.edi_864 import EDI864Parser
from app.parsers.edi_870 import EDI870Parser
from app.parsers.edi_875 import EDI875Parser
from app.parsers.edi_880 import EDI880Parser
from app.parsers.edi_997 import EDI997Parser

__all__ = [
    "BaseEDIParser",
    "EDI810Parser",
    "EDI812Parser",
    "EDI816Parser",
    "EDI820Parser",
    "EDI824Parser",
    "EDI830Parser",
    "EDI850Parser",
    "EDI852Parser",
    "EDI855Parser",
    "EDI856Parser",
    "EDI860Parser",
    "EDI861Parser",
    "EDI864Parser",
    "EDI870Parser",
    "EDI875Parser",
    "EDI880Parser",
    "EDI997Parser",
]


def get_parser(transaction_type: str) -> BaseEDIParser:
    """Get the appropriate parser for a transaction type."""
    parsers = {
        "810": EDI810Parser,
        "812": EDI812Parser,
        "816": EDI816Parser,
        "820": EDI820Parser,
        "824": EDI824Parser,
        "830": EDI830Parser,
        "850": EDI850Parser,
        "852": EDI852Parser,
        "855": EDI855Parser,
        "856": EDI856Parser,
        "860": EDI860Parser,
        "861": EDI861Parser,
        "864": EDI864Parser,
        "870": EDI870Parser,
        "875": EDI875Parser,
        "880": EDI880Parser,
        "997": EDI997Parser,
    }
    
    parser_class = parsers.get(transaction_type)
    if not parser_class:
        raise ValueError(f"Unsupported transaction type: {transaction_type}")
    
    return parser_class()
