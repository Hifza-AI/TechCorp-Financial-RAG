import os 
import gc
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# 1. Paths Setup
BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
DATA_PATH = os.path.join(BASE_DIR, "data", "pdfs")
DB_PATH = os.path.join(BASE_DIR, "chroma_db")  # Jahan database permanently save hoga

print(f"📁 Checking directory path: {DATA_PATH}")
if not os.path.exists(DATA_PATH):
    print("❌ ERROR: Path exist nahi karta!")
    exit()

# 2. Fast PyMuPDF Loading
print("\n🚀 1. PyMuPDFLoader se PDFs load ho rahi hain...")
loader = DirectoryLoader(
    DATA_PATH,
    glob="**/*.pdf",
    loader_cls=PyMuPDFLoader,
    show_progress=True
)
documents = loader.load()
print(f"✅ Documents load ho gaye! Total Pages: {len(documents)}")

# 3. Text Splitting
print("\n✂️ 2. Text splitting aur chunking shuru...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
chunks = text_splitter.split_documents(documents)
total_chunks = len(chunks)
print(f"🔥 Total Chunks bane hain: {total_chunks}")

# 4. Initialize Local Hugging Face Embedding
print("\n🧠 3. Local Hugging Face Model (`all-MiniLM-L6-v2`) initialize ho raha hai...")
# Yeh model download hoga pehli dafa, phir local cache se chalega
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 5. Safe Batching to prevent laptop from hanging
print("\n📦 4. ChromaDB mein data save ho raha hai via Safe Batching Formula...")

BATCH_SIZE = 2000  # Ek waqt mein sirf 2000 chunks process honge
db = None

for i in range(0, total_chunks, BATCH_SIZE):
    batch_chunks = chunks[i:i + BATCH_SIZE]
    print(f"🔄 Processing batch {i//BATCH_SIZE + 1} / {(total_chunks // BATCH_SIZE) + 1} (Chunks {i} to {min(i + BATCH_SIZE, total_chunks)})...")
    
    if db is None:
        # Pehle batch ke liye database create hoga disk par
        db = Chroma.from_documents(
            documents=batch_chunks,
            embedding=embeddings,
            persist_directory=DB_PATH
        )
    else:
        # Baqi batches isme add hote jayenge
        db.add_documents(documents=batch_chunks)
    
    # 🚨 RAM Cleanup: Har batch ke baad memory flush karna lazmi hai
    del batch_chunks
    gc.collect()

print("\n==============================================")
print(f"🎉 SUCCESS! Saara data permanently `chroma_db/` folder mein save ho gaya!")
print("==============================================")