-- Migration: add_weather_time.sql
-- Adds weather state tracking table and room climate/terrain columns.
-- Room climate and terrain are the PERMANENT geographic properties of a room.
-- Weather state is the DYNAMIC condition of a zone, stored in server_weather.

-- ── Per-zone dynamic weather state ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS server_weather (
    zone_id         INT          NOT NULL PRIMARY KEY,
    weather_state   VARCHAR(32)  NOT NULL DEFAULT 'clear'
                    COMMENT 'Current state: clear, rain, storm, etc.',
    intensity       VARCHAR(16)  NULL     DEFAULT NULL
                    COMMENT 'light | moderate | heavy — NULL if state has no intensity',
    forced_by       VARCHAR(32)  NULL     DEFAULT NULL
                    COMMENT 'NULL=natural | charm | event | gm',
    forced_until    DATETIME     NULL     DEFAULT NULL
                    COMMENT 'When forced weather expires and reverts to natural',
    last_changed    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Dynamic per-zone weather state';

-- ── Room-level climate and terrain ────────────────────────────────────────────
-- Added to the world.rooms table so every room can override zone-level climate.
-- NULL means "inherit from zone". Populated via room LUA files or migration scripts.

ALTER TABLE rooms
    ADD COLUMN IF NOT EXISTS climate  VARCHAR(32) NULL DEFAULT NULL
        COMMENT 'temperate|arctic|desert|tropical|coastal|swamp|underground — overrides zone climate',
    ADD COLUMN IF NOT EXISTS terrain  VARCHAR(32) NULL DEFAULT NULL
        COMMENT 'deciduous|coniferous|grassland|swamp|desert|tundra|alpine|coastal|urban|etc.',
    ADD COLUMN IF NOT EXISTS indoor   TINYINT(1)  NOT NULL DEFAULT 0
        COMMENT '1 = indoor room (no weather messages or outdoor-only effects)';

-- Note: existing indoor column in room LUA scripts maps here.
-- When rooms are loaded from LUA, these columns get populated.
-- Until then, WeatherManager falls back to zone-level climate.
