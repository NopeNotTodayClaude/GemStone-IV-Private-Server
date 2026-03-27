-- =============================================================
-- safe_full_upgrade.sql
-- Consolidated safe migration for GemStone IV private server.
--
-- Adds ALL columns that may be missing from a live DB built
-- from an older schema.  Uses ADD COLUMN IF NOT EXISTS
-- throughout so it is safe to re-run at any time.
--
-- Replaces running these individually (some of which fail on
-- older live DBs due to missing AFTER anchor columns):
--   upgrade_items_table.sql
--   add_character_age.sql
--   add_inventory_extra_data.sql
--   add_material_customization.sql
--   add_picking_queue.sql
--   add_ranks_this_level.sql
--   add_timmorain_bridge_room.sql
--   add_tutorial_fields.sql
--   fix_lockpicks.sql
--   fix_sheath_containers.sql
--
-- Run with:
--   mysql -u root gemstone_dev < safe_full_upgrade.sql
-- =============================================================

USE gemstone_dev;

-- ===========================================================
-- SECTION 1: items table — base columns that may be missing
-- ===========================================================

-- These exist in the current schema but may be absent from
-- live DBs created before they were added.

ALTER TABLE items
    ADD COLUMN IF NOT EXISTS base_name           VARCHAR(64)  DEFAULT NULL
        COMMENT 'Template base name e.g. longsword, mace',
    ADD COLUMN IF NOT EXISTS material            VARCHAR(32)  DEFAULT NULL
        COMMENT 'steel, mithril, oak, leather, etc.',
    ADD COLUMN IF NOT EXISTS worn_location       VARCHAR(32)  DEFAULT NULL
        COMMENT 'head, torso, legs, feet, hands, shoulders, waist, neck, wrist, finger, back',
    ADD COLUMN IF NOT EXISTS weapon_type         VARCHAR(32)  DEFAULT NULL
        COMMENT 'Legacy alias for weapon_category',
    ADD COLUMN IF NOT EXISTS weapon_category     VARCHAR(32)  DEFAULT NULL
        COMMENT 'edged, blunt, twohanded, polearm, ranged, thrown, brawling',
    ADD COLUMN IF NOT EXISTS damage_factor       DECIMAL(5,3) DEFAULT NULL
        COMMENT 'GS4 damage factor',
    ADD COLUMN IF NOT EXISTS damage_type         VARCHAR(64)  DEFAULT NULL
        COMMENT 'slash, puncture, crush (comma-separated)',
    ADD COLUMN IF NOT EXISTS attack_bonus        SMALLINT     DEFAULT 0
        COMMENT 'AS modifier',
    ADD COLUMN IF NOT EXISTS damage_bonus        SMALLINT     DEFAULT 0
        COMMENT 'Damage modifier',
    ADD COLUMN IF NOT EXISTS weapon_speed        TINYINT      DEFAULT 5
        COMMENT 'Base roundtime',
    ADD COLUMN IF NOT EXISTS armor_group         TINYINT UNSIGNED DEFAULT 0
        COMMENT 'Legacy: same as armor_asg',
    ADD COLUMN IF NOT EXISTS armor_asg           TINYINT UNSIGNED DEFAULT 0
        COMMENT 'ASG 1-20',
    ADD COLUMN IF NOT EXISTS cva                 SMALLINT     DEFAULT 0
        COMMENT 'Critical vulnerability of armor',
    ADD COLUMN IF NOT EXISTS defense_bonus       SMALLINT     DEFAULT 0,
    ADD COLUMN IF NOT EXISTS action_penalty      TINYINT      DEFAULT 0
        COMMENT 'Maneuver penalty',
    ADD COLUMN IF NOT EXISTS spell_hindrance     TINYINT      DEFAULT 0
        COMMENT 'Casting hindrance %',
    ADD COLUMN IF NOT EXISTS shield_size         ENUM('small','medium','large','tower') DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS shield_ds           TINYINT      DEFAULT 0
        COMMENT 'DS bonus when blocking',
    ADD COLUMN IF NOT EXISTS shield_evade_penalty TINYINT     DEFAULT 0
        COMMENT 'Dodge penalty while blocking',
    ADD COLUMN IF NOT EXISTS container_capacity  TINYINT UNSIGNED DEFAULT 0
        COMMENT 'Item slots',
    ADD COLUMN IF NOT EXISTS enchant_bonus       SMALLINT     DEFAULT 0
        COMMENT '+0 through +50',
    ADD COLUMN IF NOT EXISTS spell_id            SMALLINT UNSIGNED DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS gem_family          VARCHAR(32)  DEFAULT NULL
        COMMENT 'agate, beryl, emerald, etc.',
    ADD COLUMN IF NOT EXISTS herb_heal_type      VARCHAR(32)  DEFAULT NULL
        COMMENT 'health, head, neck, chest, etc.',
    ADD COLUMN IF NOT EXISTS herb_heal_amount    SMALLINT     DEFAULT 0,
    ADD COLUMN IF NOT EXISTS lockpick_modifier   DECIMAL(5,2) DEFAULT 0.00
        COMMENT 'Higher = easier picks',
    ADD COLUMN IF NOT EXISTS creature_source     VARCHAR(64)  DEFAULT NULL
        COMMENT 'Which creature drops this',
    ADD COLUMN IF NOT EXISTS level_required      TINYINT UNSIGNED DEFAULT 0,
    ADD COLUMN IF NOT EXISTS is_stackable        BOOLEAN      DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS is_template         BOOLEAN      DEFAULT FALSE
        COMMENT 'Master template row, not a live instance',
    ADD COLUMN IF NOT EXISTS description         TEXT,
    ADD COLUMN IF NOT EXISTS examine_text        TEXT;

