"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
import PyPDF2
import io
from utils.db import save_resume
from utils.auth import check_auth

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF files"""
    try:
        # Read PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None

def render_resume_section():
    st.markdown("### Resume Management")
    
    uploaded_files = st.file_uploader(
        "Upload Resume(s)",
        type=['pdf'],
        accept_multiple_files=True,
        key='pdf_uploader',
        help="Upload one or more PDF files"
    )
    
    if uploaded_files:
        # Process all new uploads first
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.get('processed_files', {}):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    text = extract_text_from_pdf(uploaded_file)
                    if text:
                        if 'processed_files' not in st.session_state:
                            st.session_state.processed_files = {}
                        # Auto-save on upload
                        if save_resume(st.session_state.user_id, uploaded_file.name, text, uploaded_file.type):
                            st.session_state.processed_files[uploaded_file.name] = {
                                'text': text,
                                'file_type': uploaded_file.type
                            }
                            st.toast(f"✅ Saved {uploaded_file.name}")
        
        # Display all processed files
        if st.session_state.get('processed_files'):
            st.markdown("#### Processed Resumes")
            
            # Create columns for the table header
            cols = st.columns([3, 1])
            cols[0].markdown("**Filename**")
            cols[1].markdown("**Actions**")
            
            st.markdown("---")
            
            # Display each file's info and controls
            for filename, data in st.session_state.processed_files.items():
                cols = st.columns([3, 1])
                
                # Filename
                cols[0].markdown(f"📄 {filename}")
                
                # View/Edit toggle
                if cols[1].button("👁️ View/Edit", key=f"view_{filename}"):
                    st.session_state[f'editing_{filename}'] = not st.session_state.get(f'editing_{filename}', False)
                
                # Show editor if requested
                if st.session_state.get(f'editing_{filename}', False):
                    edited_text = st.text_area(
                        "Edit content",
                        value=data['text'],
                        height=400,
                        key=f"editor_{filename}"
                    )
                    
                    # Auto-save when content changes
                    if edited_text != data['text']:
                        if save_resume(st.session_state.user_id, filename, edited_text, data['file_type']):
                            st.session_state.processed_files[filename]['text'] = edited_text
                            st.toast(f"✅ Changes saved to {filename}")
                
                st.markdown("---")

def run():
    """Main app entry point"""
    st.set_page_config(
        page_title="ApplyAI",
        page_icon="🤖",
        layout="wide"
    )
    
    # Check authentication
    if not check_auth():
        return
        
    # Main app layout
    st.title("ApplyAI")
    
    # Tabs for different sections
    tab1, tab2 = st.tabs(["Resume Management", "Analysis Results"])
    
    with tab1:
        render_resume_section()
        
    with tab2:
        render_analysis_results()

if __name__ == "__main__":
    run()