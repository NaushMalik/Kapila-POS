import sqlite3
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# SQLite
sqlite_db = sqlite3.connect('database/kapila_invoice.db')
sqlite_db.row_factory = sqlite3.Row

# MySQL
mysql_db = pymysql.connect(
    host='localhost',
    user='kapila_user',
    password='kapila_pass123',
    database='kapila_invoice_db',
    charset='utf8mb4'
)

print("Migrating SQLite → MySQL...")

tables = ['users', 'business_settings', 'products', 'invoices', 'invoice_items']

for table in tables:
    print(f"Migrating {table}...")
    
    # Get SQLite data
    cursor_sqlite = sqlite_db.execute(f"SELECT * FROM {table}")
    rows = cursor_sqlite.fetchall()
    
    if rows:
        # Prepare MySQL insert
        columns = [desc[0] for desc in cursor_sqlite.description]
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Insert to MySQL
        cursor_mysql = mysql_db.cursor()
        cursor_mysql.executemany(insert_sql, [dict(row) for row in rows])
        mysql_db.commit()
        print(f"  ✓ {cursor_mysql.rowcount} rows migrated")
    
    else:
        print("  No data")

sqlite_db.close()
mysql_db.close()
print("Migration COMPLETE! ✅")
