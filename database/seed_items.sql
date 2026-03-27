-- GemStone IV Item Seed Data
-- Generated from all item data files
-- Run: mysql -u root gemstone_dev < seed_items.sql
USE gemstone_dev;

-- ============================================================
-- EDGED WEAPONS (15 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, weight, value, weapon_category, damage_factor, weapon_speed, damage_type, description, is_template) VALUES
('a steel dagger', 'steel dagger', 'dagger', 'dagger', 'a', 'weapon', 'steel', 1.0, 50, 'edged', 0.250, 1, 'slash,puncture', 'A small, sharp blade designed for quick strikes and thrusting attacks.', 1),
('a steel main gauche', 'steel main gauche', 'gauche', 'main gauche', 'a', 'weapon', 'steel', 2.0, 120, 'edged', 0.275, 2, 'slash,puncture', 'A parrying dagger with a wide guard, favored by duelists.', 1),
('a steel rapier', 'steel rapier', 'rapier', 'rapier', 'a', 'weapon', 'steel', 2.5, 200, 'edged', 0.325, 2, 'slash,puncture', 'A long, slender thrusting sword with a complex hilt.', 1),
('a steel whip-blade', 'steel whip-blade', 'whip-blade', 'whip-blade', 'a', 'weapon', 'steel', 3.0, 350, 'edged', 0.333, 2, 'slash', 'A segmented blade that can flex and lash like a whip.', 1),
('a steel katar', 'steel katar', 'katar', 'katar', 'a', 'weapon', 'steel', 2.5, 180, 'edged', 0.325, 3, 'slash,puncture', 'A thrust-driven punch dagger with a H-shaped handle.', 1),
('a steel short sword', 'steel short sword', 'sword', 'short sword', 'a', 'weapon', 'steel', 3.0, 150, 'edged', 0.350, 3, 'slash,puncture,crush', 'A versatile short blade suitable for close combat.', 1),
('a steel scimitar', 'steel scimitar', 'scimitar', 'scimitar', 'a', 'weapon', 'steel', 3.5, 250, 'edged', 0.375, 4, 'slash,puncture,crush', 'A curved blade with a single sharp edge, favored by desert warriors.', 1),
('a steel estoc', 'steel estoc', 'estoc', 'estoc', 'a', 'weapon', 'steel', 4.0, 400, 'edged', 0.425, 4, 'slash,puncture', 'A long, stiff thrusting sword designed to pierce armor gaps.', 1),
('a steel longsword', 'steel longsword', 'longsword', 'longsword', 'a', 'weapon', 'steel', 4.0, 300, 'edged', 0.425, 4, 'slash,puncture,crush', 'A well-balanced blade suitable for both cutting and thrusting.', 1),
('a steel handaxe', 'steel handaxe', 'handaxe', 'handaxe', 'a', 'weapon', 'steel', 4.5, 200, 'edged', 0.420, 5, 'slash,crush', 'A short-hafted axe with a single cutting head.', 1),
('a steel backsword', 'steel backsword', 'backsword', 'backsword', 'a', 'weapon', 'steel', 4.5, 350, 'edged', 0.440, 5, 'slash,puncture,crush', 'A single-edged sword with a basket hilt for hand protection.', 1),
('a steel broadsword', 'steel broadsword', 'broadsword', 'broadsword', 'a', 'weapon', 'steel', 5.0, 400, 'edged', 0.450, 5, 'slash,puncture,crush', 'A heavy blade with a wide cutting edge and simple crossguard.', 1),
('a steel falchion', 'steel falchion', 'falchion', 'falchion', 'a', 'weapon', 'steel', 5.0, 380, 'edged', 0.450, 5, 'slash,crush', 'A broad, slightly curved cleaver-like sword.', 1),
('a steel katana', 'steel katana', 'katana', 'katana', 'a', 'weapon', 'steel', 4.0, 600, 'edged', 0.450, 5, 'slash', 'A single-edged curved blade with a circular guard and long grip.', 1),
('a steel bastard sword', 'steel bastard sword', 'sword', 'bastard sword', 'a', 'weapon', 'steel', 5.5, 500, 'edged', 0.450, 6, 'slash,crush', 'A hand-and-a-half sword that can be wielded in one or two hands.', 1);

-- ============================================================
-- BLUNT WEAPONS (7 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, weight, value, weapon_category, damage_factor, weapon_speed, damage_type, description, is_template) VALUES
('a steel mace', 'steel mace', 'mace', 'mace', 'a', 'weapon', 'steel', 5.0, 150, 'blunt', 0.350, 4, 'crush', 'A flanged metal head on a sturdy shaft.', 1),
('a steel morning star', 'steel morning star', 'star', 'morning star', 'a', 'weapon', 'steel', 6.0, 300, 'blunt', 0.400, 5, 'crush,puncture', 'A spiked ball on a chain attached to a handle.', 1),
('a steel war hammer', 'steel war hammer', 'hammer', 'war hammer', 'a', 'weapon', 'steel', 6.0, 350, 'blunt', 0.425, 5, 'crush', 'A heavy hammer designed for crushing armor.', 1),
('a steel ball and chain', 'steel ball and chain', 'chain', 'ball and chain', 'a', 'weapon', 'steel', 7.0, 400, 'blunt', 0.450, 6, 'crush', 'A spiked ball on a heavy chain, difficult to wield.', 1),
('a steel cudgel', 'steel cudgel', 'cudgel', 'cudgel', 'a', 'weapon', 'steel', 4.0, 50, 'blunt', 0.300, 3, 'crush', 'A simple, heavy club.', 1),
('a steel flail', 'steel flail', 'flail', 'flail', 'a', 'weapon', 'steel', 5.5, 250, 'blunt', 0.375, 5, 'crush', 'A hinged weapon with a striking head.', 1),
('a wooden quarterstaff', 'wooden quarterstaff', 'quarterstaff', 'quarterstaff', 'a', 'weapon', 'wood', 3.0, 25, 'blunt', 0.250, 3, 'crush', 'A long wooden staff used for both offense and defense.', 1);

-- ============================================================
-- TWO-HANDED WEAPONS (12 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, weight, value, weapon_category, damage_factor, weapon_speed, damage_type, description, is_template) VALUES
('a steel claymore', 'steel claymore', 'claymore', 'claymore', 'a', 'weapon', 'steel', 8.0, 500, 'twohanded', 0.500, 7, 'slash,crush', 'A massive two-handed greatsword.', 1),
('a steel flamberge', 'steel flamberge', 'flamberge', 'flamberge', 'a', 'weapon', 'steel', 9.0, 600, 'twohanded', 0.525, 7, 'slash', 'A wavy-bladed two-handed sword.', 1),
('a steel zweihander', 'steel zweihander', 'zweihander', 'zweihander', 'a', 'weapon', 'steel', 10.0, 700, 'twohanded', 0.550, 8, 'slash,crush', 'An enormous two-handed sword.', 1),
('a steel battle axe', 'steel battle axe', 'axe', 'battle axe', 'a', 'weapon', 'steel', 8.0, 400, 'twohanded', 0.500, 7, 'slash,crush', 'A large double-bitted axe.', 1),
('a steel great axe', 'steel great axe', 'axe', 'great axe', 'a', 'weapon', 'steel', 10.0, 550, 'twohanded', 0.550, 8, 'slash,crush', 'A massive axe requiring two hands.', 1),
('a steel maul', 'steel maul', 'maul', 'maul', 'a', 'weapon', 'steel', 12.0, 450, 'twohanded', 0.575, 8, 'crush', 'An enormous war hammer.', 1),
('a steel war mattock', 'steel war mattock', 'mattock', 'war mattock', 'a', 'weapon', 'steel', 10.0, 400, 'twohanded', 0.525, 7, 'crush,puncture', 'A heavy mattock adapted for war.', 1),
('a wooden runestaff', 'wooden runestaff', 'runestaff', 'runestaff', 'a', 'weapon', 'wood', 4.0, 300, 'twohanded', 0.275, 5, 'crush', 'A magical staff used by spellcasters.', 1),
('a steel halberd', 'steel halberd', 'halberd', 'halberd', 'a', 'weapon', 'steel', 9.0, 500, 'twohanded', 0.525, 7, 'slash,puncture,crush', 'An axe blade topped with a spike.', 1),
('a steel jeddart-axe', 'steel jeddart-axe', 'jeddart-axe', 'jeddart-axe', 'a', 'weapon', 'steel', 8.0, 450, 'twohanded', 0.500, 7, 'slash,puncture', 'A hooked polearm blade.', 1),
('a steel lance', 'steel lance', 'lance', 'lance', 'a', 'weapon', 'steel', 10.0, 350, 'twohanded', 0.475, 7, 'puncture', 'A long thrusting weapon used from horseback.', 1),
('a steel bastard sword', 'steel bastard sword 2h', 'sword', 'bastard sword (2h)', 'a', 'weapon', 'steel', 5.5, 500, 'twohanded', 0.475, 6, 'slash,crush', 'A hand-and-a-half sword wielded in two hands.', 1);

