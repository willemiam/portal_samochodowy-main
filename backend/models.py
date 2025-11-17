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


class Items(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
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
            'categoryId': self.category_id,
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
