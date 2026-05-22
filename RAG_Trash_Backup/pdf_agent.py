import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Embeddings ko function se bahar nikal diya taake har call pe model load na ho (Fast speed!)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_pdf_answer(query):
    # FAISS Index path
    DB_PATH = "faiss_index"
    
    if not os.path.exists(DB_PATH):
        return "Error: FAISS index folder nahi mila! Pehle PDF process karein."

    try:
        vector_db = FAISS.load_local(
            DB_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        
        # Search karein (k=5 is good for detailed context)
        docs = vector_db.similarity_search(query, k=10)
        
        # Context ko clean format mein join karna
        context = "\n\n".join([doc.page_content for doc in docs])
        
        return context

    except Exception as e:
        return f"PDF Search Error: {e}"