import os
import sys

# Windows Engine Check Support
try:
    import pysqlite3 as sqlite3
    sys.modules['sqlite3'] = sqlite3
except ImportError:
    import sqlite3

from langchain_community.utilities import SQLDatabase

# Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
DB_PATH = os.path.join(BASE_DIR, "data", "csv", "financial_enterprise.db")

print("="*60)
print("🚀 CLASS 10: INITIALIZING TEXT-TO-SQL AI AGENT ENGINE")
print("="*60)

if not os.path.exists(DB_PATH):
    print(f"❌ Error: Database file nahi mili dost! Path check karo -> {DB_PATH}")
    exit()

# Connect LangChain to our SQLite Database
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

print("✅ LangChain Connected to SQLite Database Successfully!")
print(f"📊 Detected Tables in Database: {db.get_usable_table_names()}")
print("-" * 50)

# Verify Schema Integration
print("🔍 Verifying Sample Table Schema (Products)...")
print(db.get_table_info(table_names=["products"]))
print("-" * 50)

print("\n" + "="*60)
print("✅ CLASS 10 SUCCESS: AI Agent Database Layer is Ready!")
print("💡 Ab hamara database LLM Agent ko apna schema samjhane ke liye ready hai.")
print("="*60)