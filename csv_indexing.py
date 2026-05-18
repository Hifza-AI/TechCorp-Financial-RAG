import os
import time
import sqlite3

# Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
DB_PATH = os.path.join(BASE_DIR, "data", "csv", "financial_enterprise.db")

print("="*60)
print("🚀 CLASS 9: CREATING DATABASE INDEXES FOR ULTRA-FAST RAG SEARCH")
print("="*60)

if not os.path.exists(DB_PATH):
    print(f"❌ Error: Database file nahi mili dost! Check path -> {DB_PATH}")
    exit()

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

start_time = time.time()

print("⚡ Creating enterprise B-Tree indexes on foreign keys...")

# 1. Index on Orders table for customer relationships
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);")

# 2. Index on Orders table for product searches
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id);")

# 3. Index on Orders table for company filters (Most important for RAG!)
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_company ON orders(company_id);")

# 4. Index on Orders table for timeline financial queries
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);")

# 5. Index on Products category/brand for lookup speed
cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_lookup ON products(category, brand);")

conn.commit()
end_time = time.time()

print("\n" + "="*60)
print("✅ CLASS 9 SUCCESS: Database Optimization & Indexing Complete!")
print("💡 Your 1 Million Dataset is now running at warp speed.")
print(f"⏱️ Indexing Duration: {end_time - start_time:.4f} Seconds")
print("="*60)

conn.close()