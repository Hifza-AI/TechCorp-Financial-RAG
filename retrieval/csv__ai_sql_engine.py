import os
import sqlite3
import re
from dotenv import load_dotenv
from groq import Groq

print("="*60)
print("🤖 PRODUCTION-GRADE AI TEXT-TO-SQL ENGINE (FLEXIBLE)")
print("="*60)

# Load environment configurations
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    print("❌ Error: GROQ_API_KEY env file mein nahi mili!")
    exit()

# Initialize official Groq Client
client = Groq(api_key=API_KEY)

# AUTOMATIC Absolute Path Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "csv", "financial_enterprise.db")

# ------------------------------------------------------------
# 🏗️ DYNAMIC SCHEMA INJECTION
# ------------------------------------------------------------
def get_database_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    schema_text = ""
    for table_name, schema_sql in tables:
        if table_name != 'sqlite_sequence':
            schema_text += f"\nTable: {table_name}\n{schema_sql}\n"
    return schema_text

# ------------------------------------------------------------
# 🛡️ SQL VALIDATION LAYER
# ------------------------------------------------------------
def validate_sql_query(query_string):
    clean_query = query_string.strip().upper()
    if not clean_query.startswith("SELECT"):
        return False, "SECURITY ALERT: Only reading data is permitted!"
        
    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "REPLACE"]
    for word in forbidden_keywords:
        if re.search(r'\b' + word + r'\b', clean_query):
            return False, f"SECURITY ALERT: Operational command '{word}' blocked!"
            
    return True, "Valid Query"

# ------------------------------------------------------------
# 🤖 SMART GROQ LLM PIPELINE
# ------------------------------------------------------------
def generate_sql_from_llm(user_question):
    db_schema = get_database_schema()
    
    # Clean, Smart and Flexible System Prompt
    system_prompt = f"""
    You are an expert financial system Database Assistant executing raw queries on a 1-Million row SQLite database.
    Convert natural language questions into executable SQLite code.
    
    🚫 ZERO TOLERANCE RULES - NEVER DISOBEY:
    1. Output ONLY the raw executable SQL query string. Never wrap it inside markdown syntax, backticks, or code fences.
    2. Always use explicit short table aliases (e.g., o for orders, c for companies, p for payments, s for shipping, cu for customers).
    3. To prevent resource hogging on 1 Million records, always append 'LIMIT 5' to the end of the query unless a limit is specified.
    
    ⚠️ COLUMN BINDING DIRECTIVES:
    - PROFIT: Always use `orders.profit_usd` (Never use total_price_usd for profit calculations).
    - REVENUE/SALES: Always use `orders.total_price_usd`.
    - DATE/YEAR: Always use `orders.order_date` for any date filters. Never use STRFTIME on text IDs like order_id.
    - DELIVERY STATUS: Always use `shipping.delivery_status`.
    - PAYMENT STATUS: Always use `payments.payment_status`.
    - Use LIKE operators (e.g., LIKE '%Completed%') for text filters to avoid formatting mismatches.

    ACTUAL TABLE STRUCTURES:
    {db_schema}
    """
    
    # 🎯 FIX: Using consistent 'llama-3.3-70b-versatile' model
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.0,
        max_tokens=300
    )
    
    generated_sql = response.choices[0].message.content.strip()
    generated_sql = re.sub(r"```sql|```", "", generated_sql).strip()
        
    # 🎯 THE ULTIMATE FORCE FIX INJECTION
    if "T1.order_id" in generated_sql and "STRFTIME" in generated_sql:
        generated_sql = generated_sql.replace("T1.order_id", "T1.order_date")
    elif "orders.order_id" in generated_sql and "STRFTIME" in generated_sql:
        generated_sql = generated_sql.replace("orders.order_id", "orders.order_date")
    elif "o.order_id" in generated_sql and "STRFTIME" in generated_sql:
        generated_sql = generated_sql.replace("o.order_id", "o.order_date")
        
    return generated_sql

# ------------------------------------------------------------
# 🏃 LIVE APP ENGINE GATEWAY
# ------------------------------------------------------------
if __name__ == "__main__":
    user_prompt = "What are the total sales generated in the year 2023, and which company performed the best?"
    print(f"\n🗣️ User Question: '{user_prompt}'")
    
    sql_code = generate_sql_from_llm(user_prompt)
    print(f"🤖 Generated SQL:\n{sql_code}")
    
    is_safe, message = validate_sql_query(sql_code)
    
    if is_safe:
        print("\n🛡️ Security Status: PASSED ✅")
        print("⚡ Hitting 1 Million records relational layer...")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(sql_code)
            rows = cursor.fetchall()
            print(f"\n📊 Dynamic Analytical Report:")
            for index, row in enumerate(rows, start=1):
                print(f"🏆 Row {index} Result: {row}")
        except Exception as e:
            print(f"❌ Execution Failure: {e}")
        finally:
            conn.close()
    else:
        print(f"\n🛡️ Security Status: BLOCKED ❌\nReason: {message}")
        
    print("\n" + "="*60)