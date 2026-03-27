-- Migration: add extra_data JSON column to character_inventory
-- Stores per-instance item state (lockpick condition, charges, etc.)
-- Run once against gemstone_dev

USE gemstone_dev;

ALTER TABLE character_inventory
    ADD COLUMN extra_data JSON NULL DEFAULT NULL
    COMMENT 'Per-instance item state: lockpick condition, wand charges, etc.';
