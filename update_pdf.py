#!/usr/bin/env python3
"""
PDF Generator Update Script for Kapila Invoice
Run this script to update the PDF generation function in app.py
"""

import re

# Read the current file
with open('c:/Users/malik/Downloads/KapilaInvoice/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The new PDF generation function
new_pdf_function = '''# ============= PDF Generation =============
def generate_pdf(invoice_id, invoice_data, items, business_settings):
    """Generate PDF invoice with proper formatting"""
    pdf_filename = f"invoice_{invoice_data['invoice_number']}.pdf"
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
    
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Colors
    HEADER_COLOR = colors.HexColor('#1e3fa8')
    TEXT_COLOR = colors.HexColor('#2b2b2b')
    LIGHT_GRAY = colors.HexColor('#f2f2f2')
    
    # ========== HEADER SECTION ==========
    # Header background
    c.setFillColor(HEADER_COLOR)
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    
    # Business name on header (white text)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    business_name = business_settings.get('business_name', 'Kapila Kathi Kebab')
    c.drawString(50, height - 50, business_name)
    
    # "INVOICE" text
    c.setFont("Helvetica-Bold", 28)
    c.drawRightString(width - 50, height - 50, "INVOICE")
    
    # ========== BUSINESS INFO ==========
    y_pos = height - 100
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica", 10)
    
    address = business_settings.get('address', '')
    phone = business_settings.get('phone', '')
    email = business_settings.get('email', '')
    gst_number = business_settings.get('gst_number', '')
    
    if address:
        c.drawString(50, y_pos, address)
    if phone:
        c.drawString(50, y_pos - 15, f"Phone: {phone}")
    if email:
        c.drawString(50, y_pos - 30, f"Email: {email}")
    if gst_number:
        c.drawString(50, y_pos - 45, f"GST No: {gst_number}")
    
    # ========== INVOICE DETAILS (Right side) ==========
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 50, y_pos, f"Invoice #: {invoice_data['invoice_number']}")
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 50, y_pos - 18, f"Date: {invoice_data['invoice_date']}")
    c.drawRightString(width - 50, y_pos - 36, f"Time: {invoice_data['invoice_time']}")
    c.drawRightString(width - 50, y_pos - 54, f"Payment: {invoice_data['payment_mode']}")
    
    # ========== CUSTOMER INFO ==========
    y_pos = height - 180
    
    # Customer info box
    c.setFillColor(LIGHT_GRAY)
    c.rect(50, y_pos - 60, width - 100, 65, fill=True, stroke=False)
    
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y_pos - 20, "Bill To:")
    
    c.setFont("Helvetica", 11)
    c.drawString(60, y_pos - 38, invoice_data['customer_name'])
    
    if invoice_data.get('customer_phone'):
        c.drawString(60, y_pos - 55, f"Phone: {invoice_data['customer_phone']}")
    
    if invoice_data.get('customer_email'):
        c.drawString(300, y_pos - 55, f"Email: {invoice_data['customer_email']}")
    
    # ========== ITEMS TABLE ==========
    y_pos = height - 270
    
    # Table header
    c.setFillColor(HEADER_COLOR)
    c.rect(50, y_pos - 5, width - 100, 25, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    
    # Column positions
    col_item = 60
    col_qty = 320
    col_rate = 380
    col_amount = 470
    
    c.drawString(col_item, y_pos + 8, "ITEM")
    c.drawCentredString(col_qty, y_pos + 8, "QTY")
    c.drawCentredString(col_rate, y_pos + 8, "RATE")
    c.drawRightString(col_amount + 10, y_pos + 8, "AMOUNT")
    
    # Table rows
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica", 10)
    
    row_height = 22
    y_pos -= 25
    
    for i, item in enumerate(items):
        if i % 2 == 1:
            c.setFillColor(LIGHT_GRAY)
            c.rect(50, y_pos - 3, width - 100, row_height, fill=True, stroke=False)
        
        c.setFillColor(TEXT_COLOR)
        
        # Item name (truncate if too long)
        item_name = item['item_name']
        if len(item_name) > 35:
            item_name = item_name[:35] + "..."
        c.drawString(col_item, y_pos + 6, item_name)
        
        # Quantity
        c.drawCentredString(col_qty, y_pos + 6, str(item['quantity']))
        
        # Rate
        c.drawCentredString(col_rate, y_pos + 6, f"Rs.{item['unit_price']:.2f}")
        
        # Amount (right aligned)
        c.drawRightString(col_amount + 10, y_pos + 6, f"Rs.{item['amount']:.2f}")
        
        y_pos -= row_height
    
    # ========== TOTALS SECTION ==========
    y_pos -= 20
    
    # Draw line before totals
    c.setStrokeColor(HEADER_COLOR)
    c.setLineWidth(1)
    c.line(50, y_pos, width - 50, y_pos)
    
    y_pos -= 25
    
    # Subtotal
    c.setFont("Helvetica", 11)
    c.drawString(350, y_pos, "Subtotal:")
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 60, y_pos, f"Rs.{invoice_data['subtotal']:.2f}")
    
    y_pos -= 20
    
    # Tax info (if any)
    if invoice_data.get('tax_amount', 0) > 0:
        c.setFont("Helvetica", 11)
        c.drawString(350, y_pos, f"Tax ({invoice_data.get('tax_rate', 0)}%):")
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(width - 60, y_pos, f"Rs.{invoice_data['tax_amount']:.2f}")
        y_pos -= 20
    
    # Grand Total
    c.setFillColor(HEADER_COLOR)
    c.rect(250, y_pos - 8, width - 300, 30, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(270, y_pos + 6, "TOTAL:")
    c.drawRightString(width - 60, y_pos + 6, f"Rs.{invoice_data['total']:.2f}")
    
    # ========== FOOTER ==========
    y_pos -= 60
    
    # Footer message
    footer_message = business_settings.get('footer_message', 'Thank you for your order!')
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(TEXT_COLOR)
    c.drawCentredString(width / 2, y_pos, footer_message)
    
    # Thank you message
    y_pos -= 25
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2, y_pos, "We look forward to serving you again!")
    
    # ========== SAVE PDF ==========
    c.save()
    return pdf_path
'''

# Find and replace the PDF generation function
old_pdf_pattern = r'# ============= PDF Generation =============.*?(?=# ============= Email Functions)'
old_pdf_match = re.search(old_pdf_pattern, content, re.DOTALL)

if old_pdf_match:
    content = content[:old_pdf_match.start()] + new_pdf_function + content[old_pdf_match.end():]
    with open('c:/Users/malik/Downloads/KapilaInvoice/app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('PDF function updated successfully!')
else:
    print('Could not find PDF function to replace')
    print('Trying alternative method...')
    
    # Alternative: Find by function name and replace
    alt_pattern = r'(def generate_pdf\(invoice_id, invoice_data, items, business_settings\):.*?(?=\n# =============|\n@app\.route|\nif __name__)'
    alt_match = re.search(alt_pattern, content, re.DOTALL)
    
    if alt_match:
        print('Found function with alternative pattern')
        # This is complex, so just print instructions
        print('Manual update required. Please replace the generate_pdf function in app.py')
