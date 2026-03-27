-- Quest tracking tables
USE gemstone_dev;

-- Quest definitions (supplements Lua quest scripts)
CREATE TABLE IF NOT EXISTS quests (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    slug            VARCHAR(64) NOT NULL UNIQUE,
    name            VARCHAR(128) NOT NULL,
    description     TEXT,
    level_required  TINYINT UNSIGNED DEFAULT 1,
    is_repeatable   BOOLEAN DEFAULT FALSE,
    quest_type      ENUM('main', 'side', 'bounty', 'guild', 'seasonal') DEFAULT 'side',
    INDEX idx_slug (slug)
) ENGINE=InnoDB;

-- Character quest progress
CREATE TABLE IF NOT EXISTS character_quests (
    character_id    INT UNSIGNED NOT NULL,
    quest_id        INT UNSIGNED NOT NULL,
    stage           SMALLINT UNSIGNED DEFAULT 0,
    status          ENUM('active', 'completed', 'failed', 'abandoned') DEFAULT 'active',
    started_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at    DATETIME DEFAULT NULL,
    times_completed INT UNSIGNED DEFAULT 0,
    PRIMARY KEY (character_id, quest_id),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (quest_id) REFERENCES quests(id)
) ENGINE=InnoDB;

-- Bounty system tracking
CREATE TABLE IF NOT EXISTS character_bounties (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    character_id    INT UNSIGNED NOT NULL,
    bounty_type     ENUM('gem', 'skin', 'forage', 'heirloom', 'cull', 'boss', 'escort', 'rescue', 'bandit') NOT NULL,
    target          VARCHAR(128),                   -- what to kill/find/collect
    target_count    SMALLINT UNSIGNED DEFAULT 1,
    current_count   SMALLINT UNSIGNED DEFAULT 0,
    zone_id         SMALLINT UNSIGNED DEFAULT NULL,
    status          ENUM('active', 'completed', 'expired') DEFAULT 'active',
    assigned_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at      DATETIME,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    INDEX idx_char (character_id)
) ENGINE=InnoDB;
