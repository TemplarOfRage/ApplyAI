import streamlit as st
import sqlite3
from .db import get_db

def check_password(username, password):
    """Check if username/password combo is valid"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        return user[0] if user else None

def check_auth():
    """Handle login flow and session management"""
    if 'user_id' not in st.session_state:
        st.markdown("### Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user_id = check_password(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.error("Invalid username or password")
        return False
    return True 