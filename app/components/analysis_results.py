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
        
    st.markdown("### Analysis Results")
    
    # Parse all analyses
    analyses = parse_multiple_analyses(analysis_text)
    
    # Create tabs for each analysis
    if len(analyses) > 1:
        # Multiple resumes - create a tab for each
        resume_tabs = st.tabs([f"📄 {analysis['resume_name']}" for analysis in analyses])
        
        for tab, analysis in zip(resume_tabs, analyses):
            with tab:
                render_single_analysis(analysis)
                
        # Show comparison if available
        if "Finally, if there are multiple resumes" in analysis_text:
            with st.expander("📊 Resume Comparison"):
                comparison = analysis_text.split("Finally, if there are multiple resumes")[-1]
                st.markdown(comparison)
    else:
        # Single resume - use the original tab layout
        analysis = analyses[0]
        match_tab, overall_tab, quals_tab, missing_tab, improve_tab = st.tabs([
            "Match Score", 
            "Overall",
            "Qualifications", 
            "Missing Skills", 
            "Improvements"
        ])
        
        with match_tab:
            st.markdown("#### Match Score")
            score = analysis['match_score']
            st.progress(float(score)/100)
            st.markdown(f"### {score}%")
            
            if score >= 80:
                st.success("Strong Match! 🌟")
            elif score >= 60:
                st.warning("Good Match with Room for Improvement 📈")
            else:
                st.error("Consider Targeting Different Roles 🎯")
        
        with overall_tab:
            st.markdown("#### Overall Assessment")
            for point in analysis['overall']:
                st.markdown(f"• {point}")
            
        with quals_tab:
            st.markdown("#### Key Qualifications")
            for qual in analysis['qualifications']:
                st.success(f"• {qual}")
        
        with missing_tab:
            st.markdown("#### Missing Skills")
            for skill in analysis['missing']:
                st.error(f"• {skill}")
        
        with improve_tab:
            st.markdown("#### Improvements")
            for imp in analysis['improvements']:
                st.info(f"• {imp}")
            
            st.markdown("""
                <div style='margin-top: 1em'>
                    <small>Use these suggestions to improve your resume before applying.</small>
                </div>
            """, unsafe_allow_html=True)

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