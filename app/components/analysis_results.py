import streamlit as st
import re

def parse_analysis_sections(analysis_text):
    """Parse the analysis text into structured sections"""
    sections = {
        'match_score': '',
        'overall': '',
        'qualifications': '',
        'missing': '',
        'improvements': ''
    }
    
    # Extract match score (assuming it's a percentage)
    match = re.search(r'Match Score:?\s*(\d+)%', analysis_text)
    if match:
        sections['match_score'] = int(match.group(1))
    
    # Extract other sections based on headers
    current_section = None
    current_text = []
    
    for line in analysis_text.split('\n'):
        if '1. Match Score' in line:
            current_section = 'match_score'
        elif '2. Key Qualifications' in line:
            current_section = 'qualifications'
        elif '3. Missing Skills' in line:
            current_section = 'missing'
        elif '4. Suggested Resume' in line:
            current_section = 'improvements'
        elif '5. Overall' in line:
            current_section = 'overall'
        elif current_section and line.strip():
            current_text.append(line.strip())
        
        if current_section:
            sections[current_section] = '\n'.join(current_text)
            current_text = []
    
    return sections

def render_analysis_results(analysis_text):
    """Renders the analysis results in a structured format"""
    if not analysis_text:
        return
        
    st.markdown("### Analysis Results")
    
    # Parse the analysis into sections
    sections = parse_analysis_sections(analysis_text)
    
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
        score = sections.get('match_score', 0)
        
        # Create a progress bar for the match score
        st.progress(score/100)
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
        if sections.get('overall'):
            # Split into bullet points if possible
            points = sections['overall'].split('\n')
            for point in points:
                if point.strip():
                    st.markdown(f"• {point.strip()}")
        
    with quals_tab:
        st.markdown("#### Key Qualifications Match")
        if sections.get('qualifications'):
            quals = sections['qualifications'].split('\n')
            for qual in quals:
                if qual.strip():
                    if qual.startswith(('-', '•')):
                        st.markdown(qual)
                    else:
                        st.markdown(f"• {qual.strip()}")
    
    with missing_tab:
        st.markdown("#### Missing Skills/Experience")
        if sections.get('missing'):
            missing = sections['missing'].split('\n')
            for skill in missing:
                if skill.strip():
                    if skill.startswith(('-', '•')):
                        st.error(skill)
                    else:
                        st.error(f"• {skill.strip()}")
    
    with improve_tab:
        st.markdown("#### Suggested Improvements")
        if sections.get('improvements'):
            improvements = sections['improvements'].split('\n')
            for imp in improvements:
                if imp.strip():
                    if imp.startswith(('-', '•')):
                        st.info(imp)
                    else:
                        st.info(f"• {imp.strip()}")
        
        # Add action buttons
        if st.button("📝 Edit Resume"):
            st.session_state['show_resume_editor'] = True
        
        st.markdown("""
            <div style='margin-top: 1em'>
                <small>Use these suggestions to improve your resume before applying.</small>
            </div>
        """, unsafe_allow_html=True) 