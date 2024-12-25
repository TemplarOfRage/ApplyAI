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
    
    # Custom CSS for clean layout
    st.markdown("""
        <style>
            /* Table styles */
            .resume-table {
                font-size: 0.85rem;
                width: 100%;
                margin-top: 1rem;
                border-collapse: collapse;
            }
            .resume-table th, .resume-table td {
                padding: 0.5rem;
                border-bottom: 1px solid #eee;
                text-align: left;
            }
            .resume-table th {
                color: #666;
                font-weight: 400;
            }
            /* Hide expander chevron */
            .streamlit-expanderHeader {
                display: none !important;
            }
            /* Clean button styles */
            .stButton button {
                padding: 0.25rem 0.5rem;
                font-size: 0.8rem;
                width: 2rem !important;
                height: 2rem !important;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            /* File name styles */
            .file-name {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .file-icon {
                color: #666;
                font-size: 0.9rem;
            }
            /* Hide default expander styling */
            .streamlit-expanderContent {
                border: none !important;
                padding: 0.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Show existing resumes in a table if any exist
    resumes = get_user_resumes(st.session_state.user_id)
    if resumes:
        # Create table header
        st.markdown("""
            <table class="resume-table">
                <thead>
                    <tr>
                        <th style="width: 70%">Name</th>
                        <th style="width: 10%; text-align: center">View</th>
                        <th style="width: 10%; text-align: center">Edit</th>
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
            
            # View button
            view_key = f"view_{idx}_{hash(name)}"
            if cols[1].button("👁️", key=view_key, help="View original file"):
                # Toggle the view state
                current_state = st.session_state.get(f"show_{view_key}", False)
                st.session_state[f"show_{view_key}"] = not current_state
                # Ensure edit mode is closed when viewing
                if f"edit_{view_key}" in st.session_state:
                    del st.session_state[f"edit_{view_key}"]
            
            # Edit button
            edit_key = f"edit_{idx}_{hash(name)}"
            if cols[2].button("✏️", key=edit_key, help="Edit extracted text"):
                # Toggle the edit state
                current_state = st.session_state.get(f"edit_{view_key}", False)
                st.session_state[f"edit_{view_key}"] = not current_state
                # Ensure view mode is closed when editing
                if f"show_{view_key}" in st.session_state:
                    del st.session_state[f"show_{view_key}"]
            
            # Delete button
            del_key = f"del_{idx}_{hash(name)}"
            if cols[3].button("🗑️", key=del_key, help="Delete resume"):
                if delete_resume(st.session_state.user_id, name):
                    st.rerun()
            
            # Show content based on state
            if st.session_state.get(f"show_{view_key}", False):
                with st.expander("", expanded=True):
                    file_content = get_resume_file(st.session_state.user_id, name)
                    if file_content and file_type == "application/pdf":
                        import base64
                        base64_pdf = base64.b64encode(file_content).decode('utf-8')
                        pdf_display = f'''
                            <iframe
                                src="data:application/pdf;base64,{base64_pdf}"
                                width="100%"
                                height="600"
                                style="border: none;"
                            ></iframe>
                        '''
                        st.markdown(pdf_display, unsafe_allow_html=True)
                    else:
                        st.info("Preview not available for this file type")
            
            if st.session_state.get(f"edit_{view_key}", False):
                with st.expander("", expanded=True):
                    edited_content = st.text_area(
                        "Edit extracted text:",
                        value=content,
                        height=200,
                        key=f"content_{idx}_{hash(name)}"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save", key=f"save_{idx}_{hash(name)}", 
                                   type="primary", use_container_width=True):
                            update_resume_content(st.session_state.user_id, name, edited_content)
                            del st.session_state[f"edit_{view_key}"]
                            st.rerun()
                    with col2:
                        if st.button("Cancel", key=f"cancel_{idx}_{hash(name)}", 
                                   type="secondary", use_container_width=True):
                            del st.session_state[f"edit_{view_key}"]
                            st.rerun()
    
    # File uploader section
    st.divider()
    uploaded_file = st.file_uploader(
        "Upload another resume" if resumes else "Upload your first resume",
        type=["pdf", "docx", "txt"],
        key=f"resume_uploader_{st.session_state.get('uploader_key', 0)}",
        label_visibility="collapsed"
    )
    
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