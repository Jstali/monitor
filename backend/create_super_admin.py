#!/usr/bin/env python3
"""
Create or Promote Super Admin
"""

from app import create_app
from models import db, Employee, Organization

def create_super_admin():
    """Create or promote a super admin user"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔧 Super Admin Setup")
        print("=" * 60)
        print()
        
        # Get default organization
        org = Organization.query.first()
        if not org:
            print("❌ No organization found. Run migrate_add_organization.py first")
            return
        
        # Check if super admin already exists
        existing_super_admin = Employee.query.filter_by(role='super_admin').first()
        
        if existing_super_admin:
            print(f"✓ Super admin already exists: {existing_super_admin.email}")
            print()
            choice = input("Do you want to create another super admin? (y/n): ").lower()
            if choice != 'y':
                return
        
        print("\nCreate New Super Admin")
        print("-" * 60)
        
        email = input("Email: ").strip()
        name = input("Name: ").strip()
        password = input("Password (default: test@123): ").strip() or "test@123"
        
        # Check if email already exists
        existing = Employee.query.filter_by(email=email).first()
        if existing:
            print(f"\n⚠️  User with email {email} already exists")
            promote = input("Promote to super_admin? (y/n): ").lower()
            if promote == 'y':
                existing.role = 'super_admin'
                existing.set_password(password)
                db.session.commit()
                print(f"\n✅ {existing.name} promoted to super_admin")
                print(f"   Email: {existing.email}")
                print(f"   Password: {password}")
            return
        
        # Create new super admin
        super_admin = Employee(
            email=email,
            name=name,
            role='super_admin',
            organization_id=org.id,
            is_active=True
        )
        super_admin.set_password(password)
        
        db.session.add(super_admin)
        db.session.commit()
        
        print()
        print("=" * 60)
        print("✅ Super Admin Created Successfully!")
        print("=" * 60)
        print(f"Name: {super_admin.name}")
        print(f"Email: {super_admin.email}")
        print(f"Password: {password}")
        print(f"Role: {super_admin.role}")
        print(f"Organization: {org.name}")
        print()
        
        # Print summary
        print("Current Users:")
        print("-" * 60)
        for emp in Employee.query.all():
            print(f"  {emp.role.upper():15} | {emp.name:15} | {emp.email}")
        print()

if __name__ == '__main__':
    try:
        create_super_admin()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
