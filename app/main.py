import streamlit as st
import anthropic
from datetime import datetime

from .config import config, init_streamlit_config, get_api_key
from .database import (
    init_db,
    create_user,
    authenticate_user,
    get_user_resumes,
    save_resume,
    delete_resume,
    get_user_analysis_history,
    save_analysis
)
from .utils.file_processing import process_resume_file

# Initialize configuration
init_streamlit_config()

def check_authentication():
    """Check if user is authenticated and handle login/registration."""
    if 'user_id' not in st.session_state:
        # Check if default admin exists
        if 'USERNAME' in st.secrets:
            create_user(st.secrets["USERNAME"], st.secrets["PASSWORD"])
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.title("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("Login", type="primary"):
                    user_id = authenticate_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            
            with col4:
                if st.button("Register"):
                    if username and password:
                        user_id = create_user(username, password)
                        if user_id:
                            st.session_state.user_id = user_id
                            st.success("Registration successful!")
                            st.rerun()
                        else:
                            st.error("Username already exists")
                    else:
                        st.error("Please provide username and password")
        
        with col2:
            st.title("Welcome to ApplyAI")
            st.markdown(config.app_description)
        return False
    return True

def handle_resume_upload(uploaded_files):
    """Process uploaded resume files."""
    if uploaded_files:
        current_files = {f.name for f in uploaded_files}
        saved_files = {name for name, _, _ in get_user_resumes(st.session_state.user_id)}
        
        new_files = current_files - saved_files
        if new_files:
            for file in uploaded_files:
                if file.name in new_files:
                    result = process_resume_file(file)
                    if result:
                        file_name, content, file_type = result
                        save_resume(st.session_state.user_id, file_name, content, file_type)
                        st.toast(f"Resume saved: {file_name}")

def analyze_job_posting(job_post: str, custom_questions: str = None):
    """Analyze job posting using Claude AI."""
    user_resumes = get_user_resumes(st.session_state.user_id)
    if not user_resumes:
        st.error("Please upload at least one resume first")
        return
        
    combined_resume_context = "\n---\n".join(
        content for _, content, _ in user_resumes
    )
    
    try:
        client = anthropic.Client(api_key=get_api_key())
        
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
            model=config.api_model,
            max_tokens=config.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = message.content[0].text
        save_analysis(st.session_state.user_id, job_post, analysis)
        
        return analysis
        
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None

def main():
    """Main application function."""
    if not check_authentication():
        return
        
    st.title("ApplyAI")
    
    # Sidebar for resume management
    with st.sidebar:
        st.header("My Resumes")
        
        uploaded_files = st.file_uploader(
            "Upload Resume",
            type=list(config.allowed_file_types),
            key="resume_uploader",
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        handle_resume_upload(uploaded_files)
        
        # Display user's resumes
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
                display_name = name if len(name) <= 30 else name[:27] + "..."
                cols[0].markdown(f"<div title='{name}'>{display_name}</div>", 
                               unsafe_allow_html=True)
                
                if cols[1].button("👁️", key=f"view_{name}_{hash(name)}"):
                    st.session_state.selected_resume = name
                    
                if cols[2].button("❌", key=f"delete_{name}_{hash(name)}"):
                    delete_resume(st.session_state.user_id, name)
                    if 'selected_resume' in st.session_state:
                        del st.session_state.selected_resume
                    st.rerun()
        
        # Preview panel
        if 'selected_resume' in st.session_state:
            st.divider()
            st.subheader("Preview")
            selected = next((r for r in resumes 
                           if r[0] == st.session_state.selected_resume), None)
            if selected:
                name, content, file_type = selected
                st.text_area("Content", content, height=300, 
                            key=f"preview_{name}")
                if st.button("Close Preview"):
                    del st.session_state.selected_resume
                    st.rerun()
        
        if st.button("🚪 Logout"):
            del st.session_state.user_id
            st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🎯 Job Posting Analysis")
        job_post = st.text_area("Paste the job posting here", height=200)
        custom_questions = st.text_area(
            "Custom application questions (Optional)", 
            height=100
        )

        if st.button("🎯 Analyze Job Fit", type="primary"):
            if job_post:
                with st.spinner("Analyzing your fit..."):
                    analysis = analyze_job_posting(job_post, custom_questions)
                    if analysis:
                        st.markdown(analysis)
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

if __name__ == "__main__":
    main()