-- Remove stale trivial wounds that should already have fallen off once the
-- character returned to full health. Preserve bleeding and real higher-rank
-- injuries, and keep any scar data by zeroing wound_rank instead of deleting.

UPDATE character_wounds w
JOIN characters c ON c.id = w.character_id
SET w.wound_rank = 0,
    w.is_bleeding = 0,
    w.bandaged = 0
WHERE c.health_current >= c.health_max
  AND w.wound_rank <= 1
  AND w.is_bleeding = 0;

DELETE FROM character_wounds
WHERE wound_rank <= 0
  AND scar_rank <= 0;
