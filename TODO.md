# Table & Invoice Fix Progress
Kapila POS Table System Fix - Approved Plan Implementation

## Steps (0/6 Complete)

- [x] **Step 1: Update DB Schema** ✅ (tables 1-12 + products sample)

- [x] **Step 2: Add Backend Routes** ✅ (add_order, mark_paid w/ invoice, receipt, detail/JSON APIs)

- [ ] **Step 2: Add Backend Routes** - Implement /tables/<id> (JSON+page), /add_order, /mark_paid, /receipt, /select. Update app.py. Add imports (jsonify, request.json, datetime).

- [ [ ] **Step 3: Fix Frontend JS/CSS** - templates/tables.html (onclick, openTable), table_detail.html (products), dashboard.html (JS). Ensure horizontal layouts.

- [ ] **Step 4: Invoice Integration** - On mark_paid create invoice + items from table_orders, link to PDF.

- [ ] **Step 5: Fix new_invoice Save** - Parse items, save invoice_items.

- [ ] **Step 6: Test & Demo** - Run app, login, tables -> add -> bill -> invoice. Check horizontal responsive.

## Testing Commands
```bash
python app.py
# Login: admin/admin123
# Go /tables, click table, add product, bill
```

**Progress Notes:**

Updated on: $(date)
