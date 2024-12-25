"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
from services.auth import check_authentication, logout
from services.resume import (
    get_user_resumes, 
    delete_resume, 
    save_resume,
    extract_text_from_file,
    get_resume_file,
    update_resume_content
)
from services.analysis import save_analysis, get_user_analysis_history
from config import init_streamlit_config
import anthropic
import base64
import tempfile
import os
from utils.analyze import analyze_resume_for_job
from utils.errors import AnalysisError
from components.analysis_results import render_analysis_results

def render_analyze_button(job_url, job_text, custom_questions):
    """Separate function just for the analyze button"""
    has_job = bool(job_url or job_text)
    has_resume = bool(st.session_state.get('resumes', []))
    
    col1, col2 = st.columns([1, 4])
    
    analyze_clicked = col1.button(
        "Analyze",
        key="analyze_button_separate",
        disabled=not (has_job and has_resume),
        type="primary",
        use_container_width=True
    )
    
    if not has_resume:
        col2.info("⚠️ Upload a resume to get started")
    elif not has_job:
        col2.info("⚠️ Add a job posting to analyze")
    
    if analyze_clicked and has_job and has_resume:
        with st.spinner("Analyzing..."):
            try:
                job_content = f"{job_url}\n\n{job_text}\n\n{custom_questions}"
                
                # Ensure resumes is a list of tuples
                resumes = st.session_state.resumes
                if not isinstance(resumes, list):
                    resumes = [resumes]
                
                # Get analysis
                response = analyze_resume_for_job(resumes, job_content)
                st.session_state.analysis_results = response
                
                # Store analysis for each valid resume
                for resume in resumes:
                    if isinstance(resume, (tuple, list)) and len(resume) >= 2:
                        render_analysis_results(
                            response,
                            st.session_state.user_id,
                            resume[0],  # resume name
                            job_content
                        )
                
                st.success("Analysis complete!")
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

def render_job_posting_section():
    # Job inputs
    job_url = st.text_input("Job Posting URL", placeholder="Paste a job posting URL here (optional)")
    job_text = st.text_area("Or paste job posting text", placeholder="Paste the job description here to analyze it...")
    
    with st.expander("➕ Add Custom Application Questions (Optional)", expanded=False):
        custom_questions = st.text_area(
            "Add any custom application questions",
            placeholder="Enter each question on a new line...",
            help="These questions will be analyzed along with your resume"
        )

    # Simple conditions
    has_job = bool(job_url or job_text)
    has_resume = bool(st.session_state.get('resumes', []))
    
    # Button with analysis
    col1, col2 = st.columns([1, 4])
    
    if col1.button(
        "Analyze",
        disabled=not (has_job and has_resume),
        key="basic_analyze_button",
        use_container_width=True
    ):
        if has_job and has_resume:
            with st.spinner("Analyzing your resume against the job posting..."):
                try:
                    # Get the first resume
                    resume = st.session_state.resumes[0]
                    resume_content = resume[1]  # Get content from tuple
                    
                    # Combine job content
                    job_content = job_text
                    if job_url:
                        job_content = f"URL: {job_url}\n\n{job_content}"
                    if custom_questions:
                        job_content += f"\n\nCustom Questions:\n{custom_questions}"
                    
                    # Get analysis
                    response = analyze_resume_for_job(resume_content, job_content)
                    
                    # Store and display results
                    st.session_state['analysis_results'] = response
                    st.success("Analysis complete!")
                except AnalysisError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
    
    # Helper message
    if not has_resume:
        col2.info("⚠️ Upload a resume to get started")
    elif not has_job:
        col2.info("⚠️ Add a job posting to analyze")
    
    # Show results if available
    if 'analysis_results' in st.session_state:
        render_analysis_results(st.session_state.analysis_results)

def render_resume_section():
    # Initialize resume list in session state if it doesn't exist
    if 'resumes' not in st.session_state:
        st.session_state.resumes = get_user_resumes(st.session_state.user_id)
    
    uploaded_files = st.file_uploader(
        "Upload Resume(s)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        key='resume_uploader'
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                # Debug info
                st.write(f"DEBUG - Processing file: {uploaded_file.name}")
                st.write(f"DEBUG - File type: {uploaded_file.type}")
                
                # Extract text
                content = extract_text_from_file(uploaded_file)
                
                if content:
                    # If content is a tuple, get the text content
                    if isinstance(content, tuple):
                        content = content[1] if len(content) > 1 else str(content)
                    
                    st.write(f"DEBUG - Content type: {type(content)}")
                    st.write(f"DEBUG - Content length: {len(content)}")
                    
                    # Save to database using positional arguments
                    if save_resume(
                        st.session_state.user_id,
                        uploaded_file.name,
                        content,
                        uploaded_file.type
                    ):
                        st.success(f"Successfully uploaded: {uploaded_file.name}")
                        # Refresh resumes in session state
                        st.session_state.resumes = get_user_resumes(st.session_state.user_id)
                    else:
                        st.error(f"Failed to save {uploaded_file.name}")
                else:
                    st.error(f"No content extracted from {uploaded_file.name}")
                    
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                import traceback
                st.write("DEBUG - Full error:", traceback.format_exc())

def run():
    """Main entry point for the application"""
    # Initialize configuration
    init_streamlit_config()
    
    # Check authentication first
    if not check_authentication():
        return
        
    st.title("ApplyAI")
    
    # Create a fixed container for the entire layout
    with st.container():
        # Create two main columns with fixed layout
        job_col, resume_col = st.columns([6, 4], gap="large")
        
        # Job Analysis section in fixed container
        with job_col:
            render_job_posting_section()
        
        # Resume section in scrollable container
        with resume_col:
            render_resume_section()

if __name__ == "__main__":
    run()