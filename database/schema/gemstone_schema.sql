-- =============================================================================
-- GemStone IV Private Server — Full Database Schema
-- MySQL / MariaDB  (utf8mb4)
--
-- Run with:
--   mysql -u root -p < database/schema/gemstone_schema.sql
-- =============================================================================

CREATE DATABASE IF NOT EXISTS gemstone_dev
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_uca1400_ai_ci;

USE gemstone_dev;

-- Drop all tables in reverse-dependency order so re-runs are always clean.
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS character_bank;
DROP TABLE IF EXISTS character_quests;
DROP TABLE IF EXISTS quest_definitions;
DROP TABLE IF EXISTS guild_ledger;
DROP TABLE IF EXISTS guild_master_registry;
DROP TABLE IF EXISTS character_guild_tasks;
DROP TABLE IF EXISTS guild_task_definitions;
DROP TABLE IF EXISTS character_guild_skills;
DROP TABLE IF EXISTS guild_skill_definitions;
DROP TABLE IF EXISTS character_guild_access;
DROP TABLE IF EXISTS guild_access_points;
DROP TABLE IF EXISTS character_guild_membership;
DROP TABLE IF EXISTS guild_rank_definitions;
DROP TABLE IF EXISTS guild_definitions;
DROP TABLE IF EXISTS character_spells_active;
DROP TABLE IF EXISTS character_skills;
DROP TABLE IF EXISTS character_inventory;
DROP TABLE IF EXISTS shop_inventory;
DROP TABLE IF EXISTS shops;
DROP TABLE IF EXISTS creature_treasure;
DROP TABLE IF EXISTS creature_templates;
DROP TABLE IF EXISTS experience_table;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS professions;
DROP TABLE IF EXISTS races;
DROP TABLE IF EXISTS towns;
DROP TABLE IF EXISTS characters;
DROP TABLE IF EXISTS accounts;
SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
-- ACCOUNTS
-- =============================================================================

