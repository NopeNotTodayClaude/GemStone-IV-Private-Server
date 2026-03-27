-- GemStone IV Private Server - Database Setup
-- Run this first to create the database and user

CREATE DATABASE IF NOT EXISTS gemstone_dev
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS gemstone_test
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create application user
CREATE USER IF NOT EXISTS 'gemstone'@'localhost' IDENTIFIED BY 'gemstone_dev';
GRANT ALL PRIVILEGES ON gemstone_dev.* TO 'gemstone'@'localhost';
GRANT ALL PRIVILEGES ON gemstone_test.* TO 'gemstone'@'localhost';
FLUSH PRIVILEGES;

USE gemstone_dev;
