from app import create_app
from models import db, MonitoringConfig

def add_electron_config():
    app = create_app()
    with app.app_context():
        # Get the organization ID from the employee
        from models import Employee
        employee = Employee.query.filter_by(email='stalinj4747@gmail.com').first()
        
        if not employee:
            print("Error: Employee not found")
            return
        
        org_id = employee.organization_id
        
        # Check if already exists
        existing = MonitoringConfig.query.filter_by(
            organization_id=org_id,
            config_type='application',
            pattern='Electron'
        ).first()
        
        if existing:
            print(f"✓ Configuration for 'Electron' already exists (Folder: {existing.folder_name})")
            return

        # Create new config
        config = MonitoringConfig(
            organization_id=org_id,
            config_type='application',
            pattern='Electron',
            folder_name='vs_code',  # Map Electron to vs_code folder
            is_active=True
        )
        
        db.session.add(config)
        db.session.commit()
        print("✓ Successfully added 'Electron' to allowlist (mapped to 'vs_code' folder)")

if __name__ == '__main__':
    add_electron_config()
