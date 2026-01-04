"""
EDI 830 - Planning Schedule with Release Capability Parser.
JIT manufacturing schedules and forecasts.
"""

from typing import Dict, Any, List, Optional
from app.parsers.base import BaseEDIParser, EDIDocument


# Lookup tables for 830-specific codes
TRANSACTION_PURPOSE_CODES = {
    "00": "Original",
    "01": "Cancellation",
    "04": "Change",
    "05": "Replace",
}

SCHEDULE_TYPE_CODES = {
    "DL": "Delivery Based",
    "SH": "Shipment Based",
    "ZZ": "Mutually Defined",
}

FORECAST_QUALIFIER_CODES = {
    "A": "Actual Discrete Quantities",
    "C": "Cumulative Quantities",
    "D": "Discrete Quantities",
    "F": "Flexible Interval Quantities",
    "Z": "Mutually Defined",
}

FORECAST_TIMING_CODES = {
    "D": "Discrete",
    "F": "Flexible",
    "W": "Weekly",
    "M": "Monthly",
}

PARTY_TYPE_CODES = {
    "BY": "Buyer",
    "SE": "Seller",
    "ST": "Ship To",
    "SF": "Ship From",
    "MF": "Manufacturer",
    "SU": "Supplier",
}


class EDI830Parser(BaseEDIParser):
    """Parser for EDI 830 Planning Schedule with Release Capability documents."""
    
    TRANSACTION_TYPE = "830"
    TRANSACTION_NAME = "Planning Schedule with Release Capability"
    
    def _parse_segments(self, segments: list) -> EDIDocument:
        """Parse 830 Planning Schedule segments."""
        
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
        
        # Parse BFR (Beginning Segment for Planning Schedule)
        bfr = self.get_segment_by_id(segments, "BFR")
        if bfr:
            elements = bfr["elements"]
            
            # BFR01 - Transaction Set Purpose Code
            if len(elements) > 0 and elements[0]:
                purpose = elements[0]
                document.header["purpose_code"] = purpose
                document.header["purpose"] = TRANSACTION_PURPOSE_CODES.get(purpose, purpose)
            
            # BFR02 - Reference Identification (Schedule ID)
            if len(elements) > 1 and elements[1]:
                document.header["schedule_id"] = elements[1]
            
            # BFR03 - Release Number
            if len(elements) > 2 and elements[2]:
                document.header["release_number"] = elements[2]
            
            # BFR04 - Schedule Type Qualifier
            if len(elements) > 3 and elements[3]:
                stype = elements[3]
                document.header["schedule_type_code"] = stype
                document.header["schedule_type"] = SCHEDULE_TYPE_CODES.get(stype, stype)
            
            # BFR05 - Schedule Quantity Qualifier
            if len(elements) > 4 and elements[4]:
                document.header["quantity_qualifier"] = elements[4]
            
            # BFR06 - Date (Schedule Date)
            if len(elements) > 5 and elements[5]:
                document.header["schedule_date"] = self._format_date(elements[5])
                document.date = document.header["schedule_date"]
            
            # BFR07 - Date (Horizon Start)
            if len(elements) > 6 and elements[6]:
                document.header["horizon_start"] = self._format_date(elements[6])
            
            # BFR08 - Date (Horizon End)
            if len(elements) > 7 and elements[7]:
                document.header["horizon_end"] = self._format_date(elements[7])
        
        # Parse REF (Reference Identification)
        ref_segments = self.get_all_segments_by_id(segments, "REF")
        document.header["references"] = []
        for ref in ref_segments:
            if len(ref["elements"]) >= 2:
                document.header["references"].append({
                    "qualifier": ref["elements"][0],
                    "value": ref["elements"][1],
                })
        
        # Parse N1 (Party Identification) loops
        document.header["parties"] = self._parse_parties(segments)
        
        # Parse LIN/FST/SHP loops (Line Item Detail with Forecasts)
        self._parse_line_items(segments, document)
        
        # Parse CTT (Transaction Totals)
        ctt = self.get_segment_by_id(segments, "CTT")
        if ctt:
            document.summary["total_line_items"] = ctt["elements"][0] if len(ctt["elements"]) > 0 else None
        
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
            
            # Look for N3/N4
            for i in range(n1_idx + 1, min(end_idx, n1_idx + 5)):
                if i < len(segments):
                    if segments[i]["id"] == "N3":
                        n3 = segments[i]
                        party["address_line1"] = n3["elements"][0] if len(n3["elements"]) > 0 else None
                    elif segments[i]["id"] == "N4":
                        n4 = segments[i]
                        party["city"] = n4["elements"][0] if len(n4["elements"]) > 0 else None
                        party["state"] = n4["elements"][1] if len(n4["elements"]) > 1 else None
                        party["zip"] = n4["elements"][2] if len(n4["elements"]) > 2 else None
            
            parties.append(party)
        
        return parties
    
    def _parse_line_items(self, segments: list, document: EDIDocument) -> None:
        """Parse LIN/FST/SHP loops for schedule line items."""
        
        lin_indices = []
        for i, seg in enumerate(segments):
            if seg["id"] == "LIN":
                lin_indices.append(i)
        
        for idx, lin_idx in enumerate(lin_indices):
            lin = segments[lin_idx]
            end_idx = lin_indices[idx + 1] if idx + 1 < len(lin_indices) else len(segments)
            
            line_item = {
                "line_number": lin["elements"][0] if len(lin["elements"]) > 0 else str(idx + 1),
            }
            
            # Parse product IDs from LIN
            product_ids = {}
            i = 1
            while i + 1 < len(lin["elements"]):
                qualifier = lin["elements"][i]
                value = lin["elements"][i + 1] if i + 1 < len(lin["elements"]) else ""
                if qualifier and value:
                    qual_names = {
                        "BP": "Buyer's Part Number",
                        "VP": "Vendor's Part Number",
                        "UP": "UPC",
                        "PI": "Purchaser's Item Code",
                    }
                    label = qual_names.get(qualifier, qualifier)
                    product_ids[label] = value
                i += 2
            
            line_item["product_ids"] = product_ids
            line_item["product_id"] = next(iter(product_ids.values()), None)
            
            # Look for UIT (Unit Detail)
            for i in range(lin_idx + 1, min(end_idx, lin_idx + 5)):
                if i < len(segments) and segments[i]["id"] == "UIT":
                    uit = segments[i]
                    line_item["unit"] = uit["elements"][0] if len(uit["elements"]) > 0 else None
                    break
            
            # Look for PID (Description)
            for i in range(lin_idx + 1, min(end_idx, lin_idx + 10)):
                if i < len(segments) and segments[i]["id"] == "PID":
                    pid = segments[i]
                    if len(pid["elements"]) > 4 and pid["elements"][4]:
                        line_item["description"] = pid["elements"][4]
                    break
            
            # Parse FST (Forecast Schedule) segments
            forecasts = []
            for i in range(lin_idx + 1, end_idx):
                if i < len(segments) and segments[i]["id"] == "FST":
                    fst = segments[i]
                    elements = fst["elements"]
                    
                    forecast = {}
                    
                    # FST01 - Quantity
                    if len(elements) > 0 and elements[0]:
                        forecast["quantity"] = elements[0]
                    
                    # FST02 - Forecast Qualifier
                    if len(elements) > 1 and elements[1]:
                        qual = elements[1]
                        forecast["qualifier_code"] = qual
                        forecast["qualifier"] = FORECAST_QUALIFIER_CODES.get(qual, qual)
                    
                    # FST03 - Forecast Timing Qualifier
                    if len(elements) > 2 and elements[2]:
                        timing = elements[2]
                        forecast["timing_code"] = timing
                        forecast["timing"] = FORECAST_TIMING_CODES.get(timing, timing)
                    
                    # FST04 - Date
                    if len(elements) > 3 and elements[3]:
                        forecast["date"] = self._format_date(elements[3])
                    
                    # FST05 - Date (End Date for range)
                    if len(elements) > 4 and elements[4]:
                        forecast["end_date"] = self._format_date(elements[4])
                    
                    forecasts.append(forecast)
            
            if forecasts:
                line_item["forecasts"] = forecasts
                # Calculate total forecast quantity
                total_qty = sum(float(f.get("quantity", 0)) for f in forecasts if f.get("quantity"))
                line_item["total_forecast_quantity"] = total_qty
            
            # Parse SHP (Shipped/Received Information)
            shipments = []
            for i in range(lin_idx + 1, end_idx):
                if i < len(segments) and segments[i]["id"] == "SHP":
                    shp = segments[i]
                    elements = shp["elements"]
                    
                    ship_entry = {}
                    if len(elements) > 0:
                        ship_entry["quantity_qualifier"] = elements[0]
                    if len(elements) > 1:
                        ship_entry["quantity"] = elements[1]
                    if len(elements) > 2:
                        ship_entry["date_qualifier"] = elements[2]
                    if len(elements) > 3:
                        ship_entry["date"] = self._format_date(elements[3])
                    
                    shipments.append(ship_entry)
            
            if shipments:
                line_item["shipments"] = shipments
            
            document.line_items.append(line_item)
        
        # Summary
        document.summary["total_items"] = len(document.line_items)
    
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
