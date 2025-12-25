"""
PDF Generator for EDI documents.
"""

from typing import Optional
from pathlib import Path
import tempfile

# WeasyPrint for PDF generation
# from weasyprint import HTML, CSS

from app.parsers.base import EDIDocument


class PDFGenerator:
    """Generate PDF output from parsed EDI documents."""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"
    
    def generate(self, document: EDIDocument, output_path: Optional[str] = None) -> bytes:
        """
        Generate a PDF from an EDI document.
        
        Args:
            document: Parsed EDI document
            output_path: Optional path to save the PDF
            
        Returns:
            PDF file as bytes
        """
        # Generate HTML first
        html_content = self._build_html(document)
        
        # TODO: Use WeasyPrint to convert HTML to PDF
        # For now, return placeholder
        # html = HTML(string=html_content)
        # pdf_bytes = html.write_pdf()
        
        pdf_bytes = html_content.encode('utf-8')  # Placeholder
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _build_html(self, document: EDIDocument) -> str:
        """Build HTML content for the PDF."""
        
        # Build line items table
        line_items_html = ""
        if document.line_items:
            line_items_html = """
            <table class="line-items">
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
                line_items_html += f"""
                    <tr>
                        <td>{item.get('line_number', '—')}</td>
                        <td>{item.get('product_id', '—')}</td>
                        <td>{item.get('quantity', item.get('quantity_invoiced', item.get('quantity_shipped', '—')))}</td>
                        <td>{item.get('unit', '—')}</td>
                        <td>{item.get('unit_price', '—')}</td>
                    </tr>
                """
            line_items_html += "</tbody></table>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>EDI {document.transaction_type} - {document.transaction_name}</title>
            <style>
                body {{
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    margin: 40px;
                    color: #333;
                    line-height: 1.6;
                }}
                .header {{
                    border-bottom: 3px solid #2563eb;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #2563eb;
                    margin: 0;
                    font-size: 28px;
                }}
                .header .doc-type {{
                    color: #64748b;
                    font-size: 14px;
                    margin-top: 5px;
                }}
                .section {{
                    margin-bottom: 25px;
                }}
                .section h2 {{
                    color: #1e40af;
                    font-size: 18px;
                    border-bottom: 1px solid #e2e8f0;
                    padding-bottom: 8px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                }}
                .info-item {{
                    background: #f8fafc;
                    padding: 12px;
                    border-radius: 6px;
                }}
                .info-item label {{
                    font-size: 12px;
                    color: #64748b;
                    text-transform: uppercase;
                }}
                .info-item value {{
                    font-size: 16px;
                    font-weight: 600;
                    display: block;
                    margin-top: 4px;
                }}
                .line-items {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                .line-items th {{
                    background: #1e40af;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                .line-items td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .line-items tr:nth-child(even) {{
                    background: #f8fafc;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    font-size: 12px;
                    color: #64748b;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{document.transaction_name}</h1>
                <div class="doc-type">EDI Transaction Set {document.transaction_type}</div>
            </div>
            
            <div class="section">
                <h2>Document Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Sender ID</label>
                        <value>{document.sender_id or '—'}</value>
                    </div>
                    <div class="info-item">
                        <label>Receiver ID</label>
                        <value>{document.receiver_id or '—'}</value>
                    </div>
                    <div class="info-item">
                        <label>Control Number</label>
                        <value>{document.control_number or '—'}</value>
                    </div>
                    <div class="info-item">
                        <label>Date</label>
                        <value>{document.date or '—'}</value>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Line Items</h2>
                {line_items_html if line_items_html else '<p>No line items in this document.</p>'}
            </div>
            
            <div class="footer">
                Generated by EDI.email | Transform EDI files into readable formats
            </div>
        </body>
        </html>
        """
        
        return html
