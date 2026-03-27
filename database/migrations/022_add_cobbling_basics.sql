-- 022_add_cobbling_basics.sql
-- Starter cobbling templates + cobbler shop support for leather slippers.

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a leather upper', 'leather upper', 'upper', 'a', 'crafting', 1, 0,
    0.40, 55, 'leather',
    'A prepared leather upper waiting to be joined into a simple shoe.',
    'The upper has already been cut to a novice-friendly slipper pattern.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'leather upper' AND noun = 'upper'
);

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a leather sole', 'leather sole', 'sole', 'a', 'crafting', 1, 0,
    0.35, 45, 'leather',
    'A shaped leather sole sized for a simple pair of slippers.',
    'The sole is sturdy enough for soft indoor and town wear.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'leather sole' AND noun = 'sole'
);

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a piece of tailor''s chalk', 'tailor''s chalk', 'chalk', 'a', 'crafting', 1, 0,
    0.10, 20, 'chalk',
    'A small piece of tailor''s chalk for marking leather.',
    'The chalk leaves a clean pale line across leather.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'tailor''s chalk' AND noun = 'chalk'
);

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a measuring cord', 'measuring cord', 'cord', 'a', 'crafting', 1, 0,
    0.10, 30, 'cord',
    'A thin measuring cord knotted at regular fitting intervals.',
    'The cord is meant for checking fit and spacing during cobbling work.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'measuring cord' AND noun = 'cord'
);

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, worn_location, armor_group, defense_bonus,
    description, examine_text
)
SELECT
    'some leather slippers', 'leather slippers', 'slippers', 'some', 'armor', 1, 0,
    1.00, 140, 'leather', 'feet', 'leather', 0,
    'A simple pair of leather slippers with soft, flexible soles.',
    'They look serviceable and comfortable enough for everyday wear.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'leather slippers' AND noun = 'slippers'
);

INSERT INTO shops (name, room_id, shop_type, buy_multiplier, sell_multiplier, is_active)
SELECT
    CASE room_id
        WHEN 33264 THEN 'The Elven Sole'
        WHEN 26006 THEN 'The Glimaerstone Heel'
        WHEN 9065 THEN 'The Cobbler''s Shop'
        WHEN 14808 THEN 'Cobblers'' Wares'
        WHEN 16167 THEN 'Cobbling Court Supplies'
        WHEN 16863 THEN 'D.H. Cobbling Outlet'
        WHEN 17170 THEN 'The Cobbler''s Cobby'
        WHEN 19393 THEN 'Cobbler''s Delight'
        WHEN 24448 THEN 'Icemule Cobbler Supplies'
        WHEN 33898 THEN 'Cordwainer''s Muse'
        ELSE CONCAT('Cobbling Supplies ', room_id)
    END,
    room_id,
    'armor',
    1.00,
    0.50,
    1
FROM (
    SELECT 33264 AS room_id UNION ALL
    SELECT 26006 UNION ALL
    SELECT 9065 UNION ALL
    SELECT 14808 UNION ALL
    SELECT 16167 UNION ALL
    SELECT 16863 UNION ALL
    SELECT 17170 UNION ALL
    SELECT 19393 UNION ALL
    SELECT 24448 UNION ALL
    SELECT 33898
) rooms_to_seed
WHERE EXISTS (SELECT 1 FROM rooms r WHERE r.id = rooms_to_seed.room_id)
  AND NOT EXISTS (SELECT 1 FROM shops s WHERE s.room_id = rooms_to_seed.room_id);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.short_name = 'leather upper'
WHERE s.room_id IN (33264,26006,9065,14808,16167,16863,17170,19393,24448,33898)
  AND NOT EXISTS (SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.short_name = 'leather sole'
WHERE s.room_id IN (33264,26006,9065,14808,16167,16863,17170,19393,24448,33898)
  AND NOT EXISTS (SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.short_name = 'tailor''s chalk'
WHERE s.room_id IN (33264,26006,9065,14808,16167,16863,17170,19393,24448,33898)
  AND NOT EXISTS (SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.short_name = 'measuring cord'
WHERE s.room_id IN (33264,26006,9065,14808,16167,16863,17170,19393,24448,33898)
  AND NOT EXISTS (SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.id = 1
WHERE s.room_id IN (33264,26006,9065,14808,16167,16863,17170,19393,24448,33898)
  AND NOT EXISTS (SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.short_name = 'leather slippers'
WHERE s.room_id IN (33264,26006,9065,14808,16167,16863,17170,19393,24448,33898)
  AND NOT EXISTS (SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id);