-- ============================================================
-- POLEARM WEAPONS (9 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, weight, value, weapon_category, damage_factor, weapon_speed, damage_type, description, is_template) VALUES
('a steel spear', 'steel spear', 'spear', 'spear', 'a', 'weapon', 'steel', 5.0, 100, 'polearm', 0.350, 5, 'puncture', 'A simple pole with a pointed head.', 1),
('a steel pike', 'steel pike', 'pike', 'pike', 'a', 'weapon', 'steel', 8.0, 200, 'polearm', 0.400, 6, 'puncture', 'An extremely long thrusting spear.', 1),
('a steel trident', 'steel trident', 'trident', 'trident', 'a', 'weapon', 'steel', 6.0, 250, 'polearm', 0.400, 5, 'puncture', 'A three-pronged fishing spear adapted for combat.', 1),
('a steel partisan', 'steel partisan', 'partisan', 'partisan', 'a', 'weapon', 'steel', 7.0, 300, 'polearm', 0.425, 6, 'slash,puncture', 'A broad-bladed spear with lateral projections.', 1),
('a steel glaive', 'steel glaive', 'glaive', 'glaive', 'a', 'weapon', 'steel', 7.0, 350, 'polearm', 0.450, 6, 'slash', 'A pole with a single-edged blade.', 1),
('a steel naginata', 'steel naginata', 'naginata', 'naginata', 'a', 'weapon', 'steel', 6.0, 400, 'polearm', 0.425, 5, 'slash', 'A curved-blade polearm.', 1),
('a steel javelin', 'steel javelin', 'javelin', 'javelin', 'a', 'weapon', 'steel', 3.0, 75, 'polearm', 0.300, 4, 'puncture', 'A light throwing spear.', 1),
('a steel awl-pike', 'steel awl-pike', 'awl-pike', 'awl-pike', 'a', 'weapon', 'steel', 9.0, 250, 'polearm', 0.450, 7, 'puncture', 'A long, narrow-bladed pike.', 1),
('a steel voulge', 'steel voulge', 'voulge', 'voulge', 'a', 'weapon', 'steel', 8.0, 300, 'polearm', 0.450, 6, 'slash,crush', 'A heavy cleaver mounted on a pole.', 1);

-- ============================================================
-- RANGED WEAPONS (6 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, weight, value, weapon_category, damage_factor, weapon_speed, damage_type, description, is_template) VALUES
('a wooden short bow', 'wooden short bow', 'bow', 'short bow', 'a', 'weapon', 'wood', 2.0, 100, 'ranged', 0.250, 4, 'puncture', 'A small bow for short-range combat.', 1),
('a wooden long bow', 'wooden long bow', 'bow', 'long bow', 'a', 'weapon', 'wood', 3.0, 250, 'ranged', 0.350, 5, 'puncture', 'A tall bow for long-range shooting.', 1),
('a wooden composite bow', 'wooden composite bow', 'bow', 'composite bow', 'a', 'weapon', 'wood', 3.0, 400, 'ranged', 0.400, 5, 'puncture', 'A recurve bow of laminated materials.', 1),
('a steel light crossbow', 'steel light crossbow', 'crossbow', 'light crossbow', 'a', 'weapon', 'steel', 4.0, 300, 'ranged', 0.400, 6, 'puncture', 'A small, easy-to-load crossbow.', 1),
('a steel heavy crossbow', 'steel heavy crossbow', 'crossbow', 'heavy crossbow', 'a', 'weapon', 'steel', 7.0, 500, 'ranged', 0.500, 8, 'puncture', 'A powerful crossbow requiring a winch to load.', 1),
('a wooden hand crossbow', 'wooden hand crossbow', 'crossbow', 'hand crossbow', 'a', 'weapon', 'wood', 2.0, 200, 'ranged', 0.250, 4, 'puncture', 'A tiny crossbow that can be fired one-handed.', 1);

-- ============================================================
-- THROWN WEAPONS (6 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, weight, value, weapon_category, damage_factor, weapon_speed, damage_type, description, is_template) VALUES
('a steel throwing dagger', 'steel throwing dagger', 'dagger', 'throwing dagger', 'a', 'weapon', 'steel', 1.0, 30, 'thrown', 0.200, 2, 'puncture', 'A balanced dagger designed for throwing.', 1),
('a steel throwing axe', 'steel throwing axe', 'axe', 'throwing axe', 'a', 'weapon', 'steel', 3.0, 75, 'thrown', 0.300, 3, 'slash,crush', 'A small axe balanced for throwing.', 1),
('a steel dart', 'steel dart', 'dart', 'dart', 'a', 'weapon', 'steel', 0.5, 15, 'thrown', 0.150, 2, 'puncture', 'A small, pointed missile weapon.', 1),
('a shuriken', 'steel shuriken', 'shuriken', 'shuriken', 'a', 'weapon', 'steel', 0.5, 50, 'thrown', 0.175, 2, 'slash,puncture', 'A flat, star-shaped throwing blade.', 1),
('a steel throwing hammer', 'steel throwing hammer', 'hammer', 'throwing hammer', 'a', 'weapon', 'steel', 4.0, 100, 'thrown', 0.350, 4, 'crush', 'A weighted hammer balanced for throwing.', 1),
('a stone', 'stone', 'stone', 'stone', 'a', 'weapon', 'stone', 1.0, 1, 'thrown', 0.100, 2, 'crush', 'A simple throwing stone.', 1);

