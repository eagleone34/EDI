"""
EDI 850 - Purchase Order Parser (Enhanced).
Extracts comprehensive information including addresses, contacts, terms, and item descriptions.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


class EDI850Parser(BaseEDIParser):
    """Parser for EDI 850 Purchase Order documents."""
    
    TRANSACTION_TYPE = "850"
    TRANSACTION_NAME = "Purchase Order"
    
    # Standard party type codes
    PARTY_TYPES = {
        "ST": "Ship To",
        "BT": "Bill To",
        "BY": "Buyer",
        "SE": "Seller",
        "VN": "Vendor",
        "SF": "Ship From",
        "RI": "Remit To",
        "SU": "Supplier",
    }
    
    # Reference qualifier codes
    REF_QUALIFIERS = {
        "PO": "Purchase Order Number",
        "IA": "Internal Vendor Number",
        "VR": "Vendor ID Number",
        "DP": "Department Number",
        "ZZ": "Mutually Defined",
        "AN": "Authorization Number",
    }
    
    # Date/Time qualifiers
    DATE_QUALIFIERS = {
        "002": "Delivery Requested",
        "010": "Requested Ship Date",
        "037": "Ship Not Before",
        "038": "Ship Not Later Than",
        "063": "Do Not Deliver Before",
        "064": "Do Not Deliver After",
    }
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 850 Purchase Order segments with comprehensive extraction."""
        
        # Pre-parse all segments into dicts for easier access in loop parsing
        parsed_segments = [self._parse_segment(seg) for seg in segments]
        
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
            # Extract date from ISA09 (YYMMDD format)
            if len(isa["elements"]) > 8:
                isa_date = isa["elements"][8].strip()
                if len(isa_date) == 6:
                    document.date = f"20{isa_date[:2]}-{isa_date[2:4]}-{isa_date[4:6]}"
        
        # Parse GS (Functional Group Header)
        gs = self.get_segment_by_id(segments, "GS")
        if gs and len(gs["elements"]) >= 4:
            gs_date = gs["elements"][3] if len(gs["elements"]) > 3 else None
            if gs_date and len(gs_date) == 8:
                document.date = f"{gs_date[:4]}-{gs_date[4:6]}-{gs_date[6:8]}"
        
        # Parse BEG (Beginning Segment for Purchase Order)
        beg = self.get_segment_by_id(segments, "BEG")
        if beg:
            purpose_code = beg["elements"][0] if len(beg["elements"]) > 0 else ""
            purpose_map = {"00": "Original", "01": "Cancellation", "05": "Replace", "06": "Confirmation"}
            document.header["purpose"] = purpose_map.get(purpose_code, purpose_code)
            
            type_code = beg["elements"][1] if len(beg["elements"]) > 1 else ""
            type_map = {"NE": "New Order", "DS": "Drop Ship", "RO": "Rush Order", "SA": "Stand-Alone"}
            document.header["order_type"] = type_map.get(type_code, type_code)
            
            document.header["po_number"] = beg["elements"][2] if len(beg["elements"]) > 2 else None
            
            po_date = beg["elements"][4] if len(beg["elements"]) > 4 else None
            if po_date and len(po_date) == 8:
                document.header["po_date"] = f"{po_date[:4]}-{po_date[4:6]}-{po_date[6:8]}"
            else:
                document.header["po_date"] = po_date
        
        # Parse REF segments (Reference Information)
        refs = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        document.header["notes"] = []
        for ref in refs:
            if len(ref["elements"]) >= 1:
                qualifier = ref["elements"][0]
                value = ref["elements"][1] if len(ref["elements"]) > 1 else ""
                desc = ref["elements"][2] if len(ref["elements"]) > 2 else ""
                
                # ZZ qualifiers are often notes/comments
                if qualifier == "ZZ" and (value or desc):
                    document.header["notes"].append(value + desc)
                else:
                    document.header["references"].append({
                        "type": self.REF_QUALIFIERS.get(qualifier, qualifier),
                        "qualifier": qualifier,
                        "value": value,
                    })
        
        # Parse ITD (Terms of Sale/Deferred Terms of Sale)
        itd = self.get_segment_by_id(segments, "ITD")
        if itd:
            terms_parts = []
            # Element 0: Terms Type Code
            # Element 1: Terms Basis Date Code  
            # Element 2: Terms Discount Percent
            # Element 4: Terms Discount Days Due
            # Element 11: Description
            if len(itd["elements"]) > 11 and itd["elements"][11]:
                document.header["payment_terms"] = itd["elements"][11]
            else:
                discount = itd["elements"][2] if len(itd["elements"]) > 2 else ""
                days = itd["elements"][4] if len(itd["elements"]) > 4 else ""
                if discount and days:
                    document.header["payment_terms"] = f"{discount}% {days} Days"
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        # Map qualifiers to snake_case keys for layout config
        date_key_map = {
            "002": "delivery_requested",
            "010": "requested_ship_date",
            "037": "ship_not_before",
            "038": "ship_not_later",
            "063": "do_not_deliver_before",
            "064": "do_not_deliver_after",
        }
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                
                # Format the date
                if date_value and len(date_value) == 8:
                    formatted = f"{date_value[:4]}-{date_value[4:6]}-{date_value[6:8]}"
                else:
                    formatted = date_value
                
                # Store with both human-readable key and snake_case key for header
                date_label = self.DATE_QUALIFIERS.get(qualifier, f"Date {qualifier}")
                document.header["dates"][date_label] = formatted
                # Also store directly in header with snake_case key for layout config
                if qualifier in date_key_map:
                    document.header[date_key_map[qualifier]] = formatted
        
        # Parse FOB (F.O.B. Related Instructions)
        fob = self.get_segment_by_id(segments, "FOB")
        if fob:
            fob_code = fob["elements"][0] if len(fob["elements"]) > 0 else ""
            fob_map = {"DF": "Delivered", "CC": "Collect", "PP": "Prepaid", "PS": "Paid by Seller"}
            document.header["fob"] = fob_map.get(fob_code, fob_code)
            if len(fob["elements"]) > 6:
                document.header["fob_location"] = fob["elements"][6]
        
        # Parse SAC (Service, Promotion, Allowance, or Charge Information)
        sac_segments = self.get_all_segments_by_id(segments, "SAC")
        if sac_segments:
            document.header["allowances_charges"] = []
            for sac in sac_segments:
                document.header["allowances_charges"].append({
                    "type": sac["elements"][0] if len(sac["elements"]) > 0 else "",
                    "code": sac["elements"][1] if len(sac["elements"]) > 1 else "",
                    "amount": sac["elements"][4] if len(sac["elements"]) > 4 else "",
                })
        
        # Parse TD5 (Carrier Details - Routing)
        td5_segments = self.get_all_segments_by_id(segments, "TD5")
        if td5_segments:
            routing_info = []
            for td5 in td5_segments:
                transport_method = td5["elements"][3] if len(td5["elements"]) > 3 else ""
                method_map = {
                    "J": "Air", "M": "Motor (Common Carrier)", "R": "Rail",
                    "S": "Ocean", "H": "Private Carrier", "P": "Private Parcel",
                    "CG": "Ground Carrier", "ZZ": "Mutually Defined"
                }
                routing_info.append({
                    "routing_sequence": td5["elements"][0] if len(td5["elements"]) > 0 else "",
                    "id_qualifier": td5["elements"][1] if len(td5["elements"]) > 1 else "",
                    "carrier_id": td5["elements"][2] if len(td5["elements"]) > 2 else "",
                    "transport_method": method_map.get(transport_method, transport_method),
                    "routing": td5["elements"][4] if len(td5["elements"]) > 4 else "",
                })
            document.header["carrier_routing"] = routing_info
            # Set primary routing for header display
            if routing_info:
                document.header["routing"] = routing_info[0].get("routing", "")
                document.header["transport_method"] = routing_info[0].get("transport_method", "")
                document.header["carrier"] = routing_info[0].get("carrier_id", "")
        
        # Parse TD1 (Carrier Details - Quantity and Weight)
        td1 = self.get_segment_by_id(segments, "TD1")
        if td1:
            document.header["packaging_code"] = td1["elements"][0] if len(td1["elements"]) > 0 else ""
            document.header["lading_quantity"] = td1["elements"][1] if len(td1["elements"]) > 1 else ""
            document.header["commodity_code_qualifier"] = td1["elements"][2] if len(td1["elements"]) > 2 else ""
            document.header["commodity_code"] = td1["elements"][3] if len(td1["elements"]) > 3 else ""
            document.header["weight"] = td1["elements"][6] if len(td1["elements"]) > 6 else ""
            document.header["weight_unit"] = td1["elements"][7] if len(td1["elements"]) > 7 else ""
        
        # Parse CS (Sales Requirements)
        cs = self.get_segment_by_id(segments, "CS")
        if cs:
            cs_code = cs["elements"][0] if len(cs["elements"]) > 0 else ""
            cs_map = {"NB": "No Back Order", "BO": "Back Order OK", "SH": "Ship Complete"}
            document.header["sales_requirement"] = cs_map.get(cs_code, cs_code)
            document.header["sales_requirement_code"] = cs_code
        
        # Parse header-level PER (Administrative Contact) - before N1 loops
        # Find PER segments that appear before the first N1
        first_n1_idx = len(parsed_segments)
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "N1":
                first_n1_idx = i
                break
        
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "PER" and i < first_n1_idx:
                per_func = seg["elements"][0] if len(seg["elements"]) > 0 else ""
                func_map = {"OC": "Order Contact", "BD": "Buyer Contact", "IC": "Information Contact"}
                document.header["contact_function"] = func_map.get(per_func, per_func)
                document.header["contact_name"] = seg["elements"][1] if len(seg["elements"]) > 1 else ""
                document.header["contact_type"] = seg["elements"][2] if len(seg["elements"]) > 2 else ""
                document.header["contact_number"] = seg["elements"][3] if len(seg["elements"]) > 3 else ""
                # Additional contact methods
                if len(seg["elements"]) > 5:
                    document.header["contact_type2"] = seg["elements"][4]
                    document.header["contact_number2"] = seg["elements"][5]
                break  # Take first header PER
        
        # Parse party information with addresses (N1, N2, N3, N4, PER loops)
        self._parse_party_loops(parsed_segments, document)
        
        # Parse line items with descriptions (PO1 + PID loops)
        self._parse_line_item_loops(parsed_segments, document)
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
            if len(ctt["elements"]) > 1:
                document.summary["hash_total"] = ctt["elements"][1]
            # CTT can have weight and total dollar at the end
            for i, elem in enumerate(ctt["elements"]):
                if "TOTAL DOLLAR" in elem.upper() or "TOTAL" in elem.upper():
                    # Try to extract dollar amount
                    import re
                    match = re.search(r'[\d,.]+$', elem)
                    if match:
                        try:
                            document.summary["total_amount"] = float(match.group().replace(',', ''))
                        except ValueError:
                            pass
        
        return document
    
    def _parse_party_loops(self, segments: list, document: EDIDocument) -> None:
        """Parse N1/N2/N3/N4/PER loops for party/address information."""
        
        document.header["parties"] = []
        
        # Find all N1 segment indices
        n1_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "N1":
                n1_indices.append(i)
        
        for idx, n1_idx in enumerate(n1_indices):
            n1 = segments[n1_idx]
            
            # Determine loop end (next N1 or end of party loop indicators)
            end_idx = n1_indices[idx + 1] if idx + 1 < len(n1_indices) else len(segments)
            
            party = {
                "type_code": n1["elements"][0] if len(n1["elements"]) > 0 else None,
                "type": self.PARTY_TYPES.get(
                    n1["elements"][0] if len(n1["elements"]) > 0 else "", 
                    n1["elements"][0] if len(n1["elements"]) > 0 else ""
                ),
                "name": n1["elements"][1] if len(n1["elements"]) > 1 else None,
                "id_qualifier": n1["elements"][2] if len(n1["elements"]) > 2 else None,
                "id": n1["elements"][3] if len(n1["elements"]) > 3 else None,
            }
            
            # Look for N2 (Additional Name)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments) and segments[i]["id"] == "N2":
                    n2 = segments[i]
                    if n2["elements"]:
                        party["name2"] = n2["elements"][0]
            
            # Look for N3 (Address)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments) and segments[i]["id"] == "N3":
                    n3 = segments[i]
                    party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                    party["address_line2"] = n3["elements"][1] if len(n3["elements"]) > 1 else None
            
            # Look for N4 (Geographic Location)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments) and segments[i]["id"] == "N4":
                    n4 = segments[i]
                    party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                    party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                    party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
                    party["country"] = n4["elements"][3] if len(n4["elements"]) > 3 else None
            
            # Look for PER (Administrative Contact)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments) and segments[i]["id"] == "PER":
                    per = segments[i]
                    party["contact_type"] = per["elements"][0] if len(per["elements"]) > 0 else None
                    party["contact_name"] = per["elements"][1] if len(per["elements"]) > 1 else None
                    party["contact_qualifier"] = per["elements"][2] if len(per["elements"]) > 2 else None
                    party["contact_number"] = per["elements"][3] if len(per["elements"]) > 3 else None
            
            document.header["parties"].append(party)
    
    def _parse_line_item_loops(self, segments: list, document: EDIDocument) -> None:
        """Parse PO1/PID/ACK loops for line item information with descriptions."""
        
        # Find all PO1 segment indices
        po1_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "PO1":
                po1_indices.append(i)
        
        for idx, po1_idx in enumerate(po1_indices):
            po1 = segments[po1_idx]
            
            # Determine loop end (next PO1 or end of segments)
            end_idx = po1_indices[idx + 1] if idx + 1 < len(po1_indices) else len(segments)
            
            line_item = {
                "line_number": po1["elements"][0] if len(po1["elements"]) > 0 else None,
                "quantity": po1["elements"][1] if len(po1["elements"]) > 1 else None,
                "unit": po1["elements"][2] if len(po1["elements"]) > 2 else None,
                "unit_price": po1["elements"][3] if len(po1["elements"]) > 3 else None,
            }
            
            # Calculate line total if we have quantity and unit price
            try:
                qty = float(line_item["quantity"]) if line_item["quantity"] else 0
                price = float(line_item["unit_price"]) if line_item["unit_price"] else 0
                line_item["total"] = round(qty * price, 2)
            except (ValueError, TypeError):
                line_item["total"] = None
            
            # Parse product IDs from remaining PO1 elements
            # Format is typically: Qualifier, ID, Qualifier, ID, ...
            product_ids = {}
            i = 5  # Start after price basis
            while i < len(po1["elements"]) - 1:
                qualifier = po1["elements"][i] if i < len(po1["elements"]) else ""
                value = po1["elements"][i + 1] if i + 1 < len(po1["elements"]) else ""
                if qualifier and value:
                    qualifier_names = {
                        "PI": "Purchaser's Item Code",
                        "VN": "Vendor's Item Number",
                        "UK": "UPC/EAN",
                        "UP": "UPC Consumer Package",
                        "IN": "Buyer's Item Number",
                        "BP": "Buyer's Part Number",
                        "SK": "SKU",
                        "MG": "Manufacturer's Part Number",
                    }
                    id_name = qualifier_names.get(qualifier, qualifier)
                    product_ids[id_name] = value
                i += 2
            
            line_item["product_ids"] = product_ids
            # Set primary product ID for display
            line_item["product_id"] = (
                product_ids.get("Purchaser's Item Code") or
                product_ids.get("Vendor's Item Number") or
                product_ids.get("UPC/EAN") or
                next(iter(product_ids.values()), None) if product_ids else None
            )
            
            # Look for PID (Product/Item Description)
            descriptions = []
            for i in range(po1_idx + 1, min(end_idx, po1_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "PID":
                    pid = segments[i]
                    # PID element 4 is typically the description
                    if len(pid["elements"]) > 4 and pid["elements"][4]:
                        descriptions.append(pid["elements"][4])
            
            line_item["description"] = " ".join(descriptions) if descriptions else None
            
            # Look for PO4 (Item Physical Details / Pack)
            for i in range(po1_idx + 1, min(end_idx, po1_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "PO4":
                    po4 = segments[i]
                    line_item["pack"] = po4["elements"][0] if len(po4["elements"]) > 0 else ""
                    line_item["inner_pack"] = po4["elements"][1] if len(po4["elements"]) > 1 else ""
                    line_item["gross_weight"] = po4["elements"][5] if len(po4["elements"]) > 5 else ""
                    line_item["gross_weight_unit"] = po4["elements"][6] if len(po4["elements"]) > 6 else ""
                    break
            
            # Store additional product IDs for display (UPC, SKU, Vendor Style)
            line_item["upc"] = product_ids.get("UPC/EAN") or product_ids.get("UPC Consumer Package") or ""
            line_item["sku"] = product_ids.get("SKU") or ""
            line_item["vendor_style"] = product_ids.get("Vendor's Item Number") or ""
            
            document.line_items.append(line_item)
        
        # Calculate totals
        total = 0
        for item in document.line_items:
            if item.get("total"):
                total += item["total"]
        
        if total > 0:
            document.summary["calculated_total"] = round(total, 2)
