-- =============================================================================
-- Migration 011: Weapon Techniques System
-- GemStone IV canonical implementation
-- =============================================================================

-- ---------------------------------------------------------------------------
-- weapon_techniques  (master definition table, seeded from seed file)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weapon_techniques (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    mnemonic            VARCHAR(32)  NOT NULL UNIQUE,      -- e.g. 'cripple'
    name                VARCHAR(64)  NOT NULL,             -- e.g. 'Cripple'
    weapon_category     VARCHAR(32)  NOT NULL,             -- edged|blunt|twohanded|polearm|ranged|brawling
    technique_type      VARCHAR(32)  NOT NULL,             -- setup|assault|reaction|aoe|concentration
    weapon_skill_id     INT          NOT NULL,             -- FK to skills.id
    min_skill_ranks     INT          NOT NULL DEFAULT 10,  -- ranks for rank 1
    rank2_ranks         INT          NOT NULL DEFAULT 35,
    rank3_ranks         INT          NOT NULL DEFAULT 60,
    rank4_ranks         INT          NOT NULL DEFAULT 85,
    rank5_ranks         INT          NOT NULL DEFAULT 110,
    stamina_cost        INT          NOT NULL DEFAULT 0,   -- 0 = reaction (free)
    base_roundtime      INT          NOT NULL DEFAULT 2,   -- seconds
    cooldown_seconds    INT          NOT NULL DEFAULT 0,   -- 0 = none
    description         TEXT,
    mechanics_notes     TEXT,
    available_to        VARCHAR(255) NOT NULL DEFAULT 'warrior,rogue,ranger,bard,monk,paladin',
    reaction_trigger    VARCHAR(64)  NULL,                 -- NULL if not reaction type
    -- e.g. 'recent_parry', 'recent_evade', 'recent_block', 'recent_evade_block_parry'
    offensive_gear      VARCHAR(64)  NOT NULL DEFAULT 'right_hand',
    flares_enabled      TINYINT(1)   NOT NULL DEFAULT 0,
    racial_size_mod     TINYINT(1)   NOT NULL DEFAULT 0,
    target_stance_bonus TINYINT(1)   NOT NULL DEFAULT 1,
    shield_def_bonus    TINYINT(1)   NOT NULL DEFAULT 1,
    created_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_wt_weapon_category (weapon_category),
    INDEX idx_wt_skill_id        (weapon_skill_id),
    INDEX idx_wt_type            (technique_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------------
-- character_weapon_techniques  (per-character learned state)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_weapon_techniques (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    character_id    INT         NOT NULL,
    technique_id    INT         NOT NULL,
    current_rank    TINYINT     NOT NULL DEFAULT 1,  -- 1-5
    learned_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at    TIMESTAMP   NULL,

    UNIQUE  KEY uq_char_technique (character_id, technique_id),
    INDEX   idx_cwt_character    (character_id),
    INDEX   idx_cwt_technique    (technique_id),
    FOREIGN KEY (technique_id) REFERENCES weapon_techniques(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------------
-- creature_weapon_techniques  (creatures that can use techniques)
-- Creature scripts reference mnemonic directly; this table drives auto-assignment
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS creature_weapon_techniques (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    creature_id     INT         NOT NULL,  -- FK to creatures.id
    technique_id    INT         NOT NULL,
    creature_rank   TINYINT     NOT NULL DEFAULT 1,
    use_chance_pct  TINYINT     NOT NULL DEFAULT 20, -- % chance per eligible round
    cooldown_rounds TINYINT     NOT NULL DEFAULT 3,  -- rounds between uses

    UNIQUE  KEY uq_creature_technique (creature_id, technique_id),
    INDEX   idx_creature_wt          (creature_id),
    FOREIGN KEY (technique_id) REFERENCES weapon_techniques(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------------
-- weapon_technique_reaction_log
-- Tracks ephemeral reaction-trigger state (recent_parry, recent_evade, etc.)
-- Rows are inserted on trigger event, deleted on consumption or expiry.
-- The Python session object also caches these in memory for speed;
-- this table is the durable fallback for reconnect / crash recovery.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weapon_technique_reaction_log (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity_id       INT         NOT NULL,  -- character_id or creature internal id
    entity_type     ENUM('player','creature') NOT NULL DEFAULT 'player',
    trigger_name    VARCHAR(64) NOT NULL,  -- 'recent_parry', 'recent_evade', 'recent_block'
    triggered_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP   NOT NULL,  -- typically triggered_at + 8 seconds

    INDEX idx_reaction_entity  (entity_id, entity_type),
    INDEX idx_reaction_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------------
-- Event: purge expired reaction log rows every 30 seconds
-- (Requires EVENT scheduler: SET GLOBAL event_scheduler = ON;)
-- ---------------------------------------------------------------------------
DROP EVENT IF EXISTS evt_purge_reaction_log;
CREATE EVENT evt_purge_reaction_log
    ON SCHEDULE EVERY 30 SECOND
    DO DELETE FROM weapon_technique_reaction_log WHERE expires_at < NOW();
