import pandas as pd
import sqlite3
import os

# Raste (Paths) set karein
BASE_DIR = os.getcwd()
CSV_FOLDER = os.path.join(BASE_DIR, "data", "raw_csv")
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "financial_data.db")

def start_ingestion():
    # Agar database folder nahi hai toh bana do
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    # Database se dosti (connection) karein
    conn = sqlite3.connect(DB_PATH)
    print("🔗 SQL Database se connection ban gaya hai...")

    # Har file ko table mein convert karein
    files = {
        'googl_income_statement.csv': 'income_statement',
        'googl_balance_sheet.csv': 'balance_sheet',
        'googl_cash_flow_statement.csv': 'cash_flow',
        'googl_daily_prices.csv': 'stock_prices'
    }

    for file_name, table_name in files.items():
        path = os.path.join(CSV_FOLDER, file_name)
        if os.path.exists(path):
            print(f"📥 {file_name} ko database mein dal raha hoon...")
            df = pd.read_csv(path)
            # Data ko SQL mein convert karein
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"✅ {table_name} table ready hai!")
        else:
            print(f"❌ Error: {file_name} nahi mili!")

    conn.close()
    print(f"\n🚀 Mubarak ho! Database ban gaya: {DB_PATH}")

if __name__ == "__main__":
    start_ingestion()