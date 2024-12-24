import streamlit as st
from datetime import datetime, timedelta
import jwt
import json

# This should be moved to environment variables in production
SECRET_KEY = "your-secret-key"

@st.cache_data(show_spinner=False)
def get_stored_credentials():
    """Cache the credentials to persist across reruns"""
    return {}

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
    
    # If not authenticated, show login form
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            user_id = username  # Or however you generate/retrieve user_id
            
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