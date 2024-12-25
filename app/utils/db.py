import sqlite3
import streamlit as st
import os

def get_db():
    """Get a database connection"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'applyai.db')
    return sqlite3.connect(db_path)

def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                file_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Add test user if it doesn't exist
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("test", "test")
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # Test user already exists
            pass

def save_resume(user_id, filename, content, file_type):
    """Save or update a resume in the database"""
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO resumes (user_id, filename, content, file_type)
                VALUES (?, ?, ?, ?)
            """, (user_id, filename, content, file_type))
            return True
    except Exception as e:
        st.error(f"Error saving resume: {str(e)}")
        return False

# Initialize database when module is loaded
init_db() 