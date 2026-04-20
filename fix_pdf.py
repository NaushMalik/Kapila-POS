#!/usr/bin/env python3
"""
Fixed PDF Generator Update Script for Kapila Invoice
Run this to fix the PDF layout issues
"""

import re

# Read the current file
with open('c:/Users/malik/Downloads/KapilaInvoice/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The FIXED PDF generation function with proper spacing
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
    # Header background - full width blue header
    c.setFillColor(HEADER_COLOR)
    c.rect(0, height - 70, width, 70, fill=True, stroke=False)
    
    # Business name on header (white text) - left side
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    business_name = business_settings.get('business_name', 'Kapila Kathi Kebab')
    c.drawString(50, height - 45, business_name)
    
    # "INVOICE" text - right side
    c.setFont("Helvetica-Bold", 26)
    c.drawRightString(width - 50, height - 45, "INVOICE")
    
    # ========== BUSINESS INFO - Left Side ==========
    y_pos = height - 100
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica", 9)
    
    # Address info on left
    address = business_settings.get('address', '')
    phone = business_settings.get('phone', '')
    email = business_settings.get('email', '')
    gst_number = business_settings.get('gst_number', '')
    
    if address:
        c.drawString(50, y_pos, address)
    if phone:
        c.drawString(50, y_pos - 12, f"Phone: {phone}")
    if email:
        c.drawString(50, y_pos - 24, f"Email: {email}")
    if gst_number:
        c.drawString(50, y_pos - 36, f"GST No: {gst_number}")
    
    # ========== INVOICE DETAILS - Right Side Box ==========
    # Create a light box for invoice details on the right
    invoice_box_x = width - 200
    invoice_box_width = 150
    invoice_box_y = y_pos - 10
    invoice_box_height = 70
    
    c.setFillColor(LIGHT_GRAY)
    c.rect(invoice_box_x, invoice_box_y - invoice_box_height + 30, invoice_box_width, invoice_box_height - 30, fill=True, stroke=False)
    
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(invoice_box_x + 10, y_pos + 10, f"Invoice #:")
    c.drawString(invoice_box_x + 10, y_pos - 2, f"Date:")
    c.drawString(invoice_box_x + 10, y_pos - 14, f"Time:")
    c.drawString(invoice_box_x + 10, y_pos - 26, f"Payment:")
    
    c.setFont("Helvetica", 10)
    c.drawRightString(invoice_box_x + invoice_box_width - 10, y_pos + 10, invoice_data['invoice_number'][:15])
    c.drawRightString(invoice_box_x + invoice_box_width - 10, y_pos - 2, invoice_data['invoice_date'])
    c.drawRightString(invoice_box_x + invoice_box_width - 10, y_pos - 14, invoice_data['invoice_time'][:5])
    c.drawRightString(invoice_box_x + invoice_box_width - 10, y_pos - 26, invoice_data['payment_mode'])
    
    # ========== CUSTOMER INFO ==========
    y_pos = height - 200
    
    # Customer info box - full width
    c.setFillColor(LIGHT_GRAY)
    c.rect(50, y_pos - 50, width - 100, 55, fill=True, stroke=False)
    
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y_pos - 15, "Bill To:")
    
    c.setFont("Helvetica", 10)
    c.drawString(60, y_pos - 32, invoice_data['customer_name'][:50])
    
    # Customer contact info
    contact_y = y_pos - 50
    if invoice_data.get('customer_phone'):
        c.drawString(60, contact_y, f"Phone: {invoice_data['customer_phone']}")
    if invoice_data.get('customer_email'):
        c.drawString(250, contact_y, f"Email: {invoice_data['customer_email']}")
    
    # ========== ITEMS TABLE ==========
    y_pos = height - 290
    
    # Table header - full width
    c.setFillColor(HEADER_COLOR)
    c.rect(50, y_pos - 5, width - 100, 25, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    
    # Column positions with proper spacing
    c.drawString(55, y_pos + 8, "ITEM")
    c.drawCentredString(340, y_pos + 8, "QTY")
    c.drawCentredString(410, y_pos + 8, "RATE")
    c.drawRightString(width - 60, y_pos + 8, "AMOUNT")
    
    # Table rows
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica", 9)
    
    row_height = 20
    y_pos -= 20
    
    # Draw items
    for i, item in enumerate(items):
        # Alternate row colors
        if i % 2 == 1:
            c.setFillColor(LIGHT_GRAY)
            c.rect(50, y_pos - 3, width - 100, row_height, fill=True, stroke=False)
        
        c.setFillColor(TEXT_COLOR)
        
        # Item name - truncate if too long
        item_name = item['item_name']
        if len(item_name) > 40:
            item_name = item_name[:40] + "..."
        
        c.drawString(55, y_pos + 4, item_name)
        
        # Quantity - centered
        c.drawCentredString(340, y_pos + 4, str(item['quantity']))
        
        # Rate - centered
        c.drawCentredString(410, y_pos + 4, f"Rs.{float(item['unit_price']):.2f}")
        
        # Amount - right aligned
        c.drawRightString(width - 60, y_pos + 4, f"Rs.{float(item['amount']):.2f}")
        
        y_pos -= row_height
    
    # ========== TOTALS SECTION ==========
    y_pos -= 15
    
    # Divider line
    c.setStrokeColor(HEADER_COLOR)
    c.setLineWidth(1)
    c.line(50, y_pos, width - 50, y_pos)
    
    y_pos -= 25
    
    # Subtotal
    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT_COLOR)
    c.drawString(300, y_pos, "Subtotal:")
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 60, y_pos, f"Rs.{float(invoice_data['subtotal']):.2f}")
    
    y_pos -= 18
    
    # Tax info (if any)
    tax_amount = float(invoice_data.get('tax_amount', 0))
    tax_rate = float(invoice_data.get('tax_rate', 0))
    if tax_amount > 0:
        c.setFont("Helvetica", 11)
        c.drawString(300, y_pos, f"Tax ({tax_rate}%):")
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(width - 60, y_pos, f"Rs.{tax_amount:.2f}")
        y_pos -= 18
    
    # Grand Total - highlighted box
    c.setFillColor(HEADER_COLOR)
    c.rect(220, y_pos - 12, width - 270, 30, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(235, y_pos + 2, "TOTAL:")
    c.drawRightString(width - 60, y_pos + 2, f"Rs.{float(invoice_data['total']):.2f}")
    
    # ========== FOOTER ==========
    y_pos -= 50
    
    # Footer message
    footer_message = business_settings.get('footer_message', 'Thank you for your order!')
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(TEXT_COLOR)
    c.drawCentredString(width / 2, y_pos, footer_message)
    
    # Thank you message
    y_pos -= 22
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
    print('PDF function FIXED successfully!')
    print('')
    print('Changes made:')
    print('- Fixed overlapping address and invoice number')
    print('- Created separate boxes for business info and invoice details')
    print('- Fixed items table spacing')
    print('- Fixed totals section display')
    print('- Added proper row highlighting')
else:
    print('Could not find PDF function to replace')
