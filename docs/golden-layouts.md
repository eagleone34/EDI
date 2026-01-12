# Golden Layouts Reference

> **CRITICAL**: This document defines the authoritative layout structure for each EDI transaction type.
> All parsers and layout configs MUST match these specifications exactly.
> Reference: EDI Notepad samples at `samples/EDInotepad samples/`

---

## 810 - Invoice

**Document Title:** Invoice

### Section: General Information

#### Beginning Segment for Invoice
| Field | Description |
|-------|-------------|
| Date | Invoice date |
| Invoice Number | Primary invoice reference |
| Purchase Order Number | Associated PO |

#### Reference Information
| Field | Description |
|-------|-------------|
| Internal Vendor Number | Vendor's unique identifier |

#### Address Blocks
| Block | Fields |
|-------|--------|
| Remit To | Full name and address for payment |
| Ship To | Destination name and address |

#### Terms of Sale/Deferred Terms of Sale
| Field | Description |
|-------|-------------|
| Terms Type Code | e.g., Basic |
| Terms Discount Percent | Percentage off for early payment |
| Terms Discount Due Date | Date discount expires |
| Terms Discount Days Due | Number of days for discount |
| Terms Net Due Date | Final payment deadline |
| Terms Net Days | Net terms period |
| Terms Discount Amount | Calculated discount value |
| Description | Text summary (e.g., "Up to 05/08/2025 you receive 2.000% discount") |

#### Date/Time Reference
| Field | Description |
|-------|-------------|
| Shipped | Shipping date |

### Section: Line Item Information (Table)
| Column | Description |
|--------|-------------|
| Line | Line item number |
| Description | Product description + UCC-12 |
| Quan | Quantity |
| UI | Unit of measure |
| Price($) | Unit price |
| Total($) | Line total |

### Section: Summary
| Field | Description |
|-------|-------------|
| Total | Final invoice amount |
| Discount based on | Amount eligible for discount |
| Line Count | Total line items |

---

## 812 - Credit/Debit Adjustment

**Document Title:** Credit/Debit Adjustment

> Source: User screenshots from EDI Notepad

### Section: General Information

#### Beginning Credit/Debit Adjustment
| Field | Parser Key | Description |
|-------|-----------|-------------|
| Date | `adjustment_date` | Transaction date (BCD01) |
| Credit/Debit Adjustment Number | `credit_debit_number` | Memo number (BCD02) |
| Transaction Handling Code | `transaction_handling_desc` | Handling code with description (BCD03) |
| Amount | `amount` | Total amount in cents → dollars (BCD04) |
| Credit/Debit Flag Code | `credit_debit_flag_desc` | Credit or Debit (BCD05) |
| Date (Invoice) | `secondary_date` | Invoice date (BCD06) |
| Invoice Number | `invoice_number` | Invoice reference (BCD07) |
| Date | `tertiary_date` | Additional date (BCD08) |
| Purchase Order Number | `po_number` | PO reference (BCD09) |
| Transaction Set Purpose Code | `purpose` | Original/Replacement (BCD10) |
| Transaction Type Code | `transaction_type_desc` | Debit Memo/Credit Memo (BCD11) |

### Section: Currency
| Field | Parser Key |
|-------|-----------|
| Currency | `currency` |

### Section: Contact Information
| Field | Parser Key |
|-------|-----------|
| Customer Relations | `contact_name` |
| Telephone | `comm_number` |

### Section: Parties (Two-Column Layout)
| Original Claimant | Supplier/Manufacturer |
|-------------------|----------------------|
| Name + GLN/DUNS | Name + GLN/DUNS |

### Section: Credit/Debit Adjustment Detail (Per Line Item)
| Field | Parser Key | Description |
|-------|-----------|-------------|
| Adjustment Reason Code | `adjustment_reason` | Reason + description |
| Credit/Debit Flag Code | `credit_debit_type` | Credit or Debit |
| Assigned Identification | `assigned_id` | Reference ID |
| Amount | `adjustment_amount` | Line amount |
| Credit/Debit Quantity | `quantity` | Quantity |
| Unit or Basis for Measurement Code | `unit` | Unit of measure |
| Price Identifier Code | `price_id_code` | Price type |
| Unit Price | `unit_price` | Price per unit |
| Price Identifier Code (2nd) | `price_id_code_2` | Original price type |
| Unit Price (2nd) | `original_unit_price` | Original price |
| Free-form Message Text | `message` | Additional notes |

