"""
Main Streamlit application entry point for ApplyAI.
"""

import streamlit as st
import anthropic
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Use direct imports without the 'app' prefix
from services.auth import create_user, authenticate_user, check_authentication
from services.resume import save_resume, get_user_resumes, delete_resume, extract_text_from_file
from services.analysis import save_analysis, get_user_analysis_history
from config import init_streamlit_config, get_api_key

def debug_analysis_rendering(analysis):
    """
    Helper function to debug analysis rendering and ensure all sections are visible.
    """
    # Wrap debug information in an expander
    with st.expander("🔍 Debug Analysis Output", expanded=False):
        st.write("Full Analysis Debug:")
        st.code(analysis)
        
        # Try to explicitly render each section
        sections = [
            "## Initial Assessment",
            "## Match Analysis", 
            "## Resume Strategy", 
            "## Tailored Resume", 
            "## Custom Responses", 
            "## Follow-up Actions"
        ]
        
        for section in sections:
            st.write(f"Checking section: {section}")
            section_content = extract_section(analysis, section)
            if section_content:
                st.markdown(f"{section}")
                st.markdown(section_content)
            else:
                st.warning(f"No content found for section: {section}")

def extract_section(text, section_header):
    """
    Extract a specific section from the analysis text.
    """
    sections = text.split('##')
    for section in sections:
        if section.strip().startswith(section_header.replace('## ', '')):
            # Remove the section header
            section_content = section.split('\n', 1)[1] if '\n' in section else ''
            return section_content.strip()
    return None

def extract_job_posting_from_url(url):
    """
    Attempts to extract job posting content from a given URL.
    Returns tuple of (success, content/error_message)
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False, "Please enter a valid URL"
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return True, text
        
    except requests.RequestException as e:
        return False, f"Error fetching URL: {str(e)}"
    except Exception as e:
        return False, f"Error processing content: {str(e)}"

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
        
        # Initialize session state for job posting content if not exists
        if 'job_post_content' not in st.session_state:
            st.session_state.job_post_content = ""
            
        # Track previous URL to detect changes
        if 'previous_url' not in st.session_state:
            st.session_state.previous_url = ""
        
        # URL Input with experimental label
        job_url = st.text_input(
            "Job URL (Experimental)",
            help="Automatic content extraction may not work for all job sites"
        )
        
        # Only extract content if URL is new or changed
        if job_url and job_url != st.session_state.previous_url:
            with st.spinner("Extracting job posting content..."):
                success, content = extract_job_posting_from_url(job_url)
                if success:
                    st.session_state.job_post_content = content
                    st.session_state.previous_url = job_url
                    st.success("✅ Content extracted successfully")
                else:
                    st.error(content)
        
        # Job posting content area
        job_post = st.text_area(
            "Job Posting Content",
            value=st.session_state.job_post_content,
            placeholder="Enter job posting content here. If you provided a URL above, the content will appear here automatically.",
            height=200,
            key="job_posting_textarea"  # Added unique key
        )
        
        # Manual updates to content should also be saved
        if job_post != st.session_state.job_post_content:
            st.session_state.job_post_content = job_post

        custom_questions = st.text_area("Custom application questions (Optional)", height=100)

        # Get user resumes before the button
        user_resumes = get_user_resumes(st.session_state.user_id)
        
        # Disable button if no resumes
        button_disabled = not bool(user_resumes)
        if button_disabled:
            st.warning("⚠️ Please upload at least one resume before analyzing")
            
        if st.button("🎯 Analyze Job Fit", type="primary", disabled=button_disabled):
            if job_post:
                with st.spinner("Analyzing your fit..."):
                    # Remove this check since we now prevent the button from being clicked
                    # if not user_resumes:
                    #     st.error("Please upload at least one resume first")
                    #     return
                        
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
                        
                        IMPORTANT INSTRUCTIONS:
                        - Provide a comprehensive analysis of the job posting
                        - Create a fully tailored resume section
                        - Ensure each section is clearly labeled
                        - Focus on specific resume modifications
                        
                        Please analyze this application following this EXACT format:
                        
                        ## Initial Assessment
                        - Provide an overview of job requirements
                        
                        ## Match Analysis
                        - Detail how the current resume matches job requirements
                        
                        ## Resume Strategy
                        - Specific recommendations for resume modification
                        
                        ## Tailored Resume
                        - Full rewrite of the resume, highlighting key match points
                        - Use the exact language from the job posting
                        - Emphasize skills and experiences most relevant to this role
                        
                        ## Custom Responses
                        - Craft potential answers to provided custom questions
                        
                        ## Follow-up Actions
                        - Recommended next steps in the application process"""

                        message = client.messages.create(
                            model="claude-3-sonnet-20240229",
                            max_tokens=4096,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        
                        analysis = message.content[0].text
                        save_analysis(st.session_state.user_id, job_post, analysis)
                        
                        # Enhanced rendering with debugging
                        debug_analysis_rendering(analysis)
                        
                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")
                        # Additional error logging
                        st.write("Detailed Error:")
                        st.error(e)
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