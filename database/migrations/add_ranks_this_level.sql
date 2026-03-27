-- Migration: add ranks_this_level to character_skills
-- Tracks how many times each skill was trained in the current level.
-- Resets to 0 on level-up.
USE gemstone_dev;

ALTER TABLE character_skills
    ADD COLUMN IF NOT EXISTS ranks_this_level TINYINT UNSIGNED DEFAULT 0;
