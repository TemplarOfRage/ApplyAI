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

def init_database():
    """Initialize the database and create tables if they don't exist"""
    print("\n=== Initializing Database ===")
    try:
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        # Drop existing tables to start fresh
        c.execute('DROP TABLE IF EXISTS resumes')
        print("Dropped existing resumes table")
        
        # Create fresh table
        c.execute('''
            CREATE TABLE resumes (
                user_id TEXT,
                filename TEXT,
                content TEXT,
                file_type TEXT,
                timestamp TEXT,
                PRIMARY KEY (user_id, filename)
            )
        ''')
        print("Created new resumes table")
        
        conn.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

def save_resume(user_id, filename, content, file_type):
    """Save resume to database"""
    print(f"\n=== Saving Resume ===")
    print(f"User ID: {user_id}")
    print(f"Filename: {filename}")
    print(f"Content length: {len(content) if content else 'None'}")
    print(f"File type: {file_type}")
    
    try:
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # First, verify if the resume already exists
        c.execute('SELECT COUNT(*) FROM resumes WHERE user_id = ? AND filename = ?',
                 (user_id, filename))
        exists = c.fetchone()[0]
        print(f"Resume already exists: {exists > 0}")
        
        c.execute('''
            INSERT OR REPLACE INTO resumes 
            (user_id, filename, content, file_type, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, filename, content, file_type, timestamp))
        
        conn.commit()
        
        # Verify the save
        c.execute('SELECT COUNT(*) FROM resumes WHERE user_id = ? AND filename = ?',
                 (user_id, filename))
        saved = c.fetchone()[0]
        print(f"Resume saved successfully: {saved > 0}")
        
        # Debug: show all resumes in database
        c.execute('SELECT user_id, filename FROM resumes')
        all_resumes = c.fetchall()
        print(f"All resumes in database: {all_resumes}")
        
        return True
        
    except Exception as e:
        print(f"Error saving resume: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def get_user_resumes(user_id):
    """Get all resumes for a user"""
    print(f"\n=== Getting Resumes for User: {user_id} ===")
    try:
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        # Debug: show all resumes in database
        c.execute('SELECT user_id, filename FROM resumes')
        all_resumes = c.fetchall()
        print(f"All resumes in database: {all_resumes}")
        
        # Get resumes for specific user
        c.execute('SELECT filename, content, file_type FROM resumes WHERE user_id = ?', (user_id,))
        results = c.fetchall()
        print(f"Found {len(results)} resumes for user {user_id}")
        print(f"Resume filenames: {[r[0] for r in results]}")
        
        return results
        
    except Exception as e:
        print(f"Error getting resumes: {str(e)}")
        return []
    finally:
        if 'conn' in locals():
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