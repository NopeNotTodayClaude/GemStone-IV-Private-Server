-- =============================================================================
-- GemStone IV Private Server — Reference Data Seeds
-- Run AFTER gemstone_schema.sql
--
-- Run with:
--   mysql -u root -p gemstone_dev < database/seeds/gemstone_seed.sql
-- =============================================================================

USE gemstone_dev;

-- =============================================================================
-- RACES
-- =============================================================================

INSERT INTO races (id, name, description) VALUES
(1,  'Human',         'Adaptable and ambitious, humans thrive in any role.'),
(2,  'Elf',           'Graceful and long-lived, masters of magic and archery.'),
(3,  'Dark Elf',      'Mysterious and cunning, dwellers of shadow.'),
(4,  'Half-Elf',      'Born of two worlds, blending human grit with elven grace.'),
(5,  'Dwarf',         'Stout and stubborn, master craftsmen and fierce warriors.'),
(6,  'Halfling',      'Small but quick-witted, natural rogues and survivalists.'),
(7,  'Giantman',      'Towering and powerful, unmatched in raw strength.'),
(8,  'Forest Gnome',  'Clever tinkerers at home in the wild, natural mages.'),
(9,  'Burghal Gnome', 'Urban gnomes with sharp minds and nimble fingers.'),
(10, 'Sylvankind',    'Woodland elves deeply connected to nature.'),
(11, 'Aelotoi',       'Winged refugees from another realm, empathic and agile.'),
(12, 'Erithian',      'Disciplined scholars from the eastern continent.'),
(13, 'Half-Krolvin',  'Hardy half-breeds of humans and seafaring Krolvin.')
ON DUPLICATE KEY UPDATE name=VALUES(name), description=VALUES(description);

-- =============================================================================
-- PROFESSIONS
-- =============================================================================

INSERT INTO professions (id, name, profession_type, description, hp_per_level, mana_per_level) VALUES
(1,  'Warrior',  'square', 'Masters of all weapons and armor. Pure melee power.',              15, 0),
(2,  'Rogue',    'square', 'Stealthy and cunning. Locks, traps, ambush, dual-wield.',          12, 0),
(3,  'Wizard',   'pure',   'Devastating elemental magic. The classic arcane caster.',           6, 4),
(4,  'Cleric',   'pure',   'Divine power. Healing, protection, and spiritual might.',           8, 3),
(5,  'Empath',   'pure',   'Healers who absorb wounds. Essential support class.',               7, 3),
(6,  'Sorcerer', 'pure',   'Dark magic blending elemental and spiritual forces.',               7, 3),
(7,  'Ranger',   'semi',   'Wilderness expert. Martial skill with nature magic.',              10, 2),
(8,  'Bard',     'semi',   'Loremaster musician. Magic through song and verse.',                9, 2),
(9,  'Paladin',  'semi',   'Holy warrior. Martial prowess with divine magic.',                 12, 2),
(10, 'Monk',     'semi',   'Disciplined martial artist. Inner power through focus.',           11, 2)
ON DUPLICATE KEY UPDATE name=VALUES(name), profession_type=VALUES(profession_type), description=VALUES(description),
    hp_per_level=VALUES(hp_per_level), mana_per_level=VALUES(mana_per_level);

-- =============================================================================
-- SKILLS
-- =============================================================================

