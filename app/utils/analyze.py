import streamlit as st
from anthropic import Anthropic
from .errors import AnalysisError

def analyze_resume_for_job(resume_content, job_content):
    """Basic analysis function"""
    # Get API key from Streamlit secrets
    if 'ANTHROPIC_API_KEY' not in st.secrets:
        raise AnalysisError("Anthropic API key not found in Streamlit secrets")
        
    # Create client with API key from secrets
    client = Anthropic(
        api_key=st.secrets['ANTHROPIC_API_KEY']
    )
    
    try:
        completion = client.messages.create(
            model="claude-3-opus-20240229",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                        As an AI career advisor, analyze this resume against the job posting and provide detailed feedback.
                        
                        RESUME:
                        {resume_content}
                        
                        JOB POSTING:
                        {job_content}
                        
                        Please provide:
                        1. Match Score (0-100%)
                        2. Key Qualifications Match
                        3. Missing Skills/Experience
                        4. Suggested Resume Improvements
                        5. Overall Recommendations
                    """
                }
            ],
            max_tokens=4000
        )
        return completion.content[0].text
    except Exception as e:
        st.error(f"Analysis Error: {str(e)}")
        raise AnalysisError(f"Error during analysis: {str(e)}") 