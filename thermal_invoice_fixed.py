from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
import os

def generate_invoice_pdf(data, output_path='invoice.pdf'):
    """
    Generate EXACT thermal-style 80mm invoice matching reference
    """
    
    # Ensure output dir
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    c = canvas.Canvas(output_path, pagesize=(80 * mm, 300 * mm))
    
    y = 280 * mm
    
    # HEADER CENTERED
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(40 * mm, y, "KAPILA KATHI KEBAB")
    y -= 6 * mm
    
    c.setFont("Helvetica", 9)
    c.drawCentredString(40 * mm, y, "173, Dhole Patil Road, Shop No. 4")
    y -= 4 * mm
    c.drawCentredString(40 * mm, y, "Nalini Chambers, Pune - 411001")
    y -= 4 * mm
    c.drawCentredString(40 * mm, y, "Mobile: 70382 04449")
    y -= 3 * mm
    c.drawCentredString(40 * mm, y, "Landline: 020-41280262")
    y -= 8 * mm
    
    # INVOICE DETAILS
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * mm, y, f"Invoice No: {data['invoice_number']}")
    y -= 5 * mm
    c.drawString(2 * mm, y, f"Date: {data['date']}")
    y -= 8 * mm
    
    # BILL TO
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * mm, y, "BILL TO")
    y -= 4 * mm
    c.setFont("Helvetica", 11)
    c.drawString(2 * mm, y, data["customer_name"].upper())
    y -= 10 * mm
    
    # TABLE HEADER
    c.setFont("Courier-Bold", 10)
    c.drawString(2 * mm, y, "Item")
    c.drawRightString(22 * mm, y, "Qty")
    c.drawRightString(35 * mm, y, "Rate")
    c.drawRightString(58 * mm, y, "Amount")
    y -= 4 * mm
    
    # ITEMS
    c.setFont("Courier", 9)
    for item in data["items"]:
        # Item name
        c.drawString(2 * mm, y, item["name"][:25])
        y -= 3 * mm
        # Variant
        if "variant" in item:
            c.drawString(2 * mm, y, f"({item['variant']})")
            y -= 2 * mm
        # Numbers row
        qty_str = str(item["quantity"]).rjust(4)
        rate_str = f"{item['rate']:.0f}".rjust(7)
        amt_str = f"{item['amount']:,.0f}".rjust(12)
        c.drawRightString(22 * mm, y, qty_str)
        c.drawRightString(35 * mm, y, rate_str)
        c.drawRightString(58 * mm, y, amt_str)
        y -= 6 * mm
    
    # SUBTOTAL
    y -= 2 * mm
    subtotal = sum(item["amount"] for item in data["items"])
    c.setFont("Courier-Bold", 12)
    c.drawRightString(58 * mm, y, f"Subtotal: INR {subtotal:,.0f}")
    y -= 10 * mm
    
    # PAYMENT
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * mm, y, f"Payment Mode: {data['payment_mode']}")
    y -= 12 * mm
    
    # TERMS
    c.setFont("Courier", 8)
    c.drawString(2 * mm, y, "Terms & Conditions:")
    y -= 4 * mm
    c.drawString(2 * mm, y, "All food items are freshly prepared.")
    y -= 3 * mm
    c.drawString(2 * mm, y, "Payment is requested at the time of delivery.")
    y -= 5 * mm
    c.setFont("Courier-Bold", 8)
    c.drawString(2 * mm, y, "This is a system-generated invoice.")
    
    c.save()
    print(f"Thermal invoice saved to {output_path}")
    return output_path

if __name__ == "__main__":
    test_data = {
        "invoice_number": "KKK-2024-0001",
        "date": "15 Apr 2024",
        "customer_name": "Walk-in Customer",
        "payment_mode": "Cash",
        "items": [
            {"name": "Chicken Kathi Kebab", "variant": "DF", "quantity": 33, "rate": 190, "amount": 6270},
            {"name": "Paneer Roll", "variant": "SF", "quantity": 5, "rate": 80, "amount": 400}
        ]
    }
    generate_invoice_pdf(test_data)
