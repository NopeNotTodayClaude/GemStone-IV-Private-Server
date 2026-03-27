-- Playable Races seed data
USE gemstone_dev;

CREATE TABLE IF NOT EXISTS races (
    id              TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(32) NOT NULL UNIQUE,
    description     TEXT,
    -- Stat modifiers (added to base stats)
    mod_strength    TINYINT DEFAULT 0,
    mod_constitution TINYINT DEFAULT 0,
    mod_dexterity   TINYINT DEFAULT 0,
    mod_agility     TINYINT DEFAULT 0,
    mod_discipline  TINYINT DEFAULT 0,
    mod_aura        TINYINT DEFAULT 0,
    mod_logic       TINYINT DEFAULT 0,
    mod_intuition   TINYINT DEFAULT 0,
    mod_wisdom      TINYINT DEFAULT 0,
    mod_influence   TINYINT DEFAULT 0,
    -- Spirit regeneration bonus
    spirit_regen_bonus TINYINT DEFAULT 0
) ENGINE=InnoDB;

INSERT INTO races (name, description, mod_strength, mod_constitution, mod_dexterity, mod_agility, mod_discipline, mod_aura, mod_logic, mod_intuition, mod_wisdom, mod_influence) VALUES
('Human',         'Adaptable and ambitious, humans are the most common race in Elanthia.',                0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
('Elf',           'Graceful and long-lived, elves are masters of magic and archery.',                    -5,  0,  5, 10, -5,  5,  0,  5,  0, -5),
('Dark Elf',      'Mysterious and cunning, dark elves dwell in the underground cities.',                 -5,  0, 10,  5,  5,  5,  0, -5, -5, -5),
('Half-Elf',      'Born of two worlds, half-elves blend human versatility with elven grace.',            -5,  0,  0,  5,  0,  0,  0,  5,  0,  0),
('Dwarf',         'Stout and stubborn, dwarves are master craftsmen and fierce warriors.',               10, 15, -5, -5, 10,  5, -5, -5,  0, -5),
('Halfling',      'Small but quick-witted, halflings are natural rogues and survivalists.',             -15,  0, 15, 10,  5, -5,  0, 10, -5, -5),
('Giantman',      'Towering and powerful, giantmen are unmatched in raw physical strength.',             15, 10, -5, -5,  5, -5, -5, -5, -5,  0),
('Forest Gnome',  'Clever tinkerers at home in the wild, forest gnomes are natural mages.',            -10, -5,  5,  5, -5, 10, 10, -5,  5, -5),
('Burghal Gnome', 'Urban gnomes with sharp minds and nimble fingers, natural lock-pickers.',           -10, -5, 10,  5,  0, -5, 10,  5, -5,  0),
('Sylvankind',    'Woodland elves deeply connected to nature and spiritual magic.',                     -5,  0,  0,  5,  0, 10,  0,  5,  5, -5),
('Aelotoi',       'Winged refugees from another realm, aelotoi are empathic and agile.',               -10, -5,  5, 10, -5,  5,  0,  5,  0, -5),
('Erithian',      'Disciplined scholars from the eastern continent of Atan Irith.',                     -5,  0,  0,  0, 10,  0, 10,  5, 10, -5),
('Half-Krolvin',  'Hardy half-breeds of humans and the seafaring Krolvin raiders.',                     10,  5,  5, -5,  0, -5, -5,  0, -5,  0);
