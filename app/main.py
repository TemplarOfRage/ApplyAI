"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
from services.auth import check_authentication, logout
from services.resume import (
    get_user_resumes, 
    delete_resume, 
    save_resume,
    extract_text_from_file
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
            }
            .resume-table th {
                color: #666;
                font-weight: 400;
                padding: 0.5rem;
                border-bottom: 1px solid #eee;
            }
            .resume-table td {
                padding: 0.5rem;
                border-bottom: 1px solid #eee;
                vertical-align: middle;
            }
            /* Make buttons smaller */
            .small-btn {
                padding: 0 0.5rem !important;
                height: 1.5rem !important;
                line-height: 1.5rem !important;
                font-size: 0.7rem !important;
            }
            /* Smaller icons */
            .small-icon {
                font-size: 0.8rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    resumes = get_user_resumes(st.session_state.user_id)
    
    # Handle file upload first
    uploaded_file = st.file_uploader(
        "Upload another resume" if resumes else "Upload your first resume",
        type=["pdf", "docx", "txt"],
        key="resume_uploader"
    )
    
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
    
    # Show existing resumes in a table
    if resumes:
        st.divider()
        
        # Create table header
        st.markdown("""
            <table class="resume-table">
                <thead>
                    <tr>
                        <th style="width: 80%">Name</th>
                        <th style="width: 10%">View</th>
                        <th style="width: 10%">Delete</th>
                    </tr>
                </thead>
            </table>
        """, unsafe_allow_html=True)
        
        for idx, (name, content, file_type) in enumerate(resumes):
            cols = st.columns([8, 1, 1])
            
            # Truncate filename if too long
            display_name = name if len(name) < 40 else name[:37] + "..."
            
            with cols[0]:
                st.markdown(f'<span class="small-icon">📄</span> {display_name}', unsafe_allow_html=True)
            
            # View button
            view_key = f"view_{idx}_{hash(name)}"
            if cols[1].button("👁️", key=view_key, help="View resume content", use_container_width=True):
                st.session_state[f"show_{view_key}"] = True
            
            # Delete button
            del_key = f"del_{idx}_{hash(name)}"
            if cols[2].button("🗑️", key=del_key, help="Delete resume", use_container_width=True):
                if delete_resume(st.session_state.user_id, name):
                    st.rerun()
            
            # Show content if requested
            if st.session_state.get(f"show_{view_key}", False):
                with st.expander("", expanded=True):
                    st.text_area("", value=content, height=200, 
                               disabled=True, label_visibility="collapsed",
                               key=f"content_{idx}_{hash(name)}")
                    if st.button("Close", key=f"hide_{idx}_{hash(name)}", 
                               type="secondary", use_container_width=True):
                        del st.session_state[f"show_{view_key}"]
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
            render_job_analysis_section()
        
        # Resume section in scrollable container
        with resume_col:
            render_resume_section()

if __name__ == "__main__":
    run()