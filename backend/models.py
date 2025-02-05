from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Relacja 1 do wielu 
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
            "car_size_class": self.car_size_class
        }


class Items(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)  # Zmieniono odniesienie na cars.id
    price = db.Column(db.Integer, nullable=False)
    car_mileage = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'carId': self.car_id,
            'price': self.price,
            'carMileage': self.car_mileage,
            'color': self.color,
            'description': self.description,
            'createdAt': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