### Section: Part Numbers (Per Line Item - Table)
| Field | Description |
|-------|-------------|
| Buyer's Item Number | LIN segment |
| U.P.C. Consumer Package Code (1-5-5) | UPC |
| Purchaser's Item Code | Buyer's code |

---

## 830 - Planning Schedule with Release Capability

**Document Title:** Planning Schedule with Release Capability

### Section: General Information

#### Document Information
| Field | Description |
|-------|-------------|
| Transaction Purpose Code | e.g., Original |
| Schedule Horizon Start Date | Start of planning horizon |
| Schedule Horizon End Date | End of planning horizon |
| Issue Date | Document generation date |
| Reference Number | Primary reference ID |
| Forecast Type | e.g., Customer Production (Consumption) Based |
| Schedule Quantity | e.g., Actual Discrete Quantities |

#### Reference Information
| Field | Description |
|-------|-------------|
| Internal Vendor Number | Supplier's internal ID |

#### Reporting Location
| Field | Description |
|-------|-------------|
| Entity Name | e.g., FRED MEYER, INC. |
| Identifier | D-U-N-S+4 number |

### Section: Line Information (Repeating)

#### Part Numbers
| Field | Description |
|-------|-------------|
| UCC - 12 | UPC/GTIN |
| Purchaser's Item Code | Buyer's internal part number |

#### Unit Detail
| Field | Description |
|-------|-------------|
| Composite Unit of Measure | e.g., Each |
| Unit Price | Price value |
| Basis of Unit Price Code | e.g., Retail Price per Each |

### Section: Forecast Schedule (Table per Line Item)
| Column | Description |
|--------|-------------|
| Quan | Forecasted quantity |
| Timing | Planning interval description |
| When (Start) | Start date |
| When (End) | End date |

### Section: Summary
| Field | Description |
|-------|-------------|
| Line Count | Total line items (e.g., 34) |

---

## 850 - Purchase Order

**Document Title:** Purchase Order

### Section: General Information

#### Document Information
| Field | Description |
|-------|-------------|
| Purchase Order Number | Primary PO reference |
| Transaction Purpose Code | e.g., Original |
| Purchase Order Date | Date of PO |
| Purchase Order Type Code | e.g., Stand-alone Order |

#### Reference Information
| Field | Description |
|-------|-------------|
| Internal Vendor Number | Vendor ID |

#### Contact Information
| Field | Description |
|-------|-------------|
| Buyer Name or Department | Contact name |
| Telephone | Phone number |

#### F.O.B. Related Instructions
| Field | Description |
|-------|-------------|
| Shipment Method of Payment | Who pays shipping |
| Location Qualifier | e.g., Origin (Shipping Point) |
| Description | Location name |

#### Sales Requirements
| Field | Description |
|-------|-------------|
| Sales Requirement Code | Sales conditions |

#### Terms of Sale
| Field | Description |
|-------|-------------|
| Terms Type Code | e.g., Basic |
| Description | e.g., 0200015NET 016 |

#### Date/Time Reference
| Field | Description |
|-------|-------------|
| Requested Ship | Requested ship date |
| Delivery Requested | Requested delivery date |

#### Carrier Details
| Field | Description |
|-------|-------------|
| Commodity Code Qualifier | Code type |
| Commodity Code | Code value |
| Transportation Method/Type Code | Shipping method |
| Routing | Routing instructions |

#### Parties/Addresses
| Party | Fields |
|-------|--------|
| Vendor | Name, D-U-N-S+4, full address |
| Bill-to-Party | Name, Assigned Id, full address |
| Ship To | Name, Assigned Id, full address |

### Section: Line Item Information (Table)
| Column | Description |
|--------|-------------|
| Line | Sequential line number |
| Description | UCC-12, Purchaser's Item Code, Vendor's Style, SKU, Internal Number |
| Quan | Quantity ordered |
| UI | Unit of measure |
| Price($) | Unit price |
| Price Basis | Price description |
| Total($) | Line total |

