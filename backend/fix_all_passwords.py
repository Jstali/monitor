#!/usr/bin/env python3
"""
Fix All Passwords Script
Resets all employee passwords to use bcrypt hashing
"""

from app import create_app
from models import db, Employee

def fix_all_passwords():
    """Fix all passwords that are not properly bcrypt hashed"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔧 Fixing Password Hashes")
        print("=" * 60)
        print()
        
        employees = Employee.query.all()
        
        if not employees:
            print("⚠️  No employees found in database")
            return
        
        fixed_count = 0
        already_fixed = 0
        
        for emp in employees:
            # Check if password is already bcrypt hashed
            if emp.password_hash.startswith('$2'):
                print(f"✓ {emp.email} - Already using bcrypt")
                already_fixed += 1
            else:
                print(f"🔧 {emp.email} - Converting to bcrypt...")
                # Set a default password - users should change this
                emp.set_password('test@123')
                fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print()
            print(f"✅ Fixed {fixed_count} password(s)")
            print(f"⚠️  Default password set to: test@123")
            print(f"⚠️  Users should change their passwords after logging in")
        
        print()
        print("=" * 60)
        print("Summary:")
        print(f"  Total employees: {len(employees)}")
        print(f"  Already using bcrypt: {already_fixed}")
        print(f"  Fixed: {fixed_count}")
        print("=" * 60)

if __name__ == '__main__':
    try:
        fix_all_passwords()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
