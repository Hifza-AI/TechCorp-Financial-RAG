import os
import sys
from dotenv import load_dotenv

# --- YE LINES MODULE ERROR FIX KARENGI ---
# Is se Python ko pata chalega ke project ka main folder kahan hai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -----------------------------------------

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Import chunks
from ingestion.pdf_loader import chunks

print("🚀 Local HuggingFace Embeddings load ho rahi hain...")

# Small testing batch
small_chunks = chunks

print(f"🔄 {len(small_chunks)} chunks vectors mein convert ho rahe hain...")

# FREE local embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create vector DB
vectorstore = FAISS.from_documents(
    small_chunks,
    embeddings
)

# Save locally
vectorstore.save_local("faiss_index")

print("✅ FAISS Vector DB Successfully Created!")