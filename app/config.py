# app/config.py
"""
Configuration management for Job Buddy application using Streamlit secrets.
"""

import streamlit as st

def get_api_key():
    """
    Retrieve Anthropic API key from Streamlit secrets.
    """
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except KeyError:
        st.error("Anthropic API key is missing from Streamlit secrets.")
        return None

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

def init_streamlit_config():
    """
    Initialize Streamlit-specific configurations.
    """
    st.set_page_config(
        page_title="Job Buddy AI",
        page_icon=":briefcase:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Optional: Add custom CSS
    st.markdown("""
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)