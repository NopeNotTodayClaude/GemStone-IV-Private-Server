-- Skills seed data
USE gemstone_dev;

CREATE TABLE IF NOT EXISTS skills (
    id              SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(64) NOT NULL UNIQUE,
    category        ENUM('combat', 'magic', 'survival', 'general', 'lore') NOT NULL,
    tp_type         ENUM('physical', 'mental') NOT NULL,
    description     TEXT
) ENGINE=InnoDB;

INSERT INTO skills (name, category, tp_type, description) VALUES
-- Combat Skills
('Two Weapon Combat',       'combat',   'physical', 'Ability to fight with a weapon in each hand.'),
('Armor Use',               'combat',   'physical', 'Proficiency wearing heavier armor types.'),
('Shield Use',              'combat',   'physical', 'Skill with shields of all sizes.'),
('Combat Maneuvers',        'combat',   'physical', 'Training in specialized combat techniques.'),
('Edged Weapons',           'combat',   'physical', 'Skill with swords, daggers, and other edged weapons.'),
('Blunt Weapons',           'combat',   'physical', 'Skill with maces, hammers, and clubs.'),
('Two-Handed Weapons',      'combat',   'physical', 'Skill with greatswords, halberds, and mauls.'),
('Ranged Weapons',          'combat',   'physical', 'Skill with bows, crossbows, and thrown weapons.'),
('Thrown Weapons',           'combat',   'physical', 'Skill with throwing axes, daggers, and javelins.'),
('Polearm Weapons',         'combat',   'physical', 'Skill with spears, tridents, and polearms.'),
('Brawling',                'combat',   'physical', 'Skill in unarmed combat.'),
('Multi Opponent Combat',   'combat',   'physical', 'Ability to handle multiple enemies.'),
('Physical Fitness',        'combat',   'physical', 'General physical conditioning, affects health.'),
('Dodging',                 'combat',   'physical', 'Ability to evade attacks.'),

-- Magic Skills
('Arcane Symbols',          'magic',    'mental',   'Understanding of magical glyphs and runes.'),
('Magic Item Use',          'magic',    'mental',   'Proficiency activating scrolls, wands, and magic items.'),
('Spell Aiming',            'magic',    'mental',   'Accuracy with bolt and beam spells.'),
('Harness Power',           'magic',    'mental',   'Ability to draw and store mana.'),
('Elemental Mana Control',  'magic',    'mental',   'Control over elemental mana flows.'),
('Spirit Mana Control',     'magic',    'mental',   'Control over spiritual mana flows.'),
('Mental Mana Control',     'magic',    'mental',   'Control over mental mana flows.'),
('Spell Research',          'magic',    'mental',   'Scholarly pursuit of new spells.'),

-- Survival Skills
('Survival',                'survival', 'physical', 'Wilderness survival, foraging, and skinning.'),
('Disarming Traps',         'survival', 'physical', 'Detecting and disarming mechanical traps.'),
('Picking Locks',           'survival', 'physical', 'Opening locks without a key.'),
('Stalking and Hiding',     'survival', 'physical', 'Stealth movement and concealment.'),
('Perception',              'survival', 'mental',   'Awareness of surroundings, finding hidden things.'),
('Climbing',                'survival', 'physical', 'Scaling walls, cliffs, and trees.'),
('Swimming',                'survival', 'physical', 'Moving through water.'),

-- General Skills
('First Aid',               'general',  'mental',   'Tending wounds and applying herbs.'),
('Trading',                 'general',  'mental',   'Haggling and merchant interaction.'),
('Pickpocketing',           'general',  'physical', 'Stealing from NPCs and players.'),

-- Lore Skills
('Spiritual Lore - Blessings',   'lore', 'mental', 'Knowledge of spiritual blessings and protections.'),
('Spiritual Lore - Religion',    'lore', 'mental', 'Knowledge of the Arkati and divine practices.'),
('Spiritual Lore - Summoning',   'lore', 'mental', 'Knowledge of summoning spirits and entities.'),
('Elemental Lore - Air',         'lore', 'mental', 'Knowledge of air elemental magic.'),
('Elemental Lore - Earth',       'lore', 'mental', 'Knowledge of earth elemental magic.'),
('Elemental Lore - Fire',        'lore', 'mental', 'Knowledge of fire elemental magic.'),
('Elemental Lore - Water',       'lore', 'mental', 'Knowledge of water elemental magic.'),
('Mental Lore - Manipulation',   'lore', 'mental', 'Knowledge of mental manipulation techniques.'),
('Mental Lore - Telepathy',      'lore', 'mental', 'Knowledge of telepathic communication.'),
('Mental Lore - Transference',   'lore', 'mental', 'Knowledge of mental energy transference.'),
('Ambush',                       'combat','physical','Precision strikes from hiding and aimed attack training.'),
('Mental Lore - Divination',     'lore', 'mental', 'Knowledge of foresight, omens, and predictive mental insight.'),
('Mental Lore - Transformation', 'lore', 'mental', 'Knowledge of reshaping the body through will and focus.'),
('Sorcerous Lore - Demonology',  'lore', 'mental', 'Knowledge of demonic entities, bargains, and summoning.'),
('Sorcerous Lore - Necromancy',  'lore', 'mental', 'Knowledge of undeath, corpses, and gravebound magic.');
