import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Path fix taake modules dhoond sake
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Environment variables load karein
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("🚀 Step 1: Loading Embedding Model (all-MiniLM-L6-v2)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("🚀 Step 2: Loading FAISS Vector Database...")
DB_PATH = "faiss_index"

try:
    vectorstore = FAISS.load_local(
        DB_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    print("✅ Vector DB Loaded Successfully!")
except Exception as e:
    print(f"❌ Error loading DB: {e}")
    sys.exit()

# --- THE PERMANENT MODEL FIX ---
print("🔍 Detecting the best available Gemini model...")
try:
    # 1. Live list mangwao
    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # 2. Priority check: Pehle 2.5 flash dhoondo (jo kal chal raha tha)
    model_to_use = next((m for m in all_models if "gemini-2.5-flash" in m), None)
    
    # 3. Agar wo nahi mila toh koi bhi 1.5 flash uthao
    if not model_to_use:
        model_to_use = next((m for m in all_models if "gemini-1.5-flash" in m), None)
        
    # 4. Agar kuch bhi na mile toh pehla available model
    if not model_to_use:
        model_to_use = all_models[0]

    print(f"✅ Active Model Found: {model_to_use}")
    
    # Model ko initialize karte waqt explicitly naam dena hai
    model = genai.GenerativeModel(model_name=model_to_use)

except Exception as e:
    print(f"⚠️ Detection failed: {e}. Using fallback...")
    model = genai.GenerativeModel("gemini-1.5-flash") # Direct fallback
# --- END FIX ---

# 3. User Input
query = input("\n💬 Ask your financial question: ")

print("\n🔍 Step 3: Searching relevant chunks in your PDFs...")
docs = vectorstore.similarity_search(query, k=7)
context = "\n\n".join([doc.page_content for doc in docs])

print("🤖 Step 4: Gemini is generating grounded answer...\n")

# 4. RAG Prompt
prompt = f"""
You are a professional Financial AI Assistant. 
Your task is to answer the user's question accurately using ONLY the provided context from the financial reports.

CONTEXT:
{context}

USER QUESTION:
{query}

INSTRUCTIONS:
- If the answer is not in the context, say "I'm sorry, but this information is not available in the provided reports."
- Be concise and professional.
- Use bullet points for financial data if possible.

FINAL ANSWER:
"""

try:
    response = model.generate_content(prompt)
    print("\n" + "="*30)
    print("✨ FINAL AI RESPONSE")
    print("="*30)
    print(response.text)

    print("\n" + "="*30)
    print("📜 CITATIONS (Sources)")
    print("="*30)
    for i, doc in enumerate(docs):
        source_name = doc.metadata.get('source', 'Unknown')
        page_num = doc.metadata.get('page', 'N/A')
        print(f"[{i+1}] Source: {os.path.basename(source_name)} | Page: {page_num}")

except Exception as e:
    print(f"❌ Error during generation: {e}")