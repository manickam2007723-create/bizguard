"""
BizGuard Backend Service & Export Utilities
Supports standalone execution, database migrations, and report exports.
"""

import os
import csv
import io
import sqlite3
from datetime import datetime

# Default configuration
DB_FILE = os.path.join(os.path.dirname(__file__), 'bizguard.db')
DEMO_USER_EMAIL = 'Yash@Democafe.com'
DEMO_USER_NAME = 'Yash Sharma'

def init_db(db_path=DB_FILE):
    """Initialize SQLite schema if not exists and seed initial demo transactions."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            business_name TEXT NOT NULL,
            industry TEXT,
            created_at TEXT
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            payment_status TEXT DEFAULT 'completed',
            notes TEXT,
            created_at TEXT
        )
    ''')
    
    # Update or insert user record for Yash@Democafe.com
    cursor.execute('SELECT id FROM users WHERE email = ?', (DEMO_USER_EMAIL,))
    user_row = cursor.fetchone()
    if not user_row:
        # Check if old email exists to update safely without duplicate
        cursor.execute('SELECT id FROM users WHERE LOWER(email) = ?', ('arjun@democafe.com',))
        old_user = cursor.fetchone()
        if old_user:
            cursor.execute('''
                UPDATE users
                SET email = ?, full_name = ?
                WHERE id = ?
            ''', (DEMO_USER_EMAIL, DEMO_USER_NAME, old_user[0]))
        else:
            cursor.execute('''
                INSERT INTO users (id, full_name, email, business_name, industry, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('demo-user-1', DEMO_USER_NAME, DEMO_USER_EMAIL, 'Demo Café', 'Food & Beverage / Hospitality', '2026-01-01'))
    
    # Check if transactions seeded
    cursor.execute('SELECT COUNT(*) FROM transactions')
    count = cursor.fetchone()[0]
    if count == 0:
        demo_txs = [
            ('demo-tx-101', '2026-04-05', 'Revenue', 'Product Sales', 'Product Sales', 125000, 'Coffee, Espresso & Beverage Sales'),
            ('demo-tx-102', '2026-04-12', 'Revenue', 'Product Sales', 'Product Sales', 60000, 'Pastry, Bakery & Snack Sales'),
            ('demo-tx-103', '2026-04-20', 'Revenue', 'Service Income', 'Service Income', 15000, 'Weekend Private Event & Workshop Space'),
            ('demo-tx-104', '2026-04-01', 'Expense', 'Rent', 'Rent', 45000, 'Café Commercial Space Lease'),
            ('demo-tx-105', '2026-04-07', 'Expense', 'Salaries', 'Salaries', 55000, 'Barista & Staff Payroll (3 staff)'),
            ('demo-tx-106', '2026-04-10', 'Expense', 'Materials', 'Materials', 32000, 'Single-Origin Coffee Beans, Dairy & Oat Milk'),
            ('demo-tx-107', '2026-04-15', 'Expense', 'Utilities', 'Utilities', 11000, 'Commercial Electricity, Water & High-speed WiFi'),
            ('demo-tx-108', '2026-04-18', 'Expense', 'Marketing', 'Marketing', 7000, 'Local Instagram Reels & Neighborhood Flyers'),
            ('demo-tx-201', '2026-05-04', 'Revenue', 'Product Sales', 'Product Sales', 130000, 'Coffee & Specialty Beverage Sales'),
            ('demo-tx-202', '2026-05-14', 'Revenue', 'Product Sales', 'Product Sales', 62000, 'Gourmet Sandwiches & Artisanal Desserts'),
            ('demo-tx-204', '2026-05-01', 'Expense', 'Rent', 'Rent', 45000, 'Café Commercial Space Lease'),
            ('demo-tx-205', '2026-05-07', 'Expense', 'Salaries', 'Salaries', 55000, 'Barista & Floor Staff Payroll'),
            ('demo-tx-601', '2026-09-02', 'Revenue', 'Product Sales', 'Product Sales', 138000, 'Espresso Bar, Cold Brews & Beverages'),
            ('demo-tx-602', '2026-09-08', 'Revenue', 'Product Sales', 'Product Sales', 72000, 'Artisan Pastries & Daily Sandwiches'),
            ('demo-tx-604', '2026-09-01', 'Expense', 'Rent', 'Rent', 45000, 'Café Commercial Space Lease'),
            ('demo-tx-605', '2026-09-07', 'Expense', 'Salaries', 'Salaries', 56000, 'Barista & Staff Payroll')
        ]
        cursor.executemany('''
            INSERT INTO transactions (id, date, type, title, category, amount, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', demo_txs)

    conn.commit()
    conn.close()

def generate_csv_report(db_path=DB_FILE):
    """
    Generate CSV report containing every transaction with its actual database date.
    Format: Transaction ID,Date,Type,Title,Category,Amount,Description
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Explicitly SELECT the stored transaction date from the database
    cursor.execute('''
        SELECT id, date, type, COALESCE(title, category), category, amount, COALESCE(description, '')
        FROM transactions
        ORDER BY date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\r\n')
    # Required CSV Header
    writer.writerow(['Transaction ID', 'Date', 'Type', 'Title', 'Category', 'Amount', 'Description'])
    for row in rows:
        writer.writerow(row)
    
    return output.getvalue()

# Initialize database on module load
try:
    init_db()
except Exception as e:
    pass

if __name__ == '__main__':
    print("BizGuard SQLite Database Initialized.")
    print(f"Active User: {DEMO_USER_NAME} ({DEMO_USER_EMAIL})")
    csv_sample = generate_csv_report()
    print("CSV Export Preview:")
    print("\n".join(csv_sample.splitlines()[:5]))
