import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app modules after path is set
from app import create_app
from app.models.database import init_db

@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing"""
    app = create_app({
        'TESTING': True,
        'DATABASE_PATH': 'test_inventory.db',
        'SECRET_KEY': 'test_secret_key'
    })
    
    # Establish application context
    with app.app_context():
        yield app

@pytest.fixture(scope="session")
def client(app):
    """A test client for the app"""
    return app.test_client()

@pytest.fixture(scope="session")
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner() 