-- Normalize persisted wound locations and remove impossible bleed-only rows.

UPDATE character_wounds
SET location = REPLACE(LOWER(TRIM(location)), ' ', '_');

UPDATE character_wounds
SET is_bleeding = 0,
    bandaged = 0
WHERE wound_rank <= 0;

DELETE FROM character_wounds
WHERE wound_rank <= 0
  AND scar_rank <= 0;
