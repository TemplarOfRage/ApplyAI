import streamlit as st
from anthropic import Anthropic
from .errors import AnalysisError

def analyze_resume_for_job(resumes, job_content):
    """Analyze multiple resumes against a job posting"""
    try:
        client = Anthropic(api_key=st.secrets['ANTHROPIC_API_KEY'])
        
        # Build resume context
        resume_context = ""
        for idx, (name, content, file_type, created_at, updated_at) in enumerate(resumes):
            resume_context += f"\nResume {idx + 1} - {name}:\n{content}\n"
        
        prompt = f"""
        As an AI career advisor, analyze these resumes against the job posting and provide detailed feedback.
        For each resume, provide a separate analysis in the format shown below.

        {resume_context}

        JOB POSTING:
        {job_content}

        For each resume, provide:

        ===== RESUME [Number] - {name} =====
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
        ===============================

        Finally, if there are multiple resumes, provide a comparison and recommendation for which resume is best suited for this position.
        """
        
        response = client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=4000
        )
        
        return response.content[0].text
        
    except Exception as e:
        st.error(f"Analysis Error: {str(e)}")
        raise AnalysisError(f"Error during analysis: {str(e)}") 