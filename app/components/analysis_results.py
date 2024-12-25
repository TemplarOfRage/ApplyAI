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
    
    # Debug
    st.write("DEBUG - Starting parse of multiple analyses")
    st.write("Raw text:", analysis_text[:200] + "...")  # Show first 200 chars
    
    for line in analysis_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('===== RESUME'):
            if current_analysis:
                analyses.append(current_analysis)
            current_analysis = {
                'resume_name': line.split(' - ')[1].strip('= ') if ' - ' in line else 'Resume',
                'match_score': 0,
                'overall': [],
                'qualifications': [],
                'missing': [],
                'improvements': []
            }
        elif not analyses and not current_analysis:
            # If no resume sections found, treat as single analysis
            current_analysis = {
                'resume_name': 'Analysis',
                'match_score': 0,
                'overall': [],
                'qualifications': [],
                'missing': [],
                'improvements': []
            }
            analyses.append(current_analysis)
            
            # Parse as single analysis
            sections = parse_analysis_sections(analysis_text)
            analyses[0].update(sections)
            break
            
    if current_analysis and current_analysis not in analyses:
        analyses.append(current_analysis)
    
    # Debug
    st.write(f"DEBUG - Found {len(analyses)} analyses")
    
    return analyses or [{
        'resume_name': 'Analysis',
        'match_score': 0,
        'overall': [],
        'qualifications': [],
        'missing': [],
        'improvements': []
    }]

def render_analysis_results(analysis_text, user_id=None, resume_name=None, job_content=None):
    """Renders the analysis results in a structured format"""
    if not analysis_text:
        return
        
    # Save analysis to database if we have all required info
    if user_id and resume_name and job_content:
        save_analysis(user_id, resume_name, job_content, analysis_text)
    
    st.markdown("### Analysis Results")
    
    # Parse all analyses
    analyses = parse_multiple_analyses(analysis_text)
    
    # Create tabs for each analysis
    if len(analyses) > 1:
        resume_tabs = st.tabs([f"📄 {analysis['resume_name']}" for analysis in analyses])
        
        for tab, analysis in zip(resume_tabs, analyses):
            with tab:
                render_single_analysis(analysis)
                
                # Show history button
                if st.button("📊 View Analysis History", key=f"history_{analysis['resume_name']}"):
                    history = get_resume_history(user_id, analysis['resume_name'])
                    if history:
                        st.markdown("### Previous Analyses")
                        for date, job, result in history:
                            with st.expander(f"Analysis from {date}"):
                                st.markdown("**Job Description:**")
                                st.text(job)
                                st.markdown("**Analysis:**")
                                st.markdown(result)
    else:
        # Single resume - use the original tab layout
        render_single_analysis(analyses[0])

def render_single_analysis(analysis):
    """Render a single analysis result"""
    st.markdown(f"#### Match Score: {analysis['match_score']}%")
    st.progress(float(analysis['match_score'])/100)
    
    st.markdown("#### Overall Assessment")
    for point in analysis['overall']:
        st.markdown(f"• {point}")
        
    st.markdown("#### Key Qualifications")
    for qual in analysis['qualifications']:
        st.success(f"• {qual}")
        
    st.markdown("#### Missing Skills")
    for skill in analysis['missing']:
        st.error(f"• {skill}")
        
    st.markdown("#### Improvements")
    for imp in analysis['improvements']:
        st.info(f"• {imp}") 