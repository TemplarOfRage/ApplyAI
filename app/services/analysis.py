# app/services/analysis.py
"""
Analysis history services for ApplyAI.
"""

import streamlit as st
from datetime import datetime

# In-memory storage for analysis history (replace with database in production)
@st.cache_data(show_spinner=False)
def get_analysis_store():
    """Cache the analysis store to persist across reruns"""
    return {}

def save_analysis(user_id, job_post, analysis):
    """Save an analysis to storage"""
    analyses = get_analysis_store()
    
    # Initialize user's analysis storage if it doesn't exist
    if user_id not in analyses:
        analyses[user_id] = []
    
    # Add new analysis with timestamp
    analyses[user_id].append({
        'job_post': job_post,
        'analysis': analysis,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Keep only the last 10 analyses per user
    analyses[user_id] = analyses[user_id][-10:]
    
    # Force cache update
    get_analysis_store.clear()
    return True

def get_user_analysis_history(user_id):
    """Get analysis history for a user"""
    analyses = get_analysis_store()
    
    if user_id not in analyses:
        return []
    
    # Return list of tuples (job_post, analysis, timestamp)
    # Sort by timestamp in descending order (newest first)
    return [(item['job_post'], item['analysis'], item['timestamp']) 
            for item in sorted(analyses[user_id], 
                             key=lambda x: x['timestamp'], 
                             reverse=True)]

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