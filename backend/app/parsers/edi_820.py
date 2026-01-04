"""
EDI 820 - Payment Order/Remittance Advice Parser.
Payment instructions and invoice reconciliation.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 820-specific codes
TRANSACTION_HANDLING_CODES = {
    "C": "Payment Accompanies Remittance Advice",
    "D": "Make Payment Only",
    "I": "Remittance Information Only",
    "P": "Prenotification of Future Transfers",
    "U": "Split Payment and Remittance",
    "X": "Handling Party Option to Split Payment and Remittance",
    "Z": "Mutually Defined",
}

PAYMENT_METHOD_CODES = {
    "ACH": "Automated Clearing House",
    "BOP": "Financial Institution Option",
    "CHK": "Check",
    "FWT": "Federal Reserve Funds/Wire Transfer",
    "NON": "Non-Payment Data",
}

CREDIT_DEBIT_FLAG_CODES = {
    "C": "Credit",
    "D": "Debit",
}

REFERENCE_QUALIFIERS = {
    "IV": "Invoice Number",
    "PO": "Purchase Order Number",
    "VN": "Vendor Order Number",
    "VR": "Vendor ID Number",
    "CR": "Customer Reference Number",
    "OI": "Original Invoice Number",
    "BM": "Bill of Lading Number",
}

ADJUSTMENT_REASON_CODES = {
    "01": "Pricing Error",
    "02": "Extension Error",
    "03": "Item Not Received",
    "04": "Quality Problem",
    "05": "Item Damaged",
    "06": "Wrong Item Shipped",
    "07": "Duplicate Invoice",
    "08": "Terms Discount",
    "09": "Early Payment Discount",
    "10": "Returns",
    "ZZ": "Mutually Defined",
}

PARTY_TYPE_CODES = {
    "PR": "Payer",
    "PE": "Payee",
    "BO": "Broker or Sales Office",
    "SF": "Ship From",
    "ST": "Ship To",
    "VN": "Vendor",
}


class EDI820Parser(BaseEDIParser):
    """Parser for EDI 820 Payment Order/Remittance Advice documents."""
    
    TRANSACTION_TYPE = "820"
    TRANSACTION_NAME = "Payment Order/Remittance Advice"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 820 Payment Order/Remittance Advice segments."""
        
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
        
        # Parse BPR (Beginning Segment for Payment Order/Remittance Advice)
        bpr = self.get_segment_by_id(segments, "BPR")
        if bpr:
            elements = bpr["elements"]
            
            # BPR01 - Transaction Handling Code
            if len(elements) > 0 and elements[0]:
                code = elements[0]
                document.header["transaction_handling_code"] = code
                document.header["transaction_handling"] = TRANSACTION_HANDLING_CODES.get(code, code)
            
            # BPR02 - Monetary Amount
            if len(elements) > 1 and elements[1]:
                try:
                    document.header["payment_amount"] = float(elements[1])
                except:
                    document.header["payment_amount"] = elements[1]
            
            # BPR03 - Credit/Debit Flag
            if len(elements) > 2 and elements[2]:
                flag = elements[2]
                document.header["credit_debit_flag"] = flag
                document.header["credit_debit"] = CREDIT_DEBIT_FLAG_CODES.get(flag, flag)
            
            # BPR04 - Payment Method Code
            if len(elements) > 3 and elements[3]:
                method = elements[3]
                document.header["payment_method_code"] = method
                document.header["payment_method"] = PAYMENT_METHOD_CODES.get(method, method)
            
            # BPR05 - Payment Format Code
            if len(elements) > 4 and elements[4]:
                document.header["payment_format"] = elements[4]
            
            # BPR16 - Date (Check/EFT Date)
            if len(elements) > 15 and elements[15]:
                document.header["payment_date"] = self._format_date(elements[15])
                document.date = document.header["payment_date"]
        
        # Parse TRN (Trace)
        trn = self.get_segment_by_id(segments, "TRN")
        if trn:
            elements = trn["elements"]
            document.header["trace"] = {
                "trace_type": elements[0] if len(elements) > 0 else None,
                "reference_id": elements[1] if len(elements) > 1 else None,
                "originator_id": elements[2] if len(elements) > 2 else None,
            }
            document.header["trace_number"] = elements[1] if len(elements) > 1 else None
        
        # Parse CUR (Currency)
        cur = self.get_segment_by_id(segments, "CUR")
        if cur and len(cur["elements"]) > 1:
            document.header["currency"] = cur["elements"][1]
        
        # Parse REF (Reference Identification)
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                qualifier = ref["elements"][0]
                value = ref["elements"][1]
                document.header["references"].append({
                    "qualifier": qualifier,
                    "qualifier_desc": REFERENCE_QUALIFIERS.get(qualifier, qualifier),
                    "value": value,
                })
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                document.header["dates"][f"Date ({qualifier})"] = self._format_date(date_value)
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Extract specific parties
        for party in document.header.get("parties", []):
            if party.get("type_code") == "PR":
                document.header["payer"] = party
            elif party.get("type_code") == "PE":
                document.header["payee"] = party
        
        # Parse ENT/RMR/ADX loops (Remittance Detail)
        self._parse_remittance_details(segments, document)
        
        return document
    
    def _parse_parties(self, segments: list) -> List[Dict]:
        """Parse party information."""
        parties = []
        
        n1_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "N1":
                n1_indices.append(i)
        
        for idx, n1_idx in enumerate(n1_indices):
            n1 = segments[n1_idx]
            end_idx = n1_indices[idx + 1] if idx + 1 < len(n1_indices) else len(segments)
            
            party_code = n1["elements"][0] if len(n1["elements"]) > 0 else None
            
            party = {
                "type_code": party_code,
                "type": PARTY_TYPE_CODES.get(party_code, party_code),
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
                "id_qualifier": n1["elements"][2] if len(n1["elements"]) > 2 else None,
                "id": n1["elements"][3] if len(n1["elements"]) > 3 else None,
            }
            
            # Look for N3 (Address)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments) and segments[i]["id"] == "N3":
                    n3 = segments[i]
                    party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                    party["address_line2"] = n3["elements"][1] if len(n3["elements"]) > 1 else None
                    break
            
            # Look for N4 (Geographic Location)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments) and segments[i]["id"] == "N4":
                    n4 = segments[i]
                    party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                    party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                    party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
                    party["country"] = n4["elements"][3] if len(n4["elements"]) > 3 else None
                    break
            
            parties.append(party)
        
        return parties
    
    def _parse_remittance_details(self, segments: list, document: EDIDocument) -> None:
        """Parse ENT/RMR/REF/ADX loops for remittance details."""
        
        # Find RMR segments (Remittance Advice Accounts Receivable Open Item Reference)
        rmr_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "RMR":
                rmr_indices.append(i)
        
        total_paid = 0
        total_adjustments = 0
        
        for idx, rmr_idx in enumerate(rmr_indices):
            rmr = segments[rmr_idx]
            end_idx = rmr_indices[idx + 1] if idx + 1 < len(rmr_indices) else len(segments)
            
            elements = rmr["elements"]
            
            line_item = {
                "line_number": str(len(document.line_items) + 1),
            }
            
            # RMR01 - Reference Identification Qualifier
            if len(elements) > 0 and elements[0]:
                qual = elements[0]
                line_item["reference_qualifier"] = qual
                line_item["reference_qualifier_desc"] = REFERENCE_QUALIFIERS.get(qual, qual)
            
            # RMR02 - Reference Identification (usually Invoice Number)
            if len(elements) > 1 and elements[1]:
                line_item["invoice_number"] = elements[1]
            
            # RMR03 - Payment Action Code
            if len(elements) > 2 and elements[2]:
                action_codes = {
                    "PA": "Partially Paid",
                    "PP": "Paid in Full",
                    "PD": "Past Due",
                }
                line_item["payment_action_code"] = elements[2]
                line_item["payment_action"] = action_codes.get(elements[2], elements[2])
            
            # RMR04 - Monetary Amount (Original Invoice Amount)
            if len(elements) > 3 and elements[3]:
                try:
                    line_item["invoice_amount"] = float(elements[3])
                except:
                    line_item["invoice_amount"] = elements[3]
            
            # RMR05 - Monetary Amount (Amount Paid)
            if len(elements) > 4 and elements[4]:
                try:
                    amount = float(elements[4])
                    line_item["amount_paid"] = amount
                    total_paid += amount
                except:
                    line_item["amount_paid"] = elements[4]
            
            # RMR06 - Monetary Amount (Balance Due)
            if len(elements) > 5 and elements[5]:
                try:
                    line_item["balance_due"] = float(elements[5])
                except:
                    line_item["balance_due"] = elements[5]
            
            # Look for ADX (Adjustment) segments
            adjustments = []
            for i in range(rmr_idx + 1, min(end_idx, rmr_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "ADX":
                    adx = segments[i]
                    adj_elements = adx["elements"]
                    
                    adjustment = {}
                    
                    # ADX01 - Adjustment Reason Code
                    if len(adj_elements) > 0 and adj_elements[0]:
                        reason = adj_elements[0]
                        adjustment["reason_code"] = reason
                        adjustment["reason"] = ADJUSTMENT_REASON_CODES.get(reason, reason)
                    
                    # ADX02 - Monetary Amount
                    if len(adj_elements) > 1 and adj_elements[1]:
                        try:
                            adj_amount = float(adj_elements[1])
                            adjustment["amount"] = adj_amount
                            total_adjustments += adj_amount
                        except:
                            adjustment["amount"] = adj_elements[1]
                    
                    adjustments.append(adjustment)
            
            if adjustments:
                line_item["adjustments"] = adjustments
            
            # Look for REF segments within this loop
            refs = []
            for i in range(rmr_idx + 1, min(end_idx, rmr_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "REF":
                    ref = segments[i]
                    if len(ref["elements"]) >= 2:
                        refs.append({
                            "qualifier": ref["elements"][0],
                            "value": ref["elements"][1],
                        })
            
            if refs:
                line_item["references"] = refs
            
            document.line_items.append(line_item)
        
        # Summary
        document.summary["total_remittances"] = len(document.line_items)
        document.summary["total_paid"] = round(total_paid, 2) if total_paid else None
        document.summary["total_adjustments"] = round(total_adjustments, 2) if total_adjustments else None
    
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
