"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
import anthropic
from app.services.auth import check_authentication, logout
from app.services.resume import save_resume, get_user_resumes, delete_resume, extract_text_from_file
from app.services.analysis import save_analysis, get_user_analysis_history
from app.config import init_streamlit_config, get_api_key

def run():
    """Main application entry point"""
    init_streamlit_config()
    
    # Check authentication before showing any content
    if not check_authentication():
        return
        
    # Show main application content
    st.title("ApplyAI")
    
    # Add logout button to sidebar
    with st.sidebar:
        if st.button("🚪 Logout", type="primary"):
            logout()
            st.rerun()
    
    # Create two columns
    col1, col2 = st.columns([3, 2])
    
    # Rest of your existing main.py code...
    # (Job posting analysis, resume management, etc.)

if __name__ == "__main__":
    run()