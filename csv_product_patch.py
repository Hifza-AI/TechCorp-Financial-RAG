import os
import sqlite3

# Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
DB_PATH = os.path.join(BASE_DIR, "data", "csv", "financial_enterprise.db")

print("="*60)
print("🚀 CLASS 11: PATCHING PRODUCT NAMES FOR TRUE ENTERPRISE REALISM")
print("="*60)

if not os.path.exists(DB_PATH):
    print(f"❌ Error: Database file nahi mili! Path check karo -> {DB_PATH}")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Industry ke mutabiq dynamic names assignment mapping
product_name_mapping = {
    "Electronics": "Enterprise Smart Hardware v2",
    "Computing": "High-Performance Compute Node",
    "Cloud Services": "Enterprise Cloud Infrastructure Instance",
    "Software": "Enterprise Multi-User Software License",
    "Digital Services": "Premium Corporate Digital Ad-Space",
    "Retail": "Bulk Commercial Supplies Pack",
    "Entertainment": "Corporate Media Stream Subscription",
    "Automotive": "Next-Gen Commercial Fleet EV",
    "Financial Services": "Premium Asset Portfolio Management Plan",
    "Payments": "Secure Transaction Gateway Enterprise Suite",
    "Food & Beverages": "Corporate Catering Hospitality Package",
    "Energy": "Clean Energy Wind-Turbine Utility Block"
}

print("🔄 Executing batch SQL updates on products table...")

for category, new_product_name in product_name_mapping.items():
    # Category ke base par saare ajeeb products ke naam real corporate products se replace karo
    cursor.execute("""
        UPDATE products 
        SET product_name = ? 
        WHERE category = ?;
    """, (new_product_name, category))

conn.commit()

print("🔍 Verification Query running...")
cursor.execute("SELECT product_name, category, brand FROM products LIMIT 3;")
rows = cursor.fetchall()

print("\n✨ Updated Sample Data Inside Products Table:")
for row in rows:
    print(f"📦 Product: {row[0]} | 📑 Category: {row[1]} | 👑 Brand: {row[2]}")

print("\n" + "="*60)
print("✅ CLASS 11 SUCCESS: Product Names Aligned with Financial Industries!")
print("="*60)

conn.close()