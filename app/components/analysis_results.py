import streamlit as st
import re
from utils.db import save_analysis

def parse_analysis_sections(analysis_text):
    """Parse the analysis text into structured sections"""
    sections = {
        'match_score': 0,
        'overall': [],
        'qualifications': [],
        'missing': [],
        'improvements': []
    }
    
    current_section = None
    
    # Debug
    st.write("DEBUG - Starting parse of:", analysis_text)
    
    for line in analysis_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Debug
        st.write(f"DEBUG - Processing line: {line}")
        
        # Check for section headers
        if 'Match Score:' in line:
            current_section = 'match_score'
            match = re.search(r'(\d+)%', line)
            if match:
                sections['match_score'] = int(match.group(1))
                st.write(f"DEBUG - Found match score: {sections['match_score']}")
        elif 'Overall Assessment:' in line:
            current_section = 'overall'
            st.write("DEBUG - Switched to overall section")
        elif 'Key Qualifications Match:' in line:
            current_section = 'qualifications'
            st.write("DEBUG - Switched to qualifications section")
        elif 'Missing Skills/Experience:' in line:
            current_section = 'missing'
            st.write("DEBUG - Switched to missing section")
        elif 'Suggested Resume Improvements:' in line:
            current_section = 'improvements'
            st.write("DEBUG - Switched to improvements section")
        # Add content to current section if it starts with a bullet point
        elif current_section and current_section != 'match_score' and line.startswith('•'):
            line = line.lstrip('•').strip()
            if line:
                sections[current_section].append(line)
                st.write(f"DEBUG - Added to {current_section}: {line}")
    
    # Debug final sections
    st.write("DEBUG - Final sections:", sections)
    
    return sections

def render_analysis_results(analysis_text, user_id=None, resume_name=None, job_content=None):
    """Renders the analysis results in a structured format"""
    if not analysis_text:
        return
        
    # Parse the analysis into sections
    sections = parse_analysis_sections(analysis_text)
    
    # Save to database if we have user info
    if user_id and resume_name and job_content:
        save_analysis(user_id, resume_name, job_content, analysis_text)
    
    st.markdown("### Analysis Results")
    
    # Create tabs in new order
    match_tab, overall_tab, quals_tab, missing_tab, improve_tab = st.tabs([
        "Match Score", 
        "Overall",
        "Qualifications", 
        "Missing Skills", 
        "Improvements"
    ])
    
    with match_tab:
        st.markdown("#### Match Score")
        score = sections['match_score']
        
        # Create a progress bar for the match score
        st.progress(float(score)/100)
        st.markdown(f"### {score}%")
        
        # Add color coding
        if score >= 80:
            st.success("Strong Match! 🌟")
        elif score >= 60:
            st.warning("Good Match with Room for Improvement 📈")
        else:
            st.error("Consider Targeting Different Roles 🎯")
    
    with overall_tab:
        st.markdown("#### Overall Assessment")
        for point in sections['overall']:
            st.markdown(f"• {point}")
        
    with quals_tab:
        st.markdown("#### Key Qualifications Match")
        for qual in sections['qualifications']:
            st.success(f"• {qual}")
    
    with missing_tab:
        st.markdown("#### Missing Skills/Experience")
        for skill in sections['missing']:
            st.error(f"• {skill}")
    
    with improve_tab:
        st.markdown("#### Suggested Improvements")
        for imp in sections['improvements']:
            st.info(f"• {imp}")
        
        st.markdown("""
            <div style='margin-top: 1em'>
                <small>Use these suggestions to improve your resume before applying.</small>
            </div>
        """, unsafe_allow_html=True) 