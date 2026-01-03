import os
import sys

# Setup path and env
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from seed_config import set_db_env
    set_db_env()
    print("Loaded DB config from seed_config.py")
except ImportError:
    pass

from app.services.layout_service import LayoutService
from app.schemas.layout import LayoutConfig, LayoutSection, LayoutField, LayoutColumn

def seed_all_layouts():
    print("Beginning Full Migration Seeding (17 Configurations)...")
    
    # helper for basic headers
    def basic_header_section(fields):
        return LayoutSection(
            id="header_info",
            title="Overview",
            fields=fields
        )
        
    def parties_section():
        return LayoutSection(id="parties", title="Entities & Parties", type="grid")
        
    def dates_section():
        return LayoutSection(id="dates", title="Key Dates", type="grid")

    layouts = {}

    # --- 1. 810 Invoice (Legacy Migration) ---
    layouts["810"] = LayoutConfig(
        title_format="Invoice #{ref_number}",
        theme_color="emerald",
        sections=[
            LayoutSection(
                id="invoice_info",
                title="Invoice Information",
                fields=[
                    LayoutField(key="invoice_number", label="Invoice #", style="bold"),
                    LayoutField(key="date", label="Invoice Date", type="date"),
                    LayoutField(key="po_number", label="PO Reference"),
                    LayoutField(key="currency_code", label="Currency"),
                    LayoutField(key="terms_code", label="Payment Terms")
                ]
            ),
            parties_section(),
            dates_section(),
            LayoutSection(
                id="line_items",
                title="Line Items",
                type="table",
                data_source_key="line_items",
                columns=[
                    LayoutColumn(key="line_number", label="#", width="40px"),
                    LayoutColumn(key="product_id", label="Product ID", style="bold"),
                    LayoutColumn(key="description", label="Description"),
                    LayoutColumn(key="quantity", label="Qty", width="80px"),
                    LayoutColumn(key="unit", label="Unit", width="60px"),
                    LayoutColumn(key="unit_price", label="Price", width="100px", type="currency"),
                    LayoutColumn(key="total", label="Total", width="100px", type="currency")
                ]
            ),
            LayoutSection(
                id="summary",
                title="Totals",
                type="fields",
                fields=[
                    LayoutField(key="total_amount", label="Invoice Total", type="currency", style="highlight")
                ]
            )
        ]
    )

    # --- 2. 812 Credit/Debit Adjustment (Existing Dynamic) ---
    layouts["812"] = LayoutConfig(
        title_format="{name} #{ref_number}",
        theme_color="blue",
        sections=[
            LayoutSection(
                id="order_info",
                title="Adjustment Information",
                fields=[
                    LayoutField(key="credit_debit_number", label="Credit/Debit #", style="bold"),
                    LayoutField(key="date", label="Date", type="date"),
                    LayoutField(key="purchase_order_number", label="Original PO #Reference"),
                    LayoutField(key="transaction_handling_code", label="Handling Code"),
                    LayoutField(key="amount", label="Total Adjustment", type="currency", style="highlight")
                ]
            ),
            parties_section(),
            LayoutSection(
                id="line_items",
                title="Adjustment Details",
                type="table",
                data_source_key="line_items",
                columns=[
                    LayoutColumn(key="line_number", label="Line", width="60px"),
                    LayoutColumn(key="assigned_id", label="Item ID", style="bold"),
                    LayoutColumn(key="adjustment_reason", label="Reason"),
                    LayoutColumn(key="quantity", label="Qty", width="80px"),
                    LayoutColumn(key="unit_price", label="Price", width="100px", type="currency"),
                    LayoutColumn(key="adjustment_amount", label="Amount", width="100px", type="currency")
                ]
            )
        ]
    )

    # --- 3. 816 Organizational Relationships ---
    layouts["816"] = LayoutConfig(
        title_format="Org Chart: #{ref_number}",
        theme_color="purple",
        sections=[
            basic_header_section([LayoutField(key="ref_number", label="Ref #", style="bold")]),
            LayoutSection(id="relationships", title="Relationships", type="grid") # Placeholder for now
        ]
    )

    # --- 4. 820 Payment Remittance ---
    layouts["820"] = LayoutConfig(
        title_format="Remittance Advice #{ref_number}",
        theme_color="indigo",
        sections=[
            basic_header_section([
                LayoutField(key="check_number", label="Check/Trace #", style="bold"),
                LayoutField(key="total_amount", label="Total Paid", type="currency", style="highlight"),
                LayoutField(key="date", label="Effective Date", type="date")
            ]),
            parties_section(),
            LayoutSection(id="invoices", title="Paid Invoices", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="invoice_number", label="Invoice #", style="bold"),
                    LayoutColumn(key="po_number", label="PO #"),
                    LayoutColumn(key="amount_paid", label="Amount Paid", type="currency"),
                    LayoutColumn(key="discount_taken", label="Discount", type="currency")
                ]
            )
        ]
    )

    # --- 5. 824 Application Advice ---
    layouts["824"] = LayoutConfig(
        title_format="App Advice: {name}",
        theme_color="gray",
        sections=[
            basic_header_section([
                LayoutField(key="control_number", label="Control #"),
                LayoutField(key="status_code", label="Status", style="bold")
            ]),
            LayoutSection(id="errors", title="Errors & Notes", type="table", data_source_key="errors",
                columns=[
                    LayoutColumn(key="code", label="Code", width="80px"),
                    LayoutColumn(key="message", label="Message")
                ]
            )
        ]
    )

    # --- 6. 830 Planning Schedule ---
    layouts["830"] = LayoutConfig(
        title_format="Planning Schedule #{ref_number}",
        theme_color="orange",
        sections=[
            basic_header_section([
                LayoutField(key="schedule_number", label="Schedule #", style="bold"),
                LayoutField(key="date_range", label="Horizon")
            ]),
            parties_section(),
            dates_section(),
            LayoutSection(id="forecast", title="Forecasts", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="item_number", label="Item #", style="bold"),
                    LayoutColumn(key="date", label="Date", type="date"),
                    LayoutColumn(key="quantity", label="Qty"),
                    LayoutColumn(key="type", label="Type")
                ]
            )
        ]
    )

    # --- 7. 850 Purchase Order (Existing Dynamic) ---
    layouts["850"] = LayoutConfig(
        title_format="Purchase Order #{ref_number}",
        theme_color="blue",
        sections=[
            LayoutSection(
                id="order_info",
                title="Order Information",
                fields=[
                    LayoutField(key="po_number", label="PO Number", style="bold"),
                    LayoutField(key="po_date", label="PO Date", type="date"),
                    LayoutField(key="purpose_code", label="Purpose"),
                    LayoutField(key="currency_code", label="Currency")
                ]
            ),
            parties_section(),
            dates_section(),
            LayoutSection(
                id="line_items",
                title="Line Items",
                type="table",
                data_source_key="line_items",
                columns=[
                    LayoutColumn(key="line_number", label="Line", width="60px"),
                    LayoutColumn(key="product_id", label="Product ID", style="bold"),
                    LayoutColumn(key="description", label="Description"),
                    LayoutColumn(key="quantity", label="Qty", width="80px"),
                    LayoutColumn(key="unit", label="Unit", width="60px"),
                    LayoutColumn(key="unit_price", label="Price", width="100px", type="currency"),
                    LayoutColumn(key="total", label="Total", width="100px", type="currency")
                ]
            )
        ]
    )

    # --- 8. 852 Product Activity (POS) ---
    layouts["852"] = LayoutConfig(
        title_format="Product Activity #{ref_number}",
        theme_color="cyan",
        sections=[
            basic_header_section([LayoutField(key="report_start", label="Start Date"), LayoutField(key="report_end", label="End Date")]),
            parties_section(),
            LayoutSection(id="activity", title="Sales & Inventory", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="item_number", label="Item/UPC", style="bold"),
                    LayoutColumn(key="location", label="Store #"),
                    LayoutColumn(key="qty_sold", label="Sold"),
                    LayoutColumn(key="qty_on_hand", label="On Hand"),
                    LayoutColumn(key="amount_sold", label="Sales $", type="currency")
                ]
            )
        ]
    )

    # --- 9. 855 PO Acknowledgment (Legacy Migration) ---
    layouts["855"] = LayoutConfig(
        title_format="Ack (855) for PO #{ref_number}",
        theme_color="green",
        sections=[
            basic_header_section([
                LayoutField(key="po_number", label="PO Number", style="bold"),
                LayoutField(key="ack_number", label="Ack/Ref #"),
                LayoutField(key="ack_date", label="Ack Date", type="date"),
                LayoutField(key="status", label="Overall Status")
            ]),
            parties_section(),
            LayoutSection(id="lines", title="Line Acknowledgment", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="line_number", label="#", width="40px"),
                    LayoutColumn(key="product_id", label="Product ID", style="bold"),
                    LayoutColumn(key="ack_code", label="Status Code", width="80px"),
                    LayoutColumn(key="ack_qty", label="Qty", width="80px"),
                    LayoutColumn(key="unit_price", label="Price", type="currency")
                ]
            )
        ]
    )

    # --- 10. 856 Ship Notice / ASN (Legacy Migration) ---
    layouts["856"] = LayoutConfig(
        title_format="Shipment #{ref_number}",
        theme_color="teal",
        sections=[
            LayoutSection(
                id="shipment_info",
                title="Shipment Overview",
                fields=[
                    LayoutField(key="shipment_id", label="Shipment ID", style="bold"),
                    LayoutField(key="date", label="Shipped Date", type="date"),
                    LayoutField(key="tracking_number", label="Tracking #"),
                    LayoutField(key="scac", label="Carrier")
                ]
            ),
            parties_section(),
            LayoutSection(
                id="packaging",
                title="Contents / Packaging",
                type="table",
                data_source_key="line_items",
                columns=[
                    LayoutColumn(key="carton_id", label="Carton", width="100px"),
                    LayoutColumn(key="product_id", label="Item", style="bold"),
                    LayoutColumn(key="shipped_qty", label="Qty"),
                    LayoutColumn(key="upc", label="UPC/GTIN")
                ]
            )
        ]
    )

    # --- 11. 860 PO Change Request ---
    layouts["860"] = LayoutConfig(
        title_format="PO Change #{ref_number}",
        theme_color="amber",
        sections=[
            basic_header_section([
                LayoutField(key="po_number", label="Original PO", style="bold"),
                LayoutField(key="change_type", label="Change Type")
            ]),
            LayoutSection(id="changes", title="Line Changes", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="line_number", label="#"),
                    LayoutColumn(key="product_id", label="Product"),
                    LayoutColumn(key="change_code", label="Change"),
                    LayoutColumn(key="old_qty", label="Old Qty"),
                    LayoutColumn(key="new_qty", label="New Qty")
                ]
            )
        ]
    )

    # --- 12. 861 Receiving Advice ---
    layouts["861"] = LayoutConfig(
        title_format="Receipt #{ref_number}",
        theme_color="lime",
        sections=[
            basic_header_section([LayoutField(key="receipt_number", label="Receipt #", style="bold")]),
            LayoutSection(id="received_lines", title="Received Items", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="product_id", label="Item", style="bold"),
                    LayoutColumn(key="qty_received", label="Qty Rcvd"),
                    LayoutColumn(key="condition_code", label="Condition")
                ]
            )
        ]
    )

    # --- 13. 864 Text Message ---
    layouts["864"] = LayoutConfig(
        title_format="Message #{ref_number}",
        theme_color="slate",
        sections=[
            basic_header_section([LayoutField(key="subject", label="Subject", style="bold")]),
            LayoutSection(
                id="message_body",
                title="Content",
                type="fields", # Or a new 'text' type? stick to fields for now or leverage table if lines
                fields=[
                     LayoutField(key="message_text", label="Body")
                ]
            )
        ]
    )
    
    # --- 14. 870 Order Status Report ---
    layouts["870"] = LayoutConfig(
        title_format="Order Status #{ref_number}",
        theme_color="sky",
        sections=[
            basic_header_section([LayoutField(key="report_id", label="Report #", style="bold")]),
            LayoutSection(id="statuses", title="Statuses", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="po_number", label="PO Ref"),
                    LayoutColumn(key="line_number", label="Line"),
                    LayoutColumn(key="status_code", label="Status"),
                    LayoutColumn(key="est_ship_date", label="Est. Ship", type="date")
                ]
            )
        ]
    )

    # --- 15. 875 Grocery PO ---
    layouts["875"] = LayoutConfig(
        title_format="Grocery PO #{ref_number}",
        theme_color="emerald",
        sections=[
            basic_header_section([
                LayoutField(key="po_number", label="PO #", style="bold"),
                LayoutField(key="delivery_date", label="Deliv. Date", type="date")
            ]),
            parties_section(),
            LayoutSection(id="grocery_lines", title="Line Items", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="line_number", label="#"),
                    LayoutColumn(key="upc", label="UPC", style="bold"),
                    LayoutColumn(key="quantity", label="Qty"),
                    LayoutColumn(key="pack_size", label="Pack"),
                    LayoutColumn(key="unit_price", label="Price", type="currency")
                ]
            )
        ]
    )

    # --- 16. 880 Grocery Invoice ---
    layouts["880"] = LayoutConfig(
        title_format="Grocery Inv #{ref_number}",
        theme_color="emerald",
        sections=[
             basic_header_section([
                LayoutField(key="invoice_number", label="Invoice #", style="bold"),
                LayoutField(key="po_number", label="PO #")
            ]),
             LayoutSection(id="grocery_inv_lines", title="Invoice Lines", type="table", data_source_key="line_items",
                columns=[
                    LayoutColumn(key="line_number", label="#"),
                    LayoutColumn(key="upc", label="UPC", style="bold"),
                    LayoutColumn(key="quantity", label="Qty"),
                    LayoutColumn(key="unit_price", label="Price", type="currency"),
                    LayoutColumn(key="extended_price", label="Total", type="currency")
                ]
            )
        ]
    )

    # --- 17. 997 Functional Ack (Legacy Migration) ---
    # 997 is mainly just header info and status, rarely has line items in simple view
    layouts["997"] = LayoutConfig(
        title_format="Func Ack #{ref_number}",
        theme_color="gray",
        sections=[
            LayoutSection(
                id="ack_info",
                title="Acknowledgment Details",
                fields=[
                    LayoutField(key="control_number", label="Group Control #", style="bold"),
                    LayoutField(key="status", label="Status", style="highlight"), # Accepted/Rejected
                    LayoutField(key="functional_group", label="Group ID"),
                    LayoutField(key="count", label="Trans Sets Included")
                ]
            ),
             LayoutSection(
                id="notes",
                title="Notes / Errors",
                type="table",
                data_source_key="line_items", # Usually error segments
                columns=[
                     LayoutColumn(key="error_code", label="Error Code"),
                     LayoutColumn(key="segment_id", label="Segment")
                ]
            )
        ]
    )

    # --- Execute Saves ---
    for type_code, config in layouts.items():
        print(f"Seeding layout for {type_code}...")
        try:
            LayoutService.create_initial_layout(type_code, config)
        except Exception as e:
            print(f"Error seeding {type_code}: {e}")

    print("Full Migration Seeding Complete!")

if __name__ == "__main__":
    seed_all_layouts()
