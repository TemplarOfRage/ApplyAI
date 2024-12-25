import streamlit as st
from utils.file_processing import extract_text_from_pdf
from utils.db import save_resume

def render_resume_manager():
    """Component for managing resume uploads and edits"""
    st.markdown("### Resume Management")
    
    # File uploader that stays at the top
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
        
        # Display all processed files in a table format
        if st.session_state.processed_files:
            st.markdown("#### Processed Resumes")
            
            # Create columns for the table header
            cols = st.columns([3, 1])
            cols[0].markdown("**Filename**")
            cols[1].markdown("**Actions**")
            
            st.markdown("---")
            
            # Display each file's info and controls
            for filename, data in st.session_state.processed_files.items():
                cols = st.columns([3, 1])
                
                # Filename and preview toggle in first column
                cols[0].markdown(f"📄 {filename}")
                
                # Single action button in second column
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