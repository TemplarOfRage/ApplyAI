import sqlite3
from contextlib import contextmanager
from datetime import datetime
import bcrypt
import uuid
from typing import Optional, List, Tuple
import streamlit as st

# Database connection management
@contextmanager
def get_connection():
    """Create and manage database connection."""
    conn = sqlite3.connect('applyai.db', check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database with required tables."""
    with get_connection() as conn:
        c = conn.cursor()
        
        # First drop existing tables to ensure clean initialization
        c.execute('DROP TABLE IF EXISTS analysis_history')
        c.execute('DROP TABLE IF EXISTS resumes')
        c.execute('DROP TABLE IF EXISTS users')
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        # Create resumes table
        c.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                name TEXT,
                content TEXT,
                file_type TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Create analysis_history table
        c.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                job_post TEXT,
                analysis TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Create indexes for performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis_history(user_id)')
        
        conn.commit()

# User management functions
def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_user(username: str, password: str) -> Optional[str]:
    """Create a new user in the database."""
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    
    with get_connection() as conn:
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO users (id, username, password_hash, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, password_hash))
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None

def authenticate_user(username: str, password: str) -> Optional[str]:
    """Authenticate a user and return their user_id if successful."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        if result and verify_password(password, result[1]):
            return result[0]
    return None

# Resume management functions
def save_resume(user_id: str, name: str, content: str, file_type: str):
    """Save or update a resume in the database."""
    with get_connection() as conn:
        c = conn.cursor()
        # Check if resume with same name exists
        c.execute('''
            SELECT id FROM resumes 
            WHERE user_id = ? AND name = ?
        ''', (user_id, name))
        existing = c.fetchone()
        
        if existing:
            # Update existing resume
            c.execute('''
                UPDATE resumes 
                SET content = ?, file_type = ?, created_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND name = ?
            ''', (content, file_type, user_id, name))
        else:
            # Create new resume
            c.execute('''
                INSERT INTO resumes (user_id, name, content, file_type, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, name, content, file_type))
        conn.commit()

def get_user_resumes(user_id: str) -> List[Tuple[str, str, str]]:
    """Get all resumes for a user."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT name, content, file_type 
            FROM resumes 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        return c.fetchall()

def delete_resume(user_id: str, name: str):
    """Delete a resume from the database."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            DELETE FROM resumes 
            WHERE user_id = ? AND name = ?
        ''', (user_id, name))
        conn.commit()

# Analysis management functions
def save_analysis(user_id: str, job_post: str, analysis: str):
    """Save a job analysis to the database."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO analysis_history (user_id, job_post, analysis, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, job_post, analysis))
        conn.commit()

def get_user_analysis_history(user_id: str) -> List[Tuple[str, str, datetime]]:
    """Get analysis history for a user."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT job_post, analysis, created_at 
            FROM analysis_history 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        return c.fetchall()

# Initialize database when module is imported
if not hasattr(st, '_db_initialized'):
    init_db()
    setattr(st, '_db_initialized', True)