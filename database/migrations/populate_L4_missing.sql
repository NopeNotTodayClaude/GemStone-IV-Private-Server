-- ============================================================
-- Migration: populate_L4_missing.sql
-- Bottom-to-top build — Level 4 missing creatures.
--
-- NEW CREATURES:
--   9328   cobra         wehnimers_landing / The Graveyard
--   9329   ridge orc     wehnimers_landing / Dead Plateau (Trollfang)
--   10123  cobra         solhaven / Vornavian Coast
--   10124  whiptail      solhaven / Vornavian Coast
--
-- INTENTIONALLY SKIPPED:
--   black urgh -> Yander's Farm — wiki page has zero stats (all ?'s).
--                Cannot build without confirmed AS/DS/HP. Will revisit
--                when/if wiki gets populated or you provide the data.
--
-- ALREADY EXIST (no action needed):
--   fanged viper    (toadwort,   ID 7003) ✓
--   mongrel kobold  (solhaven,   ID 10102) ✓
--   revenant        (glaise_cnoc, ID 1006) ✓  -- CEMETERY, untouched
--   spotted leaper  (rambling_meadows, ID 9107) ✓
--   urgh            (solhaven,   ID 10103) ✓
--   water moccasin  (toadwort,   ID 7004) ✓
--   kobold shaman   (tavaalor,   ID 7011) ✓
--
-- Sources: gswiki.play.net/Cobra, /Ridge_orc, /Whiptail (all verified)
-- Run AFTER populate_L1_L2_L3_missing.sql
-- ============================================================

USE gemstone_dev;

-- ────────────────────────────────────────────────────────────
-- LOOT TABLES
-- Ridge orc drops boxes — needs a loot table.
-- Cobra and whiptail drop nothing (skin only) — no table needed.
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_tables` (`id`, `name`) VALUES
    (415, 'Ridge orc drops');

-- ────────────────────────────────────────────────────────────
-- LOOT TABLE ENTRIES
-- item 1032 = wooden coffer, 1035 = dented iron box
-- Entry IDs start at 6250 (safe gap after L1-L2-L3 batch ended at 6245).
-- Level 4 humanoid drop rates — slightly better than level 3.
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_table_entries`
    (`id`, `loot_table_id`, `item_id`, `drop_chance`, `quantity_min`, `quantity_max`)
VALUES
    (6250, 415, 1032, 22.00, 1, 1),
    (6251, 415, 1035, 15.00, 1, 1);

-- ────────────────────────────────────────────────────────────
-- CREATURES
-- Column order:
--   id, name, article, level, creature_type, health_max,
--   attack_strength, defense_strength, casting_strength, target_defense,
--   action_timer, behavior_script, is_aggressive, can_cast, can_maneuver,
--   is_undead, body_type, experience_value, silver_min, silver_max,
--   loot_table_id, skin_noun, skin_item_id, description, death_message
--
-- XP level 4 = 176 (per established DB curve)
-- silver: 8-32 for humanoids (level 4 scale), 0 for animals/reptiles
-- ────────────────────────────────────────────────────────────
INSERT INTO `creatures`
    (`id`, `name`, `article`, `level`, `creature_type`, `health_max`,
     `attack_strength`, `defense_strength`, `casting_strength`, `target_defense`,
     `action_timer`, `behavior_script`, `is_aggressive`, `can_cast`, `can_maneuver`,
     `is_undead`, `body_type`, `experience_value`, `silver_min`, `silver_max`,
     `loot_table_id`, `skin_noun`, `skin_item_id`, `description`, `death_message`)
VALUES

-- Cobra — Wehnimer's Landing / The Graveyard
-- Wiki: HP 51, bite 68 AS, DS 37, bolt 23, UDF 21, TD 12, ASG 5N natural
-- No treasure. Skin: a cobra skin. venom ability.
(9328, 'cobra', 'a', 4, 'normal', 51,
 68, 37, 0, 12,
 8, NULL, 1, 0, 0,
 0, 'ophidian', 176, 0, 0,
 NULL, 'cobra skin', NULL,
 'The long, thin, varicolored cobra slithers quickly through the graveyard, its hood spreading wide as it senses a target nearby.  Its scales catch what little light reaches this place and throw back a brief, cold glitter.  The venom sacs behind its fangs are visibly swollen.',
 'coils loosely and goes still.'),

-- Ridge orc — Wehnimer's Landing / Dead Plateau (Trollfang)
-- Wiki: HP 80, handaxe 84 AS, DS 78, bolt 23, UDF 103, TD 12, ASG 5
-- Coins/gems/magic/boxes yes. Skin: an orc ear.
(9329, 'ridge orc', 'a', 4, 'normal', 80,
 84, 78, 0, 12,
 9, NULL, 1, 0, 0,
 0, 'humanoid', 176, 8, 32,
 415, 'orc ear', NULL,
 'Massive and sullen looking, the ridge orc glares and grimaces at all who dare to approach.  It stands half a head taller than most orcs and its shoulders are so broad they seem architectural.  The handaxe it carries is barely a handaxe by size — the grip alone is as wide as a forearm.',
 'crashes dead to the ground.'),

-- Cobra — Solhaven / Vornavian Coast
-- Same wiki stats as graveyard variant; separate zone entry.
(10123, 'cobra', 'a', 4, 'normal', 51,
 68, 37, 0, 12,
 8, NULL, 1, 0, 0,
 0, 'ophidian', 176, 0, 0,
 NULL, 'cobra skin', NULL,
 'The long, thin, varicolored cobra moves with fluid precision along the coastal rock, its hood spreading wide at your approach.  Salt spray has darkened the leading edge of its scales.  The venom sacs behind its fangs are visibly swollen — a detail worth noting at close range.',
 'coils loosely and goes still.'),

-- Whiptail — Solhaven / Vornavian Coast
-- Wiki: HP 50, impale+pincer 65 AS, DS 29, bolt 26, TD 12, ASG 12N natural
-- Web ability (immobilize). No treasure. Skin: a whiptail stinger.
-- can_maneuver=1 (web is a special maneuver-type effect)
(10124, 'whiptail', 'a', 4, 'normal', 50,
 65, 29, 0, 12,
 8, NULL, 1, 0, 1,
 0, 'arachnid', 176, 0, 0,
 NULL, 'whiptail stinger', NULL,
 'The whiptail''s body is squat and heavily plated, its natural armor shrugging off most blows with an ugly grinding sound.  The tail that gives it its name is thin, whip-fast, and tipped with a barbed stinger it uses to immobilize prey before the pincers close.  It scuttles sideways with surprising speed for something built like a small fortress.',
 'goes still, legs folding beneath its plated body.');

-- ────────────────────────────────────────────────────────────
-- VERIFICATION
-- SELECT id, name, level, experience_value, silver_min, skin_noun
--   FROM creatures
--   WHERE id IN (9328, 9329, 10123, 10124)
--   ORDER BY id;
--
-- Expected: all level 4, xp=176
-- is_undead=0 on all four
-- can_maneuver=1 only on whiptail (10124)
-- silver>0 only on ridge orc (9329): 8-32
-- ────────────────────────────────────────────────────────────
