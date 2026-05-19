import os
import sqlite3
import pandas as pd
import numpy as np

print("="*60)
print("🚀 STAGE 1 & 2: MASTER RE-ENGINEERED INGESTION PIPELINE (FINAL FIX)")
print("="*60)

# Paths Configuration
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
RAW_CSV_PATH = os.path.join(BASE_DIR, "data", "csv", "sales_data.csv") 
DB_PATH = os.path.join(BASE_DIR, "data", "csv", "financial_enterprise.db")

# Dynamic DB Generation
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ------------------------------------------------------------
# 🗑️ DATABASE CLEAN REFRESH LAYER
# ------------------------------------------------------------
print("🧹 Dropping old mismatched tables for a clean restart...")
cursor.execute("DROP TABLE IF EXISTS payments;")
cursor.execute("DROP TABLE IF EXISTS orders;")
cursor.execute("DROP TABLE IF EXISTS products;")
cursor.execute("DROP TABLE IF EXISTS customers;")
cursor.execute("DROP TABLE IF EXISTS companies;")
conn.commit()

# ------------------------------------------------------------
# 🏗️ STAGE 1: 3NF RELATIONAL DESIGN
# ------------------------------------------------------------
print("🔨 Setting up clean database schemas...")

cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT UNIQUE,
    sector TEXT,
    country TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    gender TEXT,
    age INTEGER,
    country TEXT,
    loyalty_score REAL DEFAULT 0.0
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    brand TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    company_id INTEGER,
    profit_usd REAL,
    total_price_usd REAL,
    order_date TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(company_id) REFERENCES companies(company_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    order_id TEXT,
    payment_method TEXT,
    payment_status TEXT,
    PRIMARY KEY(order_id, payment_method),
    FOREIGN KEY(order_id) REFERENCES orders(order_id)
);
""")

conn.commit()
print("✅ 3NF structural layout created successfully!")

# ------------------------------------------------------------
# ⚡ STAGE 2: SAFE WINDOW CHUNKING & INGESTION
# ------------------------------------------------------------
print("\n🔥 Ingesting 1 Million rows with chunksize=50000...")

initial_companies = [
    ("Nvidia", "AI Semiconductor", "USA"),
    ("JPMorgan", "Finance", "USA"),
    ("Microsoft", "Cloud Computing", "USA"),
    ("Meta", "Digital Services", "USA"),
    ("Apple", "Consumer Electronics", "USA")
]

for name, sec, ctr in initial_companies:
    cursor.execute("""
        INSERT OR IGNORE INTO companies (company_name, sector, country)
        VALUES (?, ?, ?);
    """, (name, sec, ctr))
conn.commit()

cursor.execute("SELECT company_name, company_id FROM companies;")
company_lookup = dict(cursor.fetchall())

if not os.path.exists(RAW_CSV_PATH):
    print(f"❌ Error: Raw dataset nahi mila! Path check karein: {RAW_CSV_PATH}")
    exit()

chunk_count = 1

for chunk in pd.read_csv(RAW_CSV_PATH, chunksize=50000):
    print(f"📦 Processing & downcasting block {chunk_count}...")
    
    # STEP 4: Memory Optimization
    if 'age' in chunk.columns:
        chunk['age'] = chunk['age'].fillna(30).astype(np.int32)
    if 'profit_usd' in chunk.columns:
        chunk['profit_usd'] = chunk['profit_usd'].fillna(0.0).astype(np.float32)
    if 'total_price_usd' in chunk.columns:
        chunk['total_price_usd'] = chunk['total_price_usd'].fillna(0.0).astype(np.float32)
        
    # A. Customers Extract (Using exact column 'customer_loyalty_score')
    cust_df = chunk[['customer_id', 'gender', 'age', 'country', 'customer_loyalty_score']].drop_duplicates(subset=['customer_id'])
    for _, row in cust_df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO customers (customer_id, gender, age, country, loyalty_score)
            VALUES (?, ?, ?, ?, ?);
        """, (row['customer_id'], row['gender'], int(row['age']), str(row['country']), float(row['customer_loyalty_score'])))
        
    # B. Products Extract
    prod_df = chunk[['product_id', 'product_name', 'category', 'brand']].drop_duplicates(subset=['product_id'])
    for _, row in prod_df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO products (product_id, product_name, category, brand)
            VALUES (?, ?, ?, ?);
        """, (row['product_id'], row['product_name'], row['category'], row['brand']))
        
    # C. Dynamic mapping of orders & payment layers (Mapping 'Oorder_id' cleanly)
    for _, row in chunk.iterrows():
        # Hamare dataset me company_name direct nahi hai to hum brand ya generic reference map kar sakte hain
        # Agar brand column me company names hain to row['brand'] use karein, warna default brand fallback
        c_name = row.get('brand', 'Nvidia')
        
        if c_name not in company_lookup:
            cursor.execute("""
                INSERT OR IGNORE INTO companies (company_name, sector, country)
                VALUES (?, 'General Tech', 'Global');
            """, (c_name,))
            conn.commit()
            cursor.execute("SELECT company_name, company_id FROM companies;")
            company_lookup = dict(cursor.fetchall())
            
        c_id = company_lookup.get(c_name, 1)
        
        cursor.execute("""
            INSERT OR IGNORE INTO orders (order_id, customer_id, product_id, company_id, profit_usd, total_price_usd, order_date)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (row['Oorder_id'], row['customer_id'], row['product_id'], c_id, float(row['profit_usd']), float(row['total_price_usd']), str(row['order_date'])))
        
        cursor.execute("""
            INSERT OR IGNORE INTO payments (order_id, payment_method, payment_status)
            VALUES (?, ?, ?);
        """, (row['Oorder_id'], row['payment_method'], row['payment_status']))
        
    conn.commit()
    chunk_count += 1

print("\n" + "="*60)
print("✅ SUCCESS: STAGE 1 & 2 ARCHITECTURE TO 100% STABLE STATUS!")
print("="*60)
conn.close()