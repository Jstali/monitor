"""
Database Migration Script: Add Manager Assignment
Adds manager_id column to employees table to support manager-employee relationships
"""

from app import create_app
from models import db, Employee

def migrate_add_manager():
    """Add manager_id column to employees table"""
    
    app = create_app()
    
    with app.app_context():
        print("Starting migration: Add manager_id to employees table")
        
        # Check if column already exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('employees')]
        
        if 'manager_id' in columns:
            print("✓ manager_id column already exists, skipping migration")
            return
        
        # Add the column using raw SQL
        print("Adding manager_id column...")
        db.session.execute(db.text(
            'ALTER TABLE employees ADD COLUMN manager_id INTEGER REFERENCES employees(id)'
        ))
        db.session.commit()
        print("✓ manager_id column added successfully")
        
        # Update existing admins to super_admin role
        print("Updating existing admin roles to super_admin...")
        admins = Employee.query.filter_by(role='admin').all()
        for admin in admins:
            admin.role = 'super_admin'
        db.session.commit()
        print(f"✓ Updated {len(admins)} admin(s) to super_admin role")
        
        # Optionally assign all employees to first super_admin
        super_admins = Employee.query.filter_by(role='super_admin').all()
        if super_admins:
            first_admin = super_admins[0]
            employees = Employee.query.filter_by(role='employee', manager_id=None).all()
            
            if employees:
                print(f"Assigning {len(employees)} unassigned employees to {first_admin.name}...")
                for emp in employees:
                    emp.manager_id = first_admin.id
                db.session.commit()
                print(f"✓ Assigned {len(employees)} employees to {first_admin.name}")
        
        print("\n✅ Migration completed successfully!")
        print("\nSummary:")
        print(f"  - Super Admins: {len(Employee.query.filter_by(role='super_admin').all())}")
        print(f"  - Managers: {len(Employee.query.filter_by(role='admin').all())}")
        print(f"  - Employees: {len(Employee.query.filter_by(role='employee').all())}")

if __name__ == '__main__':
    try:
        migrate_add_manager()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
