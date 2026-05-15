import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("Dost, .env file mein API key nahi mili! Check karo.")

client = genai.Client(api_key=api_key)

def classify_query(query):
    """
    User ki query ko analyze karta hai baghair kisi API call ke.
    Faisla karta hai ke data SQL database se aayega, PDF se, ya dono se.
    """
    query_clean = query.lower()

    # 1. SQL Keywords (Jo tumhare column names se match karte hain)
    # Income Statement, Balance Sheet, Cash Flow aur Daily Prices ke keywords
    sql_keywords = [
        "revenue", "profit", "assets", "liabilities", "equity", "inventory", 
        "cash", "receivables", "depreciation", "goodwill", "investments", 
        "debt", "payable", "retained earnings", "shares", "outstanding",
        "operating cashflow", "dividend", "capital expenditures", "ebit", "ebitda",
        "price", "open", "high", "low", "close", "volume", "tax", "income"
    ]

    # 2. PDF Keywords (Jo analysis, risks aur future plans ke liye hain)
    pdf_keywords = [
        "risk", "future", "strategy", "plan", "management", "outlook", 
        "business description", "competitors", "industry trends", "expansion",
        "mission", "vision", "legal", "regulatory", "environmental", "social"
    ]

    # Matching Check
    # Check if any SQL keyword is in the query
    found_sql = any(word in query_clean for word in sql_keywords)
    
    # Check if any PDF keyword is in the query
    found_pdf = any(word in query_clean for word in pdf_keywords)

    # Logic for Routing
    if found_sql and found_pdf:
        return "HYBRID"
    elif found_sql:
        return "SQL"
    elif found_pdf:
        return "PDF"
    else:
        # Agar koi keyword match na ho, toh safe side ke liye PDF (General context) par bhej do
        return "PDF"

# --- Testing Section (Tum chala kar check kar sakte ho) ---
if __name__ == "__main__":
    test_queries = [
        "What was the total revenue last year?",
        "What are the future risks of the company?",
        "Compare the net income with the expansion strategy.",
        "How are you today?"
    ]
    
    for q in test_queries:
        print(f"Query: {q} --> Route: {classify_query(q)}")