-- ===========================================================
-- SECTION 2: items table — upgrade_items_table.sql columns
-- ===========================================================

ALTER TABLE items
    ADD COLUMN IF NOT EXISTS material_bonus      SMALLINT     DEFAULT 0
        COMMENT 'Enchant bonus from material (+0 to +30)',
    ADD COLUMN IF NOT EXISTS crit_divisor        SMALLINT     DEFAULT 1
        COMMENT 'Critical hit divisor',
    ADD COLUMN IF NOT EXISTS herb_heal_severity  ENUM('minor','major','scar_minor','scar_major','missing') DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS is_customized       BOOLEAN      DEFAULT FALSE
        COMMENT 'Player-customized item',
    ADD COLUMN IF NOT EXISTS custom_prefix       VARCHAR(64)  DEFAULT NULL
        COMMENT 'e.g. gleaming, blood-stained',
    ADD COLUMN IF NOT EXISTS custom_suffix       VARCHAR(64)  DEFAULT NULL
        COMMENT 'e.g. of the Dawn',
    ADD COLUMN IF NOT EXISTS flare_type          VARCHAR(32)  DEFAULT NULL
        COMMENT 'fire, ice, lightning, holy, etc.',
    ADD COLUMN IF NOT EXISTS lore_text           TEXT         DEFAULT NULL
        COMMENT 'Special lore/history',
    ADD COLUMN IF NOT EXISTS sheath_type         VARCHAR(32)  DEFAULT NULL
        COMMENT 'dagger_sheath | small_scabbard | scabbard | large_scabbard | axe_sheath';

-- Indexes (IF NOT EXISTS on indexes requires a workaround in MySQL)
-- Safe: DROP and recreate only if missing by catching duplicate errors
-- Using CREATE INDEX without IF NOT EXISTS fails silently in many clients,
-- so we use the procedure approach below.

DROP PROCEDURE IF EXISTS gsiv_add_index;
DELIMITER //
CREATE PROCEDURE gsiv_add_index(
    IN p_table VARCHAR(64),
    IN p_index VARCHAR(64),
    IN p_cols  VARCHAR(128)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name   = p_table
          AND index_name   = p_index
        LIMIT 1
    ) THEN
        SET @sql = CONCAT('CREATE INDEX ', p_index, ' ON ', p_table, ' (', p_cols, ')');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //
DELIMITER ;

CALL gsiv_add_index('items', 'idx_base_name',      'base_name');
CALL gsiv_add_index('items', 'idx_material',        'material');
CALL gsiv_add_index('items', 'idx_weapon_category', 'weapon_category');
CALL gsiv_add_index('items', 'idx_template',        'is_template');
CALL gsiv_add_index('items', 'idx_type',            'item_type');
CALL gsiv_add_index('items', 'idx_noun',            'noun');
CALL gsiv_add_index('items', 'idx_name',            'name');
CALL gsiv_add_index('items', 'idx_asg',             'armor_asg');

DROP PROCEDURE IF EXISTS gsiv_add_index;

-- ===========================================================
-- SECTION 3: item_instances table
-- ===========================================================

