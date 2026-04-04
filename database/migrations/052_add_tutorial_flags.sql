ALTER TABLE characters
    ADD COLUMN tutorial_flags TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER tutorial_stage;

UPDATE characters
SET tutorial_flags =
    (CASE WHEN tutorial_stage = 12 THEN 1 ELSE 0 END) +
    (CASE WHEN tutorial_stage = 23 THEN 2 ELSE 0 END) +
    (CASE WHEN tutorial_stage = 31 THEN 4 ELSE 0 END) +
    (CASE WHEN tutorial_stage = 44 THEN 8 ELSE 0 END) +
    (CASE WHEN tutorial_stage >= 53 THEN 16 ELSE 0 END)
WHERE tutorial_flags = 0;
