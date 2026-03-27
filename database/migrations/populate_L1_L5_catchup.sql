-- ============================================================
-- Migration: populate_L1_L5_catchup.sql
-- Catch-up build — all previously-skipped L1-L5 creatures
-- that became buildable once zone folders were created,
-- PLUS zone registration for all new zone script folders.
--
-- NEW ZONES REGISTERED (or verified existing):
--   zone_id 18   graendlor_pasture   (Kobold Village / west Wehnimer's)
--   zone_id 37   the_cairnfang       (Cairnfang Forest)
--   zone_id 94   the_outlands        (Vornavis Outlands)
--   zone_id 102  wehntoph            (Twin Canyons)
--   zone_id 141  the_citadel         (River Tunnels)
--   zone_id 205  rocky_shoals        (Black Stone Beach)
--
-- NEW CREATURES:
--   9331   mountain rolton       wehnimers_landing / Mine Road       L1
--   9332   big ugly kobold       wehnimers_landing / Kobold Mines    L2
--   9333   kobold shepherd       wehnimers_landing / Kobold Mines    L3
--   10411  slimy little grub     wehntoph / Twin Canyons             L1
--   10412  Bresnahanini rolton   the_outlands / Vornavis Holdings    L3
--   10413  nasty little gremlin  wehntoph / Twin Canyons             L5
--   10414  night golem           the_citadel / River Tunnels         L5
--
-- STILL SKIPPED (genuinely no wiki stats available):
--   black urgh       (yanders_farm)  - wiki page blank
--   spotted velnalin (yanders_farm)  - wiki page blank
--   coconut crab     (rocky_shoals)  - wiki page blank
--   cave nipper      (old_mine_road) - wiki page blank
--
-- Run AFTER populate_L1_L2_L3_missing.sql, populate_L4_missing.sql,
-- and populate_L5_missing.sql
-- ============================================================

USE gemstone_dev;

-- ────────────────────────────────────────────────────────────
-- UPDATE ZONES TABLE — set accurate level ranges for new zones
-- All were defaulted to 1-100 in the initial DB seed.
-- ────────────────────────────────────────────────────────────
UPDATE `zones` SET `level_min` = 1,  `level_max` = 5  WHERE `id` = 18;   -- graendlor_pasture
UPDATE `zones` SET `level_min` = 1,  `level_max` = 10 WHERE `id` = 37;   -- the_cairnfang
UPDATE `zones` SET `level_min` = 1,  `level_max` = 6  WHERE `id` = 94;   -- the_outlands
UPDATE `zones` SET `level_min` = 1,  `level_max` = 8  WHERE `id` = 102;  -- wehntoph
UPDATE `zones` SET `level_min` = 1,  `level_max` = 8  WHERE `id` = 141;  -- the_citadel
UPDATE `zones` SET `level_min` = 1,  `level_max` = 5  WHERE `id` = 205;  -- rocky_shoals

-- ────────────────────────────────────────────────────────────
-- LOOT TABLES
-- Only creatures that drop boxes need a table.
-- mountain rolton, slimy grub, bresnahanini rolton: no coins — NULL table
-- big ugly kobold, kobold shepherd, nasty gremlin, night golem: coins + boxes
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_tables` (`id`, `name`) VALUES
    (417, 'Big ugly kobold drops'),
    (418, 'Kobold shepherd drops'),
    (419, 'Nasty little gremlin drops'),
    (420, 'Night golem drops');

-- ────────────────────────────────────────────────────────────
-- LOOT TABLE ENTRIES
-- item 1032 = wooden coffer, 1035 = dented iron box, 1082 = ornate brass box
-- Entry IDs start at 6270 (safe gap after L5 batch ended at 6262).
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_table_entries`
    (`id`, `loot_table_id`, `item_id`, `drop_chance`, `quantity_min`, `quantity_max`)
VALUES
    -- Big ugly kobold (417) — level 2, light boxes
    (6270, 417, 1032, 18.00, 1, 1),
    (6271, 417, 1035, 10.00, 1, 1),
    -- Kobold shepherd (418) — level 3, caster so slightly better
    (6272, 418, 1032, 20.00, 1, 1),
    (6273, 418, 1035, 15.00, 1, 1),
    (6274, 418, 1082,  5.00, 1, 1),
    -- Nasty little gremlin (419) — level 5
    (6275, 419, 1032, 22.00, 1, 1),
    (6276, 419, 1035, 15.00, 1, 1),
    (6277, 419, 1082,  5.00, 1, 1),
    -- Night golem (420) — level 5, construct, good drops
    (6278, 420, 1032, 22.00, 1, 1),
    (6279, 420, 1035, 18.00, 1, 1),
    (6280, 420, 1082,  8.00, 1, 1);

-- ────────────────────────────────────────────────────────────
-- CREATURES
-- Column order:
--   id, name, article, level, creature_type, health_max,
--   attack_strength, defense_strength, casting_strength, target_defense,
--   action_timer, behavior_script, is_aggressive, can_cast, can_maneuver,
--   is_undead, body_type, experience_value, silver_min, silver_max,
--   loot_table_id, skin_noun, skin_item_id, description, death_message
--
-- XP curve: L1=20, L2=56, L3=108, L5=260
-- ────────────────────────────────────────────────────────────
INSERT INTO `creatures`
    (`id`, `name`, `article`, `level`, `creature_type`, `health_max`,
     `attack_strength`, `defense_strength`, `casting_strength`, `target_defense`,
     `action_timer`, `behavior_script`, `is_aggressive`, `can_cast`, `can_maneuver`,
     `is_undead`, `body_type`, `experience_value`, `silver_min`, `silver_max`,
     `loot_table_id`, `skin_noun`, `skin_item_id`, `description`, `death_message`)
VALUES

-- ── Level 1 ───────────────────────────────────────────────

-- Mountain rolton — wehnimers_landing Mine Road area
-- Wiki: HP 28, bite 36 AS, DS 28, bolt 5, ASG 1N, TD ~3. No treasure. Skin: rolton eye.
(9331, 'mountain rolton', 'a', 1, 'normal', 28,
 36, 28, 0, 3,
 8, NULL, 1, 0, 0,
 0, 'quadruped', 20, 0, 0,
 NULL, 'rolton eye', NULL,
 'This is obviously a prime example of the beast of legend, the fiend of song and tale.  The rolton is covered with a dirty, matted, disgusting-looking grey pelt that might once have been white and is still abysmally smelly.  As the animal bleats at you, it is then you get a view of the maw of death, with its long, curved incisors that gnash and gnaw.',
 'bleats once and collapses.'),

-- Slimy little grub — wehntoph Twin Canyons
-- Wiki: HP 28, stinger 47 AS, DS 22-56 (mid 39), bolt 25, ASG 1N, TD 3. No treasure. No skin.
(10411, 'slimy little grub', 'a', 1, 'normal', 28,
 47, 39, 0, 3,
 7, NULL, 1, 0, 0,
 0, 'worm', 20, 0, 0,
 NULL, '', NULL,
 'The little grub is a small yellowish white creature little more than six inches long.  It is covered in a sickly green slime that leaves a trail behind it.  Somehow, despite being nearly featureless, it manages to convey a sense of singular malevolent intent.',
 'twitches once and goes very still.'),

-- ── Level 2 ───────────────────────────────────────────────

-- Big ugly kobold — wehnimers_landing Kobold Mines
-- Wiki: HP 50, short sword 36-62 AS (mid 49), DS 23-86 (mid 55), bolt 23, ASG 1N, TD 6
-- Coins/gems/boxes yes. Skin: kobold skin.
(9332, 'big ugly kobold', 'a', 2, 'normal', 50,
 49, 55, 0, 6,
 8, NULL, 1, 0, 0,
 0, 'biped', 56, 4, 16,
 417, 'kobold skin', NULL,
 'Larger and considerably uglier than the standard kobold, the big ugly kobold makes up for its lack of subtlety with raw aggression.  Its scales are thicker and more irregular, its teeth more prominent, and its expression more thoroughly hostile.  It carries a short sword with the confidence of something that has been in a great many fights and survived most of them.',
 'falls face-first into the mine floor.'),

-- ── Level 3 ───────────────────────────────────────────────

-- Kobold shepherd — wehnimers_landing Kobold Mines (deeper sublevels)
-- Wiki: HP 51, quarterstaff 50 AS, bolt spells 30 AS, CS 35 (Mana Disruption)
-- DS 57 melee, bolt DS 54, UDF 57, ASG 2 robes, TD 9
-- can_cast=1. Coins/gems/boxes yes. Skin: kobold shepherd crook.
(9333, 'kobold shepherd', 'a', 3, 'normal', 51,
 50, 57, 35, 9,
 9, NULL, 1, 1, 0,
 0, 'biped', 108, 6, 24,
 418, 'kobold shepherd crook', NULL,
 'The kobold shepherd is distinguished from its kin by the long, gnarled quarterstaff it carries and the tattered robes it wears — both signs of status in the mine''s hierarchy.  It herds the lesser kobolds with the staff in one hand and casually lobbing bolts of electrical energy with the other.  This casual mastery of two very different forms of violence is, in its way, impressive.',
 'crumples to the mine floor, staff clattering away.'),

-- Bresnahanini rolton — the_outlands Vornavis Holdings
-- Wiki: HP 44, charge 70/bite 60 AS, DS 44, bolt 17, UDF 75, ASG 5N, TD 9. No treasure. Skin: rolton eye.
(10412, 'Bresnahanini rolton', 'a', 3, 'normal', 44,
 70, 44, 0, 9,
 8, NULL, 1, 0, 1,
 0, 'quadruped', 108, 0, 0,
 NULL, 'rolton eye', NULL,
 'The Bresnahanini rolton is a prime example of the breed favoured by the Vornavian farmsteads — which is to say, it is filthy, aggressive, and in possession of incisors that would look more appropriate on something predatory.  Its matted grey-white pelt smells powerfully of wet wool and worse, and its hooves are cracked and stained with the earth of the Outlands.',
 'crashes down with a final, indignant bleat.'),

-- ── Level 5 ───────────────────────────────────────────────

-- Nasty little gremlin — wehntoph Twin Canyons
-- Wiki: HP 80, dagger 95 AS, DS 22-91 (mid 57), bolt 30, UDF 96, ASG 1N, TD 10-11 (using 15 L5 std)
-- Coins/gems/boxes yes. No skin. steal_item ability.
(10413, 'nasty little gremlin', 'a', 5, 'normal', 80,
 95, 57, 0, 15,
 8, NULL, 1, 0, 1,
 0, 'biped', 260, 10, 40,
 419, '', NULL,
 'The little gremlin is a small furless creature with beady little eyes and sharp teeth that have been filed into triangular points.  Its eyes are a vivid red, and its oversized ears are scarred from countless fights.  It carries a dagger in one clawed hand and something it just stole in the other, and it darts from shadow to shadow with manic, infuriating speed.',
 'tumbles off its perch and lands hard.'),

-- Night golem — the_citadel River Tunnels
-- Wiki: HP 65, ensnare 96/pound 86 AS, DS 11-72 (mid 42), bolt 5, UDF 77-117 (mid 97)
-- ASG 12N, TD 15 elemental (no spiritual). can_maneuver=1 (ensnare).
-- Coins/gems/boxes yes. Skin: night golem finger. crumbles=1 (golem).
(10414, 'night golem', 'a', 5, 'normal', 65,
 96, 42, 0, 15,
 9, NULL, 1, 0, 1,
 0, 'biped', 260, 10, 40,
 420, 'night golem finger', NULL,
 'Formed by the alchemists of the Citadel in their service to the Council of Twelve, these 4-foot tall golems appear to be sculpted of pure shadow.  Approximately man-shaped but with proportions subtly wrong, they move without sound and radiate a cold that has nothing to do with temperature.  Their construction means that lesser injuries simply close and are forgotten — only sustained damage finally brings them down.',
 'shudders, fractures, and crumbles into a pile of dark mineral fragments.');

-- ────────────────────────────────────────────────────────────
-- VERIFICATION
-- SELECT id, name, level, experience_value, silver_min, skin_noun
--   FROM creatures
--   WHERE id IN (9331,9332,9333,10411,10412,10413,10414)
--   ORDER BY level, id;
--
-- Expected levels: 9331=1, 10411=1, 9332=2, 9333=3, 10412=3, 10413=5, 10414=5
-- can_cast=1 on: 9333 (kobold shepherd)
-- can_maneuver=1 on: 10412 (rolton charge), 10413 (gremlin steal), 10414 (golem ensnare)
-- ────────────────────────────────────────────────────────────
