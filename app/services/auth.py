# app/services/auth.py
"""
Authentication services for ApplyAI.
"""

import streamlit as st
import bcrypt
import uuid
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_connection():
    """Database connection context manager"""
    conn = sqlite3.connect('applyai.db', check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database"""
    with get_connection() as conn:
        c = conn.cursor()
        # Drop existing tables if they exist
        c.execute('DROP TABLE IF EXISTS analysis_history')
        c.execute('DROP TABLE IF EXISTS resumes')
        c.execute('DROP TABLE IF EXISTS users')
        
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id TEXT PRIMARY KEY,
                      username TEXT UNIQUE,
                      password_hash TEXT,
                      created_at TIMESTAMP)''')
        
        # Create resumes table with file content
        c.execute('''CREATE TABLE IF NOT EXISTS resumes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      name TEXT,
                      content TEXT,
                      file_type TEXT,
                      file_content BLOB,
                      created_at TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        # Create analysis history table
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      job_post TEXT,
                      analysis TEXT,
                      created_at TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        # Create indexes for better performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis_history(user_id)')
        
        conn.commit()

def hash_password(password: str) -> bytes:
    """Hash a password for storing"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_user(username: str, password: str) -> str:
    """Create a new user and return their ID"""
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
    """Authenticate a user and return their ID"""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        if result and verify_password(password, result[1]):
            return result[0]
    return None

def check_authentication():
    """Check if user is authenticated"""
    if 'user_id' not in st.session_state:
        # Check if users exist
        with get_connection() as conn:
            c = conn.cursor()
            try:
                # Create all configured users if they don't exist
                for username, password in st.secrets.users.items():
                    c.execute('SELECT id FROM users WHERE username = ?', (username,))
                    if not c.fetchone():
                        create_user(username, password)
            except Exception as e:
                st.error("Error initializing users. Please check your configuration.")
                return False
        
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
    """Log out the current user"""
    if 'user_id' in st.session_state:
        del st.session_state.user_id
    st.rerun()

# Initialize database on startup
init_db()