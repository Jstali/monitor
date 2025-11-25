#!/usr/bin/env python3
"""
Database Creation Script
Creates the PostgreSQL database and all required tables
"""

import os
import sys
from urllib.parse import urlparse

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg://postgres:abcd@host.docker.internal:5432/monitor')

# Parse DATABASE_URL to extract connection parameters
# Format: postgresql+psycopg://user:password@host:port/database
try:
    # Remove the postgresql+psycopg:// prefix for parsing
    url = DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')
    parsed = urlparse(url)
    DB_HOST = parsed.hostname or 'host.docker.internal'
    DB_PORT = parsed.port or 5432
    DB_USER = parsed.username or 'postgres'
    DB_PASSWORD = parsed.password or 'abcd'
    DB_NAME = parsed.path.lstrip('/') or 'monitor'
except Exception as e:
    print(f"Error parsing DATABASE_URL: {e}")
    # Fallback to defaults
    DB_HOST = 'host.docker.internal'
    DB_PORT = 5432
    DB_USER = 'postgres'
    DB_PASSWORD = 'abcd'
    DB_NAME = 'monitor'

def create_database():
    """Verify the monitor database exists (skip creation since it's on server)"""
    try:
        import psycopg
        # Connect directly to the monitor database to verify it exists
        print(f"Connecting to PostgreSQL database '{DB_NAME}' at {DB_HOST}:{DB_PORT}...")
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute('SELECT version()')
        version = cursor.fetchone()
        print(f"✓ Database '{DB_NAME}' exists and is accessible")
        print(f"✓ PostgreSQL version: {version[0][:50]}...")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        print(f"  Attempted connection to: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        return False

def create_tables():
    """Create all required tables using SQLAlchemy models"""
    try:
        print("\nCreating database tables...")
        
        # Import Flask app and models
        from app import create_app
        from models import db
        
        # Create app and tables
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✓ All tables created successfully")
            
            # Print created tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\nCreated tables: {', '.join(tables)}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_connection():
    """Verify database connection (already done in create_database)"""
    return True

def main():
    """Main execution"""
    print("="*60)
    print("Employee Monitoring System - Database Setup")
    print("="*60)
    print()
    
    # Step 1: Create database
    if not create_database():
        print("\n✗ Failed to create database")
        sys.exit(1)
    
    # Step 2: Verify connection
    if not verify_connection():
        print("\n✗ Failed to verify connection")
        sys.exit(1)
    
    # Step 3: Create tables
    if not create_tables():
        print("\n✗ Failed to create tables")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ Database setup completed successfully!")
    print("="*60)
    print()
    print("Database Details:")
    print(f"  Host: {DB_HOST}")
    print(f"  Port: {DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User: {DB_USER}")
    print()
    print("You can now start the Flask application:")
    print("  python app.py")
    print()

if __name__ == '__main__':
    main()
