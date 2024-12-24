"""
Main Streamlit application for ApplyAI.
"""
import streamlit as st
import anthropic
from app.services.auth import check_authentication, logout
from app.services.resume import save_resume, get_user_resumes, delete_resume, extract_text_from_file
from app.services.analysis import save_analysis, get_user_analysis_history
from app.config import init_streamlit_config, get_api_key
import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    """Extract text content from a URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        st.error(f"Error extracting text from URL: {str(e)}")
        return None

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
        st.title("⚙️ Configuration")
        
        # Claude API Configuration
        st.subheader("Analysis Settings")
        
        system_prompt = st.text_area(
            "System Prompt",
            value="""You are an expert job application analyst. Your task is to analyze job postings and provide insights about the requirements and how to best position oneself for the role.""",
            help="This sets the context for Claude's analysis"
        )
        
        analysis_prompt = st.text_area(
            "Analysis Prompt",
            value="""Please analyze this job posting and provide:
1. Key technical skills required
2. Soft skills emphasized
3. Experience level needed
4. Main responsibilities
5. Unique requirements or preferences
6. Tips for application success""",
            help="This is the specific request sent to Claude"
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            help="Higher values make output more creative but less focused"
        )
        
        if st.button("🚪 Logout", type="primary"):
            logout()
            st.rerun()
    
    # Create two columns for main content
    col1, col2 = st.columns([3, 2])
    
    render_job_analysis_section(col1, system_prompt, analysis_prompt, temperature)
    
    with col2:
        st.subheader("📄 Your Resumes")
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
        
        if uploaded_file:
            try:
                # Validate file size
                if uploaded_file.size > 5 * 1024 * 1024:  # 5MB limit
                    st.error("File size too large. Please upload a file smaller than 5MB.")
                    return
                
                # Validate file type
                if uploaded_file.type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']:
                    st.error("Invalid file type. Please upload a PDF, DOCX, or TXT file.")
                    return
                
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

if __name__ == "__main__":
    run()