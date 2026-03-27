-- ============================================================
-- Migration: populate_missing_creatures.sql
-- Adds creature DB rows for zones whose Lua mob files existed
-- but had no corresponding creatures table entry:
--   - scripts/zones/fearling_pass/mobs/kobold.lua         (ID 9009)
--   - scripts/zones/toadwort/mobs/fanged_goblin.lua       (ID 7001)
--   - scripts/zones/toadwort/mobs/mistydeep_siren.lua     (ID 7002)
--   - scripts/zones/toadwort/mobs/fanged_viper.lua        (ID 7003)
--   - scripts/zones/toadwort/mobs/water_moccasin.lua      (ID 7004)
--   - scripts/zones/toadwort/mobs/bobcat.lua              (ID 7005)
--   - scripts/zones/neartofar_forest/mobs/plumed_cockatrice.lua (ID 6001)
--   - scripts/zones/neartofar_forest/mobs/neartofar_orc.lua     (ID 6002)
--   - scripts/zones/neartofar_forest/mobs/neartofar_troll.lua   (ID 6003)
--   - scripts/zones/neartofar_forest/mobs/ogre_warrior.lua      (ID 6004)
--
-- Run AFTER all prior migrations.
-- All stats sourced from gswiki.play.net and cross-checked against
-- existing creature entries for level-appropriate consistency.
-- ============================================================

USE gemstone_dev;

-- ────────────────────────────────────────────────────────────
-- LOOT TABLES
-- Starting at ID 400 to avoid collision with existing 201-367 range.
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_tables` (`id`, `name`) VALUES
    (400, 'Fanged goblin drops'),       -- 7001
    (401, 'Mistydeep siren drops'),     -- 7002
    (402, 'Plumed cockatrice drops'),   -- 6001
    (403, 'Neartofar orc drops'),       -- 6002
    (404, 'Neartofar troll drops'),     -- 6003
    (405, 'Ogre warrior drops');        -- 6004
-- Kobold (9009): no loot table — coins/gems handled by engine flags
-- Fanged viper (7003): no loot table — no coins/gems
-- Water moccasin (7004): no loot table — no coins/gems
-- Bobcat (7005): no loot table — no coins/gems (skin only)

-- ────────────────────────────────────────────────────────────
-- LOOT TABLE ENTRIES
-- item 1032 = a wooden coffer
-- item 1035 = a dented iron box
-- item 1082 = an ornate brass box
-- Entry IDs start at 6200 (max existing = 6130, safe gap).
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_table_entries`
    (`id`, `loot_table_id`, `item_id`, `drop_chance`, `quantity_min`, `quantity_max`)
VALUES
    -- Fanged goblin (level 2) — boxes weighted light
    (6200, 400, 1032, 20.00, 1, 1),
    (6201, 400, 1035, 10.00, 1, 1),

    -- Mistydeep siren (level 2) — caster, slightly better boxes
    (6202, 401, 1032, 15.00, 1, 1),
    (6203, 401, 1035, 15.00, 1, 1),
    (6204, 401, 1082, 5.00,  1, 1),

    -- Plumed cockatrice (level 13)
    (6205, 402, 1032, 15.00, 1, 1),
    (6206, 402, 1035, 20.00, 1, 1),
    (6207, 402, 1082, 8.00,  1, 1),

    -- Neartofar orc (level 11)
    (6208, 403, 1032, 15.00, 1, 1),
    (6209, 403, 1035, 20.00, 1, 1),
    (6210, 403, 1082, 8.00,  1, 1),

    -- Neartofar troll (level 15)
    (6211, 404, 1032, 15.00, 1, 1),
    (6212, 404, 1035, 20.00, 1, 1),
    (6213, 404, 1082, 10.00, 1, 1),

    -- Ogre warrior (level 20)
    (6214, 405, 1032, 15.00, 1, 1),
    (6215, 405, 1035, 20.00, 1, 1),
    (6216, 405, 1082, 12.00, 1, 1);

