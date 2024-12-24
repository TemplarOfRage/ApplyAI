# app/config.py
"""
Configuration management for Job Buddy application using Streamlit secrets.
"""

import streamlit as st

class ConfigManager:
    """
    Centralized configuration management for the Streamlit application.
    """
    @staticmethod
    def get_api_key():
        """
        Retrieve Anthropic API key from Streamlit secrets.
        """
        try:
            return st.secrets["ANTHROPIC_API_KEY"]
        except KeyError:
            st.error("Anthropic API key is missing from Streamlit secrets.")
            return None
    
    @staticmethod
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

# Create a singleton config instance
config = ConfigManager()

# Expose key methods for direct import
get_api_key = config.get_api_key
init_streamlit_config = config.init_streamlit_config