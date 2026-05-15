import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# PDFs ka folder path
PDF_FOLDER = "data/pdfs"

documents = []

print("🚀 PDFs load hona shuru ho rahi hain...")

# Check karna ke folder mojood hai ya nahi
if not os.path.exists(PDF_FOLDER):
    print(f"❌ Error: Folder '{PDF_FOLDER}' nahi mila!")
else:
    for file in os.listdir(PDF_FOLDER):
        if file.endswith(".pdf"):
            path = os.path.join(PDF_FOLDER, file)
            print(f"Loading: {file}")
            try:
                loader = PyPDFLoader(path)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"❌ {file} ko load karne mein masla aya: {e}")

    print(f"\n✅ Total Pages Loaded: {len(documents)}")

    # --- Chunking Step ---
    if documents:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = text_splitter.split_documents(documents)

        print(f"🔥 Total Chunks Created: {len(chunks)}")

        # Result Check
        print("\n--- Sample Chunk Metadata ---")
        print(chunks[0].metadata)
    else:
        print("⚠️ Koi document load nahi hua, chunks nahi ban sakay.")