"""
Promote First Admin to Super Admin
Updates the first admin in each organization to super_admin role
"""

from app import create_app
from models import db, Employee

def promote_first_admin():
    """Promote first admin to super_admin"""
    
    app = create_app()
    
    with app.app_context():
        print("Promoting first admin to super_admin...")
        
        # Get all organizations
        from models import Organization
        orgs = Organization.query.all()
        
        for org in orgs:
            # Find first admin in this organization
            first_admin = Employee.query.filter_by(
                organization_id=org.id,
                role='admin'
            ).order_by(Employee.id).first()
            
            if first_admin:
                first_admin.role = 'super_admin'
                print(f"✓ Promoted {first_admin.name} ({first_admin.email}) to super_admin in {org.name}")
        
        db.session.commit()
        print("\n✅ Promotion completed!")
        
        # Show summary
        print("\nCurrent roles:")
        print(f"  - Super Admins: {Employee.query.filter_by(role='super_admin').count()}")
        print(f"  - Managers (Admin): {Employee.query.filter_by(role='admin').count()}")
        print(f"  - Employees: {Employee.query.filter_by(role='employee').count()}")

if __name__ == '__main__':
    try:
        promote_first_admin()
    except Exception as e:
        print(f"\n❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
