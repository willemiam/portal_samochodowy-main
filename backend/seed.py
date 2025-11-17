from app import app, db
from models import Category, CategorySchema

def seed_database():
    with app.app_context():
        db.create_all()

        # Check if categories already exist
        if Category.query.first() is not None:
            print("Database already seeded.")
            return

        # Create categories
        car_category = Category(name='Cars', slug='cars', description='Cars for sale')
        apartment_category = Category(name='Apartments', slug='apartments', description='Apartments for rent or sale')

        db.session.add(car_category)
        db.session.add(apartment_category)
        db.session.commit()

        # Create schemas
        car_schema = [
            CategorySchema(category_id=car_category.id, field_name='make', field_type='text', field_label='Make', is_required=True, display_order=1),
            CategorySchema(category_id=car_category.id, field_name='model', field_type='text', field_label='Model', is_required=True, display_order=2),
            CategorySchema(category_id=car_category.id, field_name='year', field_type='number', field_label='Year', is_required=True, display_order=3),
            CategorySchema(category_id=car_category.id, field_name='mileage', field_type='number', field_label='Mileage', is_required=True, display_order=4),
            CategorySchema(category_id=car_category.id, field_name='fuel_type', field_type='select', field_label='Fuel Type', field_options=['Gasoline', 'Diesel', 'Electric', 'Hybrid'], is_required=True, display_order=5),
        ]

        apartment_schema = [
            CategorySchema(category_id=apartment_category.id, field_name='area', field_type='number', field_label='Area (sqm)', is_required=True, display_order=1),
            CategorySchema(category_id=apartment_category.id, field_name='rooms', field_type='number', field_label='Number of rooms', is_required=True, display_order=2),
            CategorySchema(category_id=apartment_category.id, field_name='floor', field_type='number', field_label='Floor', is_required=True, display_order=3),
            CategorySchema(category_id=apartment_category.id, field_name='year_built', field_type='number', field_label='Year Built', is_required=False, display_order=4),
        ]

        db.session.bulk_save_objects(car_schema)
        db.session.bulk_save_objects(apartment_schema)
        db.session.commit()

        print("Database seeded successfully.")

if __name__ == '__main__':
    seed_database()
