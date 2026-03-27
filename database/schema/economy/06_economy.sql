-- Economy tables - shops, banks, transactions
USE gemstone_dev;

-- NPC Shops
CREATE TABLE IF NOT EXISTS shops (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    room_id         INT UNSIGNED NOT NULL,
    shop_type       ENUM('weapon', 'armor', 'general', 'magic', 'gem', 'herb', 'food', 'other') DEFAULT 'general',
    buy_multiplier  DECIMAL(4,2) DEFAULT 1.00,     -- price multiplier for buying
    sell_multiplier DECIMAL(4,2) DEFAULT 0.50,     -- price multiplier for selling
    INDEX idx_room (room_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS shop_inventory (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    shop_id         INT UNSIGNED NOT NULL,
    item_id         INT UNSIGNED NOT NULL,
    stock           SMALLINT DEFAULT -1,            -- -1 = unlimited
    restock_amount  SMALLINT DEFAULT -1,
    restock_interval INT UNSIGNED DEFAULT 3600,     -- seconds
    FOREIGN KEY (shop_id) REFERENCES shops(id),
    INDEX idx_shop (shop_id)
) ENGINE=InnoDB;

-- Player shops
CREATE TABLE IF NOT EXISTS player_shops (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    owner_id        INT UNSIGNED NOT NULL,
    name            VARCHAR(128) NOT NULL,
    room_id         INT UNSIGNED NOT NULL,
    max_items       TINYINT UNSIGNED DEFAULT 75,
    FOREIGN KEY (owner_id) REFERENCES characters(id),
    INDEX idx_owner (owner_id)
) ENGINE=InnoDB;

-- Transaction log
CREATE TABLE IF NOT EXISTS transaction_log (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    character_id    INT UNSIGNED NOT NULL,
    transaction_type ENUM('buy', 'sell', 'trade', 'bounty', 'loot', 'bank_deposit', 'bank_withdraw') NOT NULL,
    amount          BIGINT DEFAULT 0,
    item_id         INT UNSIGNED DEFAULT NULL,
    description     VARCHAR(255),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_char (character_id),
    INDEX idx_date (created_at)
) ENGINE=InnoDB;
