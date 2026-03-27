-- Migration: Rogue Picking Queue (Box Picking Service)
-- Run at: database/migrations/add_picking_queue.sql
-- Location: Shind's Locksmith, room 10434

USE gemstone_dev;

CREATE TABLE IF NOT EXISTS picking_queue (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Submitter
    owner_id            INT UNSIGNED NOT NULL,
    owner_name          VARCHAR(64) NOT NULL,

    -- Box data (full snapshot so item survives being out of inventory)
    item_id             INT UNSIGNED NOT NULL,          -- items.id for re-adding later
    item_name           VARCHAR(128) NOT NULL,
    item_short_name     VARCHAR(128) NOT NULL,
    item_data           JSON NOT NULL,                 -- full item dict snapshot
    original_inv_id     INT UNSIGNED DEFAULT NULL,     -- NULL after escrowed

    -- Fee offered by submitter
    offered_fee         INT UNSIGNED NOT NULL DEFAULT 0,

    -- Status
    status              ENUM('pending','claimed','completed','cancelled') NOT NULL DEFAULT 'pending',

    -- Claimer (rogue who took the job)
    claimer_id          INT UNSIGNED DEFAULT NULL,
    claimer_name        VARCHAR(64) DEFAULT NULL,
    claimer_inv_id      INT UNSIGNED DEFAULT NULL,     -- inv_id once given to rogue

    -- Timestamps
    submitted_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claimed_at          DATETIME DEFAULT NULL,
    completed_at        DATETIME DEFAULT NULL,
    expires_at          DATETIME NOT NULL DEFAULT (DATE_ADD(NOW(), INTERVAL 24 HOUR)),

    INDEX idx_status    (status),
    INDEX idx_owner     (owner_id),
    INDEX idx_claimer   (claimer_id),
    INDEX idx_expires   (expires_at)
) ENGINE=InnoDB;
