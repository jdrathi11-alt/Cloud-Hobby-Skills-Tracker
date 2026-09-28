"""Database configuration notes.
Local mode uses SQLite through SQLAlchemy. Cloud mode uses the same ORM with a
PostgreSQL DATABASE_URL, keeping application code portable between environments.
"""
import os

def database_url():
    return os.getenv('DATABASE_URL','sqlite:///hobby_tracker.db')
