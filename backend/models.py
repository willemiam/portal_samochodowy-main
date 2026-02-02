from datetime import datetime
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import JSON
from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='category', lazy=True, cascade="all, delete")
    category_schemas = db.relationship('CategorySchema', backref='category', lazy=True, cascade="all, delete")

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'isActive': self.is_active,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class CategorySchema(db.Model):
    __tablename__ = 'category_schemas'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)
    field_label = db.Column(db.String(100), nullable=False)
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    field_options = db.Column(JSON)
    validation_rules = db.Column(JSON)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'id': self.id,
            'categoryId': self.category_id,
            'fieldName': self.field_name,
            'fieldType': self.field_type,
            'fieldLabel': self.field_label,
            'isRequired': self.is_required,
            'fieldOptions': self.field_options,
            'validationRules': self.validation_rules,
            'displayOrder': self.display_order,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    attributes = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('Items', backref='product', lazy=True, cascade="all, delete")

    def to_json(self):
        return {
            'id': self.id,
            'categoryId': self.category_id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'attributes': self.attributes,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


    items = db.relationship('Items', backref='user', lazy=True, cascade="all, delete")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_json(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
        }

class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)  # Marka
    model = db.Column(db.String(50), nullable=False)  # Model
    year = db.Column(db.Integer, nullable=False)  # Rok produkcji
    fuel_type = db.Column(db.String(20))  # Rodzaj paliwa
    engine_displacement = db.Column(db.Float)  # Pojemność silnika
    car_size_class = db.Column(db.String(50))  # Typ nadwozia
    doors = db.Column(db.Integer)  # Liczba drzwi
    transmission = db.Column(db.String(20))  # Skrzynia biegów
    drive_type = db.Column(db.String(20))  # Napęd

    # Relacja do Items
    items = db.relationship('Items', backref='car', lazy=True, cascade="all, delete")

    def to_json(self):
        return {
            "id": self.id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "fuel_type": self.fuel_type,
            "engine_displacement": self.engine_displacement,
            "car_size_class": self.car_size_class,
            "doors": self.doors,
            "transmission": self.transmission,
            "drive_type": self.drive_type
        }


class Items(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(50))
    location = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=False)
    attributes = db.Column(JSON)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add relationship to photos
    photos = db.relationship('Photo', backref='item', lazy=True, cascade="all, delete", order_by='Photo.display_order')

    def to_json(self):
        result = {
            'id': self.id,
            'userId': self.user_id,
            'price': self.price,
            'condition': self.condition,
            'location': self.location,
            'description': self.description,
            'attributes': self.attributes,
            'isActive': self.is_active,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'updatedAt': self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            'photos': [photo.to_json() for photo in getattr(self, 'photos', [])]
        }
        
        if self.product_id:
            result['productId'] = self.product_id
        if self.car_id:
            result['carId'] = self.car_id
            if self.attributes and 'car_mileage' in self.attributes:
                result['carMileage'] = self.attributes['car_mileage']
            if self.attributes and 'color' in self.attributes:
                result['color'] = self.attributes['color']
        
        return result


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Original filename
    stored_filename = db.Column(db.String(255), nullable=False)  # Unique filename on disk/S3
    file_path = db.Column(db.String(500), nullable=False)  # Full path or URL
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))  # image/jpeg, image/png, etc.
    is_main = db.Column(db.Boolean, default=False, nullable=False)  # Main photo flag
    display_order = db.Column(db.Integer, default=0, nullable=False)  # Order in gallery
    storage_type = db.Column(db.String(20), default='local', nullable=False)  # 'local' or 'aws_s3'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'id': self.id,
            'itemId': self.item_id,
            'filename': self.filename,
            'filePath': self.file_path,
            'fileSize': self.file_size,
            'mimeType': self.mime_type,
            'isMain': self.is_main,
            'displayOrder': self.display_order,
            'storageType': self.storage_type,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


# ============================================================================
# A/B TESTING MODELS (Bachelor's Thesis - LLM Comparison Framework)
# ============================================================================

