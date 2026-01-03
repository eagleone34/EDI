import os
import sys
from dotenv import load_dotenv

# Setup path and env
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from seed_config import set_db_env
    set_db_env()
    print("Loaded DB config from seed_config.py")
except ImportError:
    print("seed_config.py not found, attempting .env load...")
    # Fallback logic if needed, or just let it fail later
    pass

# Try loading from local.env or temp_db_config.ini
env_path = os.path.join(os.getcwd(), 'local.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

from app.services.layout_service import LayoutService
from app.schemas.layout import LayoutConfig, LayoutSection, LayoutField, LayoutColumn

def seed_layouts():
    print("Seeding initial layouts...")
    
    # --- 812 Credit/Debit Adjustment ---
    config_812 = LayoutConfig(
        title_format="{name} #{ref_number}",
        theme_color="blue",
        sections=[
            LayoutSection(
                id="order_info",
                title="Order Information",
                fields=[
                    LayoutField(key="credit_debit_number", label="Credit/Debit #", style="bold"),
                    LayoutField(key="date", label="Date", type="date"),
                    LayoutField(key="purchase_order_number", label="Original PO #Reference"),
                    LayoutField(key="transaction_handling_code", label="Handling Code"),
                    LayoutField(key="currency_code", label="Currency"),
                    LayoutField(key="amount", label="Total Amount", type="currency", style="highlight")
                ]
            ),
            LayoutSection(
                id="parties",
                title="Parties & Addresses",
                type="grid" # Handled specially by renderer
            ),
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
                    LayoutColumn(key="unit_price", label="Unit Price", width="100px", type="currency"),
                    LayoutColumn(key="adjustment_amount", label="Amount", width="100px", type="currency")
                ]
            )
        ]
    )
    
    # --- 850 Purchase Order ---
    config_850 = LayoutConfig(
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
                    LayoutField(key="type_code", label="Type"),
                    LayoutField(key="currency_code", label="Currency")
                ]
            ),
             LayoutSection(
                id="parties",
                title="Parties & Addresses",
                type="grid"
            ),
            LayoutSection(
                id="dates",
                title="Critical Dates",
                type="grid"
            ),
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
                    LayoutColumn(key="unit_price", label="Unit Price", width="100px", type="currency"),
                    LayoutColumn(key="total", label="Total", width="100px", type="currency")
                ]
            )
        ]
    )
    
    # Save to DB
    print("Saving 812 configuration...")
    LayoutService.create_initial_layout("812", config_812)
    
    print("Saving 850 configuration...")
    LayoutService.create_initial_layout("850", config_850)
    
    print("Seeding complete!")

if __name__ == "__main__":
    seed_layouts()
