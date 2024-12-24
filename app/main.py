# app/main.py
"""
Main Streamlit application entry point for ApplyAI.
"""

import streamlit as st
import anthropic
import uuid
import datetime

# Use absolute imports
from app.services.auth import create_user, authenticate_user, check_authentication
from app.services.resume import save_resume, get_user_resumes, delete_resume, extract_text_from_file
from app.services.analysis import save_analysis, get_user_analysis_history
from app.config import init_streamlit_config, get_api_key

def main():
    # Initialize Streamlit configuration
    init_streamlit_config()

    # Authentication check
    if not check_authentication():
        return
    
    st.title("ApplyAI")
    
    # Sidebar for resume management
    with st.sidebar:
        st.header("My Resumes")
        
        # Resume Upload Handler
        uploaded_files = st.file_uploader("Upload Resume", 
                                          type=['pdf', 'txt', 'docx'], 
                                          key="resume_uploader", 
                                          accept_multiple_files=True, 
                                          label_visibility="collapsed")
        
        if uploaded_files:
            current_files = {f.name for f in uploaded_files}
            saved_files = {name for name, _, _ in get_user_resumes(st.session_state.user_id)}
            
            new_files = current_files - saved_files
            if new_files:
                for file in uploaded_files:
                    if file.name in new_files:
                        file_name = file.name.rsplit('.', 1)[0]
                        file_type = file.type
                        
                        resume_content = extract_text_from_file(file)
                        
                        if resume_content:
                            save_resume(st.session_state.user_id, file_name, resume_content, file_type)
                            st.toast(f"Resume saved: {file_name}")
        
        # Resume Display and Management
        st.divider()
        st.subheader("Saved Resumes")
        
        resumes = get_user_resumes(st.session_state.user_id)
        if resumes:
            col_headers = st.columns([3, 1, 1])
            col_headers[0].write("**Name**")
            col_headers[1].write("**View**")
            col_headers[2].write("**Delete**")
            
            for name, content, file_type in resumes:
                cols = st.columns([3, 1, 1])
                # Truncate name if longer than 30 chars
                display_name = name if len(name) <= 30 else name[:27] + "..."
                cols[0].markdown(f"<div title='{name}'>{display_name}</div>", unsafe_allow_html=True)
                
                view_key = f"view_{name}_{hash(name)}"
                delete_key = f"delete_{name}_{hash(name)}"
                
                if cols[1].button("👁️", key=view_key):
                    st.session_state.selected_resume = name
                    
                if cols[2].button("❌", key=delete_key):
                    delete_resume(st.session_state.user_id, name)
                    if 'selected_resume' in st.session_state and st.session_state.selected_resume == name:
                        del st.session_state.selected_resume
                    st.rerun()
        
        # Resume Preview Panel
        if 'selected_resume' in st.session_state:
            st.divider()
            st.subheader("Preview")
            selected = next((r for r in get_user_resumes(st.session_state.user_id) 
                           if r[0] == st.session_state.selected_resume), None)
            if selected:
                name, content, file_type = selected
                st.text_area("Content", content, height=300, key=f"preview_{name}")
                if st.button("Close Preview"):
                    del st.session_state.selected_resume
                    st.rerun()
        
        # Logout Button
        if st.button("🚪 Logout"):
            del st.session_state.user_id
            st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🎯 Job Posting Analysis")
        job_post = st.text_area("Paste the job posting here", height=200)
        custom_questions = st.text_area("Custom application questions (Optional)", height=100)

        if st.button("🎯 Analyze Job Fit", type="primary"):
            if job_post:
                with st.spinner("Analyzing your fit..."):
                    # Get all user's resumes
                    user_resumes = get_user_resumes(st.session_state.user_id)
                    if not user_resumes:
                        st.error("Please upload at least one resume first")
                        return
                        
                    combined_resume_context = "\n---\n".join(
                        content for _, content, _ in user_resumes
                    )
                    
                    try:
                        # Get API key from configuration
                        api_key = get_api_key()
                        if not api_key:
                            st.error("Anthropic API key is missing")
                            return
                        
                        client = anthropic.Anthropic(api_key=api_key)
                        
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
            else:
                st.error("Please provide a job posting")

    with col2:
        st.header("📚 Analysis History")
        history = get_user_analysis_history(st.session_state.user_id)
        
        if history:
            for job_post, analysis, timestamp in history:
                with st.expander(f"Analysis: {timestamp}"):
                    st.markdown(analysis)
        else:
            st.info("Your analysis history will appear here")

# Application entry point
def run():
    main()

if __name__ == "__main__":
    run()