-- ============================================================
-- BRAWLING WEAPONS (13 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, weight, value, weapon_category, damage_factor, weapon_speed, damage_type, description, is_template) VALUES
('a pair of leather cestus', 'leather cestus', 'cestus', 'cestus', 'a', 'weapon', 'leather', 1.0, 50, 'brawling', 0.200, 2, 'crush', 'Leather hand wraps reinforced for striking.', 1),
('a pair of knuckle-dusters', 'steel knuckle-dusters', 'knuckle-dusters', 'knuckle-dusters', 'a', 'weapon', 'steel', 1.0, 75, 'brawling', 0.225, 2, 'crush', 'Metal bands worn over the knuckles.', 1),
('a steel hook-knife', 'steel hook-knife', 'hook-knife', 'hook-knife', 'a', 'weapon', 'steel', 1.0, 100, 'brawling', 0.250, 2, 'slash,puncture', 'A small curved blade strapped to the hand.', 1),
('a pair of steel paingrips', 'steel paingrips', 'paingrips', 'paingrips', 'a', 'weapon', 'steel', 1.5, 150, 'brawling', 0.275, 3, 'crush,puncture', 'Spiked gripping gloves.', 1),
('a pair of tiger-claw', 'steel tiger-claw', 'tiger-claw', 'tiger-claw', 'a', 'weapon', 'steel', 1.0, 200, 'brawling', 0.275, 2, 'slash', 'Curved blades strapped to the fingers.', 1),
('a steel fist-scythe', 'steel fist-scythe', 'fist-scythe', 'fist-scythe', 'a', 'weapon', 'steel', 1.5, 175, 'brawling', 0.275, 3, 'slash', 'A small curved blade extending from the fist.', 1),
('a pair of steel troll-claws', 'steel troll-claws', 'troll-claws', 'troll-claws', 'a', 'weapon', 'steel', 2.0, 250, 'brawling', 0.300, 3, 'slash,puncture', 'Long curved claws strapped to the hand.', 1),
('a steel yierka-spur', 'steel yierka-spur', 'yierka-spur', 'yierka-spur', 'a', 'weapon', 'steel', 1.0, 125, 'brawling', 0.250, 2, 'puncture', 'A spiked spur worn on the wrist.', 1),
('a pair of leather hand wraps', 'leather hand wraps', 'wraps', 'hand wraps', 'a', 'weapon', 'leather', 0.5, 15, 'brawling', 0.150, 2, 'crush', 'Simple cloth wraps for hand protection.', 1),
('a steel knuckle-blade', 'steel knuckle-blade', 'knuckle-blade', 'knuckle-blade', 'a', 'weapon', 'steel', 1.0, 200, 'brawling', 0.275, 2, 'slash,puncture', 'A short blade attached to a knuckle guard.', 1),
('a pair of steel razorpaws', 'steel razorpaws', 'razorpaws', 'razorpaws', 'a', 'weapon', 'steel', 1.5, 225, 'brawling', 0.275, 3, 'slash', 'Razor-edged claw gauntlets.', 1),
('a steel spiked gauntlet', 'steel spiked gauntlet', 'gauntlet', 'spiked gauntlet', 'a', 'weapon', 'steel', 2.0, 175, 'brawling', 0.275, 3, 'crush,puncture', 'An armored gauntlet with protruding spikes.', 1),
('a steel claw gauntlet', 'steel claw gauntlet', 'gauntlet', 'claw gauntlet', 'a', 'weapon', 'steel', 2.0, 200, 'brawling', 0.300, 3, 'slash', 'An armored gauntlet with extending claws.', 1);

-- ============================================================
-- ARMOR (20 ASG types)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, armor_asg, cva, action_penalty, spell_hindrance, weight, value, description, is_template) VALUES
('some normal clothing', 'normal clothing', 'clothing', 'normal clothing', 'some', 'armor', 1, 25, 0, 0, 2.0, 10, 'Plain everyday clothing offering no real protection.', 1),
('some flowing robes', 'flowing robes', 'robes', 'robes', 'some', 'armor', 2, 25, 0, 0, 3.0, 50, 'Loose robes favored by magic users for their lack of hindrance.', 1),
('some padded armor', 'padded armor', 'armor', 'padded armor', 'some', 'armor', 3, 24, 0, 0, 4.0, 75, 'Quilted layers of cloth providing light protection.', 1),
('some light leather armor', 'light leather armor', 'armor', 'light leather', 'some', 'armor', 4, 22, 0, 1, 5.0, 100, 'Thin leather armor offering basic protection.', 1),
('some full leather armor', 'full leather armor', 'armor', 'full leather', 'some', 'armor', 5, 20, 0, 3, 7.0, 200, 'Complete leather armor covering torso and limbs.', 1),
('some reinforced leather', 'reinforced leather', 'leather', 'reinforced leather', 'some', 'armor', 6, 18, 0, 5, 8.0, 300, 'Leather hardened and reinforced with additional layers.', 1),
('some double leather', 'double leather', 'leather', 'double leather', 'some', 'armor', 7, 16, 2, 8, 10.0, 400, 'Two layers of boiled and shaped leather.', 1),
('some leather breastplate', 'leather breastplate', 'breastplate', 'leather breastplate', 'some', 'armor', 8, 14, 5, 10, 12.0, 500, 'A rigid leather chestpiece.', 1),
('some studded leather', 'studded leather', 'armor', 'studded leather', 'some', 'armor', 9, 13, 5, 12, 13.0, 600, 'Leather reinforced with metal studs.', 1),
('a brigandine armor', 'brigandine armor', 'armor', 'brigandine', 'a', 'armor', 10, 12, 7, 14, 14.0, 700, 'Armor of small metal plates riveted to cloth.', 1),
('a chain mail', 'chain mail', 'mail', 'chain mail', 'a', 'armor', 11, 10, 7, 15, 16.0, 800, 'Interlocking metal rings forming flexible armor.', 1),
('a double chain mail', 'double chain mail', 'mail', 'double chain', 'a', 'armor', 12, 8, 10, 18, 20.0, 1000, 'Two layers of chain mail for added protection.', 1),
('some augmented chain', 'augmented chain', 'chain', 'augmented chain', 'some', 'armor', 13, 5, 12, 20, 22.0, 1200, 'Chain mail reinforced with metal plates.', 1),
('a chain hauberk', 'chain hauberk', 'hauberk', 'chain hauberk', 'a', 'armor', 14, 3, 13, 22, 25.0, 1500, 'A long chain mail shirt extending past the waist.', 1),
('a metal breastplate', 'metal breastplate', 'breastplate', 'metal breastplate', 'a', 'armor', 15, 1, 14, 25, 20.0, 1800, 'A solid metal chestpiece.', 1),
('an augmented breastplate', 'augmented breastplate', 'breastplate', 'augmented breastplate', 'an', 'armor', 16, -2, 16, 27, 25.0, 2200, 'A breastplate with additional plate protection.', 1),
('some half plate', 'half plate', 'plate', 'half plate', 'some', 'armor', 17, -5, 18, 30, 30.0, 3000, 'Plate armor covering upper body and thighs.', 1),
('some full plate', 'full plate', 'plate', 'full plate', 'some', 'armor', 18, -8, 20, 33, 35.0, 4000, 'Complete plate armor covering the entire body.', 1),
('some augmented plate', 'augmented plate', 'plate', 'augmented plate', 'some', 'armor', 19, -10, 22, 35, 40.0, 5000, 'Full plate with reinforced layers.', 1),
('some razern plate', 'razern plate', 'plate', 'razern plate', 'some', 'armor', 20, -12, 25, 38, 45.0, 8000, 'The heaviest and most protective plate armor.', 1);

