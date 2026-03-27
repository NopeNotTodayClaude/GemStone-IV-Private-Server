-- 020_add_crafting_foundation.sql
-- Shared Artisan Guild / crafting persistence layer.
-- Retail-aligned scope for the initial shell:
--   ARTISAN SKILLS / RANKS / UNLEARN
--   Character artisan progress
--   Work-in-progress project storage for later Fletching/Cobbling/Forging loops

CREATE TABLE IF NOT EXISTS character_artisan_skills (
    character_id         INT UNSIGNED     NOT NULL,
    skill_key            VARCHAR(32)      NOT NULL,
    ranks                SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    projects_completed   INT UNSIGNED     NOT NULL DEFAULT 0,
    last_worked_at       DATETIME         DEFAULT NULL,
    updated_at           DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id, skill_key),
    KEY idx_artisan_skill (skill_key),
    CONSTRAINT fk_artisan_skills_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS character_artisan_settings (
    character_id            INT UNSIGNED NOT NULL,
    unlearn_preference_key  VARCHAR(32)  DEFAULT NULL,
    updated_at              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id),
    CONSTRAINT fk_artisan_settings_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS artisan_projects (
    id                 BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,
    character_id       INT UNSIGNED      NOT NULL,
    skill_key          VARCHAR(32)       NOT NULL,
    recipe_key         VARCHAR(64)       NOT NULL,
    station_key        VARCHAR(32)       DEFAULT NULL,
    status             ENUM('active','paused','complete','abandoned','failed') NOT NULL DEFAULT 'active',
    stage_index        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    quality_tier       VARCHAR(24)       DEFAULT NULL,
    recipe_snapshot    JSON              DEFAULT NULL,
    progress_data      JSON              DEFAULT NULL,
    started_at         DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at       DATETIME          DEFAULT NULL,
    updated_at         DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_artisan_projects_char_status (character_id, status),
    KEY idx_artisan_projects_skill (skill_key),
    CONSTRAINT fk_artisan_projects_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
