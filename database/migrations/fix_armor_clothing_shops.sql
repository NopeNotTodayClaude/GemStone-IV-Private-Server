-- =============================================================================
-- MIGRATION: fix_armor_clothing_shops.sql
-- Description:
--   1. Fix incorrect armor_asg on chain hauberk (12->14) and half plate (15->17)
--   2. Insert 5 missing items: brocade normal clothing, brigandine armor,
--      double chain mail, augmented breastplate, augmented plate
--   3. Remove normal clothing (item 70) from Ta'Vaalor Armory (shop 2)
--   4. Remove steel main gauche (item 2) from Ta'Vaalor Women's Clothier (shop 16)
--   5. Add brocade normal clothing to Men's Clothier (shop 10)
--   6. Add wool + brocade normal clothing to Women's Clothier (shop 16)
--   7. Add brigandine, double chain mail, augmented breastplate, augmented plate
--      to Ta'Vaalor Armory (shop 2)
-- New item IDs: 1122-1126
-- New shop_inventory IDs: 517-527
-- =============================================================================

START TRANSACTION;

-- -----------------------------------------------------------------------------
-- STEP 1: Fix incorrect armor_asg values
-- chain hauberk was seeded with ASG 12 (double chain mail's slot) - correct to 14
-- half plate was seeded with ASG 15 (metal breastplate's slot) - correct to 17
-- -----------------------------------------------------------------------------

UPDATE `items` SET `armor_asg` = 14 WHERE `id` = 1063 AND `name` = 'a chain hauberk';
UPDATE `items` SET `armor_asg` = 17 WHERE `id` = 1065 AND `name` = 'some half plate';

-- -----------------------------------------------------------------------------
-- STEP 2: Insert missing items
-- All are base/unmaterieled templates (is_template=1, is_customized=0)
-- material='none' means customizable via the material system
-- Stat scaling follows the existing 1062-1065 series pattern
-- -----------------------------------------------------------------------------

INSERT INTO `items` (
    `id`, `name`, `short_name`, `noun`, `article`, `item_type`,
    `is_template`, `is_stackable`, `weight`, `value`,
    `weapon_type`, `damage_factor`, `weapon_speed`, `damage_type`,
    `attack_bonus`, `damage_bonus`, `enchant_bonus`,
    `armor_group`, `armor_asg`, `defense_bonus`, `action_penalty`, `spell_hindrance`,
    `shield_type`, `shield_ds`, `shield_evade_penalty`, `shield_size_mod`,
    `container_capacity`, `sheath_type`, `container_type`, `lock_difficulty`, `trap_type`,
    `worn_location`,
    `heal_type`, `heal_rank`, `heal_amount`, `herb_roundtime`,
    `gem_family`, `gem_region`, `lockpick_material`,
    `material`, `color`, `description`, `examine_text`, `lore_text`,
    `created_at`, `base_name`, `weapon_category`,
    `cva`, `shield_size`, `spell_id`,
    `herb_heal_type`, `herb_heal_amount`, `lockpick_modifier`,
    `creature_source`, `level_required`, `material_bonus`, `crit_divisor`,
    `herb_heal_severity`, `is_customized`, `custom_prefix`, `custom_suffix`,
    `flare_type`, `display_order`
) VALUES

-- 1122: Brocade Normal Clothing (ASG 1)
-- More opulent than silk/velvet, fits Men's and Women's clothiers
(1122, 'a brocade normal clothing', 'brocade normal clothing', 'clothing', 'a', 'armor',
    1, 0, 1.2, 75,
    NULL, NULL, NULL, NULL,
    0, 0, 0,
    NULL, 1, 0, 0, 0,
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, 0, NULL,
    'torso',
    NULL, NULL, 0, NULL,
    NULL, NULL, NULL,
    'brocade', NULL, 'Richly woven brocade clothing with no protective value.', NULL, NULL,
    NOW(), 'normal clothing', NULL,
    0, NULL, NULL,
    NULL, 0, 0.00,
    NULL, 0, 0, 1,
    NULL, 0, NULL, NULL,
    NULL, 99),

-- 1123: Brigandine Armor (ASG 10)
-- Sits between studded leather (ASG 9) and chain mail (ASG 11)
(1123, 'some brigandine armor', 'brigandine armor', 'armor', 'some', 'armor',
    1, 0, 10, 500,
    NULL, NULL, NULL, NULL,
    0, 0, 0,
    NULL, 10, 10, 7, 3,
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, 0, NULL,
    'torso',
    NULL, NULL, 0, NULL,
    NULL, NULL, NULL,
    'none', NULL, 'Small metal plates riveted to a leather backing, bridging leather and chain.', NULL, NULL,
    NOW(), 'brigandine armor', NULL,
    0, NULL, NULL,
    NULL, 0, 0.00,
    NULL, 0, 0, 1,
    NULL, 0, NULL, NULL,
    NULL, 99),

-- 1124: Double Chain Mail (ASG 12)
-- Sits between chain mail (ASG 11) and augmented chain (ASG 13)
(1124, 'some double chain mail', 'double chain mail', 'mail', 'some', 'armor',
    1, 0, 14, 1000,
    NULL, NULL, NULL, NULL,
    0, 0, 0,
    NULL, 12, 12, 13, 10,
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, 0, NULL,
    'torso',
    NULL, NULL, 0, NULL,
    NULL, NULL, NULL,
    'none', NULL, 'Two interlocked layers of chain rings providing superior coverage.', NULL, NULL,
    NOW(), 'double chain mail', NULL,
    0, NULL, NULL,
    NULL, 0, 0.00,
    NULL, 0, 0, 1,
    NULL, 0, NULL, NULL,
    NULL, 99),

-- 1125: Augmented Breastplate (ASG 16)
-- Sits between half plate (ASG 17 after fix) wait - 16 is BELOW 17
-- Ladder: aug chain(13) > chain hauberk(14) > metal breastplate(15) > aug breastplate(16) > half plate(17)
(1125, 'an augmented breastplate', 'augmented breastplate', 'breastplate', 'an', 'armor',
    1, 0, 22, 3000,
    NULL, NULL, NULL, NULL,
    0, 0, 0,
    NULL, 16, 16, 22, 32,
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, 0, NULL,
    'torso',
    NULL, NULL, 0, NULL,
    NULL, NULL, NULL,
    'none', NULL, 'A reinforced plate breastplate with chain-backed limb guards.', NULL, NULL,
    NOW(), 'augmented breastplate', NULL,
    0, NULL, NULL,
    NULL, 0, 0.00,
    NULL, 0, 0, 1,
    NULL, 0, NULL, NULL,
    NULL, 99),

-- 1126: Augmented Plate (ASG 19)
-- Sits between full plate (ASG 18) and razern plate (ASG 20, excluded)
(1126, 'some augmented plate', 'augmented plate', 'plate', 'some', 'armor',
    1, 0, 35, 6000,
    NULL, NULL, NULL, NULL,
    0, 0, 0,
    NULL, 19, 20, 30, 60,
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, 0, NULL,
    'torso',
    NULL, NULL, 0, NULL,
    NULL, NULL, NULL,
    'none', NULL, 'Full articulated plate reinforced at every joint with layered metal backing.', NULL, NULL,
    NOW(), 'augmented plate', NULL,
    0, NULL, NULL,
    NULL, 0, 0.00,
    NULL, 0, 0, 1,
    NULL, 0, NULL, NULL,
    NULL, 99);

-- -----------------------------------------------------------------------------
-- STEP 3: Remove normal clothing from Ta'Vaalor Armory (shop 2)
-- -----------------------------------------------------------------------------

DELETE FROM `shop_inventory` WHERE `shop_id` = 2 AND `item_id` = 70;

-- -----------------------------------------------------------------------------
-- STEP 4: Remove steel main gauche from Women's Clothier (shop 16)
-- -----------------------------------------------------------------------------

DELETE FROM `shop_inventory` WHERE `shop_id` = 16 AND `item_id` = 2;

-- -----------------------------------------------------------------------------
-- STEP 5: Add brocade normal clothing to Men's Clothier (shop 10)
-- -----------------------------------------------------------------------------

INSERT INTO `shop_inventory` (`id`, `shop_id`, `item_id`, `stock`, `restock_amount`, `restock_interval`, `last_restock`)
VALUES (517, 10, 1122, -1, 0, 3600, NULL);

-- -----------------------------------------------------------------------------
-- STEP 6: Add wool + brocade normal clothing to Women's Clothier (shop 16)
-- Wool (882) already exists in live items table, just missing from shop 16
-- -----------------------------------------------------------------------------

INSERT INTO `shop_inventory` (`id`, `shop_id`, `item_id`, `stock`, `restock_amount`, `restock_interval`, `last_restock`)
VALUES
    (518, 16, 882,  -1, 0, 3600, NULL),  -- wool normal clothing (existing item)
    (519, 16, 1122, -1, 0, 3600, NULL);  -- brocade normal clothing (new)

-- -----------------------------------------------------------------------------
-- STEP 7: Add 4 missing armor types to Ta'Vaalor Armory (shop 2)
-- Matches existing armory pattern: stock=-1, restock_amount=0, interval=3600
-- -----------------------------------------------------------------------------

INSERT INTO `shop_inventory` (`id`, `shop_id`, `item_id`, `stock`, `restock_amount`, `restock_interval`, `last_restock`)
VALUES
    (520, 2, 1123, -1, 0, 3600, NULL),  -- brigandine armor       (ASG 10)
    (521, 2, 1124, -1, 0, 3600, NULL),  -- double chain mail      (ASG 12)
    (522, 2, 1125, -1, 0, 3600, NULL),  -- augmented breastplate  (ASG 16)
    (523, 2, 1126, -1, 0, 3600, NULL);  -- augmented plate        (ASG 19)

COMMIT;
