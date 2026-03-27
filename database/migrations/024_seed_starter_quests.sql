-- 024_seed_starter_quests.sql
-- Seed starter-town level 1-5 quest content, materials, and support items.

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed dispatch for Aznell', 'sealed dispatch for Aznell', 'dispatch', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A neatly folded dispatch bearing the seal of Moot Hall.',
    'The dispatch is sealed for delivery to Aznell and should not be opened.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed dispatch for Aznell');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed dispatch for Krythussa', 'sealed dispatch for Krythussa', 'dispatch', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A sealed municipal dispatch marked for Krythussa''s confectionary.',
    'The dispatch is meant for Krythussa and bears the Moot Hall seal.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed dispatch for Krythussa');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed dispatch for Kilron', 'sealed dispatch for Kilron', 'dispatch', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A sealed notice intended for Kilron''s pawn counter.',
    'The dispatch is sealed for Kilron and smells faintly of sealing wax.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed dispatch for Kilron');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed packet for Berrytoe', 'sealed packet for Berrytoe', 'packet', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A wax-sealed packet marked for Berrytoe''s General Store.',
    'The packet should be delivered to Berrytoe unopened.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed packet for Berrytoe');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed packet for Leaftoe', 'sealed packet for Leaftoe', 'packet', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A carefully tied packet with Clovertooth Hall''s seal impressed in blue wax.',
    'The packet is addressed to Leaftoe and should stay sealed until delivered.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed packet for Leaftoe');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed packet for the Penguin', 'sealed packet for the Penguin', 'packet', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A tidy packet meant for the innkeeper at the Thirsty Penguin.',
    'The packet bears a Clovertooth Hall seal and a short routing note for the Penguin.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed packet for the Penguin');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed message for Yendrel', 'sealed message for Yendrel', 'message', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A crisp sealed message stamped with Sassion''s runner mark.',
    'The message is meant for Archivist Yendrel.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed message for Yendrel');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed message for Thalindra', 'sealed message for Thalindra', 'message', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A sealed message intended for the Adventurers'' Guild clerk.',
    'The message is marked for Thalindra and should be delivered promptly.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed message for Thalindra');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a sealed message for Saphrie', 'sealed message for Saphrie', 'message', 'a', 'quest', 1, 0,
    0.05, 1, 'paper',
    'A sealed requisition note bearing Sassion''s neat hand.',
    'The message is for Saphrie and appears time-sensitive.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'sealed message for Saphrie');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a glass of water', 'glass of water', 'water', 'a', 'drink', 1, 0,
    0.20, 5, 'glass',
    'A clear glass filled with cool water.',
    'The water looks fresh enough to satisfy a tired gate guard.'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM items WHERE short_name = 'glass of water' AND noun = 'water');

INSERT INTO shops (name, room_id, shop_type, buy_multiplier, sell_multiplier, is_active)
SELECT 'Malwith Inn Bar', 10386, 'food', 1.0, 0.10, 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM shops WHERE room_id = 10386);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 10, 900
FROM shops s
JOIN rooms r ON r.id = s.room_id
JOIN items i ON i.short_name = 'glass of water' AND i.noun = 'water'
WHERE r.title IN ('Malwith Inn, Bar', 'The Thirsty Penguin, Bar', 'Raging Thrak Inn, Barroom')
  AND NOT EXISTS (
      SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id
  );

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'raging_thrak_lesson', 'Thrak''s Hard Lessons',
       'Hear out Raging Thrak and prove you were listening.',
       1, 2, 0, 'quests/starter/raging_thrak_lesson'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'raging_thrak_lesson');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'trevor_dabbings_lesson', 'A Gentleman of Trace',
       'Listen to Trevor Dabbings and answer his starter questions.',
       1, 2, 0, 'quests/starter/trevor_dabbings_lesson'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'trevor_dabbings_lesson');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'tedrik_lesson', 'Tedrik''s Officer''s Briefing',
       'Sit with Tedrik and prove you absorbed the basics.',
       1, 2, 0, 'quests/starter/tedrik_lesson'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'tedrik_lesson');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'wl_town_clerk_aznell', 'Arms Ledger Dispatch',
       'Carry a sealed dispatch from Moot Hall to Aznell''s Armory.',
       1, 5, 1, 'quests/starter/wl_town_clerk_aznell'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'wl_town_clerk_aznell');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'wl_town_clerk_krythussa', 'Sweetshop Receipt Run',
       'Carry a sealed dispatch from Moot Hall to Krythussa''s shop.',
       1, 5, 1, 'quests/starter/wl_town_clerk_krythussa'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'wl_town_clerk_krythussa');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'wl_town_clerk_kilron', 'Pawn Counter Notice',
       'Carry a sealed dispatch from Moot Hall to Kilron''s pawnshop.',
       1, 5, 1, 'quests/starter/wl_town_clerk_kilron'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'wl_town_clerk_kilron');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'imt_bondsman_berrytoe', 'Market Packet',
       'Carry a sealed packet from Clovertooth Hall to Berrytoe''s store.',
       1, 5, 1, 'quests/starter/imt_bondsman_berrytoe'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'imt_bondsman_berrytoe');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'imt_bondsman_leaftoe', 'Apothecary Packet',
       'Carry a sealed packet from Clovertooth Hall to Leaftoe''s shop.',
       1, 5, 1, 'quests/starter/imt_bondsman_leaftoe'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'imt_bondsman_leaftoe');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'imt_bondsman_penguin', 'Penguin House Packet',
       'Carry a sealed packet from Clovertooth Hall to the Thirsty Penguin.',
       1, 5, 1, 'quests/starter/imt_bondsman_penguin'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'imt_bondsman_penguin');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'tv_sassion_archivist', 'Archive Message',
       'Carry Sassion''s sealed message to Archivist Yendrel.',
       1, 5, 1, 'quests/starter/tv_sassion_archivist'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'tv_sassion_archivist');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'tv_sassion_thalindra', 'Guild Hall Note',
       'Carry Sassion''s sealed message to Thalindra at the Adventurers'' Guild.',
       1, 5, 1, 'quests/starter/tv_sassion_thalindra'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'tv_sassion_thalindra');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'tv_sassion_saphrie', 'Herbal Requisition',
       'Carry Sassion''s sealed message to Saphrie''s shop.',
       1, 5, 1, 'quests/starter/tv_sassion_saphrie'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'tv_sassion_saphrie');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'tv_guard_water_victory', 'Victory Gate Water Run',
       'Bring a fresh glass of water to Laerindra at Victory Gate.',
       1, 4, 1, 'quests/starter/tv_guard_water_victory'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'tv_guard_water_victory');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'tv_guard_water_amaranth', 'Amaranth Gate Water Run',
       'Bring a fresh glass of water to Sorvael at Amaranth Gate.',
       1, 4, 1, 'quests/starter/tv_guard_water_amaranth'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'tv_guard_water_amaranth');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'tv_guard_water_vermilion', 'Vermilion Gate Water Run',
       'Bring a fresh glass of water to Raertria at Vermilion Gate.',
       1, 4, 1, 'quests/starter/tv_guard_water_vermilion'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'tv_guard_water_vermilion');

INSERT INTO quest_definitions (key_name, title, description, min_level, max_level, is_repeatable, lua_script)
SELECT 'tv_guard_water_annatto', 'Annatto Gate Water Run',
       'Bring a fresh glass of water to Daervith at Annatto Gate.',
       1, 4, 1, 'quests/starter/tv_guard_water_annatto'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM quest_definitions WHERE key_name = 'tv_guard_water_annatto');
