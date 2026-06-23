import sqlite3
import pandas as pd
import os
from google import genai
from dotenv import load_dotenv

# API Setup
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

def get_sql_answer(user_query):
    ### 1. AI ko database ka structure samjhana (Updated Prompt)
    prompt = f"""
    You are a Financial SQL Expert. 
    We have an SQLite database 'financial_data.db' with these tables and EXACT column names:

    - income_statement: (fiscalDateEnding, reportedCurrency, grossProfit, totalRevenue, costOfRevenue, operatingIncome, netIncome, etc.)
    - balance_sheet: (fiscalDateEnding, totalAssets, totalLiabilities, totalShareholderEquity, etc.)
    - cash_flow: (fiscalDateEnding, operatingCashflow, capitalExpenditures, netIncome, etc.)
    - stock_prices: (date, "1. open", "2. high", "3. low", "4. close", "5. volume")

    CRITICAL RULES:
    1. Always use double quotes for stock_prices columns, e.g., SELECT "4. close" FROM stock_prices.
    2. The column names for stock prices are EXACTLY as shown above (with numbers and dots).
    3. Output ONLY the SQL code. Do not use markdown or explanations.
    
    Task: Convert this user question into a valid SQLite query: {user_query}
    """
    
    # 2. GEMINI CALL #1: SQL generate karwana
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Latest model for better SQL
            contents=prompt
        )
        
        # SQL ko saaf karna
        sql_query = response.text.strip().replace('```sql', '').replace('```', '').split(';')[0] + ';'
        print(f"🛠️ AI Generated SQL: {sql_query}")

        # 3. Database Connection
        # Make sure 'database/financial_data.db' path sahi ho
        db_path = "database/financial_data.db"
        if not os.path.exists(db_path):
             return "Error: Database file nahi mili! Path check karein."

        conn = sqlite3.connect(db_path)
        
        # Query chalana
        result = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        if result.empty:
            return "Database mein is sawal ka koi data nahi mila."
            
        # Data ko string format mein wapas bhejna (Main RAG ke liye)
        return result.to_string(index=False)
        
    except Exception as e:
        return f"SQL Error: {str(e)}"

# Testing (sirf checking ke liye)
if __name__ == "__main__":
    test_q = "What was the total revenue and net income?"
    print(get_sql_answer(test_q))