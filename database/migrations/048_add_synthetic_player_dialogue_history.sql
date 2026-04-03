-- 048_add_synthetic_player_dialogue_history.sql
-- Run:
--   mysql --protocol=TCP --skip-ssl -u root gemstone_dev < database/migrations/048_add_synthetic_player_dialogue_history.sql

CREATE TABLE IF NOT EXISTS synthetic_player_dialogue_history (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    text_hash CHAR(40) NOT NULL,
    normalized_text VARCHAR(768) NOT NULL,
    last_used_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usage_count BIGINT UNSIGNED NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_synthetic_player_dialogue_history_hash (text_hash),
    KEY idx_synthetic_player_dialogue_history_last_used (last_used_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