CREATE TABLE IF NOT EXISTS item_instances (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    base_item_id    INT UNSIGNED NOT NULL COMMENT 'FK to items.id (the template)',
    owner_type      ENUM('character','npc','shop','ground') DEFAULT 'ground',
    owner_id        INT UNSIGNED DEFAULT NULL,
    custom_name     VARCHAR(128) DEFAULT NULL,
    custom_short    VARCHAR(64)  DEFAULT NULL,
    custom_prefix   VARCHAR(64)  DEFAULT NULL,
    custom_suffix   VARCHAR(64)  DEFAULT NULL,
    material        VARCHAR(32)  DEFAULT NULL,
    enchant_bonus   SMALLINT     DEFAULT NULL,
    flare_type      VARCHAR(32)  DEFAULT NULL,
    condition_pct   TINYINT UNSIGNED DEFAULT 100 COMMENT '0-100 durability',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_owner (owner_type, owner_id),
    FOREIGN KEY (base_item_id) REFERENCES items(id)
) ENGINE=InnoDB;

-- ===========================================================
-- SECTION 4: character_inventory — extra_data column
-- ===========================================================

ALTER TABLE character_inventory
    ADD COLUMN IF NOT EXISTS extra_data JSON NULL DEFAULT NULL
        COMMENT 'Per-instance item state: lockpick condition, wand charges, etc.';

-- ===========================================================
-- SECTION 5: characters table additions
-- ===========================================================

ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS age              SMALLINT UNSIGNED DEFAULT 0,
    ADD COLUMN IF NOT EXISTS tutorial_stage   INT     NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS tutorial_complete TINYINT(1) NOT NULL DEFAULT 0;

-- Set sensible default ages for existing characters
UPDATE characters SET age = CASE
    WHEN race_id IN (2, 3, 10) THEN 50
    WHEN race_id = 5            THEN 50
    WHEN race_id IN (6, 8, 9)   THEN 30
    ELSE 20
END
WHERE age = 0;

DROP PROCEDURE IF EXISTS gsiv_add_index2;
DELIMITER //
CREATE PROCEDURE gsiv_add_index2(
    IN p_table VARCHAR(64),
    IN p_index VARCHAR(64),
    IN p_cols  VARCHAR(128)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name   = p_table
          AND index_name   = p_index
        LIMIT 1
    ) THEN
        SET @sql = CONCAT('CREATE INDEX ', p_index, ' ON ', p_table, ' (', p_cols, ')');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //
DELIMITER ;

CALL gsiv_add_index2('characters', 'idx_characters_tutorial', 'tutorial_complete, tutorial_stage');
DROP PROCEDURE IF EXISTS gsiv_add_index2;

-- ===========================================================
-- SECTION 6: character_skills — ranks_this_level
-- ===========================================================

ALTER TABLE character_skills
    ADD COLUMN IF NOT EXISTS ranks_this_level TINYINT UNSIGNED DEFAULT 0;

-- ===========================================================
-- SECTION 7: picking_queue table
-- ===========================================================

CREATE TABLE IF NOT EXISTS picking_queue (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    owner_id            INT UNSIGNED NOT NULL,
    owner_name          VARCHAR(64)  NOT NULL,
    item_id             INT UNSIGNED NOT NULL,
    item_name           VARCHAR(128) NOT NULL,
    item_short_name     VARCHAR(128) NOT NULL,
    item_data           JSON         NOT NULL,
    original_inv_id     INT UNSIGNED DEFAULT NULL,
    offered_fee         INT UNSIGNED NOT NULL DEFAULT 0,
    status              ENUM('pending','claimed','completed','cancelled') NOT NULL DEFAULT 'pending',
    claimer_id          INT UNSIGNED DEFAULT NULL,
    claimer_name        VARCHAR(64)  DEFAULT NULL,
    claimer_inv_id      INT UNSIGNED DEFAULT NULL,
    submitted_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claimed_at          DATETIME     DEFAULT NULL,
    completed_at        DATETIME     DEFAULT NULL,
    expires_at          DATETIME     NOT NULL DEFAULT (DATE_ADD(NOW(), INTERVAL 24 HOUR)),
    INDEX idx_status    (status),
    INDEX idx_owner     (owner_id),
    INDEX idx_claimer   (claimer_id),
    INDEX idx_expires   (expires_at)
) ENGINE=InnoDB;

-- ===========================================================
-- SECTION 8: zones / rooms — Timmorain Bridge room
-- ===========================================================

INSERT INTO zones (id, slug, name, region, level_min, level_max, climate, is_enabled)
VALUES (4, 'timmorain_road', 'Timmorain Road', 'Elanith', 1, 5, 'temperate', TRUE)
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO rooms (id, zone_id, title, is_safe, is_supernode, is_indoor, terrain_type)
VALUES (5829, 4, 'Timmorain Road, Limestone Bridge', FALSE, FALSE, FALSE, 'outdoor')
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- ===========================================================
-- SECTION 9: fix_sheath_containers — sheath/scabbard items
-- ===========================================================

