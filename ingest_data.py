import os
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = r"C:\Users\riaze\Desktop\TechCorp-Financial-RAG"
DATA_PATH = os.path.join(BASE_DIR, "data", "pdfs")

print(f"📁 Checking directory path: {DATA_PATH}")
if not os.path.exists(DATA_PATH):
    print("❌ ERROR: Path exist nahi karta!")
else:
    print(f"✅ Folder mil gaya! Iske andar {len(os.listdir(DATA_PATH))} subfolders hain.")

print("\n🚀 1. PyMuPDFLoader se 250 PDFs ko JET ki raftar se load kar rahe hain...")

# PyMuPDFLoader lagane se speed 10 guna tez ho jayegi!
loader = DirectoryLoader(
    DATA_PATH,
    glob="**/*.pdf",
    loader_cls=PyMuPDFLoader,
    show_progress=True
)

documents = loader.load()
print(f"\n✅ Documents load ho gaye! Total Pages extracted: {len(documents)}")

if len(documents) > 0:
    print("\n✂️ 2. Text splitting aur chunking shuru ho rahi hai...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_documents(documents)

    print("\n==============================================")
    print(f"🔥 FINAL RESULTS: Total Chunks bane hain 👉 {len(chunks)} 👈")
    print("==============================================")

    if len(chunks) > 0:
        print("\n📝 Sample Chunk 1 ka content:")
        print(chunks[0].page_content[:300])