INSERT INTO skills (id, name, category) VALUES
(1,  'Two Weapon Combat',            'Combat'),
(2,  'Armor Use',                    'Combat'),
(3,  'Shield Use',                   'Combat'),
(4,  'Combat Maneuvers',             'Combat'),
(5,  'Edged Weapons',                'Combat'),
(6,  'Blunt Weapons',                'Combat'),
(7,  'Two-Handed Weapons',           'Combat'),
(8,  'Ranged Weapons',               'Combat'),
(9,  'Thrown Weapons',               'Combat'),
(10, 'Polearm Weapons',              'Combat'),
(11, 'Brawling',                     'Combat'),
(12, 'Multi Opponent Combat',        'Combat'),
(13, 'Physical Fitness',             'Combat'),
(14, 'Dodging',                      'Combat'),
(15, 'Arcane Symbols',               'Magic'),
(16, 'Magic Item Use',               'Magic'),
(17, 'Spell Aiming',                 'Magic'),
(18, 'Harness Power',                'Magic'),
(19, 'Elemental Mana Control',       'Magic'),
(20, 'Spirit Mana Control',          'Magic'),
(21, 'Mental Mana Control',          'Magic'),
(22, 'Spell Research',               'Magic'),
(23, 'Survival',                     'Survival'),
(24, 'Disarming Traps',              'Survival'),
(25, 'Picking Locks',                'Survival'),
(26, 'Stalking and Hiding',          'Survival'),
(27, 'Perception',                   'Survival'),
(28, 'Climbing',                     'Survival'),
(29, 'Swimming',                     'Survival'),
(30, 'First Aid',                    'General'),
(31, 'Trading',                      'General'),
(32, 'Pickpocketing',                'General'),
(33, 'Spiritual Lore - Blessings',   'Lore'),
(34, 'Spiritual Lore - Religion',    'Lore'),
(35, 'Spiritual Lore - Summoning',   'Lore'),
(36, 'Elemental Lore - Air',         'Lore'),
(37, 'Elemental Lore - Earth',       'Lore'),
(38, 'Elemental Lore - Fire',        'Lore'),
(39, 'Elemental Lore - Water',       'Lore'),
(40, 'Mental Lore - Manipulation',   'Lore'),
(41, 'Mental Lore - Telepathy',      'Lore'),
(42, 'Mental Lore - Transference',   'Lore'),
(43, 'Ambush',                       'Combat'),
(44, 'Mental Lore - Divination',     'Lore'),
(45, 'Mental Lore - Transformation', 'Lore'),
(46, 'Sorcerous Lore - Demonology',  'Lore'),
(47, 'Sorcerous Lore - Necromancy',  'Lore')
ON DUPLICATE KEY UPDATE name=VALUES(name), category=VALUES(category);

-- =============================================================================
-- EXPERIENCE TABLE (GS4 canon values, levels 1–100)
-- Each level's required TOTAL accumulated experience.
-- =============================================================================

INSERT INTO experience_table (level, exp_required) VALUES
(1,0),(2,1000),(3,3000),(4,6000),(5,10000),
(6,15000),(7,21000),(8,28000),(9,36000),(10,45000),
(11,55000),(12,66000),(13,78000),(14,91500),(15,106000),
(16,121500),(17,138000),(18,155500),(19,174000),(20,193500),
(21,214000),(22,235500),(23,258000),(24,281500),(25,306000),
(26,331500),(27,358000),(28,385500),(29,414000),(30,443500),
(31,474000),(32,505500),(33,538000),(34,571500),(35,606000),
(36,641500),(37,678000),(38,715500),(39,754000),(40,793500),
(41,834000),(42,875500),(43,918000),(44,961500),(45,1006000),
(46,1051500),(47,1098000),(48,1145500),(49,1194000),(50,1243500),
(51,1295000),(52,1347500),(53,1401000),(54,1455500),(55,1511000),
(56,1567500),(57,1625000),(58,1683500),(59,1743000),(60,1803500),
(61,1866000),(62,1929500),(63,1994000),(64,2059500),(65,2126000),
(66,2193500),(67,2262000),(68,2331500),(69,2402000),(70,2473500),
(71,2547000),(72,2621500),(73,2697000),(74,2773500),(75,2851000),
(76,2929500),(77,3009000),(78,3089500),(79,3171000),(80,3253500),
(81,3338000),(82,3423500),(83,3510000),(84,3597500),(85,3686000),
(86,3775500),(87,3866000),(88,3957500),(89,4050000),(90,4143500),
(91,4239000),(92,4335500),(93,4433000),(94,4531500),(95,4631000),
(96,4731500),(97,4833000),(98,4935500),(99,5039000),(100,5143500)
ON DUPLICATE KEY UPDATE exp_required=VALUES(exp_required);

-- =============================================================================
-- BASE ITEMS — Weapons (edged)
-- =============================================================================

INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, weapon_type,
    damage_factor, weapon_speed, damage_type, weight, value, description)
