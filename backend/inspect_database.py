#!/usr/bin/env python3
"""
Database Table Inspector
Checks all tables and their columns
"""

from app import create_app
from models import db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    
    print("=" * 70)
    print("DATABASE TABLE INSPECTION")
    print("=" * 70)
    print(f"\nDatabase: {db.engine.url}")
    print()
    
    # Get all table names
    tables = inspector.get_table_names()
    
    print(f"Total Tables: {len(tables)}\n")
    
    # Expected tables
    expected_tables = [
        'organizations',
        'employees',
        'monitoring_sessions',
        'activities',
        'screenshots',
        'monitoring_configs'  # NEW TABLE
    ]
    
    # Check each expected table
    print("Expected Tables:")
    for table in expected_tables:
        if table in tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} (MISSING!)")
    
    print("\n" + "=" * 70)
    print("TABLE DETAILS")
    print("=" * 70)
    
    # Show details for each table
    for table_name in sorted(tables):
        print(f"\n📋 Table: {table_name}")
        print("-" * 70)
        
        columns = inspector.get_columns(table_name)
        print(f"Columns ({len(columns)}):")
        
        for col in columns:
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col.get('default') else ""
            print(f"  • {col['name']:<25} {col_type:<20} {nullable}{default}")
        
        # Show foreign keys
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print(f"\nForeign Keys:")
            for fk in fks:
                print(f"  • {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
        
        # Show indexes
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print(f"\nIndexes:")
            for idx in indexes:
                print(f"  • {idx['name']}: {idx['column_names']}")
    
    # Check for new columns in screenshots table
    print("\n" + "=" * 70)
    print("SCREENSHOTS TABLE - NEW COLUMNS CHECK")
    print("=" * 70)
    
    screenshot_columns = inspector.get_columns('screenshots')
    column_names = [col['name'] for col in screenshot_columns]
    
    new_columns = ['folder_name', 'activity_name']
    print("\nNew columns for selective monitoring:")
    for col in new_columns:
        if col in column_names:
            print(f"  ✓ {col} exists")
        else:
            print(f"  ✗ {col} MISSING - Migration needed!")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    missing_tables = [t for t in expected_tables if t not in tables]
    
    if missing_tables:
        print(f"\n⚠️  Missing Tables ({len(missing_tables)}):")
        for table in missing_tables:
            print(f"  • {table}")
        print("\n❌ Database migration required!")
        print("   Run: python3 migrate_allowlist.py")
    else:
        print("\n✅ All expected tables exist!")
        
        # Check new columns
        screenshot_columns = inspector.get_columns('screenshots')
        column_names = [col['name'] for col in screenshot_columns]
        
        if 'folder_name' in column_names and 'activity_name' in column_names:
            print("✅ All new columns exist!")
            print("\n🎉 Database is ready for selective monitoring!")
        else:
            print("⚠️  New columns missing in screenshots table")
            print("   Run: python3 migrate_allowlist.py")
