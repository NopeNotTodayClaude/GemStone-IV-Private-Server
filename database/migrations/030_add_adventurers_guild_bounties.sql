-- 030_add_adventurers_guild_bounties.sql
-- Public Adventurer's Guild registration, ranks, and live bounty tracking.

CREATE TABLE IF NOT EXISTS character_adventurer_guild (
    character_id            INT UNSIGNED NOT NULL PRIMARY KEY,
    registered_town_name    VARCHAR(64)  DEFAULT NULL,
    rank_level              SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    rank_title              VARCHAR(64)  NOT NULL DEFAULT 'Associate',
    rank_points             INT UNSIGNED NOT NULL DEFAULT 0,
    lifetime_bounties       INT UNSIGNED NOT NULL DEFAULT 0,
    registered_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_character_adventurer_guild_character
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB;

ALTER TABLE character_bounties
    ADD COLUMN IF NOT EXISTS town_name VARCHAR(64) DEFAULT NULL AFTER zone_id,
    ADD COLUMN IF NOT EXISTS taskmaster_template_id VARCHAR(64) DEFAULT NULL AFTER town_name,
    ADD COLUMN IF NOT EXISTS taskmaster_room_id INT UNSIGNED DEFAULT NULL AFTER taskmaster_template_id,
    ADD COLUMN IF NOT EXISTS target_template_id VARCHAR(64) DEFAULT NULL AFTER target,
    ADD COLUMN IF NOT EXISTS target_display_name VARCHAR(128) DEFAULT NULL AFTER target_template_id,
    ADD COLUMN IF NOT EXISTS reward_silver INT UNSIGNED NOT NULL DEFAULT 0 AFTER expires_at,
    ADD COLUMN IF NOT EXISTS reward_experience INT UNSIGNED NOT NULL DEFAULT 0 AFTER reward_silver,
    ADD COLUMN IF NOT EXISTS reward_fame INT UNSIGNED NOT NULL DEFAULT 0 AFTER reward_experience,
    ADD COLUMN IF NOT EXISTS reward_points INT UNSIGNED NOT NULL DEFAULT 0 AFTER reward_fame,
    ADD COLUMN IF NOT EXISTS completed_at DATETIME DEFAULT NULL AFTER reward_points;

CREATE INDEX IF NOT EXISTS idx_character_bounties_character_status
    ON character_bounties (character_id, status);
