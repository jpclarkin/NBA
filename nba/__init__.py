"""
NBA Data Science Infrastructure

A comprehensive data pipeline for NBA analytics including:
- Data ingestion from multiple sources
- Feature engineering and ML model training
- Historical analysis and visualization
- Integration with MLflow and Feast
"""

__version__ = "0.1.0"
__author__ = "Data Science Team"

from .config import get_settings
from .db.session import get_session_factory, create_all_tables

__all__ = [
    "get_settings",
    "get_session_factory", 
    "create_all_tables"
]
