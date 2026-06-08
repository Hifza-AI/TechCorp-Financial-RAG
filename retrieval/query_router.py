import os
import sys
import sqlite3
import re
from dotenv import load_dotenv
from groq import Groq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Setup AUTOMATIC absolute paths
# 1. Setup AUTOMATIC absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Fallback check: Agar run context badle toh local path check kare
if not os.path.exists(ENV_PATH):
    ENV_PATH = os.path.join(os.getcwd(), ".env")

load_dotenv(dotenv_path=ENV_PATH)

DB_PATH = os.path.join(BASE_DIR, "data", "csv", "financial_enterprise.db")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(f"❌ Error: GROQ_API_KEY nahi mili!")

client = Groq(api_key=GROQ_API_KEY)

print("🧠 Loading Vector Database Layer (Chroma)...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
print("✅ Vector DB Connected Successfully!")

# --- DYNAMIC SCHEMA INTEGRATION ---
def get_db_schema():
    try:
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
    except Exception:
        # Fallback tracking schema if DB file initializing
        return "Table: customers (customer_id, country, loyalty_score), Table: orders (order_id, customer_id, company_id, total_price_usd, profit_usd, order_date), Table: companies (company_id, company_name)"

def run_sql_query(sql):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        return {"status": "success", "data": rows, "columns": columns}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 🚀 METADATA EXTRACTION & ENGINE SAFEGUARDS ---
def extract_metadata_filters(user_question):
    """
    Advanced Enterprise Feature: Extracts strict metadata targets 
    from the question to avoid ChromaDB vector overlap.
    """
    # Simple regex parsing for years between 2010 and 2030
    year_match = re.search(r'\b(20\d{2})\b', user_question)
    target_year = year_match.group(1) if year_match else None
    
    # Standard portfolio company mappings
    companies_list = ['MCDONALD', 'MICROSOFT', 'GOOGLE', 'ALPHABET', 'IBM', 'JPMORGAN', 'GOLDMAN', 'APPLE', 'TESLA', 'SAMSUNG', 'NVIDIA']
    target_company = None
    
    for comp in companies_list:
        if re.search(r'\b' + comp + r'\b', user_question.upper()):
            target_company = comp if comp != 'ALPHABET' else 'GOOGLE'
            break
            
    meta_filter = {}
    if target_year:
        meta_filter["year"] = str(target_year)
    # Flexible keyword match helper for nested dictionaries
    return meta_filter

# --- CORE BACKEND SUB-ENGINES ---
def execute_sql_pipeline(user_question):
    print("💻 [SQL Sub-Engine] Generating Executable SQL Query...")
    sql_prompt = f"""
    Convert this question into a raw SQLite query based on this Schema: {get_db_schema()}
    
    LAWS FOR STABLE SQL:
    1. Output ONLY raw executable SQL string. No markdown blocks (```sql), no explanations.
    2. Always append LIMIT 5 unless specified otherwise.
    3. Use explicit short table aliases and joins (o for orders, c for companies, p for payments, s for shipping, cu for customers).
    4. DATE FILTERING: Always use 'orders.order_date' for any year/date filters. Never apply date functions on IDs.
    5. Always use LIKE with wildcards for text fields (e.g., LIKE '%Completed%').
    
    Question: {user_question}
    """
    sql_query = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": sql_prompt}],
        temperature=0.0
    ).choices[0].message.content.strip()
    
    sql_query = re.sub(r"```sql|```", "", sql_query).strip()
    
    # Injection corrections
    if "o.order_id" in sql_query and "STRFTIME" in sql_query:
        sql_query = sql_query.replace("o.order_id", "o.order_date")
    elif "orders.order_id" in sql_query and "STRFTIME" in sql_query:
        sql_query = sql_query.replace("orders.order_id", "orders.order_date")
        
    print(f"💻 [SQL Sub-Engine] Executing SQL: {sql_query}")
    db_res = run_sql_query(sql_query)
    return db_res, sql_query

def execute_pdf_pipeline(user_question):
    print("📂 [PDF Sub-Engine] Fetching Corporate Knowledge Document Chunks...")
    
    # Smart Pre-Filtering Check
    filters = extract_metadata_filters(user_question)
    
    if filters:
        print(f"🎯 Applying Strict Chroma Search Metadata Filter: {filters}")
        # Search chunks using metadata tracking injection
        docs = vector_db.similarity_search(user_question, k=6, filter=filters)
    else:
        docs = vector_db.similarity_search(user_question, k=6)
        
    context_blocks = []
    citations = []
    for doc in docs:
        context_blocks.append(doc.page_content)
        source_file = os.path.basename(doc.metadata.get('source', 'Unknown_Document.pdf'))
        page_num = doc.metadata.get('page', doc.metadata.get('page_number', 'N/A'))
        citations.append(f"📄 Source: {source_file} | Page: {page_num}")
        
    return "\n\n".join(context_blocks), list(set(citations))

