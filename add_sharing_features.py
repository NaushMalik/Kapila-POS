#!/usr/bin/env python3
"""Add email and WhatsApp features to Kapila Invoice"""

import re

# Read app.py
with open("c:/Users/malik/Downloads/KapilaInvoice/app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Email function
new_email = '''
def send_thank_you_email(invoice_data, items, pdf_path, business_settings):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    
    settings = get_business_settings()
    smtp_host = settings.get("email_smtp_host")
    email_user = settings.get("email_username")
    email_password = settings.get("email_password")
    
    recipient = invoice_data.get("customer_email")
    if not recipient:
        return False, "No email address"
    
    if not all([smtp_host, email_user, email_password]):
        return False, "Email not configured"
    
    try:
        msg = MIMEMultipart()
        msg["From"] = email_user
        msg["To"] = recipient
        msg["Subject"] = f"Thank you from {business_settings.get('business_name', 'Kapila Kathi Kebab')}!"
        
        body = f"""Dear {invoice_data.get('customer_name', 'Customer')},

Thank you for your order!

Invoice: {invoice_data.get('invoice_number', 'N/A')}
Date: {invoice_data.get('invoice_date', 'N/A')}
Amount: INR {float(invoice_data.get('total', 0)):,.2f}

We look forward to serving you again!

{business_settings.get('business_name', 'Kapila Kathi Kebab')}
{business_settings.get('address', '')}
Phone: {settings.get('phone', '')}"""
        
        msg.attach(MIMEText(body, "plain"))
        
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(pdf_path)}")
                msg.attach(part)
        
        server = smtplib.SMTP(smtp_host, 587)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, recipient, msg.as_string())
        server.quit()
        return True, "Email sent"
    except Exception as e:
        return False, str(e)
'''

# Routes to add
new_routes = '''
@app.route("/invoice/email/<int:invoice_id>")
@login_required
def email_invoice(invoice_id):
    invoice = query_db("SELECT * FROM invoices WHERE id = ?", (invoice_id,), one=True)
    if not invoice:
        flash("Invoice not found", "danger")
        return redirect(url_for("dashboard"))
    
    items = query_db("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    items = [dict(item) for item in items]
    invoice = dict(invoice)
    settings = get_business_settings()
    
    if not invoice.get("pdf_path") or not os.path.exists(invoice["pdf_path"]):
        invoice_data = {
            "invoice_number": invoice["invoice_number"],
            "customer_name": invoice["customer_name"],
            "customer_phone": invoice["customer_phone"],
            "customer_email": invoice["customer_email"],
            "subtotal": invoice["subtotal"],
            "total": invoice["total"],
            "invoice_date": invoice["invoice_date"]
        }
        pdf_path = generate_pdf(invoice_id, invoice_data, items, settings)
        execute_db("UPDATE invoices SET pdf_path = ? WHERE id = ?", (pdf_path, invoice_id))
    else:
        pdf_path = invoice["pdf_path"]
    
    success, message = send_thank_you_email(invoice, items, pdf_path, settings)
    if success:
        flash(f"Thank you email sent to {invoice.get('customer_email', 'customer')}!", "success")
    else:
        flash(f"Failed to send email: {message}", "danger")
    
    return redirect(url_for("view_invoice", invoice_id=invoice_id))

@app.route("/invoice/whatsapp/<int:invoice_id>")
@login_required
def whatsapp_invoice(invoice_id):
    invoice = query_db("SELECT * FROM invoices WHERE id = ?", (invoice_id,), one=True)
    if not invoice:
        flash("Invoice not found", "danger")
        return redirect(url_for("dashboard"))
    
    invoice = dict(invoice)
    settings = get_business_settings()
    business_name = settings.get("business_name", "Kapila Kathi Kebab")
    
    message = f"""{business_name}

Thank you for your order!

Invoice: {invoice.get('invoice_number', 'N/A')}
Date: {invoice.get('invoice_date', 'N/A')}
Amount: INR {float(invoice.get('total', 0)):,.2f}

{settings.get('footer_message', 'Thank you!')}"""
    
    encoded = message.replace("\\n", "%0A").replace(" ", "%20")
    phone = invoice.get("customer_phone", "").replace(" ", "").replace("-", "")
    
    if phone and len(phone) >= 10:
        if not phone.startswith("+"):
            phone = "+91" + phone[-10:]
        return redirect(f"https://wa.me/{phone.replace('+', '')}?text={encoded}")
    else:
        flash("No valid phone number", "warning")
        return redirect(url_for("view_invoice", invoice_id=invoice_id))
'''

# Add email function after PDF function
pdf_pattern = r'(c\.save\(\)|return pdf_path)'
pdf_match = re.search(pdf_pattern, content)

if pdf_match:
    insert_pos = pdf_match.end()
    content = content[:insert_pos] + "\n" + new_email + "\n" + content[insert_pos:]
    print("Email function added!")
else:
    print("Could not find PDF function end")

# Add routes
route_pattern = r'(# ============= Error Handlers =============)'
route_match = re.search(route_pattern, content)

if route_match:
    content = content[:route_match.start()] + new_routes + content[route_match.start():]
    print("Routes added!")
else:
    print("Could not find error handlers section")

# Write back
with open("c:/Users/malik/Downloads/KapilaInvoice/app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done! Restart server to see changes.")
