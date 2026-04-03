-- Item definitions
-- Ta'Vaalor private server item schema.
-- Includes all columns referenced by seed data and the item generator.
USE gemstone_dev;

CREATE TABLE IF NOT EXISTS items (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Identity
    name                VARCHAR(128) NOT NULL,       -- "a steel longsword"
    short_name          VARCHAR(64)  NOT NULL,       -- "steel longsword"
    base_name           VARCHAR(64)  NOT NULL,       -- "longsword"
    noun                VARCHAR(32)  NOT NULL,        -- "longsword"
    article             VARCHAR(8)   DEFAULT 'a',
    item_type           VARCHAR(32)  DEFAULT 'misc',

    -- Material
    material            VARCHAR(32)  DEFAULT NULL,   -- steel, mithril, oak, leather…
    is_template         BOOLEAN      DEFAULT FALSE,   -- master template row (not a live instance)

    -- Base stats
    weight              DECIMAL(6,2) DEFAULT 1.0,    -- in lbs
    value               INT UNSIGNED DEFAULT 0,      -- base silver value
    level_required      TINYINT UNSIGNED DEFAULT 0,
    is_stackable        BOOLEAN      DEFAULT FALSE,
    worn_location       VARCHAR(32)  DEFAULT NULL,   -- head, torso, legs, feet, hands, shoulders, waist, neck, wrist, finger, back

    -- Weapon stats
    weapon_type         VARCHAR(32)  DEFAULT NULL,   -- legacy alias for weapon_category
    weapon_category     VARCHAR(32)  DEFAULT NULL,   -- edged, blunt, twohanded, polearm, ranged, thrown, brawling
    damage_factor       DECIMAL(5,3) DEFAULT NULL,   -- GS4 damage factor
    damage_type         VARCHAR(64)  DEFAULT NULL,   -- slash,puncture,crush (comma-sep)
    attack_bonus        SMALLINT     DEFAULT 0,      -- AS modifier
    damage_bonus        SMALLINT     DEFAULT 0,      -- damage modifier
    weapon_speed        TINYINT      DEFAULT 5,      -- base roundtime

    -- Armor stats
    armor_group         TINYINT UNSIGNED DEFAULT 0,  -- legacy: same as armor_asg
    armor_asg           TINYINT UNSIGNED DEFAULT 0,  -- ASG 1-20
    cva                 SMALLINT     DEFAULT 0,      -- critical vulnerability of armor
    defense_bonus       SMALLINT     DEFAULT 0,
    action_penalty      TINYINT      DEFAULT 0,      -- maneuver penalty
    spell_hindrance     TINYINT      DEFAULT 0,      -- casting hindrance %

    -- Shield stats
    shield_size         ENUM('small','medium','large','tower') DEFAULT NULL,
    shield_ds           TINYINT      DEFAULT 0,      -- DS bonus when blocking
    shield_evade_penalty TINYINT     DEFAULT 0,      -- dodge penalty while blocking

    -- Container
    container_capacity  TINYINT UNSIGNED DEFAULT 0,  -- item slots

    -- Magic / enchant
    enchant_bonus       SMALLINT     DEFAULT 0,      -- +0 through +50
    spell_id            SMALLINT UNSIGNED DEFAULT NULL,

    -- Gem
    gem_family          VARCHAR(32)  DEFAULT NULL,   -- agate, beryl, emerald…

    -- Herb
    herb_heal_type      VARCHAR(32)  DEFAULT NULL,   -- health, head, neck, chest…
    herb_heal_amount    SMALLINT     DEFAULT 0,

    -- Lockpick
    lockpick_modifier   DECIMAL(5,2) DEFAULT 0.00,   -- higher = easier picks

    -- Skin / creature drop
    creature_source     VARCHAR(64)  DEFAULT NULL,   -- which creature drops this

    -- Description
    description         TEXT,
    examine_text        TEXT,

    INDEX idx_type      (item_type),
    INDEX idx_noun      (noun),
    INDEX idx_name      (name),
    INDEX idx_material  (material),
    INDEX idx_category  (weapon_category),
    INDEX idx_asg       (armor_asg)
) ENGINE=InnoDB;
