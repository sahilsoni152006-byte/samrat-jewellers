#!/usr/bin/env python3
"""
Script to generate password hash for admin user
Run this script to generate a secure password hash for the admin account
"""

from werkzeug.security import generate_password_hash

def generate_admin_hash():
    password = "admin123"  # Change this to your desired password
    password_hash = generate_password_hash(password)
    
    print("Admin Password Hash Generator")
    print("=" * 40)
    print(f"Password: {password}")
    print(f"Hash: {password_hash}")
    print("\nUpdate the database_setup.sql file with this hash:")
    print(f"UPDATE users SET password_hash = '{password_hash}' WHERE email = 'admin@samratjewellers.com';")

if __name__ == "__main__":
    generate_admin_hash()