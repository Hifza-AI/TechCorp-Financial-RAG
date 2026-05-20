import os
import time
import sqlite3
import pandas as pd

# Paths Setup (🚨 Path aligned perfectly with your latest screenshot)
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
INPUT_CSV = os.path.join(BASE_DIR, "data", "csv", "sales_data_cleaned_optimized.csv")
# 🔥 Humne path change karke direct data/csv/ ke andar kar diya hai jahan aapki file bani hai
DB_PATH = os.path.join(BASE_DIR, "data", "csv", "financial_enterprise.db")

print("="*60)
print("🚀 CLASS 7 & 8: ENTERPRISE BULK DATA INGESTION PIPELINE")
print("="*60)

if not os.path.exists(INPUT_CSV):
    print(f"❌ Error: Cleaned CSV file nahi mili dost! Pehle Class 4 check karo.")
    exit()

if not os.path.exists(DB_PATH):
    print(f"❌ Error: database file nahi mili is path par -> {DB_PATH}")
    exit()

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# --- STEP 1: POPULATE COMPANIES TABLE FIRST ---
print("🏢 Extracting and inserting unique companies...")
df_unique_companies = pd.read_csv(INPUT_CSV, usecols=['company_name']).drop_duplicates()

for _, row in df_unique_companies.iterrows():
    try:
        cursor.execute("INSERT OR IGNORE INTO companies (company_name) VALUES (?);", (row['company_name'],))
    except Exception as e:
        pass
conn.commit()

# Create a memory map dictionary {company_name: company_id}
cursor.execute("SELECT company_id, company_name FROM companies;")
company_map = {name: cid for cid, name in cursor.fetchall()}
print(f"✅ Successfully mapped {len(company_map)} enterprise companies to internal IDs.")

# --- STEP 2: CHUNKED INGESTION FOR ALL OTHER TABLES ---
chunk_size = 200000
total_records = 0
start_time = time.time()

print("\n🚀 Starting bulk streaming injection into normalized tables...")
data_stream = pd.read_csv(INPUT_CSV, chunksize=chunk_size)

for index, chunk in enumerate(data_stream, start=1):
    # Speed Optimization Tricks
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA journal_mode = MEMORY;")
    
    # 1. Customers Data
    cust_df = chunk[['customer_id', 'customer_name', 'gender', 'age', 'customer_segment', 'country', 'city']].drop_duplicates(subset=['customer_id'])
    cursor.executemany("""
    INSERT OR IGNORE INTO customers (customer_id, customer_name, gender, age, customer_segment, country, city)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, cust_df.values.tolist())
    
    # 2. Products Data
    prod_df = chunk[['product_id', 'product_name', 'category', 'sub_category', 'brand', 'unit_price_usd']].drop_duplicates(subset=['product_id'])
    cursor.executemany("""
    INSERT OR IGNORE INTO products (product_id, product_name, category, sub_category, brand, unit_price_usd)
    VALUES (?, ?, ?, ?, ?, ?);
    """, prod_df.values.tolist())
    
    # 3. Map company_name to company_id
    chunk['company_id'] = chunk['company_name'].map(company_map)
    
    # 4. Orders Master Data
    orders_df = chunk[['order_id', 'customer_id', 'product_id', 'company_id', 'order_date', 'order_year', 'order_month', 'quantity', 'discount_percent', 'total_price_usd', 'cost_usd', 'profit_usd', 'order_priority']]
    cursor.executemany("""
    INSERT OR IGNORE INTO orders (order_id, customer_id, product_id, company_id, order_date, order_year, order_month, quantity, discount_percent, total_price_usd, cost_usd, profit_usd, order_priority)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, orders_df.values.tolist())
    
    # 5. Payments Data
    payments_df = chunk[['order_id', 'payment_method', 'payment_status', 'installment_plan']]
    cursor.executemany("""
    INSERT OR IGNORE INTO payments (order_id, payment_method, payment_status, installment_plan)
    VALUES (?, ?, ?, ?);
    """, payments_df.values.tolist())
    
    # 6. Shipping Data
    shipping_df = chunk[['order_id', 'shipping_method', 'shipping_cost_usd', 'delivery_days', 'delivery_status']]
    cursor.executemany("""
    INSERT OR IGNORE INTO shipping (order_id, shipping_method, shipping_cost_usd, delivery_days, delivery_status)
    VALUES (?, ?, ?, ?, ?);
    """, shipping_df.values.tolist())
    
    conn.commit()
    total_records += len(chunk)
    print(f"📥 Batch {index}: Streamed and linked {total_records:,} rows into Relational Layer...")

# Restore safety settings
cursor.execute("PRAGMA synchronous = NORMAL;")
end_time = time.time()

print("\n" + "="*60)
print("✅ SUCCESS: Data Ingestion Pipeline Execution Complete!")
print(f"📦 Total Relational Records Synced: {total_records:,}")
print(f"⏱️ Ingestion Time: {end_time - start_time:.2f} Seconds")
print("="*60)

conn.close()