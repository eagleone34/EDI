"""
EDI 856 - Advance Ship Notice (ASN) Parser (Enhanced).
Comprehensive hierarchical shipment data extraction.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 856-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "05": "Replace",
}

HIERARCHY_LEVEL_CODES = {
    "S": "Shipment",
    "O": "Order",
    "P": "Pack",
    "I": "Item",
    "T": "Tare (Pallet)",
    "F": "Component",
}

TRANSPORT_METHOD_CODES = {
    "M": "Motor (Common Carrier)",
    "R": "Rail",
    "A": "Air",
    "H": "Customer Pickup",
    "L": "Contract Carrier",
    "P": "Private Carrier/Dedicated Fleet",
    "U": "Parcel Post",
    "X": "Intermodal",
}

PARTY_TYPE_CODES = {
    "SF": "Ship From",
    "ST": "Ship To",
    "BY": "Buying Party",
    "SE": "Selling Party",
    "VN": "Vendor",
    "BT": "Bill To",
    "CA": "Carrier",
}

PRODUCT_ID_QUALIFIERS = {
    "PI": "Purchaser's Item Code",
    "VN": "Vendor's (Seller's) Part Number",
    "UP": "U.P.C. Consumer Package Code",
    "UK": "UPC/EAN Shipping Container Code",
    "BP": "Buyer's Part Number",
    "SN": "Serial Number",
    "LT": "Lot Number",
}

MARKS_QUALIFIER_CODES = {
    "CP": "Carrier Assigned Package Code",
    "GM": "SSCC-18",
    "UC": "UCC/EAN-128",
    "L": "Line Item Only",
}


class EDI856Parser(BaseEDIParser):
    """Parser for EDI 856 Advance Ship Notice (ASN) documents."""
    
    TRANSACTION_TYPE = "856"
    TRANSACTION_NAME = "Advance Ship Notice"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 856 Advance Ship Notice segments."""
        
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
        
        # Parse BSN (Beginning Segment for Ship Notice)
        bsn = self.get_segment_by_id(segments, "BSN")
        if bsn:
            elements = bsn["elements"]
            
            # BSN01 - Transaction Set Purpose Code
            if len(elements) > 0 and elements[0]:
                purpose = elements[0]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
            
            # BSN02 - Shipment Identification
            if len(elements) > 1 and elements[1]:
                document.header["shipment_id"] = elements[1]
            
            # BSN03 - Date
            if len(elements) > 2 and elements[2]:
                document.header["shipment_date"] = self._format_date(elements[2])
                document.date = document.header["shipment_date"]
            
            # BSN04 - Time
            if len(elements) > 3 and elements[3]:
                document.header["shipment_time"] = self._format_time(elements[3])
            
            # BSN05 - Hierarchical Structure Code
            if len(elements) > 4 and elements[4]:
                document.header["hierarchy_code"] = elements[4]
        
        # Parse DTM (Date/Time Reference)
        dtm_segments = self.get_all_segments_by_id(segments, "DTM")
        document.header["dates"] = {}
        date_qualifiers = {
            "011": "Ship Date",
            "017": "Estimated Delivery Date",
            "002": "Delivery Date",
        }
        for dtm in dtm_segments:
            if len(dtm["elements"]) >= 2:
                qualifier = dtm["elements"][0]
                date_value = dtm["elements"][1]
                label = date_qualifiers.get(qualifier, f"Date ({qualifier})")
                document.header["dates"][label] = self._format_date(date_value)
        
        # Parse TD1 (Carrier Details - Quantity and Weight)
        td1 = self.get_segment_by_id(segments, "TD1")
        if td1:
            elements = td1["elements"]
            document.header["packaging"] = {
                "packaging_code": elements[0] if len(elements) > 0 else None,
                "lading_quantity": elements[1] if len(elements) > 1 else None,
                "weight_qualifier": elements[5] if len(elements) > 5 else None,
                "weight": elements[6] if len(elements) > 6 else None,
                "unit_of_measure": elements[7] if len(elements) > 7 else None,
            }
        
        # Parse TD3 (Carrier Details - Equipment)
        td3_segments = self.get_all_segments_by_id(segments, "TD3")
        if td3_segments:
            document.header["equipment"] = []
            for td3 in td3_segments:
                elements = td3["elements"]
                document.header["equipment"].append({
                    "equipment_type": elements[0] if len(elements) > 0 else None,
                    "equipment_initial": elements[1] if len(elements) > 1 else None,
                    "equipment_number": elements[2] if len(elements) > 2 else None,
                    "seal_number": elements[8] if len(elements) > 8 else None,
                })
        
        # Parse TD5 (Carrier Details - Routing)
        td5 = self.get_segment_by_id(segments, "TD5")
        if td5:
            elements = td5["elements"]
            transport_code = elements[3] if len(elements) > 3 else None
            document.header["carrier"] = {
                "routing_sequence": elements[0] if len(elements) > 0 else None,
                "id_type": elements[1] if len(elements) > 1 else None,
                "carrier_code": elements[2] if len(elements) > 2 else None,
                "transport_method_code": transport_code,
                "transport_method": TRANSPORT_METHOD_CODES.get(transport_code, transport_code) if transport_code else None,
                "routing": elements[4] if len(elements) > 4 else None,
            }
        
        # Parse REF (Reference Identification)
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                qualifier = ref["elements"][0]
                value = ref["elements"][1]
                
                ref_entry = {
                    "qualifier": qualifier,
                    "value": value,
                }
                document.header["references"].append(ref_entry)
                
                # Store specific references
                if qualifier == "CN":
                    document.header["pro_number"] = value
                elif qualifier == "BM":
                    document.header["bill_of_lading"] = value
                elif qualifier == "PK":
                    document.header["tracking_number"] = value
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Extract specific parties
        for party in document.header.get("parties", []):
            if party.get("type_code") == "SF":
                document.header["ship_from"] = party
            elif party.get("type_code") == "ST":
                document.header["ship_to"] = party
        
        # Parse HL (Hierarchical Level) loops - This is the core of 856
        self._parse_hierarchy(segments, document)
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
        
        return document
    
    def _parse_parties(self, segments: list) -> List[Dict]:
        """Parse party information."""
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
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "N3":
                    n3 = parsed_segments[i]
                    party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                    party["address_line2"] = n3["elements"][1] if len(n3["elements"]) > 1 else None
                    break
            
            # Look for N4 (Geographic Location)
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(parsed_segments) and parsed_segments[i]["id"] == "N4":
                    n4 = parsed_segments[i]
                    party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                    party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                    party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
                    party["country"] = n4["elements"][3] if len(n4["elements"]) > 3 else None
                    break
            
            parties.append(party)
        
        return parties
    
    def _parse_hierarchy(self, segments: list, document: EDIDocument) -> None:
        """Parse HL (Hierarchical Level) loops for shipment structure."""
        
        # Parse all segments first since we need to look ahead
        parsed_segments = [self._parse_segment(s) for s in segments]
        
        # Group segments by HL level
        hl_indices = []
        for i, seg in enumerate(parsed_segments):
            if seg["id"] == "HL":
                hl_indices.append(i)
        
        shipment_info = {}
        orders = []
        packs = []
        
        for idx, hl_idx in enumerate(hl_indices):
            hl = parsed_segments[hl_idx]
            
            # Determine loop end
            end_idx = hl_indices[idx + 1] if idx + 1 < len(hl_indices) else len(parsed_segments)
            
            # HL01 - Hierarchical ID Number
            hl_id = hl["elements"][0] if len(hl["elements"]) > 0 else None
            # HL02 - Hierarchical Parent ID Number
            parent_id = hl["elements"][1] if len(hl["elements"]) > 1 else None
            # HL03 - Hierarchical Level Code
            level_code = hl["elements"][2] if len(hl["elements"]) > 2 else None
            level_desc = HIERARCHY_LEVEL_CODES.get(level_code, level_code)
            
            # Parse segments within this HL loop
            loop_data = {
                "hl_id": hl_id,
                "parent_id": parent_id,
                "level_code": level_code,
                "level": level_desc,
            }
            
            for i in range(hl_idx + 1, end_idx):
                seg = parsed_segments[i]
                seg_id = seg["id"]
                elements = seg["elements"]
                
                if seg_id == "PRF":  # Purchase Order Reference
                    loop_data["po_number"] = elements[0] if len(elements) > 0 else None
                    loop_data["po_date"] = self._format_date(elements[3]) if len(elements) > 3 else None
                
                elif seg_id == "LIN":  # Item Identification
                    product_ids = {}
                    j = 1
                    while j + 1 < len(elements):
                        qualifier = elements[j]
                        value = elements[j + 1] if j + 1 < len(elements) else ""
                        if qualifier and value:
                            label = PRODUCT_ID_QUALIFIERS.get(qualifier, qualifier)
                            product_ids[label] = value
                        j += 2
                    loop_data["product_ids"] = product_ids
                
                elif seg_id == "SN1":  # Item Detail (Shipment)
                    loop_data["quantity_shipped"] = elements[1] if len(elements) > 1 else None
                    loop_data["unit"] = elements[2] if len(elements) > 2 else None
                    loop_data["quantity_ordered"] = elements[4] if len(elements) > 4 else None
                
                elif seg_id == "PID":  # Product Description
                    loop_data["description"] = elements[4] if len(elements) > 4 else None
                
                elif seg_id == "MAN":  # Marks and Numbers
                    qualifier = elements[0] if len(elements) > 0 else None
                    value = elements[1] if len(elements) > 1 else None
                    
                    if "marks_numbers" not in loop_data:
                        loop_data["marks_numbers"] = []
                    
                    loop_data["marks_numbers"].append({
                        "qualifier": qualifier,
                        "qualifier_desc": MARKS_QUALIFIER_CODES.get(qualifier, qualifier),
                        "value": value,
                    })
                    
                    # Store SSCC specifically
                    if qualifier == "GM":
                        loop_data["sscc"] = value
                
                elif seg_id == "REF":  # Reference in HL loop
                    qualifier = elements[0] if len(elements) > 0 else None
                    value = elements[1] if len(elements) > 1 else None
                    
                    if qualifier == "LS":
                        loop_data["lot_number"] = value
                    elif qualifier == "SE":
                        loop_data["serial_number"] = value
            
            # Categorize by level
            if level_code == "S":
                shipment_info = loop_data
            elif level_code == "O":
                orders.append(loop_data)
            elif level_code == "P":
                packs.append(loop_data)
            elif level_code == "I":
                # Item level - add to line items
                line_item = {
                    "line_number": str(len(document.line_items) + 1),
                    "description": loop_data.get("description"),
                    "quantity_shipped": loop_data.get("quantity_shipped"),
                    "unit": loop_data.get("unit"),
                    "quantity_ordered": loop_data.get("quantity_ordered"),
                    "product_ids": loop_data.get("product_ids", {}),
                    "lot_number": loop_data.get("lot_number"),
                    "serial_number": loop_data.get("serial_number"),
                    "sscc": loop_data.get("sscc"),
                    "marks_numbers": loop_data.get("marks_numbers", []),
                }
                
                # Set primary product ID
                pids = loop_data.get("product_ids", {})
                line_item["product_id"] = next(iter(pids.values()), None) if pids else None
                
                document.line_items.append(line_item)
        
        # Store hierarchy summary
        document.header["shipment"] = shipment_info
        if orders:
            document.header["orders"] = orders
        if packs:
            document.header["packs"] = packs
        
        # Calculate totals
        total_qty = sum(
            float(item.get("quantity_shipped") or 0)
            for item in document.line_items
        )
        if total_qty > 0:
            document.summary["total_quantity_shipped"] = total_qty
    
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
    
    def _format_time(self, time_str: str) -> str:
        """Format time from HHMM to readable format."""
        if not time_str or len(time_str) < 4:
            return time_str
        try:
            hour = int(time_str[:2])
            minute = time_str[2:4]
            am_pm = "AM" if hour < 12 else "PM"
            hour_12 = hour if hour <= 12 else hour - 12
            if hour_12 == 0:
                hour_12 = 12
            return f"{hour_12}:{minute} {am_pm}"
        except:
            return time_str
