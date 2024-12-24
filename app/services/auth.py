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
    """Enhanced authentication check with session persistence"""
    # Check if user is already authenticated in session state
    if 'user_id' in st.session_state:
        return True
    
    # Check for stored credentials
    stored_creds = get_stored_credentials()
    
    # If we have stored credentials, verify and use them
    if 'auth_token' in stored_creds:
        user_id = verify_auth_token(stored_creds['auth_token'])
        if user_id:
            st.session_state.user_id = user_id
            return True
    
    # If not authenticated, show welcome and login/register form
    st.title("Welcome to ApplyAI")
    st.write("""
    Your AI-powered job application assistant. Upload your resume and let us help you
    analyze job postings to create tailored applications.
    """)
    
    st.divider()
    
    # Initialize default users if store is empty (for testing)
    users = get_user_store()
    if not users:
        create_user("test", "test")  # Create a test user
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Login", key="login_button", type="primary"):
                if authenticate_user(username, password):
                    user_id = username
                    
                    # Set session state
                    st.session_state.user_id = user_id
                    
                    # Create auth token and store it
                    token = create_auth_token(user_id)
                    stored_creds = get_stored_credentials()
                    stored_creds['auth_token'] = token
                    
                    # Force cache update
                    get_stored_credentials.clear()
                    
                    st.rerun()
                    return True
                else:
                    st.error("Invalid username or password")
                    return False
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Register", key="register_button", type="primary"):
                if not new_username or not new_password:
                    st.error("Please provide both username and password")
                    return False
                    
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    return False
                
                success, message = create_user(new_username, new_password)
                if success:
                    st.success(message)
                    # Automatically log in after successful registration
                    st.session_state.user_id = new_username
                    token = create_auth_token(new_username)
                    stored_creds = get_stored_credentials()
                    stored_creds['auth_token'] = token
                    get_stored_credentials.clear()
                    st.rerun()
                    return True
                else:
                    st.error(message)
                    return False
            
    return False