import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
DB_PATH = os.path.join(BASE_DIR, "chroma_db")

print("🔄 Database se connect ho raha hai...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Database ko load karein (bina naya data dale)
db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

# Total documents/chunks ka count maloom karein
collection = db._collection
total_count = collection.count()

print("\n==============================================")
print(f"📊 DATABASE REPORT:")
print(f"✅ Total Chunks in ChromaDB: {total_count}")
print("==============================================")

if total_count == 131209:
    print("🔥 PERFECT! Ek ek chunk sahi salamat save ho chuka hai!")
else:
    print("🤔 Count thoda alag hai, check karna parega.")