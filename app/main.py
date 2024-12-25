"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
import anthropic
from app.services.auth import check_authentication, logout
from app.services.resume import save_resume, get_user_resumes, delete_resume, extract_text_from_file, init_database
from app.services.analysis import save_analysis, get_user_analysis_history, analyze_job_posting, extract_text_from_url
from app.config import init_streamlit_config, get_api_key, render_config_sidebar

def render_job_analysis_section(col1, system_prompt, analysis_prompt, temperature):
    """Render job analysis section"""
    with col1:
        st.subheader("📝 Job Posting Analysis")
        
        # Check if user has any resumes
        resumes = get_user_resumes(st.session_state.user_id)
        
        url_input = st.text_input(
            "Job Posting URL",
            placeholder="Paste a job posting URL here (optional)"
        )
        
        job_post = st.text_area(
            "Or paste job posting text",
            height=300,
            placeholder="Paste the job description here to analyze it..."
        )
        
        if url_input:
            with st.spinner("Extracting content from URL..."):
                url_content = extract_text_from_url(url_input)
                if url_content:
                    job_post = url_content
                    st.success("Content extracted from URL!")
        
        if not resumes:
            st.warning("⚠️ Please upload a resume first to enable analysis")
            st.button("Analyze", type="primary", disabled=True)
        else:
            if st.button("Analyze", type="primary"):
                if not job_post:
                    st.error("Please provide a job posting (either via URL or text)")
                    return
                    
                with st.spinner("Analyzing job posting..."):
                    try:
                        analysis = analyze_job_posting(job_post, system_prompt, analysis_prompt, temperature)
                        st.success("Analysis complete!")
                        st.markdown(analysis)
                        
                        # Save analysis to history
                        save_analysis(st.session_state.user_id, job_post, analysis)
                        
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")

def render_resume_section(col2):
    """Render resume management section"""
    with col2:
        st.subheader("📄 Your Resumes")
        
        # Hide the default file uploader UI elements and improve layout
        st.markdown("""
            <style>
                /* Hide the uploaded file info */
                .uploadedFile {
                    display: none !important;
                }
                
                /* Make the upload area more compact */
                .stFileUploader > div {
                    padding: 0.5rem !important;
                }
                
                /* Improve button layout */
                .stButton button {
                    padding: 0.25rem 0.5rem !important;
                    font-size: 0.8rem !important;
                    min-height: 0 !important;
                    height: 2em !important;
                    line-height: 1 !important;
                    width: auto !important;
                    flex-shrink: 0 !important;
                }
                
                /* Ensure columns stay within bounds */
                .row-widget.stHorizontal {
                    width: 100% !important;
                    max-width: 100% !important;
                    overflow: hidden !important;
                }
                
                /* Make resume name truncate with ellipsis */
                .resume-name {
                    white-space: nowrap !important;
                    overflow: hidden !important;
                    text-overflow: ellipsis !important;
                    max-width: 200px !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx", "txt"],
            key="resume_uploader"
        )
        
        if uploaded_file is not None:
            try:
                content = extract_text_from_file(uploaded_file)
                if content:
                    success = save_resume(
                        st.session_state.user_id,
                        uploaded_file.name,
                        content,
                        uploaded_file.type
                    )
                    if success:
                        st.session_state.resume_uploader = None
                        st.rerun()
            except Exception as e:
                print(f"Error processing upload: {str(e)}")
        
        st.divider()
        render_saved_resumes()

def render_saved_resumes():
    """Render saved resumes section"""
    st.subheader("Saved Resumes")
    resumes = get_user_resumes(st.session_state.user_id)
    
    if not resumes:
        st.info("No resumes uploaded yet")
    else:
        for name, content, file_type in resumes:
            # Use a container for better layout control
            with st.container():
                col1, col2, col3 = st.columns([5, 1, 1])
                
                with col1:
                    st.markdown(f"""
                        <div class="resume-name" style="padding: 0.5rem 0;">
                            📄 {name}
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("View", key=f"view_{name}", use_container_width=True):
                        st.session_state[f"show_{name}"] = True
                
                with col3:
                    if st.button("Delete", key=f"del_{name}", use_container_width=True):
                        if delete_resume(st.session_state.user_id, name):
                            # Clear any associated session state
                            if f"show_{name}" in st.session_state:
                                del st.session_state[f"show_{name}"]
                            st.rerun()
            
            # Show content if button was clicked
            if st.session_state.get(f"show_{name}", False):
                with st.expander("Resume Content", expanded=True):
                    st.text_area("", value=content, height=200, 
                               disabled=True, label_visibility="collapsed")
                    if st.button("Hide", key=f"hide_{name}"):
                        del st.session_state[f"show_{name}"]
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
    render_job_analysis_section(col1, system_prompt, analysis_prompt, temperature)
    render_resume_section(col2)
    render_analysis_history()

if __name__ == "__main__":
    run()