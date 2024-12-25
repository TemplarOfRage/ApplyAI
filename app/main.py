"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
from .components.resume_manager import render_resume_manager
from .components.analysis_results import render_analysis_results
from .utils.auth import check_auth

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
        render_resume_manager()
        
    with tab2:
        render_analysis_results()

if __name__ == "__main__":
    run()