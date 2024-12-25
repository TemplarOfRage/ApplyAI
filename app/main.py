"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st

def check_auth():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'test_user'
    return True

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