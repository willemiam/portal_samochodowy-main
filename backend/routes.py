from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash
from app import app, db
from models import *
from models import Car


#ENDPOINT UŻYTKOWNIKÓW

#GET zwraca wszystich użytkowników POST tworzy nowego użytkownika
@app.route('/api/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = Users.query.all()
        result = [user.to_json() for user in users]
        return jsonify(result), 200

    if request.method == 'POST':
        try:
            data = request.json

            required_fields = ['first_name', 'last_name', 'email', 'password']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Input required field {field}'}), 400

            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            password = data.get('password')

            password_hash = generate_password_hash(password)

            new_user = Users(first_name=first_name, last_name=last_name, email=email, password_hash=password_hash)

            db.session.add(new_user)
            db.session.commit()

            return jsonify(new_user.to_json()), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
#Zwraca konkretnego użytkownika
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_json()), 200

#Edycja użytkownika
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify(user.to_json()), 200

#Usuwanie użytkownika
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


#ENDPOINT OGŁOSZEŃ

#Tworzenie nowego ogłoszenia
@app.route('/api/items', methods=['POST'])
def create_item():
    try:
        data = request.json

        required_fields = ['user_id', 'make', 'model', 'year', 'price', 'car_mileage', 'color', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Input required field {field}'}), 400

        user_id = data.get('user_id')
        make = data.get('make')
        model = data.get('model')
        year = data.get('year')
        price = data.get('price')
        car_mileage = data.get('car_mileage')
        color = data.get('color')
        description = data.get('description')

        # Sprawdzamy, czy samochód już istnieje w bazie (np. marka + model + rok)
        existing_car = Car.query.filter_by(make=make, model=model, year=year).first()

        if not existing_car:
            # Tworzymy nowy samochód
            new_car = Car(
                make=make,
                model=model,
                year=year,
                fuel_type=data.get('fuel_type'),
                engine_displacement=data.get('engine_displacement'),
                car_size_class=data.get('car_size_class'),
                doors=data.get('doors'),
                transmission=data.get('transmission'),
                drive_type=data.get('drive_type')
            )
            db.session.add(new_car)
            db.session.commit()
            car_id = new_car.id
        else:
            car_id = existing_car.id

        # Tworzymy ogłoszenie
        new_item = Items(
            user_id=user_id,
            car_id=car_id,
            price=price,
            car_mileage=car_mileage,
            color=color,
            description=description
        )

        db.session.add(new_item)
        db.session.commit()

        return jsonify(new_item.to_json()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

#Zwraca wszystkie ogłoszenie
@app.route('/api/items', methods=['GET'])
def get_all_items():
    items = db.session.query(Items, Car).join(Car, Items.car_id == Car.id).all()

    result = []
    for item, car in items:
        result.append({
            "id": item.id,
            "userId": item.user_id,
            "carId": item.car_id,
            "make": car.make,  # Dodajemy markę samochodu
            "model": car.model,  # Dodajemy model samochodu
            "year": car.year,
            "price": item.price,
            "carMileage": item.car_mileage,
            "color": item.color,
            "description": item.description,
            "createdAt": item.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(result), 200


#Zwraca konkretne ogłoszenie
@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Items.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(item.to_json()), 200

#Edycja ogłoszenia
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    user_id = data.get('user_id')  # Pobieramy ID użytkownika, który chce edytować

    item = Items.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    # Sprawdzamy, czy użytkownik jest właścicielem ogłoszenia
    if item.user_id != user_id:
        return jsonify({'error': 'You are not authorized to edit this item'}), 403

    # Aktualizacja danych (tylko wybrane pola)
    if 'price' in data:
        item.price = data['price']
    if 'car_mileage' in data:
        item.car_mileage = data['car_mileage']
    if 'color' in data:
        item.color = data['color']
    if 'description' in data:
        item.description = data['description']

    db.session.commit()
    return jsonify({'message': 'Item updated successfully', 'item': item.to_json()}), 200


#Usuwanie ogłoszenia
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    data = request.json
    user_id = data.get('user_id')  # Pobieramy ID użytkownika, który chce usunąć ogłoszenie

    item = Items.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    # Sprawdzamy, czy użytkownik jest właścicielem ogłoszenia
    if item.user_id != user_id:
        return jsonify({'error': 'You are not authorized to delete this item'}), 403

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted successfully'}), 200


#Zwraca ogłoszenia według ustawionych filtrów
@app.route('/api/items/filter', methods=['GET'])
def filter_items():
    make = request.args.get('make')
    model = request.args.get('model')
    year = request.args.get('year')

    # Łączymy Items z Car, aby uzyskać więcej danych
    query = db.session.query(Items, Car).join(Car, Items.car_id == Car.id)

    # Filtry
    if make:
        query = query.filter(Car.make.ilike(f"%{make}%"))  # ilike() dla wyszukiwania nieczułego na wielkość liter
    if model:
        query = query.filter(Car.model.ilike(f"%{model}%"))
    if year:
        try:
            year = int(year)
            query = query.filter(Car.year == year)
        except ValueError:
            return jsonify({"error": "Invalid year format"}), 400

    filtered_items = query.all()

    result = []
    for item, car in filtered_items:
        result.append({
            "id": item.id,
            "userId": item.user_id,
            "carId": item.car_id,
            "make": car.make,  # Marka samochodu
            "model": car.model,  # Model samochodu
            "year": car.year,  # Rok produkcji
            "fuelType": car.fuel_type,  # Rodzaj paliwa
            "engineDisplacement": car.engine_displacement,  # Pojemność silnika
            "carSizeClass": car.car_size_class,  # Klasa rozmiaru pojazdu
            "price": item.price,
            "carMileage": item.car_mileage,
            "color": item.color,
            "description": item.description,
            "createdAt": item.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(result), 200



# Pobranie unikalnych marek samochodów
@app.route('/api/cars/makes', methods=['GET'])
def get_makes():
    makes = db.session.query(Car.make).distinct().all()
    return jsonify([make[0] for make in makes]), 200

# Pobranie modeli na podstawie marki
@app.route('/api/cars/models', methods=['GET'])
def get_models():
    make = request.args.get('make')
    if not make:
        return jsonify({'error': 'Make is required'}), 400

    models = db.session.query(Car.model).filter(Car.make == make).distinct().order_by(Car.model).all()
    return jsonify([model[0] for model in models]), 200

