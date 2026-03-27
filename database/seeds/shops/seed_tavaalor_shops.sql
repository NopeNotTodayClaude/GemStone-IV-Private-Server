-- =============================================================
-- Ta'Vaalor Shop Seed
-- 18 shops — all NPC shopkeepers in Ta'Vaalor
-- Item IDs resolved by name subquery (no hardcoded IDs)
-- Safe to re-run: shops use ON DUPLICATE KEY, inventory uses INSERT IGNORE
-- =============================================================
USE gemstone_dev;

-- =============================================================
-- SHOPS TABLE
-- =============================================================
INSERT INTO shops (id, name, room_id, shop_type, buy_multiplier, sell_multiplier) VALUES
  ( 1, 'The Ta''Vaalor Weaponry',          10367, 'weapon',  1.10, 0.45),
  ( 2, 'The Ta''Vaalor Armory',            12350, 'armor',   1.10, 0.45),
  ( 3, 'Ghaerdish''s Furs and Pelts',      10329, 'armor',   1.05, 0.45),
  ( 4, 'Ta''Vaalor General Exchange',      12348, 'general', 1.00, 0.40),
  ( 5, 'Saphrie''s Herbs and Tinctures',   10396, 'herb',    1.00, 0.50),
  ( 6, 'Ta''Vaalor Antique Goods',         10379, 'general', 1.00, 0.50),
  ( 7, 'Locksmith',                        10434, 'other',   1.10, 0.30),
  ( 8, 'Elantaran''s Magic Supply',        10364, 'magic',   1.15, 0.40),
  ( 9, 'Areacne''s Gems of Ta''Vaalor',    10327, 'gem',     1.10, 0.60),
  (10, 'Ta''Vaalor Men''s Clothier',       17292, 'other',   1.00, 0.20),
  (11, 'Helgreth''s Tavern',               10424, 'food',    1.00, 0.10),
  (12, 'Clentaran''s Clerical Supply',     10372, 'magic',   1.10, 0.40),
  (13, 'Vonder''s Archery Supply',         10362, 'weapon',  1.10, 0.45),
  (14, 'Annatto Rations Shop',             10368, 'food',    1.00, 0.20),
  (15, 'Ambra''s Musicalities',            10395, 'other',   1.05, 0.25),
  (16, 'Ta''Vaalor Women''s Clothier',     17293, 'other',   1.00, 0.20),
  (17, 'Sweethen''s Bakeshop',             12349, 'food',    1.00, 0.10),
  (18, 'Ta''Vaalor Forging Supply',        10394, 'other',   1.00, 0.40)
ON DUPLICATE KEY UPDATE
  name             = VALUES(name),
  room_id          = VALUES(room_id),
  shop_type        = VALUES(shop_type),
  buy_multiplier   = VALUES(buy_multiplier),
  sell_multiplier  = VALUES(sell_multiplier);


-- =============================================================
-- HELPER: safe single-row insert from item name
-- Pattern: INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
--          SELECT <shop_id>, id, <stock>, <restock>, <interval_sec> FROM items WHERE name='...' AND is_template=1 LIMIT 1;
-- stock=-1 = unlimited;  restock_amount=-1 = unlimited restock
-- =============================================================


-- ─────────────────────────────────────────────────────────────
-- SHOP 1  |  The Ta'Vaalor Weaponry  (Aerhseth the weaponsmith)
-- Edged, blunt, two-handed, polearms — iron through vaalorn
-- ─────────────────────────────────────────────────────────────

-- Edged: daggers
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron dagger'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a bronze dagger'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel dagger'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a mithril dagger'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite dagger'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn dagger'        AND is_template=1 LIMIT 1;
-- main gauche
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel main gauche'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite main gauche'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn main gauche'   AND is_template=1 LIMIT 1;
-- short sword
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron short sword'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel short sword'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite short sword'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn short sword'   AND is_template=1 LIMIT 1;
-- backsword
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron backsword'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel backsword'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite backsword'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn backsword'     AND is_template=1 LIMIT 1;
-- broadsword
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron broadsword'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel broadsword'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a mithril broadsword'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite broadsword'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn broadsword'    AND is_template=1 LIMIT 1;
-- longsword
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron longsword'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel longsword'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a mithril longsword'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite longsword'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn longsword'     AND is_template=1 LIMIT 1;
-- rapier
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron rapier'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel rapier'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite rapier'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn rapier'        AND is_template=1 LIMIT 1;
-- falchion
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron falchion'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel falchion'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite falchion'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn falchion'      AND is_template=1 LIMIT 1;
-- scimitar
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron scimitar'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel scimitar'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite scimitar'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn scimitar'      AND is_template=1 LIMIT 1;
-- blunt: war hammer, mace, cudgel
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron war hammer'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel war hammer'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite war hammer'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn war hammer'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron mace'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel mace'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite mace'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn mace'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron cudgel'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel cudgel'          AND is_template=1 LIMIT 1;
-- two-handed: claidhmore, halberd, spear, greatsword
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron claidhmore'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel claidhmore'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite claidhmore'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn claidhmore'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron greatsword'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel greatsword'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite greatsword'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn greatsword'    AND is_template=1 LIMIT 1;
-- polearm
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron spear'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel spear'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite spear'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn spear'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='an iron halberd'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a steel halberd'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vultite halberd'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 1,id,-1,-1,3600 FROM items WHERE name='a vaalorn halberd'       AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 2  |  The Ta'Vaalor Armory  (Gearchel the armorer)
-- Armor (metal/mixed) + shields
-- ─────────────────────────────────────────────────────────────

