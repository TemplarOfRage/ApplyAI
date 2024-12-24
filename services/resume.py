import streamlit as st
from datetime import datetime
import PyPDF2
import docx
import io

# In-memory storage for resumes (replace with database in production)
@st.cache_data(show_spinner=False)
def get_resume_store():
    """Cache the resume store to persist across reruns"""
    return {}

def extract_text_from_file(uploaded_file):
    """Extract text content from various file types"""
    try:
        # Get the file extension
        file_type = uploaded_file.type
        
        if 'pdf' in file_type.lower():
            # Handle PDF files
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
            
        elif 'word' in file_type.lower() or 'docx' in file_type.lower():
            # Handle Word documents
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
            
        elif 'text' in file_type.lower():
            # Handle plain text files
            return uploaded_file.getvalue().decode('utf-8')
            
        else:
            return None
            
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None

def save_resume(user_id, name, content, file_type):
    """Save a resume to storage"""
    resumes = get_resume_store()
    
    # Initialize user's resume storage if it doesn't exist
    if user_id not in resumes:
        resumes[user_id] = {}
    
    # Save the resume with metadata
    resumes[user_id][name] = {
        'content': content,
        'file_type': file_type,
        'uploaded_at': datetime.utcnow().isoformat()
    }
    
    # Force cache update
    get_resume_store.clear()
    return True

def get_user_resumes(user_id):
    """Get all resumes for a user"""
    resumes = get_resume_store()
    
    if user_id not in resumes:
        return []
    
    # Return list of tuples (name, content, file_type)
    return [(name, data['content'], data['file_type']) 
            for name, data in resumes[user_id].items()]

def delete_resume(user_id, name):
    """Delete a resume from storage"""
    resumes = get_resume_store()
    
    if user_id in resumes and name in resumes[user_id]:
        del resumes[user_id][name]
        
        # Clean up empty user entries
        if not resumes[user_id]:
            del resumes[user_id]
        
        # Force cache update
        get_resume_store.clear()
        return True
        
    return False 