# --- ADVANCED TRI-MODE ROUTER ---
def route_and_query(user_question):
    print("\n🧠 Agent is analyzing the query route...")
    
    router_prompt = f"""
    Route this query into exactly ONE of these three modes:
    - 'SQL_ONLY': If the query requires math calculations, metrics, counts, sums, or table data lookups.
    - 'PDF_ONLY': If the query asks for qualitative text analysis, business strategy, risks, challenges or corporate policies from documents.
    - 'HYBRID': If the query combines both.
    
    CRITICAL RULE: If the query asks for qualitative analysis like 'strategic drivers', 'risk factors', or 'roadmaps' without asking for exact numeric database transaction records, route strictly to 'PDF_ONLY'.
    
    Output ONLY one word: either 'SQL_ONLY', 'PDF_ONLY', or 'HYBRID'.
    User Question: {user_question}
    """
    
    route_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": router_prompt}],
        temperature=0.0
    ).choices[0].message.content.strip()
    
    if "SQL_ONLY" in route_response.upper(): route_response = "SQL_ONLY"
    elif "PDF_ONLY" in route_response.upper(): route_response = "PDF_ONLY"
    else: route_response = "HYBRID"
        
    print(f"🎯 Route Decided by AI: **{route_response}**")
    
    # MODE 1: PURE SQL
    if route_response == "SQL_ONLY":
        db_res, sql_query = execute_sql_pipeline(user_question)
        if db_res["status"] == "error" or not db_res.get("data"):
            return {
                "answer": f"⚠️ Structured Data Informer: No matching rows found or query adjusted. (Executed: {sql_query})", 
                "citations": None, "type": "SQL_ONLY", "sql": sql_query
            }
            
        synthesis_prompt = f"Create a clear markdown financial summary table or statement from this data. Data: {db_res['data']}\nQuestion: {user_question}"
        final_ans = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": synthesis_prompt}]
        ).choices[0].message.content
        return {"answer": final_ans, "citations": None, "type": "SQL_ONLY", "sql": sql_query}

    # MODE 2: PURE PDF (ROBUST FILTER MATCHING)
    elif route_response == "PDF_ONLY":
        context, citations = execute_pdf_pipeline(user_question)
        if not context.strip():
            context = "Warning: Strict metadata match returned empty context. Loosening metadata constraints on the vector layer..."
            # Auto fallback to broad search if strict filter was too tight
            vector_db_clean = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
            fallback_docs = vector_db_clean.similarity_search(user_question, k=6)
            context = "\n\n".join([d.page_content for d in fallback_docs])
            citations = list(set([f"📄 Source: {os.path.basename(d.metadata.get('source', 'Doc.pdf'))} | Page: {d.metadata.get('page', 'N/A')}" for d in fallback_docs]))

        pdf_prompt = f"""
        You are an Elite Financial RAG Assistant. Synthesize a comprehensive answer using the text context provided below.
        CRITICAL: Rely ONLY on the clear facts from the text. Do not invent details outside the provided years.
        
        Context:
        {context}
        
        Question: {user_question}
        """
        final_ans = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": pdf_prompt}], temperature=0.1
        ).choices[0].message.content
        return {"answer": final_ans, "citations": citations, "type": "PDF_ONLY", "sql": None}

    # MODE 3: FIXED HYBRID RESPONSE FUSION
    else:
        db_res, sql_query = execute_sql_pipeline(user_question)
        
        sql_data_context = ""
        if db_res["status"] == "error" or not db_res.get("data"):
            sql_data_context = "No major structured data metrics returned for this query parameter."
        else:
            sql_data_context = f"Columns={db_res.get('columns')}, Data={db_res.get('data')}"
        
        pdf_context, citations = execute_pdf_pipeline(user_question)
        
        fusion_prompt = f"""
        You are an Elite Principal Financial Systems Analyst. Create a unified executive briefing report that brings together transactional database metrics and document text insights.
        
        Structured SQL Data Context:
        {sql_data_context}
        
        Unstructured PDF Document Context:
        {pdf_context}
        
        User Question: {user_question}
        """
        final_ans = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": fusion_prompt}],
            temperature=0.1
        ).choices[0].message.content
        
        return {"answer": final_ans, "citations": citations, "type": "HYBRID_FUSION", "sql": sql_query}

# --- INTERACTIVE LOOP ---
if __name__ == "__main__":
    print("\n============================================================")
    print("🚀 TECHCORP SMART TRI-MODE AGENT (PORTFOLIO PRO EDITION)")
    print("============================================================")
    
    while True:
        user_in = input("\n💬 Ask anything (SQL or PDF info): ")
        if user_in.lower() in ['exit', 'quit']:
            break
        if not user_in.strip():
            continue
            
        res = route_and_query(user_in)
        print("\n------------------------------------------------------------")
        print(f"🎯 AGENT ANSWER ({res['type']} MODE):")
        
        if res.get("sql"):
            print(f"💻 Executed SQL Query: {res['sql']}\n")
            
        print(res["answer"])
        
        if res.get("citations"):
            print("\n📚 DYNAMIC PDF CITATIONS:")
            for cit in res["citations"]:
                print(f"   {cit}")
        print("------------------------------------------------------------")