VALUES
(1,  'a steel dagger',          'steel dagger',          'dagger',     'a', 'weapon', 1, 'edged',    0.250, 1, 'slash,puncture',       1.0,  50,  'A small, sharp blade designed for quick strikes and thrusting attacks.'),
(2,  'a steel main gauche',     'steel main gauche',     'gauche',     'a', 'weapon', 1, 'edged',    0.275, 2, 'slash,puncture',       2.0,  120, 'A parrying dagger with a wide guard, favored by duelists.'),
(3,  'a steel rapier',          'steel rapier',          'rapier',     'a', 'weapon', 1, 'edged',    0.325, 2, 'slash,puncture',       2.5,  200, 'A long, slender thrusting sword with a complex hilt.'),
(4,  'a steel katar',           'steel katar',           'katar',      'a', 'weapon', 1, 'edged',    0.325, 3, 'slash,puncture',       2.5,  180, 'A thrust-driven punch dagger with an H-shaped handle.'),
(5,  'a steel whip-blade',      'steel whip-blade',      'whip-blade', 'a', 'weapon', 1, 'edged',    0.333, 2, 'slash',                3.0,  350, 'A segmented blade that can flex and lash like a whip.'),
(6,  'a steel scimitar',        'steel scimitar',        'scimitar',   'a', 'weapon', 1, 'edged',    0.375, 4, 'slash,puncture,crush', 3.5,  250, 'A curved blade with a single sharp edge, favored by desert warriors.'),
(7,  'a steel short sword',     'steel short sword',     'sword',      'a', 'weapon', 1, 'edged',    0.350, 3, 'slash,puncture,crush', 3.0,  150, 'A versatile short blade suitable for close combat.'),
(8,  'a steel estoc',           'steel estoc',           'estoc',      'an','weapon', 1, 'edged',    0.425, 4, 'slash,puncture',       4.0,  400, 'A long, stiff thrusting sword designed to pierce armor gaps.'),
(9,  'a steel longsword',       'steel longsword',       'longsword',  'a', 'weapon', 1, 'edged',    0.425, 4, 'slash,puncture,crush', 4.0,  300, 'A well-balanced blade suitable for both cutting and thrusting.'),
(10, 'a steel handaxe',         'steel handaxe',         'handaxe',    'a', 'weapon', 1, 'edged',    0.420, 5, 'slash,crush',          4.5,  200, 'A short-hafted axe with a single cutting head.'),
(11, 'a steel backsword',       'steel backsword',       'backsword',  'a', 'weapon', 1, 'edged',    0.440, 5, 'slash,puncture,crush', 4.5,  350, 'A single-edged sword with a basket hilt for hand protection.'),
(12, 'a steel broadsword',      'steel broadsword',      'broadsword', 'a', 'weapon', 1, 'edged',    0.450, 5, 'slash,puncture,crush', 5.0,  400, 'A heavy blade with a wide cutting edge and simple crossguard.'),
(13, 'a steel falchion',        'steel falchion',        'falchion',   'a', 'weapon', 1, 'edged',    0.450, 5, 'slash,crush',          5.0,  380, 'A broad, slightly curved cleaver-like sword.'),
(14, 'a steel katana',          'steel katana',          'katana',     'a', 'weapon', 1, 'edged',    0.450, 5, 'slash',                4.0,  600, 'A single-edged curved blade with a circular guard and long grip.'),
(15, 'a steel bastard sword',   'steel bastard sword',   'sword',      'a', 'weapon', 1, 'edged',    0.450, 6, 'slash,crush',          5.5,  500, 'A hand-and-a-half sword that can be wielded in one or two hands.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Blunt weapons (IDs 50-60)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, weapon_type,
    damage_factor, weapon_speed, damage_type, weight, value, description)