### Section: Summary
| Field | Description |
|-------|-------------|
| Line Count | Total line items |

---

## 870 - Order Status Report

**Document Title:** Order Status Report

### Section: General Information

#### Beginning Segment for Order Status Report
| Field | Description |
|-------|-------------|
| Status Report Code | e.g., Unsolicited Report |
| Order/Item Code | e.g., Selected Orders - All Items |
| Reference Identification | Reference ID |
| Date | Report date |

#### Reference Identification
| Field | Description |
|-------|-------------|
| Internal Vendor Number | Vendor ID |

### Section: Order Level Information

#### Purchase Order Reference
| Field | Description |
|-------|-------------|
| Purchase Order Number | PO reference |
| Date | PO date |

#### Item Status Report
| Field | Description |
|-------|-------------|
| Shipment/Order Status Code | e.g., Deleted Order |

#### Reference Identification
| Field | Description |
|-------|-------------|
| Department Number | Dept ID |

#### Mark-for Party
| Field | Description |
|-------|-------------|
| Assigned by Buyer or Buyer's Agent | Party ID |

### Section: Summary
| Field | Description |
|-------|-------------|
| Line Count | Total items |

---

## 875 - Grocery Products Purchase Order

**Document Title:** Grocery Products Purchase Order

### Section: General Information

(Container section for sub-sections below)

### Section: Purchase Order Identification
| Field | Description |
|-------|-------------|
| Order Status Code | e.g., Original |
| Date | Order date |
| Purchase Order Number | PO reference |

### Section: Date/Time
| Field | Description |
|-------|-------------|
| Date Qualifier | e.g., Delivery Requested on This Date |
| Date | Requested date |

### Section: Transportation Instructions
| Field | Description |
|-------|-------------|
| Shipment Method of Payment | e.g., Prepaid (by Seller) |
| Transportation Method/Type Code | e.g., Motor (Common Carrier) |
| Unit Load Option Code | e.g., Palletized |

### Section: Terms of Sale
| Field | Description |
|-------|-------------|
| Terms Type Code | e.g., Basic |
| Terms Basis Date Code | e.g., Invoice Date |
| Terms Discount Percent | Discount percentage |
| Terms Discount Days Due | Days for discount |
| Terms Net Days | Net terms |
| Free Form Message | e.g., "1% 30 NET 31" |

### Section: Parties (Dual Column Layout)
| Vendor (Left) | Bill-to-Party (Right) |
|---------------|----------------------|
| Name + D-U-N-S+4 | Name + D-U-N-S+4, Address |

### Section: Ship To
| Field | Description |
|-------|-------------|
| Name | Including D-U-N-S+4 |
| Address | Street address |
| Location | City, State, ZIP |

### Section: Line Item Detail (Vertical List - Repeating)
| Field | Description |
|-------|-------------|
| Quantity Ordered | Quantity |
| Unit or Basis for Measurement Code | e.g., Case |
| Item List Cost | Price |
| Product/Service ID Qualifier | e.g., UPC Shipping Container Code |
| Product/Service ID | ID value |
| Purchaser's Item Code | Buyer's code |
| Free-form Description | Product description |

### Section: Total Purchase Order (Summary)
| Field | Description |
|-------|-------------|
| Quantity Ordered | Total quantity |
| Unit or Basis for Measurement Code | Unit |
| Weight | Total weight |
| Weight Unit | e.g., Pound |
| Amount | Total dollar amount |

---

## Notes

1. **812 PDF Sample Issue**: The `812 edinotepad sample.pdf` file is incorrectly a duplicate of the 850 Purchase Order. The 812 layout above is based on user-provided screenshots from EDI Notepad.

2. **Table vs Vertical Lists**: Some transaction types (870, 875) use vertical key-value pairs instead of horizontal tables for line items.

3. **Dual-Column Layouts**: 812 and 875 use side-by-side party layouts (Original Claimant | Supplier/Manufacturer).

4. **Parser Alignment**: Each parser MUST extract all fields listed here with the exact key names specified.
