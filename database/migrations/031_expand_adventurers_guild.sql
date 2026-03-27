-- 031_expand_adventurers_guild.sql
-- Additional Adventurer's Guild profile controls and richer bounty data.

ALTER TABLE character_adventurer_guild
    ADD COLUMN IF NOT EXISTS difficulty_preference VARCHAR(16) NOT NULL DEFAULT 'normal' AFTER lifetime_bounties,
    ADD COLUMN IF NOT EXISTS vouchers INT UNSIGNED NOT NULL DEFAULT 0 AFTER difficulty_preference,
    ADD COLUMN IF NOT EXISTS last_checkin_at DATETIME DEFAULT NULL AFTER vouchers,
    ADD COLUMN IF NOT EXISTS next_checkin_at DATETIME DEFAULT NULL AFTER last_checkin_at;

ALTER TABLE character_bounties
    ADD COLUMN IF NOT EXISTS bounty_key VARCHAR(96) DEFAULT NULL AFTER bounty_type,
    ADD COLUMN IF NOT EXISTS bounty_data JSON DEFAULT NULL AFTER reward_points,
    ADD COLUMN IF NOT EXISTS shared_from_character_id INT UNSIGNED DEFAULT NULL AFTER bounty_data;

CREATE INDEX IF NOT EXISTS idx_character_bounties_character_status_type
    ON character_bounties (character_id, status, bounty_type);
