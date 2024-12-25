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

def render_job_posting_section():
    st.markdown("""
        <style>
            /* Custom expander styles */
            .streamlit-expanderHeader {
                background-color: #f8f9fa;
                border: 1px solid #eee;
                border-radius: 4px;
                padding: 0.5rem !important;
            }
            .streamlit-expanderHeader:hover {
                background-color: #f0f2f6;
            }
            .streamlit-expanderContent {
                border: 1px solid #eee;
                border-top: none;
                border-radius: 0 0 4px 4px;
                padding: 1rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Job Posting URL input
    job_url = st.text_input("Job Posting URL", placeholder="Paste a job posting URL here (optional)")

    # Job posting text area
    job_text = st.text_area("Or paste job posting text", placeholder="Paste the job description here to analyze it...")

    # Custom questions in an expander
    with st.expander("➕ Add Custom Application Questions (Optional)", expanded=False):
        custom_questions = st.text_area(
            "Add any custom application questions",
            placeholder="Enter each question on a new line...",
            help="These questions will be analyzed along with your resume"
        )

    # Get current resumes
    resumes = get_user_resumes(st.session_state.user_id)
    has_resumes = bool(resumes)
    has_job_content = bool(job_url or job_text)

    # Create columns for button and message
    col1, col2 = st.columns([1, 4])

    # Always show the button in the first column
    analyze_disabled = not (has_resumes and has_job_content)
    if col1.button("Analyze", disabled=analyze_disabled, type="primary", use_container_width=True):
        if has_resumes and has_job_content:
            # Your existing analysis logic here
            analyze_job_posting(job_url, job_text, custom_questions)
    
    # Show status message in the second column
    if analyze_disabled:
        if not has_resumes:
            col2.info("⚠️ Upload a resume to get started")
        elif not has_job_content:
            col2.info("⚠️ Add a job posting to analyze")

def render_resume_section():
    """Render resume management section"""
    st.subheader("📄 Resume Management")
    
    # Initialize session state for edit panels
    if 'edit_states' not in st.session_state:
        st.session_state.edit_states = {}
    
    # Update styles to be more compact
    st.markdown("""
        <style>
            /* Table styles */
            .resume-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 0.5rem;
            }
            .resume-table th {
                padding: 0.5rem;
                color: #666;
                font-weight: 500;
                border-bottom: 1px solid #eee;
                text-align: center !important;
            }
            .resume-table th:first-child {
                text-align: left !important;
            }
            /* Center icons */
            div[data-testid="column"] {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
            }
            div[data-testid="column"]:first-child {
                justify-content: flex-start !important;
            }
            /* Remove button styling */
            .stButton > button,
            .stDownloadButton > button {
                background: none !important;
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
                box-shadow: none !important;
            }
            /* Delete confirmation styles */
            .delete-confirm {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 12px;
                margin: 8px 0;
                width: fit-content;
            }
            .delete-buttons {
                display: flex;
                gap: 12px;
                margin-top: 12px;
            }
            .delete-buttons button {
                min-height: 32px !important;
                padding: 4px 12px !important;
            }
            .delete-button button {
                background-color: #ff4b4b !important;
                color: white !important;
            }
            .cancel-button button {
                background-color: #f0f2f6 !important;
                color: #333 !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize delete confirmation state (but don't set it automatically)
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = None
    
    # Clear delete confirmation when uploading new file
    if 'uploader_key' in st.session_state:
        st.session_state.delete_confirmation = None
    
    # Get current resumes
    resumes = get_user_resumes(st.session_state.user_id)
    
    if resumes:
        # Create table header
        st.markdown("""
            <table class="resume-table">
                <thead>
                    <tr>
                        <th style="width: 70%">Name</th>
                        <th style="width: 10%; text-align: center">Edit</th>
                        <th style="width: 10%; text-align: center">Download</th>
                        <th style="width: 10%; text-align: center">Delete</th>
                    </tr>
                </thead>
            </table>
        """, unsafe_allow_html=True)
        
        for idx, (name, content, file_type) in enumerate(resumes):
            cols = st.columns([7, 1, 1, 1])
            
            # Truncate filename if too long
            display_name = name if len(name) < 40 else name[:37] + "..."
            
            with cols[0]:
                st.markdown(f'<div class="file-name"><span class="file-icon">📄</span>{display_name}</div>', unsafe_allow_html=True)
            
            # Edit button
            edit_key = f"edit_{idx}_{hash(name)}"
            if cols[1].button("✏️", key=f"edit_btn_{idx}"):
                st.session_state.edit_states[edit_key] = not st.session_state.edit_states.get(edit_key, False)
                st.rerun()
            
            # Download button
            file_content = get_resume_file(st.session_state.user_id, name)
            if file_content:
                cols[2].download_button(
                    "⬇️",
                    file_content,
                    file_name=name,
                    mime=file_type,
                )
            
            # Delete button - direct delete
            if cols[3].button("🗑️", key=f"del_btn_{idx}"):
                if delete_resume(st.session_state.user_id, name):
                    st.rerun()
            
            # Show edit panel if requested
            if st.session_state.edit_states.get(edit_key, False):
                st.markdown('<div class="edit-panel">', unsafe_allow_html=True)
                
                edited_content = st.text_area(
                    "Edit extracted text:",
                    value=content,
                    height=300,
                    key=f"content_{idx}_{hash(name)}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Changes", key=f"save_{idx}", type="primary"):
                        update_resume_content(st.session_state.user_id, name, edited_content)
                        del st.session_state.edit_states[edit_key]
                        st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_{idx}", type="secondary"):
                        del st.session_state.edit_states[edit_key]
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Add divider before uploader
    st.divider()
    
    # File uploader section
    uploaded_file = st.file_uploader(
        "Upload another resume" if resumes else "Upload your first resume",
        type=["pdf", "docx", "txt"],
        key=f"resume_uploader_{st.session_state.get('uploader_key', 0)}",
        label_visibility="collapsed"
    )
    
    # Handle file upload
    if uploaded_file is not None:
        try:
            content, file_content = extract_text_from_file(uploaded_file)
            if content and save_resume(
                st.session_state.user_id,
                uploaded_file.name,
                content,
                uploaded_file.type,
                file_content
            ):
                st.session_state['uploader_key'] = st.session_state.get('uploader_key', 0) + 1
                st.rerun()
        except Exception as e:
            st.error("Failed to process resume. Please try again.")
            print(f"Error uploading resume: {str(e)}")

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