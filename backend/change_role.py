"""
Change User Role
Updates a user's role in the database
"""

from app import create_app
from models import db, Employee

def change_role(email, new_role):
    """Change a user's role"""
    
    app = create_app()
    
    with app.app_context():
        employee = Employee.query.filter_by(email=email).first()
        
        if not employee:
            print(f"❌ Employee with email {email} not found")
            return
        
        old_role = employee.role
        employee.role = new_role
        db.session.commit()
        
        print(f"✅ Changed {employee.name}'s role from {old_role} to {new_role}")

if __name__ == '__main__':
    # Change Luffy from super_admin to admin
    change_role('strawhatluff124@gmail.com', 'admin')
    
    # Show current roles
    app = create_app()
    with app.app_context():
        print("\nCurrent roles:")
        for emp in Employee.query.all():
            print(f"  - {emp.name} ({emp.email}): {emp.role}")
