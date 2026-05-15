import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
import config  # Jo config file tumne abhi banayi

# Apne modules ko import karein
from retrieval.query_router import classify_query
from retrieval.sql_agent import get_sql_answer
from retrieval.pdf_agent import get_pdf_answer

# 1. Setup & Page Config
load_dotenv()
# Sidebar for System Status & Modular Sources
with st.sidebar:
    st.title("🤖 System Control")
    st.success("RAG Engine Active")
    
    st.markdown("---")
    st.subheader("📁 Connected Sources")
    st.info(f"DB: {config.DB_PATH.split('/')[-1]}")
    st.info(f"PDF Folder: {config.PDF_FOLDER}")

    # --- NAYA CODE YAHAN SE SHURU ---
    st.markdown("---")
    st.subheader("📤 Upload New PDF")
    uploaded_file = st.file_uploader("File select karein", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        save_path = os.path.join(config.PDF_FOLDER, uploaded_file.name)
        if not os.path.exists(config.PDF_FOLDER):
            os.makedirs(config.PDF_FOLDER)
            
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"Uploaded: {uploaded_file.name}")
    # --- NAYA CODE YAHAN KHATAM ---

    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# 2. Initialize Gemini Client
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# 3. Chat Interface
st.title("📊 TechCorp Financial Research Hub")
st.caption("Ask questions about Stock Prices, Financial Statements, or Annual Reports.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani chats dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Main Logic
if user_input := st.chat_input("Apna sawal yahan likhein..."):
    # User message display
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data sources..."):
            # A. Router Decision
            route = classify_query(user_input)
            
            # B. Data Retrieval
            sql_data, pdf_data = "", ""
            if route in ["SQL", "HYBRID"]:
                sql_data = get_sql_answer(user_input)
            if route in ["PDF", "HYBRID"]:
                pdf_data = get_pdf_answer(user_input)
            
            raw_context = f"SQL: {sql_data}\nPDF: {pdf_data}"

            # C. Synthesis (Final Answer)
            final_prompt = f"User Question: {user_input}\nContext: {raw_context}\nInstructions: Provide a professional financial analysis with sources."
            
            response = client.models.generate_content(
                model=config.PRIMARY_MODEL,
                contents=final_prompt
            )
            answer = response.text

            # D. UI Display with Tabs for Traceability
            st.markdown(answer)
            
            # Ye raha wo modular "Source View" jo tumne kaha tha
            with st.expander("🔍 View System Trace & Citations"):
                tab1, tab2 = st.tabs(["📊 SQL Data", "📜 PDF Context"])
                with tab1:
                    if sql_data:
                        st.code(sql_data, language="sql")
                    else:
                        st.write("No SQL data used for this query.")
                with tab2:
                    if pdf_data:
                        st.write(pdf_data)
                    else:
                        st.write("No PDF context used for this query.")
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
