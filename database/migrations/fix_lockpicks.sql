-- ============================================================
-- Migration: Fix lockpick items to match GS4 wiki canonical list
-- gswiki.play.net/Lockpick
-- ============================================================
USE gemstone_dev;

-- ── 1. Rename "bronze lockpick" → "brass lockpick" everywhere ────────────────
-- "Bronze" is not a GS4 lockpick material. Brass is the correct beginner pick.

UPDATE items
SET name       = 'a brass lockpick',
    short_name = 'brass lockpick',
    material   = 'brass',
    value      = 250
WHERE short_name = 'bronze lockpick' OR (material = 'bronze' AND noun = 'lockpick');

-- ── 2. Remove non-GS4 fake picks (crude/simple/standard/professional/master's)─
-- These don't exist in real GS4 and have no material — causes fallback to copper.

DELETE FROM items
WHERE noun = 'lockpick'
  AND (material IS NULL OR material = '')
  AND short_name IN (
      'crude lockpick',
      'simple lockpick',
      'standard lockpick',
      'professional lockpick',
      'master''s lockpick'
  );

-- ── 3. Fix existing real picks — ensure correct prices, modifiers, item_type ──
-- item_type stays 'misc' (noun='lockpick' is what the code uses to detect picks)

UPDATE items SET value = 100,  material = 'copper'  WHERE short_name = 'copper lockpick'  AND noun = 'lockpick';
UPDATE items SET value = 250,  material = 'brass'   WHERE short_name = 'brass lockpick'   AND noun = 'lockpick';
UPDATE items SET value = 500,  material = 'steel'   WHERE short_name = 'steel lockpick'   AND noun = 'lockpick';
UPDATE items SET value = 2000, material = 'gold'    WHERE short_name = 'gold lockpick'    AND noun = 'lockpick';
UPDATE items SET value = 750,  material = 'ivory'   WHERE short_name = 'ivory lockpick'   AND noun = 'lockpick';
UPDATE items SET value = 2500, material = 'silver'  WHERE short_name = 'silver lockpick'  AND noun = 'lockpick';
UPDATE items SET value = 6000, material = 'mithril' WHERE short_name = 'mithril lockpick' AND noun = 'lockpick';
UPDATE items SET value = 5000, material = 'ora'     WHERE short_name = 'ora lockpick'     AND noun = 'lockpick';
UPDATE items SET value = 9500, material = 'glaes'   WHERE short_name = 'glaes lockpick'   AND noun = 'lockpick';
UPDATE items SET value = 17000,material = 'laje'    WHERE short_name = 'laje lockpick'    AND noun = 'lockpick';
UPDATE items SET value = 30000,material = 'vultite' WHERE short_name = 'vultite lockpick' AND noun = 'lockpick';
UPDATE items SET value = 17000,material = 'rolaren' WHERE short_name = 'rolaren lockpick' AND noun = 'lockpick';
UPDATE items SET value = 50000,material = 'veniom'  WHERE short_name = 'veniom lockpick'  AND noun = 'lockpick';
UPDATE items SET value = 75000,material = 'invar'   WHERE short_name = 'invar lockpick'   AND noun = 'lockpick';
UPDATE items SET value = 23000,material = 'alum'    WHERE short_name = 'alum lockpick'    AND noun = 'lockpick';
UPDATE items SET value = 62000,material = 'kelyn'   WHERE short_name = 'kelyn lockpick'   AND noun = 'lockpick';

-- ── 4. Add missing picks that weren't in the original seed ───────────────────
-- Checking which ones are actually missing before inserting

INSERT IGNORE INTO items
    (name, short_name, noun, base_name, article, item_type, material,
     weight, value, description, is_template)
VALUES
-- ivory: 1.20 modifier, 1 rank min, strength 5
('an ivory lockpick', 'ivory lockpick', 'lockpick', 'ivory lockpick',
 'an', 'misc', 'ivory', 1, 750,
 'A slender lockpick carved from ivory.  Its natural flexibility gives it a feel somewhere between steel and gold.',
 1),

-- silver: 1.30 modifier, 3 rank min, strength 4
('a silver lockpick', 'silver lockpick', 'lockpick', 'silver lockpick',
 'a', 'misc', 'silver', 1, 2500,
 'A bright silver lockpick, well-balanced but requiring a practiced touch to use effectively.',
 1),

-- gold: 1.20 modifier, 3 rank min, strength 3 (in case missing)
('a gold lockpick', 'gold lockpick', 'lockpick', 'gold lockpick',
 'a', 'misc', 'gold', 1, 2000,
 'A gleaming gold lockpick.  Softer than steel but surprisingly precise in skilled hands.',
 1),

-- golvern: 2.35 modifier, 40 rank min, strength 11 — hardest material in game
('a golvern lockpick', 'golvern lockpick', 'lockpick', 'golvern lockpick',
 'a', 'misc', 'golvern', 1, 95000,
 'An incredibly hard golvern lockpick of masterwork quality.  Only the most seasoned rogues can wield it effectively.',
 1),

-- vaalin: 2.50 modifier, 50 rank min, strength 10 — highest modifier in game
('a vaalin lockpick', 'vaalin lockpick', 'lockpick', 'vaalin lockpick',
 'a', 'misc', 'vaalin', 1, 125000,
 'A flawlessly crafted vaalin lockpick, the finest known to locksmithing.  Its modifier is unsurpassed.',
 1);

-- ── 5. Fix descriptions for existing picks (GS4-flavored) ────────────────────

UPDATE items SET description = 'A simple copper lockpick, the cheapest and most forgiving pick available.'
WHERE short_name = 'copper lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A brass lockpick, the standard choice for novice rogues.  Inexpensive and serviceable.'
WHERE short_name = 'brass lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A steel lockpick with better precision than copper or brass.  Requires some training to use well.'
WHERE short_name = 'steel lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A mithril lockpick of fine quality.  Requires a trained hand but holds up remarkably well.'
WHERE short_name = 'mithril lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A well-balanced ora lockpick favored by journeyman rogues.'
WHERE short_name = 'ora lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A glaes lockpick of good quality.  Its hardness allows exceptional durability.'
WHERE short_name = 'glaes lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A slender laje lockpick.  Exceptional precision but quite fragile — handle carefully.'
WHERE short_name = 'laje lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A vultite lockpick for experienced rogues.  Its precision is somewhat accurate but it lacks durability.'
WHERE short_name = 'vultite lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A rolaren lockpick, combining favorable precision with excellent durability.'
WHERE short_name = 'rolaren lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A veniom lockpick of highly accurate quality, favored by master rogues.'
WHERE short_name = 'veniom lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'An invar lockpick of masterwork quality.  Extremely accurate and nearly unbreakable.'
WHERE short_name = 'invar lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'An alum lockpick — excellent precision but very fragile.  For experts only.'
WHERE short_name = 'alum lockpick' AND noun = 'lockpick';

UPDATE items SET description = 'A kelyn lockpick of incredible precision, a prized tool among high-level rogues.'
WHERE short_name = 'kelyn lockpick' AND noun = 'lockpick';

-- ── Verify final state ────────────────────────────────────────────────────────
SELECT short_name, material, value, description
FROM items
WHERE noun = 'lockpick'
ORDER BY value;
