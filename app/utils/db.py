def create_tables():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                resume_name TEXT NOT NULL,
                job_content TEXT NOT NULL,
                match_score INTEGER,
                overall_feedback TEXT,
                qualifications TEXT,
                missing_skills TEXT,
                improvements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

def save_analysis(user_id, resume_name, job_content, analysis_results):
    """Save analysis results to database"""
    sections = parse_analysis_sections(analysis_results)
    
    with get_db() as conn:
        conn.execute("""
            INSERT INTO analyses (
                user_id, resume_name, job_content, match_score, 
                overall_feedback, qualifications, missing_skills, improvements
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, resume_name, job_content, sections['match_score'],
            sections.get('overall', ''), sections.get('qualifications', ''),
            sections.get('missing', ''), sections.get('improvements', '')
        ))

def get_user_analyses(user_id):
    """Get all analyses for a user"""
    with get_db() as conn:
        return conn.execute("""
            SELECT * FROM analyses 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,)).fetchall() 