import os
import sqlite3

# Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
# 📁 Hamara naya enterprise SQLite database file path
DB_PATH = os.path.join(BASE_DIR, "data", "financial_enterprise.db")

print("="*60)
print("🚀 CLASS 5 & 6: INITIALIZING RELATIONAL DATABASE SCHEMA")
print("="*60)

# Connect to SQLite Database (Agar file nahi hogi, toh yeh automatic bana dega)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 🔥 Enable Foreign Key Support in SQLite (By default yeh off hoti hai)
cursor.execute("PRAGMA foreign_keys = ON;")

print("🛠️ Creating normalized enterprise tables...")

# 1. COMPANIES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT UNIQUE NOT NULL
);
""")

# 2. CUSTOMERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT,
    gender TEXT,
    age INTEGER,
    customer_segment TEXT,
    country TEXT,
    city TEXT
);
""")

# 3. PRODUCTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    sub_category TEXT,
    brand TEXT,
    unit_price_usd REAL
);
""")

# 4. ORDERS MASTER TABLE (The Central Junction)
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    company_id INTEGER,
    order_date TEXT,
    order_year INTEGER,
    order_month TEXT,
    quantity INTEGER,
    discount_percent REAL,
    total_price_usd REAL,
    cost_usd REAL,
    profit_usd REAL,
    order_priority TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
""")

# 5. PAYMENTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    payment_method TEXT,
    payment_status TEXT,
    installment_plan TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
""")

# 6. SHIPPING TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS shipping (
    shipping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    shipping_method TEXT,
    shipping_cost_usd REAL,
    delivery_days INTEGER,
    delivery_status TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
""")

# Commit changes and close connection
conn.commit()
conn.close()

print("\n" + "="*60)
print("✅ SUCCESS: 6 Normalized Tables Created Flawlessly!")
print(f"📁 Database Location: {DB_PATH}")
print("="*60)