-- Robes / Clothing (mage-friendly)
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a linen flowing robes'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a cotton flowing robes'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a silk flowing robes'    AND is_template=1 LIMIT 1;
-- Leather (light)
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='some light leather armor' AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='some full leather armor'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='some reinforced leather'  AND is_template=1 LIMIT 1;
-- Breastplate / chain
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='some leather breastplate'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='an iron chain mail'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a bronze chain mail'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a steel chain mail'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a mithril chain mail'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vultite chain mail'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vaalorn chain mail'        AND is_template=1 LIMIT 1;
-- Chain hauberk
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='an iron chain hauberk'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a steel chain hauberk'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a mithril chain hauberk'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vultite chain hauberk'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vaalorn chain hauberk'    AND is_template=1 LIMIT 1;
-- Half plate / Augmented chain
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='an iron half plate'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a steel half plate'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a mithril half plate'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vultite half plate'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vaalorn half plate'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='an iron augmented chain'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a steel augmented chain'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vultite augmented chain'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vaalorn augmented chain'  AND is_template=1 LIMIT 1;
-- Shields
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='an iron buckler'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a steel buckler'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vultite buckler'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vaalorn buckler'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='an iron target shield'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a steel target shield'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a mithril target shield'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vultite target shield'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vaalorn target shield'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='an iron mantlet'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a steel mantlet'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vultite mantlet'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vaalorn mantlet'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='an iron pavise'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a steel pavise'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vultite pavise'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 2,id,-1,-1,3600 FROM items WHERE name='a vaalorn pavise'           AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 3  |  Ghaerdish's Furs and Pelts  (Sylindra the leatherworker)
-- Leather armors + containers/packs
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='some light leather armor'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='some full leather armor'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='some reinforced leather'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='some leather breastplate'         AND is_template=1 LIMIT 1;
-- Containers / packs
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a belt pouch'                    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a small leather pouch'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a gem pouch'                     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='an herb pouch'                   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a leather backpack'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a canvas haversack'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a traveler''s pack'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a hunting pack'                 AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a dark leather satchel'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a weapon harness'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='a silk coin purse'              AND is_template=1 LIMIT 1;
-- Cloaks
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='an adventurer''s cloak'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 3,id,-1,-1,3600 FROM items WHERE name='an embroidered cloak'          AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 4  |  Ta'Vaalor General Exchange  (Phisk)
-- Adventuring supplies: lights, rope, ammo, tools
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a wooden torch'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='an oil lantern'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a coil of rope'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a grappling hook'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a waterskin'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a fishing pole'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a shovel'                  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a pair of scissors'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a needle and thread'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a set of bone dice'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a bundle of arrows'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a bundle of crossbow bolts' AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a fletched hunting arrow'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,-1,-1,3600 FROM items WHERE name='a steel-headed war bolt'   AND is_template=1 LIMIT 1;
-- Deed of Lorminstra (expensive but available)
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 4,id,5,5,86400   FROM items WHERE name='a deed of Lorminstra'     AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 5  |  Saphrie's Herbs and Tinctures  (Maraene the herbalist)
-- Full herb catalog
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='a sprig of acantha leaf'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some wekaf berries'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some cuctucae berry'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='a stem of ambrominas leaf'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some yabathilium fruit'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some haphip root'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some calamia fruit'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some basal moss'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some tkaro root'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some ephlox moss'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='a sprig of aloeas stem'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some wolifrew lichen'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some sovyn clove'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='a sprig of torban leaf'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some pothinir grass'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some woth flower'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='a sprig of cactacae spine'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some talneo potion'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some brostheras potion'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some wingstem potion'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some bolmara potion'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some rose-marrow potion'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some troll''s blood potion'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 5,id,-1,-1,3600 FROM items WHERE name='some redite ore'             AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 6  |  Ta'Vaalor Antique Goods / Pawn Shop  (Dakris)
-- General buy/sell shop — carries a rotating misc stock
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a prayer bead necklace'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a crystal amulet'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='an ivory comb'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a set of bone dice'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a silver ring'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a gold ring'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a silver bracelet'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a small steel lockbox'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a wooden coffer'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a small wooden box'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 6,id,-1,-1,3600 FROM items WHERE name='a dented iron box'         AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 7  |  Locksmith  (Shind)
-- Lockpicks, crude through master
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,-1,3600 FROM items WHERE name='a crude lockpick'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,-1,3600 FROM items WHERE name='a simple lockpick'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,-1,3600 FROM items WHERE name='a standard lockpick'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,-1,3600 FROM items WHERE name='a professional lockpick'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,10,10,7200  FROM items WHERE name='a master''s lockpick'      AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 8  |  Elantaran's Magic Supply  (Elantaran)
-- Scrolls, runestones, wand
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a small crystal runestone'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a smooth grey runestone'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a glowing white runestone'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,5,5,43200   FROM items WHERE name='a silver wand'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a crinkled minor spirit scroll'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a weathered major spirit scroll'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a leaf-bound ranger scroll'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a blessed cleric scroll'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a glowing empath scroll'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a musical bard scroll'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a radiant paladin scroll'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='an arcane wizard scroll'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a dark sorcerer scroll'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 8,id,-1,-1,3600 FROM items WHERE name='a glowing glowbark wand'        AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 9  |  Areacne's Gems of Ta'Vaalor  (Tmareantha)
-- Full gem catalog + jewelry
-- ─────────────────────────────────────────────────────────────

