-- ============================================================
-- NPC SYSTEM SCHEMA
-- GemStone IV Private Server
--
-- DOS command to apply (root, no password):
--   mysql -u root gemstone4 < database/npc_schema.sql
-- ============================================================

-- ── npcs: master registry ────────────────────────────────────────────────────
-- One row per NPC template. The Lua file is the authoritative source for
-- behavior; this table is the index that lets the server find and manage it.
-- Room assignment lives here so it can be changed without editing Lua.
CREATE TABLE IF NOT EXISTS npcs (
    id           INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    template_id  VARCHAR(64)  NOT NULL UNIQUE,
    lua_script   VARCHAR(255) NOT NULL,          -- e.g. "npcs/town_guard.lua"
    home_room_id INT          NOT NULL DEFAULT 0,
    zone_slug    VARCHAR(64)  DEFAULT NULL,       -- informational only
    enabled      TINYINT(1)   NOT NULL DEFAULT 1,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_room   (home_room_id),
    INDEX idx_zone   (zone_slug),
    INDEX idx_enabled(enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── npc_state: persistent runtime state ──────────────────────────────────────
-- Survives server restarts. The manager reads this at boot and writes it on
-- any state change (death, room move). template_id is the join key.
CREATE TABLE IF NOT EXISTS npc_state (
    id              INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
    template_id     VARCHAR(64) NOT NULL UNIQUE,
    is_alive        TINYINT(1)  NOT NULL DEFAULT 1,
    current_room_id INT         NOT NULL DEFAULT 0,
    respawn_at      BIGINT      NOT NULL DEFAULT 0,  -- unix timestamp; 0 = not dead
    updated_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_alive     (is_alive),
    INDEX idx_respawn   (respawn_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── npc_shop_inventory: shop stock with restock timers ───────────────────────
-- quantity = -1 means unlimited (standard shops).
-- quantity >= 0 means finite stock; restock_at says when to refill.
CREATE TABLE IF NOT EXISTS npc_shop_inventory (
    id          INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
    template_id VARCHAR(64) NOT NULL,
    item_id     INT         NOT NULL,
    quantity    INT         NOT NULL DEFAULT -1,
    price       INT         NOT NULL DEFAULT 0,
    restock_at  BIGINT      NOT NULL DEFAULT 0,
    INDEX idx_template (template_id),
    INDEX idx_restock  (restock_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── npc_player_flags: per-player relationship/quest flags ────────────────────
-- Stores anything the NPC needs to remember about a specific player:
-- quest state, "met before", disposition, cooldowns, etc.
-- flag_value is a short string (use JSON for complex data).
CREATE TABLE IF NOT EXISTS npc_player_flags (
    id           INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    template_id  VARCHAR(64)  NOT NULL,
    character_id INT          NOT NULL,
    flag_name    VARCHAR(64)  NOT NULL,
    flag_value   VARCHAR(255) NOT NULL DEFAULT '',
    updated_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                              ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_flag (template_id, character_id, flag_name),
    INDEX idx_char  (character_id),
    INDEX idx_npc   (template_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── npc_guild_ranks: guild hierarchy ─────────────────────────────────────────
-- Each guild NPC can have a rank ladder. Players progress through ranks
-- by meeting xp / skill thresholds defined here.
CREATE TABLE IF NOT EXISTS npc_guild_ranks (
    id               INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    guild_id         VARCHAR(64)  NOT NULL,  -- matches NPC.guild_id in Lua
    rank_level       INT          NOT NULL DEFAULT 1,
    rank_name        VARCHAR(128) NOT NULL,
    rank_title       VARCHAR(128) NOT NULL DEFAULT '',
    min_xp_required  INT          NOT NULL DEFAULT 0,
    min_skill_ranks  INT          NOT NULL DEFAULT 0,
    unlock_abilities TEXT         DEFAULT NULL,  -- JSON array of ability strings
    UNIQUE KEY uq_rank   (guild_id, rank_level),
    INDEX idx_guild  (guild_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── npc_guild_membership: player guild standing ──────────────────────────────
CREATE TABLE IF NOT EXISTS npc_guild_membership (
    id           INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
    guild_id     VARCHAR(64) NOT NULL,
    character_id INT         NOT NULL,
    rank_level   INT         NOT NULL DEFAULT 1,
    guild_xp     INT         NOT NULL DEFAULT 0,
    joined_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
                             ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_membership (guild_id, character_id),
    INDEX idx_char  (character_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
