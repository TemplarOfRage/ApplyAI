def create_tables():
    """Create all necessary database tables"""
    with get_db() as conn:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Resumes table with user relationship
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                file_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, filename)
            )
        """)
        
        # Analyses table to store analysis history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                resume_id INTEGER NOT NULL,
                job_content TEXT NOT NULL,
                analysis_result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (resume_id) REFERENCES resumes(id)
            )
        """)

def save_resume(user_id, filename, content, file_type):
    """Save or update a resume"""
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO resumes (user_id, filename, content, file_type)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, filename) 
                DO UPDATE SET 
                    content = excluded.content,
                    file_type = excluded.file_type,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, filename, content, file_type))
            return True
        except Exception as e:
            print(f"Error saving resume: {e}")
            return False

def get_user_resumes(user_id):
    """Get all resumes for a user"""
    with get_db() as conn:
        return conn.execute("""
            SELECT filename, content, file_type, created_at, updated_at
            FROM resumes 
            WHERE user_id = ?
            ORDER BY updated_at DESC
        """, (user_id,)).fetchall()

def delete_resume(user_id, filename):
    """Delete a specific resume"""
    with get_db() as conn:
        try:
            conn.execute("""
                DELETE FROM resumes 
                WHERE user_id = ? AND filename = ?
            """, (user_id, filename))
            return True
        except Exception as e:
            print(f"Error deleting resume: {e}")
            return False

def get_resume_history(user_id, filename):
    """Get analysis history for a specific resume"""
    with get_db() as conn:
        return conn.execute("""
            SELECT a.created_at, a.job_content, a.analysis_result
            FROM analyses a
            JOIN resumes r ON a.resume_id = r.id
            WHERE r.user_id = ? AND r.filename = ?
            ORDER BY a.created_at DESC
        """, (user_id, filename)).fetchall()

def save_analysis(user_id, filename, job_content, analysis_result):
    """Save an analysis result"""
    with get_db() as conn:
        try:
            # Get resume_id
            resume_id = conn.execute("""
                SELECT id FROM resumes
                WHERE user_id = ? AND filename = ?
            """, (user_id, filename)).fetchone()[0]
            
            # Save analysis
            conn.execute("""
                INSERT INTO analyses (user_id, resume_id, job_content, analysis_result)
                VALUES (?, ?, ?, ?)
            """, (user_id, resume_id, job_content, analysis_result))
            return True
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return False 