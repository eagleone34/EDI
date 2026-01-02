"""
EDI 812 - Credit/Debit Adjustment Parser.
Enhanced to extract comprehensive adjustment details.
"""

from typing import Dict, Any, List
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 812-specific codes
TRANSACTION_HANDLING_CODES = {
    "C": "Off Invoice (Deduction from Original Invoice)",
    "D": "On Invoice (Addition to Original Invoice)",
    "I": "Invoice",
    "P": "Price Adjustment",
    "Z": "Mutually Defined",
    "A": "Off Invoice (Deduction from Original Invoice)",  # Mapped to match user expectation
}

CREDIT_DEBIT_FLAG_CODES = {
    "C": "Credit",
    "D": "Debit",
}

ADJUSTMENT_REASON_CODES = {
    "01": "Pricing Error",
    "02": "Quantity Error",
    "03": "Damaged Goods",
    "04": "Returns",
    "05": "Promotional Allowance",
    "06": "Early Payment Discount",
    "07": "Shipping/Handling",
    "08": "Advertising Allowance",
    "09": "Co-op Advertising",
    "10": "Defective Merchandise",
    "11": "Duplicate Payment",
    "12": "Late Delivery",
    "13": "Price Protection",
    "14": "Quality Issue",
    "15": "Short Shipment",
    "16": "Unauthorized Purchase",
    "17": "Volume Rebate",
    "18": "Warranty Claim",
    "AJ": "No open item on file",
    "ZZ": "Mutually Defined",
}

TRANSACTION_TYPE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "02": "Replacement",
    "03": "Add",
    "04": "Delete",
    "05": "Change",
    "08": "Debit Memo",
    "09": "Credit Memo",
}

PRICE_IDENTIFIER_CODES = {
    "UCP": "Unit cost price",
    "PUR": "Original Purchase Order Price",
    "CON": "Contract Price",
    "CUR": "Current Price",
    "NET": "Net Price",
    "QUO": "Quoted Price",
    "SRP": "Suggested Retail Price",
    "WHS": "Wholesale Price",
}

PARTY_TYPE_CODES = {
    "BY": "Buyer",
    "SE": "Seller",
    "SU": "Supplier/Manufacturer",
    "VN": "Vendor",
    "ST": "Ship To",
    "BT": "Bill To",
    "RI": "Remit To",
    "SF": "Ship From",
    "OC": "Original Claimant",
    "XI": "Customer Relations",
    "CR": "Customer Relations",
    "MA": "Manufacturer",
}


