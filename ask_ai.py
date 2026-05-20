import os
import sqlite3
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Environment & API Setup
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ Error: GOOGLE_API_KEY .env file mein nahi mili!")
    exit()

client = genai.Client(api_key=API_KEY)
DB_PATH = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG\data\csv\financial_enterprise.db"

# ------------------------------------------------------------
# 🏗️ DYNAMIC SCHEMA EXTRACTION
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
# 🛡️ STAGE 4: SQL VALIDATION LAYER (Security)
# ------------------------------------------------------------
def validate_sql_query(query_string):
    clean_query = query_string.strip().upper()
    if not clean_query.startswith("SELECT"):
        return False, "SECURITY ALERT: Only reading data (SELECT) is permitted!"
        
    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "REPLACE"]
    for word in forbidden_keywords:
        if re.search(r'\b' + word + r'\b', clean_query):
            return False, f"SECURITY ALERT: Command '{word}' is strictly blocked!"
            
    return True, "Valid"

# ------------------------------------------------------------
# 🔄 MAIN EXECUTION LOOP
# ------------------------------------------------------------
if __name__ == "__main__":
    print("="*60)
    print("🤖 TECHCORP FINANCIAL AI AGENT — INTERACTIVE TERMINAL")
    print("="*60)
    print("💡 Tip: Type 'exit' or 'quit' to close the program.\n")
    
    db_schema = get_database_schema()

    while True:
        user_question = input("\n💬 Enter your financial question: ")
        
        if user_question.lower() in ['exit', 'quit']:
            print("👋 Exiting AI Terminal. Allah Hafiz, dost!")
            break
            
        if not user_question.strip():
            continue
            
        print("🧠 AI is processing your request...")
        
        try:
            # STEP A: Generate SQL using modern SDK
            system_prompt = f"""
            You are an expert financial system DB assistant. Convert natural language questions into raw SQLite queries.
            LAWS:
            1. Output ONLY raw executable SQL. Never wrap inside markdown blocks like ```sql.
            2. Target the exact 3NF schema attributes provided below.
            3. Always append 'LIMIT 5' if not explicitly defined to prevent system heavy load.
            
            SCHEMA STRUCTURE:
            {db_schema}
            """
            
            response_sql = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_question,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0
                )
            )
            generated_sql = response_sql.text.strip()
            
            # Clean up markdown fences if LLM hallucinates
            if generated_sql.startswith("```"):
                generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
                
            print(f"💻 AI Generated SQL: {generated_sql}")
            
            # STEP B: Security Guardrail Check
            is_safe, sec_msg = validate_sql_query(generated_sql)
            if not is_safe:
                print(f"🛡️ Security Status: BLOCKED ❌ ({sec_msg})")
                continue
                
            # STEP C: Run Query on 1M Database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(generated_sql)
            db_results = cursor.fetchall()
            
            # Extract column names dynamically for response synthesis
            column_names = [desc[0] for desc in cursor.description]
            conn.close()
            
            # STEP D: STAGE 6 - RESPONSE SYNTHESIZER (Insani Jawab Layer)
            synthesis_prompt = f"""
            You are an expert Financial Analyst. 
            Given a user's question, the SQL query run, and the raw data from the database, write a clear, professional response for company stakeholders.
            Never show raw lists like [(6378181)]. Convert them into human-readable insights with proper metric labels ($ for currency, counts for absolute numbers).

            Original Question: {user_question}
            SQL Query Run: {generated_sql}
            Columns: {column_names}
            Raw DB Data: {db_results}
            """
            
            response_final = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=synthesis_prompt
            )
            
            print("\n" + "-"*60)
            print(f"🎯 SYSTEM ANSWER:\n{response_final.text.strip()}")
            print("-"*60)
            
        except Exception as e:
            print(f"❌ System Error: {e}")