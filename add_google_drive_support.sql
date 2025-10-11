-- Add Google Drive URL support to existing tables

-- Add image_url column to products table for Google Drive links
ALTER TABLE products ADD COLUMN image_url VARCHAR(500) NULL AFTER image;

-- Create categories table for managing category images
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    image_url VARCHAR(500) NULL,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default categories with placeholder URLs
INSERT INTO categories (name, display_order) VALUES 
('Necklaces', 1),
('Rings', 2),
('Earrings', 3),
('Chains', 4)
ON DUPLICATE KEY UPDATE display_order = VALUES(display_order);