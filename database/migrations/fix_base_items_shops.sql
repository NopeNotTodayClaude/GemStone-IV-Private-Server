-- ============================================================
-- fix_base_items_shops.sql
-- Remove ALL material-variant items from shops.
-- Shops sell ONE base item per type (no material in name).
-- Material variants stay in items table for the CUSTOMIZE system.
-- ============================================================

USE gemstone_dev;

-- ============================================================
-- SECTION 1: INSERT BASE WEAPON ITEMS (no material prefix)
-- These are the items players BUY. Customize upgrades the material.
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,weapon_category,damage_factor,weapon_speed,damage_type,attack_bonus,damage_bonus,enchant_bonus,material_bonus,description,is_template) VALUES
('a dagger','dagger','dagger','dagger','a','weapon','none',1,50,'edged',0.250,2,'slash,puncture',0,0,0,0,'A plain dagger.',1),
('a main gauche','main gauche','gauche','main gauche','a','weapon','none',2,100,'edged',0.275,2,'slash,puncture',0,0,0,0,'A balanced parrying dagger.',1),
('a short sword','short sword','sword','short sword','a','weapon','none',3,150,'edged',0.350,3,'slash,puncture',0,0,0,0,'A short single-edged sword.',1),
('a backsword','backsword','backsword','backsword','a','weapon','none',3,175,'edged',0.375,3,'slash,puncture',0,0,0,0,'A single-edged backsword.',1),
('a broadsword','broadsword','broadsword','broadsword','a','weapon','none',4,200,'edged',0.400,4,'slash,puncture',0,0,0,0,'A sturdy broadsword.',1),
('a longsword','longsword','longsword','longsword','a','weapon','none',5,250,'edged',0.425,5,'slash,puncture',0,0,0,0,'A versatile longsword.',1),
('a rapier','rapier','rapier','rapier','a','weapon','none',2,175,'edged',0.325,2,'slash,puncture',0,0,0,0,'A slender thrusting rapier.',1),
('a falchion','falchion','falchion','falchion','a','weapon','none',3,200,'edged',0.375,4,'slash',0,0,0,0,'A curved single-edged falchion.',1),
('a scimitar','scimitar','scimitar','scimitar','a','weapon','none',3,200,'edged',0.400,4,'slash',0,0,0,0,'A curved scimitar.',1),
('a war hammer','war hammer','hammer','war hammer','a','weapon','none',5,250,'blunt',0.500,6,'crush',0,0,0,0,'A heavy war hammer.',1),
('a mace','mace','mace','mace','a','weapon','none',4,225,'blunt',0.475,5,'crush',0,0,0,0,'A flanged mace.',1),
('a cudgel','cudgel','cudgel','cudgel','a','weapon','none',2,100,'blunt',0.375,4,'crush',0,0,0,0,'A stout wooden cudgel.',1),
('a claidhmore','claidhmore','claidhmore','claidhmore','a','weapon','none',8,400,'twohanded',0.550,8,'slash,crush',0,0,0,0,'A massive two-handed claidhmore.',1),
('a greatsword','greatsword','greatsword','greatsword','a','weapon','none',7,350,'twohanded',0.525,7,'slash,crush',0,0,0,0,'A large two-handed greatsword.',1),
('a spear','spear','spear','spear','a','weapon','none',4,200,'polearm',0.475,5,'puncture,slash',0,0,0,0,'A sturdy wooden-shafted spear.',1),
('a halberd','halberd','halberd','halberd','a','weapon','none',7,350,'polearm',0.525,6,'slash,puncture',0,0,0,0,'A pole-axe halberd.',1),
('a dart','dart','dart','dart','a','weapon','none',0.5,25,'thrown',0.200,1,'puncture',0,0,0,0,'A small throwing dart.',1),
('a javelin','javelin','javelin','javelin','a','weapon','none',2,75,'thrown',0.325,3,'puncture',0,0,0,0,'A throwing javelin.',1);

-- ============================================================
-- SECTION 2: INSERT BASE ARMOR ITEMS (no material prefix)
-- Soft leather and cloth already exist as base (IDs 70-81).
-- Only chain-type and plate armor need new base entries.
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,armor_asg,defense_bonus,action_penalty,spell_hindrance,worn_location,description,is_template) VALUES
('some chain mail','chain mail','mail','chain mail','some','armor','none',12,750,11,11,10,5,'torso','A suit of interlocking chain links.',1),
('a chain hauberk','chain hauberk','hauberk','chain hauberk','a','armor','none',15,1500,12,13,15,15,'torso','A heavy double-linked chain hauberk.',1),
('some augmented chain','augmented chain','chain','augmented chain','some','armor','none',18,2500,13,15,20,25,'torso','Chain reinforced at the critical strike points.',1),
('some half plate','half plate','armor','half plate','some','armor','none',25,4000,15,17,25,40,'torso','A suit of half plate covering chest and limbs.',1);

