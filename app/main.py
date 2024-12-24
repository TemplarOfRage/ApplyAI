# app/main.py
"""
Main Streamlit application entry point for Job Buddy.
"""

import streamlit as st
import anthropic

# Use absolute import
from app.config import init_streamlit_config, get_api_key, get_credentials, get_database_url

def main():
    """
    Primary application logic and routing.
    """
    # Initialize Streamlit configuration
    init_streamlit_config()
    
    # Fetch configuration details
    api_key = get_api_key()
    db_url = get_database_url()
    credentials = get_credentials()
    
    # Debug information (remove in production)
    st.write("API Key Present:", bool(api_key))
    st.write("Database URL:", db_url)
    st.write("Credentials Present:", bool(credentials))
    
    # Set up page navigation
    page = st.sidebar.radio("Navigate", 
        ["Home", "Login", "Register", "Resume Upload", "Job Analysis"]
    )
    
    # Page routing logic
    if page == "Home":
        st.title("Welcome to Job Buddy")
        st.write("Your AI-powered job application assistant")
    
    elif page == "Login":
        login_page(credentials)
    
    elif page == "Register":
        register_page()
    
    elif page == "Resume Upload":
        resume_upload_page()
    
    elif page == "Job Analysis":
        job_analysis_page(api_key)

def login_page(credentials):
    """
    Handle user login page.
    """
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if credentials and username == credentials['username'] and password == credentials['password']:
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

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

def job_analysis_page(api_key):
    """
    Handle job analysis functionality.
    """
    st.header("Job Analysis")
    
    if not api_key:
        st.error("Anthropic API key is missing")
        return
    
    job_description = st.text_area("Paste Job Description")
    
    if st.button("Analyze Job"):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            # Placeholder for job analysis logic
            st.warning("Job analysis functionality not yet implemented")
        except Exception as e:
            st.error(f"Error initializing Anthropic client: {e}")

# Application entry point
def run():
    main()

# This allows the script to be run directly
if __name__ == "__main__":
    run()