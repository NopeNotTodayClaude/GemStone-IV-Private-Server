-- Professions seed data
USE gemstone_dev;

CREATE TABLE IF NOT EXISTS professions (
    id              TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(32) NOT NULL UNIQUE,
    description     TEXT,
    profession_type ENUM('pure', 'semi', 'square') NOT NULL,
    -- Primary stat affinities
    primary_stat    VARCHAR(32),
    mana_stat       VARCHAR(32) DEFAULT NULL,      -- stat that determines mana pool
    -- Base health/mana per level
    health_per_level TINYINT UNSIGNED DEFAULT 10,
    mana_per_level  TINYINT UNSIGNED DEFAULT 0,
    -- Spell circles available (comma-separated IDs)
    spell_circles   VARCHAR(128) DEFAULT NULL
) ENGINE=InnoDB;

INSERT INTO professions (name, description, profession_type, primary_stat, mana_stat, health_per_level, mana_per_level, spell_circles) VALUES
('Warrior',   'Masters of melee combat, warriors excel with all weapons and armor.',     'square', 'strength',    NULL,      15, 0,  NULL),
('Rogue',     'Stealthy and cunning, rogues specialize in ambush, locks, and traps.',    'square', 'dexterity',   NULL,      12, 0,  NULL),
('Wizard',    'Masters of elemental magic, wizards command devastating arcane power.',    'pure',   'aura',        'aura',     6, 4,  'wizard,minor_elemental,major_elemental'),
('Cleric',    'Servants of the Arkati, clerics wield spiritual power and healing.',       'pure',   'wisdom',      'wisdom',   8, 3,  'cleric,minor_spiritual,major_spiritual'),
('Empath',    'Healers who absorb the wounds of others through empathic transfer.',       'pure',   'influence',   'wisdom',   7, 3,  'empath,minor_spiritual,minor_mental'),
('Sorcerer',  'Dark casters who blend elemental and spiritual magic into sorcery.',       'pure',   'aura',        'aura',     7, 3,  'sorcerer,minor_elemental,minor_spiritual'),
('Ranger',    'Wilderness experts combining martial skill with nature magic.',            'semi',   'dexterity',   'wisdom',  10, 2,  'ranger,minor_spiritual'),
('Bard',      'Musicians and loremasters who weave magic through song and verse.',        'semi',   'influence',   'aura',     9, 2,  'bard,minor_elemental,minor_mental'),
('Paladin',   'Holy warriors who combine martial prowess with divine magic.',             'semi',   'strength',    'wisdom',  12, 2,  'paladin,minor_spiritual'),
('Monk',      'Disciplined martial artists who harness inner power through focus.',       'semi',   'agility',     'discipline', 11, 2, 'monk,minor_mental');
