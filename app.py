import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'database/kapila_invoice.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

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
    cur = get_db().execute(query, args)
    get_db().commit()
    cur.close()

def get_table_detail(table_id):
    """Helper: Get table with orders joined to products"""
    table = query_db('SELECT * FROM tables WHERE id = ?', (table_id,), one=True)
    if not table:
        return None
    orders = query_db('''
        SELECT to.*, p.name as item_name, p.price as unit_price 
        FROM table_orders to 
        JOIN products p ON to.product_id = p.id 
        WHERE to.table_id = ?
    ''', (table_id,))
    table = dict(table)  # to mutable
    table['orders'] = orders
    table['total_amount'] = sum(o['amount'] or 0 for o in orders) or 0
    return table

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)
    if user:
        return User(user['id'], user['username'])
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            login_user(User(user['id'], user['username']))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    sales_summary = {'total_sales': 0, 'today_sales': 0, 'monthly_sales': 0, 'invoice_count': 0}
    products = query_db('SELECT * FROM products WHERE is_active = 1 LIMIT 6') or []
    tables = query_db('SELECT * FROM tables LIMIT 12') or []
    return render_template('dashboard.html', sales_summary=sales_summary, products=products, tables=tables)

@app.route('/products')
@login_required
def products():
    products = query_db('SELECT * FROM products WHERE is_active = 1')
    return render_template('products.html', products=products or [])

@app.route('/new_invoice', methods=['GET', 'POST'])
@login_required
def new_invoice():
    if request.method == 'POST':
        customer_name = request.form['customer']
        phone = request.form.get('phone', '')
        payment_mode = request.form.get('payment_mode', 'Cash')
        total = 0
        execute_db('INSERT INTO invoices (customer_name, phone, payment_mode, total) VALUES (?, ?, ?, ?)', (customer_name, phone, payment_mode, total))
        invoice_id = get_db().execute('SELECT last_insert_rowid()').fetchone()[0]
        flash('Invoice created! ID: {}'.format(invoice_id))
        return redirect(url_for('invoices'))
    
    products = query_db('SELECT * FROM products WHERE is_active = 1')
    return render_template('new_invoice.html', products=products or [])

@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form.get('category', '')
        price = float(request.form['price'])
        execute_db('INSERT INTO products (name, category, price) VALUES (?, ?, ?)', (name, category, price))
        flash('Product added!')
        return redirect(url_for('products'))
    return render_template('new_product.html')

@app.route('/delete_product/<int:product_id>')
@login_required
def delete_product(product_id):
    execute_db('DELETE FROM products WHERE id = ?', (product_id,))
    flash('Product deleted!')
    return redirect(url_for('products'))

@app.route('/invoice_list')
@login_required
def invoice_list():
    invoices = query_db('SELECT * FROM invoices ORDER BY id DESC LIMIT 20')
    return render_template('invoice_list.html', invoices=invoices or [])

@app.route('/invoices')
@login_required
def invoices():
    invoices = query_db('SELECT * FROM invoices ORDER BY id DESC')
    return render_template('invoices.html', invoices=invoices or [])

@app.route('/tables')
@login_required
def tables():
    tables = query_db('SELECT * FROM tables ORDER BY table_number')
    products = query_db('SELECT id, name, price FROM products WHERE is_active = 1')
    return render_template('tables.html', tables=tables or [], products=products or [])

@app.route('/tables/json/<int:table_id>')
@login_required
def table_json(table_id):
    """JSON endpoint for JS fetch in tables.html"""
    table = get_table_detail(table_id)
    return jsonify(table or {})

@app.route('/tables/add_order', methods=['POST'])
@login_required
def add_table_order():
    data = request.json
    table_id = data['table_id']
    product_id = data['product_id']
    quantity = data['quantity']
    
    # Get product price
    product = query_db('SELECT price FROM products WHERE id = ? AND is_active = 1', (product_id,), one=True)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'})
    
    unit_price = product['price']
    amount = unit_price * quantity
    
    execute_db('''
        INSERT INTO table_orders (table_id, product_id, quantity, unit_price, amount)
        VALUES (?, ?, ?, ?, ?)
    ''', (table_id, product_id, quantity, unit_price, amount))
    
    # Update table total
    table_detail = get_table_detail(table_id)
    execute_db('UPDATE tables SET total_amount = ? WHERE id = ?', (table_detail['total_amount'], table_id))
    
    return jsonify({'success': True, 'table': table_detail})

@app.route('/tables/mark_paid/<int:table_id>', methods=['POST'])
@login_required
def mark_table_paid(table_id):
    # Create invoice from table orders
    table = query_db('SELECT * FROM tables WHERE id = ?', (table_id,), one=True)
    if not table or not table['total_amount']:
        return jsonify({'success': False, 'error': 'No bill to pay'})
    
    # Insert invoice
    invoice_number = f"INV-T{ table['table_number'] }-{datetime.now().strftime('%Y%m%d%H%M')}"
    execute_db('''
        INSERT INTO invoices (invoice_number, customer_name, total, payment_mode)
        VALUES (?, ?, ?, 'Cash')
    ''', (invoice_number, table['customer_name'] or 'Walk-in', table['total_amount']))
    invoice_id = get_db().execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Move orders to invoice_items
    orders = query_db('SELECT * FROM table_orders WHERE table_id = ?', (table_id,))
    for order in orders:
        execute_db('''
            INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, total)
            VALUES (?, ?, ?, ?, ?)
        ''', (invoice_id, order['product_id'], order['quantity'], order['unit_price'], order['amount']))
    
    # Reset table
    execute_db('DELETE FROM table_orders WHERE table_id = ?', (table_id,))
    execute_db('UPDATE tables SET status = "paid", customer_name = NULL, total_amount = 0 WHERE id = ?', (table_id,))
    
    return jsonify({'success': True, 'invoice_id': invoice_id, 'message': 'Table paid and invoice created'})

