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
    
    custom_questions = st.text_area(
        "Custom application questions (Optional)",
        height=100
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
    
    if analyze_button and job_post and has_resume:
        with st.spinner("Analyzing your fit..."):
            # Get all user's resumes
            user_resumes = get_user_resumes(st.session_state.user_id)
            combined_resume_context = "\n---\n".join(
                content for _, content, _ in user_resumes
            )
            
            try:
                client = anthropic.Client(
                    api_key=st.secrets["ANTHROPIC_API_KEY"]
                )
                
                prompt = f"""Job Post: {job_post}
                Resume Context: {combined_resume_context}
                Custom Questions: {custom_questions if custom_questions else 'None'}
                
                Please analyze this application following the format:
                
                ## Initial Assessment
                ## Match Analysis
                ## Resume Strategy
                ## Tailored Resume
                ## Custom Responses
                ## Follow-up Actions"""

                message = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                analysis = message.content[0].text
                save_analysis(st.session_state.user_id, job_post, analysis)
                
                # Display analysis
                st.markdown(analysis)
                
            except Exception as e:
                st.error(f"Analysis error: {str(e)}")

def render_resume_section():
    """Render resume management section"""
    st.subheader("📄 Resume Management")
    
    # Initialize session state for edit panels
    if 'edit_states' not in st.session_state:
        st.session_state.edit_states = {}
    
    # Update styles to REALLY remove all boxes and improve alignment
    st.markdown("""
        <style>
            /* Table styles */
            .resume-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 1rem;
            }
            .resume-table th {
                padding: 0.75rem;
                color: #666;
                font-weight: 500;
                border-bottom: 1px solid #eee;
                text-align: center !important;
            }
            .resume-table th:first-child {
                text-align: left !important;
            }
            /* Aggressively remove button styling */
            .stButton > button,
            .stDownloadButton > button {
                background: none !important;
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
                box-shadow: none !important;
                width: auto !important;
                height: auto !important;
                line-height: normal !important;
            }
            .stButton > button:hover,
            .stDownloadButton > button:hover {
                background: none !important;
                border: none !important;
                box-shadow: none !important;
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
            /* File name styles */
            .file-name {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.75rem 0;
            }
            /* Delete dialog styles */
            .delete-dialog {
                padding: 1rem;
                margin-top: 0.5rem;
                background: #fff;
                border-radius: 4px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .delete-dialog .actions {
                display: flex;
                gap: 1rem;
                margin-top: 1rem;
            }
            /* Delete confirmation dialog */
            .delete-confirm {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 1rem;
                margin: 0.5rem 0 0.5rem 3rem;
                width: fit-content;
            }
            .delete-confirm p {
                margin: 0 0 1rem 0;
                color: #444;
            }
            .delete-buttons {
                display: flex;
                gap: 1rem;
            }
            .delete-buttons button {
                padding: 0.5rem 1rem !important;
                border-radius: 4px !important;
            }
            .delete-buttons button:first-child {
                background-color: #ff4b4b !important;
                color: white !important;
            }
            .delete-buttons button:last-child {
                background-color: #f0f2f6 !important;
                color: #444 !important;
            }
            /* Delete confirmation dialog */
            .delete-confirm-box {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 12px;
                margin: 8px 0;
                background: white;
                width: 100%;
            }
            .delete-confirm-text {
                margin-bottom: 16px;
                color: #333;
                font-size: 14px;
            }
            .delete-confirm-buttons {
                display: flex;
                justify-content: flex-end;
                gap: 8px;
            }
            /* Override Streamlit's button styles */
            .delete-confirm-buttons .stButton > button {
                padding: 4px 12px !important;
                border-radius: 4px !important;
                font-size: 14px !important;
                min-height: 32px !important;
            }
            .delete-button .stButton > button {
                background-color: #ff4b4b !important;
                color: white !important;
                border: none !important;
            }
            .cancel-button .stButton > button {
                background-color: #f0f2f6 !important;
                color: #333 !important;
                border: 1px solid #ddd !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize delete confirmation state
    if 'delete_confirmation' not in st.session_state:
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
                        <th style="width: 10%">Edit</th>
                        <th style="width: 10%">Download</th>
                        <th style="width: 10%">Delete</th>
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
            
            # Delete button
            if cols[3].button("🗑️", key=f"del_btn_{idx}"):
                st.session_state.delete_confirmation = name
            
            # Show delete confirmation if this is the file being deleted
            if st.session_state.delete_confirmation == name:
                st.markdown("""
                    <div class="delete-confirm-box">
                        <div class="delete-confirm-text">
                            Are you sure you want to delete this file?
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Use columns for button alignment
                _, col1, col2 = st.columns([3, 1, 1])
                with col1:
                    st.markdown('<div class="cancel-button">', unsafe_allow_html=True)
                    if st.button("Cancel", key=f"cancel_del_{idx}"):
                        st.session_state.delete_confirmation = None
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="delete-button">', unsafe_allow_html=True)
                    if st.button("Delete", key=f"confirm_del_{idx}"):
                        if delete_resume(st.session_state.user_id, name):
                            st.session_state.delete_confirmation = None
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            
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
            render_job_analysis_section()
        
        # Resume section in scrollable container
        with resume_col:
            render_resume_section()

if __name__ == "__main__":
    run()