-- ============================================================
-- SHIELDS (18 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, shield_size, shield_ds, shield_evade_penalty, weight, value, description, is_template) VALUES
('a small leather shield', 'small leather shield', 'shield', 'small leather shield', 'a', 'shield', 'leather', 'small', 10, 3, 4.0, 50, 'a small leather shield', 1),
('a small wooden shield', 'small wooden shield', 'shield', 'small wooden shield', 'a', 'shield', 'wood', 'small', 11, 3, 4.0, 75, 'a small wooden shield', 1),
('a small metal shield', 'small metal shield', 'shield', 'small metal shield', 'a', 'shield', 'steel', 'small', 13, 4, 5.0, 200, 'a small metal shield', 1),
('a steel buckler', 'steel buckler', 'buckler', 'buckler', 'a', 'shield', 'steel', 'small', 10, 2, 3.0, 150, 'a steel buckler', 1),
('a target shield', 'target shield', 'shield', 'target shield', 'a', 'shield', 'steel', 'small', 12, 3, 4.0, 175, 'a target shield', 1),
('a medium leather shield', 'medium leather shield', 'shield', 'medium leather shield', 'a', 'shield', 'leather', 'medium', 16, 7, 7.0, 150, 'a medium leather shield', 1),
('a medium wooden shield', 'medium wooden shield', 'shield', 'medium wooden shield', 'a', 'shield', 'wood', 'medium', 17, 7, 7.0, 200, 'a medium wooden shield', 1),
('a medium metal shield', 'medium metal shield', 'shield', 'medium metal shield', 'a', 'shield', 'steel', 'medium', 19, 8, 8.0, 400, 'a medium metal shield', 1),
('a heater shield', 'heater shield', 'shield', 'heater shield', 'a', 'shield', 'steel', 'medium', 18, 7, 7.0, 350, 'a heater shield', 1),
('a knight''s shield', 'knight''s shield', 'shield', 'knight''s shield', 'a', 'shield', 'steel', 'medium', 19, 8, 8.0, 500, 'a knight''s shield', 1),
('a large leather shield', 'large leather shield', 'shield', 'large leather shield', 'a', 'shield', 'leather', 'large', 22, 13, 10.0, 300, 'a large leather shield', 1),
('a large wooden shield', 'large wooden shield', 'shield', 'large wooden shield', 'a', 'shield', 'wood', 'large', 23, 13, 10.0, 400, 'a large wooden shield', 1),
('a large metal shield', 'large metal shield', 'shield', 'large metal shield', 'a', 'shield', 'steel', 'large', 25, 15, 12.0, 700, 'a large metal shield', 1),
('a kite shield', 'kite shield', 'shield', 'kite shield', 'a', 'shield', 'steel', 'large', 24, 14, 11.0, 600, 'a kite shield', 1),
('a mantlet', 'mantlet', 'mantlet', 'mantlet', 'a', 'shield', 'steel', 'large', 25, 15, 12.0, 750, 'a mantlet', 1),
('a tower shield', 'tower shield', 'shield', 'tower shield', 'a', 'shield', 'steel', 'tower', 30, 22, 16.0, 1200, 'a tower shield', 1),
('a pavise', 'pavise', 'pavise', 'pavise', 'a', 'shield', 'steel', 'tower', 31, 24, 18.0, 1400, 'a pavise', 1),
('a wall shield', 'wall shield', 'shield', 'wall shield', 'a', 'shield', 'steel', 'tower', 33, 26, 20.0, 1800, 'a wall shield', 1);

