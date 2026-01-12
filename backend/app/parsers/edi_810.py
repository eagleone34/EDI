"""
EDI 810 - Invoice Parser (Enhanced).
Comprehensive extraction matching EDINOTEPAD quality.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 810-specific codes
PARTY_TYPE_CODES = {
    "BY": "Buying Party (Purchaser)",
    "SE": "Selling Party",
    "ST": "Ship To",
    "BT": "Bill To",
    "VN": "Vendor",
    "RI": "Remit To",
    "SF": "Ship From",
    "SU": "Supplier",
    "PR": "Payer",
    "PY": "Payee",
}

REFERENCE_QUALIFIERS = {
    "DP": "Department Number",
    "IA": "Internal Vendor Number",
    "VR": "Vendor ID Number",
    "PO": "Purchase Order Number",
    "IV": "Invoice Number",
    "BM": "Bill of Lading Number",
    "CR": "Customer Reference Number",
    "OQ": "Order Qualifier",
    "ZZ": "Mutually Defined",
}

ID_QUALIFIERS = {
    "1": "D-U-N-S Number",
    "9": "D-U-N-S+4",
    "92": "Assigned by Buyer or Buyer's Agent",
    "UL": "GLN (Global Location Number)",
    "ZZ": "Mutually Defined",
}

PRODUCT_ID_QUALIFIERS = {
    "PI": "Purchaser's Item Code",
    "VN": "Vendor's (Seller's) Part Number",
    "UP": "U.P.C. Consumer Package Code (1-5-5-1)",
    "UK": "UPC/EAN Shipping Container Code",
    "EN": "EAN/UCC-13",
    "BP": "Buyer's Part Number",
    "MG": "Manufacturer's Part Number",
    "SK": "SKU",
    "IN": "Buyer's Item Number",
}


class EDI810Parser(BaseEDIParser):
    """Parser for EDI 810 Invoice documents."""
    
    TRANSACTION_TYPE = "810"
    TRANSACTION_NAME = "Invoice"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 810 Invoice segments with comprehensive extraction."""
        
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
        
        # Parse BIG (Beginning Segment for Invoice)
        big = self.get_segment_by_id(segments, "BIG")
        if big:
            elements = big["elements"]
            
            # BIG01 - Invoice Date
            if len(elements) > 0 and elements[0]:
                document.header["invoice_date"] = self._format_date(elements[0])
                document.date = document.header["invoice_date"]
            
            # BIG02 - Invoice Number
            if len(elements) > 1 and elements[1]:
                document.header["invoice_number"] = elements[1]
            
            # BIG03 - Purchase Order Date
            if len(elements) > 2 and elements[2]:
                document.header["po_date"] = self._format_date(elements[2])
            
            # BIG04 - Purchase Order Number
            if len(elements) > 3 and elements[3]:
                document.header["po_number"] = elements[3]
            
            # BIG07 - Transaction Type Code
            if len(elements) > 6 and elements[6]:
                type_codes = {
                    "CN": "Credit Invoice",
                    "DI": "Debit Invoice",
                    "CR": "Credit Memo",
                    "DR": "Debit Memo",
                }
                document.header["transaction_type_code"] = elements[6]
                document.header["transaction_type_desc"] = type_codes.get(elements[6], elements[6])
        
        # Parse CUR (Currency)
        cur = self.get_segment_by_id(segments, "CUR")
        if cur and len(cur["elements"]) > 1:
            document.header["currency"] = cur["elements"][1]
        
        # Parse REF (Reference Identification) segments
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                qualifier = ref["elements"][0]
                value = ref["elements"][1]
                description = ref["elements"][2] if len(ref["elements"]) > 2 else None
                
                ref_entry = {
                    "qualifier": qualifier,
                    "qualifier_desc": REFERENCE_QUALIFIERS.get(qualifier, qualifier),
                    "value": value,
                }
                if description:
                    ref_entry["description"] = description
                
                document.header["references"].append(ref_entry)
                
                # Store specific references for easy access
                if qualifier == "DP":
                    document.header["department_number"] = value
                elif qualifier == "IA":
                    document.header["internal_vendor_number"] = value
                elif qualifier == "VR":
                    document.header["vendor_id"] = value
        
        # Parse ITD (Terms of Sale/Deferred Terms of Sale)
        itd = self.get_segment_by_id(segments, "ITD")
        if itd and len(itd["elements"]) > 0:
            terms_parts = []
            # ITD01 - Terms Type Code
            terms_type = itd["elements"][0] if len(itd["elements"]) > 0 else None
            # ITD02 - Terms Basis Date Code
            # ITD03 - Terms Discount Percent
            discount = itd["elements"][2] if len(itd["elements"]) > 2 else None
            # ITD05 - Terms Discount Days Due
            discount_days = itd["elements"][4] if len(itd["elements"]) > 4 else None
            # ITD07 - Terms Net Days
            net_days = itd["elements"][6] if len(itd["elements"]) > 6 else None
            # ITD12 - Description
            description = itd["elements"][11] if len(itd["elements"]) > 11 else None
            
            if description:
                document.header["payment_terms"] = description
            elif discount and discount_days:
                document.header["payment_terms"] = f"{discount}% {discount_days} Days, Net {net_days or '30'}"
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        date_qualifiers = {
            "011": "Ship Date",
            "002": "Delivery Date",
            "003": "Invoice Date",
            "004": "Purchase Order Date",
        }
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                date_label = date_qualifiers.get(qualifier, f"Date ({qualifier})")
                document.header["dates"][date_label] = self._format_date(date_value)
        
        # Parse N1/N2/N3/N4 (Party Information with Addresses)
        document.header["parties"] = self._parse_parties(segments)
        
        # Extract specific parties for display
        for party in document.header.get("parties", []):
            if party.get("type_code") == "BY":
                document.header["buying_party"] = party
            elif party.get("type_code") == "SE":
                document.header["selling_party"] = party
            elif party.get("type_code") == "ST":
                document.header["ship_to"] = party
            elif party.get("type_code") == "RI":
                document.header["remit_to"] = party
        
        # Parse IT1 (Baseline Item Data - Invoice) segments with PID
        self._parse_line_items(segments, document)
        
        # Parse TDS (Total Monetary Value Summary)
        tds = self.get_segment_by_id(segments, "TDS")
        if tds and len(tds["elements"]) > 0:
            try:
                # TDS amounts are typically in cents
                total_cents = int(tds["elements"][0])
                document.summary["total_amount"] = total_cents / 100
            except ValueError:
                document.summary["total_amount"] = tds["elements"][0]
        
        # Parse TXI (Tax Information)
        txi_segments = self.get_all_segments_by_id(segments, "TXI")
        if txi_segments:
            document.header["taxes"] = []
            for txi in txi_segments:
                tax_entry = {}
                if len(txi["elements"]) > 0:
                    tax_entry["type"] = txi["elements"][0]
                if len(txi["elements"]) > 1:
                    try:
                        tax_entry["amount"] = float(txi["elements"][1])
                    except:
                        tax_entry["amount"] = txi["elements"][1]
                document.header["taxes"].append(tax_entry)
        
        # Parse SAC (Service, Promotion, Allowance, or Charge)
        sac_segments = self.get_all_segments_by_id(segments, "SAC")
        if sac_segments:
            document.header["allowances_charges"] = []
            for sac in sac_segments:
                entry = {
                    "indicator": sac["elements"][0] if len(sac["elements"]) > 0 else None,
                    "type": "Allowance" if sac["elements"][0] == "A" else "Charge" if sac["elements"][0] == "C" else sac["elements"][0] if len(sac["elements"]) > 0 else None,
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
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            if len(ctt["elements"]) > 0:
                document.summary["total_line_items"] = ctt["elements"][0]
            if len(ctt["elements"]) > 1:
                document.summary["hash_total"] = ctt["elements"][1]
        
        # Parse CAD (Carrier Detail)
        cad = self.get_segment_by_id(segments, "CAD")
        if cad:
            document.header["carrier"] = {
                "transport_method": cad["elements"][0] if len(cad["elements"]) > 0 else None,
                "equipment_code": cad["elements"][1] if len(cad["elements"]) > 1 else None,
                "scac": cad["elements"][3] if len(cad["elements"]) > 3 else None,
                "routing": cad["elements"][4] if len(cad["elements"]) > 4 else None,
            }
        
        return document
    
    def _parse_parties(self, segments: list) -> List[Dict]:
        """Parse N1 loops (Party Identification)."""
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
            
            # N101 - Entity Identifier Code
            party_code = n1["elements"][0] if len(n1["elements"]) > 0 else None
            
            party = {
                "type_code": party_code,
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
                "id_qualifier": n1["elements"][2] if len(n1["elements"]) > 2 else None,
                "id": n1["elements"][3] if len(n1["elements"]) > 3 else None,
            }
            
            # Look for N2 (Additional Name)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 6)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "N2":
                    n2 = parsed_segments[i]
                    if len(n2["elements"]) > 0 and n2["elements"][0]:
                        party["additional_name"] = n2["elements"][0]
                    break
            
            # Look for N3 (Address Info)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                 if i < len(parsed_segments):
                    if parsed_segments[i]["id"] == "N3":
                        n3 = parsed_segments[i]
                        party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                        if len(n3["elements"]) > 1:
                            party["address_line2"] = n3["elements"][1]
                    
                    # Look for N4 (Geographic Location)
                    elif parsed_segments[i]["id"] == "N4":
                        n4 = parsed_segments[i]
                        party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                        party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                        party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
                        if len(n4["elements"]) > 3:
                            party["country"] = n4["elements"][3]
            
            # Look for PER (Administrative Communication Contact)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 6)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "PER":
                    per = parsed_segments[i]
                    party["contact_type"] = per["elements"][0] if len(per["elements"]) > 0 else None
                    party["contact_name"] = per["elements"][1] if len(per["elements"]) > 1 else None
                    if len(per["elements"]) > 3:
                        party["contact_qualifier"] = per["elements"][2]
                        party["contact_number"] = per["elements"][3]
                    break
            
            parties.append(party)
            
        return parties
    
    def _parse_line_items(self, segments: list, document: EDIDocument) -> None:
        """Parse IT1/PID loops for line item information."""
        
        # Parse all segments first since we need to look ahead
        parsed_segments = [self._parse_segment(s) for s in segments]
        
        # Find all IT1 segment indices
        it1_indices = []
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "IT1":
                it1_indices.append(i)
        
        for idx, it1_idx in enumerate(it1_indices):
            it1 = parsed_segments[it1_idx]
            
            # Determine loop end (next IT1 or segment that breaks the loop)
            end_idx = it1_indices[idx + 1] if idx + 1 < len(it1_indices) else len(parsed_segments)
            
            line_item = {
                "line_number": it1["elements"][0] if len(it1["elements"]) > 0 else str(idx + 1),
                "quantity_invoiced": it1["elements"][1] if len(it1["elements"]) > 1 else None,
                "unit": it1["elements"][2] if len(it1["elements"]) > 2 else None,
                "unit_price": it1["elements"][3] if len(it1["elements"]) > 3 else None,
            }
            
            # Calculate line total
            try:
                qty = float(line_item["quantity_invoiced"]) if line_item["quantity_invoiced"] else 0
                price = float(line_item["unit_price"]) if line_item["unit_price"] else 0
                line_item["total"] = round(qty * price, 2)
            except (ValueError, TypeError):
                line_item["total"] = None
            
            # Parse product IDs from IT1 elements (format: qualifier, value pairs starting at element 5)
            product_ids = {}
            i = 5
            while i + 1 < len(it1["elements"]):
                qualifier = it1["elements"][i] if i < len(it1["elements"]) else ""
                value = it1["elements"][i + 1] if i + 1 < len(it1["elements"]) else ""
                if qualifier and value:
                    id_label = PRODUCT_ID_QUALIFIERS.get(qualifier, qualifier)
                    product_ids[id_label] = value
                i += 2
            
            line_item["product_ids"] = product_ids
            
            # Set primary display values
            line_item["upc"] = product_ids.get("U.P.C. Consumer Package Code (1-5-5-1)")
            line_item["vendor_part_number"] = product_ids.get("Vendor's (Seller's) Part Number")
            line_item["product_id"] = (
                line_item["upc"] or 
                line_item["vendor_part_number"] or 
                product_ids.get("Purchaser's Item Code") or
                next(iter(product_ids.values()), None) if product_ids else None
            )
            
            # Look for PID (Product/Item Description)
            descriptions = []
            for i in range(it1_idx + 1, min(end_idx, it1_idx + 10)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "PID":
                    pid = parsed_segments[i]
                    # PID05 is typically the description
                    if len(pid["elements"]) > 4 and pid["elements"][4]:
                        descriptions.append(pid["elements"][4])
            
            line_item["description"] = " ".join(descriptions) if descriptions else None
            
            # Look for additional information in SLN (Subline Item Detail)
            additional_info = []
            for i in range(it1_idx + 1, min(end_idx, it1_idx + 15)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "SLN":
                    sln = parsed_segments[i]
                    if len(sln["elements"]) > 8:
                        additional_info.append({
                            "quantity": sln["elements"][4] if len(sln["elements"]) > 4 else None,
                            "unit": sln["elements"][5] if len(sln["elements"]) > 5 else None,
                        })
            
            if additional_info:
                line_item["additional_info"] = additional_info
            
            document.line_items.append(line_item)
        
        # Calculate totals from line items
        total = 0
        for item in document.line_items:
            if item.get("total"):
                total += item["total"]
        
        if total > 0:
            document.summary["calculated_total"] = round(total, 2)
    
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
