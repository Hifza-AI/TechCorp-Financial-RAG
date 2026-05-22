import sqlite3

# 🎯 FIX: Folder ka sahi path de diya hamne yahan
db_path = "data/csv/financial_enterprise.db" 

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("📊 TABLES IN DATABASE:", tables)

print("\n🔎 COLUMNS DETAILS:")
for table in tables:
    table_name = table[0]
    print(f"\n📋 Table: {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()