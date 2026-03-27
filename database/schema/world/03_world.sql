-- World tables - zones, rooms, spawn points
USE gemstone_dev;

-- Zone registry (supplements Lua zone files)
CREATE TABLE IF NOT EXISTS zones (
    id              SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    slug            VARCHAR(64) NOT NULL UNIQUE,
    name            VARCHAR(128) NOT NULL,
    region          VARCHAR(64) DEFAULT 'Unknown',
    level_min       TINYINT UNSIGNED DEFAULT 1,
    level_max       TINYINT UNSIGNED DEFAULT 100,
    climate         VARCHAR(32) DEFAULT 'temperate',
    is_enabled      BOOLEAN DEFAULT TRUE,
    INDEX idx_slug (slug)
) ENGINE=InnoDB;

-- Room registry (supplements Lua room files, used for DB-backed room data)
CREATE TABLE IF NOT EXISTS rooms (
    id              INT UNSIGNED PRIMARY KEY,
    zone_id         SMALLINT UNSIGNED NOT NULL,
    title           VARCHAR(128) NOT NULL,
    is_safe         BOOLEAN DEFAULT FALSE,
    is_supernode    BOOLEAN DEFAULT FALSE,
    is_indoor       BOOLEAN DEFAULT FALSE,
    terrain_type    VARCHAR(32) DEFAULT 'urban',
    FOREIGN KEY (zone_id) REFERENCES zones(id),
    INDEX idx_zone (zone_id)
) ENGINE=InnoDB;

-- Room exits (can supplement or override Lua)
CREATE TABLE IF NOT EXISTS room_exits (
    room_id         INT UNSIGNED NOT NULL,
    direction       VARCHAR(32) NOT NULL,
    target_room_id  INT UNSIGNED NOT NULL,
    is_hidden       BOOLEAN DEFAULT FALSE,
    search_dc       TINYINT UNSIGNED DEFAULT 0,
    PRIMARY KEY (room_id, direction),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (target_room_id) REFERENCES rooms(id)
) ENGINE=InnoDB;

-- Creature spawn points
CREATE TABLE IF NOT EXISTS spawn_points (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    room_id         INT UNSIGNED NOT NULL,
    creature_id     INT UNSIGNED NOT NULL,
    max_count       TINYINT UNSIGNED DEFAULT 1,
    respawn_seconds INT UNSIGNED DEFAULT 300,
    is_enabled      BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    INDEX idx_room (room_id)
) ENGINE=InnoDB;
