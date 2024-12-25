import streamlit as st
from anthropic import Anthropic
from .errors import AnalysisError

def analyze_resume_for_job(resume_content, job_content):
    """Basic analysis function"""
    try:
        client = Anthropic(api_key=st.secrets['ANTHROPIC_API_KEY'])
        
        prompt = f"""
        As an AI career advisor, analyze this resume against the job posting and provide detailed feedback.
        Please format your response exactly as shown below, using the exact section headers:

        Match Score: [0-100]%

        Overall Assessment:
        • [Key point 1]
        • [Key point 2]
        • [Key point 3]

        Key Qualifications Match:
        • [Matching qualification 1]
        • [Matching qualification 2]
        • [Matching qualification 3]

        Missing Skills/Experience:
        • [Missing skill 1]
        • [Missing skill 2]
        • [Missing skill 3]

        Suggested Resume Improvements:
        • [Improvement 1]
        • [Improvement 2]
        • [Improvement 3]

        RESUME:
        {resume_content}

        JOB POSTING:
        {job_content}
        """
        
        response = client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=4000
        )
        
        # Debug the response
        st.write("DEBUG - Raw Response:", response.content[0].text)
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"Analysis Error: {str(e)}")
        raise AnalysisError(f"Error during analysis: {str(e)}") 