-- ============================================================
-- SECTION 3: INSERT BASE SHIELD ITEMS (no material prefix)
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,shield_type,shield_ds,shield_size,shield_evade_penalty,worn_location,description,is_template) VALUES
('a buckler','buckler','buckler','buckler','a','shield','none',2,100,'small',15,'small',0,'arm','A small round buckler.',1),
('a target shield','target shield','shield','target shield','a','shield','none',4,200,'medium',20,'medium',-5,'arm','A medium-sized target shield.',1),
('a kite shield','kite shield','shield','kite shield','a','shield','none',6,350,'medium',25,'medium',-10,'arm','A medium kite-shaped shield.',1),
('a greatshield','greatshield','shield','greatshield','a','shield','none',10,600,'large',30,'large',-20,'arm','A large tower greatshield.',1);

-- ============================================================
-- SECTION 4: BASE ARCHERY ITEMS (crossbows/thrown without material)
-- Bows stay differentiated by wood (yew/oak) - that IS their identity.
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,weapon_category,damage_factor,weapon_speed,damage_type,attack_bonus,damage_bonus,enchant_bonus,material_bonus,description,is_template) VALUES
('a light crossbow','light crossbow','crossbow','light crossbow','a','weapon','none',5,200,'ranged',0.325,5,'puncture',0,0,0,0,'A light crossbow.',1),
('a heavy crossbow','heavy crossbow','crossbow','heavy crossbow','a','weapon','none',8,325,'ranged',0.450,7,'puncture',0,0,0,0,'A heavy crossbow.',1);

-- ============================================================
-- SECTION 5: REBUILD SHOP INVENTORIES - WEAPONS (shop 1)
-- One of each base weapon type only.
-- ============================================================

DELETE FROM shop_inventory WHERE shop_id = 1;

INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a dagger'      AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a main gauche' AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a short sword' AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a backsword'   AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a broadsword'  AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a longsword'   AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a rapier'      AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a falchion'    AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a scimitar'    AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a war hammer'  AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a mace'        AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a cudgel'      AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a claidhmore'  AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a greatsword'  AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a spear'       AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a halberd'     AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a dart'        AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 1,id,-1,0,3600 FROM items WHERE name='a javelin'     AND is_template=1 AND material='none' LIMIT 1;

-- ============================================================
-- SECTION 6: REBUILD SHOP INVENTORIES - ARMORY (shop 2)
-- Cloth/leather use existing base items (IDs 70-81, no material in name).
-- Chain/plate use new base items.
-- ============================================================

DELETE FROM shop_inventory WHERE shop_id = 2;

-- Soft armor / cloth (existing base items by exact name)
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some normal clothing'     AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some flowing robes'       AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some padded armor'        AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some light leather armor' AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some full leather armor'  AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some reinforced leather'  AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some double leather armor' AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some leather breastplate' AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some studded leather armor' AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='a metal breastplate'      AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='a suit of full plate armor' AND is_template=1 LIMIT 1;

-- Chain / plate (new base items, material='none')
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some chain mail'     AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='a chain hauberk'     AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some augmented chain' AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='some half plate'      AND is_template=1 AND material='none' LIMIT 1;

-- Shields (new base items, material='none')
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='a buckler'       AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='a target shield'  AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='a kite shield'    AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 2,id,-1,0,3600 FROM items WHERE name='a greatshield'    AND is_template=1 AND material='none' LIMIT 1;

-- ============================================================
-- SECTION 7: REBUILD SHOP INVENTORIES - ARCHERY (shop 13)
-- Bows: yew/oak variants are fine (wood = bow identity, not upgradeable).
-- Crossbows: base only (no iron/steel prefix).
-- Thrown: base only.
-- Ammo: stays as-is.
-- ============================================================

DELETE FROM shop_inventory WHERE shop_id = 13;

-- Bows (wood type IS their identity - not material-customizable)
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a yew short bow'      AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='an oak short bow'      AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a yew long bow'        AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='an oak long bow'       AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a yew composite bow'   AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='an oak composite bow'  AND is_template=1 LIMIT 1;

-- Crossbows (base, no material prefix)
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a light crossbow' AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a heavy crossbow' AND is_template=1 AND material='none' LIMIT 1;

-- Thrown (base, no material prefix)
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a dart'    AND is_template=1 AND material='none' LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a javelin' AND is_template=1 AND material='none' LIMIT 1;

-- Ammo (no material upgrade path - stays as-is)
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a fletched hunting arrow' AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a bundle of war arrows'  AND is_template=1 LIMIT 1;
INSERT INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
SELECT 13,id,-1,0,3600 FROM items WHERE name='a steel-headed war bolt' AND is_template=1 LIMIT 1;

-- ============================================================
-- VERIFICATION
-- ============================================================

SELECT 'fix_base_items_shops.sql complete.' AS status;

SELECT s.id, s.name AS shop, COUNT(si.item_id) AS items
FROM shops s JOIN shop_inventory si ON s.id=si.shop_id
WHERE s.id IN (1,2,13)
GROUP BY s.id, s.name;

SELECT i.name, i.item_type, i.material
FROM shop_inventory si
JOIN items i ON si.item_id=i.id
WHERE si.shop_id=1
ORDER BY i.weapon_category, i.noun;
