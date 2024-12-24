"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
import anthropic
from app.services.auth import check_authentication, logout
from app.services.resume import save_resume, get_user_resumes, delete_resume, extract_text_from_file
from app.services.analysis import save_analysis, get_user_analysis_history
from app.config import init_streamlit_config, get_api_key

def run():
    """Main application entry point"""
    init_streamlit_config()
    
    # Check authentication before showing any content
    if not check_authentication():
        return
        
    # Show main application content
    st.title("ApplyAI")
    
    # Add logout button to sidebar
    with st.sidebar:
        if st.button("🚪 Logout", type="primary"):
            logout()
            st.rerun()
    
    # Create two columns for main content
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📝 Job Posting Analysis")
        job_post = st.text_area(
            "Paste a job posting here",
            height=300,
            placeholder="Paste the job description here to analyze it..."
        )
        
        if st.button("Analyze", type="primary"):
            if not job_post:
                st.error("Please paste a job posting to analyze")
                return
                
            with st.spinner("Analyzing job posting..."):
                # Your analysis logic here
                st.success("Analysis complete!")
                
    with col2:
        st.subheader("📄 Your Resumes")
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
        
        if uploaded_file:
            try:
                content = extract_text_from_file(uploaded_file)
                if content:
                    if save_resume(st.session_state.user_id, uploaded_file.name, content, uploaded_file.type):
                        st.success(f"Resume '{uploaded_file.name}' uploaded successfully!")
                    else:
                        st.error("Failed to save resume")
                else:
                    st.error("Could not extract text from file")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        # Show existing resumes
        st.divider()
        st.subheader("Saved Resumes")
        resumes = get_user_resumes(st.session_state.user_id)
        
        if not resumes:
            st.info("No resumes uploaded yet")
        else:
            for name, content, file_type in resumes:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {name}")
                with col2:
                    if st.button("Delete", key=f"del_{name}"):
                        if delete_resume(st.session_state.user_id, name):
                            st.rerun()
    
    # Analysis History
    st.divider()
    st.subheader("📊 Analysis History")
    history = get_user_analysis_history(st.session_state.user_id)
    
    if not history:
        st.info("No analysis history yet")
    else:
        for job_post, analysis, timestamp in history:
            with st.expander(f"Analysis from {timestamp}"):
                st.text_area("Job Post", value=job_post, height=100, disabled=True)
                st.write("Analysis:", analysis)

if __name__ == "__main__":
    run()