class EDI812Parser(BaseEDIParser):
    """Parser for EDI 812 Credit/Debit Adjustment documents."""
    
    TRANSACTION_TYPE = "812"
    TRANSACTION_NAME = "Credit/Debit Adjustment"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 812 Credit/Debit Adjustment segments."""
        
        document = EDIDocument(
            transaction_type=self.TRANSACTION_TYPE,
            transaction_name=self.TRANSACTION_NAME,
        )
        
        # Parse ISA (Interchange Control Header)
        isa = self.get_segment_by_id(segments, "ISA")
        if isa and len(isa["elements"]) >= 12:
            document.sender_id = isa["elements"][5].strip() if len(isa["elements"]) > 5 else None
            document.receiver_id = isa["elements"][7].strip() if len(isa["elements"]) > 7 else None
            document.control_number = isa["elements"][12].strip() if len(isa["elements"]) > 12 else None
        
        # Parse BCD (Beginning Credit/Debit Adjustment) - Primary segment for 812
        bcd = self.get_segment_by_id(segments, "BCD")
        if bcd:
            elements = bcd["elements"]
            
            # BCD01 - Date
            if len(elements) > 0 and elements[0]:
                date_raw = elements[0]
                document.header["adjustment_date"] = self._format_date(date_raw)
                document.date = document.header["adjustment_date"]
            
            # BCD02 - Credit/Debit Adjustment Number
            if len(elements) > 1 and elements[1]:
                document.header["credit_debit_number"] = elements[1]
            
            # BCD03 - Transaction Handling Code
            if len(elements) > 2 and elements[2]:
                code = elements[2]
                document.header["transaction_handling_code"] = code
                document.header["transaction_handling_desc"] = TRANSACTION_HANDLING_CODES.get(code, code)
            
            # BCD04 - Amount (in cents, divide by 100)
            if len(elements) > 3 and elements[3]:
                try:
                    amount_cents = int(elements[3])
                    document.header["amount"] = amount_cents / 100
                except ValueError:
                    document.header["amount"] = elements[3]
            
            # BCD05 - Credit/Debit Flag Code
            if len(elements) > 4 and elements[4]:
                code = elements[4]
                document.header["credit_debit_flag"] = code
                document.header["credit_debit_flag_desc"] = CREDIT_DEBIT_FLAG_CODES.get(code, code)
            
            # BCD06 - Date (secondary date, often invoice date)
            if len(elements) > 5 and elements[5]:
                document.header["secondary_date"] = self._format_date(elements[5])
            
            # BCD07 - Invoice Number
            if len(elements) > 6 and elements[6]:
                document.header["invoice_number"] = elements[6]
            
            # BCD08 - Date (PO Date in this context?)
            if len(elements) > 8 and elements[8]:
                document.header["po_date"] = self._format_date(elements[8])
            
            # BCD09 - Purchase Order Number
            if len(elements) > 9 and elements[9]:
                document.header["po_number"] = elements[9]
            
            # BCD10 - Transaction Set Purpose Code
            if len(elements) > 10 and elements[10]:
                document.header["purpose_code"] = elements[10]
            
            # BCD11 - Transaction Type Code
            if len(elements) > 11 and elements[11]:
                code = elements[11]
                document.header["transaction_type_code"] = code
                document.header["transaction_type_desc"] = TRANSACTION_TYPE_CODES.get(code, code)
        
        # Parse CUR (Currency)
        cur = self.get_segment_by_id(segments, "CUR")
        if cur and len(cur["elements"]) > 1:
            document.header["currency"] = cur["elements"][1]
        
        # Parse REF (Reference Identification) segments
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2 and ref["elements"][1]:
                ref_qual = ref["elements"][0]
                ref_val = ref["elements"][1]
                ref_desc = ref["elements"][2] if len(ref["elements"]) > 2 else None
                
                document.header["references"].append({
                    "qualifier": ref_qual,
                    "value": ref_val,
                    "description": ref_desc,
                })
                
                # Store specific references
                if ref_qual in ["IV", "IN"]:
                    document.header["invoice_number"] = ref_val
                elif ref_qual == "PO":
                    document.header["po_number"] = ref_val
        
        # Parse PER (Administrative Communications Contact)
        per_segments = self.get_all_segments_by_id(segments, "PER")
        document.header["contacts"] = []
        for per in per_segments:
            if len(per["elements"]) >= 2:
                contact = {
                    "function": per["elements"][0],
                    "name": per["elements"][1] if len(per["elements"]) > 1 else None,
                }
                # Communication numbers
                if len(per["elements"]) > 3:
                    contact["comm_type"] = per["elements"][2]
                    contact["comm_number"] = per["elements"][3]
                if len(per["elements"]) > 5:
                    contact["comm_type2"] = per["elements"][4]
                    contact["comm_number2"] = per["elements"][5]
                document.header["contacts"].append(contact)
        
        # Parse N1/N2/N3/N4 (Name and Address) segments
        document.header["parties"] = self._parse_parties(segments)
        
        # Parse CDD (Credit/Debit Adjustment Detail) segments - line items
        cdd_segments = self.get_all_segments_by_id(segments, "CDD")
        current_line_index = 0
        
        for cdd in cdd_segments:
            current_line_index += 1
            elements = cdd["elements"]
            
            line_item = {
                "line_number": str(current_line_index),
            }
            
            # CDD01 - Adjustment Reason Code
            if len(elements) > 0 and elements[0]:
                code = elements[0]
                line_item["adjustment_reason_code"] = code
                line_item["adjustment_reason"] = ADJUSTMENT_REASON_CODES.get(code, code)
            
            # CDD02 - Credit/Debit Flag Code
            if len(elements) > 1 and elements[1]:
                code = elements[1]
                line_item["credit_debit_flag"] = code
                line_item["credit_debit_type"] = CREDIT_DEBIT_FLAG_CODES.get(code, code)
            
            # CDD03 - Assigned Identification
            if len(elements) > 2 and elements[2]:
                line_item["assigned_id"] = elements[2]
            
            # CDD04 - Amount (adjustment amount in cents)
            if len(elements) > 3 and elements[3]:
                try:
                    amount_cents = float(elements[3])
                    line_item["adjustment_amount"] = amount_cents / 100
                except ValueError:
                    line_item["adjustment_amount"] = elements[3]
            
            # CDD05 - Credit/Debit Quantity
            if len(elements) > 4 and elements[4]:
                line_item["quantity"] = elements[4]
            
            # CDD06 - Unit or Basis for Measurement Code
            if len(elements) > 5 and elements[5]:
                line_item["unit"] = elements[5]
            
            # CDD07 - Price Identifier Code
            if len(elements) > 6 and elements[6]:
                code = elements[6]
                line_item["price_id_code"] = code
                line_item["price_id_desc"] = PRICE_IDENTIFIER_CODES.get(code, code)
            
            # CDD08 - Unit Price
            if len(elements) > 7 and elements[7]:
                try:
                    line_item["unit_price"] = float(elements[7])
                except ValueError:
                    line_item["unit_price"] = elements[7]
            
            # CDD09 - Price Identifier Code (for original price)
            if len(elements) > 8 and elements[8]:
                code = elements[8]
                line_item["original_price_id_code"] = code
                line_item["original_price_id_desc"] = PRICE_IDENTIFIER_CODES.get(code, code)
            
            # CDD10 - Unit Price (original purchase order price)
            if len(elements) > 9 and elements[9]:
                try:
                    line_item["original_unit_price"] = float(elements[9])
                except ValueError:
                    line_item["original_unit_price"] = elements[9]
            
            document.line_items.append(line_item)
        
        # Parse MSG (Message Text) for free-form messages
        msg_segments = self.get_all_segments_by_id(segments, "MSG")
        for i, msg in enumerate(msg_segments):
            if len(msg["elements"]) > 0 and msg["elements"][0]:
                # Try to associate with last line item
                if document.line_items and i < len(document.line_items):
                    document.line_items[i]["message"] = msg["elements"][0]
                elif document.line_items:
                    document.line_items[-1]["message"] = msg["elements"][0]
        
        # Parse LIN (Item Identification) for part numbers
        lin_segments = self.get_all_segments_by_id(segments, "LIN")
        for i, lin in enumerate(lin_segments):
            if i < len(document.line_items):
                part_numbers = {}
                # Parse product ID qualifiers and values
                j = 1
                while j + 1 < len(lin["elements"]):
                    qualifier = lin["elements"][j]
                    value = lin["elements"][j + 1] if j + 1 < len(lin["elements"]) else None
                    if qualifier and value:
                        # Map common qualifiers
                        qual_map = {
                            "BP": "Buyer's Part Number",
                            "UP": "U.P.C. Consumer Package Code",
                            "PI": "Purchaser's Item Code",
                            "VP": "Vendor's Part Number",
                            "MG": "Manufacturer's Part Number",
                            "EN": "EAN/UCC-13",
                        }
                        label = qual_map.get(qualifier, qualifier)
                        part_numbers[label] = value
                    j += 2
                document.line_items[i]["part_numbers"] = part_numbers
        
        # Parse SAC (Service, Promotion, Allowance, or Charge Information)
        sac_segments = self.get_all_segments_by_id(segments, "SAC")
        document.header["allowances_charges"] = []
        for sac in sac_segments:
            if len(sac["elements"]) > 0:
                entry = {
                    "indicator": sac["elements"][0],  # A=Allowance, C=Charge
                    "type": "Allowance" if sac["elements"][0] == "A" else "Charge" if sac["elements"][0] == "C" else sac["elements"][0],
                }
                if len(sac["elements"]) > 1:
                    entry["code"] = sac["elements"][1]
                if len(sac["elements"]) > 4:
                    try:
                        entry["amount"] = float(sac["elements"][4]) / 100
                    except:
                        entry["amount"] = sac["elements"][4]
                if len(sac["elements"]) > 14:
                    entry["description"] = sac["elements"][14]
                document.header["allowances_charges"].append(entry)
        
        # Parse TDS (Total Monetary Value Summary)
        tds = self.get_segment_by_id(segments, "TDS")
        if tds and len(tds["elements"]) > 0:
            try:
                total_cents = int(tds["elements"][0])
                document.summary["total_amount"] = total_cents / 100
            except ValueError:
                document.summary["total_amount"] = tds["elements"][0]
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
        
        return document
    
    def _parse_parties(self, segments: list) -> List[Dict]:
        """Parse all party-related segments (N1, N2, N3, N4)."""
        parties = []
        n1_segments = self.get_all_segments_by_id(segments, "N1")
        n2_segments = self.get_all_segments_by_id(segments, "N2")
        n3_segments = self.get_all_segments_by_id(segments, "N3")
        n4_segments = self.get_all_segments_by_id(segments, "N4")
        
        for i, n1 in enumerate(n1_segments):
            elements = n1["elements"]
            party_code = elements[0] if len(elements) > 0 else None
            
            party = {
                "type_code": party_code,
                "type": PARTY_TYPE_CODES.get(party_code, party_code),
                "name": elements[1] if len(elements) > 1 else None,
            }
            
            # ID qualifier and ID
            if len(elements) > 2 and elements[2]:
                party["id_qualifier"] = elements[2]
                # Translate common qualifiers
                qual_map = {"1": "DUNS", "9": "DUNS+4", "UL": "GLN (Global Location Number)", "92": "Assigned by Buyer"}
                party["id_qualifier_desc"] = qual_map.get(elements[2], elements[2])
            if len(elements) > 3 and elements[3]:
                party["id"] = elements[3]
            
            # Additional name from N2 (if exists at same index)
            if i < len(n2_segments):
                n2 = n2_segments[i]
                if len(n2["elements"]) > 0 and n2["elements"][0]:
                    party["additional_name"] = n2["elements"][0]
            
            # Address from N3 (if exists at same index)
            if i < len(n3_segments):
                n3 = n3_segments[i]
                if len(n3["elements"]) > 0:
                    party["address_line1"] = n3["elements"][0]
                if len(n3["elements"]) > 1:
                    party["address_line2"] = n3["elements"][1]
            
            # City/State/Zip from N4 (if exists at same index)
            if i < len(n4_segments):
                n4 = n4_segments[i]
                if len(n4["elements"]) > 0:
                    party["city"] = n4["elements"][0]
                if len(n4["elements"]) > 1:
                    party["state"] = n4["elements"][1]
                if len(n4["elements"]) > 2:
                    party["zip"] = n4["elements"][2]
                if len(n4["elements"]) > 3:
                    party["country"] = n4["elements"][3]
            
            parties.append(party)
        
        return parties
    
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
