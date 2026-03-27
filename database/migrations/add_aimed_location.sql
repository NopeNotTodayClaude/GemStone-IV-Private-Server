-- Migration: add_aimed_location.sql
-- Adds the aimed_location column to characters so a player's AIM preference
-- persists across logins. NULL = random (no preference set).

ALTER TABLE characters
    ADD COLUMN aimed_location VARCHAR(32) NULL DEFAULT NULL
    COMMENT 'Persistent AIM preference. NULL = random. e.g. head, right arm, chest';
