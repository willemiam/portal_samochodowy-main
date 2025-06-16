import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
import pandas as pd
from app import app, db, init_database


@pytest.fixture
def test_app():
    """Create a test Flask application with temporary database."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure test app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DISABLE_AUTH'] = True  # Disable auth for testing
    
    with app.app_context():
        db.create_all()
        yield app
        
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_app):
    """Create a test client for the Flask application."""
    return test_app.test_client()


@pytest.fixture
def app_context(test_app):
    """Create an application context for database operations."""
    with test_app.app_context():
        # Clear all data before each test
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield test_app
        # Clean up after each test
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing database initialization."""
    return pd.DataFrame({
        'Make': ['Toyota', 'BMW', 'Ford'],
        'Model': ['Camry', 'X5', 'Focus'],
        'Year': [2020, 2019, 2021],
        'Fuel Type1': ['Gasoline', 'Diesel', 'Gasoline'],
        'Engine displacement': [2.5, 3.0, 1.6],
        'Typ nadwozia': ['Sedan', 'SUV', 'Hatchback']
    })


@pytest.fixture
def mock_csv_file(sample_csv_data, monkeypatch):
    """Mock CSV file reading for testing."""
    def mock_read_csv(filename):
        if filename == 'final_vehicle_data.csv':
            return sample_csv_data
        raise FileNotFoundError()
    
    monkeypatch.setattr(pd, 'read_csv', mock_read_csv)