-- ============================================================
-- GEMS (68 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, gem_family, weight, value, description, is_stackable, is_template) VALUES
('a piece of blue ridge coral', 'blue ridge coral', 'coral', 'piece of blue ridge coral', 'a', 'gem', 'agate', 1, 25, 'a piece of blue ridge coral', 1, 1),
('a blood marble', 'blood marble', 'marble', 'blood marble', 'a', 'gem', 'agate', 1, 50, 'a blood marble', 1, 1),
('a piece of cat''s eye quartz', 'cat''s eye quartz', 'quartz', 'piece of cat''s eye quartz', 'a', 'gem', 'agate', 1, 50, 'a piece of cat''s eye quartz', 1, 1),
('a tigerfang crystal', 'tigerfang crystal', 'crystal', 'tigerfang crystal', 'a', 'gem', 'agate', 1, 75, 'a tigerfang crystal', 1, 1),
('a turquoise stone', 'turquoise stone', 'stone', 'turquoise stone', 'a', 'gem', 'agate', 1, 100, 'a turquoise stone', 1, 1),
('a leopard quartz', 'leopard quartz', 'quartz', 'leopard quartz', 'a', 'gem', 'agate', 1, 100, 'a leopard quartz', 1, 1),
('a piece of golden amber', 'golden amber', 'amber', 'piece of golden amber', 'a', 'gem', 'agate', 1, 125, 'a piece of golden amber', 1, 1),
('a smoky topaz', 'smoky topaz', 'topaz', 'smoky topaz', 'a', 'gem', 'agate', 1, 150, 'a smoky topaz', 1, 1),
('a blue lace agate', 'blue lace agate', 'agate', 'blue lace agate', 'a', 'gem', 'agate', 1, 50, 'a blue lace agate', 1, 1),
('a sardonyx stone', 'sardonyx stone', 'stone', 'sardonyx stone', 'a', 'gem', 'agate', 1, 75, 'a sardonyx stone', 1, 1),
('a small golden topaz', 'golden topaz', 'topaz', 'small golden topaz', 'a', 'gem', 'beryl', 1, 350, 'a small golden topaz', 1, 1),
('a pink topaz', 'pink topaz', 'topaz', 'pink topaz', 'a', 'gem', 'beryl', 1, 500, 'a pink topaz', 1, 1),
('an aquamarine gem', 'aquamarine gem', 'gem', 'aquamarine gem', 'an', 'gem', 'beryl', 1, 500, 'an aquamarine gem', 1, 1),
('a green malachite stone', 'green malachite', 'stone', 'green malachite stone', 'a', 'gem', 'beryl', 1, 200, 'a green malachite stone', 1, 1),
('a golden beryl gem', 'golden beryl gem', 'gem', 'golden beryl gem', 'a', 'gem', 'beryl', 1, 600, 'a golden beryl gem', 1, 1),
('a green beryl stone', 'green beryl stone', 'stone', 'green beryl stone', 'a', 'gem', 'beryl', 1, 350, 'a green beryl stone', 1, 1),
('a dark red-green bloodstone', 'red-green bloodstone', 'bloodstone', 'dark red-green bloodstone', 'a', 'gem', 'carbuncle', 1, 200, 'a dark red-green bloodstone', 1, 1),
('a deep red carbuncle', 'deep red carbuncle', 'carbuncle', 'deep red carbuncle', 'a', 'gem', 'carbuncle', 1, 350, 'a deep red carbuncle', 1, 1),
('a red carbuncle', 'red carbuncle', 'carbuncle', 'red carbuncle', 'a', 'gem', 'carbuncle', 1, 300, 'a red carbuncle', 1, 1),
('a violet sapphire', 'violet sapphire', 'sapphire', 'violet sapphire', 'a', 'gem', 'cordierite', 1, 1000, 'a violet sapphire', 1, 1),
('a blue sapphire', 'blue sapphire', 'sapphire', 'blue sapphire', 'a', 'gem', 'cordierite', 1, 1000, 'a blue sapphire', 1, 1),
('a star sapphire', 'star sapphire', 'sapphire', 'star sapphire', 'a', 'gem', 'cordierite', 1, 1500, 'a star sapphire', 1, 1),
('a pale blue moonstone', 'blue moonstone', 'moonstone', 'pale blue moonstone', 'a', 'gem', 'cordierite', 1, 150, 'a pale blue moonstone', 1, 1),
('a blue cordierite', 'blue cordierite', 'cordierite', 'blue cordierite', 'a', 'gem', 'cordierite', 1, 300, 'a blue cordierite', 1, 1),
('an uncut diamond', 'uncut diamond', 'diamond', 'uncut diamond', 'an', 'gem', 'diamond', 1, 2500, 'an uncut diamond', 1, 1),
('a white crystal', 'white crystal', 'crystal', 'white crystal', 'a', 'gem', 'diamond', 1, 75, 'a white crystal', 1, 1),
('a clear zircon', 'clear zircon', 'zircon', 'clear zircon', 'a', 'gem', 'diamond', 1, 200, 'a clear zircon', 1, 1),
('a rock crystal', 'rock crystal', 'crystal', 'rock crystal', 'a', 'gem', 'diamond', 1, 100, 'a rock crystal', 1, 1),
('a white opal', 'white opal', 'opal', 'white opal', 'a', 'gem', 'diamond', 1, 400, 'a white opal', 1, 1),
('an emerald', 'emerald', 'emerald', 'emerald', 'an', 'gem', 'emerald', 1, 2000, 'an emerald', 1, 1),
('a green aventurine stone', 'green aventurine', 'stone', 'green aventurine stone', 'a', 'gem', 'emerald', 1, 100, 'a green aventurine stone', 1, 1),
('a green jade', 'green jade', 'jade', 'green jade', 'a', 'gem', 'emerald', 1, 350, 'a green jade', 1, 1),
('a green tourmaline', 'green tourmaline', 'tourmaline', 'green tourmaline', 'a', 'gem', 'emerald', 1, 500, 'a green tourmaline', 1, 1),
('a green garnet', 'green garnet', 'garnet', 'green garnet', 'a', 'gem', 'emerald', 1, 600, 'a green garnet', 1, 1),
('a green chrysoberyl gem', 'green chrysoberyl', 'gem', 'green chrysoberyl gem', 'a', 'gem', 'emerald', 1, 400, 'a green chrysoberyl gem', 1, 1),
('a peridot', 'peridot', 'peridot', 'peridot', 'a', 'gem', 'emerald', 1, 250, 'a peridot', 1, 1),
('a dark red garnet', 'dark red garnet', 'garnet', 'dark red garnet', 'a', 'gem', 'garnet', 1, 300, 'a dark red garnet', 1, 1),
('a red spinel', 'red spinel', 'spinel', 'red spinel', 'a', 'gem', 'garnet', 1, 400, 'a red spinel', 1, 1),
('a star ruby', 'star ruby', 'ruby', 'star ruby', 'a', 'gem', 'garnet', 1, 1500, 'a star ruby', 1, 1),
('a ruby', 'ruby', 'ruby', 'ruby', 'a', 'gem', 'garnet', 1, 2000, 'a ruby', 1, 1),
('a fire opal', 'fire opal', 'opal', 'fire opal', 'a', 'gem', 'garnet', 1, 800, 'a fire opal', 1, 1),
('an almandine garnet', 'almandine garnet', 'garnet', 'almandine garnet', 'an', 'gem', 'garnet', 1, 500, 'an almandine garnet', 1, 1),
('some lapis lazuli', 'lapis lazuli', 'lazuli', 'lapis lazuli', 'some', 'gem', 'lapis', 1, 200, 'some lapis lazuli', 1, 1),
('some azurite', 'azurite', 'azurite', 'azurite', 'some', 'gem', 'lapis', 1, 75, 'some azurite', 1, 1),
('a shimmertine shard', 'shimmertine shard', 'shard', 'shimmertine shard', 'a', 'gem', 'lapis', 1, 150, 'a shimmertine shard', 1, 1),
('a blue tourmaline', 'blue tourmaline', 'tourmaline', 'blue tourmaline', 'a', 'gem', 'lapis', 1, 400, 'a blue tourmaline', 1, 1),
('some obsidian', 'obsidian', 'obsidian', 'obsidian', 'some', 'gem', 'obsidian', 1, 25, 'some obsidian', 1, 1),
('a black opal', 'black opal', 'opal', 'black opal', 'a', 'gem', 'obsidian', 1, 1000, 'a black opal', 1, 1),
('a jet black onyx', 'jet black onyx', 'onyx', 'jet black onyx', 'a', 'gem', 'obsidian', 1, 250, 'a jet black onyx', 1, 1),
('a piece of black hematite', 'black hematite', 'hematite', 'piece of black hematite', 'a', 'gem', 'obsidian', 1, 50, 'a piece of black hematite', 1, 1),
('a clear quartz', 'clear quartz', 'quartz', 'clear quartz', 'a', 'gem', 'quartz', 1, 50, 'a clear quartz', 1, 1),
('a rose quartz', 'rose quartz', 'quartz', 'rose quartz', 'a', 'gem', 'quartz', 1, 75, 'a rose quartz', 1, 1),
('a citrine quartz', 'citrine quartz', 'quartz', 'citrine quartz', 'a', 'gem', 'quartz', 1, 100, 'a citrine quartz', 1, 1),
('an amethyst', 'amethyst', 'amethyst', 'amethyst', 'an', 'gem', 'quartz', 1, 200, 'an amethyst', 1, 1),
('a smoky quartz', 'smoky quartz', 'quartz', 'smoky quartz', 'a', 'gem', 'quartz', 1, 75, 'a smoky quartz', 1, 1),
('a small white pearl', 'white pearl', 'pearl', 'small white pearl', 'a', 'gem', 'pearl', 1, 150, 'a small white pearl', 1, 1),
('a large white pearl', 'large white pearl', 'pearl', 'large white pearl', 'a', 'gem', 'pearl', 1, 350, 'a large white pearl', 1, 1),
('a pink pearl', 'pink pearl', 'pearl', 'pink pearl', 'a', 'gem', 'pearl', 1, 500, 'a pink pearl', 1, 1),
('a black pearl', 'black pearl', 'pearl', 'black pearl', 'a', 'gem', 'pearl', 1, 800, 'a black pearl', 1, 1),
('a golden pearl', 'golden pearl', 'pearl', 'golden pearl', 'a', 'gem', 'pearl', 1, 600, 'a golden pearl', 1, 1),
('a chrysoberyl gem', 'chrysoberyl gem', 'gem', 'chrysoberyl gem', 'a', 'gem', 'misc', 1, 300, 'a chrysoberyl gem', 1, 1),
('an alexandrite stone', 'alexandrite stone', 'stone', 'alexandrite stone', 'an', 'gem', 'misc', 1, 1500, 'an alexandrite stone', 1, 1),
('a piece of jasper', 'piece of jasper', 'jasper', 'piece of jasper', 'a', 'gem', 'misc', 1, 75, 'a piece of jasper', 1, 1),
('a piece of carnelian quartz', 'carnelian quartz', 'quartz', 'piece of carnelian quartz', 'a', 'gem', 'misc', 1, 100, 'a piece of carnelian quartz', 1, 1),
('an aventurine', 'aventurine', 'aventurine', 'aventurine', 'an', 'gem', 'misc', 1, 100, 'an aventurine', 1, 1),
('an ametrine gem', 'ametrine gem', 'gem', 'ametrine gem', 'an', 'gem', 'misc', 1, 250, 'an ametrine gem', 1, 1),
('an opal', 'opal', 'opal', 'opal', 'an', 'gem', 'misc', 1, 400, 'an opal', 1, 1),
('a dragonfire opal', 'dragonfire opal', 'opal', 'dragonfire opal', 'a', 'gem', 'misc', 1, 2000, 'a dragonfire opal', 1, 1),
('a moonstone', 'moonstone', 'moonstone', 'moonstone', 'a', 'gem', 'misc', 1, 150, 'a moonstone', 1, 1),
('a sunstone', 'sunstone', 'sunstone', 'sunstone', 'a', 'gem', 'misc', 1, 200, 'a sunstone', 1, 1),
('a piece of jade', 'piece of jade', 'jade', 'piece of jade', 'a', 'gem', 'misc', 1, 250, 'a piece of jade', 1, 1),
('an uncut ruby', 'uncut ruby', 'ruby', 'uncut ruby', 'an', 'gem', 'garnet', 1, 1500, 'an uncut ruby', 1, 1),
('an uncut emerald', 'uncut emerald', 'emerald', 'uncut emerald', 'an', 'gem', 'emerald', 1, 1500, 'an uncut emerald', 1, 1);

