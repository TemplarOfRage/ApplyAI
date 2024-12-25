import PyPDF2
import docx
import io
import streamlit as st

def extract_text_from_file(uploaded_file):
    """Extract text from various file types"""
    try:
        if uploaded_file.type == "application/pdf":
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
            
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Read DOCX
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
            
        elif uploaded_file.type == "text/plain":
            # Read TXT
            return uploaded_file.getvalue().decode('utf-8')
            
        else:
            st.error(f"Unsupported file type: {uploaded_file.type}")
            return None
            
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None