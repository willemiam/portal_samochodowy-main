from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
import os
from sqlalchemy import text

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from routes import *

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
    app.run(debug=True, host='0.0.0.0', port=5000)