VALUES
(50, 'a leather whip',           'leather whip',           'whip',    'a', 'weapon', 1, 'blunt', 0.275, 2, 'crush',          2.0, 80,  'A long, braided leather whip with a weighted tip.'),
(51, 'a steel crowbill',         'steel crowbill',         'crowbill','a', 'weapon', 1, 'blunt', 0.350, 3, 'puncture,crush', 3.0, 200, 'A hammer with a pointed beak on one side for piercing armor.'),
(52, 'a wooden cudgel',          'wooden cudgel',          'cudgel',  'a', 'weapon', 1, 'blunt', 0.350, 4, 'crush',          4.0, 30,  'A short, thick club made from a heavy piece of wood.'),
(53, 'a steel mace',             'steel mace',             'mace',    'a', 'weapon', 1, 'blunt', 0.400, 4, 'crush',          5.0, 250, 'A flanged steel mace designed to crush through armor.'),
(54, 'a steel war hammer',       'steel war hammer',       'hammer',  'a', 'weapon', 1, 'blunt', 0.410, 4, 'puncture,crush', 5.0, 350, 'A heavy hammer with a flat face and a spiked reverse.'),
(55, 'a steel morning star',     'steel morning star',     'star',    'a', 'weapon', 1, 'blunt', 0.425, 5, 'crush,puncture', 6.0, 400, 'A spiked ball mounted on a sturdy shaft.'),
(56, 'a steel ball and chain',   'steel ball and chain',   'chain',   'a', 'weapon', 1, 'blunt', 0.400, 6, 'crush',          7.0, 300, 'A spiked ball connected to a handle by a heavy chain.'),
(57, 'a steel flail',            'steel flail',            'flail',   'a', 'weapon', 1, 'blunt', 0.425, 5, 'crush,puncture', 6.5, 380, 'A flail with a spiked metal ball on a length of chain.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Armor (IDs 70-90)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, armor_asg, armor_group,
    defense_bonus, action_penalty, weapon_speed, spell_hindrance, worn_location, weight, value, description)
VALUES
(70, 'some normal clothing',          'normal clothing',          'clothing',    'some','armor', 1, 1,  'cloth',   0,   0,  0,  0,  'torso', 2.0,  10,   'Plain everyday clothing offering no real protection.'),
(71, 'some flowing robes',            'flowing robes',            'robes',       'some','armor', 1, 2,  'cloth',   0,   0,  0,  0,  'torso', 3.0,  50,   'Loose robes favored by magic users for their lack of hindrance.'),
(72, 'some padded armor',             'padded armor',             'armor',       'some','armor', 1, 3,  'leather', 0,   0,  0,  0,  'torso', 4.0,  100,  'Thick quilted cloth offering minimal protection.'),
(73, 'some light leather armor',      'light leather armor',      'armor',       'some','armor', 1, 5,  'leather', 0,   0,  0,  0,  'torso', 5.0,  200,  'Supple leather armor covering vital areas.'),
(74, 'some full leather armor',       'full leather armor',       'armor',       'some','armor', 1, 6,  'leather', 0,  -1,  1,  0,  'torso', 8.0,  350,  'Complete leather armor covering the entire body.'),
(75, 'some reinforced leather armor', 'reinforced leather armor', 'armor',       'some','armor', 1, 7,  'leather', 0,  -5,  2,  4,  'torso', 12.0, 500,  'Leather armor reinforced with metal studs and rings.'),
(76, 'some double leather armor',     'double leather armor',     'armor',       'some','armor', 1, 8,  'leather', 0,  -6,  2,  6,  'torso', 15.0, 600,  'Two layers of hardened leather providing solid protection.'),
(77, 'a leather breastplate',         'leather breastplate',      'breastplate', 'a',  'armor', 1, 9,  'scale',   0,  -7,  3, 16,  'torso', 18.0, 800,  'A rigid boiled leather breastplate with metal fittings.'),
(78, 'some studded leather armor',    'studded leather armor',    'armor',       'some','armor', 1, 11, 'scale',   0, -10,  5, 24,  'torso', 22.0, 1000, 'Leather armor covered with metal studs for added defense.'),
(79, 'some chain mail',               'chain mail',               'mail',        'some','armor', 1, 13, 'chain',   0, -13,  7, 40,  'torso', 30.0, 1500, 'Interlocking metal rings forming a flexible metal armor.'),
(80, 'a metal breastplate',           'metal breastplate',        'breastplate', 'a',  'armor', 1, 17, 'plate',   0, -20,  9, 90,  'torso', 40.0, 4000, 'A solid metal chest piece providing excellent torso protection.'),
(81, 'a suit of full plate armor',    'full plate armor',         'armor',       'a',  'armor', 1, 20, 'plate',   0, -35, 12, 96,  'torso', 60.0, 10000,'Complete suit of articulated steel plates covering the entire body.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Robes and padded (separate IDs needed by starter gear)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, armor_asg, armor_group,
    action_penalty, weapon_speed, spell_hindrance, worn_location, weight, value, description)
