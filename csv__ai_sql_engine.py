import os
import sqlite3
import re
from dotenv import load_dotenv
# 🔥 Switching to the official, modern 2026 Google GenAI SDK
from google import genai
from google.genai import types

print("="*60)
print("🤖 STAGE 4: PRODUCTION-GRADE AI TEXT-TO-SQL ENGINE")
print("="*60)

# Load environment configurations
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ Error: GOOGLE_API_KEY env file mein nahi mili!")
    exit()

# Initialize the modern client
client = genai.Client(api_key=API_KEY)
DB_PATH = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG\data\csv\financial_enterprise.db"

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
# 🤖 MODERN GEMINI 2.5 API PIPELINE
# ------------------------------------------------------------
def generate_sql_from_llm(user_question):
    db_schema = get_database_schema()
    
    system_prompt = f"""
    You are an expert financial system DB assistant. Convert natural language questions into raw SQLite queries.
    
    LAWS:
    1. Output ONLY raw executable SQL. Never wrap inside markdown fences like ```sql.
    2. Target the exact 3NF schema attributes provided below.
    3. To prevent resource hogging on 1 Million rows, always append 'LIMIT 5' if not explicitly defined.
    
    SCHEMA STRUCTURE:
    {db_schema}
    """
    
    # Using gemini-2.5-flash for lighting fast text-to-sql translation
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_question,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1 # Low temperature ensures strict structural outputs
        )
    )
    
    generated_sql = response.text.strip()
    if generated_sql.startswith("```"):
        generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
        
    return generated_sql

# ------------------------------------------------------------
# 🏃 LIVE APP ENGINE GATEWAY
# ------------------------------------------------------------
if __name__ == "__main__":
    user_prompt = "Find the top 3 countries with the highest customer spending"
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
                print(f"🏆 Rank {index} | Country: {row[0]} | Total Value: ${row[1]:,.2f}")
        except Exception as e:
            print(f"❌ Execution Failure: {e}")
        finally:
            conn.close()
    else:
        print(f"\n🛡️ Security Status: BLOCKED ❌\nReason: {message}")
        
    print("\n" + "="*60)