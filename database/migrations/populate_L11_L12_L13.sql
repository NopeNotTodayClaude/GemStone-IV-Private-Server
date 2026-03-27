-- ============================================================
-- Migration: populate_L11_L12_L13.sql
-- Levels 11, 12, and 13 new creatures.
--
-- NEW CREATURES:
--   10439  shelfae chieftain   solhaven / Coastal Cliffs + marshtown   L11
--   10440  wall guardian       the_citadel / Thurfel's Keep            L11
--   9339   crystal golem       wehnimers_landing / Old Mine Road       L12
--   10441  deranged sentry     the_citadel / Thurfel's Keep deep       L13
--   10442  gnoll thief         the_krag_slopes / Zeltoph               L13
--   10443  tawny brindlecat    the_yegharren_plains / Yegharren Plains L13
--
-- NEW ZONES:
--   zone_id 87  the_yegharren_plains  (level range updated)
--
-- ALREADY EXIST (no action):
--   L11: Neartofar orc (neartofar_forest)
--   L12: dark orc (yanders_farm)
--   L13: great stag (yanders_farm), Gnoil thief (wehnimers_landing),
--        Darkwoode (wehnimers_landing), plumed cockatrice (neartofar_forest),
--        rotting farmhand (lunule_weald)
--
-- Sources: gswiki.play.net verified for all wiki-sourced creatures.
-- Run after populate_L2_L4_guessed_and_L6_L10.sql
-- ============================================================

USE gemstone_dev;

-- ── ZONE LEVEL RANGE UPDATE ───────────────────────────────────────────
UPDATE `zones` SET level_min = 11, level_max = 16 WHERE id = 87; -- the_yegharren_plains

-- ── LOOT TABLES ───────────────────────────────────────────────────────
-- XP L11=1058, L12=1296, L13=1508
-- shelfae chieftain: boxes yes
-- wall guardian: boxes yes
-- crystal golem: boxes yes
-- deranged sentry: boxes yes
-- gnoll thief: boxes yes
-- tawny brindlecat: no coins, no boxes — NULL table
INSERT IGNORE INTO `loot_tables` (`id`, `name`) VALUES
    (433, 'Shelfae chieftain drops'),
    (434, 'Wall guardian drops'),
    (435, 'Crystal golem drops'),
    (436, 'Deranged sentry drops'),
    (437, 'Gnoll thief drops');

-- ── LOOT TABLE ENTRIES ────────────────────────────────────────────────
-- item 1032=wooden coffer, 1035=dented iron box, 1082=ornate brass box
-- Entry IDs start at 6330 (safe gap after L6-L10 batch ended at 6325)
-- Scale L11-L13: ~30/25/15% drop rates
INSERT IGNORE INTO `loot_table_entries`
    (`id`, `loot_table_id`, `item_id`, `drop_chance`, `quantity_min`, `quantity_max`)
VALUES
    -- Shelfae chieftain (433) L11
    (6330, 433, 1032, 30.00, 1, 1),
    (6331, 433, 1035, 25.00, 1, 1),
    (6332, 433, 1082, 15.00, 1, 1),
    -- Wall guardian (434) L11
    (6333, 434, 1032, 30.00, 1, 1),
    (6334, 434, 1035, 25.00, 1, 1),
    (6335, 434, 1082, 15.00, 1, 1),
    -- Crystal golem (435) L12
    (6336, 435, 1032, 30.00, 1, 1),
    (6337, 435, 1035, 25.00, 1, 1),
    (6338, 435, 1082, 15.00, 1, 1),
    -- Deranged sentry (436) L13
    (6339, 436, 1032, 32.00, 1, 1),
    (6340, 436, 1035, 26.00, 1, 1),
    (6341, 436, 1082, 16.00, 1, 1),
    -- Gnoll thief (437) L13
    (6342, 437, 1032, 32.00, 1, 1),
    (6343, 437, 1035, 26.00, 1, 1),
    (6344, 437, 1082, 16.00, 1, 1);

-- ── CREATURES ─────────────────────────────────────────────────────────
-- XP: L11=1058, L12=1296, L13=1508
-- Silver: L11=34-136, L12=38-152, L13=42-168
-- Using INSERT IGNORE to be re-run safe.
INSERT IGNORE INTO `creatures`
    (`id`, `name`, `article`, `level`, `creature_type`, `health_max`,
     `attack_strength`, `defense_strength`, `casting_strength`, `target_defense`,
     `action_timer`, `behavior_script`, `is_aggressive`, `can_cast`, `can_maneuver`,
     `is_undead`, `body_type`, `experience_value`, `silver_min`, `silver_max`,
     `loot_table_id`, `skin_noun`, `skin_item_id`, `description`, `death_message`)
VALUES

-- Shelfae chieftain — solhaven / Coastal Cliffs + marshtown  L11
-- HP 140, halberd/morning star 130 AS, DS 45, bolt 25, TD 33, ASG 11
-- tail_strike + tremors | coins+boxes
(10439, 'shelfae chieftain', 'a', 11, 'normal', 140,
 130, 45, 0, 33,
 10, NULL, 1, 0, 1,
 0, 'hybrid', 1058, 34, 136,
 433, 'chieftain scale', NULL,
 'The shelfae chieftain stands half again the height of the soldiers it commands, its overlapping chitin plates scarred and recoloured by a long history of violence. It carries both a halberd and a morning star with the casual ease of something that has decided not to choose between them. The thick tail it uses as a third strike sweeps low and without warning.',
 'crashes to the ground with a sound that shakes the rock.'),

