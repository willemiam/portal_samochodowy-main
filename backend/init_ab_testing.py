#!/usr/bin/env python3
"""
A/B Testing Database Initialization

Creates database tables and verifies schema.
Run from backend directory: python init_ab_testing.py
"""

from app import db, create_app
from models import Experiment, ExperimentRun, QualityEvaluation
import sys

def init_database():
    """Initialize A/B testing tables."""
    app = create_app() if hasattr(sys.modules['app'], 'create_app') else None
    
    with app.app_context() if app else db.app.app_context():
        print("🗄️  Creating A/B Testing tables...")
        
        try:
            # Create tables
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['experiments', 'experiment_runs', 'quality_evaluations']
            for table in required_tables:
                if table in tables:
                    print(f"  ✓ {table} table exists")
                else:
                    print(f"  ✗ {table} table MISSING")
                    return False
            
            print("\n📋 Schema verification:")
            print(f"  Experiments table has {len(inspector.get_columns('experiments'))} columns")
            print(f"  ExperimentRuns table has {len(inspector.get_columns('experiment_runs'))} columns")
            print(f"  QualityEvaluations table has {len(inspector.get_columns('quality_evaluations'))} columns")
            
            print("\n✨ Database initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

def create_sample_experiment():
    """Create a sample experiment for testing."""
    app = create_app() if hasattr(sys.modules['app'], 'create_app') else None
    
    with app.app_context() if app else db.app.app_context():
        # Check if sample already exists
        existing = Experiment.query.filter_by(name='Sample A/B Test').first()
        if existing:
            print("ℹ️  Sample experiment already exists, skipping...")
            return
        
        sample = Experiment(
            name='Sample A/B Test',
            description='Initial test comparing 2 models on 5 ads',
            models=['bielik-1.5b-gguf', 'llama-3.1-8b'],
            parameters={
                'temperature': 0.3,
                'max_tokens': 200,
                'grammar_enabled': True
            },
            test_ads=[1, 2, 3, 4, 5],  # Sample ad IDs
            status='pending',
            notes='Initial thesis test run'
        )
        
        db.session.add(sample)
        db.session.commit()
        print("✅ Sample experiment created!")
        print(f"   ID: {sample.id}, Name: {sample.name}")

if __name__ == '__main__':
    print("=" * 60)
    print("A/B Testing Database Initialization")
    print("=" * 60)
    
    success = init_database()
    
    if success:
        print("\nWould you like to create a sample experiment? (y/n): ", end='')
        # Uncomment for interactive mode
        # response = input().lower()
        # if response == 'y':
        #     create_sample_experiment()
        
        # Auto-create sample for testing
        create_sample_experiment()
    
    sys.exit(0 if success else 1)
