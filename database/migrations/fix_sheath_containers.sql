-- =============================================================
-- fix_sheath_containers.sql
-- Migration: make sheaths and scabbards proper weapon containers.
--
-- What this does:
--   1. Adds sheath_type and worn_location_slot columns to items if missing.
--   2. Sets item_type = 'container', container_capacity = 1 for all sheath/
--      scabbard items (both template and any existing instances).
--   3. Tags each row with the correct sheath_type so sheath.lua can gate
--      which weapon nouns are accepted.
--   4. Sets worn_location to 'hip' (default) — adjust per item as needed.
-- =============================================================
USE gemstone_dev;

-- ── 1. Add sheath_type column if missing ─────────────────────────────────────
ALTER TABLE items
    ADD COLUMN IF NOT EXISTS sheath_type VARCHAR(32) DEFAULT NULL
        COMMENT 'dagger_sheath | small_scabbard | scabbard | large_scabbard | axe_sheath'
        AFTER container_capacity;

-- ── 2. Fix item_type and capacity for ALL sheath/scabbard nouns ──────────────
-- Dagger sheaths
UPDATE items
SET    item_type         = 'container',
       container_capacity = 1,
       sheath_type       = 'dagger_sheath',
       worn_location     = 'hip'
WHERE  noun IN ('dagger sheath','sheath')
  AND  name LIKE '%dagger%';

-- Generic small sheaths / dirk sheaths
UPDATE items
SET    item_type         = 'container',
       container_capacity = 1,
       sheath_type       = 'dagger_sheath',
       worn_location     = 'hip'
WHERE  noun IN ('sheath','scabbard')
  AND  (name LIKE '%knife%' OR name LIKE '%dirk%' OR name LIKE '%stiletto%');

-- Small scabbards (short swords, backswords)
UPDATE items
SET    item_type         = 'container',
       container_capacity = 1,
       sheath_type       = 'small_scabbard',
       worn_location     = 'hip'
WHERE  noun = 'scabbard'
  AND  (name LIKE '%short%' OR name LIKE '%back%' OR name LIKE '%small%');

-- Standard scabbards (longswords, broadswords, rapiers, falchions, scimitars)
-- This also catches a plain "leather scabbard" or "a scabbard"
UPDATE items
SET    item_type         = 'container',
       container_capacity = 1,
       sheath_type       = 'scabbard',
       worn_location     = 'hip'
WHERE  noun = 'scabbard'
  AND  sheath_type IS NULL;   -- catch-all for any scabbard not tagged above

-- Large scabbards (two-handed swords, claidhmores)
UPDATE items
SET    item_type         = 'container',
       container_capacity = 1,
       sheath_type       = 'large_scabbard',
       worn_location     = 'back'
WHERE  noun = 'scabbard'
  AND  (name LIKE '%great%' OR name LIKE '%large%' OR name LIKE '%claidh%' OR name LIKE '%two-hand%');

-- Axe sheaths
UPDATE items
SET    item_type         = 'container',
       container_capacity = 1,
       sheath_type       = 'axe_sheath',
       worn_location     = 'hip'
WHERE  noun IN ('sheath','axe sheath')
  AND  (name LIKE '%axe%' OR name LIKE '%hatchet%' OR name LIKE '%tomahawk%');

-- ── 3. Safety: any remaining rows named *sheath* or *scabbard* that slipped
--    through (paranoid catch-all – sets container but leaves sheath_type NULL
--    so sheath.lua will emit "unknown sheath type" gracefully)
UPDATE items
SET    item_type         = 'container',
       container_capacity = 1,
       worn_location     = COALESCE(worn_location, 'hip')
WHERE  item_type != 'container'
  AND  (noun LIKE '%sheath%' OR noun LIKE '%scabbard%'
        OR name LIKE '%sheath%' OR name LIKE '%scabbard%');

-- ── 4. Verify ─────────────────────────────────────────────────────────────────
SELECT
    id,
    name,
    noun,
    item_type,
    container_capacity,
    sheath_type,
    worn_location
FROM items
WHERE noun LIKE '%sheath%'
   OR noun LIKE '%scabbard%'
   OR name LIKE '%sheath%'
   OR name LIKE '%scabbard%'
ORDER BY sheath_type, name;

SELECT 'fix_sheath_containers migration complete.' AS status;
