---
description: Rules for protecting the core layout system - the foundation of ReadableEDI
---

# Layout Protection Rules

> **CRITICAL**: The layout system is the CORE VALUE of ReadableEDI. 
> If layouts don't match the quality of EDI Notepad, the application is useless.

## The Golden Rule

Every conversion output must:
1. Display **all relevant fields** for that transaction type
2. **Never show irrelevant fields** or "—" for fields that don't apply
3. Match or **exceed the quality** of EDI Notepad output

## Before ANY Layout-Related Change

### 1. Verify Parser-Layout Alignment
```
Parser output field names MUST EXACTLY match layout config keys.
Example: If parser stores `adjustment_date`, layout must use `adjustment_date` (not `date`)
```

### 2. Test with Real Files
- Use actual production EDI files
- Test ALL formats: HTML, PDF, and Excel
- Compare output to EDI Notepad

### 3. Check These Files Before Modifying

| File | Risk | What to Check |
|------|------|---------------|
| `parsers/edi_*.py` | HIGH | All EDI fields extracted correctly |
| `generators/dynamic_generator.py` | HIGH | Title format, section rendering |
| `main.py` - seed_layouts() | HIGH | Layout config correctness |
| `services/edi_segments.py` | MEDIUM | Segment-to-key mappings |
| `update_all_layouts.py` | HIGH | Master layout configs |

## Layout Config Requirements

Every layout configuration MUST have:

1. **title_format** using a transaction-specific identifier field
2. **Sections** that match EDI Notepad organization
3. **Field keys** that EXACTLY match parser output (case-sensitive!)
4. **Appropriate types**: text, date, currency, number
5. **No placeholder sections** - only show what applies to this transaction

## Parser Requirements

Every parser MUST:

1. Extract ALL fields shown by EDI Notepad for that transaction type
2. Use **consistent, documented field names**
3. Store data in **predictable locations** (header, line_items, parties)
4. Include **code lookups** for better readability (e.g., flag code → "Debit")

## Testing Checklist

Before committing any layout-related change:

- [ ] Load a real EDI file of this transaction type
- [ ] Convert to HTML - verify all fields populated
- [ ] Convert to PDF - verify formatting correct
- [ ] Convert to Excel - verify data exports correctly
- [ ] Compare to EDI Notepad - output should be equal or better
- [ ] No console errors during conversion
- [ ] No "—" for fields that should have data

## Recovery Process

If a layout breaks in production:

1. Immediately check the seed_layouts() function in main.py
2. Verify parser field names match layout config keys
3. Check recent changes to the protected files above
4. Test with the original EDI file that triggered the issue
