-- Create database
CREATE DATABASE IF NOT EXISTS samrat_jewellers;
USE samrat_jewellers;

-- Users table for admin authentication
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
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
);

-- Metal rates table
CREATE TABLE metal_rates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metal ENUM('gold', 'silver') NOT NULL,
    rate_per_gram DECIMAL(10,2) NOT NULL,
    margin_percent DECIMAL(5,2) DEFAULT 10.00,
    source VARCHAR(50) DEFAULT 'Manual',
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_metal (metal)
);

-- Settings table
CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default admin user (password: admin123)
INSERT INTO users (name, email, password_hash, role) VALUES 
('Admin', 'admin@samratjewellers.com', 'pbkdf2:sha256:260000$salt123$5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'admin');

-- Insert default metal rates
INSERT INTO metal_rates (metal, rate_per_gram, margin_percent, source) VALUES 
('gold', 6500.00, 10.00, 'Manual'),
('silver', 85.00, 15.00, 'Manual');

-- Insert default settings
INSERT INTO settings (setting_key, setting_value) VALUES 
('whatsapp_number', '919999999999'),
('store_name', 'Samrat Jewellers'),
('store_address', 'Mumbai, India');

-- Insert sample products
INSERT INTO products (name, sku, category, description, price_type, weight_in_grams, base_price, metal_type, image, stock) VALUES 
('Gold Chain Necklace', 'GC001', 'Necklaces', 'Beautiful 22K gold chain necklace with intricate design', 'per_gram', 15.500, 0, 'gold', 'gold-chain.jpg', 5),
('Silver Earrings', 'SE001', 'Earrings', 'Elegant silver earrings with traditional design', 'per_gram', 8.200, 0, 'silver', 'silver-earrings.jpg', 10),
('Diamond Ring', 'DR001', 'Rings', 'Stunning diamond ring with 18K gold band', 'fixed', 0, 45000.00, 'gold', 'diamond-ring.jpg', 3),
('Gold Bracelet', 'GB001', 'Bracelets', '22K gold bracelet with modern design', 'per_gram', 12.300, 0, 'gold', 'gold-bracelet.jpg', 7),
('Silver Pendant', 'SP001', 'Pendants', 'Beautiful silver pendant with gemstone', 'per_gram', 5.800, 0, 'silver', 'silver-pendant.jpg', 15),
('Gold Bangles Set', 'GBS001', 'Bangles', 'Set of 2 traditional gold bangles', 'per_gram', 25.600, 0, 'gold', 'gold-bangles.jpg', 4);