# app/services/auth.py
"""
Authentication services for ApplyAI.
"""

import streamlit as st
import sqlite3
import uuid
import bcrypt
from contextlib import contextmanager

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
    if 'user_id' not in st.session_state:
        # Check if default admin exists
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE username = ?', (st.secrets["USERNAME"],))
            if not c.fetchone():
                # Create default admin user
                create_user(st.secrets["USERNAME"], st.secrets["PASSWORD"])
        
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