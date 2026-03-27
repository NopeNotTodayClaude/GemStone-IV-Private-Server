CREATE TABLE IF NOT EXISTS room_ground_items (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    room_id INT UNSIGNED NOT NULL,
    item_id INT UNSIGNED NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_short_name VARCHAR(255) NOT NULL,
    item_noun VARCHAR(80) DEFAULT NULL,
    item_type VARCHAR(64) DEFAULT NULL,
    base_value INT NOT NULL DEFAULT 0,
    item_data LONGTEXT NOT NULL,
    dropped_by_character_id INT UNSIGNED DEFAULT NULL,
    dropped_by_name VARCHAR(64) DEFAULT NULL,
    source VARCHAR(32) NOT NULL DEFAULT 'drop',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    KEY idx_room_ground_room (room_id, expires_at),
    KEY idx_room_ground_expiry (expires_at)
);
