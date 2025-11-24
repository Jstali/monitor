#!/usr/bin/env python3
"""
Create SUPER admin user
"""

from app import create_app
from models import db, Employee, Organization

def create_super_user():
    """Create the SUPER admin user"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔧 Creating SUPER Admin")
        print("=" * 60)
        print()
        
        # Get default organization
        org = Organization.query.first()
        if not org:
            print("❌ No organization found. Creating default organization...")
            org = Organization(name="Default Organization", screenshot_interval=10)
            db.session.add(org)
            db.session.commit()
            print(f"✓ Created organization: {org.name}")
        
        # Check if SUPER already exists
        existing = Employee.query.filter_by(name='SUPER').first()
        if existing:
            print(f"⚠️  User 'SUPER' already exists with email: {existing.email}")
            print(f"   Current role: {existing.role}")
            
            if existing.role != 'super_admin':
                update = input("\nPromote to super_admin? (y/n): ").lower()
                if update == 'y':
                    existing.role = 'super_admin'
                    existing.set_password('test@123')
                    db.session.commit()
                    print("✅ SUPER promoted to super_admin")
            return
        
        # Create SUPER admin
        print("Creating new SUPER admin user...")
        email = input("Email for SUPER (default: super@admin.com): ").strip() or "super@admin.com"
        password = input("Password (default: test@123): ").strip() or "test@123"
        
        super_admin = Employee(
            email=email,
            name='SUPER',
            role='super_admin',
            organization_id=org.id,
            is_active=True
        )
        super_admin.set_password(password)
        
        db.session.add(super_admin)
        db.session.commit()
        
        print()
        print("=" * 60)
        print("✅ SUPER Admin Created Successfully!")
        print("=" * 60)
        print(f"Name: {super_admin.name}")
        print(f"Email: {super_admin.email}")
        print(f"Password: {password}")
        print(f"Role: {super_admin.role}")
        print()
        
        # Print all users
        print("Current Users:")
        print("-" * 60)
        for emp in Employee.query.all():
            print(f"  {emp.role.upper():15} | {emp.name:15} | {emp.email}")
        print()

if __name__ == '__main__':
    try:
        create_super_user()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
