import os
import sqlite3
import re
from dotenv import load_dotenv
from groq import Groq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Setup AUTOMATIC absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
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

# --- CORE BACKEND ENGINES ---

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

def get_db_schema():
    return """
    Table: customers -> Columns: customer_id, gender, age, country, loyalty_score
    Table: companies -> Columns: company_id, company_name (Values: 'Samsung', 'Apple', 'Nvidia', 'Tesla', 'Microsoft', 'JPMorgan Chase', 'Goldman Sachs', etc.)
    Table: orders -> Columns: order_id, customer_id, company_id, total_price_usd, profit_usd, order_date
    Table: payments -> Columns: payment_id, order_id, payment_status ('Completed', 'Pending', 'Failed'), payment_method ('Credit Card', 'PayPal', 'Debit Card', 'Apple Pay', 'Bank Transfer')
    Table: shipping -> Columns: shipping_id, order_id, shipping_method, shipping_cost_usd, delivery_days, delivery_status
    """

def execute_sql_pipeline(user_question):
    print("💻 [SQL Sub-Engine] Generating Executable SQL Query...")
    sql_prompt = f"""
    Convert this question into a raw SQLite query based on this Schema: {get_db_schema()}
    
    LAWS FOR STABLE SQL:
    1. Output ONLY raw executable SQL string. No markdown blocks (```sql), no explanations.
    2. Always append LIMIT 5 unless specified otherwise.
    3. Use explicit table aliases and joins (e.g., o for orders, c for companies, p for payments, s for shipping, cu for customers).
    4. DATE FILTERING: Always use 'orders.order_date' for any year/date filters. Never apply date functions on IDs.
    5. For text filters like payment_status, delivery_status or payment_method, always use 'LIKE' with wildcards (e.g., LIKE '%Completed%').
    
    Question: {user_question}
    """
    sql_query = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": sql_prompt}],
        temperature=0.0
    ).choices[0].message.content.strip()
    
    sql_query = re.sub(r"```sql|```", "", sql_query).strip()
    
    # Force fix mechanism for common date mistakes
    if "T1.order_id" in sql_query and "STRFTIME" in sql_query:
        sql_query = sql_query.replace("T1.order_id", "T1.order_date")
    elif "orders.order_id" in sql_query and "STRFTIME" in sql_query:
        sql_query = sql_query.replace("orders.order_id", "orders.order_date")
        
    print(f"💻 [SQL Sub-Engine] Executing SQL: {sql_query}")
    db_res = run_sql_query(sql_query)
    return db_res, sql_query

def execute_pdf_pipeline(user_question):
    print("📂 [PDF Sub-Engine] Fetching Corporate Knowledge Document Chunks...")
    
    # 🎯 REMOVED THE STRICT METADATA FILTER THAT BLOCKED SEARCHES
    # Open semantic search retrieves context much more intelligently without crashing
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
    - 'SQL_ONLY': If the query requires mathematical calculations, metrics, counts, sums, or table data lookups.
    - 'PDF_ONLY': If the query asks for qualitative text analysis, business strategy, risks, challenges or policies from documents.
    - 'HYBRID': If the query combines both (requires database metrics AND document strategies).
    
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
            
        synthesis_prompt = f"Create a clear and concise financial summary from this data. Data: {db_res['data']}\nQuestion: {user_question}"
        final_ans = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": synthesis_prompt}]
        ).choices[0].message.content
        return {"answer": final_ans, "citations": None, "type": "SQL_ONLY", "sql": sql_query}

    # MODE 2: PURE PDF (RELAXED & INTELLIGENT)
    elif route_response == "PDF_ONLY":
        context, citations = execute_pdf_pipeline(user_question)
        pdf_prompt = f"""
        You are a helpful Financial AI Assistant. Synthesize a comprehensive answer using the corporate text context provided below. 
        Be detailed, thorough, and structure your answer with clear bullet points.
        
        Context:
        {context}
        
        Question: {user_question}
        """
        final_ans = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": pdf_prompt}], temperature=0.2
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
            temperature=0.2
        ).choices[0].message.content
        
        return {"answer": final_ans, "citations": citations, "type": "HYBRID_FUSION", "sql": sql_query}

# --- INTERACTIVE LOOP ---
if __name__ == "__main__":
    print("\n============================================================")
    print("🚀 TECHCORP SMART TRI-MODE AGENT (CLEAN & FLEXIBLE)")
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