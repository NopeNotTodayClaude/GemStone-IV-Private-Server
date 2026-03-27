-- Migration: Add missing Timmorain Bridge room (5829)
-- Fixes broken Vermilion Gate -> Cemetery connection

USE gemstone_dev;

-- Ensure zone 4 exists first (foreign key requirement)
INSERT INTO zones (id, slug, name, region, level_min, level_max, climate, is_enabled)
VALUES (4, 'timmorain_road', 'Timmorain Road', 'Elanith', 1, 5, 'temperate', TRUE)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- Now insert the missing bridge room
INSERT INTO rooms (id, zone_id, title, is_safe, is_supernode, is_indoor, terrain_type)
VALUES (5829, 4, 'Timmorain Road, Limestone Bridge', FALSE, FALSE, FALSE, 'outdoor')
ON DUPLICATE KEY UPDATE title = VALUES(title);
