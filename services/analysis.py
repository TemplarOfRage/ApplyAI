from .auth import get_connection

def save_analysis(user_id: str, job_post: str, analysis: str):
    """Save an analysis to the database"""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO analysis_history 
                     (user_id, job_post, analysis, created_at)
                     VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                 (user_id, job_post, analysis))
        conn.commit()

def get_user_analysis_history(user_id: str):
    """Get analysis history for a user"""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT job_post, analysis, created_at 
                    FROM analysis_history 
                    WHERE user_id = ?
                    ORDER BY created_at DESC''', (user_id,))
        return c.fetchall() 