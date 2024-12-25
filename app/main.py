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
    """Render resume management section"""
    st.subheader("📄 Resume Management")
    
    # Custom CSS for clean layout
    st.markdown("""
        <style>
            /* Container styling */
            .resume-list {
                margin-top: 1rem;
            }
            
            /* Clean layout for resume items */
            [data-testid="stHorizontalBlock"] {
                background: white;
                padding: 0.25rem 0.5rem;  /* Reduced padding */
                margin: 0.15rem 0;  /* Reduced margin */
                border: 1px solid #f0f0f0;
                border-radius: 4px;
                align-items: center;
                min-height: 2rem;  /* Set minimum height */
            }
            
            [data-testid="stHorizontalBlock"]:hover {
                background: #f8f9fa;
            }
            
            /* Resume name styling */
            [data-testid="stHorizontalBlock"] > div:first-child p {
                margin: 0;
                font-size: 0.85rem;  /* Slightly smaller font */
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                padding-right: 1rem;
                line-height: 1.2;  /* Reduced line height */
            }
            
            /* Button styling */
            [data-testid="stButton"] button {
                padding: 0.15rem 0.3rem;  /* Reduced padding */
                height: 1.5rem;  /* Fixed height */
                min-height: 0;
                width: 1.8rem;  /* Slightly narrower */
                background: transparent;
                border: none;
                color: #666;
                font-size: 0.9rem;  /* Smaller icons */
            }
            
            [data-testid="stButton"] button:hover {
                color: #ff4b4b;
                background: #f0f0f0;
            }
            
            /* Hide file uploader elements */
            .uploadedFile {
                display: none !important;
            }
            
            /* Divider styling */
            hr {
                margin: 1.5rem 0;
            }
            
            /* Expander styling */
            .streamlit-expanderContent {
                padding: 0.5rem 0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Resume list
    resumes = get_user_resumes(st.session_state.user_id)
    
    if not resumes:
        uploaded_file = st.file_uploader(
            "Upload your first resume",
            type=["pdf", "docx", "txt"],
            key="resume_uploader"
        )
    else:
        # Show existing resumes
        st.markdown('<div class="resume-list">', unsafe_allow_html=True)
        for name, content, file_type in resumes:
            cols = st.columns([8, 1, 1])
            
            # Truncate filename if too long
            display_name = name if len(name) < 40 else name[:37] + "..."
            
            # Resume name
            cols[0].markdown(f"📄 {display_name}")
            
            # View button
            if cols[1].button("👁️", key=f"view_{name}", help="View resume content"):
                st.session_state[f"show_{name}"] = True
            
            # Delete button
            if cols[2].button("🗑️", key=f"del_{name}", help="Delete resume"):
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add new resume option
        st.divider()
        uploaded_file = st.file_uploader(
            "Upload another resume",
            type=["pdf", "docx", "txt"],
            key="resume_uploader"
        )
    
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
            print(f"Error uploading resume: {str(e)}")

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
    
    # Render the main page with fixed columns
    render_page()

if __name__ == "__main__":
    run()