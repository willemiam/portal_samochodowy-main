#!/usr/bin/env python3
"""
Migration script to add Photo table to existing database
Run this to update your database with photo storage capabilities
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import app, db
from models import Photo

def migrate_database():
    """Create the Photo table in the existing database"""
    with app.app_context():
        try:
            # Create the photos table
            db.create_all()
            
            print("✅ Successfully created Photo table!")
            print("📋 Photo table columns:")
            print("   - id (Primary Key)")
            print("   - item_id (Foreign Key to items)")
            print("   - filename (Original filename)")
            print("   - stored_filename (Unique stored filename)")
            print("   - file_path (Full path or URL)")
            print("   - file_size (Size in bytes)")
            print("   - mime_type (image/jpeg, etc.)")
            print("   - is_main (Main photo flag)")
            print("   - display_order (Order in gallery)")
            print("   - storage_type (local or aws_s3)")
            print("   - created_at (Timestamp)")
            
            # Create uploads directory
            uploads_dir = os.path.join(os.getcwd(), 'uploads', 'photos')
            Path(uploads_dir).mkdir(parents=True, exist_ok=True)
            print(f"📁 Created uploads directory: {uploads_dir}")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print("📊 Adding Photo table for image storage...")
    migrate_database()
    print("🎉 Migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Restart your Flask server")
    print("2. Photos will be stored in: uploads/photos/")
    print("3. To switch to AWS S3 later, set STORAGE_TYPE=aws_s3 in environment") 