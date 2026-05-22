import streamlit as st
import sys
import os

# AUTOMATIC Absolute Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# 🎯 SAFE IMPORT INJECTION: Agar retrieval folder ke andar hai toh wahan se bhi path pick karega
try:
    from query_router import route_and_query
except ImportError:
    # Agar direct nahi mili, toh python ko 'retrieval' folder ka rasta dikhao
    sys.path.append(os.path.join(BASE_DIR, "retrieval"))
    from query_router import route_and_query
# 🏗️ STREAMLIT PAGE CONFIGURATION
st.set_page_config(
    page_title="TechCorp Financial Hybrid-RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 CUSTOM CSS FOR ENTERPRISE LOOK
st.markdown("""
    <style>
    .main-title {
        font-size: 38px !important;
        font-weight: 700 !important;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 16px !important;
        color: #556B2F;
        margin-bottom: 25px;
    }
    .status-tag {
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# 🏢 SIDEBAR CONTROL PANEL
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2761/2761118.png", width=80)
    st.markdown("### 🛠️ System Dashboard")
    st.info("⚡ **Engine Status:** Active\n\n🦾 **Core LLM:** Llama-3.3-70b-Versatile\n\n📊 **Relational Layer:** 1M SQLite Rows\n\n📂 **Vector Store:** ChromaDB (SEC 10-K Files)")
    st.markdown("---")
    st.caption("Developed by Group No 8 | Emerson University Multan")

# 🏛️ MAIN HERO SECTION
st.markdown("<div class='main-title'>🧠 TechCorp Financial Multi-Modal Hybrid-RAG</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Seamlessly Blending 1-Million Relational Sales Records with Unstructured Corporate Knowledge Documents</div>", unsafe_allow_html=True)

# 💬 CHAT REPOSITORY INITIALIZATION (State Management)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🔄 BUTTON TO CLEAR STREAMLIT MEMORY CACHE
if st.button("🧹 Clear Chat History & Cache"):
    st.session_state.chat_history = []
    st.cache_data.clear()
    st.success("Cache cleared successfully!")
    st.rerun()

st.markdown("---")

# 📥 DISPLAY HISTORICAL MESSAGES
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])
        
        # Historical Expanders backup display if data exists
        if chat["role"] == "assistant":
            if chat.get("sql"):
                with st.expander("💻 Executed SQL String Verification"):
                    st.code(chat["sql"], language="sql")
            if chat.get("citations"):
                with st.expander("📚 Source Report Document Citations"):
                    for citation in chat["citations"]:
                        st.markdown(f"- {citation}")

# 📥 LIVE USER CHAT BOX INPUT
user_query = st.chat_input("Ask about sales trends, profit analytics, or company strategic risk factors...")

if user_query:
    # Display user's question immediately
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Trigger the full architecture backend with a spinner animation
    with st.chat_message("assistant"):
        with st.spinner("🤖 Architectural Router is processing and analyzing query execution..."):
            try:
                # Fire query to our newly optimized route_and_query function
                backend_response = route_and_query(user_query)
                
                response_text = backend_response["answer"]
                route_mode = backend_response["type"]
                executed_sql = backend_response.get("sql")
                retrieved_citations = backend_response.get("citations")
                
                # Print the core structural text response
                st.markdown(response_text)
                
                # 💻 CONDITION 1: If SQL data or Hybrid Mode was triggered, reveal the exact raw code
                if executed_sql:
                    with st.expander("💻 Executed SQL String Verification"):
                        st.code(executed_sql, language="sql")
                        
                # 📚 CONDITION 2: If PDF or Hybrid Mode was triggered, list out precise citations
                if retrieved_citations:
                    with st.expander("📚 Source Report Document Citations"):
                        for citation in retrieved_citations:
                            st.markdown(f"- {citation}")
                            
                # Save whole transaction block into history tracking
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response_text,
                    "sql": executed_sql,
                    "citations": retrieved_citations
                })
                
            except Exception as error:
                st.error(f"❌ Pipeline Interface Error: {str(error)}")