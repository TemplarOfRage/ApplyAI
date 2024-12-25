# utils/__init__.py
"""
Utility module for Job Buddy application.
This module provides package-level imports and initialization for utility functions.
"""

from .errors import APIError, AnalysisError

__all__ = [
    'APIError',
    'AnalysisError',
]