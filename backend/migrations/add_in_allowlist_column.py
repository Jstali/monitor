"""
Add in_allowlist column to activities table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from models import db
from sqlalchemy import text
from flask import Flask

def upgrade():
    """Add in_allowlist column to activities table"""
    # Create minimal Flask app for database context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/employee_monitoring')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='activities' AND column_name='in_allowlist'
            """))
            
            if result.fetchone():
                print("✅ Column 'in_allowlist' already exists in activities table")
                return
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE activities 
                ADD COLUMN in_allowlist BOOLEAN DEFAULT FALSE
            """))
            db.session.commit()
            print("✅ Successfully added 'in_allowlist' column to activities table")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding column: {e}")
            raise

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Running migration: Add in_allowlist to activities table")
    upgrade()
    print("Migration completed!")

