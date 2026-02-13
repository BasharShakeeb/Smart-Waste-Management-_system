-- ============================================
-- Collect Me IoT Database Setup Script
-- Run this script in MySQL Workbench
-- ============================================

-- Create the database
CREATE DATABASE IF NOT EXISTS collect_me_iot 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Use the database
USE collect_me_iot;

-- Create a dedicated user for the application (optional but recommended)
-- Uncomment and modify the password below if you want to create a specific user
/*
CREATE USER IF NOT EXISTS 'collectme_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON collect_me_iot.* TO 'collectme_user'@'localhost';
FLUSH PRIVILEGES;
*/

-- The Flask application will automatically create all tables when you run it
-- But here are the table structures for reference:

-- ============================================
-- Table: users
-- ============================================
/*
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'driver',
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
*/

-- ============================================
-- Table: vehicles
-- ============================================
/*
CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL UNIQUE,
    vehicle_type VARCHAR(50) NOT NULL,
    make VARCHAR(50),
    model VARCHAR(50),
    year INT,
    license_plate VARCHAR(20) UNIQUE,
    capacity FLOAT,
    fuel_type VARCHAR(20) DEFAULT 'diesel',
    fuel_level FLOAT,
    mileage FLOAT,
    last_maintenance DATETIME,
    next_maintenance DATETIME,
    insurance_expiry DATE,
    status VARCHAR(20) DEFAULT 'available',
    gps_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_vehicle_id (vehicle_id)
);
*/

-- Show databases to confirm creation
SHOW DATABASES LIKE 'collect_me_iot';

-- Show current database
SELECT DATABASE() as current_database;

-- Show table status (will be empty until Flask creates the tables)
SHOW TABLE STATUS;