@app.route('/tables/receipt/<int:table_id>')
@login_required
def table_receipt(table_id):
    table = get_table_detail(table_id)
    if not table:
        flash('Table not found')
        return redirect(url_for('tables'))
    table['now'] = datetime.now()
    # Simple grouping by category
    grouped = {}
    for order in table['orders']:
        cat = query_db('SELECT category FROM products WHERE id = ?', (order['product_id'],), one=True)
        cat = cat['category'] if cat else 'Other'
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(order)
    table['grouped_orders'] = grouped.items()
    return render_template('table_receipt.html', table=table)

@app.route('/tables/select/<int:table_id>', methods=['POST'])
@login_required
def select_table(table_id):
    customer_name = request.form.get('customer_name', 'Walk-in')
    execute_db('UPDATE tables SET status = "booked", customer_name = ? WHERE id = ?', (customer_name, table_id))
    table = get_table_detail(table_id)
    return jsonify({'success': True, 'table': table})

@app.route('/tables/<int:table_id>')
@login_required
def table_detail(table_id):
    """Full page for table detail"""
    table = get_table_detail(table_id)
    if not table:
        flash('Table not found')
        return redirect(url_for('tables'))
    products = query_db('SELECT * FROM products WHERE is_active = 1')
    return render_template('table_detail.html', table=table, products=products or [])

@app.route('/whatsapp_invoice/<int:invoice_id>')
def whatsapp_invoice(invoice_id):
    return redirect(url_for('invoice_list'))

@app.route('/generate_invoice_pdf')
@login_required
def generate_invoice_pdf():
    invoice_id = request.args.get('invoice_id')
    if not invoice_id:
        flash('No invoice ID provided')
        return redirect(url_for('invoice_list'))
    
    invoice = query_db('SELECT * FROM invoices WHERE id = ?', (invoice_id,), one=True)
    if not invoice:
        flash('Invoice not found')
        return redirect(url_for('invoice_list'))
    
    items = query_db('SELECT ii.*, p.name FROM invoice_items ii JOIN products p ON ii.product_id = p.id WHERE invoice_id = ?', (invoice_id,))
    
    invoice_data = {
        "invoice_number": invoice['invoice_number'] or f"INV-{invoice['id']}",
        "date": invoice['created_at'][:11] if invoice['created_at'] else "Today",
        "customer_name": invoice['customer_name'] or "Walk-in Customer",
        "payment_mode": "Cash",
        "items": [{"name": row['name'], "variant": "DF", "quantity": row['quantity'], "rate": row['price'], "amount": row['total']} for row in items]
    }
    
    from thermal_invoice import generate_invoice_pdf
    filename = f"invoice_{invoice['id']}.pdf"
    output_path = os.path.join('invoices', filename)
    generate_invoice_pdf(invoice_data, output_path)
    
    flash(f'Thermal PDF saved: {filename}')
    return redirect(url_for('invoice_list'))

@app.errorhandler(404)
def not_found(e):
    return '<h1>404 Not Found</h1>', 404

def init_database():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, is_active INTEGER)')
    db.execute('CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY, invoice_number TEXT UNIQUE, customer_name TEXT, total REAL)')
    db.execute('CREATE TABLE IF NOT EXISTS tables (id INTEGER PRIMARY KEY, table_number INTEGER, status TEXT DEFAULT "empty", customer_name TEXT, total_amount REAL DEFAULT 0)')
    db.commit()

    # Add new tables if not exist
    db.execute('CREATE TABLE IF NOT EXISTS table_orders (id INTEGER PRIMARY KEY AUTOINCREMENT, table_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price REAL, amount REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    db.execute('CREATE TABLE IF NOT EXISTS invoice_items (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price REAL, total REAL)')
    db.commit()

    # Sample tables if empty
    if not query_db('SELECT COUNT(*) from tables', one=True) or query_db('SELECT COUNT(*) from tables', one=True)[0] == 0:
        for i in range(1, 13):
            db.execute('INSERT OR IGNORE INTO tables (id, table_number, status) VALUES (?, ?, "empty")', (i, i))
        db.commit()

    # Sample products if empty
    if not query_db('SELECT COUNT(*) from products', one=True) or query_db('SELECT COUNT(*) from products', one=True)[0] == 0:
        sample_products = [
            ('Aloo Roll', 'Rolls', 50.0),
            ('Paneer Roll', 'Rolls', 70.0),
            ('Chicken Roll', 'Rolls', 90.0),
            ('Veg Biryani', 'Biryani', 120.0),
            ('Chicken Biryani', 'Biryani', 180.0),
            ('Cold Drink', 'Beverages', 30.0)
        ]
        for name, cat, price in sample_products:
            db.execute('INSERT OR IGNORE INTO products (name, category, price, is_active) VALUES (?, ?, ?, 1)', (name, cat, price))
        db.commit()
    
    if not query_db('SELECT * FROM users WHERE username="admin"'):
        pw_hash = generate_password_hash('admin123')
        db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', pw_hash))
        db.commit()
    
    print("Database ready!")

with app.app_context():
    init_database()

if __name__ == '__main__':
    app.run(debug=True, port=5001)