CREATE TABLE accounts (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    username        VARCHAR(32)     NOT NULL,
    password_hash   VARCHAR(128)    NOT NULL,
    email           VARCHAR(128)    DEFAULT NULL,
    is_banned       TINYINT(1)      NOT NULL DEFAULT 0,
    is_admin        TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login      DATETIME        DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_accounts_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- CHARACTERS
-- =============================================================================

CREATE TABLE characters (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    account_id          INT UNSIGNED    NOT NULL,
    name                VARCHAR(32)     NOT NULL,
    race_id             TINYINT UNSIGNED NOT NULL DEFAULT 1,
    profession_id       TINYINT UNSIGNED NOT NULL DEFAULT 1,
    culture_key         VARCHAR(32)     DEFAULT NULL,
    gender              ENUM('male','female','other') NOT NULL DEFAULT 'male',

    -- Stats (base values stored, race mods applied at runtime)
    stat_strength       SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_constitution   SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_dexterity      SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_agility        SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_discipline     SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_aura           SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_logic          SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_intuition      SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_wisdom         SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    stat_influence      SMALLINT UNSIGNED NOT NULL DEFAULT 50,

    -- Vitals
    health_max          SMALLINT UNSIGNED NOT NULL DEFAULT 100,
    health_current      SMALLINT UNSIGNED NOT NULL DEFAULT 100,
    mana_max            SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    mana_current        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    spirit_max          TINYINT UNSIGNED  NOT NULL DEFAULT 10,
    spirit_current      TINYINT UNSIGNED  NOT NULL DEFAULT 10,
    stamina_max         SMALLINT UNSIGNED NOT NULL DEFAULT 100,
    stamina_current     SMALLINT UNSIGNED NOT NULL DEFAULT 100,

    -- Progression
    level               SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    experience          INT UNSIGNED      NOT NULL DEFAULT 0,
    field_experience    INT UNSIGNED      NOT NULL DEFAULT 0,
    physical_tp         SMALLINT UNSIGNED NOT NULL DEFAULT 25,
    mental_tp           SMALLINT UNSIGNED NOT NULL DEFAULT 25,

    -- Economy
    silver              INT UNSIGNED      NOT NULL DEFAULT 0,
    bank_silver         INT UNSIGNED      NOT NULL DEFAULT 0,

    -- Location
    current_room_id     INT UNSIGNED      NOT NULL DEFAULT 100,
    starting_room_id    INT UNSIGNED      DEFAULT NULL,
    position            VARCHAR(16)       NOT NULL DEFAULT 'standing',
    stance              VARCHAR(16)       NOT NULL DEFAULT 'neutral',

    -- Appearance
    height              TINYINT UNSIGNED  NOT NULL DEFAULT 68,
    hair_color          VARCHAR(32)       NOT NULL DEFAULT 'brown',
    hair_style          VARCHAR(32)       NOT NULL DEFAULT 'short',
    eye_color           VARCHAR(32)       NOT NULL DEFAULT 'brown',
    skin_tone           VARCHAR(32)       NOT NULL DEFAULT 'fair',
    age                 SMALLINT UNSIGNED DEFAULT NULL,
    age_descriptor      TINYINT UNSIGNED  DEFAULT NULL,
    birthday            VARCHAR(8)        DEFAULT NULL,

    -- Progression flags
    tutorial_stage      TINYINT UNSIGNED  NOT NULL DEFAULT 0,
    tutorial_complete   TINYINT(1)        NOT NULL DEFAULT 0,
    total_playtime      INT UNSIGNED      NOT NULL DEFAULT 0,
    last_login          DATETIME          DEFAULT NULL,
    created_at          DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_characters_name (name),
    KEY idx_characters_account (account_id),
    KEY idx_characters_room (current_room_id),
    CONSTRAINT fk_characters_account FOREIGN KEY (account_id)
        REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- CHARACTER SKILLS
-- =============================================================================

CREATE TABLE character_skills (
    character_id        INT UNSIGNED    NOT NULL,
    skill_id            TINYINT UNSIGNED NOT NULL,
    ranks               SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    bonus               SMALLINT         NOT NULL DEFAULT 0,
    ranks_this_level    TINYINT UNSIGNED  NOT NULL DEFAULT 0,
    PRIMARY KEY (character_id, skill_id),
    CONSTRAINT fk_charskills_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- CHARACTER ACTIVE SPELLS
-- =============================================================================

CREATE TABLE character_spells_active (
    character_id        INT UNSIGNED    NOT NULL,
    spell_id            SMALLINT UNSIGNED NOT NULL,
    duration_remaining  INT             NOT NULL DEFAULT 0,
    PRIMARY KEY (character_id, spell_id),
    CONSTRAINT fk_charspells_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- GUILDS
-- =============================================================================

CREATE TABLE guild_definitions (
    guild_id             VARCHAR(32)      NOT NULL,
    profession_id        TINYINT UNSIGNED NOT NULL,
    name                 VARCHAR(64)      NOT NULL,
    support_level        ENUM('complete','incomplete','social') NOT NULL DEFAULT 'social',
    initiation_fee       INT UNSIGNED     NOT NULL DEFAULT 0,
    monthly_dues         INT UNSIGNED     NOT NULL DEFAULT 0,
    join_level           SMALLINT UNSIGNED NOT NULL DEFAULT 15,
    max_prepay_months    TINYINT UNSIGNED NOT NULL DEFAULT 3,
    has_skill_training   TINYINT(1)       NOT NULL DEFAULT 0,
    has_guildmaster      TINYINT(1)       NOT NULL DEFAULT 0,
    progression_multiplier DECIMAL(8,2)   NOT NULL DEFAULT 20.00,
    description          TEXT             DEFAULT NULL,
    oath_text            TEXT             DEFAULT NULL,
    is_active            TINYINT(1)       NOT NULL DEFAULT 1,
    PRIMARY KEY (guild_id),
    UNIQUE KEY uq_guild_profession (profession_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE guild_rank_definitions (
    guild_id             VARCHAR(32)       NOT NULL,
    rank_level           SMALLINT UNSIGNED NOT NULL,
    rank_name            VARCHAR(64)       NOT NULL,
    description          TEXT              DEFAULT NULL,
    min_total_skill_ranks SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    min_distinct_skills  TINYINT UNSIGNED  NOT NULL DEFAULT 0,
    PRIMARY KEY (guild_id, rank_level),
    CONSTRAINT fk_guildranks_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE character_guild_membership (
    id                   INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    character_id         INT UNSIGNED      NOT NULL,
    guild_id             VARCHAR(32)       NOT NULL,
    status               ENUM('active','resigned','suspended') NOT NULL DEFAULT 'active',
    rank_level           SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    rank_visible         TINYINT(1)        NOT NULL DEFAULT 1,
    is_guildmaster       TINYINT(1)        NOT NULL DEFAULT 0,
    vouchers             INT UNSIGNED      NOT NULL DEFAULT 0,
    guild_training_points INT UNSIGNED     NOT NULL DEFAULT 0,
    active_skill_name    VARCHAR(64)       DEFAULT NULL,
    joined_at            DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dues_paid_through    DATETIME          DEFAULT NULL,
    last_checkin_at      DATETIME          DEFAULT NULL,
    next_checkin_due_at  DATETIME          DEFAULT NULL,
    last_task_at         DATETIME          DEFAULT NULL,
    resigned_at          DATETIME          DEFAULT NULL,
    notes                JSON              DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_character_guild (character_id, guild_id),
    KEY idx_guildmember_char (character_id),
    KEY idx_guildmember_guild (guild_id),
    CONSTRAINT fk_guildmember_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildmember_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE guild_access_points (
    id                   INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    guild_id             VARCHAR(32)       NOT NULL,
    city_name            VARCHAR(64)       DEFAULT NULL,
    entry_room_id        INT UNSIGNED      NOT NULL,
    target_room_id       INT UNSIGNED      NOT NULL,
    access_keyword       VARCHAR(32)       NOT NULL DEFAULT 'door',
    primer_verb          VARCHAR(16)       NOT NULL DEFAULT 'lean',
    pass_sequence        VARCHAR(255)      DEFAULT NULL,
    exit_keyword         VARCHAR(32)       NOT NULL DEFAULT 'out',
    notes                TEXT              DEFAULT NULL,
    is_active            TINYINT(1)        NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_guild_access_roompair (guild_id, entry_room_id, target_room_id),
    KEY idx_guild_access_entry (entry_room_id),
    KEY idx_guild_access_target (target_room_id),
    CONSTRAINT fk_guildaccess_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE character_guild_access (
    character_id         INT UNSIGNED      NOT NULL,
    guild_id             VARCHAR(32)       NOT NULL,
    is_invited           TINYINT(1)        NOT NULL DEFAULT 0,
    password_known       TINYINT(1)        NOT NULL DEFAULT 0,
    invited_at           DATETIME          DEFAULT NULL,
    invited_by_template_id VARCHAR(64)     DEFAULT NULL,
    invited_by_character_id INT UNSIGNED   DEFAULT NULL,
    password_shared_at   DATETIME          DEFAULT NULL,
    sequence_step        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    sequence_room_id     INT UNSIGNED      DEFAULT NULL,
    sequence_started_at  DATETIME          DEFAULT NULL,
    updated_at           DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id, guild_id),
    CONSTRAINT fk_guildaccesschar_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildaccesschar_inviter FOREIGN KEY (invited_by_character_id)
        REFERENCES characters(id) ON DELETE SET NULL,
    CONSTRAINT fk_guildaccesschar_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE character_guild_skills (
    character_id         INT UNSIGNED      NOT NULL,
    guild_id             VARCHAR(32)       NOT NULL,
    skill_name           VARCHAR(64)       NOT NULL,
    ranks                SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    training_points      INT UNSIGNED      NOT NULL DEFAULT 0,
    is_mastered          TINYINT(1)        NOT NULL DEFAULT 0,
    last_trained_at      DATETIME          DEFAULT NULL,
    PRIMARY KEY (character_id, guild_id, skill_name),
    CONSTRAINT fk_guildskills_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildskills_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE guild_skill_definitions (
    guild_id             VARCHAR(32)       NOT NULL,
    skill_name           VARCHAR(64)       NOT NULL,
    display_name         VARCHAR(64)       NOT NULL,
    skill_order          SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    max_rank             SMALLINT UNSIGNED NOT NULL DEFAULT 63,
    points_per_rank      INT UNSIGNED      NOT NULL DEFAULT 100,
    practice_only        TINYINT(1)        NOT NULL DEFAULT 0,
    is_active            TINYINT(1)        NOT NULL DEFAULT 1,
    PRIMARY KEY (guild_id, skill_name),
    KEY idx_guildskillsdefs_order (guild_id, skill_order),
    CONSTRAINT fk_guildskilldefs_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE character_guild_tasks (
    id                    INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    character_id          INT UNSIGNED      NOT NULL,
    guild_id              VARCHAR(32)       NOT NULL,
    skill_name            VARCHAR(64)       DEFAULT NULL,
    task_code             VARCHAR(64)       DEFAULT NULL,
    task_type             VARCHAR(64)       DEFAULT NULL,
    task_text             TEXT              DEFAULT NULL,
    objective_event       VARCHAR(64)       DEFAULT NULL,
    target_count          SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    progress_count        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    award_points          INT UNSIGNED      NOT NULL DEFAULT 0,
    repetitions_remaining SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    task_data             JSON              DEFAULT NULL,
    status                ENUM('assigned','ready','complete','abandoned') NOT NULL DEFAULT 'assigned',
    assigned_at           DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at          DATETIME          DEFAULT NULL,
    PRIMARY KEY (id),
    KEY idx_guildtasks_char (character_id),
    KEY idx_guildtasks_guild (guild_id),
    CONSTRAINT fk_guildtasks_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildtasks_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE guild_task_definitions (
    id                   INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    guild_id             VARCHAR(32)       NOT NULL,
    skill_name           VARCHAR(64)       NOT NULL,
    task_code            VARCHAR(64)       NOT NULL,
    title                VARCHAR(64)       NOT NULL,
    description          TEXT              DEFAULT NULL,
    objective_event      VARCHAR(64)       NOT NULL,
    required_count       SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    base_points          INT UNSIGNED      NOT NULL DEFAULT 1,
    min_rank             SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    max_rank             SMALLINT UNSIGNED DEFAULT NULL,
    practice_room_id     INT UNSIGNED      DEFAULT NULL,
    requires_guild_authority TINYINT(1)    NOT NULL DEFAULT 0,
    is_active            TINYINT(1)        NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_guild_task_code (guild_id, task_code),
    KEY idx_guildtaskdefs_skill (guild_id, skill_name, min_rank),
    CONSTRAINT fk_guildtaskdefs_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE guild_guildmaster_nominations (
    guild_id               VARCHAR(32)      NOT NULL,
    nominee_character_id   INT UNSIGNED     NOT NULL,
    nominator_character_id INT UNSIGNED     NOT NULL,
    status                 ENUM('active','used','revoked') NOT NULL DEFAULT 'active',
    notes                  TEXT             DEFAULT NULL,
    nominated_at           DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at                DATETIME         DEFAULT NULL,
    PRIMARY KEY (guild_id, nominee_character_id, nominator_character_id),
    KEY idx_guildnom_nominee (nominee_character_id),
    KEY idx_guildnom_nominator (nominator_character_id),
    CONSTRAINT fk_guildnom_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE,
    CONSTRAINT fk_guildnom_nominee FOREIGN KEY (nominee_character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildnom_nominator FOREIGN KEY (nominator_character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE guild_master_registry (
    id                   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    guild_id             VARCHAR(32)      NOT NULL,
    npc_template_id      VARCHAR(64)      NOT NULL,
    role_type            ENUM('master','administrator','contact','trainer') NOT NULL DEFAULT 'contact',
    room_id              INT UNSIGNED     NOT NULL DEFAULT 0,
    lich_room_id         INT UNSIGNED     DEFAULT NULL,
    city_name            VARCHAR(64)      DEFAULT NULL,
    is_active            TINYINT(1)       NOT NULL DEFAULT 1,
    notes                TEXT             DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_guildmaster_template (guild_id, npc_template_id, room_id),
    KEY idx_guildmaster_room (room_id),
    CONSTRAINT fk_guildmaster_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE guild_ledger (
    id                   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    character_id         INT UNSIGNED     NOT NULL,
    guild_id             VARCHAR(32)      NOT NULL,
    entry_type           ENUM('join','invite','initiate','dues','checkin','resign','promotion','task','voucher','nominate','guildmaster','quest') NOT NULL,
    amount               INT              NOT NULL DEFAULT 0,
    months_paid          TINYINT UNSIGNED NOT NULL DEFAULT 0,
    actor_template_id    VARCHAR(64)      DEFAULT NULL,
    notes                TEXT             DEFAULT NULL,
    created_at           DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_guildledger_char (character_id),
    KEY idx_guildledger_guild (guild_id),
    CONSTRAINT fk_guildledger_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildledger_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- REFERENCE: RACES
-- =============================================================================

CREATE TABLE races (
    id          TINYINT UNSIGNED NOT NULL,
    name        VARCHAR(32)      NOT NULL,
    description TEXT             DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_races_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- REFERENCE: PROFESSIONS
-- =============================================================================

CREATE TABLE professions (
    id              TINYINT UNSIGNED NOT NULL,
    name            VARCHAR(32)      NOT NULL,
    profession_type ENUM('square','semi','pure') NOT NULL DEFAULT 'square',
    description     TEXT             DEFAULT NULL,
    hp_per_level    TINYINT UNSIGNED NOT NULL DEFAULT 10,
    mana_per_level  TINYINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uq_professions_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- REFERENCE: SKILLS
-- =============================================================================

CREATE TABLE skills (
    id          TINYINT UNSIGNED NOT NULL,
    name        VARCHAR(64)      NOT NULL,
    category    VARCHAR(32)      NOT NULL DEFAULT 'General',
    PRIMARY KEY (id),
    UNIQUE KEY uq_skills_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- ITEMS
-- =============================================================================

CREATE TABLE items (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    name                VARCHAR(128)    NOT NULL,
    short_name          VARCHAR(128)    DEFAULT NULL,
    noun                VARCHAR(32)     DEFAULT NULL,
    article             VARCHAR(8)      NOT NULL DEFAULT 'a',
    item_type           VARCHAR(32)     NOT NULL DEFAULT 'misc',
    is_template         TINYINT(1)      NOT NULL DEFAULT 1,
    is_stackable        TINYINT(1)      NOT NULL DEFAULT 0,
    weight              FLOAT           NOT NULL DEFAULT 1.0,
    value               INT UNSIGNED    NOT NULL DEFAULT 0,

    -- Combat / weapon
    weapon_type         VARCHAR(16)     DEFAULT NULL,
    damage_factor       FLOAT           DEFAULT NULL,
    weapon_speed        TINYINT UNSIGNED DEFAULT NULL,
    damage_type         VARCHAR(32)     DEFAULT NULL,
    attack_bonus        SMALLINT        NOT NULL DEFAULT 0,
    damage_bonus        SMALLINT        NOT NULL DEFAULT 0,
    enchant_bonus       SMALLINT        NOT NULL DEFAULT 0,

    -- Armor
    armor_group         VARCHAR(16)     DEFAULT NULL,
    armor_asg           TINYINT UNSIGNED DEFAULT NULL,
    defense_bonus       SMALLINT        NOT NULL DEFAULT 0,
    action_penalty      SMALLINT        NOT NULL DEFAULT 0,
    spell_hindrance     TINYINT UNSIGNED DEFAULT 0,

    -- Shield
    shield_type         VARCHAR(16)     DEFAULT NULL,
    shield_ds           TINYINT UNSIGNED DEFAULT NULL,
    shield_evade_penalty TINYINT UNSIGNED DEFAULT NULL,
    shield_size_mod     SMALLINT        DEFAULT NULL,

    -- Container
    container_capacity  SMALLINT UNSIGNED DEFAULT NULL,
    container_type      VARCHAR(16)     DEFAULT NULL,
    lock_difficulty     SMALLINT UNSIGNED DEFAULT 0,
    trap_type           VARCHAR(16)     DEFAULT NULL,

    -- Worn
    worn_location       VARCHAR(32)     DEFAULT NULL,

    -- Herb
    heal_type           VARCHAR(16)     DEFAULT NULL,
    heal_rank           TINYINT UNSIGNED DEFAULT NULL,
    heal_amount         SMALLINT UNSIGNED DEFAULT 0,
    herb_roundtime      TINYINT UNSIGNED DEFAULT NULL,

    -- Gem
    gem_family          VARCHAR(32)     DEFAULT NULL,
    gem_region          VARCHAR(32)     DEFAULT NULL,

    -- Lockpick
    lockpick_material   VARCHAR(32)     DEFAULT NULL,

    -- Material
    material            VARCHAR(32)     DEFAULT 'steel',

    -- Text
    description         TEXT            DEFAULT NULL,
    examine_text        TEXT            DEFAULT NULL,
    lore_text           TEXT            DEFAULT NULL,

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_items_name (name(64)),
    KEY idx_items_type (item_type),
    KEY idx_items_template (is_template)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- CHARACTER INVENTORY
-- =============================================================================

CREATE TABLE character_inventory (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    character_id    INT UNSIGNED    NOT NULL,
    item_id         INT UNSIGNED    NOT NULL,
    container_id    INT UNSIGNED    DEFAULT NULL,  -- inv row id of the container holding this
    slot            VARCHAR(32)     DEFAULT NULL,   -- worn slot: back, belt, torso, etc.
    quantity        SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    extra_data      JSON            DEFAULT NULL,   -- per-instance state (pick modifier, charges…)
    PRIMARY KEY (id),
    KEY idx_inv_char (character_id),
    KEY idx_inv_item (item_id),
    CONSTRAINT fk_inv_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_inv_item FOREIGN KEY (item_id)
        REFERENCES items(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- SHOPS
-- =============================================================================

CREATE TABLE shops (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    name            VARCHAR(128)    NOT NULL,
    room_id         INT UNSIGNED    NOT NULL,
    shop_type       VARCHAR(32)     NOT NULL DEFAULT 'general',
    buy_multiplier  FLOAT           NOT NULL DEFAULT 1.0,   -- multiply item value for purchase price
    sell_multiplier FLOAT           NOT NULL DEFAULT 0.5,   -- multiply item value for sell price
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    KEY idx_shops_room (room_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE shop_inventory (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    shop_id         INT UNSIGNED    NOT NULL,
    item_id         INT UNSIGNED    NOT NULL,
    stock           SMALLINT        NOT NULL DEFAULT -1,   -- -1 = infinite
    restock_amount  SMALLINT UNSIGNED NOT NULL DEFAULT 5,
    restock_interval INT UNSIGNED   NOT NULL DEFAULT 3600, -- seconds
    last_restock    DATETIME        DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_shopinv (shop_id, item_id),
    CONSTRAINT fk_shopinv_shop FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE,
    CONSTRAINT fk_shopinv_item FOREIGN KEY (item_id) REFERENCES items(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- EXPERIENCE / LEVEL TABLE
-- =============================================================================

CREATE TABLE experience_table (
    level           SMALLINT UNSIGNED NOT NULL,
    exp_required    INT UNSIGNED      NOT NULL,
    PRIMARY KEY (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- CREATURE TEMPLATES
-- =============================================================================

CREATE TABLE creature_templates (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    name            VARCHAR(64)     NOT NULL,
    display_name    VARCHAR(128)    DEFAULT NULL,
    level           TINYINT UNSIGNED NOT NULL DEFAULT 1,
    health_base     SMALLINT UNSIGNED NOT NULL DEFAULT 50,
    attack_strength SMALLINT        NOT NULL DEFAULT 100,
    defense_strength SMALLINT       NOT NULL DEFAULT 100,
    creature_type   VARCHAR(32)     NOT NULL DEFAULT 'humanoid',
    is_undead       TINYINT(1)      NOT NULL DEFAULT 0,
    is_magical      TINYINT(1)      NOT NULL DEFAULT 0,
    lua_script      VARCHAR(128)    DEFAULT NULL,  -- path to zone/mobs/x.lua
    PRIMARY KEY (id),
    KEY idx_creat_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- CREATURE TREASURE TABLES
-- =============================================================================

CREATE TABLE creature_treasure (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    creature_id     INT UNSIGNED    NOT NULL,
    item_id         INT UNSIGNED    DEFAULT NULL,
    silver_min      INT UNSIGNED    NOT NULL DEFAULT 0,
    silver_max      INT UNSIGNED    NOT NULL DEFAULT 0,
    drop_chance     FLOAT           NOT NULL DEFAULT 1.0,  -- 0.0-1.0
    PRIMARY KEY (id),
    KEY idx_ctreasure_creature (creature_id),
    CONSTRAINT fk_ctreasure_creature FOREIGN KEY (creature_id)
        REFERENCES creature_templates(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- QUESTS
-- =============================================================================

CREATE TABLE quest_definitions (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    key_name        VARCHAR(64)     NOT NULL,
    title           VARCHAR(128)    NOT NULL,
    description     TEXT            DEFAULT NULL,
    min_level       TINYINT UNSIGNED NOT NULL DEFAULT 1,
    max_level       TINYINT UNSIGNED NOT NULL DEFAULT 100,
    is_repeatable   TINYINT(1)      NOT NULL DEFAULT 0,
    lua_script      VARCHAR(128)    DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_quests_key (key_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE character_quests (
    character_id    INT UNSIGNED    NOT NULL,
    quest_id        INT UNSIGNED    NOT NULL,
    status          ENUM('available','active','complete','failed') NOT NULL DEFAULT 'available',
    stage           TINYINT UNSIGNED NOT NULL DEFAULT 0,
    progress_count  SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    target_count    SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    quest_data      JSON            DEFAULT NULL,
    started_at      DATETIME        DEFAULT NULL,
    completed_at    DATETIME        DEFAULT NULL,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id, quest_id),
    CONSTRAINT fk_cquests_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_cquests_quest FOREIGN KEY (quest_id)
        REFERENCES quest_definitions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- =============================================================================
-- TOWNS / BANKS
-- =============================================================================

CREATE TABLE towns (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    name            VARCHAR(64)     NOT NULL,
    bank_room_id    INT UNSIGNED    DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_towns_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE character_bank (
    character_id    INT UNSIGNED    NOT NULL,
    town_id         INT UNSIGNED    NOT NULL,
    silver          INT UNSIGNED    NOT NULL DEFAULT 0,
    PRIMARY KEY (character_id, town_id),
    CONSTRAINT fk_bank_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
