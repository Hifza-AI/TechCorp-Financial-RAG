import os
from dotenv import load_dotenv
from google import genai

# Apne banaye hue modules ko import karein
# Purane imports ko hata kar ye likhein:
from retrieval.query_router import classify_query  # Agar file ka naam query_router.py hai
from retrieval.sql_agent import get_sql_answer
from retrieval.pdf_agent import get_pdf_answer

# 1. Environment Setup
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("Dost, GOOGLE_API_KEY nahi mili! .env file check karo.")

client = genai.Client(api_key=api_key)

def ask_financial_ai(query):
    print(f"\n🔍 Sawal: {query}")
    
    # 2. Router Decision (Ab ye local hai, 0 API Call)
    try:
        route = classify_query(query)
        print(f"🛣️ Router Decision: {route}")
    except Exception as e:
        print(f"⚠️ Router Error: {e}")
        route = "PDF" # Backup default

    # 3. Agents se data mangwao
    raw_context = ""
    if route == "SQL":
        # GEMINI CALL #1 yahan SQL Agent ke andar hoti hai
        raw_context = get_sql_answer(query)
        
    elif route == "PDF":
        # 0 API Call (Local Vector DB search)
        raw_context = get_pdf_answer(query)
        
    elif route == "HYBRID":
        print("🔄 Fetching both SQL and PDF data...")
        sql_data = get_sql_answer(query)
        pdf_data = get_pdf_answer(query)
        raw_context = f"--- DATABASE NUMBERS ---\n{sql_data}\n\n--- ANNUAL REPORT TEXT ---\n{pdf_data}"

    # 4. FINAL STEP: Raw data ko "Insani" jawab mein badlo
    # GEMINI CALL #2 (Final Answer Generation)
    final_prompt = f"""
You are a Financial Expert AI. 

USER QUESTION: {query}
RAW DATA: {raw_context}

INSTRUCTIONS:
1. Provide a detailed and structured answer.
2. Mention the source of your information (e.g., "According to the financial database..." or "As per the annual report...").
3. If numbers are available, interpret them. 
4. If you used SQL data, explain what the numbers show.
5. Maintain a helpful and professional tone.
"""
    
    try:
        # Gemini-2.5-flash use karein (Fast aur Accurate)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_prompt
        )
        print("\n📜 SYSTEM TRACE & CITATIONS:")
        if route == "SQL" or route == "HYBRID":
            print(f"   🔹 Data Source: SQL Database (financial_data.db)")
        
        if route == "PDF" or route == "HYBRID":
            print(f"   🔹 Data Source: PDF Vector Index (FAISS)")
            # Agar aapne get_pdf_answer mein metadata return karwaya hai toh wo yahan show hoga
            print(f"   🔹 Context Quality: High (Top 10 chunks retrieved)")
        print(f"   🔹 Model Used: Gemini-2.5-Flash")
        # -------------------------------------------------------
        return response.text.strip()
    except Exception as e:
        return f"Synthesis Error: {e}\nRaw Context was: {raw_context}"

# --- APP START ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 TECHCORP FINANCIAL RAG SYSTEM ACTIVE")
    print("="*50)
    
    while True:
        user_input = input("\n💬 Apna sawal likhein (ya 'exit' likhein): ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Allah Hafiz! Phir milenge.")
            break
            
        if not user_input.strip():
            continue

        answer = ask_financial_ai(user_input)
        print("\n💡 AI KA JAWAB:")
        print(answer)
        print("\n" + "-"*50)