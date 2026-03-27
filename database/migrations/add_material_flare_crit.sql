-- =============================================================================
-- database/migrations/add_material_flare_crit.sql
--
-- Material flare and crit system migration.
--
-- What this does:
--   1. Backfills flare_type on existing items whose material field is set to a
--      known flare material (rhimar, drakar, zorchar, gornar).
--      The flare_type column already exists (added in add_material_customization.sql).
--
--   2. Adds flare_type to character_inventory overrides so per-character
--      flare type can be overridden if desired (future merchant/alteration use).
--
--   3. Documents that crit_weight (razern CEP) lives entirely in materials.lua —
--      no DB column needed.  The Lua engine drives it at runtime.
--
-- NOTE: weight_modifier also lives entirely in materials.lua.
--       No DB column needed.  encumbrance.py reads it via material_combat.py.
--
-- Run with:
--   mysql -u root gemstone_dev < database/migrations/add_material_flare_crit.sql
-- =============================================================================

USE gemstone_dev;

-- ── Step 1: Backfill flare_type on base items table ───────────────────────────
--
-- Items seeded or created before this migration with a flare material will have
-- NULL flare_type.  This sets them from the material field.
-- Items that already have flare_type set are left untouched (WHERE clause).

UPDATE items
SET flare_type = CASE material
    WHEN 'rhimar'  THEN 'cold'
    WHEN 'drakar'  THEN 'fire'
    WHEN 'zorchar' THEN 'lightning'
    WHEN 'gornar'  THEN 'vibration'
END
WHERE material IN ('rhimar', 'drakar', 'zorchar', 'gornar')
  AND (flare_type IS NULL OR flare_type = '');

-- ── Step 2: Add flare_type override to character_inventory (if missing) ───────
--
-- Allows per-character flare type (e.g. merchant adds fire flares to a sword)
-- without changing the base item template.

ALTER TABLE character_inventory
    ADD COLUMN IF NOT EXISTS flare_type_override VARCHAR(32) DEFAULT NULL
    AFTER defense_bonus_override;

-- ── Step 3: Verify ────────────────────────────────────────────────────────────

SELECT
    material,
    flare_type,
    COUNT(*) AS item_count
FROM items
WHERE material IN ('rhimar', 'drakar', 'zorchar', 'gornar')
GROUP BY material, flare_type
ORDER BY material;

SELECT 'Migration add_material_flare_crit complete.' AS status;
