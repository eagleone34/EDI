from typing import Any, Dict, List
from app.schemas.layout import LayoutConfig, LayoutSection, LayoutField, LayoutColumn

class DynamicGenerator:
    """
    Generates HTML based on a LayoutConfig and extracted EDI data.
    """
    
    def __init__(self, config: LayoutConfig):
        self.config = config

    def generate(self, doc) -> bytes:
        """
        Main entry point. Generates the full HTML document.
        """
        # 1. Build Document Title
        title = self.config.title_format.format(
            name=doc.transaction_name, 
            ref_number=doc.header.get('po_number', 'Unknown')
        )
        
        # 2. Render Content
        content_html = self.render_content(doc)
        
        # 3. Wrap in Main Template (Premium Style)
        full_html = f"""
        <div class="main-container">
            <!-- Header Card -->
            <div class="nav-card">
                <h1>{title}</h1>
                <div class="nav-links">
                    <span class="active">View</span>
                    <span>Raw Data</span>
                </div>
            </div>

            <!-- Dynamic Content -->
            {content_html}
        </div>
        """
        
        return self._wrap_in_html(title, full_html)

    def render_content(self, doc) -> str:
        """
        Renders the sections for a single document based on config.
        Returns HTML string (without <html> body wrappers).
        """
        sections_html = []
        for section in self.config.sections:
            if not section.visible:
                continue
            
            content = ""
            if section.type == "fields":
                content = self._render_fields_section(section, doc.header)
            elif section.type == "table":
                content = self._render_table_section(section, doc)
            elif section.type == "grid":
                 content = self._render_placeholder(section)
            
            if content:
                 sections_html.append(f"""
                    <div class="section">
                        <div class="section-title">{section.title}</div>
                        {content}
                    </div>
                 """)
        return "".join(sections_html)

    def _wrap_in_html(self, title: str, body_content: str) -> bytes:
        css = self._get_premium_css()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>{css}</style>
        </head>
        <body>
            {body_content}
        </body>
        </html>
        """.encode('utf-8')

    def _render_fields_section(self, section: LayoutSection, data: Dict[str, Any]) -> str:
        fields_html = []
        for field in section.fields:
            if not field.visible:
                continue
                
            val = data.get(field.key, "—")
            
            # Format value
            if field.type == "currency":
                try: val = f"${float(val):,.2f}"
                except: pass
            
            style_class = f"style-{field.style}" if field.style else ""
            
            fields_html.append(f"""
                <div class="field-group">
                    <div class="label">{field.label}</div>
                    <div class="value {style_class}">{val}</div>
                </div>
            """)
            
        return f'<div class="fields-grid">{"".join(fields_html)}</div>'

    def _render_table_section(self, section: LayoutSection, doc) -> str:
        # Get list source
        items = getattr(doc, section.data_source_key, []) or []
        
        headers = "".join([f'<th width="{col.width or ""}">{col.label}</th>' for col in section.columns])
        
        rows = []
        for item in items:
            cells = []
            for col in section.columns:
                val = item.get(col.key, "—")
                # Format
                if col.type == "currency":
                    try: val = f"${float(val):,.2f}"
                    except: pass
                
                style = f'class="font-{col.style}"' if col.style else ""
                cells.append(f'<td {style}>{val}</td>')
            
            rows.append(f'<tr>{"".join(cells)}</tr>')
            
        return f"""
        <div style="overflow-x: auto;">
            <table>
                <thead><tr>{headers}</tr></thead>
                <tbody>{"".join(rows)}</tbody>
            </table>
        </div>
        """

    def _render_placeholder(self, section):
        return f'<div style="padding:10px; color:#666;">Legacy Section: {section.title} (Not yet dynamic)</div>'

    def _get_premium_css(self) -> str:
        return """
            body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 20px; }
            .main-container { max_width: 1000px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); overflow: hidden; }
            .nav-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 24px; color: white; display: flex; justify-content: space-between; align-items: center; }
            .nav-card h1 { margin: 0; font-size: 20px; font-weight: 600; }
            .section { padding: 24px; border-bottom: 1px solid #e2e8f0; }
            .section-title { font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-weight: 600; margin-bottom: 16px; }
            
            .fields-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 24px; }
            .label { font-size: 12px; color: #64748b; margin-bottom: 4px; }
            .value { font-size: 14px; font-weight: 500; color: #0f172a; }
            .style-bold { font-weight: 700; }
            .style-highlight { color: #2563eb; font-weight: 600; }
            
            table { width: 100%; border-collapse: collapse; font-size: 14px; }
            th { text-align: left; padding: 12px; background: #f8fafc; color: #64748b; font-weight: 600; border-bottom: 2px solid #e2e8f0; }
            td { padding: 12px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }
            tr:last-child td { border-bottom: none; }
            .font-bold { font-weight: 600; }
        """
