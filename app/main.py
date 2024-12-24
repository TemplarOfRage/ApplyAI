# app/main.py
"""
Main Streamlit application entry point for Job Buddy.
"""

import streamlit as st
import anthropic

# Import configuration 
from .config import init_streamlit_config, get_api_key

def main():
    """
    Primary application logic and routing.
    """
    # Initialize Streamlit configuration
    init_streamlit_config()
    
    # Set up page navigation
    page = st.sidebar.radio("Navigate", 
        ["Home", "Login", "Register", "Resume Upload", "Job Analysis"]
    )
    
    # Page routing logic
    if page == "Home":
        st.title("Welcome to Job Buddy")
        st.write("Your AI-powered job application assistant")
    
    elif page == "Login":
        login_page()
    
    elif page == "Register":
        register_page()
    
    elif page == "Resume Upload":
        resume_upload_page()
    
    elif page == "Job Analysis":
        job_analysis_page()

def login_page():
    """
    Handle user login page.
    """
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        st.warning("Login functionality not yet implemented")

def register_page():
    """
    Handle user registration page.
    """
    st.header("Register")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        st.warning("Registration functionality not yet implemented")

def resume_upload_page():
    """
    Handle resume upload functionality.
    """
    st.header("Resume Upload")
    uploaded_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        # TODO: Implement file processing logic

def job_analysis_page():
    """
    Handle job analysis functionality.
    """
    st.header("Job Analysis")
    job_description = st.text_area("Paste Job Description")
    
    if st.button("Analyze Job"):
        st.warning("Job analysis functionality not yet implemented")

# Application entry point
def run():
    # Get API key for Anthropic
    api_key = get_api_key()
    
    # Initialize Anthropic client if API key is available
    if api_key:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            # Store client in session state for use across pages
            st.session_state['anthropic_client'] = client
        except Exception as e:
            st.error(f"Failed to initialize Anthropic client: {e}")
    else:
        st.error("Anthropic API key is missing. Please configure it in Streamlit secrets.")
    
    # Run the main application
    main()

# This allows the script to be run directly
if __name__ == "__main__":
    run()