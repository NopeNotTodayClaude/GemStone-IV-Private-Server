-- Creature/Monster definitions
USE gemstone_dev;

CREATE TABLE IF NOT EXISTS creatures (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(64) NOT NULL,
    article         VARCHAR(8) DEFAULT 'a',       -- "a", "an", "the", ""
    level           SMALLINT UNSIGNED DEFAULT 1,
    creature_type   ENUM('normal', 'boss', 'rare', 'event') DEFAULT 'normal',

    -- Combat stats
    health_max      INT UNSIGNED DEFAULT 50,
    attack_strength INT DEFAULT 50,               -- AS
    defense_strength INT DEFAULT 50,              -- DS
    casting_strength INT DEFAULT 0,               -- CS (0 = no magic)
    target_defense  INT DEFAULT 0,                -- TD
    action_timer    TINYINT UNSIGNED DEFAULT 10,  -- seconds between actions

    -- Behavior
    behavior_script VARCHAR(128) DEFAULT NULL,    -- Lua script path
    is_aggressive   BOOLEAN DEFAULT TRUE,
    can_cast        BOOLEAN DEFAULT FALSE,
    can_maneuver    BOOLEAN DEFAULT FALSE,
    is_undead       BOOLEAN DEFAULT FALSE,
    body_type       VARCHAR(32) DEFAULT 'humanoid',

    -- Rewards
    experience_value INT UNSIGNED DEFAULT 100,
    silver_min      INT UNSIGNED DEFAULT 0,
    silver_max      INT UNSIGNED DEFAULT 50,
    loot_table_id   INT UNSIGNED DEFAULT NULL,
    skin_noun       VARCHAR(32) DEFAULT NULL,      -- "skin", "pelt", "scalp"
    skin_item_id    INT UNSIGNED DEFAULT NULL,

    -- Description
    description     TEXT,
    death_message   VARCHAR(255) DEFAULT 'falls to the ground and dies.',

    INDEX idx_level (level),
    INDEX idx_name (name)
) ENGINE=InnoDB;

-- Creature loot tables
CREATE TABLE IF NOT EXISTS loot_tables (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(64) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS loot_table_entries (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    loot_table_id   INT UNSIGNED NOT NULL,
    item_id         INT UNSIGNED NOT NULL,
    drop_chance     DECIMAL(5,2) DEFAULT 10.00,   -- percentage
    quantity_min    TINYINT UNSIGNED DEFAULT 1,
    quantity_max    TINYINT UNSIGNED DEFAULT 1,
    FOREIGN KEY (loot_table_id) REFERENCES loot_tables(id),
    INDEX idx_table (loot_table_id)
) ENGINE=InnoDB;