UPDATE items
SET    item_type          = 'container',
       container_capacity = 1,
       sheath_type        = 'dagger_sheath',
       worn_location      = 'hip'
WHERE  noun IN ('dagger sheath','sheath')
  AND  name LIKE '%dagger%';

UPDATE items
SET    item_type          = 'container',
       container_capacity = 1,
       sheath_type        = 'dagger_sheath',
       worn_location      = 'hip'
WHERE  noun IN ('sheath','scabbard')
  AND  (name LIKE '%knife%' OR name LIKE '%dirk%' OR name LIKE '%stiletto%');

UPDATE items
SET    item_type          = 'container',
       container_capacity = 1,
       sheath_type        = 'small_scabbard',
       worn_location      = 'hip'
WHERE  noun = 'scabbard'
  AND  (name LIKE '%short%' OR name LIKE '%back%' OR name LIKE '%small%');

UPDATE items
SET    item_type          = 'container',
       container_capacity = 1,
       sheath_type        = 'large_scabbard',
       worn_location      = 'back'
WHERE  noun = 'scabbard'
  AND  (name LIKE '%great%' OR name LIKE '%large%' OR name LIKE '%claidh%' OR name LIKE '%two-hand%');

UPDATE items
SET    item_type          = 'container',
       container_capacity = 1,
       sheath_type        = 'scabbard',
       worn_location      = 'hip'
WHERE  noun = 'scabbard'
  AND  sheath_type IS NULL;

UPDATE items
SET    item_type          = 'container',
       container_capacity = 1,
       sheath_type        = 'axe_sheath',
       worn_location      = 'hip'
WHERE  noun IN ('sheath','axe sheath')
  AND  (name LIKE '%axe%' OR name LIKE '%hatchet%' OR name LIKE '%tomahawk%');

UPDATE items
SET    item_type          = 'container',
       container_capacity = 1,
       worn_location      = COALESCE(worn_location, 'hip')
WHERE  item_type != 'container'
  AND  (noun LIKE '%sheath%' OR noun LIKE '%scabbard%'
        OR name LIKE '%sheath%' OR name LIKE '%scabbard%');

-- ===========================================================
-- SECTION 10: fix_lockpicks — seed lockpick items
-- ===========================================================

INSERT IGNORE INTO items
    (name, short_name, noun, base_name, article, item_type, material,
     weight, value, description, is_template)
VALUES
('a steel lockpick',   'steel lockpick',   'lockpick', 'steel lockpick',
 'a',  'misc', 'steel',   1, 350,
 'A thin steel lockpick, standard quality.  Reliable but unremarkable.',  1),

('a bronze lockpick',  'bronze lockpick',  'lockpick', 'bronze lockpick',
 'a',  'misc', 'bronze',  1, 200,
 'A bronze lockpick.  Softer than steel and easier to bend, making it suitable for simpler locks.', 1),

('an ivory lockpick',  'ivory lockpick',   'lockpick', 'ivory lockpick',
 'an', 'misc', 'ivory',   1, 750,
 'A slender lockpick carved from ivory.  Its natural flexibility gives it a feel somewhere between steel and gold.', 1),

('a silver lockpick',  'silver lockpick',  'lockpick', 'silver lockpick',
 'a',  'misc', 'silver',  1, 2500,
 'A bright silver lockpick, well-balanced but requiring a practiced touch to use effectively.', 1),

('a gold lockpick',    'gold lockpick',    'lockpick', 'gold lockpick',
 'a',  'misc', 'gold',    1, 2000,
 'A gleaming gold lockpick.  Softer than steel but surprisingly precise in skilled hands.', 1),

('a golvern lockpick', 'golvern lockpick', 'lockpick', 'golvern lockpick',
 'a',  'misc', 'golvern', 1, 95000,
 'An incredibly hard golvern lockpick of masterwork quality.  Only the most seasoned rogues can wield it effectively.', 1),

('a vaalin lockpick',  'vaalin lockpick',  'lockpick', 'vaalin lockpick',
 'a',  'misc', 'vaalin',  1, 125000,
 'A flawlessly crafted vaalin lockpick, the finest known to locksmithing.  Its modifier is unsurpassed.', 1);

-- ===========================================================
-- DONE
-- ===========================================================

SELECT 'safe_full_upgrade.sql complete.' AS status;
SELECT
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_schema = DATABASE() AND table_name = 'items') AS items_columns,
    (SELECT COUNT(*) FROM items)                                AS items_rows,
    (SELECT COUNT(*) FROM characters)                          AS character_count;
