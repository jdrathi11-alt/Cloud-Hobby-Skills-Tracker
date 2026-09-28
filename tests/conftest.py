import os
import shutil
import sys
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Make the backend directory importable when pytest is executed from the
# project root.
#
# Project structure:
#
# Cloud-Hobby-Skills-Tracker/
# ├── backend/
# │   └── app/
# │       └── __init__.py
# └── tests/
#     └── conftest.py
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# db is defined directly inside backend/app/__init__.py
from app import create_app, db


@pytest.fixture()
def client():
    """
    Create an isolated Flask test client.

    Each test receives:
    - a fresh temporary SQLite database
    - a temporary upload directory
    - TESTING mode enabled
    - a test JWT secret

    The database connection is disposed after the test so that
    Windows can safely remove the temporary SQLite file.
    """

    # -----------------------------------------------------------------------
    # Create a temporary SQLite database.
    # -----------------------------------------------------------------------
    fd, database_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # -----------------------------------------------------------------------
    # Create a temporary upload directory.
    # -----------------------------------------------------------------------
    upload_folder = tempfile.mkdtemp()

    # -----------------------------------------------------------------------
    # Create the Flask application using the test configuration.
    # -----------------------------------------------------------------------
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + database_path,
        "UPLOAD_FOLDER": upload_folder,
        "JWT_SECRET": "test-secret",
    })

    # -----------------------------------------------------------------------
    # Create a completely clean database for this test.
    # -----------------------------------------------------------------------
    with app.app_context():
        db.drop_all()
        db.create_all()

    # -----------------------------------------------------------------------
    # Run the test using Flask's test client.
    # -----------------------------------------------------------------------
    with app.test_client() as test_client:
        yield test_client

    # -----------------------------------------------------------------------
    # IMPORTANT FOR WINDOWS:
    #
    # SQLAlchemy may still have the SQLite file open after the test.
    # Remove the session and dispose of the engine before deleting it.
    # -----------------------------------------------------------------------
    with app.app_context():
        db.session.remove()
        db.engine.dispose()

    # -----------------------------------------------------------------------
    # Delete the temporary SQLite database.
    # -----------------------------------------------------------------------
    try:
        if os.path.exists(database_path):
            os.remove(database_path)
    except PermissionError:
        # Windows may occasionally keep the file locked briefly.
        # Leaving the temporary file is safer than failing the test suite.
        pass

    # -----------------------------------------------------------------------
    # Delete the temporary upload directory.
    # -----------------------------------------------------------------------
    shutil.rmtree(upload_folder, ignore_errors=True)