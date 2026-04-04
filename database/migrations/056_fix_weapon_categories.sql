-- Backfill missing weapon_category values from weapon_type so combat skill
-- lookups stop silently falling back to edged for malformed weapon rows.

UPDATE items
SET weapon_category = weapon_type
WHERE item_type = 'weapon'
  AND (weapon_category IS NULL OR TRIM(weapon_category) = '')
  AND weapon_type IN ('edged', 'blunt', 'twohanded', 'polearm', 'ranged', 'thrown', 'brawling');
