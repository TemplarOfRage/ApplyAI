# app/services/auth.py
"""
Authentication services for ApplyAI.
"""

import streamlit as st
from datetime import datetime, timedelta
import jwt
import json
import hashlib
import os

# This should be moved to environment variables in production
SECRET_KEY = "your-secret-key"

# Simple in-memory user store (replace with database in production)
@st.cache_data(show_spinner=False)
def get_user_store():
    """Cache the user store to persist across reruns"""
    return {}

@st.cache_data(show_spinner=False)
def get_stored_credentials():
    """Cache the credentials to persist across reruns"""
    return {}

def hash_password(password):
    """Create a secure hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    """Create a new user"""
    users = get_user_store()
    
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        'password_hash': hash_password(password),
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Force cache update
    get_user_store.clear()
    return True, "User created successfully"

def authenticate_user(username, password):
    """Authenticate a user"""
    users = get_user_store()
    
    if username not in users:
        return False
    
    stored_hash = users[username]['password_hash']
    return stored_hash == hash_password(password)

def create_auth_token(user_id):
    """Create a JWT token for the user"""
    expiration = datetime.utcnow() + timedelta(days=7)
    token = jwt.encode(
        {
            'user_id': user_id,
            'exp': expiration
        },
        SECRET_KEY,
        algorithm='HS256'
    )
    return token

def verify_auth_token(token):
    """Verify the JWT token and return the user_id if valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except:
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
    
    # If not authenticated, show welcome screen
    st.title("🎯 Welcome to ApplyAI")
    
    # Feature highlights with icons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📝 Resume Management")
        st.write("Upload and manage multiple versions of your resume")
    
    with col2:
        st.markdown("### 🔍 Job Analysis")
        st.write("Get AI-powered insights on job postings and requirements")
    
    with col3:
        st.markdown("### ✨ Custom Tailoring")
        st.write("Receive personalized suggestions to match job requirements")
    
    st.divider()
    
    # Description
    st.markdown("""
    ApplyAI is your intelligent job application assistant that helps you:
    - 📊 Analyze job postings for key requirements
    - 🎯 Match your skills to job requirements
    - 💡 Generate tailored application materials
    - 🔄 Track your application history
    """)
    
    st.divider()
    
    # Initialize default users if store is empty (for testing)
    users = get_user_store()
    if not users:
        create_user("test", "test")  # Create a test user
    
    # Login/Register tabs
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