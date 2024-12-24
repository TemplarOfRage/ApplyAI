# app/services/auth.py
"""
Authentication services for ApplyAI.
"""

import streamlit as st
import sqlite3
import uuid
import bcrypt
from contextlib import contextmanager
import os

@contextmanager
def get_connection():
    """
    Context manager for database connections.
    """
    # Ensure the directory exists
    db_path = 'applyai.db'
    
    # Create the database connection
    conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """
    Initialize the database with necessary tables.
    """
    with get_connection() as conn:
        c = conn.cursor()
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id TEXT PRIMARY KEY,
                      username TEXT UNIQUE,
                      password_hash TEXT,
                      created_at TIMESTAMP)''')
        
        # Resumes table with user association
        c.execute('''CREATE TABLE IF NOT EXISTS resumes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      name TEXT,
                      content TEXT,
                      file_type TEXT,
                      created_at TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        # Analysis history with user association
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      job_post TEXT,
                      analysis TEXT,
                      created_at TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis_history(user_id)')
        
        conn.commit()

def hash_password(password: str) -> bytes:
    """
    Hash a password using bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    """
    Verify a password against its hash.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_user(username: str, password: str) -> str:
    """
    Create a new user in the database.
    """
    # Ensure database is initialized
    init_db()
    
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    
    with get_connection() as conn:
        c = conn.cursor()
        try:
            c.execute('''INSERT INTO users (id, username, password_hash, created_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                     (user_id, username, password_hash))
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None

def authenticate_user(username: str, password: str) -> str:
    """
    Authenticate a user and return user ID if credentials are correct.
    """
    # Ensure database is initialized
    init_db()
    
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        if result and verify_password(password, result[1]):
            return result[0]
    return None

def check_authentication():
    """
    Handle user authentication and login/registration UI.
    """
    # Ensure database is initialized
    init_db()
    
    # Safely get username from secrets, with fallback
    try:
        default_username = st.secrets.get("USERNAME", "admin")
    except Exception:
        default_username = "admin"
    
    # Safely get password from secrets, with fallback
    try:
        default_password = st.secrets.get("PASSWORD", "password")
    except Exception:
        default_password = "password"
    
    # Check if default admin exists
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username = ?', (default_username,))
        if not c.fetchone():
            # Create default admin user
            create_user(default_username, default_password)
    
    if 'user_id' not in st.session_state:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.title("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("Login", type="primary"):
                    user_id = authenticate_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            
            with col4:
                if st.button("Register"):
                    if username and password:
                        user_id = create_user(username, password)
                        if user_id:
                            st.session_state.user_id = user_id
                            st.success("Registration successful!")
                            st.rerun()
                        else:
                            st.error("Username already exists")
                    else:
                        st.error("Please provide username and password")
        
        with col2:
            st.title("Welcome to ApplyAI")
            st.markdown("""
                #### Your AI-Powered Job Application Assistant
                
                Transform your job search with intelligent application analysis:
                
                🎯 **Smart Job Fit Analysis**  
                ✨ **Custom Resume Tailoring**  
                💡 **Strategic Insights**  
                📝 **Application Assistance**  
                
                Start your smarter job search today!
            """)
        return False
    return True

def logout():
    """Handle logout"""
    if 'user_id' in st.session_state:
        del st.session_state.user_id
    
    # Clear stored credentials
    stored_creds = get_stored_credentials()
    if 'auth_token' in stored_creds:
        del stored_creds['auth_token']
    get_stored_credentials.clear()
    
    # Force a rerun to update the UI
    st.rerun()