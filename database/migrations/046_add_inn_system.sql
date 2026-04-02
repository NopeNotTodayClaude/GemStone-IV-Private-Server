-- Inn system persistence.
-- Run with:
--   mysql --protocol=TCP --skip-ssl -u root gemstone_dev < database/migrations/046_add_inn_system.sql

CREATE TABLE IF NOT EXISTS character_inn_stays (
    character_id INT NOT NULL,
    inn_id VARCHAR(64) NOT NULL,
    checked_in_room_id INT NOT NULL,
    private_room_id INT NULL,
    private_table_room_id INT NULL,
    room_latched TINYINT(1) NOT NULL DEFAULT 0,
    checked_in_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id),
    KEY idx_inn_id (inn_id),
    KEY idx_private_room (private_room_id),
    KEY idx_private_table (private_table_room_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS character_inn_access (
    id INT NOT NULL AUTO_INCREMENT,
    owner_character_id INT NOT NULL,
    guest_character_id INT NOT NULL,
    inn_id VARCHAR(64) NOT NULL,
    room_id INT NOT NULL,
    access_kind ENUM('room', 'table') NOT NULL,
    granted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_guest_room_kind (guest_character_id, room_id, access_kind),
    KEY idx_owner_room_kind (owner_character_id, room_id, access_kind),
    KEY idx_room_kind (room_id, access_kind)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
