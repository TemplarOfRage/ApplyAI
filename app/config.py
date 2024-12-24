import streamlit as st
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class AppConfig:
    """Application configuration settings"""
    # App information
    app_name: str = "ApplyAI"
    app_icon: str = "🎯"
    app_description: str = """Transform your job search with intelligent application analysis:
    
    🎯 Smart Job Fit Analysis
    ✨ Custom Resume Tailoring
    💡 Strategic Insights
    📝 Application Assistance"""

    # Database settings
    db_name: str = "applyai.db"
    db_path: Path = Path("applyai.db")

    # File upload settings
    allowed_file_types: tuple = ("pdf", "docx", "txt")
    max_file_size_mb: int = 10

    # API settings
    api_model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4096

    # UI settings
    sidebar_width: int = 300
    main_content_width: int = 800

def init_streamlit_config():
    """Initialize Streamlit configuration"""
    st.set_page_config(
        page_title="ApplyAI",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom styling
    st.markdown("""
        <style>
        .stButton button {
            width: 100%;
        }
        .stTextArea textarea {
            height: 200px;
        }
        .stHeader {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

def load_secrets() -> dict:
    """Load and validate required secrets"""
    required_secrets = [
        "ANTHROPIC_API_KEY",
        "USERNAME",
        "PASSWORD"
    ]
    
    # Check for required secrets
    missing_secrets = [
        secret for secret in required_secrets 
        if secret not in st.secrets
    ]
    
    if missing_secrets:
        raise ValueError(
            f"Missing required secrets: {', '.join(missing_secrets)}\n"
            f"Please add them to .streamlit/secrets.toml"
        )
    
    return st.secrets

def get_api_key() -> str:
    """Get Anthropic API key from secrets"""
    return st.secrets["ANTHROPIC_API_KEY"]

def get_admin_credentials() -> tuple[str, str]:
    """Get admin username and password from secrets"""
    return st.secrets["USERNAME"], st.secrets["PASSWORD"]

# Create global config instance
config = AppConfig()

# Initialize all configurations
def init_all():
    """Initialize all configurations"""
    init_streamlit_config()
    load_secrets()