-- ============================================================
-- HERBS (24 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, herb_heal_type, herb_heal_amount, weight, value, description, is_stackable, is_template) VALUES
('a sprig of acantha leaf', 'acantha leaf', 'leaf', 'sprig of acantha leaf', 'a', 'herb', 'health', 10, 1, 50, 'a sprig of acantha leaf', 1, 1),
('a stem of ambrominas leaf', 'ambrominas leaf', 'leaf', 'stem of ambrominas leaf', 'a', 'herb', 'health', 25, 1, 200, 'a stem of ambrominas leaf', 1, 1),
('a sprig of cactacae spine', 'cactacae spine', 'spine', 'sprig of cactacae spine', 'a', 'herb', 'head', 0, 1, 100, 'a sprig of cactacae spine', 1, 1),
('some wolifrew lichen', 'wolifrew lichen', 'lichen', 'some wolifrew lichen', 'some', 'herb', 'head', 0, 1, 300, 'some wolifrew lichen', 1, 1),
('a sprig of torban leaf', 'torban leaf', 'leaf', 'sprig of torban leaf', 'a', 'herb', 'neck', 0, 1, 100, 'a sprig of torban leaf', 1, 1),
('some pothinir grass', 'pothinir grass', 'grass', 'some pothinir grass', 'some', 'herb', 'chest', 0, 1, 100, 'some pothinir grass', 1, 1),
('some brostheras potion', 'brostheras potion', 'potion', 'some brostheras potion', 'some', 'herb', 'chest', 0, 1, 300, 'some brostheras potion', 1, 1),
('some woth flower', 'woth flower', 'flower', 'some woth flower', 'some', 'herb', 'abdomen', 0, 1, 100, 'some woth flower', 1, 1),
('some ephlox moss', 'ephlox moss', 'moss', 'some ephlox moss', 'some', 'herb', 'right_leg', 0, 1, 75, 'some ephlox moss', 1, 1),
('some haphip root', 'haphip root', 'root', 'some haphip root', 'some', 'herb', 'left_arm', 0, 1, 75, 'some haphip root', 1, 1),
('a sprig of aloeas stem', 'aloeas stem', 'stem', 'sprig of aloeas stem', 'a', 'herb', 'left_leg', 0, 1, 75, 'a sprig of aloeas stem', 1, 1),
('some basal moss', 'basal moss', 'moss', 'some basal moss', 'some', 'herb', 'right_arm', 0, 1, 75, 'some basal moss', 1, 1),
('some rose-marrow potion', 'rose-marrow potion', 'potion', 'some rose-marrow potion', 'some', 'herb', 'right_eye', 0, 1, 200, 'some rose-marrow potion', 1, 1),
('some sovyn clove', 'sovyn clove', 'clove', 'some sovyn clove', 'some', 'herb', 'left_eye', 0, 1, 200, 'some sovyn clove', 1, 1),
('some wingstem potion', 'wingstem potion', 'potion', 'some wingstem potion', 'some', 'herb', 'nerves', 0, 1, 300, 'some wingstem potion', 1, 1),
('some bolmara potion', 'bolmara potion', 'potion', 'some bolmara potion', 'some', 'herb', 'nerves', 0, 1, 600, 'some bolmara potion', 1, 1),
('some redite ore', 'redite ore', 'ore', 'some redite ore', 'some', 'herb', 'blood', 0, 1, 250, 'some redite ore', 1, 1),
('some troll''s blood potion', 'troll''s blood', 'potion', 'some troll''s blood potion', 'some', 'herb', 'scars', 0, 1, 500, 'some troll''s blood potion', 1, 1),
('some talneo potion', 'talneo potion', 'potion', 'some talneo potion', 'some', 'herb', 'back', 0, 1, 100, 'some talneo potion', 1, 1),
('some calamia fruit', 'calamia fruit', 'fruit', 'some calamia fruit', 'some', 'herb', 'left_hand', 0, 1, 75, 'some calamia fruit', 1, 1),
('some tkaro root', 'tkaro root', 'root', 'some tkaro root', 'some', 'herb', 'right_hand', 0, 1, 75, 'some tkaro root', 1, 1),
('some yabathilium fruit', 'yabathilium fruit', 'fruit', 'some yabathilium fruit', 'some', 'herb', 'health', 50, 1, 750, 'some yabathilium fruit', 1, 1),
('some cuctucae berry', 'cuctucae berry', 'berry', 'some cuctucae berry', 'some', 'herb', 'health', 15, 1, 75, 'some cuctucae berry', 1, 1),
('some wekaf berries', 'wekaf berries', 'berries', 'some wekaf berries', 'some', 'herb', 'health', 5, 1, 25, 'some wekaf berries', 1, 1);

-- ============================================================
-- LOCKPICKS (18 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, lockpick_modifier, weight, value, description, is_template) VALUES
('a crude lockpick', 'crude lockpick', 'lockpick', 'crude lockpick', 'a', 'misc', NULL, 5.00, 1, 50, 'a crude lockpick', 1),
('a simple lockpick', 'simple lockpick', 'lockpick', 'simple lockpick', 'a', 'misc', NULL, 10.00, 1, 100, 'a simple lockpick', 1),
('a standard lockpick', 'standard lockpick', 'lockpick', 'standard lockpick', 'a', 'misc', NULL, 15.00, 1, 200, 'a standard lockpick', 1),
('a professional lockpick', 'professional lockpick', 'lockpick', 'professional lockpick', 'a', 'misc', NULL, 20.00, 1, 400, 'a professional lockpick', 1),
('a master''s lockpick', 'master''s lockpick', 'lockpick', 'master''s lockpick', 'a', 'misc', NULL, 25.00, 1, 800, 'a master''s lockpick', 1),
('a copper lockpick', 'copper lockpick', 'lockpick', 'copper lockpick', 'a', 'misc', 'copper', 10.00, 1, 150, 'a copper lockpick', 1),
('a bronze lockpick', 'bronze lockpick', 'lockpick', 'bronze lockpick', 'a', 'misc', 'bronze', 15.00, 1, 250, 'a bronze lockpick', 1),
('a steel lockpick', 'steel lockpick', 'lockpick', 'steel lockpick', 'a', 'misc', 'steel', 20.00, 1, 500, 'a steel lockpick', 1),
('a mithril lockpick', 'mithril lockpick', 'lockpick', 'mithril lockpick', 'a', 'misc', 'mithril', 30.00, 1, 2000, 'a mithril lockpick', 1),
('a vultite lockpick', 'vultite lockpick', 'lockpick', 'vultite lockpick', 'a', 'misc', 'vultite', 35.00, 1, 5000, 'a vultite lockpick', 1),
('a laje lockpick', 'laje lockpick', 'lockpick', 'laje lockpick', 'a', 'misc', 'laje', 30.00, 1, 3000, 'a laje lockpick', 1),
('an ora lockpick', 'ora lockpick', 'lockpick', 'ora lockpick', 'an', 'misc', 'ora', 25.00, 1, 1500, 'an ora lockpick', 1),
('a veniom lockpick', 'veniom lockpick', 'lockpick', 'veniom lockpick', 'a', 'misc', 'veniom', 40.00, 1, 10000, 'a veniom lockpick', 1),
('a rolaren lockpick', 'rolaren lockpick', 'lockpick', 'rolaren lockpick', 'a', 'misc', 'rolaren', 35.00, 1, 7500, 'a rolaren lockpick', 1),
('an alum lockpick', 'alum lockpick', 'lockpick', 'alum lockpick', 'an', 'misc', 'alum', 25.00, 1, 1200, 'an alum lockpick', 1),
('an invar lockpick', 'invar lockpick', 'lockpick', 'invar lockpick', 'an', 'misc', 'invar', 25.00, 1, 1200, 'an invar lockpick', 1),
('a kelyn lockpick', 'kelyn lockpick', 'lockpick', 'kelyn lockpick', 'a', 'misc', 'kelyn', 30.00, 1, 2500, 'a kelyn lockpick', 1),
('a glaes lockpick', 'glaes lockpick', 'lockpick', 'glaes lockpick', 'a', 'misc', 'glaes', 35.00, 1, 6000, 'a glaes lockpick', 1);