-- ────────────────────────────────────────────────────────────
-- CREATURES
-- Column order matches existing schema:
--   id, name, article, level, creature_type, health_max,
--   attack_strength, defense_strength, casting_strength, target_defense,
--   action_timer, behavior_script, is_aggressive, can_cast, can_maneuver,
--   is_undead, body_type, experience_value, silver_min, silver_max,
--   loot_table_id, skin_noun, skin_item_id, description, death_message
--
-- attack_strength  = highest single AS from Lua attacks block
-- defense_strength = ds_melee from Lua
-- casting_strength = cs from Lua spells block (0 if none)
-- target_defense   = td_spiritual from Lua (elemental matches in all cases)
-- can_cast         = 1 if spells block is non-empty
-- can_maneuver     = 1 if abilities contain a maneuver-type (pounce, stare_maneuver)
-- is_undead        = 0 for all below (all living classification)
-- experience_value = verified against existing creature level curve in DB
-- silver_min/max   = 0 for non-coin carriers; scaled by level for humanoids
-- ────────────────────────────────────────────────────────────
INSERT INTO `creatures`
    (`id`, `name`, `article`, `level`, `creature_type`, `health_max`,
     `attack_strength`, `defense_strength`, `casting_strength`, `target_defense`,
     `action_timer`, `behavior_script`, `is_aggressive`, `can_cast`, `can_maneuver`,
     `is_undead`, `body_type`, `experience_value`, `silver_min`, `silver_max`,
     `loot_table_id`, `skin_noun`, `skin_item_id`, `description`, `death_message`)
VALUES

-- ── Fearling Pass / Briar Thicket ─────────────────────────
-- Kobold (level 1) — Briar Thicket rooms only.
-- Stats from gswiki.play.net/Kobold: DS 18, AS 36 short sword, TD 3.
-- HP 40 per wiki. XP 20 (level 1 curve).
(9009, 'kobold', 'a', 1, 'normal', 40,
 36, 18, 0, 3,
 8, NULL, 1, 0, 0,
 0, 'biped', 20, 2, 8,
 NULL, 'kobold skin', NULL,
 'Smaller than a dwarf and even many halflings, the kobold has ruddy skin and a hairless pate topped with small horns.  Long-limbed for its size, it eschews brute strength and relies on what agility it can pretend to possess.  Its beady little black eyes size you up with improbable calculation.',
 'falls face-first into the dirt.'),

-- ── Toadwort ──────────────────────────────────────────────
-- Fanged goblin (level 2) — Muddy Path / upper toadwort.
-- Stats from Lua: AS 46, DS 55, TD 6. HP 50. XP 56 (level 2 curve).
-- Silver: 4-16 (humanoid level 2 standard). Loot table 400.
(7001, 'fanged goblin', 'a', 2, 'normal', 50,
 46, 55, 0, 6,
 9, NULL, 1, 0, 0,
 0, 'biped', 56, 4, 16,
 400, 'goblin fang', NULL,
 'Round-headed with a squat nose and wide mouth, the fanged goblin has dark cast green skin with a sickly yellow tinge.  Long, sharp fangs poke out of puffed lips forcing a perpetual sneer.  A yeasty smell of something left to rot completes its aura.',
 'crumples into the muck.'),

-- Mistydeep siren (level 2) — Muddy Path / waterways.
-- Stats from Lua: AS 50, DS 20, CS 10 (Calm 201), TD 6. HP 42. XP 56.
-- Silver: 4-16. Loot table 401.
(7002, 'Mistydeep siren', 'a', 2, 'normal', 42,
 50, 20, 10, 6,
 9, NULL, 1, 1, 0,
 0, 'biped', 56, 4, 16,
 401, '', NULL,
 'The Mistydeep siren''s pale eyes melt to a warm blue as she transfixes her gaze on victims.  She uses her melodious voice to allure.  From a distance she appears a beautiful maiden, but without glamour her bluish corpselike skin reveals her true nature.',
 'slumps to the soggy ground.'),

-- Fanged viper (level 4) — Blackened Morass.
-- Stats from Lua: AS 68, DS 37, TD 12. HP 50. XP 176.
-- No coins or boxes (snake). Skin only.
(7003, 'fanged viper', 'a', 4, 'normal', 50,
 68, 37, 0, 12,
 8, NULL, 1, 0, 0,
 0, 'ophidian', 176, 0, 0,
 NULL, 'viper skin', NULL,
 'The fanged viper slithers quickly through the landscape, its massive venomous fangs hidden by small flaps of skin.  Once its ire is aroused, the flaps pull back revealing the true monster.  Death rapidly awaits any who doubt its abilities.',
 'coils loosely and goes still.'),

-- Water moccasin (level 4) — Blackened Morass / waterways.
-- Stats from Lua: AS 68, DS 37, TD 12. HP 50. XP 176.
-- No coins or boxes. Skin only.
(7004, 'water moccasin', 'a', 4, 'normal', 50,
 68, 37, 0, 12,
 8, NULL, 1, 0, 0,
 0, 'ophidian', 176, 0, 0,
 NULL, 'water moccasin skin', NULL,
 'The water moccasin appears to be at least three feet long, with dark olive-colored skin and a faint diamond pattern.  When the mouth opens you can see a sickly white lining within.',
 'uncoils slowly and is still.'),

