-- ============================================================
-- Migration: add_convert_debt_tracking.sql
-- Adds lossless conversion debt tracking columns.
-- Run as root:
--   mysql -u root gemstone_dev < database\migrations\add_convert_debt_tracking.sql
-- ============================================================

USE gemstone_dev;

-- ptp_loaned: PTP currently borrowed from the MTP pool
--   Increases when player does CONVERT PTP n (spent 2n MTP, got n PTP)
--   Decreases/zeroed when player does CONVERT REFUND
-- mtp_loaned: MTP currently borrowed from the PTP pool
--   Increases when player does CONVERT MTP n (spent 2n PTP, got n MTP)
--   Decreases/zeroed when player does CONVERT REFUND
ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS ptp_loaned  SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS mtp_loaned  SMALLINT UNSIGNED NOT NULL DEFAULT 0;

SELECT 'Migration add_convert_debt_tracking.sql complete.' AS status;
