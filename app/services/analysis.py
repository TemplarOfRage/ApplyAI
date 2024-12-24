# app/services/analysis.py
"""
Analysis history services for ApplyAI.
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Tuple
from datetime import datetime

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

def save_analysis(user_id: str, job_post: str, analysis: str):
    """
    Save a job analysis to the user's history.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO analysis_history 
                     (user_id, job_post, analysis, created_at)
                     VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                 (user_id, job_post, analysis))
        conn.commit()

def get_user_analysis_history(user_id: str) -> List[Tuple[str, str, datetime]]:
    """
    Retrieve analysis history for a specific user.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT job_post, analysis, created_at 
                    FROM analysis_history 
                    WHERE user_id = ?
                    ORDER BY created_at DESC''', (user_id,))
        return c.fetchall()