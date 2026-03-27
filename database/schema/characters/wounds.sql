-- ============================================================
-- Migration: character_wounds table
-- GemStone IV private server
-- ============================================================
-- One row per (character, location).
-- wound_rank 0-3: 0 = no wound, 1 = minor, 2 = moderate, 3 = severe
-- scar_rank  0-3: 0 = no scar
-- is_bleeding: 1 if actively bleeding, 0 otherwise
-- bandaged:    1 if TEND was applied (stops bleed, wound persists)
-- ============================================================

USE gemstone_dev;

CREATE TABLE IF NOT EXISTS character_wounds (
    id              INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    character_id    INT UNSIGNED     NOT NULL,
    location        VARCHAR(30)      NOT NULL
                        COMMENT 'head|neck|chest|abdomen|back|right_eye|left_eye|right_arm|left_arm|right_hand|left_hand|right_leg|left_leg|nervous_system',
    wound_rank      TINYINT UNSIGNED NOT NULL DEFAULT 0,
    scar_rank       TINYINT UNSIGNED NOT NULL DEFAULT 0,
    is_bleeding     TINYINT(1)       NOT NULL DEFAULT 0,
    bandaged        TINYINT(1)       NOT NULL DEFAULT 0,
    created_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE  KEY uq_char_loc      (character_id, location),
    INDEX   idx_char_wounds      (character_id),
    INDEX   idx_bleeding         (character_id, is_bleeding),

    CONSTRAINT fk_cw_character
        FOREIGN KEY (character_id)
        REFERENCES  characters(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COMMENT='Per-location wound and scar tracking for player characters';

-- ── Seed valid location names as a reference check view ──────────────
-- (optional, useful for debugging)
CREATE OR REPLACE VIEW v_wound_summary AS
SELECT
    c.name          AS character_name,
    cw.location,
    cw.wound_rank,
    cw.scar_rank,
    cw.is_bleeding,
    cw.bandaged,
    cw.updated_at
FROM character_wounds cw
JOIN characters c ON c.id = cw.character_id
WHERE cw.wound_rank > 0 OR cw.scar_rank > 0
ORDER BY c.name, cw.wound_rank DESC, cw.scar_rank DESC;
