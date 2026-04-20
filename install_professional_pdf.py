#!/usr/bin/env python3
"""
Integration script to replace the PDF generator in app.py
with the professional reportlab.platypus version
"""

import re

# Read the current app.py
with open('c:/Users/malik/Downloads/KapilaInvoice/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The new professional PDF generation function
new_pdf_function = '''# ============= PDF Generation (Professional) =============
def generate_pdf(invoice_id, invoice_data, items, business_settings):
    """
    Generate professional A4 PDF invoice using reportlab.platypus
    Exact layout as specified by user
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    import os
    from datetime import datetime
    
    pdf_filename = f"invoice_{invoice_data['invoice_number']}.pdf"
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
    
    # Create document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    # Container for elements
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Title styles
    title_blue = ParagraphStyle('TitleBlue', parent=styles['Heading1'], fontSize=28,
        textColor=colors.HexColor('#1E3FA8'), alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=2)
    title_mustard = ParagraphStyle('TitleMustard', parent=styles['Heading1'], fontSize=28,
        textColor=colors.HexColor('#E1B12C'), alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=20)
    
    # Address style
    address_style = ParagraphStyle('Address', parent=styles['Normal'], fontSize=9,
        textColor=colors.black, alignment=TA_LEFT, spaceAfter=3)
    
    # Meta style
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=10,
        textColor=colors.black, alignment=TA_RIGHT, spaceAfter=3)
    
    # BILL TO styles
    bill_heading = ParagraphStyle('BillHeading', parent=styles['Normal'], fontSize=10,
        textColor=colors.black, fontName='Helvetica-Bold', spaceAfter=5)
    bill_content = ParagraphStyle('BillContent', parent=styles['Normal'], fontSize=10,
        textColor=colors.black, spaceAfter=3)
    
    # Table styles
    table_header = ParagraphStyle('TblHeader', parent=styles['Normal'], fontSize=10,
        textColor=colors.black, fontName='Helvetica-Bold', alignment=TA_CENTER)
    item_cell = ParagraphStyle('ItemCell', parent=styles['Normal'], fontSize=10,
        textColor=colors.black, alignment=TA_LEFT)
    item_cell_center = ParagraphStyle('ItemCellC', parent=styles['Normal'], fontSize=10,
        textColor=colors.black, alignment=TA_CENTER)
    item_cell_right = ParagraphStyle('ItemCellR', parent=styles['Normal'], fontSize=10,
        textColor=colors.black, alignment=TA_RIGHT)
    
    # Subtotal style
    subtotal_style = ParagraphStyle('Subtotal', parent=styles['Normal'], fontSize=11,
        textColor=colors.black, fontName='Helvetica-Bold', alignment=TA_RIGHT, spaceAfter=3)
    
    # Payment style
    payment_style = ParagraphStyle('Payment', parent=styles['Normal'], fontSize=10,
        textColor=colors.black, spaceAfter=8)
    
    # Payment received style
    payment_received = ParagraphStyle('PaymentRec', parent=styles['Normal'], fontSize=14,
        textColor=colors.HexColor('#1E8F4F'), fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=15)
    
    # Terms style
    terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=9,
        textColor=colors.gray, alignment=TA_CENTER, spaceAfter=3)
    
    # Footer style
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
        textColor=colors.gray, alignment=TA_CENTER)
    
    # 1. Title
    elements.append(Paragraph("KAPILA", title_blue))
    elements.append(Paragraph("KATHI KEBAB", title_mustard))
    elements.append(Spacer(1, 15))
    
    # 2. Address
    elements.append(Paragraph("173, Dhole Patil Road, Shop No. 4", address_style))
    elements.append(Paragraph("Nalini Chambers, Pune - 411001", address_style))
    elements.append(Paragraph("Mobile: 70382 04449", address_style))
    elements.append(Paragraph("Landline: 020-41280262", address_style))
    elements.append(Spacer(1, 15))
    
    # 3. Invoice meta
    invoice_no = invoice_data.get('invoice_number', 'N/A')
    invoice_date = invoice_data.get('invoice_date', datetime.now().strftime('%d/%m/%Y'))
    elements.append(Paragraph(f"Invoice No: {invoice_no}", meta_style))
    elements.append(Paragraph(f"Date: {invoice_date}", meta_style))
    elements.append(Spacer(1, 20))
    
    # 4. BILL TO
    elements.append(Paragraph("BILL TO", bill_heading))
    elements.append(Paragraph(invoice_data.get('customer_name', 'N/A'), bill_content))
    if invoice_data.get('customer_gst'):
        elements.append(Paragraph(f"GST No: {invoice_data['customer_gst']}", bill_content))
    if invoice_data.get('customer_address'):
        elements.append(Paragraph(invoice_data['customer_address'], bill_content))
    if invoice_data.get('customer_phone'):
        elements.append(Paragraph(f"Contact: {invoice_data['customer_phone']}", bill_content))
    elements.append(Spacer(1, 15))
    
    # 5. Item table
    table_data = []
    header_row = [
        Paragraph("Item", table_header),
        Paragraph("Qty", table_header),
        Paragraph("Rate", table_header),
        Paragraph("Amount", table_header)
    ]
    table_data.append(header_row)
    
    for item in items:
        row = [
            Paragraph(item.get('item_name', ''), item_cell),
            Paragraph(str(item.get('quantity', 0)), item_cell_center),
            Paragraph(f"{float(item.get('unit_price', 0)):,.2f}", item_cell_center),
            Paragraph(f"{float(item.get('amount', 0)):,.2f}", item_cell_right)
        ]
        table_data.append(row)
    
    col_widths = [280, 60, 90, 90]
    item_table = Table(table_data, colWidths=col_widths, hAlign=TA_LEFT)
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 15))
    
    # 6. Subtotal
    subtotal = f"{float(invoice_data.get('subtotal', 0)):,.2f}"
    elements.append(Paragraph(f"Subtotal: INR {subtotal}", subtotal_style))
    elements.append(Spacer(1, 10))
    
    # 7. Payment Mode
    payment_mode = invoice_data.get('payment_mode', 'Cash')
    elements.append(Paragraph(f"Payment Mode: {payment_mode}", payment_style))
    elements.append(Spacer(1, 5))
    
    # 8. FULL PAYMENT RECEIVED
    elements.append(Paragraph("FULL PAYMENT RECEIVED", payment_received))
    elements.append(Spacer(1, 20))
    
    # 9. Terms
    elements.append(Paragraph("All food items are freshly prepared.", terms_style))
    elements.append(Paragraph("Payment is requested at the time of delivery.", terms_style))
    elements.append(Spacer(1, 25))
    
    # 10. Footer
    elements.append(Paragraph("This is a system-generated invoice.", footer_style))
    
    doc.build(elements)
    return pdf_path
'''

# Find and replace the old PDF function
old_pdf_pattern = r'# ============= PDF Generation =============.*?(?=# ============= Email Functions)'
old_match = re.search(old_pdf_pattern, content, re.DOTALL)

if old_match:
    content = content[:old_match.start()] + new_pdf_function + content[old_match.end():]
    with open('c:/Users/malik/Downloads/KapilaInvoice/app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Professional PDF generator installed successfully!')
    print('')
    print('Features:')
    print('- reportlab.platypus (SimpleDocTemplate)')
    print('- Blue KAPILA title (#1E3FA8)')
    print('- Mustard KATHI KEBAB title (#E1B12C)')
    print('- Address block with proper spacing')
    print('- BILL TO section')
    print('- Clean table with single line under header')
    print('- INR currency formatting')
    print('- FULL PAYMENT RECEIVED')
    print('- Terms & Conditions in grey')
    print('- Centered footer')
else:
    print('Could not find PDF function to replace')
