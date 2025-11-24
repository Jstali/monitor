#!/usr/bin/env python3
"""
Database Schema Verification Script
Checks if the database schema matches the expected structure
and provides guidance on fixing any issues
"""

from app import create_app
from models import db, Employee, Organization
from sqlalchemy import inspect
import sys

def check_database_connection():
    """Verify database connection"""
    print("🔍 Checking database connection...")
    try:
        app = create_app()
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection successful\n")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}\n")
        print("💡 Fix: Ensure PostgreSQL is running and DATABASE_URL in .env is correct")
        return False

def check_tables():
    """Check if all required tables exist"""
    print("🔍 Checking required tables...")
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'organizations',
            'employees', 
            'monitoring_sessions',
            'activities',
            'screenshots',
            'monitoring_configs'
        ]
        
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}\n")
            print("💡 Fix: Run 'python create_db.py' to create tables")
            return False
        else:
            print(f"✅ All required tables exist: {', '.join(required_tables)}\n")
            return True

def check_employee_schema():
    """Check if employees table has all required columns"""
    print("🔍 Checking employees table schema...")
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('employees')]
        
        required_columns = [
            'id',
            'email',
            'name',
            'password_hash',
            'role',
            'organization_id',
            'manager_id',
            'is_active',
            'created_at'
        ]
        
        missing_columns = [c for c in required_columns if c not in columns]
        
        if missing_columns:
            print(f"❌ Missing columns in employees table: {', '.join(missing_columns)}\n")
            print("💡 Fix: Run 'python migrate_add_organization.py' to add missing columns")
            return False
        else:
            print(f"✅ Employees table has all required columns\n")
            return True

def check_password_hashing():
    """Check if passwords are properly hashed with bcrypt"""
    print("🔍 Checking password hashing...")
    app = create_app()
    with app.app_context():
        employees = Employee.query.limit(5).all()
        
        if not employees:
            print("⚠️  No employees found in database\n")
            return True
        
        invalid_hashes = []
        for emp in employees:
            # Bcrypt hashes start with $2a$, $2b$, or $2y$
            if not emp.password_hash.startswith('$2'):
                invalid_hashes.append(emp.email)
        
        if invalid_hashes:
            print(f"❌ Invalid password hashes found for: {', '.join(invalid_hashes)}\n")
            print("💡 Fix: Run 'python reset_password.py' to reset passwords with bcrypt")
            return False
        else:
            print(f"✅ All passwords are properly hashed with bcrypt\n")
            return True

def check_organizations():
    """Check if at least one organization exists"""
    print("🔍 Checking organizations...")
    app = create_app()
    with app.app_context():
        org_count = Organization.query.count()
        
        if org_count == 0:
            print("❌ No organizations found\n")
            print("💡 Fix: Run 'python migrate_add_organization.py' to create default organization")
            return False
        else:
            print(f"✅ Found {org_count} organization(s)\n")
            return True

def print_summary():
    """Print database summary"""
    print("=" * 60)
    print("📊 Database Summary")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        print(f"Organizations: {Organization.query.count()}")
        print(f"Total Employees: {Employee.query.count()}")
        print(f"  - Super Admins: {Employee.query.filter_by(role='super_admin').count()}")
        print(f"  - Admins/Managers: {Employee.query.filter_by(role='admin').count()}")
        print(f"  - Regular Employees: {Employee.query.filter_by(role='employee').count()}")
        print(f"  - Active Employees: {Employee.query.filter_by(is_active=True).count()}")
        print()

def main():
    """Main verification"""
    print("=" * 60)
    print("🔧 Database Schema Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Database Connection", check_database_connection),
        ("Required Tables", check_tables),
        ("Employee Schema", check_employee_schema),
        ("Organizations", check_organizations),
        ("Password Hashing", check_password_hashing),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during {name} check: {e}\n")
            results.append((name, False))
    
    # Print final results
    print("=" * 60)
    print("📋 Verification Results")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("=" * 60)
        print("🎉 All checks passed! Database is ready.")
        print("=" * 60)
        print()
        print_summary()
        sys.exit(0)
    else:
        print("=" * 60)
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("=" * 60)
        print()
        print("Common fixes:")
        print("1. python create_db.py              # Create database and tables")
        print("2. python migrate_add_organization.py  # Add missing columns")
        print("3. python reset_password.py         # Fix password hashing")
        print()
        sys.exit(1)

if __name__ == '__main__':
    main()
