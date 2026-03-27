-- Characters table - player characters with all stats
USE gemstone_dev;

CREATE TABLE IF NOT EXISTS characters (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    account_id      INT UNSIGNED NOT NULL,
    name            VARCHAR(20) NOT NULL UNIQUE,
    race_id         TINYINT UNSIGNED NOT NULL DEFAULT 1,
    profession_id   TINYINT UNSIGNED NOT NULL DEFAULT 1,
    gender          ENUM('male', 'female') DEFAULT 'male',
    level           SMALLINT UNSIGNED DEFAULT 1,
    experience      BIGINT UNSIGNED DEFAULT 0,
    field_experience BIGINT UNSIGNED DEFAULT 0,

    -- 10 Core Stats (base values, 0-100)
    stat_strength       TINYINT UNSIGNED DEFAULT 50,
    stat_constitution   TINYINT UNSIGNED DEFAULT 50,
    stat_dexterity      TINYINT UNSIGNED DEFAULT 50,
    stat_agility        TINYINT UNSIGNED DEFAULT 50,
    stat_discipline     TINYINT UNSIGNED DEFAULT 50,
    stat_aura           TINYINT UNSIGNED DEFAULT 50,
    stat_logic          TINYINT UNSIGNED DEFAULT 50,
    stat_intuition      TINYINT UNSIGNED DEFAULT 50,
    stat_wisdom         TINYINT UNSIGNED DEFAULT 50,
    stat_influence      TINYINT UNSIGNED DEFAULT 50,

    -- Resource pools
    health_current  SMALLINT UNSIGNED DEFAULT 100,
    health_max      SMALLINT UNSIGNED DEFAULT 100,
    mana_current    SMALLINT UNSIGNED DEFAULT 0,
    mana_max        SMALLINT UNSIGNED DEFAULT 0,
    spirit_current  SMALLINT UNSIGNED DEFAULT 10,
    spirit_max      SMALLINT UNSIGNED DEFAULT 10,
    stamina_current SMALLINT UNSIGNED DEFAULT 100,
    stamina_max     SMALLINT UNSIGNED DEFAULT 100,

    -- Economy
    silver          BIGINT UNSIGNED DEFAULT 0,
    bank_silver     BIGINT UNSIGNED DEFAULT 0,

    -- Training points (unspent)
    physical_tp     INT UNSIGNED DEFAULT 0,
    mental_tp       INT UNSIGNED DEFAULT 0,

    -- Position / location
    current_room_id INT UNSIGNED DEFAULT 100,
    position        ENUM('standing', 'sitting', 'kneeling', 'lying', 'dead') DEFAULT 'standing',

    -- Appearance
    height          TINYINT UNSIGNED DEFAULT 70,  -- inches
    hair_color      VARCHAR(32) DEFAULT 'brown',
    hair_style      VARCHAR(32) DEFAULT 'short',
    eye_color       VARCHAR(32) DEFAULT 'blue',

    -- Timestamps
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login      DATETIME,
    total_playtime  INT UNSIGNED DEFAULT 0,  -- seconds

    -- Bounty system
    bounty_points   INT UNSIGNED DEFAULT 0,

    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    INDEX idx_account (account_id),
    INDEX idx_name (name),
    INDEX idx_level (level),
    INDEX idx_room (current_room_id)
) ENGINE=InnoDB;

-- Character skills training
CREATE TABLE IF NOT EXISTS character_skills (
    character_id    INT UNSIGNED NOT NULL,
    skill_id        SMALLINT UNSIGNED NOT NULL,
    ranks           SMALLINT UNSIGNED DEFAULT 0,
    bonus           SMALLINT DEFAULT 0,
    PRIMARY KEY (character_id, skill_id),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Active spell effects on character
CREATE TABLE IF NOT EXISTS character_spells_active (
    character_id    INT UNSIGNED NOT NULL,
    spell_id        SMALLINT UNSIGNED NOT NULL,
    duration_remaining INT DEFAULT 0,  -- seconds
    caster_id       INT UNSIGNED,
    PRIMARY KEY (character_id, spell_id),
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Character inventory
CREATE TABLE IF NOT EXISTS character_inventory (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    character_id    INT UNSIGNED NOT NULL,
    item_id         INT UNSIGNED NOT NULL,
    container_id    INT UNSIGNED DEFAULT NULL,  -- NULL = worn/held directly
    slot            VARCHAR(32) DEFAULT NULL,    -- wear location
    quantity        SMALLINT UNSIGNED DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    INDEX idx_char (character_id)
) ENGINE=InnoDB;
