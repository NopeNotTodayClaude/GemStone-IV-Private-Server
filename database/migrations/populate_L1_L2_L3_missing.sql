-- ============================================================
-- Migration: populate_L1_L2_L3_missing.sql
-- Bottom-to-top build — levels 1, 2, and 3.
-- Adds creature DB rows for mobs whose Lua files now exist
-- but had no creatures table entry.
--
-- LEVEL 1 (4 new):
--   10116  black-winged daggerbeak  solhaven / Coastal Cliffs
--   10117  carrion worm             solhaven / Coastal Cliffs
--   10318  carrion worm             icemule_trace / Snowy Forest
--   10319  zombie rolton            icemule_trace / Snowy Forest
--
-- LEVEL 2 (6 new):
--   10118  ghost                    solhaven / Coastal Cliffs
--   10119  pale crab                solhaven / Coastal Cliffs
--   10120  sea nymph                solhaven / Coastal Cliffs
--   10320  lesser frost shade       icemule_trace / Snowy Forest
--   9320   phantom                  wehnimers_landing / Graveyard
--   9321   spotted gak              wehnimers_landing / Trollfang entry
--
-- LEVEL 3 (9 new):
--   9322   hobgoblin                wehnimers_landing / Graveyard + Trollfang
--   9323   cave gnoll               wehnimers_landing / Trollfang entry
--   9324   striped gak              wehnimers_landing / Trollfang entry
--   9325   troglodyte               wehnimers_landing / Trollfang entry
--   9326   velnalin                 wehnimers_landing / Trollfang entry
--   9327   mountain snowcat         wehnimers_landing / Trollfang entry
--   9112   striped relnak           rambling_meadows
--   10321  greater ice spider       icemule_trace / Glatoph lower
--   10322  white vysan              icemule_trace / Snowy Forest
--
-- INTENTIONALLY SKIPPED (no zone built yet):
--   mountain rolton   -> Old Mine Road
--   slimy little grub -> Wehntoph
--   big ugly kobold   -> Kobold Village
--   coconut crab      -> Rocky Shoals (no wiki stats)
--   bresnahanini rolton -> Outlands
--   cave nipper       -> Old Mine Road (no wiki stats)
--   kobold shepherd   -> Kobold Village
--   spotted velnalin  -> no zone built
--
-- Run AFTER all prior migrations.
-- All stats sourced from gswiki.play.net and verified before writing.
-- ============================================================

USE gemstone_dev;

