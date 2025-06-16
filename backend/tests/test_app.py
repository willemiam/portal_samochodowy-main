"""
Test suite for the Flask marketplace application.
Contains 14 comprehensive tests covering all major functionality.
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
import pandas as pd


def test_app_configuration(test_app):
    """Test 1: Verify Flask app configuration is correct."""
    assert test_app.config['TESTING'] is True
    assert test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    assert test_app.config['DISABLE_AUTH'] is True
    assert 'sqlite' in test_app.config['SQLALCHEMY_DATABASE_URI']


def test_database_initialization_with_csv(app_context, mock_csv_file):
    """Test 2: Verify database initialization loads CSV data correctly."""
    from app import db, init_database
    from models import Car
    
    # Clear any existing data
    db.session.query(Car).delete()
    db.session.commit()
    
    # Test database initialization
    init_database()
    
    # Verify cars were loaded from CSV
    cars = Car.query.all()
    assert len(cars) == 3
    assert any(car.make == 'Toyota' and car.model == 'Camry' for car in cars)
    assert any(car.make == 'BMW' and car.model == 'X5' for car in cars)
    assert any(car.make == 'Ford' and car.model == 'Focus' for car in cars)


def test_database_initialization_missing_csv(app_context):
    """Test 3: Verify graceful handling when CSV file is missing."""
    from app import db, init_database
    
    with patch('pandas.read_csv') as mock_read_csv:
        mock_read_csv.side_effect = FileNotFoundError()
        
        # Should not raise exception
        init_database()
        
        # Database should still be created (tables exist)
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        assert 'users' in table_names
        assert 'cars' in table_names
        assert 'items' in table_names


def test_create_user_success(client, app_context):
    """Test 4: Successfully create a new user."""
    timestamp = str(int(time.time()))
    user_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': f'john.doe.{timestamp}@example.com',
        'password': 'securepassword123'
    }
    
    response = client.post('/api/users', 
                         data=json.dumps(user_data),
                         content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['firstName'] == 'John'
    assert data['lastName'] == 'Doe'
    assert data['email'] == f'john.doe.{timestamp}@example.com'
    assert 'id' in data


def test_create_user_missing_fields(client):
    """Test 5: Handle missing required fields when creating user."""
    user_data = {
        'first_name': 'John',
        'email': 'john.doe@example.com'
        # Missing last_name and password
    }
    
    response = client.post('/api/users',
                         data=json.dumps(user_data),
                         content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Input required field' in data['error']


def test_get_all_users(client, app_context):
    """Test 6: Retrieve all users."""
    from app import db
    from models import Users
    
    # Clear existing users to ensure clean test
    db.session.query(Users).delete()
    db.session.commit()
    
    # Create test users
    timestamp = str(int(time.time()))
    user1 = Users(first_name='Alice', last_name='Smith', 
                 email=f'alice.{timestamp}@example.com', password_hash='hash1')
    user2 = Users(first_name='Bob', last_name='Johnson', 
                 email=f'bob.{timestamp}@example.com', password_hash='hash2')
    
    db.session.add_all([user1, user2])
    db.session.commit()
    
    response = client.get('/api/users')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert any(user['firstName'] == 'Alice' for user in data)
    assert any(user['firstName'] == 'Bob' for user in data)


def test_get_user_by_id(client, app_context):
    """Test 7: Retrieve specific user by ID."""
    from app import db
    from models import Users
    
    timestamp = str(int(time.time()))
    user = Users(first_name='Charlie', last_name='Brown',
                email=f'charlie.{timestamp}@example.com', password_hash='hash')
    db.session.add(user)
    db.session.commit()
    
    response = client.get(f'/api/users/{user.id}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['firstName'] == 'Charlie'
    assert data['lastName'] == 'Brown'
    assert data['email'] == f'charlie.{timestamp}@example.com'


def test_get_user_not_found(client):
    """Test 8: Handle user not found scenario."""
    response = client.get('/api/users/99999')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == 'User not found'


def test_create_item_success(client, app_context):
    """Test 9: Successfully create a new item listing."""
    from app import db
    from models import Users
    
    # Create test user
    timestamp = str(int(time.time()))
    user = Users(first_name='Test', last_name='User',
                email=f'test.{timestamp}@example.com', password_hash='hash')
    db.session.add(user)
    db.session.commit()
    
    item_data = {
        'make': 'Toyota',
        'model': 'Corolla',
        'year': 2020,
        'price': 25000,
        'car_mileage': 50000,
        'color': 'Blue',
        'description': 'Great car in excellent condition',
        'fuel_type': 'Gasoline',
        'engine_displacement': 1.8,
        'car_size_class': 'Compact'
    }
    
    # Mock authentication
    with patch('routes.requires_auth') as mock_auth:
        # Create a mock decorator that just sets the user
        def mock_decorator(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.current_user = user
                return f(*args, **kwargs)
            return wrapper
        mock_auth.return_value = mock_decorator
        mock_auth.side_effect = lambda f: mock_decorator
        
        response = client.post('/api/items',
                             data=json.dumps(item_data),
                             content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['price'] == 25000
    assert data['color'] == 'Blue'
    assert data['description'] == 'Great car in excellent condition'


def test_get_all_items(client, app_context):
    """Test 10: Retrieve all items with car details."""
    from app import db
    from models import Users, Car, Items
    
    # Clear existing data
    db.session.query(Items).delete()
    db.session.query(Car).delete()
    db.session.query(Users).delete()
    db.session.commit()
    
    # Create test data
    timestamp = str(int(time.time()))
    user = Users(first_name='Test', last_name='User',
                email=f'test.items.{timestamp}@example.com', password_hash='hash')
    car = Car(make='Honda', model='Civic', year=2019, fuel_type='Gasoline')
    
    db.session.add_all([user, car])
    db.session.commit()
    
    item = Items(user_id=user.id, car_id=car.id, price=20000,
                car_mileage=30000, color='Red', description='Nice car')
    
    db.session.add(item)
    db.session.commit()
    
    response = client.get('/api/items')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['make'] == 'Honda'
    assert data[0]['model'] == 'Civic'
    assert data[0]['price'] == 20000
    assert data[0]['color'] == 'Red'


def test_filter_items_by_make(client, app_context):
    """Test 11: Filter items by car make."""
    from app import db
    from models import Users, Car, Items
    
    # Clear existing data
    db.session.query(Items).delete()
    db.session.query(Car).delete()
    db.session.query(Users).delete()
    db.session.commit()
    
    # Create test data
    timestamp = str(int(time.time()))
    user = Users(first_name='Test', last_name='User',
                email=f'test.filter.{timestamp}@example.com', password_hash='hash')
    car1 = Car(make='Toyota', model='Camry', year=2020, fuel_type='Gasoline')
    car2 = Car(make='Honda', model='Accord', year=2019, fuel_type='Gasoline')
    
    db.session.add_all([user, car1, car2])
    db.session.commit()
    
    item1 = Items(user_id=user.id, car_id=car1.id, price=25000,
                 car_mileage=40000, color='White', description='Toyota car')
    item2 = Items(user_id=user.id, car_id=car2.id, price=23000,
                 car_mileage=45000, color='Black', description='Honda car')
    
    db.session.add_all([item1, item2])
    db.session.commit()
    
    response = client.get('/api/items/filter?make=Toyota')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['make'] == 'Toyota'
    assert data[0]['model'] == 'Camry'


def test_get_car_makes(client, app_context):
    """Test 12: Retrieve distinct car makes."""
    from app import db
    from models import Car
    
    # Clear existing cars
    db.session.query(Car).delete()
    db.session.commit()
    
    # Create test cars
    cars = [
        Car(make='Toyota', model='Camry', year=2020, fuel_type='Gasoline'),
        Car(make='Honda', model='Civic', year=2019, fuel_type='Gasoline'),
        Car(make='Toyota', model='Corolla', year=2021, fuel_type='Gasoline'),
    ]
    
    db.session.add_all(cars)
    db.session.commit()
    
    response = client.get('/api/cars/makes')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Toyota' in data
    assert 'Honda' in data
    assert len(set(data)) == len(data)  # No duplicates


def test_get_car_models_by_make(client, app_context):
    """Test 13: Retrieve car models filtered by make."""
    from app import db
    from models import Car
    
    # Clear existing cars
    db.session.query(Car).delete()
    db.session.commit()
    
    # Create test cars
    cars = [
        Car(make='Toyota', model='Camry', year=2020, fuel_type='Gasoline'),
        Car(make='Toyota', model='Corolla', year=2021, fuel_type='Gasoline'),
        Car(make='Honda', model='Civic', year=2019, fuel_type='Gasoline'),
    ]
    
    db.session.add_all(cars)
    db.session.commit()
    
    response = client.get('/api/cars/models?make=Toyota')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Camry' in data
    assert 'Corolla' in data
    assert 'Civic' not in data
    assert len(data) == 2


def test_invalid_filter_year(client):
    """Test 14: Handle invalid year format in filter."""
    response = client.get('/api/items/filter?year=invalid_year')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid year format'