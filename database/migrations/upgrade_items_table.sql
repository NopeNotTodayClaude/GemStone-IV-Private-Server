-- Upgrade items table for full GemStone IV item system
-- Adds material system, damage factors, AvD, flares, customization flags
USE gemstone_dev;

-- Add new columns to items table
ALTER TABLE items
    ADD COLUMN base_name VARCHAR(64) DEFAULT NULL COMMENT 'Template name like longsword, mace'
        AFTER noun,
    ADD COLUMN material VARCHAR(32) DEFAULT 'steel' COMMENT 'Material: steel, vultite, mithril, etc.'
        AFTER base_name,
    ADD COLUMN material_bonus SMALLINT DEFAULT 0 COMMENT 'Enchant bonus from material (+0 to +30)'
        AFTER material,
    ADD COLUMN damage_factor DECIMAL(5,3) DEFAULT 0.000 COMMENT 'Weapon DF vs cloth'
        AFTER weapon_speed,
    ADD COLUMN damage_type VARCHAR(32) DEFAULT NULL COMMENT 'slash, crush, puncture, or combos'
        AFTER damage_factor,
    ADD COLUMN weapon_category ENUM('edged','blunt','twohanded','polearm','ranged','thrown','brawling') DEFAULT NULL
        AFTER damage_type,
    ADD COLUMN crit_divisor SMALLINT DEFAULT 1 COMMENT 'Critical hit divisor'
        AFTER weapon_category,
    ADD COLUMN armor_asg TINYINT UNSIGNED DEFAULT 1 COMMENT 'Armor Strength Group 1-20'
        AFTER armor_group,
    ADD COLUMN cva SMALLINT DEFAULT 25 COMMENT 'Cast vs Armor modifier'
        AFTER armor_asg,
    ADD COLUMN spell_hindrance TINYINT DEFAULT 0 COMMENT 'Max spell hindrance %'
        AFTER cva,
    ADD COLUMN shield_ds SMALLINT DEFAULT 0 COMMENT 'Base shield DS bonus'
        AFTER shield_size,
    ADD COLUMN shield_evade_penalty SMALLINT DEFAULT 0 COMMENT 'Evade penalty from shield'
        AFTER shield_ds,
    ADD COLUMN herb_heal_type VARCHAR(32) DEFAULT NULL COMMENT 'HP, nerve, head, torso, limb'
        AFTER container_capacity,
    ADD COLUMN herb_heal_amount SMALLINT DEFAULT 0
        AFTER herb_heal_type,
    ADD COLUMN herb_heal_severity ENUM('minor','major','scar_minor','scar_major','missing') DEFAULT NULL
        AFTER herb_heal_amount,
    ADD COLUMN gem_family VARCHAR(32) DEFAULT NULL COMMENT 'Gem family: ruby, diamond, etc.'
        AFTER herb_heal_severity,
    ADD COLUMN lockpick_modifier DECIMAL(4,2) DEFAULT 1.00 COMMENT 'Lockpick quality modifier'
        AFTER gem_family,
    ADD COLUMN is_customized BOOLEAN DEFAULT FALSE COMMENT 'Player-customized item'
        AFTER is_stackable,
    ADD COLUMN custom_prefix VARCHAR(64) DEFAULT NULL COMMENT 'e.g. gleaming, blood-stained'
        AFTER is_customized,
    ADD COLUMN custom_suffix VARCHAR(64) DEFAULT NULL COMMENT 'e.g. of the Dawn'
        AFTER custom_prefix,
    ADD COLUMN flare_type VARCHAR(32) DEFAULT NULL COMMENT 'fire, ice, lightning, holy, etc.'
        AFTER enchant_bonus,
    ADD COLUMN lore_text TEXT DEFAULT NULL COMMENT 'Special lore/history'
        AFTER examine_text,
    ADD COLUMN is_template BOOLEAN DEFAULT FALSE COMMENT 'TRUE = base template, not an instance'
        AFTER lore_text;

-- Add indexes for common lookups
ALTER TABLE items
    ADD INDEX idx_base_name (base_name),
    ADD INDEX idx_material (material),
    ADD INDEX idx_weapon_category (weapon_category),
    ADD INDEX idx_template (is_template);

-- Create item_instances for player-owned customized copies
CREATE TABLE IF NOT EXISTS item_instances (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    base_item_id    INT UNSIGNED NOT NULL COMMENT 'FK to items.id (the template)',
    owner_type      ENUM('character','npc','shop','ground') DEFAULT 'ground',
    owner_id        INT UNSIGNED DEFAULT NULL,

    -- Overrides (NULL = use base item value)
    custom_name     VARCHAR(128) DEFAULT NULL,
    custom_short    VARCHAR(64) DEFAULT NULL,
    custom_prefix   VARCHAR(64) DEFAULT NULL,
    custom_suffix   VARCHAR(64) DEFAULT NULL,
    material        VARCHAR(32) DEFAULT NULL,
    enchant_bonus   SMALLINT DEFAULT NULL,
    flare_type      VARCHAR(32) DEFAULT NULL,
    condition_pct   TINYINT UNSIGNED DEFAULT 100 COMMENT '0-100 durability',

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_owner (owner_type, owner_id),
    FOREIGN KEY (base_item_id) REFERENCES items(id)
) ENGINE=InnoDB;