-- ────────────────────────────────────────────────────────────
-- LOOT TABLES
-- Starting at 406 (max existing = 405 from prior migration).
-- Only creatures that drop boxes get a loot table entry.
-- Animals/non-humanoids with no box drops are NULL loot_table_id.
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_tables` (`id`, `name`) VALUES
    -- Level 2
    (406, 'Ghost drops'),
    (407, 'Pale crab drops'),
    (408, 'Sea nymph drops'),
    (409, 'Lesser frost shade drops'),
    (410, 'Phantom drops'),
    -- Level 3
    (412, 'Hobgoblin drops'),
    (413, 'Cave gnoll drops'),
    (414, 'Troglodyte drops');
-- spotted_gak, striped_gak, velnalin, mountain_snowcat,
-- striped_relnak, greater_ice_spider, white_vysan: no loot tables (skin only)

-- ────────────────────────────────────────────────────────────
-- LOOT TABLE ENTRIES
-- item 1032 = wooden coffer, 1035 = dented iron box, 1082 = ornate brass box
-- Entry IDs start at 6230 (prior batch ended at 6229).
-- Level 2: very light box rates (entry content).
-- Level 3: slightly heavier — level 3 humanoids carry better loot.
-- ────────────────────────────────────────────────────────────
INSERT IGNORE INTO `loot_table_entries`
    (`id`, `loot_table_id`, `item_id`, `drop_chance`, `quantity_min`, `quantity_max`)
VALUES
    -- Ghost (406)
    (6230, 406, 1032, 18.00, 1, 1),
    (6231, 406, 1035, 10.00, 1, 1),
    -- Pale crab (407)
    (6232, 407, 1032, 18.00, 1, 1),
    (6233, 407, 1035, 10.00, 1, 1),
    -- Sea nymph (408)
    (6234, 408, 1032, 18.00, 1, 1),
    (6235, 408, 1035, 12.00, 1, 1),
    -- Lesser frost shade (409)
    (6236, 409, 1032, 18.00, 1, 1),
    (6237, 409, 1035, 10.00, 1, 1),
    -- Phantom (410)
    (6238, 410, 1032, 18.00, 1, 1),
    (6239, 410, 1035, 10.00, 1, 1),
    -- Hobgoblin (412) — level 3 humanoid, slightly better
    (6240, 412, 1032, 20.00, 1, 1),
    (6241, 412, 1035, 15.00, 1, 1),
    -- Cave gnoll (413)
    (6242, 413, 1032, 20.00, 1, 1),
    (6243, 413, 1035, 15.00, 1, 1),
    -- Troglodyte (414)
    (6244, 414, 1032, 20.00, 1, 1),
    (6245, 414, 1035, 12.00, 1, 1);

-- ────────────────────────────────────────────────────────────
-- CREATURES
-- Column order:
--   id, name, article, level, creature_type, health_max,
--   attack_strength, defense_strength, casting_strength, target_defense,
--   action_timer, behavior_script, is_aggressive, can_cast, can_maneuver,
--   is_undead, body_type, experience_value, silver_min, silver_max,
--   loot_table_id, skin_noun, skin_item_id, description, death_message
--
-- XP values per established DB curve:
--   Level 1 = 20, Level 2 = 56, Level 3 = 108
-- ────────────────────────────────────────────────────────────
INSERT INTO `creatures`
    (`id`, `name`, `article`, `level`, `creature_type`, `health_max`,
     `attack_strength`, `defense_strength`, `casting_strength`, `target_defense`,
     `action_timer`, `behavior_script`, `is_aggressive`, `can_cast`, `can_maneuver`,
     `is_undead`, `body_type`, `experience_value`, `silver_min`, `silver_max`,
     `loot_table_id`, `skin_noun`, `skin_item_id`, `description`, `death_message`)
VALUES

-- ══════════════════════════════════════════════════════════════
-- LEVEL 1
-- ══════════════════════════════════════════════════════════════

(10116, 'black-winged daggerbeak', 'a', 1, 'normal', 28,
 36, 27, 0, 3,   7, NULL, 1, 0, 0,
 0, 'avian', 20, 0, 0,
 NULL, 'daggerbeak wing', NULL,
 'With its naked head resembling that of a vulture and a wingspan of almost three feet, the black-winged daggerbeak gets its name from its wickedly pointed beak and the way it uses it.  Created by a mean-spirited enchanter for the bedevilment of some peasants who had offended him, the daggerbeak survives by stabbing domesticated herd animals with its beak and drinking their blood.',
 'tumbles from the air and hits the ground hard.'),

(10117, 'carrion worm', 'a', 1, 'normal', 28,
 39, 47, 0, 3,   7, NULL, 1, 0, 0,
 0, 'worm', 20, 0, 0,
 NULL, 'worm skin', NULL,
 'The carrion worm eagerly consumes anything dead and anything living that doesn''t put up too much of a fight.  Its long, slimy body tapers to a point at the tail end.  At the business end, several hundred waving cilia force food into the worm''s maw where the food is crushed by rows of short, sharp teeth.',
 'convulses once and goes still.'),

(10318, 'carrion worm', 'a', 1, 'normal', 28,
 39, 47, 0, 3,   7, NULL, 1, 0, 0,
 0, 'worm', 20, 0, 0,
 NULL, 'worm skin', NULL,
 'The carrion worm burrows through the frozen soil of the snowy forest, erupting where the scent of blood reaches it.  Its pale, slimy body tapers to a point at the tail end, and at the business end rows of short, sharp teeth gnash continuously.  Cold has done nothing to blunt its appetite.',
 'convulses once and goes still.'),

(10319, 'zombie rolton', 'a', 1, 'normal', 28,
 32, 7, 0, 3,   8, NULL, 1, 0, 0,
 1, 'quadruped', 20, 0, 0,
 NULL, 'rotting rolton pelt', NULL,
 'An undead version of the domesticated breed, these were one of the earlier attempts by the Council of Twelve to create undead.  The zombie rolton''s dirty, matted pelt hangs loosely from a bloated carcass, and its long, curved incisors gnash with mindless aggression.',
 'bleats once, wetly, and collapses.'),

-- ══════════════════════════════════════════════════════════════
-- LEVEL 2
-- ══════════════════════════════════════════════════════════════

-- Ghost — Solhaven Coastal Cliffs | non-corporeal undead | no skin
(10118, 'ghost', 'a', 2, 'normal', 51,
 58, -2, 0, 6,   8, NULL, 1, 0, 0,
 1, 'biped', 56, 4, 16,
 406, '', NULL,
 'Found near graveyards and other resting places of the dead, the ghost presents itself as a pale reflection of what it once was in life.  Its translucent form flickers at the edges, and its eyes — the only truly solid-seeming part of it — fix upon you with cold recognition.',
 'fades with a sigh and is gone.'),

-- Pale crab — Solhaven Coastal Cliffs | claw+ensnare | skin: pale crab claw
(10119, 'pale crab', 'a', 2, 'normal', 36,
 43, 27, 0, 6,   8, NULL, 1, 0, 0,
 0, 'crustacean', 56, 4, 16,
 407, 'pale crab claw', NULL,
 'Bleached to a sickly off-white by years among the tide pools, the pale crab is not particularly large but compensates with powerful, asymmetrical claws.  The larger of the two is capable of pinning a limb entirely, while the smaller delivers a sawing slash.  It moves sideways with unsettling speed.',
 'curls up and goes still.'),

-- Sea nymph — Solhaven Coastal Cliffs | caster CS 10 | skin: sea nymph lock
(10120, 'sea nymph', 'a', 2, 'normal', 44,
 50, 33, 10, 6,   8, NULL, 1, 1, 0,
 0, 'biped', 56, 4, 16,
 408, 'sea nymph lock', NULL,
 'The sea nymph''s voice carries clearly over the sound of the surf, and there is something in it that makes the listener want to stop and listen further.  Her pale blue-green skin and salt-tangled hair give her the look of something that crawled out of the ocean and elected to stay.',
 'crumples to the shoreline rocks.'),

-- Lesser frost shade — Icemule Snowy Forest | non-corporeal undead | caster CS 14
(10320, 'lesser frost shade', 'a', 2, 'normal', 44,
 43, 3, 14, 6,   8, NULL, 1, 1, 0,
 1, 'biped', 56, 4, 16,
 409, '', NULL,
 'Barely distinguishable from the snow and mist around it, the lesser frost shade is a dim silhouette of cold blue-white light.  The temperature drops noticeably as it drifts closer.  It wields a handaxe of pure ice that looks real enough and swings like it.',
 'dissolves into a brief flurry of snow and is gone.'),

-- Phantom — Wehnimer Graveyard | non-corporeal undead | bolt caster | no skin
(9320, 'phantom', 'a', 2, 'normal', 42,
 35, -23, 0, 6,   8, NULL, 1, 1, 0,
 1, 'biped', 56, 4, 16,
 410, '', NULL,
 'The phantom drifts several inches above the earth, an indistinct shape of pale light and cold air that occasionally resolves into something almost human before losing cohesion again.  The Minor Shock it channels comes less from any training than from raw spiritual agitation.',
 'scatters into a cold grey mist.'),

-- Spotted gak — Wehnimer Trollfang entry | no coins | skin: gak hide
(9321, 'spotted gak', 'a', 2, 'normal', 70,
 48, 26, 0, 6,   8, NULL, 1, 0, 1,
 0, 'quadruped', 56, 0, 0,
 NULL, 'gak hide', NULL,
 'The spotted gak is a big, ugly beast with a heavy spotted brown pelt.  A marked odor of dung and musk precedes it by some distance, and its thick hide and powerful hindquarters make it look like something that decided being a bull wasn''t ambitious enough.',
 'crashes down with a grunt and does not rise.'),

-- ══════════════════════════════════════════════════════════════
-- LEVEL 3
-- ══════════════════════════════════════════════════════════════

-- Hobgoblin — Wehnimer Graveyard + Trollfang entry | coins/boxes | skin: hobgoblin ear
(9322, 'hobgoblin', 'a', 3, 'normal', 60,
 68, 15, 0, 9,   9, NULL, 1, 0, 0,
 0, 'humanoid', 108, 6, 24,
 412, 'hobgoblin ear', NULL,
 'Larger and meaner than a goblin by an order of magnitude, the hobgoblin compensates for its relative lack of cunning with brute aggression and an oversized weapon it swings with more enthusiasm than skill.  Lumpy grey-green skin and heavy brow ridges give it a permanently furious expression that its behavior tends to justify.',
 'pitches forward, dead.'),

-- Cave gnoll — Wehnimer Trollfang entry | coins/boxes | skin: cave gnoll hide
(9323, 'cave gnoll', 'a', 3, 'normal', 60,
 68, 28, 0, 9,   9, NULL, 1, 0, 0,
 0, 'humanoid', 108, 6, 24,
 413, 'cave gnoll hide', NULL,
 'Hyena-headed and hump-backed, the cave gnoll has adapted to dim tunnels and cramped spaces without losing any of its aggression.  Its pale, watery eyes catch available light and its scimitar — too large for the cramped spaces it apparently prefers — it swings with practiced efficiency anyway.',
 'slumps to the ground.'),

-- Striped gak — Wehnimer Trollfang entry | no coins | skin: gak hide
(9324, 'striped gak', 'a', 3, 'normal', 80,
 61, 40, 0, 9,   8, NULL, 1, 0, 1,
 0, 'quadruped', 108, 0, 0,
 NULL, 'gak hide', NULL,
 'Where the spotted gak is merely large and hostile, the striped gak seems to have channeled its additional age into additional meanness.  Bold dark stripes cut across its heavy brown pelt and its horns are longer and more curved than its spotted kin.  It paws the earth, lowers its head, and commits.',
 'crashes down heavily and does not rise.'),

-- Troglodyte — Wehnimer Trollfang entry | coins/boxes | skin: troglodyte hide
(9325, 'troglodyte', 'a', 3, 'normal', 60,
 68, 26, 0, 9,   9, NULL, 1, 0, 0,
 0, 'humanoid', 108, 6, 24,
 414, 'troglodyte hide', NULL,
 'Hunched and cave-pale, the troglodyte''s long arms drag the knuckles of one hand along the ground while the other grips a heavy cudgel with practiced ease.  Its wide, lipless mouth opens and closes rhythmically, and the musk it produces is an assault in itself.',
 'collapses with a wet thud.'),

-- Velnalin — Wehnimer Trollfang entry | no coins | skin: velnalin pelt
(9326, 'velnalin', 'a', 3, 'normal', 44,
 71, 32, 0, 9,   8, NULL, 1, 0, 1,
 0, 'quadruped', 108, 0, 0,
 NULL, 'velnalin pelt', NULL,
 'The velnalin resembles a large, athletic deer — until it opens its mouth and reveals a set of sharp, interlocking teeth completely inappropriate for an herbivore.  It watches you with calm, dark eyes, then charges without warning at a speed its build should not permit.',
 'crashes to the ground.'),

-- Mountain snowcat — Wehnimer Trollfang entry | no coins | skin: snowcat pelt
(9327, 'mountain snowcat', 'a', 3, 'normal', 44,
 59, 26, 0, 9,   8, NULL, 1, 0, 1,
 0, 'quadruped', 108, 0, 0,
 NULL, 'snowcat pelt', NULL,
 'Compact and powerful beneath a thick cream-and-grey coat, the mountain snowcat moves through the scrub in almost total silence.  Its paws are oversized for its body — natural snowshoes — and its eyes are pale gold, patient, and entirely predatory.',
 'slides to the ground and goes still.'),

-- Striped relnak — Rambling Meadows | no coins | skin: relnak hide
(9112, 'striped relnak', 'a', 3, 'normal', 42,
 71, 34, 0, 9,   8, NULL, 1, 0, 1,
 0, 'quadruped', 108, 0, 0,
 NULL, 'relnak hide', NULL,
 'The striped relnak is a low-slung reptilian quadruped marked with vivid bands of dark brown on tawny gold.  Its short legs are deceptive — when it charges, it accelerates with startling speed, and the stomp it delivers with its broad forefeet is the hit that usually breaks things.',
 'crashes to the ground, limbs splaying.'),

-- Greater ice spider — Icemule Glatoph lower | no coins | venom+web | skin: spider leg
(10321, 'greater ice spider', 'a', 3, 'normal', 44,
 71, 55, 0, 9,   8, NULL, 1, 0, 1,
 0, 'arachnid', 108, 0, 0,
 NULL, 'spider leg', NULL,
 'The greater ice spider''s body is a translucent blue-white, and the ice crystals that form along its legs give it an almost beautiful appearance at a distance.  Closer inspection reveals the stinger coiled beneath its abdomen and the webs it trails — not silk, but frozen filament strong enough to pin a limb.',
 'curls in on itself, legs folding inward.'),

-- White vysan — Icemule Snowy Forest | no coins | skin: white vysan pelt
(10322, 'white vysan', 'a', 3, 'normal', 50,
 54, 11, 0, 9,   8, NULL, 1, 0, 0,
 0, 'biped', 108, 0, 0,
 NULL, 'white vysan pelt', NULL,
 'The white vysan stands roughly waist-high on broad, flat feet, its shaggy white coat nearly invisible against the snow.  It has no neck to speak of — the head seems to emerge directly from the torso — and its wide, pawing arms end in thick-fingered hands that grip with surprising force.',
 'slumps into the snow.');

-- ────────────────────────────────────────────────────────────
-- VERIFICATION QUERIES
-- Run these after import to confirm correctness:
--
-- SELECT id, name, level, is_undead, can_cast, experience_value, skin_noun
--   FROM creatures
--   WHERE id IN (
--     10116,10117,10118,10119,10120,
--     10318,10319,10320,10321,10322,
--     9320,9321,9322,9323,9324,9325,9326,9327,9112
--   )
--   ORDER BY level, id;
--
-- Expected totals: 4 level-1 (xp=20), 6 level-2 (xp=56), 9 level-3 (xp=108)
-- is_undead=1: 10319 (zombie rolton), 10118 (ghost), 10320 (frost shade), 9320 (phantom)
-- can_cast=1:  10120 (sea nymph), 10320 (frost shade), 9320 (phantom)
-- ────────────────────────────────────────────────────────────
