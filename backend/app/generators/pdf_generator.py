"""
PDF Generator for EDI documents using ReportLab.
"""

from typing import Optional, List
from pathlib import Path
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.parsers.base import EDIDocument


class PDFGenerator:
    """Generate PDF output from parsed EDI documents using ReportLab."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='DocTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceBefore=20,
            spaceAfter=10,
            borderColor=colors.HexColor('#e2e8f0'),
            borderWidth=1,
            borderPadding=5
        ))
        self.styles.add(ParagraphStyle(
            name='InfoLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
        ))
        self.styles.add(ParagraphStyle(
            name='InfoValue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1e293b'),
        ))
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        ))
    
    def generate(self, document: EDIDocument, output_path: Optional[str] = None) -> bytes:
        """Generate a PDF from a single EDI document."""
        return self.generate_all([document], output_path)
    
    def generate_all(self, documents: List, output_path: Optional[str] = None) -> bytes:
        """
        Generate a PDF from multiple EDI documents.
        Creates a multi-page PDF with all POs.
        """
        if not documents:
            documents = [EDIDocument(transaction_type="850", transaction_name="Purchase Order")]
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        story = []
        
        # If multiple documents, add summary page
        if len(documents) > 1:
            story.extend(self._build_summary_page(documents))
            story.append(PageBreak())
        
        # Add each document
        for idx, edi_doc in enumerate(documents, 1):
            if idx > 1:
                story.append(PageBreak())
            story.extend(self._build_document_content(edi_doc, idx, len(documents)))
        
        # Build the PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _build_summary_page(self, documents: List) -> List:
        """Build summary page content for multiple documents."""
        elements = []
        
        # Use the transaction info from first document
        doc_type = documents[0].transaction_type if documents else "850"
        doc_name = documents[0].transaction_name if documents else "Purchase Order"
        
        # Title
        elements.append(Paragraph(
            f"📦 {len(documents)} {doc_name}s",
            self.styles['DocTitle']
        ))
        elements.append(Paragraph(
            f"EDI {doc_type} Conversion Summary",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 30))
        
        # Summary table with document-type specific headers
        if doc_type == "810":
            headers = ['Invoice #', 'Invoice Date', 'Line Items', 'Total Amount']
        elif doc_type == "812":
            headers = ['Memo #', 'Date', 'Adjustments', 'Total Amount']
        elif doc_type == "856":
            headers = ['Shipment ID', 'Ship Date', 'Items', 'Weight']
        else:
            headers = ['PO Number', 'PO Date', 'Line Items', 'Total Amount']
        
        data = [headers]
        
        for doc in documents:
            # Get appropriate identifier and date based on doc type
            if doc_type == "810":
                id_val = doc.header.get("invoice_number", doc.header.get("po_number", "—"))
                date_val = doc.header.get("invoice_date", doc.header.get("po_date", "—"))
            elif doc_type == "812":
                id_val = doc.header.get("credit_debit_number", doc.header.get("po_number", "—"))
                date_val = doc.header.get("adjustment_date", doc.header.get("po_date", "—"))
            elif doc_type == "856":
                id_val = doc.header.get("shipment_id", doc.header.get("po_number", "—"))
                date_val = doc.header.get("ship_date", doc.header.get("po_date", "—"))
            else:
                id_val = doc.header.get("po_number", "—")
                date_val = doc.header.get("po_date", "—")
            
            line_count = str(len(doc.line_items))
            total = doc.summary.get("total_amount") or doc.summary.get("calculated_total")
            total_str = f"${total:,.2f}" if isinstance(total, (int, float)) else "—"
            data.append([id_val, date_val, line_count, total_str])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_document_content(self, document: EDIDocument, idx: int, total: int) -> List:
        """Build content for a single document."""
        elements = []
        
        # Get document type info
        doc_name = document.transaction_name or "Document"
        doc_type = document.transaction_type or "850"
        
        # Get primary identifier based on document type
        if doc_type == "810":
            primary_id = document.header.get("invoice_number", document.header.get("po_number", "—"))
            id_label = "Invoice"
        elif doc_type == "812":
            primary_id = document.header.get("credit_debit_number", document.header.get("po_number", "—"))
            id_label = "Memo"
        elif doc_type == "856":
            primary_id = document.header.get("shipment_id", document.header.get("po_number", "—"))
            id_label = "Shipment"
        else:
            primary_id = document.header.get("po_number", "—")
            id_label = "PO"
        
        # Header
        if total > 1:
            title_text = f"{doc_name} {idx} of {total} — {id_label} #{primary_id}"
        else:
            title_text = f"{doc_name} — {id_label} #{primary_id}"
        
        elements.append(Paragraph(title_text, self.styles['DocTitle']))
        elements.append(Spacer(1, 10))
        
        # Section title based on document type
        if doc_type == "810":
            section_title = "Invoice Information"
        elif doc_type == "812":
            section_title = "Adjustment Information"
        elif doc_type == "856":
            section_title = "Shipment Information"
        else:
            section_title = "Order Information"
        
        elements.append(Paragraph(section_title, self.styles['SectionTitle']))
        
        # Specialized info for 812
        if doc_type == "812":
            elements.extend(self._build_812_general_info(document))
        else:
            elements.extend(self._build_order_info(document))
        
        # Parties section
        parties = document.header.get("parties", [])
        if parties:
            elements.append(Paragraph("Parties & Addresses", self.styles['SectionTitle']))
            elements.extend(self._build_parties_table(parties))
        
        # Line Items section
        if document.line_items:
            if doc_type == "812":
                elements.append(Paragraph(f"Adjustment Details ({len(document.line_items)} items)", self.styles['SectionTitle']))
                elements.extend(self._build_812_details(document.line_items))
            else:
                elements.append(Paragraph(f"Line Items ({len(document.line_items)} items)", self.styles['SectionTitle']))
                elements.extend(self._build_line_items_table(document.line_items))
        
        # Summary section
        total_amount = document.summary.get("total_amount") or document.summary.get("calculated_total")
        if total_amount:
            elements.append(Paragraph("Summary", self.styles['SectionTitle']))
            elements.append(Paragraph(
                f"<b>Total Amount:</b> ${total_amount:,.2f}",
                ParagraphStyle(
                    name='TotalAmount',
                    parent=self.styles['Normal'],
                    fontSize=16,
                    textColor=colors.HexColor('#059669'),
                    spaceBefore=10
                )
            ))
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(
            "Generated by ReadableEDI — Transform EDI files into readable formats",
            self.styles['Footer']
        ))
        
        return elements
    
    def _build_order_info(self, document: EDIDocument) -> List:
        """Build order information table."""
        data = []
        
        info_items = [
            ("PO Number", document.header.get("po_number", "—")),
            ("PO Date", document.header.get("po_date", "—")),
            ("Purpose", document.header.get("purpose", "—")),
            ("Order Type", document.header.get("order_type", "—")),
            ("Sender ID", document.sender_id or "—"),
            ("Receiver ID", document.receiver_id or "—"),
            ("Payment Terms", document.header.get("payment_terms", "—")),
            ("F.O.B.", document.header.get("fob", "—")),
        ]
        
        # Build 2-column layout
        row = []
        for i, (label, value) in enumerate(info_items):
            if value and value != "—":
                row.append(f"{label}: {value}")
                if len(row) == 2:
                    data.append(row)
                    row = []
        if row:
            row.append("")
            data.append(row)
        
        if not data:
            return []
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        
        return [table, Spacer(1, 10)]
    
    def _build_parties_table(self, parties: List) -> List:
        """Build parties table with proper text wrapping."""
        elements = []
        
        # Create a style for wrapped text
        wrap_style = ParagraphStyle(
            name='PartyText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
        )
        name_style = ParagraphStyle(
            name='PartyName',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            leading=12,
        )
        
        for party in parties[:4]:  # Limit to 4
            name = party.get("name", "Unknown")
            party_type = party.get("type", party.get("type_code", ""))
            
            address_parts = []
            if party.get("address_line1"):
                address_parts.append(party["address_line1"])
            if party.get("address_line2"):
                address_parts.append(party["address_line2"])
            city_state = ", ".join(filter(None, [
                party.get("city", ""),
                party.get("state", "")
            ]))
            if city_state:
                zip_code = party.get("zip", "")
                address_parts.append(f"{city_state} {zip_code}".strip())
            
            address = "<br/>".join(address_parts)
            
            # Create table row with wrapped text
            data = [[
                Paragraph(f"<b>[{party_type}]</b>", wrap_style),
                Paragraph(f"<b>{name}</b>", name_style),
                Paragraph(address, wrap_style)
            ]]
            
            table = Table(data, colWidths=[0.7*inch, 2.5*inch, 2.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dbeafe')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 4))
        
        elements.append(Spacer(1, 6))
        return elements
    
    def _build_line_items_table(self, line_items: List) -> List:
        """Build line items table with proper text wrapping."""
        # Create styles for wrapped text
        header_style = ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER,
        )
        cell_style = ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
        )
        right_style = ParagraphStyle(
            name='TableCellRight',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_RIGHT,
        )
        center_style = ParagraphStyle(
            name='TableCellCenter',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
        )
        
        # Header row
        headers = ['Line', 'Product ID', 'Description', 'Qty', 'Unit', 'Price', 'Total']
        header_row = [Paragraph(f"<b>{h}</b>", header_style) for h in headers]
        data = [header_row]
        
        for item in line_items:
            line_num = str(item.get("line_number", "—"))
            product_id = str(item.get("product_id", "—"))
            description = str(item.get("description", "—"))
            qty = str(item.get("quantity", "—"))
            unit = str(item.get("unit", "—"))
            
            unit_price = item.get("unit_price", "—")
            try:
                unit_price = f"${float(unit_price):,.2f}"
            except (ValueError, TypeError):
                unit_price = "—"
            
            total = item.get("total", "")
            try:
                total = f"${float(total):,.2f}" if total else "—"
            except (ValueError, TypeError):
                total = "—"
            
            row = [
                Paragraph(line_num, center_style),
                Paragraph(product_id, cell_style),
                Paragraph(description, cell_style),
                Paragraph(qty, center_style),
                Paragraph(unit, center_style),
                Paragraph(unit_price, right_style),
                Paragraph(total, right_style),
            ]
            data.append(row)
        
        # Adjusted column widths to fit content better
        table = Table(data, colWidths=[0.4*inch, 0.9*inch, 2.3*inch, 0.4*inch, 0.4*inch, 0.7*inch, 0.7*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            # Data rows
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return [table, Spacer(1, 10)]
    def _build_812_general_info(self, document: EDIDocument) -> List:
        """Build 812-specific general information table."""
        h = document.header
        data = []
        
        # Build fields list
        fields = [
            ("Date", h.get("adjustment_date")),
            ("Adj Number", h.get("credit_debit_number")),
            ("Handling Code", h.get("transaction_handling_desc")),
            ("Amount", h.get("amount")),
            ("Flag Code", h.get("credit_debit_flag_desc")),
            ("Invoice #", h.get("invoice_number")),
            ("PO Number", h.get("po_number")),
            ("Purpose", h.get("purpose_code")),
            ("Type", h.get("transaction_type_desc")),
            ("Currency", h.get("currency"))
        ]
        
        row_buffer = []
        for label, val in fields:
            if val:
                row_buffer.append(f"{label}: {val}")
                if len(row_buffer) == 2:
                    data.append(row_buffer)
                    row_buffer = []
        if row_buffer:
            row_buffer.append("")
            data.append(row_buffer)
            
        if not data:
            return []
            
        # Contacts
        contacts = h.get("contacts", [])
        if contacts:
            data.append(["----------", "----------"]) # Separator
            for c in contacts:
                if c.get("name"):
                    data.append([f"Contact: {c['name']}", f"Tel: {c.get('comm_number', '—')}"])

        # Styled Table (similar to Order Info)
        table = Table(data, colWidths=[3.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        
        return [table, Spacer(1, 10)]

    def _build_812_details(self, line_items: List) -> List:
        """Build 812 adjustment details blocks."""
        elements = []
        
        detail_style = ParagraphStyle(
            name='DetailLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#475569'),
        )
        val_style = ParagraphStyle(
            name='DetailValue',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        )

        for item in line_items:
            # Build data grid for each item
            data = []
            
            # Helper to create row pair
            def make_pair(l1, v1, l2=None, v2=None):
                p1 = [Paragraph(l1, detail_style), Paragraph(v1 or "", val_style)]
                p2 = [Paragraph(l2, detail_style), Paragraph(v2 or "", val_style)] if l2 else ["", ""]
                return p1 + p2

            # Row 1
            data.append(make_pair(
                "Reason:", item.get("adjustment_reason", "—"),
                "Flag:", item.get("credit_debit_type", "—")
            ))
            # Row 2
            amt = item.get("adjustment_amount", "—")
            try: amt = f"${float(amt):,.2f}" 
            except: pass
            data.append(make_pair(
                "Amount:", amt,
                "Quantity:", item.get("quantity", "—")
            ))
            # Row 3
            price = item.get("unit_price", "—")
            try: price = f"${float(price):.2f}"
            except: pass
            data.append(make_pair(
                "Unit Price:", price,
                "Unit:", item.get("unit", "—")
            ))
            # Row 4 - Part Numbers
            parts = item.get("part_numbers", {})
            part_str = ", ".join([f"{k}: {v}" for k,v in parts.items()])
            if part_str:
                data.append([Paragraph("Parts:", detail_style), Paragraph(part_str, val_style), "", ""])
            
            # Message
            if item.get("message"):
                data.append([Paragraph("Note:", detail_style), Paragraph(item["message"], val_style), "", ""],)

            # Create Table
            table = Table(data, colWidths=[0.8*inch, 2.2*inch, 0.8*inch, 2.2*inch])
            
            # Build style commands dynamically to avoid passing None
            style_cmds = [
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
            
            if part_str:
                style_cmds.append(('SPAN', (1, -2), (3, -2)))
            
            if item.get("message"):
                style_cmds.append(('SPAN', (1, -1), (3, -1)))
            
            table.setStyle(TableStyle(style_cmds))
            
            elements.append(table)
            elements.append(Spacer(1, 8)) # Space between items
            
        return elements
