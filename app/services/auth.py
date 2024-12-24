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
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 3em;
            font-weight: 700;
            background: linear-gradient(90deg, #4776E6 0%, #8E54E9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }
        .subheader {
            font-size: 1.5em;
            color: #666;
            margin-bottom: 2em;
        }
        .feature-card {
            padding: 1.5em;
            border-radius: 10px;
            background: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 1em 0;
            border: 1px solid #f0f0f0;
        }
        .feature-icon {
            font-size: 2em;
            margin-bottom: 0.5em;
        }
        .feature-title {
            font-weight: 600;
            margin-bottom: 0.5em;
        }
        .feature-text {
            color: #666;
            font-size: 0.9em;
        }
        .testimonial {
            font-style: italic;
            color: #555;
            padding: 1em;
            border-left: 3px solid #8E54E9;
            background: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown('<h1 class="main-header">ApplyAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Your AI-powered career acceleration platform</p>', unsafe_allow_html=True)
    
    # Quick Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Success Rate", "85%", "vs. industry avg.")
    with col2:
        st.metric("Time Saved", "75%", "per application")
    with col3:
        st.metric("User Rating", "4.9/5", "⭐")
    
    st.divider()
    
    # Main Features Section
    st.subheader("Why Choose ApplyAI?")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Smart Job Analysis</div>
                <div class="feature-text">
                    Instantly analyze job descriptions and identify key requirements using advanced AI technology.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with feat_col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">✨</div>
                <div class="feature-title">Tailored Applications</div>
                <div class="feature-text">
                    Get personalized suggestions to match your experience with job requirements perfectly.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with feat_col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Progress Tracking</div>
                <div class="feature-text">
                    Monitor your application success rate and improve with AI-powered insights.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Social Proof
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("What Users Say")
        st.markdown("""
            <div class="testimonial">
                "ApplyAI helped me land my dream job at a top tech company. The AI-powered insights were game-changing!"
                <br><strong>- Sarah K., Software Engineer</strong>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Login/Register Container
        st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        """, unsafe_allow_html=True)
        
        # Initialize default users if store is empty (for testing)
        users = get_user_store()
        if not users:
            create_user("test", "test")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            if st.button("Login", key="login_button", type="primary", use_container_width=True):
                if authenticate_user(username, password):
                    user_id = username
                    st.session_state.user_id = user_id
                    token = create_auth_token(user_id)
                    stored_creds = get_stored_credentials()
                    stored_creds['auth_token'] = token
                    get_stored_credentials.clear()
                    st.rerun()
                    return True
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            new_username = st.text_input("Username", key="register_username", placeholder="Choose a username")
            new_password = st.text_input("Password", type="password", key="register_password", placeholder="Choose a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            if st.button("Register", key="register_button", type="primary", use_container_width=True):
                if not new_username or not new_password:
                    st.error("Please provide both username and password")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = create_user(new_username, new_password)
                    if success:
                        st.success(message)
                        st.session_state.user_id = new_username
                        token = create_auth_token(new_username)
                        stored_creds = get_stored_credentials()
                        stored_creds['auth_token'] = token
                        get_stored_credentials.clear()
                        st.rerun()
                        return True
                    else:
                        st.error(message)
    
    # Footer
    st.divider()
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2em;">
            © 2024 ApplyAI • Privacy Policy • Terms of Service
        </div>
    """, unsafe_allow_html=True)
    
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