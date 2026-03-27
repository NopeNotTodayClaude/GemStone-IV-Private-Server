-- ============================================================
-- add_sync_tokens.sql
-- Real-time client sync token table.
-- Each logged-in character gets one row; revoked on logout.
-- ============================================================

CREATE TABLE IF NOT EXISTS sync_tokens (
    id            INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
    character_id  INT UNSIGNED     NOT NULL,
    token         CHAR(64)         NOT NULL,          -- 32 random bytes hex-encoded
    expires_at    DATETIME         NOT NULL,          -- rolling 24h from last refresh
    created_at    TIMESTAMP        DEFAULT CURRENT_TIMESTAMP,
    UNIQUE  KEY uk_token        (token),
    UNIQUE  KEY uk_character_id (character_id),       -- one live token per character
    KEY          idx_expires    (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Clean up stale tokens on migration run
DELETE FROM sync_tokens WHERE expires_at < NOW();