class Experiment(db.Model):
    __tablename__ = 'experiments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    models = db.Column(JSON, nullable=False)  # List of models: ["bielik-1.5b-gguf", "bielik-11b-gguf", "llama-3.1-8b"]
    parameters = db.Column(JSON)  # Shared experiment parameters: {temperature, max_tokens, grammar_enabled, etc.}
    test_ads = db.Column(JSON, nullable=False)  # List of test ad IDs to use
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, running, completed, failed
    total_runs = db.Column(db.Integer, default=0)
    completed_runs = db.Column(db.Integer, default=0)
    failed_runs = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)  # Research notes

    # Relationships
    runs = db.relationship('ExperimentRun', backref='experiment', lazy=True, cascade="all, delete")
    evaluations = db.relationship('QualityEvaluation', backref='experiment', lazy=True, cascade="all, delete")

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'models': self.models,
            'parameters': self.parameters,
            'testAds': self.test_ads,
            'status': self.status,
            'totalRuns': self.total_runs,
            'completedRuns': self.completed_runs,
            'failedRuns': self.failed_runs,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            'startedAt': self.started_at.strftime("%Y-%m-%d %H:%M:%S") if self.started_at else None,
            'completedAt': self.completed_at.strftime("%Y-%m-%d %H:%M:%S") if self.completed_at else None,
            'notes': self.notes
        }


class ExperimentRun(db.Model):
    __tablename__ = 'experiment_runs'

    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)  # Which model was used
    ad_id = db.Column(db.Integer, nullable=False)  # Reference to Items.id (test ad)
    original_text = db.Column(db.Text, nullable=False)  # Original ad with gaps
    filled_text = db.Column(db.Text)  # LLM output
    gap_fills = db.Column(JSON)  # Per-gap results: {1: {choice: "word", alternatives: [...]}, 2: {...}}
    
    # Metrics (calculated by metrics.py module)
    semantic_score = db.Column(db.Float)  # 0-1, word embedding similarity
    domain_relevance_score = db.Column(db.Float)  # 0-1, car vocabulary check
    grammar_score = db.Column(db.Float)  # 0-1, Polish case correctness
    overall_score = db.Column(db.Float)  # 0-1, weighted average
    
    # Execution details
    generation_time = db.Column(db.Float)  # Seconds
    status = db.Column(db.String(20), default='success', nullable=False)  # success, error, invalid_output
    error_message = db.Column(db.Text)  # If status = error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'id': self.id,
            'experimentId': self.experiment_id,
            'modelName': self.model_name,
            'adId': self.ad_id,
            'originalText': self.original_text,
            'filledText': self.filled_text,
            'gapFills': self.gap_fills,
            'semanticScore': self.semantic_score,
            'domainRelevanceScore': self.domain_relevance_score,
            'grammarScore': self.grammar_score,
            'overallScore': self.overall_score,
            'generationTime': self.generation_time,
            'status': self.status,
            'errorMessage': self.error_message,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class QualityEvaluation(db.Model):
    __tablename__ = 'quality_evaluations'

    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    run_id = db.Column(db.Integer, db.ForeignKey('experiment_runs.id'), nullable=False)
    
    # Human evaluation (optional, for validation)
    human_rating = db.Column(db.Integer)  # 1-5 star rating
    human_notes = db.Column(db.Text)  # Evaluator feedback
    
    # Gap-specific feedback
    gap_feedback = db.Column(JSON)  # Per-gap human judgment: {1: "correct", 2: "incorrect", 3: "acceptable"}
    
    # Validation flags
    is_valid = db.Column(db.Boolean, default=True)  # JSON valid, all gaps filled
    has_errors = db.Column(db.Boolean, default=False)  # Parsing errors
    error_details = db.Column(db.Text)
    
    evaluated_by = db.Column(db.String(100))  # Email or user identifier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'id': self.id,
            'experimentId': self.experiment_id,
            'runId': self.run_id,
            'humanRating': self.human_rating,
            'humanNotes': self.human_notes,
            'gapFeedback': self.gap_feedback,
            'isValid': self.is_valid,
            'hasErrors': self.has_errors,
            'errorDetails': self.error_details,
            'evaluatedBy': self.evaluated_by,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
