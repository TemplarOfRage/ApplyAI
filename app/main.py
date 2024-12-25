"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
import anthropic
from app.services.auth import check_authentication, logout
from app.services.resume import save_resume, get_user_resumes, delete_resume, extract_text_from_file, init_database
from app.services.analysis import save_analysis, get_user_analysis_history, analyze_job_posting, extract_text_from_url
from app.config import init_streamlit_config, get_api_key, render_config_sidebar
import uuid

def render_page():
    """Render the main page with fixed columns"""
    # Create two main columns with fixed layout
    left_col, right_col = st.columns([6, 4], gap="large")
    
    # Render job analysis section in left column
    with left_col:
        render_job_analysis_section()
    
    # Render resume section in right column
    with right_col:
        render_resume_section()

def render_job_analysis_section():
    """Render job analysis section"""
    st.subheader("📝 Job Posting Analysis")
    
    url_input = st.text_input(
        "Job Posting URL",
        placeholder="Paste a job posting URL here (optional)"
    )
    
    job_post = st.text_area(
        "Or paste job posting text",
        height=300,
        placeholder="Paste the job description here to analyze it..."
    )
    
    # Get resumes for analysis check
    resumes = get_user_resumes(st.session_state.user_id)
    has_resume = bool(resumes)
    has_job_post = bool(url_input or job_post)
    
    # Show single consolidated message if either requirement is missing
    if not (has_resume and has_job_post):
        st.warning("⚠️ Please upload a resume & job posting to begin an analysis")
        
    analyze_button = st.button(
        "Analyze",
        type="primary",
        disabled=not (has_resume and has_job_post)
    )

def render_resume_section():
    """Render resume management in sidebar"""
    # Upload section
    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx", "txt"],
        key="resume_uploader"
    )
    
    st.divider()
    
    # Resume list
    resumes = get_user_resumes(st.session_state.user_id)
    if resumes:
        for name, content, file_type in resumes:
            cols = st.columns([3, 1, 1])
            
            # Truncate filename if too long
            display_name = name if len(name) < 25 else name[:22] + "..."
            
            # Resume name
            cols[0].markdown(f"📄 {display_name}")
            
            # View button
            if cols[1].button("👁️", key=f"view_{name}"):
                st.session_state[f"show_{name}"] = True
            
            # Delete button
            if cols[2].button("🗑️", key=f"del_{name}"):
                if delete_resume(st.session_state.user_id, name):
                    st.rerun()
            
            # Show content if requested
            if st.session_state.get(f"show_{name}", False):
                with st.expander("", expanded=True):
                    st.text_area("", value=content, height=200, 
                               disabled=True, label_visibility="collapsed")
                    if st.button("Hide", key=f"hide_{name}"):
                        del st.session_state[f"show_{name}"]
                        st.rerun()
    
    # Handle file upload
    if uploaded_file:
        try:
            content = extract_text_from_file(uploaded_file)
            if content and save_resume(st.session_state.user_id, 
                                    uploaded_file.name, 
                                    content, 
                                    uploaded_file.type):
                st.rerun()
        except Exception as e:
            st.error("Failed to process resume. Please try again.")
    
    # Logout button at bottom of sidebar
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout"):
        del st.session_state.user_id
        st.rerun()

def render_analysis_history():
    """Render analysis history section"""
    st.divider()
    st.subheader("📊 Analysis History")
    history = get_user_analysis_history(st.session_state.user_id)
    
    if not history:
        st.info("No analysis history yet")
    else:
        for job_post, analysis, timestamp in history:
            with st.expander(f"Analysis from {timestamp}"):
                st.text_area("Job Post", value=job_post, height=100, disabled=True)
                st.markdown("### Analysis")
                st.markdown(analysis)

def run():
    """Main entry point for the application"""
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    st.title("ApplyAI")
    
    # Sidebar for resume management
    with st.sidebar:
        st.header("📄 Resume Management")
        render_resume_section()
    
    # Main content area with fixed columns
    main_container = st.container()
    with main_container:
        col1, col2 = st.columns([2, 1])
        
        # Job Analysis section (left column)
        with col1:
            render_job_analysis_section()
        
        # Analysis History (right column)
        with col2:
            st.header("📚 Analysis History")
            render_analysis_history()

def render_sidebar():
    """Render the configuration sidebar"""
    st.sidebar.title("⚙️ Configuration")
    
    # Add your sidebar configuration options here
    st.sidebar.selectbox(
        "Language Model",
        ["GPT-4", "GPT-3.5"],
        index=0,
        help="Select the AI model to use for analysis"
    )
    
    st.sidebar.slider(
        "Response Length",
        min_value=100,
        max_value=1000,
        value=400,
        step=100,
        help="Adjust the length of the AI response"
    )
    
    # Add any other configuration options you need
    st.sidebar.divider()
    
    # Add version info at bottom of sidebar
    st.sidebar.markdown("---")
    st.sidebar.caption("ApplyAI v1.0.0")

if __name__ == "__main__":
    run()