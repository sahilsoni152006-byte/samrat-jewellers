#!/usr/bin/env python3
"""
Startup script for Samrat Jewellers eCommerce application
"""

import os
import sys
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create admin user with proper password hash"""
    try:
        from app import get_db_connection
        
        password = "admin123"
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE email = 'admin@samratjewellers.com'")
        if cursor.fetchone():
            print("Admin user already exists")
        else:
            # Create admin user
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role) 
                VALUES ('Admin', 'admin@samratjewellers.com', %s, 'admin')
            """, (password_hash,))
            conn.commit()
            print("Admin user created successfully")
            print(f"Email: admin@samratjewellers.com")
            print(f"Password: {password}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating admin user: {e}")

def check_requirements():
    """Check if all requirements are met"""
    try:
        import flask
        import mysql.connector
        import requests
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_database():
    """Check database connection"""
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Please check your MySQL configuration in app.py")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'static/images/products',
        'static/css',
        'static/js'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ Directories created")

def main():
    """Main startup function"""
    print("Samrat Jewellers - Startup Script")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check database
    if not check_database():
        print("\nPlease ensure:")
        print("1. MySQL is running")
        print("2. Database 'samrat_jewellers' exists")
        print("3. Run: mysql -u root -p < database_setup.sql")
        sys.exit(1)
    
    # Create admin user
    create_admin_user()
    
    print("\n" + "=" * 40)
    print("Setup completed successfully!")
    print("\nTo start the application:")
    print("python app.py")
    print("\nAccess URLs:")
    print("Website: http://localhost:5000")
    print("Admin Panel: http://localhost:5000/admin/login")
    print("\nAdmin Credentials:")
    print("Email: admin@samratjewellers.com")
    print("Password: admin123")

if __name__ == "__main__":
    main()