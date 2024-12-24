# app/__init__.py
"""
Initialization module for Job Buddy application.
Sets up core application components and configurations.
"""

from .config import load_config, AppConfig
from .database.operations import DatabaseManager
from .services.auth import AuthenticationService
from .services.resume import ResumeService
from .services.analysis import AnalysisService

# Initialize core application components
config = load_config()
db_manager = DatabaseManager(db_path=config.db_path)

# Initialize repositories and services
user_repository = UserRepository(db_manager)
resume_repository = ResumeRepository(db_manager)
analysis_repository = AnalysisRepository(db_manager)

auth_service = AuthenticationService(user_repository)
resume_service = ResumeService(resume_repository)
analysis_service = AnalysisService(analysis_repository)

# You can add any application-wide initialization here
def initialize_app():
    """
    Initialize the Job Buddy application.
    Sets up database, checks configurations, etc.
    """
    # Initialize database
    db_manager.init_db()
    
    # Perform any startup checks or validations
    # For example, check API keys, database connection, etc.
    
    return {
        'config': config,
        'auth_service': auth_service,
        'resume_service': resume_service,
        'analysis_service': analysis_service
    }

__all__ = [
    'config',
    'auth_service',
    'resume_service',
    'analysis_service',
    'initialize_app'
]