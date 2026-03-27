-- Accounts table - player login accounts
USE gemstone_dev;

CREATE TABLE IF NOT EXISTS accounts (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(32) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    email           VARCHAR(255),
    role            ENUM('player', 'gm', 'admin') DEFAULT 'player',
    is_premium      BOOLEAN DEFAULT FALSE,
    max_characters  TINYINT UNSIGNED DEFAULT 5,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login      DATETIME,
    is_banned       BOOLEAN DEFAULT FALSE,
    ban_reason      TEXT,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB;
