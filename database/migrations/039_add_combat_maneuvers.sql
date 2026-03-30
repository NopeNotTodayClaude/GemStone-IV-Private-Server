-- =============================================================================
-- Migration 039: Combat Maneuvers System
-- Lua-driven maneuver registry, per-character training, and maneuver settings.
-- =============================================================================

CREATE TABLE IF NOT EXISTS combat_maneuvers (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    mnemonic            VARCHAR(32)  NOT NULL UNIQUE,
    name                VARCHAR(96)  NOT NULL,
    maneuver_type       VARCHAR(32)  NOT NULL,
    category_key        VARCHAR(32)  NOT NULL DEFAULT 'general',
    raw_category        VARCHAR(64)  NULL,
    raw_type            VARCHAR(64)  NULL,
    is_guild_skill      TINYINT(1)   NOT NULL DEFAULT 0,
    is_learnable        TINYINT(1)   NOT NULL DEFAULT 1,
    max_rank            TINYINT      NOT NULL DEFAULT 5,
    rank1_cost          SMALLINT     NOT NULL DEFAULT 0,
    rank2_cost          SMALLINT     NOT NULL DEFAULT 0,
    rank3_cost          SMALLINT     NOT NULL DEFAULT 0,
    rank4_cost          SMALLINT     NOT NULL DEFAULT 0,
    rank5_cost          SMALLINT     NOT NULL DEFAULT 0,
    base_roundtime      SMALLINT     NOT NULL DEFAULT 0,
    roundtime_mode      VARCHAR(16)  NOT NULL DEFAULT 'fixed',
    roundtime_modifier  SMALLINT     NOT NULL DEFAULT 0,
    raw_roundtime       VARCHAR(128) NULL,
    stamina_cost_min    SMALLINT     NOT NULL DEFAULT 0,
    stamina_cost_max    SMALLINT     NOT NULL DEFAULT 0,
    raw_stamina         VARCHAR(255) NULL,
    offensive_gear      VARCHAR(96)  NULL,
    requirements        TEXT         NULL,
    available_to        VARCHAR(255) NOT NULL DEFAULT '',
    description         TEXT         NULL,
    mechanics_notes     TEXT         NULL,
    handler_key         VARCHAR(64)  NULL,
    created_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_cman_type        (maneuver_type),
    INDEX idx_cman_category    (category_key),
    INDEX idx_cman_learnable   (is_learnable),
    INDEX idx_cman_guild_skill (is_guild_skill)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS character_combat_maneuvers (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    character_id    INT UNSIGNED NOT NULL,
    maneuver_id     INT UNSIGNED NOT NULL,
    current_rank    TINYINT     NOT NULL DEFAULT 1,
    learned_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at    TIMESTAMP   NULL DEFAULT NULL,

    UNIQUE KEY uq_char_maneuver (character_id, maneuver_id),
    INDEX idx_ccm_character     (character_id),
    INDEX idx_ccm_maneuver      (maneuver_id),
    CONSTRAINT fk_ccm_character FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_ccm_maneuver FOREIGN KEY (maneuver_id)
        REFERENCES combat_maneuvers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS character_combat_maneuver_settings (
    character_id     INT UNSIGNED PRIMARY KEY,
    settings_json    LONGTEXT     NOT NULL,
    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ccms_character FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
