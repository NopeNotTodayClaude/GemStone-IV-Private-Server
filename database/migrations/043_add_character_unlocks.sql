CREATE TABLE IF NOT EXISTS character_unlocks (
    character_id INT(10) UNSIGNED NOT NULL,
    unlock_key VARCHAR(96) NOT NULL,
    unlock_type VARCHAR(32) NOT NULL DEFAULT 'generic',
    notes TEXT NULL,
    unlocked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id, unlock_key),
    KEY idx_character_unlocks_type (unlock_type),
    CONSTRAINT fk_character_unlocks_character
        FOREIGN KEY (character_id) REFERENCES characters(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
