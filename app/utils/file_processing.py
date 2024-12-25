import streamlit as st

def extract_text_from_file(uploaded_file):
    """Extract text from various file types"""
    try:
        # For text files
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read().decode('utf-8'))
            
        # For PDFs and DOCXs, just read the raw text content
        content = str(uploaded_file.read())
        
        # If we got content, return it
        if content:
            return content
        else:
            st.error(f"Could not extract text from {uploaded_file.name}")
            return None
            
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None