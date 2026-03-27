-- 023_add_fame_system.sql
-- Starter fame system, retail-inspired.

ALTER TABLE characters
    ADD COLUMN fame BIGINT UNSIGNED NOT NULL DEFAULT 0 AFTER field_experience,
    ADD COLUMN fame_list_opt_in TINYINT(1) NOT NULL DEFAULT 0 AFTER fame;

CREATE TABLE IF NOT EXISTS character_fame_ledger (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    character_id INT UNSIGNED NOT NULL,
    amount INT NOT NULL,
    source_key VARCHAR(64) NOT NULL,
    detail_text VARCHAR(255) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_fame_ledger_char (character_id, created_at),
    CONSTRAINT fk_fame_ledger_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