VALUES
(352, 'some flowing robes',  'flowing robes', 'robes', 'some', 'armor', 1, 2, 'cloth', 0, 0, 0, 'torso', 3.0, 50,  'Loose robes favored by magic users for their lack of hindrance.'),
(353, 'some padded armor',   'padded armor',  'armor', 'some', 'armor', 1, 3, 'leather', 0, 0, 0, 'torso', 4.0, 100, 'Thick quilted cloth offering minimal protection.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Shields (IDs 90-100)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, shield_type,
    shield_ds, shield_evade_penalty, shield_size_mod, worn_location, weight, value, material, description)
VALUES
(93, 'a steel buckler',          'steel buckler',        'buckler', 'a', 'shield', 1, 'small',  10, 22, -15, 'shoulder_slung', 3.0, 150,  'steel', 'A small, round steel shield strapped to the forearm.'),
(94, 'a steel target shield',    'steel target shield',  'shield',  'a', 'shield', 1, 'medium', 20, 30,   0, 'shoulder_slung', 8.0, 400,  'steel', 'The standard adventurer''s shield, a medium-sized steel target shield.'),
(95, 'a steel kite shield',      'steel kite shield',    'shield',  'a', 'shield', 1, 'large',  25, 38,  15, 'shoulder_slung', 9.0, 700,  'steel', 'A large kite-shaped steel shield providing excellent body coverage.'),
(96, 'a steel greatshield',      'steel greatshield',    'greatshield','a','shield',1, 'tower', 30, 46,  30, 'shoulder_slung',12.0, 1200, 'steel', 'An enormous steel shield nearly as tall as the bearer.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Two-handed weapons (IDs 100-120)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, weapon_type,
    damage_factor, weapon_speed, damage_type, weight, value, description)
VALUES
(101,'a wooden runestaff',       'wooden runestaff',      'runestaff',    'a', 'weapon', 1, 'twohanded', 0.250, 6, 'crush',        3.0, 500, 'An ancient staff inscribed with glowing runes of arcane power.'),
(102,'a wooden quarterstaff',    'wooden quarterstaff',   'quarterstaff', 'a', 'weapon', 1, 'twohanded', 0.450, 3, 'crush',        4.0, 40,  'A sturdy wooden staff suitable for both defense and offense.'),
(103,'a bastard sword',          'bastard sword',         'sword',        'a', 'weapon', 1, 'twohanded', 0.550, 6, 'slash,crush',  6.0, 550, 'A versatile blade that bridges the gap between longsword and greatsword.'),
(104,'a flamberge',              'flamberge',             'flamberge',    'a', 'weapon', 1, 'twohanded', 0.600, 7, 'slash,crush',  8.0, 600, 'A broad sword with a wavy blade designed to shear through flesh.'),
(105,'a battle axe',             'battle axe',            'axe',          'a', 'weapon', 1, 'twohanded', 0.650, 8, 'slash,crush', 10.0, 650, 'A double-headed axe honed sharp enough to cleave through armor.'),
(106,'a claidhmore',             'claidhmore',            'claidhmore',   'a', 'weapon', 1, 'twohanded', 0.625, 8, 'slash,crush',  9.0, 750, 'A legendary great sword of ancient Highland warriors.'),
(107,'a maul',                   'maul',                  'maul',         'a', 'weapon', 1, 'twohanded', 0.550, 7, 'crush',       10.0, 350, 'An enormous two-handed hammer capable of shattering bone.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Ranged weapons (IDs 200-210)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, weapon_type,
    damage_factor, weapon_speed, damage_type, weight, value, description)
