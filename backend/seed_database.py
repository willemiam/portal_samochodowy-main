#!/usr/bin/env python3
"""
Database seeding script for the marketplace application.
This script creates sample users, cars, and items for development and testing.
"""

import sys
import os
from datetime import datetime

# Import Flask app and models
try:
    from app import app, db
    from models import Users, Car, Items
    print("✅ Successfully imported app and models")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def seed_database():
    """Seed the database with sample data"""
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Check if we already have sample data
        existing_items = Items.query.count()
        if existing_items > 0:
            print(f"Database already contains {existing_items} items. Skipping seeding.")
            return
        
        # Create sample users
        print("Creating sample users...")
        users_data = [
            {
                'first_name': 'Jan',
                'last_name': 'Kowalski',
                'email': 'jan.kowalski@example.com',
                'password': 'password123'
            },
            {
                'first_name': 'Anna',
                'last_name': 'Nowak',
                'email': 'anna.nowak@example.com',
                'password': 'password123'
            },
            {
                'first_name': 'Piotr',
                'last_name': 'Wiśniewski',
                'email': 'piotr.wisniewski@example.com',
                'password': 'password123'
            }
        ]
        
        created_users = []
        for user_data in users_data:
            # Check if user already exists
            existing_user = Users.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = Users(
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                created_users.append(user)
                print(f"Created user: {user_data['first_name']} {user_data['last_name']}")
            else:
                created_users.append(existing_user)
                print(f"User already exists: {user_data['email']}")
        
        # Commit users first
        db.session.commit()
        
        # Create sample cars
        print("Creating sample cars...")
        cars_data = [
            {
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2019,
                'fuel_type': 'Benzyna',
                'engine_displacement': 1.6,
                'car_size_class': 'Sedan',
                'doors': 4,
                'transmission': 'Manualna',
                'drive_type': 'FWD'
            },
            {
                'make': 'BMW',
                'model': 'X3',
                'year': 2020,
                'fuel_type': 'Diesel',
                'engine_displacement': 2.0,
                'car_size_class': 'SUV',
                'doors': 5,
                'transmission': 'Automatyczna',
                'drive_type': 'AWD'
            },
            {
                'make': 'Volkswagen',
                'model': 'Golf',
                'year': 2018,
                'fuel_type': 'Benzyna',
                'engine_displacement': 1.4,
                'car_size_class': 'Hatchback',
                'doors': 5,
                'transmission': 'Manualna',
                'drive_type': 'FWD'
            }
        ]
        
        created_cars = []
        for car_data in cars_data:
            # Check if car already exists
            existing_car = Car.query.filter_by(
                make=car_data['make'],
                model=car_data['model'],
                year=car_data['year']
            ).first()
            
            if not existing_car:
                car = Car(**car_data)
                db.session.add(car)
                created_cars.append(car)
                print(f"Created car: {car_data['make']} {car_data['model']} ({car_data['year']})")
            else:
                created_cars.append(existing_car)
                print(f"Car already exists: {car_data['make']} {car_data['model']} ({car_data['year']})")
        
        # Commit cars
        db.session.commit()
        
        # Create sample items (listings)
        print("Creating sample items...")
        items_data = [
            {
                'user': created_users[0],
                'car': created_cars[0],
                'price': 45000,
                'condition': 'Bardzo dobry',
                'location': 'Warszawa',
                'description': 'Świetnie utrzymana Toyota Corolla z 2019 roku. Auto serwisowane w ASO, jeden właściciel. Bogata wersja wyposażenia z klimatyzacją automatyczną, systemem multimedialnym i kamerą cofania.',
                'attributes': {
                    'car_mileage': 85000,
                    'color': 'Srebrny',
                    'features': ['Klimatyzacja automatyczna', 'System multimedialny', 'Kamera cofania'],
                    'first_registration': '2019-03-15'
                }
            },
            {
                'user': created_users[1],
                'car': created_cars[1],
                'price': 180000,
                'condition': 'Idealny',
                'location': 'Kraków',
                'description': 'BMW X3 2020 w idealnym stanie. Auto kupione w polskim salonie, wszystkie serwisy w ASO. Pełne wyposażenie premium z pakietem M-Sport, skórzaną tapicerką i panoramicznym dachem.',
                'attributes': {
                    'car_mileage': 35000,
                    'color': 'Czarny',
                    'features': ['Pakiet M-Sport', 'Skórzana tapicerka', 'Panoramiczny dach', 'Nawigacja GPS', 'Ksenony'],
                    'first_registration': '2020-06-20'
                }
            },
            {
                'user': created_users[2],
                'car': created_cars[2],
                'price': 52000,
                'condition': 'Dobry',
                'location': 'Gdańsk',
                'description': 'Volkswagen Golf VII 1.4 TSI z 2018 roku. Ekonomiczny i niezawodny samochód idealny do miasta. Regularne serwisy, wszystkie dokumenty dostępne. Wymienione opony na nowe.',
                'attributes': {
                    'car_mileage': 120000,
                    'color': 'Biały',
                    'features': ['Klimatyzacja', 'Radio CD', 'Komputer pokładowy', 'Elektryczne szyby'],
                    'first_registration': '2018-09-10'
                }
            }
        ]
        
        for item_data in items_data:
            item = Items(
                user_id=item_data['user'].id,
                car_id=item_data['car'].id,
                price=item_data['price'],
                condition=item_data['condition'],
                location=item_data['location'],
                description=item_data['description'],
                attributes=item_data['attributes'],
                is_active=True
            )
            db.session.add(item)
            print(f"Created item: {item_data['car'].make} {item_data['car'].model} - {item_data['price']} PLN")
        
        # Final commit
        db.session.commit()
        
        print("\n✅ Database seeding completed successfully!")
        print(f"Created {len(created_users)} users")
        print(f"Created {len(created_cars)} cars")
        print(f"Created {len(items_data)} items")

def clear_sample_data():
    """Clear all sample data from the database"""
    with app.app_context():
        print("Clearing sample data...")
        
        # Delete items first (due to foreign keys)
        Items.query.delete()
        
        # Delete cars and users
        Car.query.delete()
        Users.query.delete()
        
        db.session.commit()
        print("✅ Sample data cleared!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_sample_data()
    else:
        seed_database()