-- Jewelry
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a silver ring'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a gold ring'                AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a silver bracelet'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a gold bracelet'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a gold necklace'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a crystal amulet'          AND is_template=1 LIMIT 1;
-- Gems: agate/quartz tier
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a blue lace agate'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a clear quartz'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a rose quartz'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a smoky quartz'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a citrine quartz'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a turquoise stone'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a tigerfang crystal'       AND is_template=1 LIMIT 1;
-- Mid-tier gems
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='an amethyst'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a green jade'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a peridot'                 AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a piece of golden amber'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a pale blue moonstone'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a moonstone'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='an aquamarine gem'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a red carbuncle'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a dark red garnet'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,-1,-1,3600 FROM items WHERE name='a fire opal'               AND is_template=1 LIMIT 1;
-- High-value gems (limited stock)
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,3,1,86400  FROM items WHERE name='a blue sapphire'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,2,1,86400  FROM items WHERE name='a star sapphire'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,3,1,86400  FROM items WHERE name='an uncut emerald'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,3,1,86400  FROM items WHERE name='an uncut ruby'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 9,id,2,1,172800 FROM items WHERE name='an uncut diamond'          AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 10  |  Ta'Vaalor Men's Clothier  (Vendara)
-- Clothing for male characters
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 10,id,-1,-1,3600 FROM items WHERE name='a linen normal clothing'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 10,id,-1,-1,3600 FROM items WHERE name='a wool normal clothing'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 10,id,-1,-1,3600 FROM items WHERE name='a cotton normal clothing'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 10,id,-1,-1,3600 FROM items WHERE name='a silk normal clothing'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 10,id,-1,-1,3600 FROM items WHERE name='a velvet normal clothing'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 10,id,-1,-1,3600 FROM items WHERE name='a satin normal clothing'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 10,id,-1,-1,3600 FROM items WHERE name='an adventurer''s cloak'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 10,id,-1,-1,3600 FROM items WHERE name='an embroidered cloak'     AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 11  |  Helgreth's Tavern  (Helgreth the innkeeper)
-- Drinks and hot food
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a tankard of elven ale'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a mug of dwarven stout'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a glass of Vaalor red wine'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a bottle of wine'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a flask of elven spirits'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a flask of elven brandy'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a flask of water'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a bowl of hearty stew'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a roasted haunch'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a meat pie'                   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a piece of bread'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 11,id,-1,-1,1800 FROM items WHERE name='a cheese wedge'               AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 12  |  Clentaran's Clerical Supply  (Clentaran)
-- Cleric/spiritual focused — scrolls, prayer beads, holy items
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,-1,-1,3600 FROM items WHERE name='a prayer bead necklace'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,-1,-1,3600 FROM items WHERE name='a blessed cleric scroll'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,-1,-1,3600 FROM items WHERE name='a glowing empath scroll'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,-1,-1,3600 FROM items WHERE name='a radiant paladin scroll'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,-1,-1,3600 FROM items WHERE name='a crinkled minor spirit scroll' AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,-1,-1,3600 FROM items WHERE name='a weathered major spirit scroll' AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,5,5,86400  FROM items WHERE name='a deed of Lorminstra'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,3,3,86400  FROM items WHERE name='a glowing deed of Lorminstra'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 12,id,-1,-1,3600 FROM items WHERE name='a crystal amulet'              AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 13  |  Vonder's Archery Supply  (Vonder)
-- Bows, crossbows, arrows, bolts
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='an oak short bow'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a yew short bow'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='an oak composite bow'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a yew composite bow'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='an oak long bow'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a yew long bow'                AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='an iron light crossbow'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a steel light crossbow'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='an iron heavy crossbow'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a steel heavy crossbow'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a fletched hunting arrow'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a bundle of arrows'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a bundle of war arrows'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a steel-headed war bolt'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a bundle of crossbow bolts'   AND is_template=1 LIMIT 1;
-- Thrown weapons
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='an iron dart'                 AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a steel dart'                 AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='an iron javelin'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 13,id,-1,-1,3600 FROM items WHERE name='a steel javelin'              AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 14  |  Annatto Rations Shop  (Drevith)
-- Trail rations, basic food, water
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a bundle of travel rations'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a pouch of trail mix'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a loaf of elven waybread'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a strip of dried venison'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a piece of bread'            AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='an apple'                   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a biscuit'                  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a flask of water'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a waterskin'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 14,id,-1,-1,1800 FROM items WHERE name='a cheese wedge'            AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 15  |  Ambra's Musicalities  (Ambra)
-- Musical misc items + entertainment goods
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 15,id,-1,-1,3600 FROM items WHERE name='a set of bone dice'          AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 15,id,-1,-1,3600 FROM items WHERE name='an ivory comb'              AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 15,id,-1,-1,3600 FROM items WHERE name='a musical bard scroll'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 15,id,-1,-1,3600 FROM items WHERE name='a needle and thread'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 15,id,-1,-1,3600 FROM items WHERE name='a prayer bead necklace'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 15,id,-1,-1,3600 FROM items WHERE name='a small crystal runestone'  AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 16  |  Ta'Vaalor Women's Clothier  (Raeliveth)
-- Clothing for female characters (mirrors men's + robes)
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='a linen normal clothing'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='a cotton normal clothing'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='a silk normal clothing'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='a velvet normal clothing'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='a satin normal clothing'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='a linen flowing robes'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='a silk flowing robes'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='a velvet flowing robes'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='an embroidered cloak'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 16,id,-1,-1,3600 FROM items WHERE name='an adventurer''s cloak'   AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 17  |  Sweethen's Bakeshop  (Sweethen the baker)
-- Baked goods, pastries, sweet items
-- ─────────────────────────────────────────────────────────────

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='a biscuit'                  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='a honey roll'               AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='a piece of bread'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='a loaf of elven waybread'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='a meat pie'                 AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='a cheese wedge'             AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='an apple'                   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='a pouch of trail mix'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 17,id,-1,-1,1800 FROM items WHERE name='a flask of water'           AND is_template=1 LIMIT 1;


-- ─────────────────────────────────────────────────────────────
-- SHOP 18  |  Ta'Vaalor Forging Supply  (Tarneth)
-- Smithing ores, forge tools
-- ─────────────────────────────────────────────────────────────

-- Common ores
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a chunk of iron ore'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a chunk of copper ore'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a chunk of silver ore'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a chunk of gold ore'        AND is_template=1 LIMIT 1;
-- Rare ores (limited stock)
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,5,3,14400  FROM items WHERE name='a chunk of mithril ore'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,5,3,14400  FROM items WHERE name='a chunk of invar ore'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,5,3,14400  FROM items WHERE name='a chunk of ora ore'         AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,3,2,28800  FROM items WHERE name='a chunk of vultite ore'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,3,2,28800  FROM items WHERE name='a chunk of kelyn ore'       AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,2,1,43200  FROM items WHERE name='a chunk of laje ore'        AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,2,1,43200  FROM items WHERE name='a chunk of rolaren ore'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,1,1,86400  FROM items WHERE name='a chunk of faenor ore'      AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,1,1,86400  FROM items WHERE name='a chunk of eahnor ore'      AND is_template=1 LIMIT 1;
-- Tools
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a hammer'                  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a pair of tongs'           AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a pickaxe'                 AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a shovel'                  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 18,id,-1,-1,3600 FROM items WHERE name='a shard of glaes'          AND is_template=1 LIMIT 1;
