ALTER TABLE shops
    ADD COLUMN IF NOT EXISTS backroom_room_id INT UNSIGNED NULL AFTER room_id;

CREATE TABLE IF NOT EXISTS pawnshop_backroom_inventory (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    shop_id INT UNSIGNED NOT NULL,
    item_id INT UNSIGNED NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_short_name VARCHAR(255) NOT NULL,
    item_noun VARCHAR(80) DEFAULT NULL,
    item_type VARCHAR(64) DEFAULT NULL,
    category_key VARCHAR(16) NOT NULL DEFAULT 'misc',
    base_value INT NOT NULL DEFAULT 0,
    ask_price INT NOT NULL DEFAULT 0,
    item_data LONGTEXT NOT NULL,
    sold_by_character_id INT UNSIGNED DEFAULT NULL,
    sold_by_name VARCHAR(64) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_pawn_backroom_shop_created (shop_id, created_at),
    KEY idx_pawn_backroom_shop_category (shop_id, category_key, created_at)
);

UPDATE shops
SET shop_type = 'pawn',
    backroom_room_id = 10380
WHERE id = 6;
