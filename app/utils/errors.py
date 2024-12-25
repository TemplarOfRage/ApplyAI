class APIError(Exception):
    """Base class for API errors"""
    pass

class AnalysisError(APIError):
    """Raised when analysis fails"""
    pass 