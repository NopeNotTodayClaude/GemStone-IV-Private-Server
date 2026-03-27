-- =============================================================
-- add_disarming_tools_shind.sql
-- Adds trap-disarming consumable tools to the items table
-- and stocks them at Shind's Locksmith (shop_id = 7).
--
-- Run with:
--   mysql -u root gemstone_dev < database/migrations/add_disarming_tools_shind.sql
--
-- In GS4, disarming traps uses the Disarming Traps skill directly —
-- no tool is required.  These consumables provide a skill bonus,
-- making them useful for lower-ranked rogues tackling harder traps.
-- =============================================================

USE gemstone_dev;

-- ── Trap Disarming Tools ──────────────────────────────────────────────────────
-- item_type = 'disarming_tool' (new subtype; cmd_disarm checks for it as optional bonus)
-- Uses 'consumable' item_type so it works with existing USE flow.
-- The disarm command checks for a disarming tool in hand and applies its bonus.

INSERT IGNORE INTO items (
    name, short_name, base_name, noun, article, item_type,
    material, weight, value, is_template,
    description, examine_text, lore_text
) VALUES
-- Basic: +10 bonus, common, cheap
(
    'a disarming tool',
    'disarming tool', 'disarming tool', 'tool', 'a',
    'disarming_tool', NULL,
    0.2, 200, 1,
    'A simple set of fine-tipped probes and tension wrenches for disarming mechanical traps.',
    'The small kit contains three probe tips of different gauges and a pair of micro tension wrenches, all nestled in a thin leather roll.',
    'Basic trap-disarming kit.  Provides a modest bonus to Disarming Traps skill when held.'
),
-- Improved: +20 bonus
(
    'a quality disarming kit',
    'quality disarming kit', 'disarming kit', 'kit', 'a',
    'disarming_tool', NULL,
    0.3, 650, 1,
    'A well-made set of disarming tools with tempered probes and precision tension wrenches.',
    'The kit is clearly the work of a skilled craftsman.  The probes are tempered steel, the wrenches finely calibrated — the sort of tools a serious rogue carries.',
    'Professional trap-disarming kit.  Provides a solid bonus to Disarming Traps skill when held.'
),
-- Expert: +35 bonus, limited stock, high cost
(
    'a masterwork disarming kit',
    'masterwork disarming kit', 'disarming kit', 'kit', 'a',
    'disarming_tool', NULL,
    0.4, 2000, 1,
    'A masterwork set of disarming instruments, their balance and temper immediately apparent to any trained hand.',
    'Each probe in this kit is individually ground and balanced.  The tension wrenches have micro-adjustable flex.  This is not a tool you buy — it is one you earn, or pay dearly for.',
    'Masterwork trap-disarming kit.  Provides an excellent bonus to Disarming Traps skill when held.'
);

-- ── Stock at Shind's Locksmith (shop_id = 7) ──────────────────────────────────
-- Unlimited basic and quality; masterwork limited (5, restocks slowly)
INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 7, id, -1, -1, 3600 FROM items
    WHERE name = 'a disarming tool' AND is_template = 1 LIMIT 1;

INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 7, id, -1, -1, 3600 FROM items
    WHERE name = 'a quality disarming kit' AND is_template = 1 LIMIT 1;

INSERT IGNORE INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
    SELECT 7, id, 5, 2, 86400 FROM items
    WHERE name = 'a masterwork disarming kit' AND is_template = 1 LIMIT 1;

-- ── Verification (comment out for production) ─────────────────────────────────
-- SELECT name, value FROM items WHERE item_type = 'disarming_tool';
-- SELECT i.name, si.stock FROM shop_inventory si JOIN items i ON si.item_id = i.id WHERE si.shop_id = 7;
