import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from .errors import AnalysisError
import streamlit as st

def analyze_resume_for_job(resume_content, job_content):
    """Basic analysis function"""
    # Initialize with API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY') or st.secrets.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise AnalysisError("No API key found for Claude")
        
    client = Anthropic(api_key=api_key)
    
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{
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
            }],
            max_tokens=4000
        )
        return response.content[0].text
    except Exception as e:
        raise AnalysisError(f"Error calling Claude API: {str(e)}")
    finally:
        # Clean up
        del client 