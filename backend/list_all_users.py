#!/usr/bin/env python3
"""
List All Users and Their Credentials
Shows all employees with their roles and password status
"""

from app import create_app
from models import db, Employee, Organization

def list_all_users():
    """List all users with their details"""
    
    app = create_app()
    
    with app.app_context():
        print()
        print("=" * 80)
        print("👥 ALL USERS IN DATABASE")
        print("=" * 80)
        print()
        
        employees = Employee.query.order_by(Employee.id).all()
        
        if not employees:
            print("⚠️  No users found in database")
            return
        
        # Get organization info
        orgs = {org.id: org.name for org in Organization.query.all()}
        
        print(f"{'ID':<4} {'Name':<20} {'Email':<30} {'Role':<15} {'Organization':<20} {'Active':<8}")
        print("-" * 80)
        
        for emp in employees:
            org_name = orgs.get(emp.organization_id, 'N/A')
            active = "✓" if emp.is_active else "✗"
            print(f"{emp.id:<4} {emp.name:<20} {emp.email:<30} {emp.role:<15} {org_name:<20} {active:<8}")
        
        print()
        print("=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Total Users: {len(employees)}")
        print(f"  Super Admins: {len([e for e in employees if e.role == 'super_admin'])}")
        print(f"  Admins/Managers: {len([e for e in employees if e.role == 'admin' or e.role == 'manager'])}")
        print(f"  Employees: {len([e for e in employees if e.role == 'employee'])}")
        print(f"  Active: {len([e for e in employees if e.is_active])}")
        print(f"  Inactive: {len([e for e in employees if not e.is_active])}")
        print()
        
        print("=" * 80)
        print("🔑 DEFAULT CREDENTIALS (if passwords were reset)")
        print("=" * 80)
        print("All users currently have password: test@123")
        print()
        print("Individual User Credentials:")
        print("-" * 80)
        for emp in employees:
            print(f"  {emp.role.upper():<15} | {emp.email:<30} | Password: test@123")
        print()
        
        print("💡 To change a password:")
        print("   1. Edit reset_password.py with the user's email and new password")
        print("   2. Run: python reset_password.py")
        print()

if __name__ == '__main__':
    try:
        list_all_users()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