-- ============================================================
-- CONTAINERS (22 items - treasure + wearable)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, container_capacity, weight, value, description, is_template) VALUES
('a small chest', 'small chest', 'chest', 'small chest', 'a', 'container', 5, 3, 0, 'a small chest', 1),
('a medium chest', 'medium chest', 'chest', 'medium chest', 'a', 'container', 8, 5, 0, 'a medium chest', 1),
('a large chest', 'large chest', 'chest', 'large chest', 'a', 'container', 12, 8, 0, 'a large chest', 1),
('a metal strongbox', 'metal strongbox', 'strongbox', 'metal strongbox', 'a', 'container', 5, 6, 0, 'a metal strongbox', 1),
('an enruned strongbox', 'enruned strongbox', 'strongbox', 'enruned strongbox', 'an', 'container', 5, 6, 0, 'an enruned strongbox', 1),
('a wooden coffer', 'wooden coffer', 'coffer', 'wooden coffer', 'a', 'container', 4, 2, 0, 'a wooden coffer', 1),
('an iron coffer', 'iron coffer', 'coffer', 'iron coffer', 'an', 'container', 4, 4, 0, 'an iron coffer', 1),
('a mithril coffer', 'mithril coffer', 'coffer', 'mithril coffer', 'a', 'container', 4, 3, 0, 'a mithril coffer', 1),
('a small steel lockbox', 'steel lockbox', 'lockbox', 'small steel lockbox', 'a', 'container', 3, 4, 0, 'a small steel lockbox', 1),
('an ornate brass box', 'ornate brass box', 'box', 'ornate brass box', 'an', 'container', 4, 3, 0, 'an ornate brass box', 1),
('a dented iron box', 'dented iron box', 'box', 'dented iron box', 'a', 'container', 3, 4, 0, 'a dented iron box', 1),
('a heavy steel trunk', 'heavy steel trunk', 'trunk', 'heavy steel trunk', 'a', 'container', 10, 12, 0, 'a heavy steel trunk', 1),
('a small leather pouch', 'small leather pouch', 'pouch', 'small leather pouch', 'a', 'container', 5, 1, 50, 'a small leather pouch', 1),
('a leather backpack', 'leather backpack', 'backpack', 'leather backpack', 'a', 'container', 20, 3, 200, 'a leather backpack', 1),
('a large sack', 'large sack', 'sack', 'large sack', 'a', 'container', 15, 2, 75, 'a large sack', 1),
('a belt pouch', 'belt pouch', 'pouch', 'belt pouch', 'a', 'container', 5, 1, 30, 'a belt pouch', 1),
('an herb pouch', 'herb pouch', 'pouch', 'herb pouch', 'an', 'container', 10, 1, 100, 'an herb pouch', 1),
('a gem pouch', 'gem pouch', 'pouch', 'gem pouch', 'a', 'container', 20, 1, 150, 'a gem pouch', 1),
('an adventurer''s cloak', 'adventurer''s cloak', 'cloak', 'adventurer''s cloak', 'an', 'container', 10, 2, 300, 'an adventurer''s cloak', 1),
('a weapon harness', 'weapon harness', 'harness', 'weapon harness', 'a', 'container', 4, 3, 500, 'a weapon harness', 1),
('a small wooden box', 'small wooden box', 'box', 'small wooden box', 'a', 'container', 6, 2, 20, 'a small wooden box', 1),
('a traveler''s pack', 'traveler''s pack', 'pack', 'traveler''s pack', 'a', 'container', 25, 4, 400, 'a traveler''s pack', 1);

-- ============================================================
-- MISC ITEMS - Ores (15 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, weight, value, description, is_template) VALUES
('a chunk of iron ore', 'iron ore', 'ore', 'iron ore', 'a', 'misc', 3, 10, 'a chunk of iron ore', 1),
('a chunk of copper ore', 'copper ore', 'ore', 'copper ore', 'a', 'misc', 3, 15, 'a chunk of copper ore', 1),
('a chunk of silver ore', 'silver ore', 'ore', 'silver ore', 'a', 'misc', 3, 50, 'a chunk of silver ore', 1),
('a chunk of gold ore', 'gold ore', 'ore', 'gold ore', 'a', 'misc', 3, 100, 'a chunk of gold ore', 1),
('a chunk of mithril ore', 'mithril ore', 'ore', 'mithril ore', 'a', 'misc', 2, 500, 'a chunk of mithril ore', 1),
('a chunk of vultite ore', 'vultite ore', 'ore', 'vultite ore', 'a', 'misc', 2, 1000, 'a chunk of vultite ore', 1),
('a chunk of ora ore', 'ora ore', 'ore', 'ora ore', 'a', 'misc', 3, 200, 'a chunk of ora ore', 1),
('a chunk of imflass ore', 'imflass ore', 'ore', 'imflass ore', 'a', 'misc', 2, 400, 'a chunk of imflass ore', 1),
('a chunk of invar ore', 'invar ore', 'ore', 'invar ore', 'a', 'misc', 3, 200, 'a chunk of invar ore', 1),
('a chunk of kelyn ore', 'kelyn ore', 'ore', 'kelyn ore', 'a', 'misc', 3, 350, 'a chunk of kelyn ore', 1),
('a chunk of rolaren ore', 'rolaren ore', 'ore', 'rolaren ore', 'a', 'misc', 2, 2000, 'a chunk of rolaren ore', 1),
('a chunk of laje ore', 'laje ore', 'ore', 'laje ore', 'a', 'misc', 2, 800, 'a chunk of laje ore', 1),
('a chunk of faenor ore', 'faenor ore', 'ore', 'faenor ore', 'a', 'misc', 2, 3000, 'a chunk of faenor ore', 1),
('a shard of glaes', 'glaes shard', 'shard', 'glaes shard', 'a', 'misc', 2, 1500, 'a shard of glaes', 1),
('a chunk of eahnor ore', 'eahnor ore', 'ore', 'eahnor ore', 'a', 'misc', 2, 5000, 'a chunk of eahnor ore', 1);

-- ============================================================
-- MISC ITEMS - Skins (10 items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, weight, value, description, is_template) VALUES
('a tattered kobold skin', 'tattered kobold skin', 'skin', 'tattered kobold skin', 'a', 'skin', 2, 10, 'a tattered kobold skin', 1),
('a rat pelt', 'rat pelt', 'pelt', 'rat pelt', 'a', 'skin', 1, 5, 'a rat pelt', 1),
('a wolf pelt', 'wolf pelt', 'pelt', 'wolf pelt', 'a', 'skin', 3, 50, 'a wolf pelt', 1),
('a bear skin', 'bear skin', 'skin', 'bear skin', 'a', 'skin', 5, 100, 'a bear skin', 1),
('a troll hide', 'troll hide', 'hide', 'troll hide', 'a', 'skin', 6, 150, 'a troll hide', 1),
('a worm skin', 'worm skin', 'skin', 'worm skin', 'a', 'skin', 4, 75, 'a worm skin', 1),
('a basilisk skin', 'basilisk skin', 'skin', 'basilisk skin', 'a', 'skin', 5, 200, 'a basilisk skin', 1),
('some cockatrice feathers', 'cockatrice feathers', 'feathers', 'cockatrice feathers', 'some', 'skin', 1, 100, 'some cockatrice feathers', 1),
('a manticore mane', 'manticore mane', 'mane', 'manticore mane', 'a', 'skin', 3, 250, 'a manticore mane', 1),
('a griffin feather', 'griffin feather', 'feather', 'griffin feather', 'a', 'skin', 1, 500, 'a griffin feather', 1);

