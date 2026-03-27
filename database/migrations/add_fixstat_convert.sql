-- ============================================================
-- Migration: add_fixstat_convert.sql
-- Adds fixstat use tracking + starting stat snapshot to characters.
-- Run as root:
--   mysql -u root gemstone_dev < database/migrations/add_fixstat_convert.sql
-- ============================================================

USE gemstone_dev;

-- ── Stat reallocation tracking ───────────────────────────────────────────────
-- fixstat_uses_remaining: 10 free uses before level 20 (single-player rule)
-- fixstat_uses_total:     total lifetime uses (for logging / future reference)
-- fixstat_last_free:      timestamp of last free post-20 use (1 per 24 hrs)
ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS fixstat_uses_remaining  TINYINT UNSIGNED  NOT NULL DEFAULT 10,
    ADD COLUMN IF NOT EXISTS fixstat_uses_total      SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS fixstat_last_free       DATETIME          DEFAULT NULL;

-- ── Stat baseline snapshot (recorded once at character creation) ──────────────
-- Used to re-validate that a player can't exceed their race/profession caps
-- when reallocating. Stored so we never lose the original allocation budget.
ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS base_stat_strength       TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_constitution   TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_dexterity      TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_agility        TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_discipline     TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_aura           TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_logic          TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_intuition      TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_wisdom         TINYINT UNSIGNED DEFAULT 50,
    ADD COLUMN IF NOT EXISTS base_stat_influence      TINYINT UNSIGNED DEFAULT 50;

-- Backfill base stats from current stats for existing characters
-- (they haven't changed their stats yet, so current == base for them)
UPDATE characters SET
    base_stat_strength     = stat_strength,
    base_stat_constitution = stat_constitution,
    base_stat_dexterity    = stat_dexterity,
    base_stat_agility      = stat_agility,
    base_stat_discipline   = stat_discipline,
    base_stat_aura         = stat_aura,
    base_stat_logic        = stat_logic,
    base_stat_intuition    = stat_intuition,
    base_stat_wisdom       = stat_wisdom,
    base_stat_influence    = stat_influence
WHERE base_stat_strength = 50
  AND base_stat_constitution = 50
  AND base_stat_dexterity = 50
  AND base_stat_agility = 50;

SELECT 'Migration add_fixstat_convert.sql complete.' AS status;
