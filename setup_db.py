#!/usr/bin/env python3
import mysql.connector
from werkzeug.security import generate_password_hash

# Create database and tables without password
try:
    # Connect without database first
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=''
    )
    cursor = conn.cursor()
    
    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS samrat_jewellers")
    cursor.execute("USE samrat_jewellers")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('admin', 'user') DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            sku VARCHAR(50) UNIQUE NOT NULL,
            category VARCHAR(100) NOT NULL,
            description TEXT,
            price_type ENUM('fixed', 'per_gram') DEFAULT 'fixed',
            weight_in_grams DECIMAL(10,3) DEFAULT 0,
            base_price DECIMAL(10,2) NOT NULL,
            metal_type ENUM('gold', 'silver') DEFAULT 'gold',
            image VARCHAR(255) DEFAULT 'default.jpg',
            stock INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metal_rates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            metal ENUM('gold', 'silver') NOT NULL,
            rate_per_gram DECIMAL(10,2) NOT NULL,
            margin_percent DECIMAL(5,2) DEFAULT 10.00,
            source VARCHAR(50) DEFAULT 'Manual',
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_metal (metal)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            setting_key VARCHAR(100) UNIQUE NOT NULL,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    
    # Insert admin user
    password_hash = generate_password_hash('admin123')
    cursor.execute("""
        INSERT IGNORE INTO users (name, email, password_hash, role) 
        VALUES ('Admin', 'admin@samratjewellers.com', %s, 'admin')
    """, (password_hash,))
    
    # Insert metal rates
    cursor.execute("""
        INSERT INTO metal_rates (metal, rate_per_gram, margin_percent, source) 
        VALUES ('gold', 6500.00, 10.00, 'Manual')
        ON DUPLICATE KEY UPDATE rate_per_gram = 6500.00
    """)
    
    cursor.execute("""
        INSERT INTO metal_rates (metal, rate_per_gram, margin_percent, source) 
        VALUES ('silver', 85.00, 15.00, 'Manual')
        ON DUPLICATE KEY UPDATE rate_per_gram = 85.00
    """)
    
    # Insert settings
    cursor.execute("""
        INSERT INTO settings (setting_key, setting_value) 
        VALUES ('whatsapp_number', '919999999999')
        ON DUPLICATE KEY UPDATE setting_value = '919999999999'
    """)
    
    # Insert sample products
    products = [
        ('Gold Chain Necklace', 'GC001', 'Necklaces', 'Beautiful 22K gold chain necklace', 'per_gram', 15.500, 0, 'gold', 'gold-chain.jpg', 5),
        ('Silver Earrings', 'SE001', 'Earrings', 'Elegant silver earrings', 'per_gram', 8.200, 0, 'silver', 'silver-earrings.jpg', 10),
        ('Diamond Ring', 'DR001', 'Rings', 'Stunning diamond ring', 'fixed', 0, 45000.00, 'gold', 'diamond-ring.jpg', 3)
    ]
    
    for product in products:
        cursor.execute("""
            INSERT IGNORE INTO products (name, sku, category, description, price_type, weight_in_grams, base_price, metal_type, image, stock)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, product)
    
    conn.commit()
    print("✓ Database setup completed successfully!")
    print("Admin credentials: admin@samratjewellers.com / admin123")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()