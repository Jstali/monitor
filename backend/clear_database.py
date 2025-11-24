"""
Database Reset Script
Clears all data from the database tables
"""

from app import create_app
from models import db, Organization, Employee, MonitoringSession, Activity, Screenshot
import os
import shutil

def clear_database():
    """Clear all data from database"""
    
    app = create_app()
    
    with app.app_context():
        print("Starting database cleanup...")
        
        # Delete all records
        print("Deleting screenshots...")
        Screenshot.query.delete()
        
        print("Deleting activities...")
        Activity.query.delete()
        
        print("Deleting monitoring sessions...")
        MonitoringSession.query.delete()
        
        print("Deleting employees...")
        Employee.query.delete()
        
        print("Deleting organizations...")
        Organization.query.delete()
        
        db.session.commit()
        print("✓ All database records deleted")
        
        # Clear screenshot files
        screenshot_folder = app.config.get('SCREENSHOT_FOLDER', 'screenshots')
        if os.path.exists(screenshot_folder):
            print(f"\nClearing screenshot files from {screenshot_folder}...")
            for filename in os.listdir(screenshot_folder):
                file_path = os.path.join(screenshot_folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            print("✓ Screenshot files cleared")
        
        print("\n✅ Database cleared successfully!")
        print("\nYou can now register new users and start fresh.")

if __name__ == '__main__':
    confirm = input("⚠️  This will DELETE ALL DATA from the database. Are you sure? (yes/no): ")
    if confirm.lower() == 'yes':
        try:
            clear_database()
        except Exception as e:
            print(f"\n❌ Failed to clear database: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("Operation cancelled.")
