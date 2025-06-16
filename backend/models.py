from datetime import datetime
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
            'updatedAt': self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
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
