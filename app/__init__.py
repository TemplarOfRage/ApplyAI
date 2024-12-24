# app/__init__.py
"""
Initialization for the Job Buddy application package.
"""

# Import key configuration functions to make them easily accessible
from .config import (
    get_api_key, 
    get_database_url, 
    get_credentials, 
    init_streamlit_config
)

# You can add any package-level initialization here if needed