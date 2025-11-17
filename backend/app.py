from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)



