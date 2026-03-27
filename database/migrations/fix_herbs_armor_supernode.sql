-- ============================================================
-- fix_herbs_armor_supernode.sql
-- Run with:
--   mysql -u root gemstone_dev < database/migrations/fix_herbs_armor_supernode.sql
--
-- Fixes:
--   1. Herb canonical columns (heal_type/heal_amount/heal_rank)
--      mapped from legacy herb_heal_type/herb_heal_amount seed data
--   2. Correct herb names, articles, and heal amounts per GS4 wiki
--   3. Adds leather gorget / leather gloves / leather boots as
--      actual ARMOR items (item_type='armor') for neck/hands/feet
--   4. Stocks those items in Ta'Vaalor shops 2 and 3
--   5. Sets room 3542 (Ta'Vaalor, Victory Court) as a supernode
-- ============================================================

USE gemstone_dev;

-- ============================================================
-- SECTION 1: Fix herb names, articles, and canonical columns
-- Authoritative source: gswiki.play.net/Herb
-- ============================================================

-- Blood/Concussion herbs (restore HP)
UPDATE items SET
    name='some acantha leaf', short_name='acantha leaf', article='some',
    heal_type='blood', heal_rank=1, heal_amount=10, herb_roundtime=5
WHERE base_name='acantha leaf' OR name LIKE '%acantha leaf%' AND item_type='herb';

UPDATE items SET
    name='some cothinar flower', short_name='cothinar flower', article='some',
    heal_type='blood', heal_rank=1, heal_amount=15, herb_roundtime=5
WHERE (base_name='cothinar flower' OR name LIKE '%cothinar%') AND item_type='herb';

UPDATE items SET
    name='some marallis berry', short_name='marallis berry', article='some',
    heal_type='blood', heal_rank=1, heal_amount=10, herb_roundtime=5
WHERE (base_name='marallis berry' OR name LIKE '%marallis%') AND item_type='herb';

UPDATE items SET
    name='some cuctucae berry', short_name='cuctucae berry', article='some',
    heal_type='blood', heal_rank=1, heal_amount=5, herb_roundtime=5
WHERE (base_name='cuctucae berry' OR name LIKE '%cuctucae%') AND item_type='herb';

UPDATE items SET
    name='some yabathilium fruit', short_name='yabathilium fruit', article='some',
    heal_type='blood', heal_rank=2, heal_amount=50, herb_roundtime=0
WHERE (base_name='yabathilium fruit' OR name LIKE '%yabathilium%') AND item_type='herb';

UPDATE items SET
    name='some wekaf berries', short_name='wekaf berries', article='some',
    heal_type='blood', heal_rank=1, heal_amount=5, herb_roundtime=5
WHERE (base_name='wekaf berries' OR name LIKE '%wekaf%') AND item_type='herb';

-- Nervous system herbs
UPDATE items SET
    name='some wolifrew lichen', short_name='wolifrew lichen', article='some',
    heal_type='nerves', heal_rank=1, heal_amount=0, herb_roundtime=15
WHERE (base_name='wolifrew lichen' OR name LIKE '%wolifrew%') AND item_type='herb';

UPDATE items SET
    name='a bolmara potion', short_name='bolmara potion', article='a',
    heal_type='nerves', heal_rank=2, heal_amount=0, herb_roundtime=25
WHERE (base_name='bolmara potion' OR name LIKE '%bolmara%') AND item_type='herb';

UPDATE items SET
    name='some torban leaf', short_name='torban leaf', article='some',
    heal_type='nerves', heal_rank=3, heal_amount=0, herb_roundtime=15
WHERE (base_name='torban leaf' OR name LIKE '%torban%') AND item_type='herb';

UPDATE items SET
    name='some woth flower', short_name='woth flower', article='some',
    heal_type='nerves', heal_rank=4, heal_amount=0, herb_roundtime=30
WHERE (base_name='woth flower' OR name LIKE '%woth flower%') AND item_type='herb';

-- Head & neck herbs
UPDATE items SET
    name='a rose-marrow potion', short_name='rose-marrow potion', article='a',
    heal_type='head', heal_rank=1, heal_amount=0, herb_roundtime=15
WHERE (base_name='rose-marrow potion' OR name LIKE '%rose-marrow%') AND item_type='herb';

UPDATE items SET
    name='some aloeas stem', short_name='aloeas stem', article='some',
    heal_type='head', heal_rank=2, heal_amount=0, herb_roundtime=25
WHERE (base_name='aloeas stem' OR name LIKE '%aloeas%') AND item_type='herb';

UPDATE items SET
    name='some haphip root', short_name='haphip root', article='some',
    heal_type='head', heal_rank=3, heal_amount=0, herb_roundtime=15
WHERE (base_name='haphip root' OR name LIKE '%haphip%') AND item_type='herb';

UPDATE items SET
    name='a brostheras potion', short_name='brostheras potion', article='a',
    heal_type='head', heal_rank=4, heal_amount=0, herb_roundtime=30
WHERE (base_name='brostheras potion' OR name LIKE '%brostheras%') AND item_type='herb';

-- Torso & eye herbs
UPDATE items SET
    name='some basal moss', short_name='basal moss', article='some',
    heal_type='torso', heal_rank=1, heal_amount=0, herb_roundtime=15
WHERE (base_name='basal moss' OR name LIKE '%basal moss%') AND item_type='herb';

UPDATE items SET
    name='some pothinir grass', short_name='pothinir grass', article='some',
    heal_type='torso', heal_rank=2, heal_amount=0, herb_roundtime=25
WHERE (base_name='pothinir grass' OR name LIKE '%pothinir%') AND item_type='herb';

UPDATE items SET
    name='a talneo potion', short_name='talneo potion', article='a',
    heal_type='torso', heal_rank=3, heal_amount=0, herb_roundtime=15
WHERE (base_name='talneo potion' OR name LIKE '%talneo%') AND item_type='herb';

UPDATE items SET
    name='a wingstem potion', short_name='wingstem potion', article='a',
    heal_type='torso', heal_rank=4, heal_amount=0, herb_roundtime=30
WHERE (base_name='wingstem potion' OR name LIKE '%wingstem%') AND item_type='herb';

UPDATE items SET
    name='a bur-clover potion', short_name='bur-clover potion', article='a',
    heal_type='eye', heal_rank=5, heal_amount=0, herb_roundtime=30
WHERE (base_name='bur-clover potion' OR name LIKE '%bur-clover%') AND item_type='herb';

-- Limb herbs
UPDATE items SET
    name='some ambrominas leaf', short_name='ambrominas leaf', article='some',
    heal_type='limb', heal_rank=1, heal_amount=0, herb_roundtime=15
WHERE (base_name='ambrominas leaf' OR name LIKE '%ambrominas%') AND item_type='herb';

UPDATE items SET
    name='some ephlox moss', short_name='ephlox moss', article='some',
    heal_type='limb', heal_rank=2, heal_amount=0, herb_roundtime=25
WHERE (base_name='ephlox moss' OR name LIKE '%ephlox%') AND item_type='herb';

UPDATE items SET
    name='some cactacae spine', short_name='cactacae spine', article='some',
    heal_type='limb', heal_rank=3, heal_amount=0, herb_roundtime=15
WHERE (base_name='cactacae spine' OR name LIKE '%cactacae%') AND item_type='herb';

UPDATE items SET
    name='some calamia fruit', short_name='calamia fruit', article='some',
    heal_type='limb', heal_rank=4, heal_amount=0, herb_roundtime=30
WHERE (base_name='calamia fruit' OR name LIKE '%calamia%') AND item_type='herb';

UPDATE items SET
    name='some sovyn clove', short_name='sovyn clove', article='some',
    heal_type='limb_regen', heal_rank=5, heal_amount=0, herb_roundtime=30
WHERE (base_name='sovyn clove' OR name LIKE '%sovyn%') AND item_type='herb';

-- ============================================================
-- SECTION 2: Add proper armor pieces for exposed locations
-- Double Leather (ASG 8) covers head/torso/arms/legs.
-- Neck, hands, and feet need separate armor pieces.
-- Per GS4 wiki, leather gorget/gloves/boots fill these slots.
-- ============================================================

-- Leather gorget (neck, ASG 5 equivalent)
INSERT IGNORE INTO items (
    name, short_name, base_name, noun, article, item_type,
    material, armor_asg, armor_group, defense_bonus, action_penalty,
    spell_hindrance, worn_location, weight, value, is_template,
    description, examine_text
) VALUES (
    'a leather gorget', 'leather gorget', 'gorget', 'gorget', 'a', 'armor',
    'leather', 5, 'leather', 0, 0, 0, 'neck', 0.5, 800, 1,
    'A supple leather gorget shaped to protect the throat and lower neck.',
    'The gorget is made of several layers of boiled leather stitched tightly together, providing reasonable protection for the vulnerable neck region.'
);

-- Reinforced leather gorget (neck, ASG 7)
INSERT IGNORE INTO items (
    name, short_name, base_name, noun, article, item_type,
    material, armor_asg, armor_group, defense_bonus, action_penalty,
    spell_hindrance, worn_location, weight, value, is_template,
    description, examine_text
) VALUES (
    'a reinforced leather gorget', 'reinforced leather gorget', 'gorget', 'gorget', 'a', 'armor',
    'leather', 7, 'leather', 0, 0, 1, 'neck', 0.8, 2200, 1,
    'A reinforced leather gorget with additional plating sewn into the lining.',
    'The gorget features a layered construction with hardened inserts providing greater neck protection at the cost of slightly reduced spell casting ease.'
);

-- Leather gloves (hands, ASG 5 equivalent)
INSERT IGNORE INTO items (
    name, short_name, base_name, noun, article, item_type,
    material, armor_asg, armor_group, defense_bonus, action_penalty,
    spell_hindrance, worn_location, weight, value, is_template,
    description, examine_text
) VALUES (
    'some leather gloves', 'leather gloves', 'gloves', 'gloves', 'some', 'armor',
    'leather', 5, 'leather', 0, 0, 0, 'hands', 0.3, 600, 1,
    'A pair of supple leather gloves offering basic hand protection.',
    'The gloves are cut from a single piece of soft leather, stitched at the fingers to allow reasonable dexterity while protecting the hands.'
);

-- Leather gauntlets (hands, ASG 8)
INSERT IGNORE INTO items (
    name, short_name, base_name, noun, article, item_type,
    material, armor_asg, armor_group, defense_bonus, action_penalty,
    spell_hindrance, worn_location, weight, value, is_template,
    description, examine_text
) VALUES (
    'some leather gauntlets', 'leather gauntlets', 'gauntlets', 'gauntlets', 'some', 'armor',
    'leather', 8, 'leather', 0, 1, 1, 'hands', 0.6, 1800, 1,
    'A pair of thick double-leather gauntlets reinforced with overlapping panels.',
    'The gauntlets are constructed from the same double-layer leather used in full body armor, with extra padding at the knuckles and wrist guards.'
);

-- Leather boots (feet, ASG 5 equivalent)
INSERT IGNORE INTO items (
    name, short_name, base_name, noun, article, item_type,
    material, armor_asg, armor_group, defense_bonus, action_penalty,
    spell_hindrance, worn_location, weight, value, is_template,
    description, examine_text
) VALUES (
    'some leather boots', 'leather boots', 'boots', 'boots', 'some', 'armor',
    'leather', 5, 'leather', 0, 0, 0, 'feet', 0.8, 700, 1,
    'A sturdy pair of leather boots reaching mid-calf.',
    'The boots are made of stiff, cured leather with a reinforced toe and heel. They provide solid foot protection without significantly impeding movement.'
);

-- Reinforced leather boots (feet, ASG 8)
INSERT IGNORE INTO items (
    name, short_name, base_name, noun, article, item_type,
    material, armor_asg, armor_group, defense_bonus, action_penalty,
    spell_hindrance, worn_location, weight, value, is_template,
    description, examine_text
) VALUES (
    'some reinforced leather boots', 'reinforced leather boots', 'boots', 'boots', 'some', 'armor',
    'leather', 8, 'leather', 0, 1, 0, 'feet', 1.2, 2000, 1,
    'A pair of double-leather boots with reinforced ankle guards and shin panels.',
    'The boots match a full suit of double leather armor in construction — two layers of boiled leather with rigid shin guards and ankle protection.'
);

-- ============================================================
-- SECTION 3: Stock new armor pieces in Ta'Vaalor shops
-- Shop 2: The Ta'Vaalor Armory (Gearchel)
-- Shop 3: Ghaerdish's Furs and Pelts (Sylindra)
-- ============================================================

-- Ta'Vaalor Armory stocks gorgets, gauntlets, reinforced boots
INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 2, id, -1, -1, 3600 FROM items WHERE name='a leather gorget'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 2, id, -1, -1, 3600 FROM items WHERE name='a reinforced leather gorget'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 2, id, -1, -1, 3600 FROM items WHERE name='some leather gauntlets'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 2, id, -1, -1, 3600 FROM items WHERE name='some reinforced leather boots' AND is_template=1 LIMIT 1;

-- Ghaerdish's Furs and Pelts stocks gorgets, basic gloves, basic boots (leather focus)
INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 3, id, -1, -1, 3600 FROM items WHERE name='a leather gorget'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 3, id, -1, -1, 3600 FROM items WHERE name='some leather gloves' AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 3, id, -1, -1, 3600 FROM items WHERE name='some leather boots'  AND is_template=1 LIMIT 1;

-- ============================================================
-- SECTION 4: Room 3542 (Ta'Vaalor, Victory Court) — Supernode
-- The Victory Court with the statue of Kai is a known supernode
-- in Ta'Vaalor per the GS4 wiki (mana-rich location).
-- ============================================================

-- Ensure the zone row exists (zone_id=2 is Ta'Vaalor)
INSERT IGNORE INTO zones (id, slug, name, region, level_min, level_max, climate, is_enabled)
VALUES (2, 'tavaalor', 'Ta''Vaalor', 'Elanith', 1, 30, 'temperate', TRUE)
ON DUPLICATE KEY UPDATE is_enabled=TRUE;

-- Upsert the room with is_supernode=TRUE
INSERT INTO rooms (id, zone_id, title, is_safe, is_supernode, is_indoor, terrain_type)
VALUES (3542, 2, 'Ta''Vaalor, Victory Court', TRUE, TRUE, FALSE, 'outdoor')
ON DUPLICATE KEY UPDATE
    is_supernode = TRUE,
    is_safe      = TRUE;

-- ============================================================
-- Verification queries (comment out for production runs)
-- ============================================================
-- SELECT name, article, heal_type, heal_rank, heal_amount FROM items WHERE item_type='herb' ORDER BY heal_type, heal_rank;
-- SELECT name, worn_location, armor_asg FROM items WHERE item_type='armor' AND worn_location IN ('neck','hands','feet');
-- SELECT is_supernode FROM rooms WHERE id=3542;