-- ============================================================
-- MISC ITEMS - Tools, Lights, Scrolls, Food, Drink, etc (40+ items)
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, weight, value, description, is_template) VALUES
('a shovel', 'shovel', 'shovel', 'shovel', 'a', 'misc', 4, 25, 'a shovel', 1),
('a pickaxe', 'pickaxe', 'pickaxe', 'pickaxe', 'a', 'misc', 5, 30, 'a pickaxe', 1),
('a fishing pole', 'fishing pole', 'pole', 'fishing pole', 'a', 'misc', 3, 20, 'a fishing pole', 1),
('a hammer', 'hammer', 'hammer', 'hammer', 'a', 'misc', 3, 15, 'a hammer', 1),
('a pair of tongs', 'tongs', 'tongs', 'tongs', 'a', 'misc', 2, 15, 'a pair of tongs', 1),
('a forging anvil', 'forging anvil', 'anvil', 'forging anvil', 'a', 'misc', 20, 100, 'a forging anvil', 1),
('a pair of scissors', 'scissors', 'scissors', 'scissors', 'a', 'misc', 1, 10, 'a pair of scissors', 1),
('a needle and thread', 'needle and thread', 'thread', 'needle and thread', 'a', 'misc', 1, 5, 'a needle and thread', 1),
('a coil of rope', 'coil of rope', 'rope', 'rope', 'a', 'misc', 3, 15, 'a coil of rope', 1),
('a grappling hook', 'grappling hook', 'hook', 'grapple', 'a', 'misc', 3, 50, 'a grappling hook', 1),
('a wooden torch', 'wooden torch', 'torch', 'torch', 'a', 'misc', 2, 5, 'a wooden torch', 1),
('an oil lantern', 'oil lantern', 'lantern', 'oil lantern', 'an', 'misc', 3, 50, 'an oil lantern', 1),
('a glowing glowbark wand', 'glowbark wand', 'wand', 'glowbark wand', 'a', 'misc', 1, 200, 'a glowing glowbark wand', 1);

INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, weight, value, description, is_stackable, is_template) VALUES
('a crinkled minor spirit scroll', 'minor spirit scroll', 'scroll', 'minor spirit scroll', 'a', 'scroll', 1, 100, 'a crinkled minor spirit scroll', 0, 1),
('a weathered major spirit scroll', 'major spirit scroll', 'scroll', 'major spirit scroll', 'a', 'scroll', 1, 200, 'a weathered major spirit scroll', 0, 1),
('an arcane wizard scroll', 'wizard scroll', 'scroll', 'wizard scroll', 'an', 'scroll', 1, 250, 'an arcane wizard scroll', 0, 1),
('a dark sorcerer scroll', 'sorcerer scroll', 'scroll', 'sorcerer scroll', 'a', 'scroll', 1, 300, 'a dark sorcerer scroll', 0, 1),
('a blessed cleric scroll', 'cleric scroll', 'scroll', 'cleric scroll', 'a', 'scroll', 1, 200, 'a blessed cleric scroll', 0, 1),
('a glowing empath scroll', 'empath scroll', 'scroll', 'empath scroll', 'a', 'scroll', 1, 200, 'a glowing empath scroll', 0, 1),
('a leaf-bound ranger scroll', 'ranger scroll', 'scroll', 'ranger scroll', 'a', 'scroll', 1, 150, 'a leaf-bound ranger scroll', 0, 1),
('a musical bard scroll', 'bard scroll', 'scroll', 'bard scroll', 'a', 'scroll', 1, 200, 'a musical bard scroll', 0, 1),
('a radiant paladin scroll', 'paladin scroll', 'scroll', 'paladin scroll', 'a', 'scroll', 1, 200, 'a radiant paladin scroll', 0, 1);

INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, weight, value, description, is_template) VALUES
('a small crystal runestone', 'crystal runestone', 'runestone', 'small crystal runestone', 'a', 'wand', 1, 50, 'a small crystal runestone', 1),
('a smooth grey runestone', 'grey runestone', 'runestone', 'smooth grey runestone', 'a', 'wand', 1, 150, 'a smooth grey runestone', 1),
('a glowing white runestone', 'white runestone', 'runestone', 'glowing white runestone', 'a', 'wand', 1, 300, 'a glowing white runestone', 1);

INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, weight, value, description, is_stackable, is_template) VALUES
('a piece of bread', 'piece of bread', 'bread', 'piece of bread', 'a', 'consumable', 1, 5, 'a piece of bread', 1, 1),
('a meat pie', 'meat pie', 'pie', 'meat pie', 'a', 'consumable', 1, 10, 'a meat pie', 1, 1),
('a roasted haunch', 'roasted haunch', 'haunch', 'roasted haunch', 'a', 'consumable', 2, 15, 'a roasted haunch', 1, 1),
('a piece of elven waybread', 'elven waybread', 'waybread', 'elven waybread', 'a', 'consumable', 1, 50, 'a piece of elven waybread', 1, 1),
('a biscuit', 'biscuit', 'biscuit', 'biscuit', 'a', 'consumable', 1, 3, 'a biscuit', 1, 1),
('a cheese wedge', 'cheese wedge', 'wedge', 'cheese wedge', 'a', 'consumable', 1, 8, 'a cheese wedge', 1, 1),
('an apple', 'apple', 'apple', 'apple', 'an', 'consumable', 1, 3, 'an apple', 1, 1),
('a flask of water', 'flask of water', 'flask', 'flask of water', 'a', 'consumable', 2, 5, 'a flask of water', 1, 1),
('a mug of ale', 'mug of ale', 'mug', 'mug of ale', 'a', 'consumable', 2, 10, 'a mug of ale', 1, 1),
('a bottle of wine', 'bottle of wine', 'bottle', 'bottle of wine', 'a', 'consumable', 2, 25, 'a bottle of wine', 1, 1),
('a flask of elven spirits', 'flask of elven spirits', 'flask', 'flask of elven spirits', 'a', 'consumable', 2, 100, 'a flask of elven spirits', 1, 1),
('a mug of dwarven stout', 'dwarven stout', 'mug', 'mug of dwarven stout', 'a', 'consumable', 2, 15, 'a mug of dwarven stout', 1, 1);

-- ============================================================
-- MISC ITEMS - Jewelry, Wands, Trinkets
-- ============================================================
INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, weight, value, description, is_template) VALUES
('a silver wand', 'silver wand', 'wand', 'silver wand', 'a', 'wand', 1, 500, 'a silver wand', 1),
('a gold ring', 'gold ring', 'ring', 'gold ring', 'a', 'jewelry', 1, 200, 'a gold ring', 1),
('a silver ring', 'silver ring', 'ring', 'silver ring', 'a', 'jewelry', 1, 50, 'a silver ring', 1),
('a gold necklace', 'gold necklace', 'necklace', 'gold necklace', 'a', 'jewelry', 1, 400, 'a gold necklace', 1),
('a silver bracelet', 'silver bracelet', 'bracelet', 'silver bracelet', 'a', 'jewelry', 1, 75, 'a silver bracelet', 1),
('a gold bracelet', 'gold bracelet', 'bracelet', 'gold bracelet', 'a', 'jewelry', 1, 300, 'a gold bracelet', 1),
('a crystal amulet', 'crystal amulet', 'amulet', 'crystal amulet', 'a', 'jewelry', 1, 150, 'a crystal amulet', 1),
('an ivory comb', 'ivory comb', 'comb', 'ivory comb', 'an', 'misc', 1, 30, 'an ivory comb', 1),
('a set of bone dice', 'bone dice', 'dice', 'bone dice', 'a', 'misc', 1, 10, 'a set of bone dice', 1),
('a prayer bead necklace', 'prayer beads', 'necklace', 'prayer bead necklace', 'a', 'misc', 1, 25, 'a prayer bead necklace', 1);

-- Done! Verify counts:
SELECT item_type, COUNT(*) as count FROM items WHERE is_template = 1 GROUP BY item_type ORDER BY item_type;
SELECT CONCAT('Total item templates: ', COUNT(*)) as summary FROM items WHERE is_template = 1;
