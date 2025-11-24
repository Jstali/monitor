"""
Database Migration Script: Add Organization Support
Adds organization_id, manager_id, and is_active columns to employees table
Creates organizations table and links employees to a default organization
"""

from app import create_app
from models import db, Employee, Organization

def migrate_add_organization():
    """Add organization support to the database"""
    
    app = create_app()
    
    with app.app_context():
        print("Starting migration: Add organization support")
        print("=" * 60)
        
        # Check if organizations table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'organizations' not in tables:
            print("Creating organizations table...")
            db.session.execute(db.text("""
                CREATE TABLE organizations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    screenshot_interval INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("✓ organizations table created")
        else:
            print("✓ organizations table already exists")
        
        # Create default organization if none exists
        default_org = Organization.query.first()
        if not default_org:
            print("Creating default organization...")
            default_org = Organization(name="Default Organization", screenshot_interval=10)
            db.session.add(default_org)
            db.session.commit()
            print(f"✓ Created default organization (ID: {default_org.id})")
        else:
            print(f"✓ Using existing organization: {default_org.name} (ID: {default_org.id})")
        
        # Check which columns need to be added to employees table
        columns = [col['name'] for col in inspector.get_columns('employees')]
        
        # Add organization_id column
        if 'organization_id' not in columns:
            print("Adding organization_id column to employees table...")
            db.session.execute(db.text(
                f'ALTER TABLE employees ADD COLUMN organization_id INTEGER REFERENCES organizations(id)'
            ))
            db.session.commit()
            print("✓ organization_id column added")
            
            # Set all existing employees to default organization
            print(f"Assigning all employees to organization ID {default_org.id}...")
            db.session.execute(db.text(
                f'UPDATE employees SET organization_id = {default_org.id} WHERE organization_id IS NULL'
            ))
            db.session.commit()
            
            # Make organization_id NOT NULL
            db.session.execute(db.text(
                'ALTER TABLE employees ALTER COLUMN organization_id SET NOT NULL'
            ))
            db.session.commit()
            print("✓ All employees assigned to default organization")
        else:
            print("✓ organization_id column already exists")
        
        # Add manager_id column
        if 'manager_id' not in columns:
            print("Adding manager_id column to employees table...")
            db.session.execute(db.text(
                'ALTER TABLE employees ADD COLUMN manager_id INTEGER REFERENCES employees(id)'
            ))
            db.session.commit()
            print("✓ manager_id column added")
        else:
            print("✓ manager_id column already exists")
        
        # Add is_active column
        if 'is_active' not in columns:
            print("Adding is_active column to employees table...")
            db.session.execute(db.text(
                'ALTER TABLE employees ADD COLUMN is_active BOOLEAN DEFAULT TRUE'
            ))
            db.session.commit()
            
            # Set all existing employees to active
            db.session.execute(db.text(
                'UPDATE employees SET is_active = TRUE WHERE is_active IS NULL'
            ))
            db.session.commit()
            print("✓ is_active column added and set to TRUE for all employees")
        else:
            print("✓ is_active column already exists")
        
        # Check if monitoring_configs table exists
        if 'monitoring_configs' not in tables:
            print("Creating monitoring_configs table...")
            db.session.execute(db.text("""
                CREATE TABLE monitoring_configs (
                    id SERIAL PRIMARY KEY,
                    organization_id INTEGER NOT NULL REFERENCES organizations(id),
                    config_type VARCHAR(20) NOT NULL,
                    pattern VARCHAR(500) NOT NULL,
                    folder_name VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("✓ monitoring_configs table created")
        else:
            print("✓ monitoring_configs table already exists")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
        # Print summary
        print("\nDatabase Summary:")
        print(f"  Organizations: {Organization.query.count()}")
        print(f"  Total Employees: {Employee.query.count()}")
        print(f"  Active Employees: {Employee.query.filter_by(is_active=True).count()}")
        print(f"  Super Admins: {Employee.query.filter_by(role='super_admin').count()}")
        print(f"  Admins/Managers: {Employee.query.filter_by(role='admin').count()}")
        print(f"  Regular Employees: {Employee.query.filter_by(role='employee').count()}")

if __name__ == '__main__':
    try:
        migrate_add_organization()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
