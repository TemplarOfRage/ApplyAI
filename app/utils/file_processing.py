import PyPDF2
import io
import streamlit as st

def extract_text_from_file(uploaded_file):
    """Extract text from various file types"""
    try:
        if uploaded_file.type == "application/pdf":
            # Create a PDF reader object
            pdf_bytes = io.BytesIO(uploaded_file.getvalue())
            pdf_reader = PyPDF2.PdfReader(pdf_bytes)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Debug info
            st.write(f"DEBUG - Extracted {len(text)} characters from PDF")
            return text
            
        elif uploaded_file.type == "text/plain":
            # For text files, simply decode the content
            text = uploaded_file.getvalue().decode('utf-8')
            st.write(f"DEBUG - Extracted {len(text)} characters from text file")
            return text
            
        else:
            st.error(f"Unsupported file type: {uploaded_file.type}")
            return None
            
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None