VALUES
(201,'a short bow',              'short bow',             'bow',       'a', 'weapon', 1, 'ranged', 0.325, 5, 'puncture,slash', 3.0, 200, 'A compact bow designed for maneuverability in close quarters.'),
(202,'a composite bow',          'composite bow',         'bow',       'a', 'weapon', 1, 'ranged', 0.350, 6, 'puncture,slash', 4.0, 400, 'A bow constructed from multiple materials for superior power and range.'),
(203,'a long bow',               'long bow',              'bow',       'a', 'weapon', 1, 'ranged', 0.400, 7, 'puncture,slash', 5.0, 500, 'A towering bow requiring considerable strength but delivering devastating force.'),
(204,'a light crossbow',         'light crossbow',        'crossbow',  'a', 'weapon', 1, 'ranged', 0.350, 6, 'puncture,slash', 6.0, 400, 'A crossbow balanced between ease of use and projectile power.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Ammunition (IDs 210-220)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, is_stackable, weight, value, description)
VALUES
(211,'a bundle of arrows',       'bundle of arrows',      'arrows',  'a', 'ammo', 1, 1, 1.0, 50,  'A bundle of twenty steel-tipped arrows.'),
(212,'a bundle of crossbow bolts','bundle of crossbow bolts','bolts','a', 'ammo', 1, 1, 1.5, 60,  'A bundle of steel crossbow bolts.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Lockpicks (IDs 205-209)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, weight, value, material, description)
VALUES
(205,'a crude lockpick',         'crude lockpick',        'lockpick','a', 'lockpick', 1, 0.1, 100,  'copper', 'A crude copper lockpick, bent and imprecise.'),
(206,'a simple lockpick',        'simple lockpick',       'lockpick','a', 'lockpick', 1, 0.1, 250,  'brass',  'A simple brass lockpick, adequate for beginner rogues.'),
(207,'a standard lockpick',      'standard lockpick',     'lockpick','a', 'lockpick', 1, 0.1, 500,  'steel',  'A standard steel lockpick used by working rogues.'),
(208,'an ivory lockpick',        'ivory lockpick',        'lockpick','an','lockpick', 1, 0.1, 750,  'ivory',  'An ivory lockpick carved smooth, with good feel.'),
(209,'a silver lockpick',        'silver lockpick',       'lockpick','a', 'lockpick', 1, 0.1, 2500, 'silver', 'A silver lockpick, a step up for experienced rogues.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Containers / wearables (IDs 236-250)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, container_capacity,
    container_type, worn_location, weight, value, description)
VALUES
(236,'a leather backpack',       'leather backpack',       'backpack','a', 'container', 1, 60, 'wearable','back',      2.0, 100, 'A sturdy leather backpack with multiple compartments and brass buckles.'),
(237,'a canvas knapsack',        'canvas knapsack',        'knapsack','a', 'container', 1, 60, 'wearable','back',      1.5, 50,  'A simple canvas pack, practical if unglamorous.'),
(238,'a belt pouch',             'belt pouch',             'pouch',   'a', 'container', 1, 20, 'wearable','belt',      0.5, 25,  'A small leather pouch worn at the hip, ideal for coins and small items.'),
(239,'a herb pouch',             'herb pouch',             'pouch',   'a', 'container', 1, 40, 'wearable','belt',      0.5, 75,  'A specially-designed pouch with compartments for herbs.'),
(240,'a gem pouch',              'gem pouch',              'pouch',   'a', 'container', 1, 80, 'wearable','belt',      0.5, 150, 'A velvet-lined pouch for storing gems securely.'),
(241,'an adventurer''s cloak',   'adventurer''s cloak',    'cloak',   'an','container', 1, 40, 'wearable','shoulders', 2.0, 200, 'A hooded travel cloak with numerous interior pockets.'),
(242,'a flowing silk cloak',     'flowing silk cloak',     'cloak',   'a', 'container', 1, 40, 'wearable','shoulders', 1.0, 350, 'An elegant silk cloak with hidden pockets woven into its folds.'),
(243,'a white linen cloak',      'white linen cloak',      'cloak',   'a', 'container', 1, 40, 'wearable','shoulders', 1.5, 150, 'A clean white linen cloak with inside pockets for holy components.'),
(244,'a pale green cloak',       'pale green cloak',       'cloak',   'a', 'container', 1, 40, 'wearable','shoulders', 1.5, 200, 'A pale green cloak traditionally worn by empaths, with wide herb pockets.'),
(245,'a dark silk cloak',        'dark silk cloak',        'cloak',   'a', 'container', 1, 40, 'wearable','shoulders', 1.0, 300, 'A dark silk cloak that seems to absorb light.'),
(246,'a forest green cloak',     'forest green cloak',     'cloak',   'a', 'container', 1, 40, 'wearable','shoulders', 2.0, 200, 'A deep forest green travel cloak that blends into surroundings.'),
(247,'a colorful traveling cloak','colorful traveling cloak','cloak', 'a', 'container', 1, 40, 'wearable','shoulders', 1.5, 300, 'A vibrantly colored cloak with troubadour patterns and wide pockets.'),
(248,'a white tabard cloak',     'white tabard cloak',     'cloak',   'a', 'container', 1, 40, 'wearable','shoulders', 2.0, 400, 'A white tabard with an embroidered holy sigil and interior compartments.'),
(249,'a rough-spun monk''s cloak','rough-spun monk''s cloak','cloak','a', 'container', 1, 40, 'wearable','shoulders', 1.5, 100, 'A plainly woven monk''s traveling cloak, functional rather than decorative.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Tools / components (IDs 750-760)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, weight, value, description)
VALUES
(750,'a copper symbol',          'copper symbol',          'symbol',  'a', 'component',  1, 1.0, 50,  'A copper arcane symbol used as a magic component.'),
(751,'a holy symbol',            'holy symbol',            'symbol',  'a', 'component',  1, 1.0, 100, 'A religious holy symbol inscribed with sacred glyphs.'),
(752,'a vaalin stylus',          'vaalin stylus',          'stylus',  'a', 'component',  1, 1.0, 200, 'A slender vaalin stylus for scribing magical formulae.'),
(760,'a simple wooden lute',     'simple wooden lute',     'lute',    'a', 'instrument', 1, 3.0, 300, 'A simply-made wooden lute with gut strings.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Brawling weapons (IDs 300-315)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, weapon_type,
    damage_factor, weapon_speed, damage_type, weight, value, description)
VALUES
(300,'a steel cestus',           'steel cestus',           'cestus',       'a', 'weapon', 1, 'brawling', 0.250, 1, 'crush',               1.0, 100, 'Leather and metal wrapped around the fist for devastating punching power.'),
(301,'a razorpaw',               'razorpaw',               'razorpaw',     'a', 'weapon', 1, 'brawling', 0.275, 1, 'slash',               1.0, 150, 'Clawed gloves that extend the reach of a warrior''s slashing strikes.'),
(302,'a steel cestus',           'steel cestus',           'cestus',       'a', 'weapon', 1, 'brawling', 0.250, 1, 'crush',               1.0, 100, 'Leather and metal wrapped around the fist for devastating punching power.'),
(303,'a knuckle-duster',         'knuckle-duster',         'duster',       'a', 'weapon', 1, 'brawling', 0.250, 1, 'crush',               1.0, 80,  'Brass-studded knuckles that augment natural striking with added weight.'),
(304,'a sai',                    'sai',                    'sai',          'a', 'weapon', 1, 'brawling', 0.250, 2, 'puncture',            1.5, 120, 'A three-pronged striking weapon favored by Eastern martial artists.'),
(305,'a tiger-claw',             'tiger-claw',             'claw',         'a', 'weapon', 1, 'brawling', 0.275, 1, 'slash,crush',         1.0, 170, 'Fearsome curved talons mimicking a great cat''s lethal grip.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Herbs (IDs 600-625)
INSERT INTO items (id, name, short_name, noun, article, item_type, is_template, is_stackable,
    heal_type, heal_rank, heal_amount, herb_roundtime, weight, value, description)
VALUES
(601,'some acantha leaf',        'acantha leaf',           'leaf',    'some','herb', 1, 1, 'blood',      1, 10, 5,  1, 50,   'some acantha leaf'),
(602,'some wolifrew lichen',     'wolifrew lichen',        'lichen',  'some','herb', 1, 1, 'nerves',     1,  0, 15, 1, 100,  'some wolifrew lichen'),
(603,'some torban leaf',         'torban leaf',            'leaf',    'some','herb', 1, 1, 'nerves',     3,  0, 15, 1, 150,  'some torban leaf'),
(604,'some woth flower',         'woth flower',            'flower',  'some','herb', 1, 1, 'nerves',     4,  0, 30, 1, 600,  'some woth flower'),
(605,'some basal moss',          'basal moss',             'moss',    'some','herb', 1, 1, 'torso',      1,  0, 15, 1, 150,  'some basal moss'),
(606,'some ambrominas leaf',     'ambrominas leaf',        'leaf',    'some','herb', 1, 1, 'limb',       1,  0, 15, 1, 100,  'some ambrominas leaf'),
(607,'some haphip root',         'haphip root',            'root',    'some','herb', 1, 1, 'head',       3,  0, 15, 1, 250,  'some haphip root'),
(608,'some cactacae spine',      'cactacae spine',         'spine',   'some','herb', 1, 1, 'limb',       3,  0, 15, 1, 150,  'some cactacae spine'),
(609,'some aloeas stem',         'aloeas stem',            'stem',    'some','herb', 1, 1, 'head',       2,  0, 25, 1, 800,  'some aloeas stem'),
(610,'some pothinir grass',      'pothinir grass',         'grass',   'some','herb', 1, 1, 'torso',      2,  0, 25, 1, 1000, 'some pothinir grass'),
(611,'some ephlox moss',         'ephlox moss',            'moss',    'some','herb', 1, 1, 'limb',       2,  0, 25, 1, 700,  'some ephlox moss'),
(612,'some calamia fruit',       'calamia fruit',          'fruit',   'some','herb', 1, 1, 'limb',       4,  0, 30, 1, 1500, 'some calamia fruit'),
(613,'some sovyn clove',         'sovyn clove',            'clove',   'some','herb', 1, 1, 'limb_regen', 5,  0, 30, 1, 5000, 'some sovyn clove'),
(614,'some cothinar flower',     'cothinar flower',        'flower',  'some','herb', 1, 1, 'blood',      1, 15,  5, 1, 75,   'some cothinar flower'),
(615,'some yabathilium fruit',   'yabathilium fruit',      'fruit',   'some','herb', 1, 1, 'blood',      2, 50,  0, 1, 300,  'some yabathilium fruit'),
(616,'a bolmara potion',         'bolmara potion',         'potion',  'a',  'herb', 1, 0, 'nerves',     2,  0, 25, 1, 500,  'a bolmara potion'),
(617,'a rose-marrow potion',     'rose-marrow potion',     'potion',  'a',  'herb', 1, 0, 'head',       1,  0, 15, 1, 200,  'a rose-marrow potion'),
(618,'a brostheras potion',      'brostheras potion',      'potion',  'a',  'herb', 1, 0, 'head',       4,  0, 30, 1, 900,  'a brostheras potion'),
(619,'a talneo potion',          'talneo potion',          'potion',  'a',  'herb', 1, 0, 'torso',      3,  0, 15, 1, 300,  'a talneo potion'),
(620,'a wingstem potion',        'wingstem potion',        'potion',  'a',  'herb', 1, 0, 'torso',      4,  0, 30, 1, 1200, 'a wingstem potion'),
(621,'a bur-clover potion',      'bur-clover potion',      'potion',  'a',  'herb', 1, 0, 'eye',        5,  0, 30, 1, 2000, 'a bur-clover potion')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- =============================================================================
-- TOWNS
-- =============================================================================

INSERT INTO towns (id, name, bank_room_id) VALUES
(1, 'Wehnimer''s Landing', 100),
(2, 'Ta''Vaalor',          5907),
(3, 'Icemule Trace',       NULL),
(4, 'River''s Rest',       NULL),
(5, 'Solhaven',            NULL),
(6, 'Teras Isle',          NULL),
(7, 'Zul Logoth',          NULL)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- =============================================================================
-- DONE
-- =============================================================================
SELECT 'Schema seeded successfully.' AS status;
