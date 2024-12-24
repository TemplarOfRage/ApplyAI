import streamlit as st
from datetime import datetime, timedelta
import jwt  # You'll need to add PyJWT to requirements.txt

# Add this to your imports and requirements.txt
from streamlit_cookies_manager import CookieManager

# Secret key for JWT - in production, this should be in environment variables
SECRET_KEY = "your-secret-key"  # TODO: Move to environment variables

def create_auth_token(user_id):
    """Create a JWT token for the user"""
    expiration = datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
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
    """Enhanced authentication check with persistent login"""
    # Initialize cookie manager
    cookies = CookieManager()
    
    # If already authenticated in session state, return True
    if 'user_id' in st.session_state:
        return True
        
    # Check for auth token in cookies
    if cookies.get('auth_token'):
        user_id = verify_auth_token(cookies.get('auth_token'))
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
            
            # Create and set auth token in cookies
            token = create_auth_token(user_id)
            cookies.set('auth_token', token)
            
            # Save cookies
            cookies.save()
            
            return True
        else:
            st.error("Invalid username or password")
            return False
            
    return False 