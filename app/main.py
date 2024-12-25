"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
import anthropic
from app.services.auth import check_authentication, logout
from app.services.resume import save_resume, get_user_resumes, delete_resume, extract_text_from_file, init_database
from app.services.analysis import save_analysis, get_user_analysis_history, analyze_job_posting, extract_text_from_url
from app.config import init_streamlit_config, get_api_key, render_config_sidebar

def render_job_analysis_section(col1):
    """Render job analysis section"""
    with col1:
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
        
        # Show analyze button with appropriate state
        if not has_resume:
            st.warning("⚠️ Please upload a resume first to enable analysis")
        if not has_job_post:
            st.info("ℹ️ Please provide a job posting to analyze")
            
        analyze_button = st.button(
            "Analyze",
            type="primary",
            disabled=not (has_resume and has_job_post)
        )

def render_resume_section(col2):
    """Render resume management section"""
    with col2:
        st.subheader("📄 Resume Management")
        
        # Custom CSS for clean layout
        st.markdown("""
            <style>
                /* Clean layout for resume items */
                .resume-item {
                    display: flex;
                    align-items: center;
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    border: 1px solid #eee;
                    border-radius: 4px;
                }
                
                .resume-name {
                    flex-grow: 1;
                    font-size: 0.9rem;
                    margin-right: 1rem;
                }
                
                .resume-actions {
                    display: flex;
                    gap: 0.5rem;
                }
                
                .icon-button {
                    background: none;
                    border: none;
                    cursor: pointer;
                    padding: 0.3rem;
                    border-radius: 4px;
                    transition: background-color 0.2s;
                }
                
                .icon-button:hover {
                    background-color: #f0f2f6;
                }
                
                /* Hide file uploader elements when file is selected */
                .uploadedFile {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Resume list
        resumes = get_user_resumes(st.session_state.user_id)
        
        # Upload section
        if not resumes:
            uploaded_file = st.file_uploader(
                "Upload your first resume",
                type=["pdf", "docx", "txt"],
                key="resume_uploader"
            )
        else:
            # Show existing resumes first
            for name, content, file_type in resumes:
                st.markdown(f"""
                    <div class="resume-item">
                        <div class="resume-name">📄 {name}</div>
                        <div class="resume-actions">
                            <button class="icon-button" title="View Resume" 
                                    onclick="document.getElementById('view_{name}').click()">
                                👁️
                            </button>
                            <button class="icon-button" title="Delete Resume" 
                                    onclick="document.getElementById('del_{name}').click()">
                                🗑️
                            </button>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Hidden buttons for functionality
                if st.button("", key=f"view_{name}", help="View resume"):
                    st.session_state[f"show_{name}"] = True
                if st.button("", key=f"del_{name}", help="Delete resume"):
                    if delete_resume(st.session_state.user_id, name):
                        st.rerun()
                
                # Show content if requested
                if st.session_state.get(f"show_{name}", False):
                    with st.expander("Resume Content", expanded=True):
                        st.text_area("", value=content, height=200, 
                                   disabled=True, label_visibility="collapsed")
                        if st.button("Hide", key=f"hide_{name}"):
                            del st.session_state[f"show_{name}"]
                            st.rerun()
            
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
                    st.session_state.resume_uploader = None
                    st.rerun()
            except Exception as e:
                st.error(f"Error uploading resume: {str(e)}")

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
    """Main application entry point"""
    init_streamlit_config()
    
    if not check_authentication():
        return
        
    st.title("ApplyAI")
    
    # Render configuration sidebar and get settings
    system_prompt, analysis_prompt, temperature = render_config_sidebar()
    
    # Add logout button to sidebar
    with st.sidebar:
        if st.button("🚪 Logout", type="primary"):
            logout()
            st.rerun()
    
    # Create main layout
    col1, col2 = st.columns([3, 2])
    
    # Render main sections
    render_job_analysis_section(col1)
    render_resume_section(col2)
    render_analysis_history()

if __name__ == "__main__":
    run()