"""
HTML Generator for EDI documents.
"""

from typing import Optional

from app.parsers.base import EDIDocument


class HTMLGenerator:
    """Generate HTML output from parsed EDI documents."""
    
    def generate(self, document: EDIDocument, output_path: Optional[str] = None) -> str:
        """
        Generate HTML from an EDI document.
        
        Args:
            document: Parsed EDI document
            output_path: Optional path to save the HTML
            
        Returns:
            HTML content as string
        """
        html_content = self._build_html(document)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    def _build_html(self, document: EDIDocument) -> str:
        """Build responsive HTML content."""
        
        # Build line items
        line_items_html = ""
        if document.line_items:
            line_items_html = """
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Line #</th>
                            <th>Product ID</th>
                            <th>Quantity</th>
                            <th>Unit</th>
                            <th>Unit Price</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for item in document.line_items:
                qty = item.get('quantity', item.get('quantity_invoiced', item.get('quantity_shipped', '—')))
                line_items_html += f"""
                    <tr>
                        <td data-label="Line #">{item.get('line_number', '—')}</td>
                        <td data-label="Product ID">{item.get('product_id', '—')}</td>
                        <td data-label="Quantity">{qty}</td>
                        <td data-label="Unit">{item.get('unit', '—')}</td>
                        <td data-label="Unit Price">{item.get('unit_price', '—')}</td>
                    </tr>
                """
            line_items_html += "</tbody></table></div>"
        
        # Build header info cards
        header_cards = ""
        header_items = [
            ("Sender ID", document.sender_id),
            ("Receiver ID", document.receiver_id),
            ("Control Number", document.control_number),
            ("Date", document.date),
        ]
        for label, value in header_items:
            header_cards += f"""
                <div class="info-card">
                    <span class="label">{label}</span>
                    <span class="value">{value or '—'}</span>
                </div>
            """
        
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
                    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
                    min-height: 100vh;
                    padding: 20px;
                    color: #1e293b;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                    color: white;
                    padding: 30px;
                }}
                .header h1 {{
                    font-size: 28px;
                    margin-bottom: 8px;
                }}
                .header .badge {{
                    display: inline-block;
                    background: rgba(255, 255, 255, 0.2);
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-size: 14px;
                }}
                .content {{
                    padding: 30px;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .section h2 {{
                    font-size: 18px;
                    color: #1e40af;
                    margin-bottom: 16px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #e2e8f0;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                }}
                .info-card {{
                    background: #f8fafc;
                    padding: 16px;
                    border-radius: 10px;
                    border-left: 4px solid #2563eb;
                }}
                .info-card .label {{
                    display: block;
                    font-size: 12px;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 4px;
                }}
                .info-card .value {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #1e293b;
                }}
                .table-responsive {{
                    overflow-x: auto;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th {{
                    background: #1e40af;
                    color: white;
                    padding: 14px;
                    text-align: left;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                td {{
                    padding: 14px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                tr:nth-child(even) {{
                    background: #f8fafc;
                }}
                tr:hover {{
                    background: #f1f5f9;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background: #f8fafc;
                    color: #64748b;
                    font-size: 14px;
                }}
                .footer a {{
                    color: #2563eb;
                    text-decoration: none;
                }}
                
                @media (max-width: 600px) {{
                    .header h1 {{
                        font-size: 22px;
                    }}
                    table thead {{
                        display: none;
                    }}
                    table tr {{
                        display: block;
                        margin-bottom: 16px;
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                        overflow: hidden;
                    }}
                    table td {{
                        display: flex;
                        justify-content: space-between;
                        padding: 12px;
                    }}
                    table td::before {{
                        content: attr(data-label);
                        font-weight: 600;
                        color: #64748b;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{document.transaction_name}</h1>
                    <span class="badge">EDI {document.transaction_type}</span>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>Document Information</h2>
                        <div class="info-grid">
                            {header_cards}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Line Items</h2>
                        {line_items_html if line_items_html else '<p style="color: #64748b;">No line items in this document.</p>'}
                    </div>
                </div>
                
                <div class="footer">
                    Generated by <a href="https://edi.email">EDI.email</a> — Transform EDI files into readable formats
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
