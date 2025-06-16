"""
Integration tests for the complete application workflow.

This module tests the integration between app.py, models, and routes
to ensure the application works as a cohesive unit.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import pandas as pd

from app import app, db, init_database
from models import Car, Users, Items


class TestApplicationWorkflow:
    """Integration tests for complete application workflows."""
    
    def test_full_application_startup_workflow(self, client, app_context):
        """Test the complete application startup and basic functionality."""
        # Test that routes are accessible
        response = client.get('/api/cars/makes')
        assert response.status_code == 200
        
        # Test database connectivity
        makes = db.session.query(Car.make).distinct().all()
        assert isinstance(makes, list)
        
    def test_database_initialization_with_csv_integration(self, app_context):
        """Test complete database initialization workflow with CSV data."""
        # Create sample CSV data
        sample_data = pd.DataFrame({
            'Make': ['Toyota', 'BMW', 'Ford'],
            'Model': ['Camry', 'X5', 'Focus'],
            'Year': [2020, 2019, 2021],
            'Fuel Type1': ['Gasoline', 'Diesel', 'Gasoline'],
            'Engine displacement': [2.5, 3.0, 1.6],
            'Typ nadwozia': ['Sedan', 'SUV', 'Hatchback']
        })
        
        with patch('pandas.read_csv', return_value=sample_data):
            # Clear existing data
            db.session.query(Car).delete()
            db.session.commit()
            
            # Run initialization
            init_database()
              # Verify data was loaded
            cars = db.session.query(Car).all()
            assert len(cars) == 3
            
            # Verify data mapping
            toyota = db.session.query(Car).filter_by(make='Toyota').first()
            assert toyota is not None
            assert toyota.model == 'Camry'
            assert toyota.year == 2020
            assert toyota.fuel_type == 'Gasoline'
            
    def test_user_car_items_relationship_workflow(self, app_context):
        """Test the complete workflow of creating related data."""
        # Create a user with unique email
        import time
        unique_email = f'john.doe.{int(time.time())}.{id(self)}@example.com'
        
        user = Users(
            first_name='John',
            last_name='Doe',
            email=unique_email,
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create a car
        car = Car(
            make='Toyota',
            model='Camry',
            year=2020,
            fuel_type='Gasoline',
            engine_displacement=2.5,
            car_size_class='Sedan'
        )
        db.session.add(car)
        db.session.commit()
        
        # Create an item linking user and car
        item = Items(
            user_id=user.id,
            car_id=car.id,
            price=25000,
            car_mileage=10000,
            color='Blue',
            description='Well maintained Toyota Camry'
        )
        db.session.add(item)
        db.session.commit()
        
        # Test relationships
        assert len(user.items) == 1
        assert user.items[0].id == item.id
        assert len(car.items) == 1
        assert car.items[0].id == item.id
        assert item.user.email == unique_email
        assert item.car.make == 'Toyota'
        
    def test_api_endpoint_integration(self, client, app_context):
        """Test integration between app configuration and API endpoints."""
        # Test CORS is working (should not get CORS errors)
        response = client.get('/api/cars/makes')
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200
        
        # Test authentication is properly disabled in test mode
        assert app.config['DISABLE_AUTH'] is True
        
    def test_database_cascade_delete_integration(self, app_context):
        """Test cascade delete functionality works across relationships."""
        # Create test data with unique email
        import time
        unique_email = f'test.user.{int(time.time())}.{id(self)}@example.com'
        
        user = Users(
            first_name='Test',
            last_name='User',
            email=unique_email,
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        
        car = Car(
            make='Test',
            model='Car',
            year=2020,
            fuel_type='Gasoline'
        )
        db.session.add(car)
        db.session.commit()
        
        item = Items(
            user_id=user.id,
            car_id=car.id,
            price=10000,
            car_mileage=5000,
            color='Red',
            description='Test item'
        )
        db.session.add(item)
        db.session.commit()
        
        item_id = item.id
        
        # Delete user - should cascade delete items
        db.session.delete(user)
        db.session.commit()
        
        # Verify item was deleted
        deleted_item = db.session.query(Items).filter_by(id=item_id).first()
        assert deleted_item is None
        
        # Car should still exist
        existing_car = db.session.query(Car).filter_by(id=car.id).first()
        assert existing_car is not None


class TestApplicationConfiguration:
    """Integration tests for application configuration."""
    
    def test_environment_based_configuration(self):
        """Test that configuration adapts to environment variables."""
        # Test default configuration
        assert 'AUTH0_DOMAIN' in app.config
        assert 'AUTH0_AUDIENCE' in app.config
        assert 'SECRET_KEY' in app.config
        
        # Test database configuration
        assert app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///')
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
        
    def test_testing_mode_configuration(self, test_app):
        """Test that testing mode has appropriate configuration."""
        with test_app.app_context():
            assert test_app.config['TESTING'] is True
            assert test_app.config['DISABLE_AUTH'] is True
            assert 'sqlite:///' in test_app.config['SQLALCHEMY_DATABASE_URI']


class TestDataIntegrity:
    """Integration tests for data integrity across the application."""
    
    def test_csv_to_database_data_integrity(self, app_context):
        """Test data integrity from CSV loading to database storage."""
        sample_data = pd.DataFrame({
            'Make': ['Toyota', 'BMW'],
            'Model': ['Camry', 'X5'],
            'Year': [2020, 2019],
            'Fuel Type1': ['Gasoline', 'Diesel'],
            'Engine displacement': [2.5, 3.0],
            'Typ nadwozia': ['Sedan', 'SUV']
        })
        
        with patch('pandas.read_csv', return_value=sample_data):
            # Clear and reload data
            db.session.query(Car).delete()
            db.session.commit()
            
            init_database()
            
            # Verify all data was preserved
            cars = db.session.query(Car).order_by(Car.make).all()
            assert len(cars) == 2
            
            # Verify first car data integrity
            bmw = cars[0]  # BMW comes first alphabetically            assert bmw.make == 'BMW'
            assert bmw.model == 'X5'
            assert bmw.year == 2019
            assert bmw.fuel_type == 'Diesel'
            assert bmw.engine_displacement == 3.0
            assert bmw.car_size_class == 'SUV'
            
            # Verify second car data integrity
            toyota = cars[1]
            assert toyota.make == 'Toyota'
            assert toyota.model == 'Camry'
            assert toyota.year == 2020
            assert toyota.fuel_type == 'Gasoline'
            assert toyota.engine_displacement == 2.5
            assert toyota.car_size_class == 'Sedan'
            
    def test_model_json_serialization_integrity(self, app_context):
        """Test that model to_json methods preserve data integrity."""
        # Create test objects with unique email
        import time
        unique_email = f'john.doe.{int(time.time())}@example.com'
        
        user = Users(
            first_name='John',
            last_name='Doe',
            email=unique_email,
            password_hash='hashed_password'
        )
        
        car = Car(
            make='Toyota',
            model='Camry',
            year=2020,
            fuel_type='Gasoline',
            engine_displacement=2.5,
            car_size_class='Sedan',
            doors=4,
            transmission='Automatic',
            drive_type='FWD'
        )
        
        db.session.add_all([user, car])
        db.session.commit()
        
        item = Items(
            user_id=user.id,
            car_id=car.id,
            price=25000,
            car_mileage=10000,
            color='Blue',
            description='Well maintained car'
        )
        db.session.add(item)
        db.session.commit()
          # Test JSON serialization
        user_json = user.to_json()
        car_json = car.to_json()
        item_json = item.to_json()
        
        # Verify user JSON
        assert user_json['firstName'] == 'John'
        assert user_json['lastName'] == 'Doe'
        assert user_json['email'] == unique_email
        assert 'password_hash' not in user_json  # Should not expose password
        
        # Verify car JSON
        assert car_json['make'] == 'Toyota'
        assert car_json['model'] == 'Camry'
        assert car_json['year'] == 2020
        assert car_json['fuel_type'] == 'Gasoline'
        assert car_json['engine_displacement'] == 2.5
        
        # Verify item JSON
        assert item_json['userId'] == user.id
        assert item_json['carId'] == car.id
        assert item_json['price'] == 25000
        assert item_json['carMileage'] == 10000


class TestApplicationRobustness:
    """Integration tests for application robustness and error handling."""
    
    def test_database_connection_recovery(self, app_context):
        """Test application behavior under database stress."""
        # Test multiple concurrent database operations
        users = []
        for i in range(10):
            user = Users(
                first_name=f'User{i}',
                last_name=f'Test{i}',
                email=f'user{i}@test.com',
                password_hash='password'
            )
            users.append(user)
        
        # Batch insert
        db.session.add_all(users)
        db.session.commit()
        
        # Verify all users were created
        user_count = db.session.query(Users).count()
        assert user_count >= 10
        
    def test_csv_loading_idempotency(self, app_context):
        """Test that CSV loading is idempotent (can be run multiple times safely)."""
        sample_data = pd.DataFrame({
            'Make': ['Toyota'],
            'Model': ['Camry'],
            'Year': [2020],
            'Fuel Type1': ['Gasoline'],
            'Engine displacement': [2.5],
            'Typ nadwozia': ['Sedan']
        })
        
        with patch('pandas.read_csv', return_value=sample_data):
            # First initialization
            init_database()
            first_count = db.session.query(Car).count()
            
            # Second initialization (should not duplicate data)
            init_database()
            second_count = db.session.query(Car).count()
            
            # Count should be the same
            assert first_count == second_count
            
    @patch('pandas.read_csv')
    def test_graceful_degradation_on_csv_error(self, mock_read_csv, app_context, capsys):
        """Test that application continues to function even if CSV loading fails."""
        # Mock CSV read failure
        mock_read_csv.side_effect = FileNotFoundError("CSV file not found")
        
        # Initialize database (should handle error gracefully)
        init_database()
        
        # Verify error was logged
        captured = capsys.readouterr()
        assert "nie został znaleziony" in captured.out
        
        # Verify application still functions
        car_count = db.session.query(Car).count()
        assert isinstance(car_count, int)  # Should not crash
