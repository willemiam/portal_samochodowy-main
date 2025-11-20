from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='uploads', static_url_path='/uploads')
CORS(app, resources={r"/*": {"origins": "*"}})  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Auth0 Configuration
app.config['AUTH0_DOMAIN'] = os.environ.get('AUTH0_DOMAIN', 'your-domain.auth0.com')
app.config['AUTH0_AUDIENCE'] = os.environ.get('AUTH0_AUDIENCE', 'your-api-identifier')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Development mode - disable auth for testing (set to False in production)
app.config['DISABLE_AUTH'] = os.environ.get('DISABLE_AUTH', 'True').lower() == 'true'

db = SQLAlchemy(app)

from routes import *

# Register blueprints after routes are loaded (only once)
if 'platforms' not in [bp.name for bp in app.blueprints.values()]:
    from services.platforms import platforms_bp
    app.register_blueprint(platforms_bp)

def init_database():
    """Initialize database and load CSV data"""
    with app.app_context():
        db.create_all()  

        try:
            df = pd.read_csv('final_vehicle_data.csv')

            df = df.rename(columns={
                "Make": "make",
                "Model": "model", 
                "Year": "year",
                "Fuel Type1": "fuel_type",
                "Engine displacement": "engine_displacement",
                "Typ nadwozia": "car_size_class"
            })

            existing_cars = db.session.execute(text("SELECT COUNT(*) FROM cars")).fetchone()[0]
            if existing_cars == 0:
                df.to_sql('cars', con=db.engine, if_exists='append', index=False)
                print("Dane CSV załadowane do bazy.")
            else:
                print("Tabela 'cars' już zawiera dane. Pominięto ładowanie CSV.")
        except FileNotFoundError:
            print("Błąd: Plik final_vehicle_data.csv nie został znaleziony.")



if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)



