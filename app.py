"""
============================================================
U-SIOP APPLICATION - Main Entry Point
Umbrella Corporation Security-Integrated Onboarding Protocol
============================================================
"""

from employees import generate_employee_data
from dotenv import load_dotenv
import streamlit as st 
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import logging
from assistant import OnboardingAssistant
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE
from langchain_groq import ChatGroq
from ui import initialize_ui, apply_custom_style


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================
def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="U-SIOP Terminal | Umbrella Corp.",
        page_icon="☂️",
        layout="wide",
        initial_sidebar_state="expanded"
    )


# ============================================================
# DATA INITIALIZATION FUNCTIONS
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_user_data():
    """Generate and cache employee data"""
    return generate_employee_data(1)[0]


@st.cache_resource(ttl=3600, show_spinner=False)
def init_vector_store(pdf_path: str):
    """
    Initialize the vector store with PDF documents.
    Uses optimized chunk settings for RAG retrieval.
    """
    try:
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        # Split documents with optimized settings
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=400
        )
        splits = text_splitter.split_documents(docs)
        
        # Initialize embeddings
        embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create vector store with persistence
        persistent_path = ".\\data\\vectorstore"
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding_function,
            persist_directory=persistent_path,
        )
        
        return vectorstore
        
    except Exception as e:
        logging.error(f"Error initializing vector store: {str(e)}")
        return None


# ============================================================
# MAIN APPLICATION
# ============================================================
def main():
    """Main application entry point"""
    
    # Load environment variables
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Configure page (must be first Streamlit command)
    configure_page()
    
    # Initialize data
    user_data = get_user_data()
    vector_store = init_vector_store("data/Umbrella_Employee_Handbook.pdf")
    
    # Initialize session state
    if "employee" not in st.session_state:
        st.session_state.employee = user_data
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = user_data.get("employee_id", "default")
    
    # Initialize LLM
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    # Initialize Assistant
    assistant = OnboardingAssistant(
        system_prompt=SYSTEM_PROMPT,
        llm=llm,
        message_history=st.session_state.messages,
        employee_information=st.session_state.employee,
        vector_store=vector_store,
        session_id=st.session_state.session_id,
    )
    
    # Initialize and render the U-SIOP Terminal UI
    initialize_ui(
        employee=st.session_state.employee,
        messages=st.session_state.messages,
        assistant=assistant,
        welcome_message_template=WELCOME_MESSAGE
    )


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()