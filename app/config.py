# app/config.py
"""
Configuration settings for ApplyAI.
"""
import streamlit as st
import os

def init_streamlit_config():
    """Initialize Streamlit configuration settings"""
    st.set_page_config(
        page_title="ApplyAI",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

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