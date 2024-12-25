from anthropic import Anthropic

def analyze_resume_for_job(resume_content, job_content):
    """Basic analysis function"""
    anthropic = Anthropic()
    
    prompt = f"""
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
    
    try:
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0,
            system="You are an expert career advisor and resume consultant.",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text
    except Exception as e:
        raise Exception(f"Error calling Claude API: {str(e)}") 