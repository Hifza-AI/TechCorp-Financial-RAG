import os
import sqlite3
import re
from dotenv import load_dotenv
# Naya lightweight client standard open-source models ke liye
from google import genai 

# 1. Environment & Setup
load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_KEY:
    print("❌ Error: GROQ_API_KEY .env file mein nahi mili!")
    exit()

# Hum Groq console ko direct hit karenge using standard OpenAI/Groq structures
from openai import OpenAI
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_KEY
)

DB_PATH = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG\data\csv\financial_enterprise.db"

def get_database_schema():
    return """
    Table: customers
    Columns: customer_id (TEXT PRIMARY KEY), gender (TEXT), age (INTEGER), country (TEXT), loyalty_score (REAL)

    Table: companies
    Columns: company_id (INTEGER PRIMARY KEY), company_name (TEXT)

    Table: orders
    Columns: order_id (INTEGER PRIMARY KEY), customer_id (TEXT), company_id (INTEGER), total_price_usd (REAL)

    Table: payments
    Columns: payment_id (INTEGER PRIMARY KEY), order_id (INTEGER), payment_status (TEXT), payment_method (TEXT)
    """

def validate_sql_query(query_string):
    clean_query = query_string.strip().upper()
    if not clean_query.startswith("SELECT"):
        return False, "SECURITY ALERT: Only reading data (SELECT) is permitted!"
    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "REPLACE"]
    for word in forbidden_keywords:
        if re.search(r'\b' + word + r'\b', clean_query):
            return False, f"SECURITY ALERT: Command '{word}' is strictly blocked!"
    return True, "Valid"

if __name__ == "__main__":
    print("="*60)
    print("🚀 TECHCORP FINANCIAL AI AGENT — ULTRA-FAST GROQ LAYER")
    print("="*60)
    print("💡 Tip: Type 'exit' or 'quit' to close the program.\n")
    
    db_schema = get_database_schema()

    while True:
        user_question = input("\n💬 Enter your financial question: ")
        
        if user_question.lower() in ['exit', 'quit']:
            print("👋 Allah Hafiz, dost!")
            break
            
        if not user_question.strip():
            continue
            
        print("🧠 Llama-3 (Groq) is processing your request...")
        
        try:
            # STEP A: Generate SQL using Llama 3 70B (Industry Standard)
            system_prompt = f"""
            You are an expert financial database assistant. Convert natural language questions into raw SQLite queries.
            LAWS:
            1. Output ONLY raw executable SQL query string. Never wrap inside markdown blocks like ```sql or include text.
            2. Target the exact schema: {db_schema}
            3. CRITICAL: You must always include the proper 'FROM' clause and explicitly SELECT all columns requested by the user. Do not assume 'customer_name' exists; use 'customer_id', 'gender', 'age', 'country', and 'loyalty_score' for customer details.
            4. Always append 'LIMIT 5' to prevent heavy load.
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0
            )
            generated_sql = response.choices[0].message.content.strip()
            
            if generated_sql.startswith("```"):
                generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
                
            print(f"💻 AI Generated SQL: {generated_sql}")
            
            # STEP B: Security Check
            is_safe, sec_msg = validate_sql_query(generated_sql)
            if not is_safe:
                print(f"🛡️ Security Status: BLOCKED ❌ ({sec_msg})")
                continue
                
            # STEP C: Run Query on 1M Database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(generated_sql)
            db_results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            conn.close()
            
            # STEP D: Response Synthesizer
            synthesis_prompt = f"""
            You are an expert Financial Analyst. Write a clear, professional analytical response.
            Convert raw lists into clean human-readable insights with proper metric labels ($ for currency).

            Original Question: {user_question}
            Columns: {column_names}
            Raw DB Data: {db_results}
            """
            
            response_final = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": synthesis_prompt}]
            )
            
            print("\n" + "-"*60)
            print(f"🎯 SYSTEM ANSWER:\n{response_final.choices[0].message.content.strip()}")
            print("-"*60)
            
        except Exception as e:
            print(f"❌ System Error: {e}")