import streamlit as st
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any
import time

# Core dependencies
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "10000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "1000"))

# Configure Gemini API
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("⚠️ Please set your GOOGLE_API_KEY in the .env file")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="IntelliDocs AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Custom header */
.custom-header {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}

.custom-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

/* Chat messages */
.user-message {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    padding: 1rem;
    border-radius: 15px;
    margin: 1rem 0;
    margin-left: 20%;
}

.ai-message {
    background: #f8fafc;
    color: #1e293b;
    padding: 1rem;
    border-radius: 15px;
    margin: 1rem 0;
    margin-right: 20%;
    border-left: 4px solid #06b6d4;
}

.source-citation {
    background: rgba(6, 182, 212, 0.1);
    border: 1px solid #06b6d4;
    border-radius: 8px;
    padding: 0.5rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

/* Stats cards */
.stats-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    text-align: center;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

.stats-number {
    font-size: 2rem;
    font-weight: 700;
    color: #6366f1;
    margin-bottom: 0.5rem;
}

.stats-label {
    color: #64748b;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processed_documents' not in st.session_state:
        st.session_state.processed_documents = {}
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]

# Utility functions
def get_pdf_text(pdf_docs):
    """Extract text from PDF files"""
    text = ""
    for pdf_doc in pdf_docs:
        pdf_doc.seek(0)
        try:
            pdf_reader = PdfReader(pdf_doc)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n\n--- Page {page_num + 1} of {pdf_doc.name} ---\n"
                    text += page_text
        except Exception as e:
            st.error(f"Error reading {pdf_doc.name}: {str(e)}")
            continue
    return text

def get_text_chunks(text):
    """Split text into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_text(text)
    return [chunk for chunk in chunks if len(chunk.strip()) > 100]

def get_vector_store(text_chunks):
    """Create vector store from text chunks"""
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
        return vector_store
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return None

def get_conversational_chain():
    """Create the conversational chain"""
    prompt_template = """
    You are IntelliDocs AI, an intelligent document analysis assistant. Answer questions based on the provided context.

    Instructions:
    1. Answer using ONLY the information in the context
    2. If the answer is not in the context, say "The answer is not available in the provided documents"
    3. Provide detailed, well-structured answers
    4. Use bullet points or numbered lists when helpful
    5. Quote relevant parts when necessary

    Context:
    {context}

    Question: {question}

    Answer:
    """
    
    model = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=TEMPERATURE
    )
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def process_question(question):
    """Process user question and return response"""
    if not st.session_state.vector_store:
        return {
            'answer': "Please upload and process documents first.",
            'sources': []
        }
    
    try:
        # Search for relevant documents
        docs = st.session_state.vector_store.similarity_search(question, k=5)
        
        if not docs:
            return {
                'answer': "No relevant information found in the documents.",
                'sources': []
            }
        
        # Generate response
        chain = get_conversational_chain()
        response = chain(
            {"input_documents": docs, "question": question},
            return_only_outputs=True
        )
        
        # Extract sources
        sources = []
        for doc in docs:
            source_info = extract_source_info(doc.page_content)
            if source_info:
                sources.append(source_info)
        
        return {
            'answer': response["output_text"],
            'sources': sources
        }
        
    except Exception as e:
        return {
            'answer': f"Error processing question: {str(e)}",
            'sources': []
        }

def extract_source_info(content):
    """Extract source information from content"""
    lines = content.split('\n')
    for line in lines:
        if '--- Page' in line and 'of' in line:
            try:
                parts = line.split(' of ')
                if len(parts) > 1:
                    filename = parts[1].replace(' ---', '').strip()
                    page_part = parts[0].split('--- Page ')[1].strip()
                    return {
                        'document': filename,
                        'page': page_part
                    }
            except:
                continue
    return None

def validate_pdf_file(uploaded_file):
    """Validate uploaded PDF file"""
    try:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False, f"File too large ({file_size_mb:.1f} MB). Max size: {MAX_FILE_SIZE_MB} MB"
        
        if not uploaded_file.name.lower().endswith('.pdf'):
            return False, "Only PDF files are supported"
        
        # Test PDF reading
        uploaded_file.seek(0)
        try:
            pdf_reader = PdfReader(uploaded_file)
            if len(pdf_reader.pages) == 0:
                return False, "PDF appears to be empty"
        except:
            return False, "Invalid or corrupted PDF file"
        finally:
            uploaded_file.seek(0)
        
        return True, ""
    except Exception as e:
        return False, f"Validation error: {str(e)}"

# Main UI functions
def render_header():
    """Render the application header"""
    st.markdown("""
    <div class="custom-header">
        <h1>🧠 IntelliDocs AI</h1>
        <p>Intelligent Document Analysis & Conversation Platform</p>
    </div>
    """, unsafe_allow_html=True)

def render_chat_interface():
    """Render the chat interface"""
    st.markdown("### 💬 Chat with Your Documents")
    
    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong> {message['content']}
                    <br><small>🕒 {message['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-message">
                    <strong>IntelliDocs AI:</strong><br>
                    {message['content']}
                    <br><small>🕒 {message['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Show sources
                if message.get('sources'):
                    st.markdown("**📚 Sources:**")
                    for source in message['sources']:
                        st.markdown(f"""
                        <div class="source-citation">
                            📄 {source['document']} (Page {source['page']})
                        </div>
                        """, unsafe_allow_html=True)
    
    # Chat input
    user_question = st.text_input(
        "Ask a question about your documents:",
        placeholder="e.g., What are the main findings in the documents?",
        key="chat_input"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚀 Send", key="send_button"):
            if user_question and user_question.strip():
                if not st.session_state.processed_documents:
                    st.error("⚠️ Please upload and process documents first!")
                else:
                    # Add user message
                    user_msg = {
                        'type': 'user',
                        'content': user_question,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.chat_history.append(user_msg)
                    
                    # Process question
                    with st.spinner("🤔 Thinking..."):
                        response_data = process_question(user_question)
                        
                        # Add AI response
                        ai_msg = {
                            'type': 'ai',
                            'content': response_data['answer'],
                            'sources': response_data.get('sources', []),
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.chat_history.append(ai_msg)
                    
                    st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat", key="clear_button"):
            st.session_state.chat_history = []
            st.rerun()

def render_document_management():
    """Render document management interface"""
    st.markdown("### 📚 Document Management")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type="pdf",
        accept_multiple_files=True,
        help="Select multiple PDF files to analyze"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Process Documents", key="process_button"):
            if uploaded_files:
                process_documents(uploaded_files)
            else:
                st.warning("Please select PDF files to process")
    
    with col2:
        if st.button("🗑️ Remove All", key="remove_all_button"):
            st.session_state.processed_documents = {}
            st.session_state.chat_history = []
            st.session_state.vector_store = None
            # Clear saved vector store
            try:
                import shutil
                if os.path.exists("faiss_index"):
                    shutil.rmtree("faiss_index")
            except:
                pass
            st.success("🗑️ All documents removed!")
            st.rerun()
    
    # Display processed documents
    if st.session_state.processed_documents:
        st.markdown("#### 📄 Processed Documents")
        for doc_name, metadata in st.session_state.processed_documents.items():
            with st.expander(f"📄 {doc_name}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Pages", metadata.get('pages', 'N/A'))
                with col2:
                    st.metric("Chunks", metadata.get('chunks', 'N/A'))
                with col3:
                    st.metric("Size", f"{metadata.get('size_mb', 0):.1f} MB")

def process_documents(uploaded_files):
    """Process uploaded documents"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_text_chunks = []
    processed_count = 0
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Validate file
        is_valid, error = validate_pdf_file(uploaded_file)
        if not is_valid:
            st.error(f"❌ {uploaded_file.name}: {error}")
            continue
        
        try:
            # Extract text
            text = get_pdf_text([uploaded_file])
            if not text.strip():
                st.error(f"❌ No text extracted from {uploaded_file.name}")
                continue
            
            # Create chunks
            chunks = get_text_chunks(text)
            if not chunks:
                st.error(f"❌ No valid text chunks from {uploaded_file.name}")
                continue
            
            all_text_chunks.extend(chunks)
            
            # Store metadata
            file_size_mb = uploaded_file.size / (1024 * 1024)
            pdf_reader = PdfReader(uploaded_file)
            pages = len(pdf_reader.pages)
            
            st.session_state.processed_documents[uploaded_file.name] = {
                'pages': pages,
                'chunks': len(chunks),
                'size_mb': round(file_size_mb, 2),
                'processed_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            processed_count += 1
            
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            continue
    
    # Create vector store if we have chunks
    if all_text_chunks:
        status_text.text("Creating vector database...")
        vector_store = get_vector_store(all_text_chunks)
        if vector_store:
            st.session_state.vector_store = vector_store
            status_text.empty()
            progress_bar.empty()
            st.success(f"✅ Successfully processed {processed_count} document(s)!")
        else:
            st.error("❌ Failed to create vector database")
    else:
        status_text.empty()
        progress_bar.empty()
        st.error("❌ No documents were successfully processed")

def render_analytics():
    """Render analytics dashboard"""
    if not st.session_state.processed_documents:
        st.info("📊 Upload documents to see analytics")
        return
    
    st.markdown("### 📊 Analytics Dashboard")
    
    # Calculate stats
    total_docs = len(st.session_state.processed_documents)
    total_pages = sum(doc.get('pages', 0) for doc in st.session_state.processed_documents.values())
    total_chunks = sum(doc.get('chunks', 0) for doc in st.session_state.processed_documents.values())
    total_conversations = len(st.session_state.chat_history) // 2
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total_docs}</div>
            <div class="stats-label">Documents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total_pages}</div>
            <div class="stats-label">Pages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total_chunks}</div>
            <div class="stats-label">Text Chunks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total_conversations}</div>
            <div class="stats-label">Conversations</div>
        </div>
        """, unsafe_allow_html=True)

def render_export():
    """Render export options"""
    if not st.session_state.chat_history:
        st.info("💬 Start a conversation to enable export options")
        return
    
    st.markdown("### 📤 Export Conversation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as JSON"):
            export_data = {
                'session_id': st.session_state.session_id,
                'export_time': datetime.now().isoformat(),
                'documents': list(st.session_state.processed_documents.keys()),
                'chat_history': st.session_state.chat_history
            }
            st.download_button(
                label="💾 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"intellidocs_chat_{st.session_state.session_id}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📝 Export as Text"):
            text_export = f"IntelliDocs AI Chat Export\n"
            text_export += f"Session ID: {st.session_state.session_id}\n"
            text_export += f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            text_export += "=" * 50 + "\n\n"
            
            for message in st.session_state.chat_history:
                if message['type'] == 'user':
                    text_export += f"[{message['timestamp']}] YOU: {message['content']}\n\n"
                else:
                    text_export += f"[{message['timestamp']}] AI: {message['content']}\n\n"
            
            st.download_button(
                label="💾 Download Text",
                data=text_export,
                file_name=f"intellidocs_chat_{st.session_state.session_id}.txt",
                mime="text/plain"
            )

# Main application
def main():
    initialize_session_state()
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        # Navigation
        tab = st.selectbox(
            "Navigate",
            ["💬 Chat", "📚 Documents", "📊 Analytics", "📤 Export"],
            index=0
        )
        
        st.markdown("---")
        
        # Quick info
        if st.session_state.processed_documents:
            st.markdown("### 📈 Quick Stats")
            st.info(f"📄 {len(st.session_state.processed_documents)} documents")
            st.info(f"💬 {len(st.session_state.chat_history)} messages")
        
        st.markdown("---")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        st.info(f"🤖 Model: {MODEL_NAME}")
        st.info(f"🌡️ Temperature: {TEMPERATURE}")
        st.info(f"📏 Chunk Size: {CHUNK_SIZE}")
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.info("💡 Ask specific questions for better results")
        st.info("🔍 Try asking for summaries or comparisons")
        st.info("📊 Check Analytics tab for document stats")
    
    # Main content
    if tab == "💬 Chat":
        render_chat_interface()
    elif tab == "📚 Documents":
        render_document_management()
    elif tab == "📊 Analytics":
        render_analytics()
    elif tab == "📤 Export":
        render_export()
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #64748b; font-size: 0.9rem;'>
        🧠 IntelliDocs AI - Session: {st.session_state.session_id}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
