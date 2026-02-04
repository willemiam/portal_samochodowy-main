#!/usr/bin/env python3
"""
Quick test to verify A/B testing database implementation
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("A/B Testing Database Verification")
print("=" * 60)

try:
    print("\n1️⃣  Importing Flask app...")
    from app import app, db
    print("   ✅ Flask app imported")
    
    print("\n2️⃣  Creating app context...")
    with app.app_context():
        print("   ✅ App context created")
        
        print("\n3️⃣  Importing models...")
        from models import Experiment, ExperimentRun, QualityEvaluation, Car, Photo, Users
        print("   ✅ All models imported successfully")
        
        print("\n4️⃣  Checking database...")
        db.create_all()
        print("   ✅ Database tables created/verified")
        
        print("\n5️⃣  Verifying A/B testing tables...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = ['experiments', 'experiment_runs', 'quality_evaluations']
        all_exist = True
        for table in required_tables:
            if table in tables:
                cols = len(inspector.get_columns(table))
                print(f"   ✅ {table:20} ({cols} columns)")
            else:
                print(f"   ❌ {table:20} MISSING")
                all_exist = False
        
        if all_exist:
            print("\n✨ SUCCESS! All A/B testing tables created!")
            print("\nNext steps:")
            print("  1. Create an experiment: POST /api/experiments")
            print("  2. Add run results: POST /api/experiments/<id>/runs")
            print("  3. View results: GET /api/experiments/<id>/results")
            print("\nSee AB_TESTING_DATABASE.md for complete API docs")
            sys.exit(0)
        else:
            print("\n❌ Some tables are missing!")
            sys.exit(1)

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
