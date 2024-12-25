import PyPDF2
import io
import streamlit as st

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF files"""
    try:
        # Create PDF reader object
        pdf_bytes = io.BytesIO(uploaded_file.getvalue())
        reader = PyPDF2.PdfReader(pdf_bytes)
        
        # Extract text
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        # Quick validation
        if not text.strip():
            st.error("No text could be extracted from the PDF")
            return None
            
        return text
        
    except Exception as e:
        st.error(f"Failed to process PDF: {str(e)}")
        return None