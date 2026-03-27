-- Migration: add_events_system.sql
-- Adds server_events table for tracking active world events,
-- and lumnis bonus tracking columns to characters.

-- ── Server-wide event state ───────────────────────────────────────────────────
-- One row per event type (lumnis, bonus_xp).
-- Written by EventManager scheduler, read by ExperienceManager on every pulse.

CREATE TABLE IF NOT EXISTS server_events (
    event_type      VARCHAR(32)  NOT NULL PRIMARY KEY
                    COMMENT 'lumnis | bonus_xp',
    is_active       TINYINT(1)   NOT NULL DEFAULT 0,
    started_at      DATETIME     NULL,
    expires_at      DATETIME     NULL,
    multiplier      DECIMAL(4,2) NOT NULL DEFAULT 1.00
                    COMMENT 'Active multiplier for this event',
    phase           TINYINT      NOT NULL DEFAULT 0
                    COMMENT 'Lumnis: 0=inactive 1=phase1 2=phase2',
    notes           VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Active world events (Lumnis, bonus XP, etc.)';

-- Seed with inactive rows so ExperienceManager always finds something
INSERT IGNORE INTO server_events (event_type, is_active, multiplier, phase)
VALUES
    ('lumnis',   0, 1.00, 0),
    ('bonus_xp', 0, 1.00, 0);

-- ── Per-character Lumnis state ────────────────────────────────────────────────
-- Tracks how much of the weekly bonus each character has consumed.
-- Resets when a new Lumnis cycle fires (started_at in server_events changes).

ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS lumnis_phase         TINYINT      NOT NULL DEFAULT 0
        COMMENT '0=inactive 1=phase1 2=phase2',
    ADD COLUMN IF NOT EXISTS lumnis_bonus_earned  INT          NOT NULL DEFAULT 0
        COMMENT 'Total bonus XP absorbed under current Lumnis cycle',
    ADD COLUMN IF NOT EXISTS lumnis_cycle_id      DATETIME     NULL
        COMMENT 'started_at of the Lumnis cycle this character is on — NULL if never set';
