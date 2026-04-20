#!/usr/bin/env python3
"""Check Kapila Invoice database connection"""

import sqlite3
import os

# Database path
db_path = 'database/kapila_invoice.db'
print(f'Database file: {os.path.abspath(db_path)}')
print(f'Exists: {os.path.exists(db_path)}')
if os.path.exists(db_path):
    print(f'Size: {os.path.getsize(db_path)} bytes')
else:
    print('ERROR: Database file not found!')
    exit(1)

# Connect and query
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f'\nTables in database: {[t[0] for t in tables]}')

# Check users
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()
print(f'\nUsers: {len(users)} found')
for u in users:
    print(f'  - {u[1]} ({u[2]}) - Role: {u[4]}')

# Check products
cursor.execute('SELECT COUNT(*) FROM products')
count = cursor.fetchone()[0]
print(f'\nProducts: {count} found')

# Check invoices
cursor.execute('SELECT COUNT(*) FROM invoices')
count = cursor.fetchone()[0]
print(f'Invoices: {count} found')

# Check business settings
cursor.execute('SELECT * FROM business_settings')
settings = cursor.fetchone()
if settings:
    print(f'\nBusiness Settings:')
    print(f'  Name: {settings[1]}')
    print(f'  Address: {settings[4]}')
    print(f'  Phone: {settings[5]}')

conn.close()
print('\n' + '='*50)
print('DATABASE CONNECTION: SUCCESSFUL')
print('='*50)

