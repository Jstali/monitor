"""
Assign Existing Employees to Managers
Updates employees with NULL manager_id to be assigned to first admin/super_admin
"""

from app import create_app
from models import db, Employee

def assign_employees_to_managers():
    """Assign unassigned employees to managers"""
    
    app = create_app()
    
    with app.app_context():
        print("Assigning unassigned employees to managers...")
        
        # Get all employees without a manager
        unassigned = Employee.query.filter_by(manager_id=None, role='employee').all()
        
        if not unassigned:
            print("✓ No unassigned employees found")
            return
        
        print(f"Found {len(unassigned)} unassigned employee(s)")
        
        # Group by organization
        by_org = {}
        for emp in unassigned:
            if emp.organization_id not in by_org:
                by_org[emp.organization_id] = []
            by_org[emp.organization_id].append(emp)
        
        # Assign to first admin/super_admin in each organization
        for org_id, employees in by_org.items():
            manager = Employee.query.filter_by(
                organization_id=org_id
            ).filter(
                Employee.role.in_(['super_admin', 'admin'])
            ).first()
            
            if manager:
                for emp in employees:
                    emp.manager_id = manager.id
                    print(f"  ✓ Assigned {emp.name} ({emp.email}) to {manager.name}")
            else:
                print(f"  ⚠️  No manager found for organization {org_id}")
        
        db.session.commit()
        print("\n✅ Assignment completed!")

if __name__ == '__main__':
    try:
        assign_employees_to_managers()
    except Exception as e:
        print(f"\n❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