-- Bobcat (level 5) — Fetid Muck & Mire.
-- Stats from Lua: AS 90 (claw), DS 44, TD 15. HP 60. XP 260.
-- can_maneuver=1 (pounce). No coins. Skin claw only.
(7005, 'bobcat', 'a', 5, 'normal', 60,
 90, 44, 0, 15,
 8, NULL, 1, 0, 1,
 0, 'quadruped', 260, 0, 0,
 NULL, 'bobcat claw', NULL,
 'Twice the size of a domestic cat, the bobcat is covered in dense, thick fur varying from soft greys to light reddish brown.  Deep brown spots mark the bobcat''s pelt.  Whisking back and forth with her short banded tail, the bobcat seems anxious to pounce.',
 'crashes to the ground, claws raking one final time.'),

-- ── Neartofar Forest ──────────────────────────────────────
-- Plumed cockatrice (level 13) — Forest paths.
-- Stats from Lua: AS 167 (charge), DS 111, TD 39. HP 120. XP 1508.
-- can_maneuver=1 (stare_maneuver). Silver 0 (animal). Loot 402.
(6001, 'plumed cockatrice', 'a', 13, 'normal', 120,
 167, 111, 0, 39,
 9, NULL, 1, 0, 1,
 0, 'biped', 1508, 0, 0,
 402, 'cockatrice plume', NULL,
 'The plumed cockatrice has a snake-like body, plumes of feathers spearing from its head, dapple grey wings, and short stout legs.  Its cold penetrating gaze is not as deadly as a basilisk''s, but its sharp beak and raking claws make it a fierce opponent.',
 'twitches and goes still.'),

-- Neartofar orc (level 11) — Forest / river paths.
-- Stats from Lua: AS 159 (morning star), DS 80, TD 32. HP 140. XP 1058.
-- Silver 22-88 (humanoid level 11). Loot 403.
(6002, 'Neartofar orc', 'a', 11, 'normal', 140,
 159, 80, 0, 32,
 10, NULL, 1, 0, 0,
 0, 'humanoid', 1058, 22, 88,
 403, 'orc knuckle', NULL,
 'Taller than a common human and of substantially heavier build, the Neartofar orc has a build of solid bone and gristle.  Piercing yellow eyes glare angrily under a thick bony ridge.  His arms resemble thick twisted tree trunks ending in ragged gore-crusted claws.',
 'pitches forward, dead.'),

-- Neartofar troll (level 15) — Forest hillside & ridge.
-- Stats from Lua: AS 179 (longsword), DS 127, TD 52. HP 200. XP 1980.
-- Troll regeneration ability (can_maneuver=0, handled by ability).
-- Silver 0 (troll). Loot 404 for scalp/boxes.
(6003, 'Neartofar troll', 'a', 15, 'normal', 200,
 179, 127, 0, 52,
 10, NULL, 1, 0, 0,
 0, 'humanoid', 1980, 0, 0,
 404, 'greasy troll scalp', NULL,
 'Huge and dangerous, the Neartofar troll towers above even a tall giantman.  Brown and green pigmented skin so thick it serves well as armor covers most of it.  No light of intellect glows in its narrow piggish eyes — only the lust for slaughter.',
 'crashes down dead.'),

-- Ogre warrior (level 20) — Stockade / barracks.
-- Stats from Lua: AS 201 (mace), DS 131, TD 60. HP 250. XP 3440.
-- sunder_shield and essence_shard_drop abilities. Silver 40-160.
-- Loot 405.
(6004, 'ogre warrior', 'an', 20, 'normal', 250,
 201, 131, 0, 60,
 10, NULL, 1, 0, 1,
 0, 'humanoid', 3440, 40, 160,
 405, 'ogre tooth', NULL,
 'The ogre warrior''s bulging muscles and long arms give it an advantage in any encounter.  The heavy, rock-hard skin serves equally well as armor or to keep itself dry from the elements.  Dark, smoking eyes glare out as it challenges any to oppose it.',
 'falls dead with a thunderous crash.');

-- ────────────────────────────────────────────────────────────
-- VERIFICATION NOTES (run after import to confirm)
-- ────────────────────────────────────────────────────────────
-- SELECT id, name, level, experience_value FROM creatures
--   WHERE id IN (9009, 7001, 7002, 7003, 7004, 7005, 6001, 6002, 6003, 6004)
--   ORDER BY id;
--
-- SELECT lt.name, COUNT(lte.id) as entries
--   FROM loot_tables lt
--   LEFT JOIN loot_table_entries lte ON lt.id = lte.loot_table_id
--   WHERE lt.id IN (400,401,402,403,404,405)
--   GROUP BY lt.id, lt.name;
