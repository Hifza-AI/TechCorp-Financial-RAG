import sqlite3
import time

print("="*60)
print("🚀 STAGE 3: HIGH-SPEED SQL PERFORMANCE INDEXING (SUPERCHARGED)")
print("="*60)

DB_PATH = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG\data\csv\financial_enterprise.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ------------------------------------------------------------
# ⚡ STEP 6: CREATE STRATEGIC COVERING INDEXES
# ------------------------------------------------------------
print("🏗️ Injecting advanced covering indexes to bypass Full Table Scans...")

# Heavy lifting indexes for Joins and Aggregations
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_company_id ON orders(company_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id);")

# Aggregation speedups (Sums & Counts optimization)
cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_profit_total ON orders(profit_usd, total_price_usd);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_status_method ON payments(payment_status, payment_method, order_id);")

# Dimension tables lookup enhancement
cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country, customer_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category, product_id);")

conn.commit()
print("✅ Advanced indexing layer deployed across 1M rows storage!")

# ------------------------------------------------------------
# 📊 STEP 7: LIVE QUERY TESTING LAB
# ------------------------------------------------------------
print("\n🔥 Executing diagnostic performance lookups across 1 Million rows...")

test_queries = {
    "1. Top Profitable Company/Brand": """
        SELECT T2.company_name, SUM(T1.profit_usd) as total_profit 
        FROM orders T1 
        JOIN companies T2 ON T1.company_id = T2.company_id 
        GROUP BY T2.company_name 
        ORDER BY total_profit DESC 
        LIMIT 3;
    """,
    "2. Country-Wise Revenue Generation": """
        SELECT T2.country, SUM(T1.total_price_usd) as total_revenue 
        FROM orders T1 
        JOIN customers T2 ON T1.customer_id = T2.customer_id 
        GROUP BY T2.country 
        ORDER BY total_revenue DESC 
        LIMIT 5;
    """,
    "3. Product Categories Contributing to Highest Financial Volatility": """
        SELECT T2.category, AVG(T1.profit_usd) as avg_profit 
        FROM orders T1 
        JOIN products T2 ON T1.product_id = T2.product_id 
        GROUP BY T2.category 
        ORDER BY avg_profit DESC;
    """,
    "4. Payment Failures / High Fraud Risk Mapping": """
        SELECT T2.payment_method, COUNT(*) as failed_transactions 
        FROM payments T2
        WHERE T2.payment_status = 'Failed' OR T2.payment_status = 'Fraud'
        GROUP BY T2.payment_method;
    """
}

for title, sql_query in test_queries.items():
    print(f"\n⏱️ Running: {title}...")
    start_time = time.time()
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    
    end_time = time.time()
    latency = (end_time - start_time) * 1000 # convert to milliseconds
    
    print(f"📊 Results: {results}")
    print(f"⚡ Execution Latency: {latency:.2f} ms")
    print("-" * 50)

conn.close()
print("\n" + "="*60)
print("✅ STAGE 3 SUCCESS: Hardcore Optimization Complete!")
print("="*60)