"""
Enhanced HTML Generator for EDI documents.
Produces professional, multi-section output matching industry standards.
"""

from typing import Optional, Dict, Any, List

from app.parsers.base import EDIDocument


class HTMLGenerator:
    """Generate professional HTML output from parsed EDI documents."""
    
    def generate(self, document: EDIDocument, output_path: Optional[str] = None) -> bytes:
        """
        Generate HTML from an EDI document.
        
        Args:
            document: Parsed EDI document
            output_path: Optional path to save the HTML
            
        Returns:
            HTML content as bytes
        """
        html_content = self._build_html(document)
        html_bytes = html_content.encode('utf-8')
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(html_bytes)
        
        return html_bytes
    
    def _build_html(self, document: EDIDocument) -> str:
        """Build comprehensive, professional HTML content."""
        
        # Build Order Information section
        order_info_html = self._build_order_info(document)
        
        # Build Parties/Addresses section
        parties_html = self._build_parties(document)
        
        # Build Dates section
        dates_html = self._build_dates(document)
        
        # Build Terms section
        terms_html = self._build_terms(document)
        
        # Build Line Items table
        line_items_html = self._build_line_items(document)
        
        # Build Summary section
        summary_html = self._build_summary(document)
        
        # Build Notes section
        notes_html = self._build_notes(document)
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EDI {document.transaction_type} - {document.transaction_name}</title>
            <style>
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: #f8fafc;
                    color: #1e293b;
                    font-size: 14px;
                    line-height: 1.5;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1100px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                    color: white;
                    padding: 24px 32px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .header h1 {{
                    font-size: 24px;
                    font-weight: 600;
                }}
                .header .doc-id {{
                    font-size: 18px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 24px 32px;
                }}
                .section {{
                    margin-bottom: 24px;
                }}
                .section-title {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #1e40af;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #e2e8f0;
                    margin-bottom: 16px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                }}
                .info-row {{
                    display: flex;
                    padding: 8px 0;
                    border-bottom: 1px solid #f1f5f9;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #64748b;
                    min-width: 160px;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .info-value {{
                    color: #1e293b;
                    flex: 1;
                }}
                .party-card {{
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 12px;
                }}
                .party-card .party-type {{
                    font-size: 12px;
                    font-weight: 600;
                    color: #1e40af;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 8px;
                }}
                .party-card .party-name {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #1e293b;
                    margin-bottom: 4px;
                }}
                .party-card .party-address {{
                    color: #64748b;
                    line-height: 1.6;
                }}
                .party-card .party-contact {{
                    margin-top: 8px;
                    padding-top: 8px;
                    border-top: 1px solid #e2e8f0;
                    font-size: 13px;
                    color: #64748b;
                }}
                .parties-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 16px;
                }}
                .dates-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 12px;
                }}
                .date-item {{
                    background: #f0f9ff;
                    border-left: 3px solid #3b82f6;
                    padding: 12px;
                    border-radius: 0 6px 6px 0;
                }}
                .date-label {{
                    font-size: 11px;
                    font-weight: 600;
                    color: #1e40af;
                    text-transform: uppercase;
                }}
                .date-value {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #1e293b;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                }}
                th {{
                    background: #1e40af;
                    color: white;
                    padding: 12px 8px;
                    text-align: left;
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-weight: 600;
                }}
                th:last-child, td:last-child {{
                    text-align: right;
                }}
                td {{
                    padding: 10px 8px;
                    border-bottom: 1px solid #e2e8f0;
                    vertical-align: top;
                }}
                tr:hover td {{
                    background: #f8fafc;
                }}
                .item-description {{
                    font-size: 12px;
                    color: #64748b;
                    margin-top: 4px;
                }}
                .product-ids {{
                    font-size: 11px;
                    color: #94a3b8;
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 16px;
                }}
                .summary-card {{
                    background: #f0fdf4;
                    border: 1px solid #bbf7d0;
                    border-radius: 8px;
                    padding: 16px;
                    text-align: center;
                }}
                .summary-card.total {{
                    background: #1e40af;
                    border-color: #1e40af;
                    color: white;
                }}
                .summary-label {{
                    font-size: 11px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    color: #16a34a;
                }}
                .summary-card.total .summary-label {{
                    color: rgba(255,255,255,0.8);
                }}
                .summary-value {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #166534;
                }}
                .summary-card.total .summary-value {{
                    color: white;
                }}
                .notes {{
                    background: #fefce8;
                    border: 1px solid #fef08a;
                    border-radius: 8px;
                    padding: 16px;
                }}
                .notes p {{
                    margin-bottom: 8px;
                    color: #854d0e;
                }}
                .notes p:last-child {{
                    margin-bottom: 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 16px;
                    background: #f8fafc;
                    color: #64748b;
                    font-size: 12px;
                    border-top: 1px solid #e2e8f0;
                }}
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                        border-radius: 0;
                    }}
                }}
                @media (max-width: 640px) {{
                    .header {{
                        flex-direction: column;
                        text-align: center;
                        gap: 8px;
                    }}
                    th, td {{
                        padding: 8px 4px;
                        font-size: 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{document.transaction_name}</h1>
                    <div class="doc-id">EDI {document.transaction_type}</div>
                </div>
                
                <div class="content">
                    {order_info_html}
                    {parties_html}
                    {dates_html}
                    {terms_html}
                    {line_items_html}
                    {summary_html}
                    {notes_html}
                </div>
                
                <div class="footer">
                    Generated by ReadableEDI — Transform EDI files into readable formats
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _build_order_info(self, document: EDIDocument) -> str:
        """Build order information section."""
        rows = []
        
        # PO Number
        if document.header.get("po_number"):
            rows.append(f'<div class="info-row"><span class="info-label">PO Number</span><span class="info-value"><strong>{document.header["po_number"]}</strong></span></div>')
        
        # PO Date
        if document.header.get("po_date"):
            rows.append(f'<div class="info-row"><span class="info-label">PO Date</span><span class="info-value">{document.header["po_date"]}</span></div>')
        
        # Purpose
        if document.header.get("purpose"):
            rows.append(f'<div class="info-row"><span class="info-label">Purpose</span><span class="info-value">{document.header["purpose"]}</span></div>')
        
        # Order Type
        if document.header.get("order_type"):
            rows.append(f'<div class="info-row"><span class="info-label">Order Type</span><span class="info-value">{document.header["order_type"]}</span></div>')
        
        # Sender/Receiver
        if document.sender_id:
            rows.append(f'<div class="info-row"><span class="info-label">Sender ID</span><span class="info-value">{document.sender_id}</span></div>')
        if document.receiver_id:
            rows.append(f'<div class="info-row"><span class="info-label">Receiver ID</span><span class="info-value">{document.receiver_id}</span></div>')
        
        # Control Number
        if document.control_number:
            rows.append(f'<div class="info-row"><span class="info-label">Control Number</span><span class="info-value">{document.control_number}</span></div>')
        
        # References
        refs = document.header.get("references", [])
        for ref in refs[:5]:  # Limit to 5 references
            if ref.get("value"):
                rows.append(f'<div class="info-row"><span class="info-label">{ref.get("type", ref.get("qualifier", "Ref"))}</span><span class="info-value">{ref["value"]}</span></div>')
        
        if rows:
            return f'''
            <div class="section">
                <div class="section-title">Order Information</div>
                <div class="info-rows">{"".join(rows)}</div>
            </div>
            '''
        return ""
    
    def _build_parties(self, document: EDIDocument) -> str:
        """Build parties/addresses section."""
        parties = document.header.get("parties", [])
        if not parties:
            return ""
        
        cards = []
        for party in parties:
            name = party.get("name", "Unknown")
            party_type = party.get("type", party.get("type_code", ""))
            
            # Build address
            address_lines = []
            if party.get("address_line1"):
                address_lines.append(party["address_line1"])
            if party.get("address_line2"):
                address_lines.append(party["address_line2"])
            
            city_state_zip = []
            if party.get("city"):
                city_state_zip.append(party["city"])
            if party.get("state"):
                city_state_zip.append(party["state"])
            if party.get("zip"):
                city_state_zip.append(party["zip"])
            
            if city_state_zip:
                address_lines.append(", ".join(city_state_zip[:2]) + (" " + city_state_zip[2] if len(city_state_zip) > 2 else ""))
            
            if party.get("country") and party["country"] not in ("US", "USA"):
                address_lines.append(party["country"])
            
            address_html = "<br>".join(address_lines) if address_lines else ""
            
            # Build contact
            contact_html = ""
            if party.get("contact_name") or party.get("contact_number"):
                contact_parts = []
                if party.get("contact_name"):
                    contact_parts.append(party["contact_name"])
                if party.get("contact_number"):
                    contact_parts.append(party["contact_number"])
                contact_html = f'<div class="party-contact">Contact: {" • ".join(contact_parts)}</div>'
            
            # Party ID
            id_html = ""
            if party.get("id"):
                id_html = f'<div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">ID: {party["id"]}</div>'
            
            cards.append(f'''
                <div class="party-card">
                    <div class="party-type">{party_type}</div>
                    <div class="party-name">{name}</div>
                    {id_html}
                    <div class="party-address">{address_html}</div>
                    {contact_html}
                </div>
            ''')
        
        return f'''
        <div class="section">
            <div class="section-title">Parties & Addresses</div>
            <div class="parties-grid">{"".join(cards)}</div>
        </div>
        '''
    
    def _build_dates(self, document: EDIDocument) -> str:
        """Build dates section."""
        dates = document.header.get("dates", {})
        if not dates:
            return ""
        
        items = []
        for label, value in dates.items():
            items.append(f'''
                <div class="date-item">
                    <div class="date-label">{label}</div>
                    <div class="date-value">{value}</div>
                </div>
            ''')
        
        return f'''
        <div class="section">
            <div class="section-title">Key Dates</div>
            <div class="dates-grid">{"".join(items)}</div>
        </div>
        '''
    
    def _build_terms(self, document: EDIDocument) -> str:
        """Build terms section."""
        rows = []
        
        if document.header.get("payment_terms"):
            rows.append(f'<div class="info-row"><span class="info-label">Payment Terms</span><span class="info-value">{document.header["payment_terms"]}</span></div>')
        
        if document.header.get("fob"):
            fob_text = document.header["fob"]
            if document.header.get("fob_location"):
                fob_text += f" - {document.header['fob_location']}"
            rows.append(f'<div class="info-row"><span class="info-label">F.O.B.</span><span class="info-value">{fob_text}</span></div>')
        
        if not rows:
            return ""
        
        return f'''
        <div class="section">
            <div class="section-title">Terms</div>
            {"".join(rows)}
        </div>
        '''
    
    def _build_line_items(self, document: EDIDocument) -> str:
        """Build line items table with descriptions."""
        if not document.line_items:
            return '<div class="section"><p>No line items in this document.</p></div>'
        
        rows = []
        for item in document.line_items:
            # Product info
            product_id = item.get("product_id", "—")
            description = item.get("description", "")
            
            # Build product IDs detail
            product_ids = item.get("product_ids", {})
            ids_html = ""
            if product_ids:
                id_parts = [f"{k}: {v}" for k, v in list(product_ids.items())[:3]]
                ids_html = f'<div class="product-ids">{" | ".join(id_parts)}</div>'
            
            # Price formatting
            unit_price = item.get("unit_price", "—")
            try:
                unit_price = f"${float(unit_price):,.2f}"
            except (ValueError, TypeError):
                pass
            
            # Total formatting
            total = item.get("total", "")
            if total:
                total = f"${float(total):,.2f}"
            else:
                total = "—"
            
            rows.append(f'''
                <tr>
                    <td>{item.get("line_number", "—")}</td>
                    <td>
                        <strong>{product_id}</strong>
                        {f'<div class="item-description">{description}</div>' if description else ""}
                        {ids_html}
                    </td>
                    <td>{item.get("quantity", "—")}</td>
                    <td>{item.get("unit", "—")}</td>
                    <td>{unit_price}</td>
                    <td>{total}</td>
                </tr>
            ''')
        
        return f'''
        <div class="section">
            <div class="section-title">Line Items</div>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 60px;">Line</th>
                            <th>Product</th>
                            <th style="width: 80px;">Qty</th>
                            <th style="width: 60px;">Unit</th>
                            <th style="width: 100px;">Unit Price</th>
                            <th style="width: 100px;">Total</th>
                        </tr>
                    </thead>
                    <tbody>{"".join(rows)}</tbody>
                </table>
            </div>
        </div>
        '''
    
    def _build_summary(self, document: EDIDocument) -> str:
        """Build summary section."""
        cards = []
        
        if document.summary.get("total_line_items"):
            cards.append(f'''
                <div class="summary-card">
                    <div class="summary-label">Line Items</div>
                    <div class="summary-value">{document.summary["total_line_items"]}</div>
                </div>
            ''')
        
        if document.summary.get("hash_total"):
            cards.append(f'''
                <div class="summary-card">
                    <div class="summary-label">Total Qty</div>
                    <div class="summary-value">{document.summary["hash_total"]}</div>
                </div>
            ''')
        
        # Total amount
        total = document.summary.get("total_amount") or document.summary.get("calculated_total")
        if total:
            cards.append(f'''
                <div class="summary-card total">
                    <div class="summary-label">Total Amount</div>
                    <div class="summary-value">${total:,.2f}</div>
                </div>
            ''')
        
        if not cards:
            return ""
        
        return f'''
        <div class="section">
            <div class="section-title">Summary</div>
            <div class="summary-grid">{"".join(cards)}</div>
        </div>
        '''
    
    def _build_notes(self, document: EDIDocument) -> str:
        """Build notes section."""
        notes = document.header.get("notes", [])
        if not notes:
            return ""
        
        note_items = "".join(f"<p>• {note}</p>" for note in notes if note.strip())
        
        if not note_items:
            return ""
        
        return f'''
        <div class="section">
            <div class="section-title">Notes</div>
            <div class="notes">{note_items}</div>
        </div>
        '''
