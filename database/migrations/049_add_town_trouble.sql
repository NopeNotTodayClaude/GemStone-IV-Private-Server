-- 049_add_town_trouble.sql
-- Run:
--   mysql --protocol=TCP --skip-ssl -u root gemstone_dev < database/migrations/049_add_town_trouble.sql

CREATE TABLE IF NOT EXISTS town_trouble_incidents (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    city_key VARCHAR(64) NOT NULL,
    incident_key VARCHAR(64) NOT NULL,
    district_key VARCHAR(64) NOT NULL,
    state VARCHAR(24) NOT NULL DEFAULT 'active',
    target_level INT UNSIGNED NOT NULL DEFAULT 1,
    difficulty TINYINT UNSIGNED NOT NULL DEFAULT 1,
    duration_seconds INT UNSIGNED NOT NULL DEFAULT 600,
    stage_index INT UNSIGNED NOT NULL DEFAULT 0,
    state_json JSON NULL,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    resolved_at DATETIME NULL,
    next_announce_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_town_trouble_city_state (city_key, state),
    KEY idx_town_trouble_expires (expires_at),
    KEY idx_town_trouble_incident (incident_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS town_trouble_participants (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    incident_id BIGINT UNSIGNED NOT NULL,
    character_id INT UNSIGNED NOT NULL,
    damage_done INT UNSIGNED NOT NULL DEFAULT 0,
    kill_count INT UNSIGNED NOT NULL DEFAULT 0,
    qualifies TINYINT(1) NOT NULL DEFAULT 0,
    reward_payload_json JSON NULL,
    reward_granted_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_town_trouble_participant (incident_id, character_id),
    KEY idx_town_trouble_character_rewards (character_id, reward_granted_at),
    CONSTRAINT fk_town_trouble_participant_incident
        FOREIGN KEY (incident_id) REFERENCES town_trouble_incidents(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_town_trouble_participant_character
        FOREIGN KEY (character_id) REFERENCES characters(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
