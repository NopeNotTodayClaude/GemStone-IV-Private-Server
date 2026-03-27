-- ============================================================
-- Migration: populate_L5_missing.sql
-- Bottom-to-top build — Level 5 missing creatures.
--
-- NEW CREATURES:
--   9330  mongrel hobgoblin   wehnimers_landing / Upper Trollfang
--
-- INTENTIONALLY SKIPPED:
--   nasty little gremlin -> Wehntoph — no zone built
--   night golem          -> The Citadel — no zone built
--
-- ALREADY EXIST (no action needed):
--   bobcat          (toadwort,          ID 7005) ✓
--   coyote          (rambling_meadows,  ID 9108) ✓
--   coyote          (wehnimers_landing, ID 9402) ✓
--   dark apparition (glaise_cnoc,       ID 1008) ✓  -- CEMETERY, untouched
--   mist wraith     (glaise_cnoc,       ID 1007) ✓  -- CEMETERY, untouched
--   water witch     (solhaven,          ID 10114) ✓
--   black bear      (tavaalor,          ID 7022) ✓
--   skeleton warrior(tavaalor,          ID 7004) ✓
--
-- Sources: gswiki.play.net/Mongrel_hobgoblin (verified)
-- Run AFTER populate_L4_missing.sql
-- ============================================================

USE gemstone_dev;

-- ────────────────────────────────────────────────────────────
-- LOOT TABLES
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_tables` (`id`, `name`) VALUES
    (416, 'Mongrel hobgoblin drops');

-- ────────────────────────────────────────────────────────────
-- LOOT TABLE ENTRIES
-- item 1032 = wooden coffer, 1035 = dented iron box
-- Entry IDs start at 6260 (safe gap after L4 batch ended at 6251).
-- Level 5 humanoid — slightly better box rates.
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_table_entries`
    (`id`, `loot_table_id`, `item_id`, `drop_chance`, `quantity_min`, `quantity_max`)
VALUES
    (6260, 416, 1032, 22.00, 1, 1),
    (6261, 416, 1035, 15.00, 1, 1),
    (6262, 416, 1082,  5.00, 1, 1);

-- ────────────────────────────────────────────────────────────
-- CREATURES
-- XP level 5 = 260 (per established DB curve)
-- silver: 10-40 for humanoids (level 5 scale)
-- ────────────────────────────────────────────────────────────
INSERT INTO `creatures`
    (`id`, `name`, `article`, `level`, `creature_type`, `health_max`,
     `attack_strength`, `defense_strength`, `casting_strength`, `target_defense`,
     `action_timer`, `behavior_script`, `is_aggressive`, `can_cast`, `can_maneuver`,
     `is_undead`, `body_type`, `experience_value`, `silver_min`, `silver_max`,
     `loot_table_id`, `skin_noun`, `skin_item_id`, `description`, `death_message`)
VALUES

-- Mongrel hobgoblin — Wehnimer's Landing / Upper Trollfang
-- Wiki: HP 80, morning star 99 AS, DS 57, bolt 3, UDF 113, TD 15, ASG 8
-- Coins/gems/magic/boxes yes. Skin: a mongrel hobgoblin snout.
(9330, 'mongrel hobgoblin', 'a', 5, 'normal', 80,
 99, 57, 0, 15,
 9, NULL, 1, 0, 0,
 0, 'humanoid', 260, 10, 40,
 416, 'mongrel hobgoblin snout', NULL,
 'The mongrel hobgoblin is a horribly misshapen beast, with a hideously deformed face.  The large, knotted muscles on her arms betray the creature''s strength, which is capable of rending a man''s limbs right out of their sockets.  Mottled skin with a greenish-yellow hue is splotched with randomly scattered patches of reddish-brown fur.  The dark beady eyes of the hobgoblin glare menacingly, as if crushing the life from someone would somehow make her life more bearable.',
 'crashes to the ground.');

-- ────────────────────────────────────────────────────────────
-- VERIFICATION
-- SELECT id, name, level, experience_value, silver_min, silver_max, skin_noun
--   FROM creatures WHERE id = 9330;
-- Expected: level 5, xp 260, silver 10-40, skin 'mongrel hobgoblin snout'
-- ────────────────────────────────────────────────────────────
