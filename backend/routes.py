from flask import Flask, jsonify, request, send_file
from werkzeug.security import generate_password_hash
from app import app, db
from models import *
from auth_middleware import requires_auth, requires_auth_optional
from services.storage_service import storage_service
from metrics import GapFillMetrics
import requests
import time
import csv
from io import StringIO
from datetime import datetime
import os


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


# ============================================================================
# A/B TESTING ENDPOINTS (Bachelor's Thesis - LLM Comparison Framework)
# ============================================================================

@app.route('/api/experiments', methods=['GET', 'POST'])
def experiments():
    """List all experiments or create a new one."""
    try:
        if request.method == 'GET':
            # Get all experiments with pagination
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            query = Experiment.query.order_by(Experiment.created_at.desc())
            experiments = query.paginate(page=page, per_page=per_page)
            
            return jsonify({
                'experiments': [exp.to_json() for exp in experiments.items],
                'total': experiments.total,
                'pages': experiments.pages,
                'current_page': page
            }), 200
        
        elif request.method == 'POST':
            # Create new experiment
            data = request.json
            
            required_fields = ['name', 'models', 'test_ads']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            experiment = Experiment(
                name=data.get('name'),
                description=data.get('description', ''),
                models=data.get('models'),  # List of model names
                parameters=data.get('parameters', {}),  # Optional parameters
                test_ads=data.get('test_ads'),  # List of ad IDs
                notes=data.get('notes', '')
            )
            
            db.session.add(experiment)
            db.session.commit()
            
            return jsonify(experiment.to_json()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>', methods=['GET', 'PUT', 'DELETE'])
def experiment_detail(experiment_id):
    """Get, update, or delete a specific experiment."""
    try:
        experiment = Experiment.query.get(experiment_id)
        
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        if request.method == 'GET':
            return jsonify(experiment.to_json()), 200
        
        elif request.method == 'PUT':
            # Update experiment
            data = request.json
            
            if 'name' in data:
                experiment.name = data['name']
            if 'description' in data:
                experiment.description = data['description']
            if 'parameters' in data:
                experiment.parameters = data['parameters']
            if 'status' in data:
                experiment.status = data['status']
            if 'notes' in data:
                experiment.notes = data['notes']
            
            db.session.commit()
            return jsonify(experiment.to_json()), 200
        
        elif request.method == 'DELETE':
            # Delete experiment and all related runs
            db.session.delete(experiment)
            db.session.commit()
            return jsonify({'message': 'Experiment deleted'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>/runs', methods=['GET', 'POST'])
def experiment_runs(experiment_id):
    """Get all runs for an experiment or add a new run."""
    try:
        experiment = Experiment.query.get(experiment_id)
        
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        if request.method == 'GET':
            # Get all runs with optional filtering
            model_filter = request.args.get('model', None)
            
            query = ExperimentRun.query.filter_by(experiment_id=experiment_id)
            if model_filter:
                query = query.filter_by(model_name=model_filter)
            
            runs = query.order_by(ExperimentRun.created_at.desc()).all()
            
            return jsonify({
                'experimentId': experiment_id,
                'totalRuns': len(runs),
                'runs': [run.to_json() for run in runs]
            }), 200
        
        elif request.method == 'POST':
            # Add a new run result
            data = request.json
            
            required_fields = ['model_name', 'ad_id', 'original_text', 'filled_text', 'gap_fills']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            run = ExperimentRun(
                experiment_id=experiment_id,
                model_name=data.get('model_name'),
                ad_id=data.get('ad_id'),
                original_text=data.get('original_text'),
                filled_text=data.get('filled_text'),
                gap_fills=data.get('gap_fills'),
                semantic_score=data.get('semantic_score'),
                domain_relevance_score=data.get('domain_relevance_score'),
                grammar_score=data.get('grammar_score'),
                overall_score=data.get('overall_score'),
                generation_time=data.get('generation_time'),
                status=data.get('status', 'success')
            )
            
            db.session.add(run)
            
            # Update experiment stats
            experiment.total_runs += 1
            if data.get('status') == 'success':
                experiment.completed_runs += 1
            else:
                experiment.failed_runs += 1
            
            db.session.commit()
            
            return jsonify(run.to_json()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>/results', methods=['GET'])
def experiment_results(experiment_id):
    """Get aggregated results and statistics for an experiment."""
    try:
        experiment = Experiment.query.get(experiment_id)
        
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        runs = ExperimentRun.query.filter_by(experiment_id=experiment_id).all()
        
        if not runs:
            return jsonify({
                'experimentId': experiment_id,
                'message': 'No runs yet',
                'results': {}
            }), 200
        
        # Aggregate results by model
        model_stats = {}
        
        for model_name in experiment.models:
            model_runs = [r for r in runs if r.model_name == model_name]
            
            if model_runs:
                successful_runs = [r for r in model_runs if r.status == 'success']
                
                model_stats[model_name] = {
                    'total_runs': len(model_runs),
                    'successful_runs': len(successful_runs),
                    'failed_runs': len(model_runs) - len(successful_runs),
                    'avg_semantic_score': round(sum(r.semantic_score or 0 for r in successful_runs) / len(successful_runs), 3) if successful_runs else 0,
                    'avg_domain_relevance': round(sum(r.domain_relevance_score or 0 for r in successful_runs) / len(successful_runs), 3) if successful_runs else 0,
                    'avg_grammar_score': round(sum(r.grammar_score or 0 for r in successful_runs) / len(successful_runs), 3) if successful_runs else 0,
                    'avg_overall_score': round(sum(r.overall_score or 0 for r in successful_runs) / len(successful_runs), 3) if successful_runs else 0,
                    'avg_generation_time': round(sum(r.generation_time or 0 for r in successful_runs) / len(successful_runs), 2) if successful_runs else 0,
                }
        
        return jsonify({
            'experimentId': experiment_id,
            'experimentName': experiment.name,
            'status': experiment.status,
            'totalRuns': experiment.total_runs,
            'modelStats': model_stats
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>/export', methods=['GET'])
def export_experiment_results(experiment_id):
    """Export experiment results as CSV."""
    import csv
    from io import StringIO
    
    try:
        experiment = Experiment.query.get(experiment_id)
        
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        runs = ExperimentRun.query.filter_by(experiment_id=experiment_id).all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow([
            'Model', 'AD ID', 'Original Text', 'Filled Text', 
            'Semantic Score', 'Domain Relevance', 'Grammar Score', 'Overall Score',
            'Generation Time (s)', 'Status', 'Created At'
        ])
        
        # Data rows
        for run in runs:
            writer.writerow([
                run.model_name,
                run.ad_id,
                run.original_text[:100],  # Truncate for readability
                run.filled_text[:100] if run.filled_text else '',
                run.semantic_score or 0,
                run.domain_relevance_score or 0,
                run.grammar_score or 0,
                run.overall_score or 0,
                run.generation_time or 0,
                run.status,
                run.created_at.strftime("%Y-%m-%d %H:%M:%S") if run.created_at else ''
            ])
        
        csv_content = output.getvalue()
        
        return {
            'data': csv_content,
            'filename': f'experiment_{experiment_id}_results.csv'
        }, 200, {'Content-Disposition': f'attachment; filename="experiment_{experiment_id}_results.csv"'}
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>/evaluations', methods=['GET', 'POST'])
def experiment_evaluations(experiment_id):
    """Get or create quality evaluations for an experiment."""
    try:
        experiment = Experiment.query.get(experiment_id)
        
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        if request.method == 'GET':
            # Get all evaluations
            evaluations = QualityEvaluation.query.filter_by(experiment_id=experiment_id).all()
            
            return jsonify({
                'experimentId': experiment_id,
                'totalEvaluations': len(evaluations),
                'evaluations': [eval.to_json() for eval in evaluations]
            }), 200
        
        elif request.method == 'POST':
            # Create new evaluation
            data = request.json
            
            required_fields = ['run_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            evaluation = QualityEvaluation(
                experiment_id=experiment_id,
                run_id=data.get('run_id'),
                human_rating=data.get('human_rating'),
                human_notes=data.get('human_notes'),
                gap_feedback=data.get('gap_feedback', {}),
                is_valid=data.get('is_valid', True),
                has_errors=data.get('has_errors', False),
                error_details=data.get('error_details'),
                evaluated_by=data.get('evaluated_by', 'system')
            )
            
            db.session.add(evaluation)
            db.session.commit()
            
            return jsonify(evaluation.to_json()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# A/B TESTING ENDPOINTS
# ============================================================================

BIELIK_API_URL = os.environ.get('BIELIK_APP_URL', 'http://localhost:8000')

@app.route('/api/experiments', methods=['GET'])
def get_experiments():
    """List all experiments"""
    try:
        experiments = Experiment.query.order_by(Experiment.created_at.desc()).all()
        return jsonify([{
            'id': e.id,
            'name': e.name,
            'description': e.description,
            'models': e.models,
            'parameters': e.parameters,
            'status': e.status,
            'created_at': e.created_at.isoformat() if e.created_at else None,
            'completed_runs': e.completed_runs,
            'total_runs': e.total_runs
        } for e in experiments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments', methods=['POST'])
def create_experiment():
    """Create a new experiment"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        if not data.get('models') or len(data['models']) == 0:
            return jsonify({'error': 'At least one model must be selected'}), 400
        
        experiment = Experiment(
            name=data['name'],
            description=data.get('description', ''),
            models=data['models'],
            parameters=data.get('parameters', {}),
            test_ads=data.get('test_ads', []),
            notes=data.get('notes', '')
        )
        
        db.session.add(experiment)
        db.session.commit()
        
        return jsonify({
            'id': experiment.id,
            'name': experiment.name,
            'description': experiment.description,
            'models': experiment.models,
            'parameters': experiment.parameters,
            'created_at': experiment.created_at.isoformat(),
            'status': experiment.status
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>', methods=['GET'])
def get_experiment(experiment_id):
    """Get a single experiment"""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        return jsonify({
            'id': experiment.id,
            'name': experiment.name,
            'description': experiment.description,
            'models': experiment.models,
            'parameters': experiment.parameters,
            'test_ads': experiment.test_ads,
            'status': experiment.status,
            'created_at': experiment.created_at.isoformat() if experiment.created_at else None,
            'completed_at': experiment.completed_at.isoformat() if experiment.completed_at else None,
            'total_runs': experiment.total_runs,
            'completed_runs': experiment.completed_runs,
            'failed_runs': experiment.failed_runs
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>/run', methods=['POST'])
def run_experiment(experiment_id):
    """Execute experiment on test items"""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        data = request.json
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'No test items provided'}), 400
        
        experiment.status = 'running'
        experiment.started_at = datetime.utcnow()
        experiment.total_runs = len(items) * len(experiment.models)
        experiment.completed_runs = 0
        experiment.failed_runs = 0
        db.session.commit()
        
        results = []
        metrics = GapFillMetrics()
        
        # Run each item with each model
        for item in items:
            item_id = item.get('id', f'item-{len(results)}')
            text_with_gaps = item.get('text_with_gaps', '')
            
            for model_name in experiment.models:
                try:
                    start_time = time.time()
                    
                    # Call Bielik service
                    response = requests.post(
                        f'{BIELIK_API_URL}/infill',
                        json={
                            'domain': 'cars',
                            'model': model_name,
                            'items': [{'id': item_id, 'text_with_gaps': text_with_gaps}],
                            'options': experiment.parameters
                        },
                        timeout=120
                    )
                    
                    generation_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        model_results = result_data.get('results', [])
                        
                        if model_results:
                            model_result = model_results[0]
                            
                            # Calculate metrics
                            filled_text = model_result.get('filled_text', '')
                            gaps = model_result.get('gaps', [])
                            
                            # Extract gap choices for scoring
                            gap_choices = {}
                            for gap in gaps:
                                gap_choices[gap['index']] = gap['choice']
                            
                            semantic_score = metrics.calculate_semantic_score(filled_text, text_with_gaps)
                            domain_score = metrics.calculate_domain_score(gap_choices)
                            grammar_score = metrics.calculate_grammar_score(gap_choices)
                            
                            overall_score = (semantic_score + domain_score + grammar_score) / 3
                            
                            # Save run result
                            run = ExperimentRun(
                                experiment_id=experiment_id,
                                model_name=model_name,
                                ad_id=item_id,
                                original_text=text_with_gaps,
                                filled_text=filled_text,
                                gap_fills={str(g['index']): g for g in gaps},
                                semantic_score=semantic_score,
                                domain_relevance_score=domain_score,
                                grammar_score=grammar_score,
                                overall_score=overall_score,
                                generation_time=generation_time,
                                status='success'
                            )
                            
                            db.session.add(run)
                            db.session.commit()
                            
                            results.append({
                                'id': run.id,
                                'item_id': item_id,
                                'model_name': model_name,
                                'filled_text': filled_text,
                                'gaps': gaps,
                                'semantic_score': semantic_score,
                                'domain_score': domain_score,
                                'grammar_score': grammar_score,
                                'overall_score': overall_score,
                                'generation_time': generation_time
                            })
                            
                            experiment.completed_runs += 1
                        else:
                            experiment.failed_runs += 1
                    else:
                        experiment.failed_runs += 1
                
                except Exception as e:
                    experiment.failed_runs += 1
                    run = ExperimentRun(
                        experiment_id=experiment_id,
                        model_name=model_name,
                        ad_id=item_id,
                        original_text=text_with_gaps,
                        status='error',
                        error_message=str(e),
                        generation_time=0
                    )
                    db.session.add(run)
                    db.session.commit()
        
        experiment.status = 'completed'
        experiment.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'results': results, 'status': 'completed'}), 200
    
    except Exception as e:
        experiment.status = 'failed'
        db.session.commit()
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>/results', methods=['GET'])
def get_experiment_results(experiment_id):
    """Get experiment results"""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        runs = ExperimentRun.query.filter_by(experiment_id=experiment_id).all()
        
        return jsonify({
            'experiment_id': experiment_id,
            'experiment_name': experiment.name,
            'models_compared': experiment.models,
            'total_items': experiment.total_runs // len(experiment.models) if experiment.models else 0,
            'results': [{
                'id': r.id,
                'item_id': r.ad_id,
                'model_name': r.model_name,
                'original_text': r.original_text,
                'filled_text': r.filled_text,
                'gaps': [g for g in (r.gap_fills or {}).values()] if r.gap_fills else [],
                'semantic_score': r.semantic_score,
                'domain_score': r.domain_relevance_score,
                'grammar_score': r.grammar_score,
                'overall_score': r.overall_score,
                'generation_time': r.generation_time
            } for r in runs],
            'created_at': experiment.created_at.isoformat() if experiment.created_at else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>/export', methods=['GET'])
def export_experiment(experiment_id):
    """Export experiment results as CSV"""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        runs = ExperimentRun.query.filter_by(experiment_id=experiment_id).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Item ID', 'Model', 'Original Text', 'Filled Text',
            'Semantic Score', 'Domain Score', 'Grammar Score', 'Overall Score',
            'Generation Time (s)'
        ])
        
        for run in runs:
            writer.writerow([
                run.ad_id,
                run.model_name,
                run.original_text,
                run.filled_text,
                f"{run.semantic_score:.2f}" if run.semantic_score else "N/A",
                f"{run.domain_relevance_score:.2f}" if run.domain_relevance_score else "N/A",
                f"{run.grammar_score:.2f}" if run.grammar_score else "N/A",
                f"{run.overall_score:.2f}" if run.overall_score else "N/A",
                f"{run.generation_time:.2f}" if run.generation_time else "N/A"
            ])
        
        output.seek(0)
        return send_file(
            StringIO(output.getvalue()),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"experiment_{experiment_id}_results.csv"
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<int:experiment_id>', methods=['DELETE'])
def delete_experiment(experiment_id):
    """Delete an experiment"""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        # Delete related runs first
        ExperimentRun.query.filter_by(experiment_id=experiment_id).delete()
        QualityEvaluation.query.filter_by(experiment_id=experiment_id).delete()
        
        db.session.delete(experiment)
        db.session.commit()
        
        return jsonify({'status': 'deleted', 'id': experiment_id}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/models', methods=['GET'])
def get_available_models():
    """Get list of available models"""
    try:
        # Try to get from Bielik service
        response = requests.get(f'{BIELIK_API_URL}/models', timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            return jsonify([{'name': m.get('name', m) if isinstance(m, dict) else m} for m in models]), 200
        
        # Fallback if service not available
        fallback_models = [
            'bielik-1.5b-gguf',
            'bielik-11b-gguf',
            'llama-3.1-8b'
        ]
        return jsonify([{'name': m} for m in fallback_models]), 200
    
    except:
        # Fallback if service not available
        fallback_models = [
            'bielik-1.5b-gguf',
            'bielik-11b-gguf',
            'llama-3.1-8b'
        ]
        return jsonify([{'name': m} for m in fallback_models]), 200


