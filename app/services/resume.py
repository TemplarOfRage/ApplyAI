# app/services/resume.py
"""
Resume processing services for ApplyAI.
"""

import streamlit as st
import sqlite3
from datetime import datetime
import PyPDF2
import docx
import io

def validate_file(uploaded_file):
    """Validate uploaded file"""
    if uploaded_file.size > 5 * 1024 * 1024:  # 5MB limit
        raise ValueError("File size too large. Please upload a file smaller than 5MB.")
    
    if uploaded_file.type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']:
        raise ValueError("Invalid file type. Please upload a PDF, DOCX, or TXT file.")
    
    return True

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file"""
    try:
        if uploaded_file.type == 'application/pdf':
            return extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return extract_text_from_docx(uploaded_file)
        elif uploaded_file.type == 'text/plain':
            return uploaded_file.getvalue().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.type}")
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(io.BytesIO(docx_file.getvalue()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")

def init_resume_db():
    """Initialize or migrate resume database"""
    try:
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        # Check if table exists
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='resumes' ''')
        
        # If table doesn't exist, create it
        if c.fetchone()[0] == 0:
            c.execute('''CREATE TABLE resumes
                        (user_id TEXT,
                         filename TEXT,
                         content TEXT,
                         file_type TEXT,
                         timestamp TEXT,
                         PRIMARY KEY (user_id, filename))''')
            conn.commit()
            
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
    finally:
        conn.close()

def save_resume(user_id, filename, content, file_type):
    """Save resume to database"""
    try:
        # Ensure database is initialized
        init_resume_db()
        
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        # Insert or replace resume
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('INSERT OR REPLACE INTO resumes VALUES (?, ?, ?, ?, ?)',
                 (user_id, filename, content, file_type, timestamp))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving resume: {str(e)}")
        return False
    finally:
        conn.close()

def get_user_resumes(user_id):
    """Get all resumes for a user"""
    try:
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        c.execute('SELECT filename, content, file_type FROM resumes WHERE user_id = ? ORDER BY timestamp DESC',
                 (user_id,))
        return c.fetchall()
    except Exception as e:
        st.error(f"Error fetching resumes: {str(e)}")
        return []
    finally:
        conn.close()

def delete_resume(user_id, filename):
    """Delete a resume"""
    try:
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        c.execute('DELETE FROM resumes WHERE user_id = ? AND filename = ?',
                 (user_id, filename))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting resume: {str(e)}")
        return False
    finally:
        conn.close()