-- Wall guardian — the_citadel / Thurfel''s Keep  L11
-- HP 140, military pick 100-153 (mid 127) AS, DS 53, bolt 45, UDF 109, TD 33, ASG 16
-- coins+boxes | skin: a guardian finger
(10440, 'wall guardian', 'a', 11, 'normal', 140,
 127, 53, 0, 33,
 10, NULL, 1, 0, 0,
 0, 'biped', 1058, 34, 136,
 434, 'guardian finger', NULL,
 'The wall guardian is enormously broad and wears chain hauberk as though it were a second skin. It carries a military pick with both hands and holds its post with the conviction of something that has been stationed at this tunnel since before anyone currently alive was born. It does not pursue. It does not warn. It simply strikes anything that passes through without authorisation.',
 'drops to one knee, then to the floor.'),

-- Crystal golem — wehnimers_landing / Old Mine Road  L12
-- HP 140, ensnare/pound 134 / stomp 144 AS, DS 112, bolt 60, TD 36, ASG 14N, magical
-- stomp quake | coins+boxes | crumbles
(9339, 'crystal golem', 'a', 12, 'normal', 140,
 144, 112, 0, 36,
 10, NULL, 1, 0, 1,
 0, 'biped', 1296, 38, 152,
 435, 'crystal golem shard', NULL,
 'The crystal golem was created to guard the mine and has been performing this function without interruption for longer than the mine has been worked. Its double-chain natural armour is compressed crystal lattice that catches torchlight and shatters it across the tunnel walls. When its foot comes down with full force, the tremor travels through the stone for twenty feet in every direction.',
 'shatters with a sound like breaking glass and falls still.'),

-- Deranged sentry — the_citadel / Thurfel''s Keep deep  L13
-- HP 160, halberd 114-160 (mid 137) AS, DS 100, bolt 60, UDF 151, TD 40, ASG 11
-- disarm + tackle + trip | coins+boxes
(10441, 'deranged sentry', 'a', 13, 'normal', 160,
 137, 100, 0, 40,
 10, NULL, 1, 0, 1,
 0, 'biped', 1508, 42, 168,
 436, 'sentry badge', NULL,
 'The deranged sentry was a wall guardian once. Whatever happened to its mind has not slowed its halberd. It moves through the deep tunnels in an erratic patrol pattern that covers every approach regardless of logic, and its disarm attempt comes with a reflexive sweep that takes your footing at the same time it takes your weapon.',
 'finally stops, crumpling against the tunnel wall.'),

-- Gnoll thief — the_krag_slopes / Krag Slopes (Zeltoph)  L13
-- HP 160, short sword 162 AS, DS 176, bolt 90, TD 39, ASG 6
-- hurl weapon + steal | coins+boxes
(10442, 'gnoll thief', 'a', 13, 'normal', 160,
 162, 176, 0, 39,
 10, NULL, 1, 0, 1,
 0, 'biped', 1508, 42, 168,
 437, 'gnoll claw', NULL,
 'The gnoll thief operates by a simple philosophy: take everything that can be taken and hurl what cannot. Its defensive skill is genuinely exceptional for something wearing full leather — it moves with the fluid evasion of a creature that has developed the specific art of not being where the weapon arrives. The short sword is a backup. The thrown weapon that precedes it is the opening.',
 'drops and does not rise.'),

-- Tawny brindlecat — the_yegharren_plains  L13
-- HP 120, claw 162 / bite 150 AS, DS 97, bolt 45, TD 39, ASG 8N
-- pounce maneuver | no coins | skin: a brindlecat pelt
(10443, 'tawny brindlecat', 'a', 13, 'normal', 120,
 162, 97, 0, 39,
 9, NULL, 1, 0, 1,
 0, 'quadruped', 1508, 0, 0,
 NULL, 'brindlecat pelt', NULL,
 'The tawny brindlecat moves through the high grass of the Yegharren Plains with the unhurried patience of a predator that knows nothing here is faster than it. Its coat is a deep tawny gold broken by irregular dark brindle stripes that function as near-perfect camouflage in the dry grass. The pounce it delivers from concealment is the first indication most prey gets that the cat was ever there.',
 'slides into the grass and goes still.');

-- ── VERIFICATION ─────────────────────────────────────────────────────
-- SELECT id, name, level, experience_value, silver_min, is_undead,
--        can_maneuver, skin_noun
-- FROM creatures
-- WHERE id IN (10439, 10440, 9339, 10441, 10442, 10443)
-- ORDER BY level, id;
--
-- Expected xp: L11=1058 x2, L12=1296 x1, L13=1508 x3
-- can_maneuver=1: 10439,9339,10441,10442,10443
-- is_undead=0: all six
-- silver=0: 10443 (tawny brindlecat, no coins)
