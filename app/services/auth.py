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
    
    # If not authenticated, show login/register form
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
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
                
                return True
            else:
                st.error("Invalid username or password")
                return False
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Register", key="register_button"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
                return False
            
            success, message = create_user(new_username, new_password)
            if success:
                st.success(message)
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