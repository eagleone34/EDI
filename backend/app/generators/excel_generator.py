"""
Excel Generator for EDI documents.
"""

from typing import Optional
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from app.parsers.base import EDIDocument


class ExcelGenerator:
    """Generate Excel output from parsed EDI documents."""
    
    # Styling constants
    HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
    HEADER_FILL = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")
    HEADER_ALIGNMENT = Alignment(horizontal="center", vertical="center")
    THIN_BORDER = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    def generate(self, document: EDIDocument, output_path: Optional[str] = None) -> bytes:
        """
        Generate an Excel file from an EDI document.
        
        Args:
            document: Parsed EDI document
            output_path: Optional path to save the Excel file
            
        Returns:
            Excel file as bytes
        """
        wb = Workbook()
        
        # Create worksheets
        self._create_header_sheet(wb, document)
        self._create_line_items_sheet(wb, document)
        self._create_summary_sheet(wb, document)
        
        # Remove default sheet if we created others
        if "Sheet" in wb.sheetnames and len(wb.sheetnames) > 1:
            del wb["Sheet"]
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        excel_bytes = output.read()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(excel_bytes)
        
        return excel_bytes
    
    def _create_header_sheet(self, wb: Workbook, document: EDIDocument) -> None:
        """Create the header/document info sheet."""
        ws = wb.active
        ws.title = "Document Info"
        
        # Title
        ws["A1"] = f"EDI {document.transaction_type} - {document.transaction_name}"
        ws["A1"].font = Font(bold=True, size=16, color="1E40AF")
        ws.merge_cells("A1:B1")
        
        # Document info
        info_data = [
            ("Transaction Type", document.transaction_type),
            ("Transaction Name", document.transaction_name),
            ("Sender ID", document.sender_id or "—"),
            ("Receiver ID", document.receiver_id or "—"),
            ("Control Number", document.control_number or "—"),
            ("Date", document.date or "—"),
        ]
        
        # Add header info
        for key, value in document.header.items():
            if not isinstance(value, (list, dict)):
                info_data.append((key.replace("_", " ").title(), str(value)))
        
        row = 3
        for label, value in info_data:
            ws[f"A{row}"] = label
            ws[f"A{row}"].font = Font(bold=True)
            ws[f"B{row}"] = value
            row += 1
        
        # Set column widths
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 40
    
    def _create_line_items_sheet(self, wb: Workbook, document: EDIDocument) -> None:
        """Create the line items sheet."""
        if not document.line_items:
            return
        
        ws = wb.create_sheet("Line Items")
        
        # Determine columns from first item
        if document.line_items:
            columns = list(document.line_items[0].keys())
        else:
            return
        
        # Headers
        for col_idx, col_name in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_name.replace("_", " ").title())
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = self.HEADER_ALIGNMENT
            cell.border = self.THIN_BORDER
        
        # Data rows
        for row_idx, item in enumerate(document.line_items, 2):
            for col_idx, col_name in enumerate(columns, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=item.get(col_name, ""))
                cell.border = self.THIN_BORDER
                
                # Alternate row colors
                if row_idx % 2 == 0:
                    cell.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        
        # Auto-fit columns
        for col_idx in range(1, len(columns) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 15
    
    def _create_summary_sheet(self, wb: Workbook, document: EDIDocument) -> None:
        """Create the summary sheet."""
        if not document.summary:
            return
        
        ws = wb.create_sheet("Summary")
        
        ws["A1"] = "Summary"
        ws["A1"].font = Font(bold=True, size=14, color="1E40AF")
        
        row = 3
        for key, value in document.summary.items():
            ws[f"A{row}"] = key.replace("_", " ").title()
            ws[f"A{row}"].font = Font(bold=True)
            ws[f"B{row}"] = str(value)
            row += 1
        
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 30
