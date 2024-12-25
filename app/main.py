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
from utils.file_processing import extract_text_from_pdf

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

def truncate_filename(filename, max_length=30):
    """Truncate filename if too long"""
    if len(filename) <= max_length:
        return filename
    name, ext = os.path.splitext(filename)
    return name[:max_length-5] + '...' + ext

def render_resume_section():
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
                        st.session_state.processed_files[uploaded_file.name] = {
                            'text': text,
                            'file_type': uploaded_file.type,
                            'edited': False,
                            'saved': False
                        }
        
        # Display all processed files in a table format
        if st.session_state.processed_files:
            st.markdown("#### Processed Resumes")
            
            # Create columns for the table header
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown("**Filename**")
            cols[1].markdown("**Status**")
            cols[2].markdown("**Preview**")
            cols[3].markdown("**Actions**")
            
            st.markdown("---")
            
            # Display each file's info and controls
            for filename, data in st.session_state.processed_files.items():
                cols = st.columns([3, 1, 1, 1])
                
                # Filename
                cols[0].markdown(f"📄 {filename}")
                
                # Status
                status = "✅ Saved" if data['saved'] else "📝 Edited" if data['edited'] else "New"
                cols[1].markdown(status)
                
                # Preview button
                if cols[2].button("👁️", key=f"preview_{filename}"):
                    st.session_state[f'show_preview_{filename}'] = True
                
                # Edit button
                if cols[3].button("✏️", key=f"edit_{filename}"):
                    st.session_state[f'editing_{filename}'] = True
                
                # Show preview if requested
                if st.session_state.get(f'show_preview_{filename}', False):
                    with st.expander("Preview", expanded=True):
                        st.text(data['text'][:1000] + "..." if len(data['text']) > 1000 else data['text'])
                        if st.button("Close Preview", key=f"close_preview_{filename}"):
                            st.session_state[f'show_preview_{filename}'] = False
                            st.rerun()
                
                # Show editor if requested
                if st.session_state.get(f'editing_{filename}', False):
                    with st.expander("Edit Content", expanded=True):
                        edited_text = st.text_area(
                            "Edit extracted text",
                            value=data['text'],
                            height=400,
                            key=f"editor_{filename}"
                        )
                        
                        col1, col2 = st.columns([1, 4])
                        if col1.button("Save", key=f"save_{filename}"):
                            if save_resume(
                                st.session_state.user_id,
                                filename,
                                edited_text,
                                data['file_type']
                            ):
                                st.session_state.processed_files[filename]['text'] = edited_text
                                st.session_state.processed_files[filename]['edited'] = True
                                st.session_state.processed_files[filename]['saved'] = True
                                st.toast(f"✅ Saved changes to {filename}")
                                st.session_state[f'editing_{filename}'] = False
                                st.rerun()
                        
                        if col2.button("Cancel", key=f"cancel_{filename}"):
                            st.session_state[f'editing_{filename}'] = False
                            st.rerun()
                
                st.markdown("---")
            
            # Batch actions
            if not all(f['saved'] for f in st.session_state.processed_files.values()):
                if st.button("💾 Save All Unsaved"):
                    with st.spinner("Saving all resumes..."):
                        for filename, data in st.session_state.processed_files.items():
                            if not data['saved']:
                                if save_resume(
                                    st.session_state.user_id,
                                    filename,
                                    data['text'],
                                    data['file_type']
                                ):
                                    st.session_state.processed_files[filename]['saved'] = True
                        st.toast("✅ All resumes saved!")
                        st.rerun()

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