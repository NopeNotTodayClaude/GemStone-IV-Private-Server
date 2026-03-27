-- Migration: add age column to characters table
USE gemstone_dev;

ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS age SMALLINT UNSIGNED DEFAULT 0 AFTER gender;

-- Set default ages for existing characters based on race_id
-- Elves/Dark Elves/Sylvankind: 50, Dwarves: 50, Halflings/Gnomes: 30, all others: 20
UPDATE characters SET age = CASE
    WHEN race_id IN (2, 3, 10) THEN 50   -- Elf, Dark Elf, Sylvankind
    WHEN race_id = 5            THEN 50   -- Dwarf
    WHEN race_id IN (6, 8, 9)   THEN 30   -- Halfling, Forest Gnome, Burghal Gnome
    ELSE 20                               -- Human, Half-Elf, Giantman, Aelotoi, Erithian, Half-Krolvin
END
WHERE age = 0;

SELECT 'Age column added.' AS status;
SELECT id, name, race_id, age FROM characters LIMIT 10;
