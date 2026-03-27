-- Migration: add material and color customization support
-- Run once against gemstone_dev database
USE gemstone_dev;

-- Add material and color columns to the base items table
ALTER TABLE items
    ADD COLUMN IF NOT EXISTS material    VARCHAR(32) DEFAULT NULL AFTER enchant_bonus,
    ADD COLUMN IF NOT EXISTS color       VARCHAR(32) DEFAULT NULL AFTER material;

-- Add per-instance material/color overrides to character_inventory
-- (so two players can own the same item_id but with different materials)
ALTER TABLE character_inventory
    ADD COLUMN IF NOT EXISTS material    VARCHAR(32) DEFAULT NULL AFTER quantity,
    ADD COLUMN IF NOT EXISTS color       VARCHAR(32) DEFAULT NULL AFTER material,
    ADD COLUMN IF NOT EXISTS custom_name VARCHAR(128) DEFAULT NULL AFTER color,
    ADD COLUMN IF NOT EXISTS enchant_bonus_override SMALLINT DEFAULT NULL AFTER custom_name,
    ADD COLUMN IF NOT EXISTS attack_bonus_override  SMALLINT DEFAULT NULL AFTER enchant_bonus_override,
    ADD COLUMN IF NOT EXISTS defense_bonus_override SMALLINT DEFAULT NULL AFTER attack_bonus_override;

-- Track customization orders in transaction_log (already has bank_deposit/withdraw)
-- Update the ENUM to add shop_order and item_customize
ALTER TABLE transaction_log
    MODIFY COLUMN transaction_type ENUM(
        'buy', 'sell', 'trade', 'bounty', 'loot',
        'bank_deposit', 'bank_withdraw',
        'shop_order', 'item_customize'
    ) NOT NULL;

-- Verify
SELECT 'Migration complete.' AS status;
SELECT column_name, column_type, column_default
FROM information_schema.columns
WHERE table_schema = 'gemstone_dev'
  AND table_name IN ('items', 'character_inventory')
  AND column_name IN ('material', 'color', 'custom_name', 'enchant_bonus_override')
ORDER BY table_name, ordinal_position;
