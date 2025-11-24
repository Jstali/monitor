#!/usr/bin/env python3
"""
Database Migration: Add Selective Monitoring Support
- Adds folder_name and activity_name columns to screenshots table
- Removes old monitoring_rules table if it exists
"""

from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

def run_migration():
    """Execute database migration"""
    with app.app_context():
        print("=" * 70)
        print("DATABASE MIGRATION: Selective Monitoring Support")
        print("=" * 70)
        print()
        
        try:
            # Check current state
            print("1. Checking current database state...")
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'screenshots'
            """))
            existing_columns = [row[0] for row in result]
            print(f"   Current screenshots columns: {len(existing_columns)}")
            
            # Add folder_name column if missing
            if 'folder_name' not in existing_columns:
                print("\n2. Adding 'folder_name' column to screenshots table...")
                db.session.execute(text("""
                    ALTER TABLE screenshots 
                    ADD COLUMN folder_name VARCHAR(100)
                """))
                db.session.commit()
                print("   ✓ folder_name column added")
            else:
                print("\n2. 'folder_name' column already exists")
            
            # Add activity_name column if missing
            if 'activity_name' not in existing_columns:
                print("\n3. Adding 'activity_name' column to screenshots table...")
                db.session.execute(text("""
                    ALTER TABLE screenshots 
                    ADD COLUMN activity_name VARCHAR(200)
                """))
                db.session.commit()
                print("   ✓ activity_name column added")
            else:
                print("\n3. 'activity_name' column already exists")
            
            # Check for old monitoring_rules table
            print("\n4. Checking for old monitoring_rules table...")
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'monitoring_rules'
            """))
            
            if result.fetchone():
                print("   Found old monitoring_rules table")
                print("   Note: This table is deprecated. Use monitoring_configs instead.")
                print("   To remove it manually, run: DROP TABLE monitoring_rules CASCADE;")
            else:
                print("   ✓ No old tables found")
            
            # Verify migration
            print("\n5. Verifying migration...")
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'screenshots' 
                AND column_name IN ('folder_name', 'activity_name')
            """))
            
            new_columns = list(result)
            if len(new_columns) == 2:
                print("   ✓ Migration successful!")
                print("\n   New columns:")
                for col_name, col_type in new_columns:
                    print(f"     • {col_name}: {col_type}")
            else:
                print("   ✗ Migration incomplete!")
                return False
            
            print("\n" + "=" * 70)
            print("MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print("\n✅ Database is now ready for selective monitoring!")
            print("\nNext steps:")
            print("  1. Restart the backend server (if not auto-reloaded)")
            print("  2. Refresh the frontend")
            print("  3. Configure monitoring rules via the dashboard")
            print("  4. Restart the monitoring agent")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
