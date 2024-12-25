"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st

def check_auth():
    # Temporarily move auth check here until we fix imports
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'test_user'
    return True

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
        from components.resume_manager import render_resume_manager
        render_resume_manager()
        
    with tab2:
        from components.analysis_results import render_analysis_results
        render_analysis_results()

if __name__ == "__main__":
    run()