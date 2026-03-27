-- Migration: Add tutorial tracking fields to characters table
-- These fields track the new player tutorial quest progress

ALTER TABLE characters ADD COLUMN IF NOT EXISTS tutorial_stage INT NOT NULL DEFAULT 0;
ALTER TABLE characters ADD COLUMN IF NOT EXISTS tutorial_complete TINYINT(1) NOT NULL DEFAULT 0;

-- Create index for finding characters still in tutorial
CREATE INDEX IF NOT EXISTS idx_characters_tutorial ON characters (tutorial_complete, tutorial_stage);
