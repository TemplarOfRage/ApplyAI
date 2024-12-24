# app/services/resume.py
"""
Resume processing services for ApplyAI.
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Tuple
import PyPDF2
import docx2txt

@contextmanager
def get_connection():
    """
    Context manager for database connections.
    """
    conn = sqlite3.connect('applyai.db', check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def extract_text_from_file(file) -> str:
    """
    Extract text from different file types.
    """
    try:
        if file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            return " ".join(page.extract_text() for page in pdf_reader.pages)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return docx2txt.process(file)
        else:
            # For text files or other types
            return file.getvalue().decode()
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

def save_resume(user_id: str, name: str, content: str, file_type: str):
    """
    Save or update a user's resume.
    """
    with get_connection() as conn:
        c = conn.cursor()
        # Check if resume with same name exists
        c.execute('''SELECT id FROM resumes 
                    WHERE user_id = ? AND name = ?''', (user_id, name))
        existing = c.fetchone()
        
        if existing:
            # Update existing resume
            c.execute('''UPDATE resumes 
                        SET content = ?, file_type = ?, created_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND name = ?''',
                     (content, file_type, user_id, name))
        else:
            # Create new resume
            c.execute('''INSERT INTO resumes 
                        (user_id, name, content, file_type, created_at)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                     (user_id, name, content, file_type))
        conn.commit()

def get_user_resumes(user_id: str) -> List[Tuple[str, str, str]]:
    """
    Retrieve all resumes for a specific user.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT name, content, file_type 
                    FROM resumes 
                    WHERE user_id = ?
                    ORDER BY created_at DESC''', (user_id,))
        return c.fetchall()

def delete_resume(user_id: str, name: str):
    """
    Delete a specific resume for a user.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM resumes WHERE user_id = ? AND name = ?', 
                 (user_id, name))
        conn.commit()