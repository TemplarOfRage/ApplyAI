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

def parse_multiple_analyses(analysis_text):
    """Parse multiple resume analyses"""
    analyses = []
    current_analysis = None
    
    for line in analysis_text.split('\n'):
        if line.startswith('===== RESUME'):
            if current_analysis:
                analyses.append(current_analysis)
            current_analysis = {'resume_name': line.split(' - ')[1].strip('=')}
        elif current_analysis:
            # Add content to current analysis using existing parsing logic
            # ... (rest of parsing logic)
            pass
    
    if current_analysis:
        analyses.append(current_analysis)
    
    return analyses

def render_analysis_results(analysis_text, user_id=None, resume_name=None, job_content=None):
    """Renders the analysis results in a structured format"""
    if not analysis_text:
        return
        
    analyses = parse_multiple_analyses(analysis_text)
    
    # Create tabs for each resume
    resume_tabs = st.tabs([analysis['resume_name'] for analysis in analyses])
    
    for tab, analysis in zip(resume_tabs, analyses):
        with tab:
            # Use existing rendering logic for each analysis
            # ... (rest of rendering logic)
            pass
    
    # If there are multiple resumes, show the comparison
    if len(analyses) > 1:
        with st.expander("📊 Resume Comparison"):
            comparison = analysis_text.split("Finally, if there are multiple resumes")[-1]
            st.markdown(comparison) 