"""
Kapila Restaurant Billing & Management System - College Project
Full-stack POS with SQLite/MySQL support, PDF/email/WhatsApp, reports, stock mgmt
Stable SQLite - MySQL optional
"""

import os
from dotenv import load_dotenv
import uuid
import smtplib
import secrets
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

load_dotenv()

# App config
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database/kapila_invoice.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static/images/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['PDF_FOLDER'] = os.path.join(os.path.dirname(__file__), 'invoices')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure dirs
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

# DB
db = SQLAlchemy(app)

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models (matching mysql_schema)
# Models (matching mysql_schema) - REMOVED RAW SQLAlchemy MODELS
# Use manual mysql_schema.sql instead for precise control
# db.create_all() will be skipped to avoid SQLite conflict
pass

# Configuration
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Add 'now' to all templates (must be after app is defined)
@app.context_processor
def inject_now():
    return dict(now=datetime.now())

# Database configuration - SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'kapila_invoice.db')

# File upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'uploads')
PDF_FOLDER = os.path.join(BASE_DIR, 'invoices')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============= Database Helpers =============
# Database Helpers - Updated for MySQL
# Keep raw sqlite3 functions temporarily until full migration
# TODO: Replace with db.session.query after testing

# MySQL migration paused - SQLite stable
DATABASE = os.path.join(BASE_DIR, 'database', 'kapila_invoice.db')

import sqlite3
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur

# ============= Database Initialization =============
def init_database():
    """Initialize database tables"""
    db = get_db()
    
    # Create users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'staff',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create business_settings table
    db.execute('''
        CREATE TABLE IF NOT EXISTS business_settings (
            id INTEGER PRIMARY KEY,
            business_name TEXT DEFAULT 'Kapila Kathi Kebab',
            logo_path TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            gst_number TEXT,
            footer_message TEXT DEFAULT 'Thank you for your order!',
            email_smtp_host TEXT,
            email_smtp_port INTEGER DEFAULT 587,
            email_username TEXT,
            email_password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
    db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            image_path TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create invoices table
    db.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL UNIQUE,
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            customer_email TEXT,
            customer_address TEXT,
            subtotal REAL NOT NULL DEFAULT 0,
            tax_rate REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total REAL NOT NULL,
            payment_mode TEXT DEFAULT 'Cash',
            notes TEXT,
            pdf_path TEXT,
            created_by INTEGER,
            invoice_date TEXT NOT NULL,
            invoice_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create invoice_items table
    db.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        )
    ''')
    
    db.commit()
    
    # Insert default admin user
    admin = query_db('SELECT * FROM users WHERE username = ?', ('admin',), one=True)
    if not admin:
        hashed_pw = generate_password_hash('admin123')
        db.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@kapila.com', hashed_pw, 'admin'))
        db.commit()
    
    # Insert default business settings
    settings = query_db('SELECT * FROM business_settings WHERE id = ?', (1,), one=True)
    if not settings:
        db.execute('''
            INSERT INTO business_settings (id, business_name, address, phone, footer_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, 'Kapila Kathi Kebab', '123 Restaurant Street, City', '+91 9876543210', 'Thank you for your order!'))
        db.commit()
    
    # Insert sample products
    products_count = query_db('SELECT COUNT(*) as count FROM products')
    if products_count[0]['count'] == 0:
        products = [
            ('Chicken Kathi Roll (SF)', 'Rolls', 90),
            ('Paneer Kathi Roll (SF)', 'Rolls', 80),
            ('Chicken Kathi Roll (DF)', 'Rolls', 100),
            ('Paneer Kathi Roll (DF)', 'Rolls', 90),
            ('Veggie Special Roll', 'Rolls', 70),
            ('Egg Roll (SF)', 'Rolls', 60),
            ('Chicken Biryani', 'Biryani', 150),
            ('Paneer Biryani', 'Biryani', 130),
            ('Veg Biryani', 'Biryani', 100),
            ('Chicken Fried Rice', 'Rice', 120),
            ('Paneer Fried Rice', 'Rice', 100),
            ('Spring Roll', 'Starters', 50),
            ('Paneer Pakora', 'Starters', 60),
            ('Chicken Pakora', 'Starters', 70),
            ('Masala Papad', 'Starters', 30),
            ('Buttermilk', 'Beverages', 30),
            ('Lassi', 'Beverages', 40),
            ('Mineral Water', 'Beverages', 20)
        ]
        for name, category, price in products:
            db.execute('INSERT INTO products (name, category, price) VALUES (?, ?, ?)', (name, category, price))
        db.commit()
    
    print("Database initialized successfully!")

# ============= User Class =============
class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)
    if user:
        return User(user['id'], user['username'], user['email'], user['role'])
    return None

# ============= Helper Functions =============
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_invoice_number():
    """Generate unique invoice number"""
    today = datetime.now().strftime('%Y%m%d')
    last_invoice = query_db(
        "SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
        (f'INV-{today}%',),
        one=True
    )
    
    if last_invoice:
        num = int(last_invoice['invoice_number'].split('-')[-1]) + 1
    else:
        num = 1
    
    return f'INV-{today}-{str(num).zfill(4)}'

def get_business_settings():
    """Get business settings"""
    settings = query_db('SELECT * FROM business_settings WHERE id = ?', (1,), one=True)
    return dict(settings) if settings else {}

def get_products():
    """Get all active products"""
    products = query_db('SELECT * FROM products WHERE is_active = 1 ORDER BY category, name')
    return [dict(p) for p in products]

def get_product_by_id(product_id):
    """Get product by ID"""
    product = query_db('SELECT * FROM products WHERE id = ?', (product_id,), one=True)
    return dict(product) if product else None

def calculate_sales_summary():
    """Calculate sales summary"""
    today = datetime.now().strftime('%Y-%m-%d')
    month_start = datetime.now().strftime('%Y-%m-01')
    
    total_sales = query_db("SELECT COALESCE(SUM(total), 0) as total FROM invoices", one=True)
    today_sales = query_db("SELECT COALESCE(SUM(total), 0) as total FROM invoices WHERE invoice_date = ?", (today,), one=True)
    monthly_sales = query_db("SELECT COALESCE(SUM(total), 0) as total FROM invoices WHERE invoice_date >= ?", (month_start,), one=True)
    invoice_count = query_db("SELECT COUNT(*) as count FROM invoices", one=True)
    
    return {
        'total_sales': total_sales['total'] if total_sales else 0,
        'today_sales': today_sales['total'] if today_sales else 0,
        'monthly_sales': monthly_sales['total'] if monthly_sales else 0,
        'invoice_count': invoice_count['count'] if invoice_count else 0
    }

# ============= PDF Generation (Professional) =============
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
    
    pdf_filename = f"{invoice_data['invoice_number']}.pdf"
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
    
    # 2. Address - Mobile & Landline on one line, Email on another
    business_email = business_settings.get('email') if business_settings else 'Parvezkapila@gmail.com'
    elements.append(Paragraph("173, Dhole Patil Road, Shop No. 4", address_style))
    elements.append(Paragraph("Nalini Chambers, Pune - 411001", address_style))
    elements.append(Paragraph("Mobile: 70382 04449 | Landline: 020-41280262", address_style))
    elements.append(Paragraph(f"Email: {business_email}", address_style))
    elements.append(Spacer(1, 15))
    
    # 3. Invoice meta
    invoice_no = invoice_data.get('invoice_number', 'N/A')
    invoice_date = invoice_data.get('invoice_date', datetime.now().strftime('%d/%m/%Y'))
    elements.append(Paragraph(f"Invoice No: {invoice_no}", meta_style))
    elements.append(Paragraph(f"Date: {invoice_date}", meta_style))
    elements.append(Spacer(1, 20))
    
    # 4. BILL TO - Customer name in UPPERCASE
    elements.append(Paragraph("BILL TO", bill_heading))
    customer_name_upper = invoice_data.get('customer_name', 'N/A').upper()
    elements.append(Paragraph(customer_name_upper, bill_content))
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
        # Test SMTP login first
        server = smtplib.SMTP(smtp_host, 587)
        server.starttls()
        server.login(email_user, email_password)
        print("SMTP login successful")

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
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(pdf_path)}")
                msg.attach(part)

        server.sendmail(email_user, recipient, msg.as_string())
        server.quit()
        return True, "Email sent"
    except Exception as e:
        return False, str(e)


# ============= Email Functions =============
def send_email(recipient_email, subject, body, attachment_path=None):
    """Send email with optional attachment"""
    settings = get_business_settings()
    
    smtp_host = settings.get('email_smtp_host')
    email_user = settings.get('email_username')
    email_password = settings.get('email_password')
    
    if not all([smtp_host, email_user, email_password]):
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
                msg.attach(part)
        
        server = smtplib.SMTP(smtp_host, 587)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ============= Routes =============
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['email'], user['role'])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    sales_summary = calculate_sales_summary()
    settings = get_business_settings()
    recent_invoices = query_db('SELECT * FROM invoices ORDER BY created_at DESC LIMIT 5')
    recent_invoices = [dict(inv) for inv in recent_invoices]
    
    products = get_products()
    return render_template('dashboard.html', sales_summary=sales_summary, 
                         settings=settings, recent_invoices=recent_invoices,
                         products=products)

@app.route('/invoice/new', methods=['GET', 'POST'])
@login_required
def new_invoice():
    settings = get_business_settings()
    products = get_products()
    
    products_by_category = {}
    for product in products:
        category = product['category']
        if category not in products_by_category:
            products_by_category[category] = []
        products_by_category[category].append(product)
    
    if request.method == 'POST':
        try:
            invoice_number = generate_invoice_number()
            customer_name = request.form.get('customer_name')
            customer_phone = request.form.get('customer_phone')
            customer_email = request.form.get('customer_email')
            customer_address = request.form.get('customer_address')
            payment_mode = request.form.get('payment_mode', 'Cash')

            # Collect items from request
            items = []
            item_count = int(request.form.get('item_count', 0))
            print(f"Debug - item_count: {item_count}")

            for i in range(item_count):
                product_id = request.form.get(f'product_id_{i}')
                quantity = int(request.form.get(f'quantity_{i}', 0))
                print(f"Debug - item {i}: product_id={product_id}, quantity={quantity}")

                if quantity > 0 and product_id:
                    product = get_product_by_id(int(product_id))
                    if product:
                        amount = float(product['price']) * quantity
                        items.append({
                            'product_id': product_id,
                            'item_name': product['name'],
                            'quantity': quantity,
                            'unit_price': product['price'],
                            'amount': amount
                        })

            print(f"Debug - collected items: {len(items)}")

            invoice_date = datetime.now().strftime('%Y-%m-%d')
            invoice_time = datetime.now().strftime('%H:%M:%S')

            # Insert invoice with initial values
            cur = execute_db('''
                INSERT INTO invoices (
                    invoice_number, customer_name, customer_phone,
                    customer_email, customer_address, subtotal, total,
                    payment_mode, created_by, invoice_date, invoice_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (invoice_number, customer_name, customer_phone,
                 customer_email, customer_address, 0, 0,
                 payment_mode, current_user.id, invoice_date, invoice_time))

            invoice_id = cur.lastrowid

            # Insert invoice items
            print(f"Debug - About to insert {len(items)} items for invoice_id: {invoice_id}")
            for item in items:
                print(f"Debug - Inserting item: {item}")
                execute_db('''
                    INSERT INTO invoice_items (
                        invoice_id, product_id, item_name, quantity, unit_price, amount
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (invoice_id, item['product_id'], item['item_name'],
                     item['quantity'], item['unit_price'], item['amount']))

            # Fetch invoice and items from database
            print(f"Debug - Fetching invoice with id: {invoice_id}")
            invoice = query_db('SELECT * FROM invoices WHERE id = ?', (invoice_id,), one=True)
            print(f"Debug - Invoice fetched: {invoice}")
            print(f"Debug - Fetching items for invoice_id: {invoice_id}")
            db_items = query_db('SELECT * FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
            db_items = [dict(item) for item in db_items]
            print(f"Debug - Items fetched from DB: {len(db_items)}")

            # Validate that items were saved
            if not db_items:
                flash('No items found for the invoice', 'danger')
                # Optionally delete the empty invoice
                execute_db('DELETE FROM invoices WHERE id = ?', (invoice_id,))
                return redirect(url_for('new_invoice'))

            # Recalculate subtotal from database items
            subtotal = sum(float(item['quantity']) * float(item['unit_price']) for item in db_items)
            total = subtotal

            # Update invoice with correct subtotal and total
            execute_db('UPDATE invoices SET subtotal = ?, total = ? WHERE id = ?', (subtotal, total, invoice_id))

            # Debug logs before PDF generation
            print(f"Debug - Subtotal: {subtotal}, Items count: {len(db_items)}")
            if subtotal == 0 or not db_items:
                print("Warning: Subtotal is zero or no items found")

            # Generate PDF after saving to database
            invoice_data = dict(invoice)
            invoice_data['subtotal'] = subtotal
            invoice_data['total'] = total

            pdf_path = generate_pdf(invoice_id, invoice_data, db_items, settings)

            # Update PDF path
            execute_db('UPDATE invoices SET pdf_path = ? WHERE id = ?', (pdf_path, invoice_id))

            flash(f'Invoice {invoice_number} created successfully!', 'success')
            return redirect(url_for('view_invoice', invoice_id=invoice_id))

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('new_invoice.html', settings=settings,
                         products=products, products_by_category=products_by_category)

@app.route('/invoice/view/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    invoice = query_db('SELECT * FROM invoices WHERE id = ?', (invoice_id,), one=True)
    
    if not invoice:
        flash('Invoice not found', 'danger')
        return redirect(url_for('dashboard'))
    
    items = query_db('SELECT * FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
    items = [dict(item) for item in items]
    
    settings = get_business_settings()
    
    return render_template('view_invoice.html', invoice=dict(invoice), items=items, settings=settings)

@app.route('/invoice/list')
@login_required
def invoice_list():
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10

    # Build query
    query = 'SELECT * FROM invoices WHERE 1=1'
    args = []

    if search:
        query += ' AND (customer_name LIKE ? OR invoice_number LIKE ?)'
        args.extend([f'%{search}%', f'%{search}%'])

    query += ' ORDER BY created_at DESC'

    # Get total count for pagination
    count_query = query.replace('SELECT *', 'SELECT COUNT(*) as count')
    total_result = query_db(count_query, args, one=True)
    total_invoices = total_result['count'] if total_result else 0
    total_pages = (total_invoices + per_page - 1) // per_page

    # Add pagination to query
    offset = (page - 1) * per_page
    query += f' LIMIT {per_page} OFFSET {offset}'

    invoices = query_db(query, args)
    invoices = [dict(inv) for inv in invoices]

    return render_template('invoice_list.html',
                         invoices=invoices,
                         search_query=search,
                         current_page=page,
                         total_pages=total_pages)

@app.route('/invoice/pdf/<int:invoice_id>')
@login_required
def download_pdf(invoice_id):
    invoice = query_db('SELECT * FROM invoices WHERE id = ?', (invoice_id,), one=True)
    
    if invoice and invoice['pdf_path'] and os.path.exists(invoice['pdf_path']):
        return send_file(invoice['pdf_path'], as_attachment=True,
                       download_name=f"invoice_{invoice['invoice_number']}.pdf")
    
    flash('PDF not found', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/products')
@login_required
def products():
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    query = 'SELECT * FROM products WHERE is_active = 1'
    args = []
    
    if search:
        query += ' AND name LIKE ?'
        args.append(f'%{search}%')
    
    if category_filter:
        query += ' AND category = ?'
        args.append(category_filter)
    
    query += ' ORDER BY category, name'
    
    products_list = query_db(query, args)
    products_list = [dict(p) for p in products_list]
    
    return render_template('products.html', products=products_list, 
                         search_query=search, category_filter=category_filter)

@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(str(uuid.uuid4()) + '_' + file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_path = os.path.join(UPLOAD_FOLDER, filename)
        
        execute_db('INSERT INTO products (name, category, price, image_path) VALUES (?, ?, ?, ?)',
                  (name, category, price, image_path))
        
        flash('Product added!', 'success')
        return redirect(url_for('products'))
    
    return render_template('new_product.html')

@app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = query_db('SELECT * FROM products WHERE id = ?', (product_id,), one=True)
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        
        execute_db('UPDATE products SET name = ?, category = ?, price = ? WHERE id = ?',
                  (name, category, price, product_id))
        
        flash('Product updated!', 'success')
        return redirect(url_for('products'))
    
    return render_template('edit_product.html', product=dict(product))

@app.route('/product/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    execute_db('UPDATE products SET is_active = 0 WHERE id = ?', (product_id,))
    flash('Product deleted!', 'success')
    return redirect(url_for('products'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    settings_data = get_business_settings()
    
    if request.method == 'POST':
        business_name = request.form.get('business_name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        email = request.form.get('email')
        gst_number = request.form.get('gst_number')
        footer_message = request.form.get('footer_message')
        
        execute_db('''
            UPDATE business_settings SET 
            business_name = ?, address = ?, phone = ?, email = ?, 
            gst_number = ?, footer_message = ? WHERE id = 1
        ''', (business_name, address, phone, email, gst_number, footer_message))
        
        flash('Settings updated!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', settings=settings_data)

# ============= Signup Route =============
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'staff')
        
        # Validation
        if len(username) < 3:
            flash('Username must be at least 3 characters', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('signup'))
        
        # Check if username or email exists
        existing_user = query_db('SELECT * FROM users WHERE username = ? OR email = ?', (username, email), one=True)
        if existing_user:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('signup'))
        
        # Create user
        hashed_pw = generate_password_hash(password)
        execute_db('INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                  (username, email, hashed_pw, role))
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


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

    # Ensure PDF exists
    pdf_path = invoice.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        flash("PDF not found, please regenerate invoice", "danger")
        return redirect(url_for("view_invoice", invoice_id=invoice_id))

    print(f"PDF path for WhatsApp: {pdf_path}")

    message = f"""{business_name}

Thank you for your order!

Invoice: {invoice.get('invoice_number', 'N/A')}
Date: {invoice.get('invoice_date', 'N/A')}
Amount: INR {float(invoice.get('total', 0)):,.2f}

{settings.get('footer_message', 'Thank you!')}"""

    encoded = message.replace("\n", "%0A").replace(" ", "%20")
    phone = invoice.get("customer_phone", "").replace(" ", "").replace("-", "")

    if phone and len(phone) >= 10:
        if not phone.startswith("+"):
            phone = "+91" + phone[-10:]
        return redirect(f"https://wa.me/{phone.replace('+', '')}?text={encoded}")
    else:
        flash("No valid phone number", "warning")
        return redirect(url_for("view_invoice", invoice_id=invoice_id))

@app.route("/invoice/delete/<int:invoice_id>", methods=['POST'])
@login_required
def delete_invoice(invoice_id):
    invoice = query_db("SELECT * FROM invoices WHERE id = ?", (invoice_id,), one=True)
    if not invoice:
        flash("Invoice not found", "danger")
        return redirect(url_for("dashboard"))
    
    invoice = dict(invoice)
    
    # Delete associated PDF file if exists
    if invoice.get('pdf_path') and os.path.exists(invoice['pdf_path']):
        try:
            os.remove(invoice['pdf_path'])
        except Exception as e:
            print(f"Error deleting PDF: {e}")
    
    # Delete invoice items first
    execute_db('DELETE FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
    
    # Delete invoice
    execute_db('DELETE FROM invoices WHERE id = ?', (invoice_id,))
    
    flash(f'Invoice {invoice.get("invoice_number", "")} deleted successfully', 'success')
    return redirect(url_for('dashboard'))

# ============= Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', error=str(e)), 500

@app.errorhandler(403)
def forbidden(e):
    flash('You do not have permission to access this page', 'danger')
    return redirect(url_for('dashboard')), 403

@app.errorhandler(400)
def bad_request(e):
    flash('Invalid request', 'danger')
    return redirect(url_for('dashboard')), 400

# ============= Offline Route =============
@app.route('/offline')
def offline():
    return render_template('offline.html')

# ============= Share Route =============
@app.route('/share', methods=['POST'])
def share_target():
    # Handle shared content from other apps
    data = request.form
    title = data.get('title', '')
    text = data.get('text', '')
    url = data.get('url', '')
    
    flash(f'Shared: {title} - {text}', 'info')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    with app.app_context():
        init_database()
    # Run on port 5001 to avoid conflict with student management system
    app.run(debug=True, port=5001)

