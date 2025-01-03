# app/config.py
"""
Configuration settings for ApplyAI.
"""
import streamlit as st
import os

def init_streamlit_config():
    """Initialize Streamlit configuration"""
    st.set_page_config(
        page_title="ApplyAI",
        page_icon="🎯",
        layout="wide"
    )
    
    # Add security headers and minimal CSS
    st.markdown("""
        <style>
            /* Global font size reduction */
            .stMarkdown, .stText, .stTextArea textarea, .stTextInput input, 
            .stSelectbox select, .stMultiSelect select {
                font-size: 0.9rem !important;
            }
            
            /* Resume file styling */
            .resume-file {
                transition: background-color 0.3s;
            }
            
            .resume-file:hover {
                background-color: #f0f2f6;
            }
            
            .file-info {
                color: #666;
                font-size: 0.8em;
                margin-left: 8px;
            }
            
            /* Compact spacing */
            .block-container {
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
            }
            
            .element-container {
                margin-bottom: 0.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Disable telemetry
    st.markdown("""
        <script>
            if (window.PerformanceObserver) {
                const observer = new PerformanceObserver(() => {});
                observer.observe({ entryTypes: ['resource'] });
            }
        </script>
    """, unsafe_allow_html=True)

def get_api_key():
    """Get Anthropic API key from environment or Streamlit secrets"""
    return os.getenv('ANTHROPIC_API_KEY') or st.secrets.get('ANTHROPIC_API_KEY')

def get_database_url():
    """
    Retrieve database URL from Streamlit secrets.
    """
    try:
        return st.secrets["DATABASE_URL"]
    except KeyError:
        st.error("Database URL is missing from Streamlit secrets.")
        return "sqlite:///applyai.db"

def get_credentials():
    """
    Retrieve username and password from Streamlit secrets.
    """
    try:
        return {
            "username": st.secrets["USERNAME"],
            "password": st.secrets["PASSWORD"]
        }
    except KeyError:
        st.error("Credentials are missing from Streamlit secrets.")
        return None

def get_jwt_secret():
    return os.getenv('JWT_SECRET_KEY', 'your-secret-key')

def get_default_system_prompt():
    """Get default system prompt for Claude"""
    return """You are an expert job application analyst. Your task is to analyze job postings and provide insights about the requirements and how to best position oneself for the role."""

def get_default_analysis_prompt():
    """Get default analysis prompt for Claude"""
    return """Please analyze this job posting and provide:
1. Key technical skills required
2. Soft skills emphasized
3. Experience level needed
4. Main responsibilities
5. Unique requirements or preferences
6. Tips for application success"""

def render_config_sidebar():
    """Render configuration sidebar"""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Claude API Configuration
        st.subheader("Analysis Settings")
        
        system_prompt = st.text_area(
            "System Prompt",
            value=get_default_system_prompt(),
            help="This sets the context for Claude's analysis"
        )
        
        analysis_prompt = st.text_area(
            "Analysis Prompt",
            value=get_default_analysis_prompt(),
            help="This is the specific request sent to Claude"
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            help="Higher values make output more creative but less focused"
        )
        
        return system_prompt, analysis_prompt, temperature