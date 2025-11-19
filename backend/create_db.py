#!/usr/bin/env python3
"""
Database Creation Script
Creates the PostgreSQL database and all required tables
"""

import psycopg
import sys

# Database connection parameters
DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'postgres'
DB_PASSWORD = 'stali'
DB_NAME = 'monitor'

def create_database():
    """Create the monitor database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (default postgres database)
        print(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT}...")
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname='postgres',
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{DB_NAME}' already exists")
        else:
            # Create database
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"✓ Database '{DB_NAME}' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg.Error as e:
        print(f"✗ Error creating database: {e}")
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
    """Verify database connection"""
    try:
        print("\nVerifying database connection...")
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
        print(f"✓ Connected to PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except psycopg.Error as e:
        print(f"✗ Connection error: {e}")
        return False

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
