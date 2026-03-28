USE gemstone_dev;

-- Add the core skinning tool templates.
-- Shop-facing prices are tuned for current furrier buy_multiplier = 1.05:
--   skinning knife  -> 5700 silver ask price (value 5429)
--   hook-knife      -> 6000 silver ask price (value 5715)
-- The sheath price is a custom local price point because a consistent GS4 wiki
-- town-shop reference was not available for it.

INSERT INTO items (
    name, short_name, base_name, noun, article, item_type,
    is_template, is_stackable, material, weight, value,
    weapon_type, weapon_category, damage_factor, weapon_speed, damage_type,
    description, examine_text, lore_text
)
SELECT
    'a skinning knife', 'skinning knife', 'skinning knife', 'knife', 'a', 'weapon',
    1, 0, 'steel', 0.5, 5429,
    'edged', 'edged', 0.25, 1, 'slash,puncture',
    'A slim steel knife designed for careful skinning work and quick close-in cuts.',
    'The narrow blade is keenly honed, with just enough curve near the tip to separate hide from flesh cleanly.',
    'A purpose-built skinning tool prized by hunters, trappers, and anyone who knows the value of a clean pelt.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'skinning knife' AND is_template = 1
);

UPDATE items
SET
    name = 'a skinning knife',
    base_name = 'skinning knife',
    noun = 'knife',
    article = 'a',
    item_type = 'weapon',
    is_template = 1,
    is_stackable = 0,
    material = 'steel',
    weight = 0.5,
    value = 5429,
    weapon_type = 'edged',
    weapon_category = 'edged',
    damage_factor = 0.25,
    weapon_speed = 1,
    damage_type = 'slash,puncture',
    description = 'A slim steel knife designed for careful skinning work and quick close-in cuts.',
    examine_text = 'The narrow blade is keenly honed, with just enough curve near the tip to separate hide from flesh cleanly.',
    lore_text = 'A purpose-built skinning tool prized by hunters, trappers, and anyone who knows the value of a clean pelt.'
WHERE short_name = 'skinning knife' AND is_template = 1;

INSERT INTO items (
    name, short_name, base_name, noun, article, item_type,
    is_template, is_stackable, material, weight, value,
    weapon_type, weapon_category, damage_factor, weapon_speed, damage_type,
    description, examine_text, lore_text
)
SELECT
    'a hook-knife', 'hook-knife', 'hook-knife', 'knife', 'a', 'weapon',
    1, 0, 'steel', 0.5, 5715,
    'brawling', 'brawling', 0.25, 1, 'slash,puncture',
    'A curved blade that hooks and tears with each close-quarter strike.',
    'The inside edge sweeps into a wicked hook, making the knife useful for both carving and ripping cuts.',
    'Hunters favor the compact weapon when they want a skinning-capable blade that still bites hard in a clinch.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'hook-knife' AND is_template = 1
);

UPDATE items
SET
    name = 'a hook-knife',
    base_name = 'hook-knife',
    noun = 'knife',
    article = 'a',
    item_type = 'weapon',
    is_template = 1,
    is_stackable = 0,
    material = 'steel',
    weight = 0.5,
    value = 5715,
    weapon_type = 'brawling',
    weapon_category = 'brawling',
    damage_factor = 0.25,
    weapon_speed = 1,
    damage_type = 'slash,puncture',
    description = 'A curved blade that hooks and tears with each close-quarter strike.',
    examine_text = 'The inside edge sweeps into a wicked hook, making the knife useful for both carving and ripping cuts.',
    lore_text = 'Hunters favor the compact weapon when they want a skinning-capable blade that still bites hard in a clinch.'
WHERE short_name = 'hook-knife' AND is_template = 1;

INSERT INTO items (
    name, short_name, base_name, noun, article, item_type,
    is_template, is_stackable, material, weight, value,
    container_capacity, sheath_type, container_type, worn_location,
    description, examine_text, lore_text
)
SELECT
    'a skinning knife sheath', 'skinning knife sheath', 'skinning knife sheath', 'sheath', 'a', 'container',
    1, 0, 'leather', 0.4, 239,
    1, 'skinning_tool_sheath', 'wearable', 'skinning_sheath',
    'A narrow leather sheath made to ride beside your other gear without taking up a normal worn slot.',
    'The sheath is slim but stiff, with a reinforced mouth sized for compact skinning blades and daggers.',
    'This dedicated sheath is cut for small skinning tools and buckles on independently of ordinary worn equipment.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'skinning knife sheath' AND is_template = 1
);

UPDATE items
SET
    name = 'a skinning knife sheath',
    base_name = 'skinning knife sheath',
    noun = 'sheath',
    article = 'a',
    item_type = 'container',
    is_template = 1,
    is_stackable = 0,
    material = 'leather',
    weight = 0.4,
    value = 239,
    container_capacity = 1,
    sheath_type = 'skinning_tool_sheath',
    container_type = 'wearable',
    worn_location = 'skinning_sheath',
    description = 'A narrow leather sheath made to ride beside your other gear without taking up a normal worn slot.',
    examine_text = 'The sheath is slim but stiff, with a reinforced mouth sized for compact skinning blades and daggers.',
    lore_text = 'This dedicated sheath is cut for small skinning tools and buckles on independently of ordinary worn equipment.'
WHERE short_name = 'skinning knife sheath' AND is_template = 1;

-- Stock every current furrier.
INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.short_name = 'skinning knife' AND i.is_template = 1
WHERE s.name IN (
    'Dagresar''s Furs',
    'Dakris''s Furs',
    'E and S''s Fine Furs',
    'Felinium''s Fur Emporium',
    'Gaedrein''s Furs and Pelts',
    'Ghaerdish''s Furs and Pelts',
    'Maeve''s Furs'
)
AND NOT EXISTS (
    SELECT 1
    FROM shop_inventory si
    WHERE si.shop_id = s.id AND si.item_id = i.id
);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.short_name = 'hook-knife' AND i.is_template = 1
WHERE s.name IN (
    'Dagresar''s Furs',
    'Dakris''s Furs',
    'E and S''s Fine Furs',
    'Felinium''s Fur Emporium',
    'Gaedrein''s Furs and Pelts',
    'Ghaerdish''s Furs and Pelts',
    'Maeve''s Furs'
)
AND NOT EXISTS (
    SELECT 1
    FROM shop_inventory si
    WHERE si.shop_id = s.id AND si.item_id = i.id
);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN items i ON i.short_name = 'skinning knife sheath' AND i.is_template = 1
WHERE s.name IN (
    'Dagresar''s Furs',
    'Dakris''s Furs',
    'E and S''s Fine Furs',
    'Felinium''s Fur Emporium',
    'Gaedrein''s Furs and Pelts',
    'Ghaerdish''s Furs and Pelts',
    'Maeve''s Furs'
)
AND NOT EXISTS (
    SELECT 1
    FROM shop_inventory si
    WHERE si.shop_id = s.id AND si.item_id = i.id
);
