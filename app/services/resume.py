# app/services/resume.py
"""
Resume processing services for ApplyAI.
"""

import streamlit as st
import PyPDF2
import docx2txt
from .auth import get_connection

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from a PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        return " ".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_docx(docx_file) -> str:
    """Extract text from a DOCX file"""
    try:
        return docx2txt.process(docx_file)
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return None

def extract_text_from_file(uploaded_file) -> tuple[str, bytes]:
    """Extract text from an uploaded file and return both text and original content"""
    file_content = uploaded_file.getvalue()
    
    if uploaded_file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = " ".join(page.extract_text() for page in pdf_reader.pages)
            return text_content, file_content
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None, None
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            text_content = docx2txt.process(uploaded_file)
            return text_content, file_content
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return None, None
    else:
        text_content = file_content.decode()
        return text_content, file_content

def save_resume(user_id: str, name: str, content: str, file_type: str, file_content: bytes = None) -> bool:
    """Save a resume to the database"""
    with get_connection() as conn:
        c = conn.cursor()
        try:
            # Check if resume with same name exists
            c.execute(
                'SELECT id FROM resumes WHERE user_id = ? AND name = ?',
                (user_id, name)
            )
            existing = c.fetchone()
            
            if existing:
                # Update existing resume
                c.execute(
                    'UPDATE resumes SET content = ?, file_type = ?, file_content = ?, created_at = CURRENT_TIMESTAMP WHERE user_id = ? AND name = ?',
                    (content, file_type, file_content, user_id, name)
                )
            else:
                # Create new resume
                c.execute(
                    'INSERT INTO resumes (user_id, name, content, file_type, file_content, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
                    (user_id, name, content, file_type, file_content)
                )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving resume: {str(e)}")
            return False

def get_user_resumes(user_id: str):
    """Get all resumes for a user"""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT name, content, file_type 
                    FROM resumes 
                    WHERE user_id = ?
                    ORDER BY created_at DESC''', (user_id,))
        return c.fetchall()

def delete_resume(user_id: str, name: str) -> bool:
    """Delete a resume from the database"""
    with get_connection() as conn:
        c = conn.cursor()
        try:
            c.execute('DELETE FROM resumes WHERE user_id = ? AND name = ?',
                     (user_id, name))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting resume: {str(e)}")
            return False

def get_resume_file(user_id: str, name: str):
    """Get the original file content for a resume"""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            'SELECT file_content FROM resumes WHERE user_id = ? AND name = ?',
            (user_id, name)
        )
        result = c.fetchone()
        return result[0] if result else None

def update_resume_content(user_id: str, name: str, content: str) -> bool:
    """Update the extracted text content of a resume"""
    with get_connection() as conn:
        c = conn.cursor()
        try:
            c.execute(
                'UPDATE resumes SET content = ? WHERE user_id = ? AND name = ?',
                (content, user_id, name)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating resume content: {str(e)}")
            return False