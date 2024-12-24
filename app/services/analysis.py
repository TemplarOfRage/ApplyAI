# app/services/analysis.py
"""
Analysis history services for ApplyAI.
"""

import streamlit as st
from datetime import datetime
import sqlite3
from app.config import get_api_key

def extract_text_from_url(url):
    """Extract text content from a URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        st.error(f"Error extracting text from URL: {str(e)}")
        return None

def analyze_job_posting(job_post, system_prompt, analysis_prompt, temperature=0.7):
    """Analyze job posting using Claude"""
    try:
        client = anthropic.Anthropic(api_key=get_api_key())
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"{analysis_prompt}\n\nJob Posting:\n{job_post}"
            }
        ]
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=temperature,
            messages=messages
        )
        
        return response.content[0].text
        
    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")

def save_analysis(user_id, job_post, analysis):
    """Save analysis to database"""
    try:
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        # Create table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_history
                    (user_id text, job_post text, analysis text, timestamp text)''')
        
        # Insert analysis
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('INSERT INTO analysis_history VALUES (?, ?, ?, ?)',
                 (user_id, job_post, analysis, timestamp))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving analysis: {str(e)}")
        return False
    finally:
        conn.close()

def get_user_analysis_history(user_id):
    """Get analysis history for a user"""
    try:
        conn = sqlite3.connect('applyai.db')
        c = conn.cursor()
        
        c.execute('SELECT job_post, analysis, timestamp FROM analysis_history WHERE user_id = ? ORDER BY timestamp DESC',
                 (user_id,))
        return c.fetchall()
    except Exception as e:
        st.error(f"Error fetching analysis history: {str(e)}")
        return []
    finally:
        conn.close()

def delete_analysis(user_id, timestamp):
    """Delete an analysis from storage"""
    analyses = get_analysis_store()
    
    if user_id in analyses:
        # Filter out the analysis with matching timestamp
        analyses[user_id] = [
            item for item in analyses[user_id] 
            if item['timestamp'] != timestamp
        ]
        
        # Clean up empty user entries
        if not analyses[user_id]:
            del analyses[user_id]
        
        # Force cache update
        get_analysis_store.clear()
        return True
        
    return False