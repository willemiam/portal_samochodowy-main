from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash
from app import app, db
from models import *
from models import Car, Photo
from auth_middleware import requires_auth, requires_auth_optional
from services.storage_service import storage_service


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
@requires_auth
def create_item():
    try:
        data = request.json
        user = request.current_user  
        
        required_fields = ['make', 'model', 'year', 'price', 'car_mileage', 'color', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Input required field {field}'}), 400

        # Remove user_id from required fields since we get it from auth
        user_id = user.id
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
            new_car = Car()
            new_car.make = make
            new_car.model = model
            new_car.year = year
            new_car.fuel_type = data.get('fuel_type')
            new_car.engine_displacement = data.get('engine_displacement')
            new_car.car_size_class = data.get('car_size_class')
            new_car.doors = data.get('doors')
            new_car.transmission = data.get('transmission')
            new_car.drive_type = data.get('drive_type')
            db.session.add(new_car)
            db.session.commit()
            car_id = new_car.id
        else:
            car_id = existing_car.id        # Tworzymy ogłoszenie
        attributes = {
            'car_mileage': car_mileage,
            'color': color
        }
        
        new_item = Items(
            user_id=user_id,
            car_id=car_id,
            price=price,
            description=description,
            attributes=attributes
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
        car_mileage = item.attributes.get('car_mileage') if item.attributes else None
        color = item.attributes.get('color') if item.attributes else None
        
        result.append({
            "id": item.id,
            "userId": item.user_id,
            "carId": item.car_id,
            "make": car.make,
            "model": car.model,
            "year": car.year,
            "price": item.price,
            "carMileage": car_mileage,
            "color": color,
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
@requires_auth
def update_item(item_id):
    data = request.json
    user = request.current_user  # Get authenticated user

    item = Items.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    # Sprawdzamy, czy użytkownik jest właścicielem ogłoszenia
    if item.user_id != user.id:
        return jsonify({'error': 'You are not authorized to edit this item'}), 403    # Aktualizacja danych (tylko wybrane pola)
    if 'price' in data:
        item.price = data['price']
    if 'car_mileage' in data or 'color' in data:
        if not item.attributes:
            item.attributes = {}
        if 'car_mileage' in data:
            item.attributes['car_mileage'] = data['car_mileage']
        if 'color' in data:
            item.attributes['color'] = data['color']
    if 'description' in data:
        item.description = data['description']

    db.session.commit()
    return jsonify({'message': 'Item updated successfully', 'item': item.to_json()}), 200


#Usuwanie ogłoszenia
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@requires_auth
def delete_item(item_id):
    user = request.current_user  # Get authenticated user

    item = Items.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    # Sprawdzamy, czy użytkownik jest właścicielem ogłoszenia
    if item.user_id != user.id:
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
        query = query.filter(Car.make.ilike(f"%{make}%"))
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
        car_mileage = item.attributes.get('car_mileage') if item.attributes else None
        color = item.attributes.get('color') if item.attributes else None
        
        result.append({
            "id": item.id,
            "userId": item.user_id,
            "carId": item.car_id,
            "make": car.make,
            "model": car.model,
            "year": car.year,
            "fuelType": car.fuel_type,
            "engineDisplacement": car.engine_displacement,
            "carSizeClass": car.car_size_class,
            "price": item.price,
            "carMileage": car_mileage,
            "color": color,
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

# Photo upload endpoint
@app.route('/api/photos/upload', methods=['POST'])
@requires_auth
def upload_photo():
    """Upload a single photo file"""
    try:
        user = request.current_user
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Upload file using storage service
        success, file_info, error_message = storage_service.upload_file(file)
        
        if not success:
            return jsonify({'error': error_message}), 400

        # Return file info for frontend to store temporarily
        return jsonify({
            'success': True,
            'file': file_info
        }), 200

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


# Batch photo upload for item
@app.route('/api/items/<int:item_id>/photos', methods=['POST'])
@requires_auth
def upload_item_photos(item_id):
    """Upload multiple photos for an item"""
    try:
        user = request.current_user
        
        # Check if item exists and user owns it
        item = Items.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        if item.user_id != user.id:
            return jsonify({'error': 'You are not authorized to upload photos for this item'}), 403

        # Get photo data from request
        data = request.json
        if not data or 'photos' not in data:
            return jsonify({'error': 'No photo data provided'}), 400

        photos_data = data['photos']
        saved_photos = []

        for idx, photo_data in enumerate(photos_data):
            # Create photo record in database
            photo = Photo(
                item_id=item_id,
                filename=photo_data['filename'],
                stored_filename=photo_data['stored_filename'],
                file_path=photo_data['file_path'],
                file_size=photo_data.get('file_size'),
                mime_type=photo_data.get('mime_type'),
                is_main=photo_data.get('is_main', False),
                display_order=idx,
                storage_type=photo_data.get('storage_type', 'local')
            )
            
            db.session.add(photo)
            saved_photos.append(photo)

        # Ensure only one main photo
        main_photos = [p for p in saved_photos if p.is_main]
        if len(main_photos) > 1:
            # Keep only the first one as main
            for i, photo in enumerate(main_photos):
                if i > 0:
                    photo.is_main = False
        elif len(main_photos) == 0 and saved_photos:
            # Set first photo as main if none specified
            saved_photos[0].is_main = True

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Uploaded {len(saved_photos)} photos',
            'photos': [photo.to_json() for photo in saved_photos]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Photo upload failed: {str(e)}'}), 500


# Get photos for an item
@app.route('/api/items/<int:item_id>/photos', methods=['GET'])
def get_item_photos(item_id):
    """Get all photos for an item"""
    item = Items.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    photos = Photo.query.filter_by(item_id=item_id).order_by(Photo.display_order).all()
    
    return jsonify({
        'photos': [photo.to_json() for photo in photos]
    }), 200


# Delete a photo
@app.route('/api/photos/<int:photo_id>', methods=['DELETE'])
@requires_auth
def delete_photo(photo_id):
    """Delete a photo"""
    try:
        user = request.current_user
        
        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({'error': 'Photo not found'}), 404

        # Check if user owns the item
        item = Items.query.get(photo.item_id)
        if not item or item.user_id != user.id:
            return jsonify({'error': 'You are not authorized to delete this photo'}), 403

        # Delete file from storage
        storage_service.delete_file(photo.file_path, photo.storage_type)
        
        # Delete from database
        db.session.delete(photo)
        db.session.commit()

        return jsonify({'message': 'Photo deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500


# Update photo order and main photo
@app.route('/api/items/<int:item_id>/photos/reorder', methods=['PUT'])
@requires_auth
def reorder_photos(item_id):
    """Reorder photos and set main photo"""
    try:
        user = request.current_user
        
        # Check if item exists and user owns it
        item = Items.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        if item.user_id != user.id:
            return jsonify({'error': 'You are not authorized to modify this item'}), 403

        data = request.json
        if not data or 'photos' not in data:
            return jsonify({'error': 'No photo data provided'}), 400

        # Update photo order and main photo
        for photo_data in data['photos']:
            photo = Photo.query.get(photo_data['id'])
            if photo and photo.item_id == item_id:
                photo.display_order = photo_data.get('display_order', 0)
                photo.is_main = photo_data.get('is_main', False)

        db.session.commit()

        return jsonify({'message': 'Photos reordered successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Reorder failed: {str(e)}'}), 500

