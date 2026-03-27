-- ============================================================
-- fix_items_master.sql
-- Complete item data cleanup and restoration for GemStone IV
--
-- Run with:
--   mysql -u root gemstone_dev < fix_items_master.sql
--
-- What this does:
--   1. Removes bad lockpick records (wrong item_type)
--   2. Renames mis-named existing items to match seed expectations
--   3. Inserts all 18 canonical GS4 lockpick materials + tools
--   4. Inserts iron/bronze/mithril/vultite/vaalorn weapon variants
--   5. Inserts armor/shield material variants
--   6. Inserts clothing (linen/cotton/silk/wool/satin/velvet)
--   7. Inserts gems, magic items, food, forging supplies, archery
--   8. Adds missing herbs
--   9. Clears shop_inventory so seed can repopulate cleanly
-- ============================================================

USE gemstone_dev;

SET FOREIGN_KEY_CHECKS=0;

-- ============================================================
-- SECTION 1: CLEANUP
-- ============================================================

-- Remove the 5 bad lockpicks (item_type='lockpick' is wrong, should be misc)
DELETE FROM shop_inventory WHERE item_id IN (
    SELECT id FROM items WHERE noun = 'lockpick' AND item_type = 'lockpick'
);
DELETE FROM character_inventory WHERE item_id IN (
    SELECT id FROM items WHERE noun = 'lockpick' AND item_type = 'lockpick'
);
DELETE FROM items WHERE noun = 'lockpick' AND item_type = 'lockpick';

-- Remove duplicate armor rows that snuck in
DELETE FROM items WHERE id = 352;
DELETE FROM items WHERE id = 353;

SET FOREIGN_KEY_CHECKS=1;

-- ============================================================
-- SECTION 2: RENAME EXISTING ITEMS TO MATCH SEED EXPECTATIONS
-- ============================================================

UPDATE items SET name='some reinforced leather', short_name='reinforced leather'
    WHERE id = 75 AND name LIKE '%reinforced leather%';

UPDATE items SET name='some leather breastplate', short_name='leather breastplate', article='some'
    WHERE id = 77;

UPDATE items SET name='a steel chain mail', short_name='steel chain mail', article='a', noun='mail'
    WHERE id = 79;

UPDATE items SET name='a steel claidhmore', short_name='steel claidhmore', material='steel'
    WHERE id = 106 AND name = 'a claidhmore';

UPDATE items SET name='a sprig of acantha leaf', short_name='sprig of acantha leaf', article='a', noun='acantha leaf' WHERE id = 601;
UPDATE items SET name='a sprig of aloeas stem', short_name='sprig of aloeas stem', article='a', noun='aloeas stem' WHERE id = 609;
UPDATE items SET name='a sprig of cactacae spine', short_name='sprig of cactacae spine', article='a', noun='cactacae spine' WHERE id = 608;
UPDATE items SET name='a sprig of torban leaf', short_name='sprig of torban leaf', article='a', noun='torban leaf' WHERE id = 603;
UPDATE items SET name='a stem of ambrominas leaf', short_name='stem of ambrominas leaf', article='a', noun='ambrominas leaf' WHERE id = 606;

UPDATE items SET name='some bolmara potion', short_name='bolmara potion', article='some' WHERE id = 616;
UPDATE items SET name='some brostheras potion', short_name='brostheras potion', article='some' WHERE id = 618;
UPDATE items SET name='some rose-marrow potion', short_name='rose-marrow potion', article='some' WHERE id = 617;
UPDATE items SET name='some talneo potion', short_name='talneo potion', article='some' WHERE id = 619;
UPDATE items SET name='some wingstem potion', short_name='wingstem potion', article='some' WHERE id = 620;

-- ============================================================
-- SECTION 3: LOCKPICKS - Full canonical GS4 list (18 materials)
-- ============================================================

INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, lockpick_modifier, weight, value, description, is_template) VALUES
('a copper lockpick','copper lockpick','lockpick','copper lockpick','a','misc','copper',1.00,1,100,'A simple copper lockpick, the cheapest and most forgiving pick available.',1),
('a brass lockpick','brass lockpick','lockpick','brass lockpick','a','misc','brass',1.05,1,250,'A brass lockpick, the standard choice for novice rogues.',1),
('a steel lockpick','steel lockpick','lockpick','steel lockpick','a','misc','steel',1.10,1,500,'A steel lockpick with better precision than copper or brass.',1),
('an ivory lockpick','ivory lockpick','lockpick','ivory lockpick','an','misc','ivory',1.20,1,750,'A slender ivory lockpick with natural flexibility.',1),
('a gold lockpick','gold lockpick','lockpick','gold lockpick','a','misc','gold',1.20,1,2000,'A gleaming gold lockpick.  Softer than steel but precise in skilled hands.',1),
('a silver lockpick','silver lockpick','lockpick','silver lockpick','a','misc','silver',1.30,1,2500,'A bright silver lockpick, well-balanced but requiring a practiced touch.',1),
('a mithril lockpick','mithril lockpick','lockpick','mithril lockpick','a','misc','mithril',1.50,1,6000,'A mithril lockpick of fine quality.',1),
('an ora lockpick','ora lockpick','lockpick','ora lockpick','an','misc','ora',1.60,1,5000,'A well-balanced ora lockpick favored by journeyman rogues.',1),
('a glaes lockpick','glaes lockpick','lockpick','glaes lockpick','a','misc','glaes',1.75,1,9500,'A glaes lockpick whose hardness allows exceptional durability.',1),
('a laje lockpick','laje lockpick','lockpick','laje lockpick','a','misc','laje',1.80,1,17000,'A slender laje lockpick.  Exceptional precision but fragile.',1),
('a vultite lockpick','vultite lockpick','lockpick','vultite lockpick','a','misc','vultite',1.90,1,30000,'A vultite lockpick for experienced rogues.',1),
('a rolaren lockpick','rolaren lockpick','lockpick','rolaren lockpick','a','misc','rolaren',2.00,1,17000,'A rolaren lockpick combining precision with excellent durability.',1),
('a veniom lockpick','veniom lockpick','lockpick','veniom lockpick','a','misc','veniom',2.10,1,50000,'A veniom lockpick of highly accurate quality.',1),
('an invar lockpick','invar lockpick','lockpick','invar lockpick','an','misc','invar',2.20,1,75000,'An invar lockpick of masterwork quality.',1),
('an alum lockpick','alum lockpick','lockpick','alum lockpick','an','misc','alum',2.00,1,23000,'An alum lockpick - excellent precision but very fragile.',1),
('a kelyn lockpick','kelyn lockpick','lockpick','kelyn lockpick','a','misc','kelyn',2.25,1,62000,'A kelyn lockpick of incredible precision.',1),
('a golvern lockpick','golvern lockpick','lockpick','golvern lockpick','a','misc','golvern',2.35,1,95000,'An incredibly hard golvern lockpick of masterwork quality.',1),
('a vaalin lockpick','vaalin lockpick','lockpick','vaalin lockpick','a','misc','vaalin',2.50,1,125000,'A flawlessly crafted vaalin lockpick, the finest known to locksmithing.',1);

INSERT IGNORE INTO items (name, short_name, noun, base_name, article, item_type, material, weight, value, worn_location, container_capacity, container_type, description, is_template) VALUES
('a lockpick case','lockpick case','case','lockpick case','a','container','leather',0.5,500,'belt',18,'lockpick','A small leather case with loops for lockpicks.',1),
('a key ring','key ring','ring','key ring','a','container','steel',0.2,100,'belt',20,'keychain','A sturdy steel ring for holding keys.',1);

-- ============================================================
-- SECTION 4: WEAPONS - Iron / Bronze / Mithril / Vultite / Vaalorn
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,weapon_category,damage_factor,weapon_speed,damage_type,attack_bonus,damage_bonus,enchant_bonus,material_bonus,description,is_template) VALUES
('an iron dagger','iron dagger','dagger','dagger','an','weapon','iron',1,30,'edged',0.250,2,'slash,puncture',0,0,0,0,'A crude iron dagger.',1),
('a bronze dagger','bronze dagger','dagger','dagger','a','weapon','bronze',1,40,'edged',0.250,2,'slash,puncture',0,0,0,0,'A bronze dagger.',1),
('a mithril dagger','mithril dagger','dagger','dagger','a','weapon','mithril',1,150,'edged',0.250,2,'slash,puncture',0,0,0,0,'A mithril dagger.',1),
('a vultite dagger','vultite dagger','dagger','dagger','a','weapon','vultite',1,400,'edged',0.250,2,'slash,puncture',0,0,0,0,'A vultite dagger.',1),
('a vaalorn dagger','vaalorn dagger','dagger','dagger','a','weapon','vaalorn',1,750,'edged',0.250,2,'slash,puncture',0,0,0,0,'A vaalorn dagger of elven make.',1),
('an iron main gauche','iron main gauche','gauche','main gauche','an','weapon','iron',2,60,'edged',0.275,2,'slash,puncture',0,0,0,0,'An iron parrying dagger.',1),
('a bronze main gauche','bronze main gauche','gauche','main gauche','a','weapon','bronze',2,80,'edged',0.275,2,'slash,puncture',0,0,0,0,'A bronze main gauche.',1),
('a mithril main gauche','mithril main gauche','gauche','main gauche','a','weapon','mithril',2,360,'edged',0.275,2,'slash,puncture',0,0,0,0,'A mithril main gauche.',1),
('a vultite main gauche','vultite main gauche','gauche','main gauche','a','weapon','vultite',2,960,'edged',0.275,2,'slash,puncture',0,0,0,0,'A vultite main gauche.',1),
('a vaalorn main gauche','vaalorn main gauche','gauche','main gauche','a','weapon','vaalorn',2,1800,'edged',0.275,2,'slash,puncture',0,0,0,0,'A vaalorn main gauche.',1),
('an iron short sword','iron short sword','sword','short sword','an','weapon','iron',3,75,'edged',0.350,3,'slash,puncture',0,0,0,0,'An iron short sword.',1),
('a bronze short sword','bronze short sword','sword','short sword','a','weapon','bronze',3,100,'edged',0.350,3,'slash,puncture',0,0,0,0,'A bronze short sword.',1),
('a mithril short sword','mithril short sword','sword','short sword','a','weapon','mithril',3,450,'edged',0.350,3,'slash,puncture',0,0,0,0,'A mithril short sword.',1),
('a vultite short sword','vultite short sword','sword','short sword','a','weapon','vultite',3,1200,'edged',0.350,3,'slash,puncture',0,0,0,0,'A vultite short sword.',1),
('a vaalorn short sword','vaalorn short sword','sword','short sword','a','weapon','vaalorn',3,2250,'edged',0.350,3,'slash,puncture',0,0,0,0,'A vaalorn short sword.',1),
('an iron backsword','iron backsword','backsword','backsword','an','weapon','iron',3,100,'edged',0.375,3,'slash,puncture',0,0,0,0,'An iron backsword.',1),
('a bronze backsword','bronze backsword','backsword','backsword','a','weapon','bronze',3,140,'edged',0.375,3,'slash,puncture',0,0,0,0,'A bronze backsword.',1),
('a mithril backsword','mithril backsword','backsword','backsword','a','weapon','mithril',3,600,'edged',0.375,3,'slash,puncture',0,0,0,0,'A mithril backsword.',1),
('a vultite backsword','vultite backsword','backsword','backsword','a','weapon','vultite',3,1600,'edged',0.375,3,'slash,puncture',0,0,0,0,'A vultite backsword.',1),
('a vaalorn backsword','vaalorn backsword','backsword','backsword','a','weapon','vaalorn',3,3000,'edged',0.375,3,'slash,puncture',0,0,0,0,'A vaalorn backsword.',1),
('an iron broadsword','iron broadsword','broadsword','broadsword','an','weapon','iron',4,120,'edged',0.400,4,'slash,puncture',0,0,0,0,'An iron broadsword.',1),
('a bronze broadsword','bronze broadsword','broadsword','broadsword','a','weapon','bronze',4,160,'edged',0.400,4,'slash,puncture',0,0,0,0,'A bronze broadsword.',1),
('a mithril broadsword','mithril broadsword','broadsword','broadsword','a','weapon','mithril',4,640,'edged',0.400,4,'slash,puncture',0,0,0,0,'A mithril broadsword.',1),
('a vultite broadsword','vultite broadsword','broadsword','broadsword','a','weapon','vultite',4,1700,'edged',0.400,4,'slash,puncture',0,0,0,0,'A vultite broadsword.',1),
('a vaalorn broadsword','vaalorn broadsword','broadsword','broadsword','a','weapon','vaalorn',4,3200,'edged',0.400,4,'slash,puncture',0,0,0,0,'A vaalorn broadsword.',1),
('an iron longsword','iron longsword','longsword','longsword','an','weapon','iron',5,150,'edged',0.425,5,'slash,puncture',0,0,0,0,'An iron longsword.',1),
('a bronze longsword','bronze longsword','longsword','longsword','a','weapon','bronze',5,200,'edged',0.425,5,'slash,puncture',0,0,0,0,'A bronze longsword.',1),
('a mithril longsword','mithril longsword','longsword','longsword','a','weapon','mithril',5,800,'edged',0.425,5,'slash,puncture',0,0,0,0,'A mithril longsword.',1),
('a vultite longsword','vultite longsword','longsword','longsword','a','weapon','vultite',5,2100,'edged',0.425,5,'slash,puncture',0,0,0,0,'A vultite longsword.',1),
('a vaalorn longsword','vaalorn longsword','longsword','longsword','a','weapon','vaalorn',5,4000,'edged',0.425,5,'slash,puncture',0,0,0,0,'A vaalorn longsword.',1),
('an iron rapier','iron rapier','rapier','rapier','an','weapon','iron',2,90,'edged',0.325,2,'slash,puncture',0,0,0,0,'An iron rapier.',1),
('a bronze rapier','bronze rapier','rapier','rapier','a','weapon','bronze',2,120,'edged',0.325,2,'slash,puncture',0,0,0,0,'A bronze rapier.',1),
('a mithril rapier','mithril rapier','rapier','rapier','a','weapon','mithril',2,480,'edged',0.325,2,'slash,puncture',0,0,0,0,'A mithril rapier.',1),
('a vultite rapier','vultite rapier','rapier','rapier','a','weapon','vultite',2,1280,'edged',0.325,2,'slash,puncture',0,0,0,0,'A vultite rapier.',1),
('a vaalorn rapier','vaalorn rapier','rapier','rapier','a','weapon','vaalorn',2,2400,'edged',0.325,2,'slash,puncture',0,0,0,0,'A vaalorn rapier.',1),
('an iron falchion','iron falchion','falchion','falchion','an','weapon','iron',3,100,'edged',0.375,4,'slash',0,0,0,0,'An iron falchion.',1),
('a bronze falchion','bronze falchion','falchion','falchion','a','weapon','bronze',3,140,'edged',0.375,4,'slash',0,0,0,0,'A bronze falchion.',1),
('a mithril falchion','mithril falchion','falchion','falchion','a','weapon','mithril',3,600,'edged',0.375,4,'slash',0,0,0,0,'A mithril falchion.',1),
('a vultite falchion','vultite falchion','falchion','falchion','a','weapon','vultite',3,1600,'edged',0.375,4,'slash',0,0,0,0,'A vultite falchion.',1),
('a vaalorn falchion','vaalorn falchion','falchion','falchion','a','weapon','vaalorn',3,3000,'edged',0.375,4,'slash',0,0,0,0,'A vaalorn falchion.',1),
('an iron scimitar','iron scimitar','scimitar','scimitar','an','weapon','iron',3,110,'edged',0.400,4,'slash',0,0,0,0,'An iron scimitar.',1),
('a bronze scimitar','bronze scimitar','scimitar','scimitar','a','weapon','bronze',3,150,'edged',0.400,4,'slash',0,0,0,0,'A bronze scimitar.',1),
('a mithril scimitar','mithril scimitar','scimitar','scimitar','a','weapon','mithril',3,640,'edged',0.400,4,'slash',0,0,0,0,'A mithril scimitar.',1),
('a vultite scimitar','vultite scimitar','scimitar','scimitar','a','weapon','vultite',3,1720,'edged',0.400,4,'slash',0,0,0,0,'A vultite scimitar.',1),
('a vaalorn scimitar','vaalorn scimitar','scimitar','scimitar','a','weapon','vaalorn',3,3200,'edged',0.400,4,'slash',0,0,0,0,'A vaalorn scimitar.',1),
('an iron war hammer','iron war hammer','hammer','war hammer','an','weapon','iron',5,140,'blunt',0.500,6,'crush',0,0,0,0,'An iron war hammer.',1),
('a bronze war hammer','bronze war hammer','hammer','war hammer','a','weapon','bronze',5,185,'blunt',0.500,6,'crush',0,0,0,0,'A bronze war hammer.',1),
('a mithril war hammer','mithril war hammer','hammer','war hammer','a','weapon','mithril',5,750,'blunt',0.500,6,'crush',0,0,0,0,'A mithril war hammer.',1),
('a vultite war hammer','vultite war hammer','hammer','war hammer','a','weapon','vultite',5,2000,'blunt',0.500,6,'crush',0,0,0,0,'A vultite war hammer.',1),
('a vaalorn war hammer','vaalorn war hammer','hammer','war hammer','a','weapon','vaalorn',5,3750,'blunt',0.500,6,'crush',0,0,0,0,'A vaalorn war hammer.',1),
('an iron mace','iron mace','mace','mace','an','weapon','iron',4,120,'blunt',0.475,5,'crush',0,0,0,0,'An iron mace.',1),
('a bronze mace','bronze mace','mace','mace','a','weapon','bronze',4,160,'blunt',0.475,5,'crush',0,0,0,0,'A bronze mace.',1),
('a mithril mace','mithril mace','mace','mace','a','weapon','mithril',4,640,'blunt',0.475,5,'crush',0,0,0,0,'A mithril mace.',1),
('a vultite mace','vultite mace','mace','mace','a','weapon','vultite',4,1700,'blunt',0.475,5,'crush',0,0,0,0,'A vultite mace.',1),
('a vaalorn mace','vaalorn mace','mace','mace','a','weapon','vaalorn',4,3200,'blunt',0.475,5,'crush',0,0,0,0,'A vaalorn mace.',1),
('an iron cudgel','iron cudgel','cudgel','cudgel','an','weapon','iron',2,40,'blunt',0.375,4,'crush',0,0,0,0,'An iron cudgel.',1),
('a steel cudgel','steel cudgel','cudgel','cudgel','a','weapon','steel',2,65,'blunt',0.375,4,'crush',0,0,0,0,'A steel cudgel.',1),
('a bronze cudgel','bronze cudgel','cudgel','cudgel','a','weapon','bronze',2,50,'blunt',0.375,4,'crush',0,0,0,0,'A bronze cudgel.',1),
('an iron claidhmore','iron claidhmore','claidhmore','claidhmore','an','weapon','iron',8,200,'twohanded',0.550,8,'slash,crush',0,0,0,0,'A large iron two-handed sword.',1),
('a bronze claidhmore','bronze claidhmore','claidhmore','claidhmore','a','weapon','bronze',8,300,'twohanded',0.550,8,'slash,crush',0,0,0,0,'A large bronze claidhmore.',1),
('a mithril claidhmore','mithril claidhmore','claidhmore','claidhmore','a','weapon','mithril',8,1200,'twohanded',0.550,8,'slash,crush',0,0,0,0,'A mithril claidhmore.',1),
('a vultite claidhmore','vultite claidhmore','claidhmore','claidhmore','a','weapon','vultite',8,3200,'twohanded',0.550,8,'slash,crush',0,0,0,0,'A vultite claidhmore.',1),
('a vaalorn claidhmore','vaalorn claidhmore','claidhmore','claidhmore','a','weapon','vaalorn',8,6000,'twohanded',0.550,8,'slash,crush',0,0,0,0,'A vaalorn claidhmore.',1),
('an iron greatsword','iron greatsword','greatsword','greatsword','an','weapon','iron',7,180,'twohanded',0.525,7,'slash,crush',0,0,0,0,'A large iron greatsword.',1),
('a steel greatsword','steel greatsword','greatsword','greatsword','a','weapon','steel',7,300,'twohanded',0.525,7,'slash,crush',0,0,0,0,'A large steel greatsword.',1),
('a bronze greatsword','bronze greatsword','greatsword','greatsword','a','weapon','bronze',7,250,'twohanded',0.525,7,'slash,crush',0,0,0,0,'A bronze greatsword.',1),
('a mithril greatsword','mithril greatsword','greatsword','greatsword','a','weapon','mithril',7,1100,'twohanded',0.525,7,'slash,crush',0,0,0,0,'A mithril greatsword.',1),
('a vultite greatsword','vultite greatsword','greatsword','greatsword','a','weapon','vultite',7,2900,'twohanded',0.525,7,'slash,crush',0,0,0,0,'A vultite greatsword.',1),
('a vaalorn greatsword','vaalorn greatsword','greatsword','greatsword','a','weapon','vaalorn',7,5500,'twohanded',0.525,7,'slash,crush',0,0,0,0,'A vaalorn greatsword.',1),
('an iron spear','iron spear','spear','spear','an','weapon','iron',4,100,'polearm',0.475,5,'puncture,slash',0,0,0,0,'An iron spear.',1),
('a steel spear','steel spear','spear','spear','a','weapon','steel',4,170,'polearm',0.475,5,'puncture,slash',0,0,0,0,'A steel spear.',1),
('a bronze spear','bronze spear','spear','spear','a','weapon','bronze',4,130,'polearm',0.475,5,'puncture,slash',0,0,0,0,'A bronze spear.',1),
('a mithril spear','mithril spear','spear','spear','a','weapon','mithril',4,680,'polearm',0.475,5,'puncture,slash',0,0,0,0,'A mithril spear.',1),
('a vultite spear','vultite spear','spear','spear','a','weapon','vultite',4,1800,'polearm',0.475,5,'puncture,slash',0,0,0,0,'A vultite spear.',1),
('a vaalorn spear','vaalorn spear','spear','spear','a','weapon','vaalorn',4,3400,'polearm',0.475,5,'puncture,slash',0,0,0,0,'A vaalorn spear.',1),
('an iron halberd','iron halberd','halberd','halberd','an','weapon','iron',7,200,'polearm',0.525,6,'slash,puncture',0,0,0,0,'An iron halberd.',1),
('a steel halberd','steel halberd','halberd','halberd','a','weapon','steel',7,330,'polearm',0.525,6,'slash,puncture',0,0,0,0,'A steel halberd.',1),
('a bronze halberd','bronze halberd','halberd','halberd','a','weapon','bronze',7,260,'polearm',0.525,6,'slash,puncture',0,0,0,0,'A bronze halberd.',1),
('a mithril halberd','mithril halberd','halberd','halberd','a','weapon','mithril',7,1200,'polearm',0.525,6,'slash,puncture',0,0,0,0,'A mithril halberd.',1),
('a vultite halberd','vultite halberd','halberd','halberd','a','weapon','vultite',7,3200,'polearm',0.525,6,'slash,puncture',0,0,0,0,'A vultite halberd.',1),
('a vaalorn halberd','vaalorn halberd','halberd','halberd','a','weapon','vaalorn',7,6000,'polearm',0.525,6,'slash,puncture',0,0,0,0,'A vaalorn halberd.',1),
('an iron dart','iron dart','dart','dart','an','weapon','iron',0.5,20,'thrown',0.200,1,'puncture',0,0,0,0,'A small iron throwing dart.',1),
('a steel dart','steel dart','dart','dart','a','weapon','steel',0.5,30,'thrown',0.200,1,'puncture',0,0,0,0,'A small steel throwing dart.',1),
('an iron javelin','iron javelin','javelin','javelin','an','weapon','iron',2,50,'thrown',0.325,3,'puncture',0,0,0,0,'An iron throwing javelin.',1),
('a steel javelin','steel javelin','javelin','javelin','a','weapon','steel',2,80,'thrown',0.325,3,'puncture',0,0,0,0,'A steel throwing javelin.',1);

-- ============================================================
-- SECTION 5: ARMOR VARIANTS
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,armor_asg,defense_bonus,action_penalty,spell_hindrance,worn_location,description,is_template) VALUES
('a linen flowing robes','linen flowing robes','robes','flowing robes','a','armor','linen',2,80,2,0,0,0,'torso','Simple linen robes favored by mages.',1),
('a cotton flowing robes','cotton flowing robes','robes','flowing robes','a','armor','cotton',2,100,2,0,0,0,'torso','Comfortable cotton flowing robes.',1),
('a silk flowing robes','silk flowing robes','robes','flowing robes','a','armor','silk',2,350,2,0,0,0,'torso','Finely woven silk robes.',1),
('a velvet flowing robes','velvet flowing robes','robes','flowing robes','a','armor','velvet',2,600,2,0,0,0,'torso','Rich velvet flowing robes.',1),
('a linen normal clothing','linen normal clothing','clothing','normal clothing','a','armor','linen',1.5,40,1,0,0,0,'torso','Simple linen clothing.',1),
('a cotton normal clothing','cotton normal clothing','clothing','normal clothing','a','armor','cotton',1.5,50,1,0,0,0,'torso','Plain cotton clothing.',1),
('a silk normal clothing','silk normal clothing','clothing','normal clothing','a','armor','silk',1.5,250,1,0,0,0,'torso','Smooth silk clothing.',1),
('a wool normal clothing','wool normal clothing','clothing','normal clothing','a','armor','wool',1.5,70,1,0,0,0,'torso','Warm wool clothing.',1),
('a satin normal clothing','satin normal clothing','clothing','normal clothing','a','armor','satin',1.5,350,1,0,0,0,'torso','Fine satin clothing.',1),
('a velvet normal clothing','velvet normal clothing','clothing','normal clothing','a','armor','velvet',1.5,500,1,0,0,0,'torso','Luxurious velvet clothing.',1),
('an iron chain mail','iron chain mail','mail','chain mail','an','armor','iron',12,600,11,11,10,5,'torso','A suit of iron chain mail.',1),
('a bronze chain mail','bronze chain mail','mail','chain mail','a','armor','bronze',12,900,11,11,10,5,'torso','A suit of bronze chain mail.',1),
('a mithril chain mail','mithril chain mail','mail','chain mail','a','armor','mithril',12,4500,11,11,10,5,'torso','Finely wrought mithril chain mail.',1),
('a vultite chain mail','vultite chain mail','mail','chain mail','a','armor','vultite',12,12000,11,11,10,5,'torso','Gleaming vultite chain mail.',1),
('a vaalorn chain mail','vaalorn chain mail','mail','chain mail','a','armor','vaalorn',12,22500,11,11,10,5,'torso','Elven-crafted vaalorn chain mail.',1),
('an iron chain hauberk','iron chain hauberk','hauberk','chain hauberk','an','armor','iron',15,1200,12,13,15,15,'torso','A heavy iron double chain hauberk.',1),
('a steel chain hauberk','steel chain hauberk','hauberk','chain hauberk','a','armor','steel',15,2000,12,13,15,15,'torso','A heavy steel chain hauberk.',1),
('a mithril chain hauberk','mithril chain hauberk','hauberk','chain hauberk','a','armor','mithril',15,8000,12,13,15,15,'torso','A mithril chain hauberk.',1),
('a vultite chain hauberk','vultite chain hauberk','hauberk','chain hauberk','a','armor','vultite',15,21000,12,13,15,15,'torso','A vultite chain hauberk.',1),
('a vaalorn chain hauberk','vaalorn chain hauberk','hauberk','chain hauberk','a','armor','vaalorn',15,40000,12,13,15,15,'torso','A vaalorn chain hauberk.',1),
('an iron augmented chain','iron augmented chain','chain','augmented chain','an','armor','iron',18,1800,13,15,20,25,'torso','Iron chain reinforced at critical points.',1),
('a steel augmented chain','steel augmented chain','chain','augmented chain','a','armor','steel',18,3000,13,15,20,25,'torso','Steel augmented chain.',1),
('a vultite augmented chain','vultite augmented chain','chain','augmented chain','a','armor','vultite',18,28000,13,15,20,25,'torso','Vultite augmented chain.',1),
('a vaalorn augmented chain','vaalorn augmented chain','chain','augmented chain','a','armor','vaalorn',18,52000,13,15,20,25,'torso','Vaalorn augmented chain.',1),
('an iron half plate','iron half plate','armor','half plate','an','armor','iron',25,2000,15,17,25,40,'torso','Iron half plate.',1),
('a steel half plate','steel half plate','armor','half plate','a','armor','steel',25,3500,15,17,25,40,'torso','Steel half plate armor.',1),
('a mithril half plate','mithril half plate','armor','half plate','a','armor','mithril',25,14000,15,17,25,40,'torso','Mithril half plate of masterwork quality.',1),
('a vultite half plate','vultite half plate','armor','half plate','a','armor','vultite',25,37000,15,17,25,40,'torso','Vultite half plate.',1),
('a vaalorn half plate','vaalorn half plate','armor','half plate','a','armor','vaalorn',25,70000,15,17,25,40,'torso','Vaalorn half plate of elven make.',1);

-- ============================================================
-- SECTION 6: SHIELD VARIANTS
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,shield_type,shield_ds,shield_size,shield_evade_penalty,worn_location,description,is_template) VALUES
('an iron buckler','iron buckler','buckler','buckler','an','shield','iron',2,60,'small',15,'small',0,'arm','A small iron shield.',1),
('a bronze buckler','bronze buckler','buckler','buckler','a','shield','bronze',2,80,'small',15,'small',0,'arm','A small bronze shield.',1),
('a mithril buckler','mithril buckler','buckler','buckler','a','shield','mithril',2,400,'small',15,'small',0,'arm','A small mithril shield.',1),
('a vultite buckler','vultite buckler','buckler','buckler','a','shield','vultite',2,1000,'small',15,'small',0,'arm','A small vultite shield.',1),
('a vaalorn buckler','vaalorn buckler','buckler','buckler','a','shield','vaalorn',2,2000,'small',15,'small',0,'arm','A small vaalorn shield.',1),
('an iron target shield','iron target shield','shield','target shield','an','shield','iron',4,130,'medium',20,'medium',-5,'arm','An iron target shield.',1),
('a bronze target shield','bronze target shield','shield','target shield','a','shield','bronze',4,175,'medium',20,'medium',-5,'arm','A bronze target shield.',1),
('a mithril target shield','mithril target shield','shield','target shield','a','shield','mithril',4,800,'medium',20,'medium',-5,'arm','A mithril target shield.',1),
('a vultite target shield','vultite target shield','shield','target shield','a','shield','vultite',4,2000,'medium',20,'medium',-5,'arm','A vultite target shield.',1),
('a vaalorn target shield','vaalorn target shield','shield','target shield','a','shield','vaalorn',4,4000,'medium',20,'medium',-5,'arm','A vaalorn target shield.',1),
('an iron mantlet','iron mantlet','mantlet','mantlet','an','shield','iron',6,200,'medium',25,'medium',-10,'arm','An iron kite mantlet.',1),
('a steel mantlet','steel mantlet','mantlet','mantlet','a','shield','steel',6,350,'medium',25,'medium',-10,'arm','A steel kite mantlet.',1),
('a mithril mantlet','mithril mantlet','mantlet','mantlet','a','shield','mithril',6,1200,'medium',25,'medium',-10,'arm','A mithril mantlet.',1),
('a vultite mantlet','vultite mantlet','mantlet','mantlet','a','shield','vultite',6,3000,'medium',25,'medium',-10,'arm','A vultite mantlet.',1),
('a vaalorn mantlet','vaalorn mantlet','mantlet','mantlet','a','shield','vaalorn',6,6000,'medium',25,'medium',-10,'arm','A vaalorn mantlet.',1),
('an iron pavise','iron pavise','pavise','pavise','an','shield','iron',10,400,'large',30,'large',-20,'arm','A large iron pavise.',1),
('a steel pavise','steel pavise','pavise','pavise','a','shield','steel',10,700,'large',30,'large',-20,'arm','A large steel pavise.',1),
('a mithril pavise','mithril pavise','pavise','pavise','a','shield','mithril',10,2500,'large',30,'large',-20,'arm','A mithril pavise.',1),
('a vultite pavise','vultite pavise','pavise','pavise','a','shield','vultite',10,6500,'large',30,'large',-20,'arm','A vultite pavise.',1),
('a vaalorn pavise','vaalorn pavise','pavise','pavise','a','shield','vaalorn',10,12000,'large',30,'large',-20,'arm','A vaalorn pavise.',1);

-- ============================================================
-- SECTION 7: ARCHERY
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,weapon_category,damage_factor,weapon_speed,damage_type,attack_bonus,damage_bonus,enchant_bonus,material_bonus,description,is_template) VALUES
('a yew short bow','yew short bow','bow','short bow','a','weapon','yew',3,200,'ranged',0.325,4,'puncture',0,0,0,0,'A short bow of flexible yew.',1),
('an oak short bow','oak short bow','bow','short bow','an','weapon','oak',3,150,'ranged',0.300,4,'puncture',0,0,0,0,'A short bow of sturdy oak.',1),
('a yew long bow','yew long bow','bow','long bow','a','weapon','yew',4,350,'ranged',0.400,5,'puncture',0,0,0,0,'A yew long bow.',1),
('an oak long bow','oak long bow','bow','long bow','an','weapon','oak',4,280,'ranged',0.375,5,'puncture',0,0,0,0,'An oak long bow.',1),
('a yew composite bow','yew composite bow','bow','composite bow','a','weapon','yew',4,500,'ranged',0.450,5,'puncture',0,0,0,0,'A yew composite bow.',1),
('an oak composite bow','oak composite bow','bow','composite bow','an','weapon','oak',4,400,'ranged',0.425,5,'puncture',0,0,0,0,'An oak composite bow.',1),
('an iron light crossbow','iron light crossbow','crossbow','light crossbow','an','weapon','iron',5,150,'ranged',0.325,5,'puncture',0,0,0,0,'An iron light crossbow.',1),
('a steel light crossbow','steel light crossbow','crossbow','light crossbow','a','weapon','steel',5,250,'ranged',0.325,5,'puncture',0,0,0,0,'A steel light crossbow.',1),
('an iron heavy crossbow','iron heavy crossbow','crossbow','heavy crossbow','an','weapon','iron',8,250,'ranged',0.450,7,'puncture',0,0,0,0,'A heavy iron crossbow.',1),
('a steel heavy crossbow','steel heavy crossbow','crossbow','heavy crossbow','a','weapon','steel',8,400,'ranged',0.450,7,'puncture',0,0,0,0,'A heavy steel crossbow.',1);

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,is_stackable,description,is_template) VALUES
('a fletched hunting arrow','fletched hunting arrow','arrow','hunting arrow','a','ammo','wood',0.1,5,1,'A standard hunting arrow with fletching.',1),
('a bundle of war arrows','bundle of war arrows','arrows','war arrows','a','ammo','steel',1,100,0,'A bundle of war-grade steel-tipped arrows.',1),
('a steel-headed war bolt','steel-headed war bolt','bolt','war bolt','a','ammo','steel',0.2,15,1,'A heavy steel-headed crossbow bolt.',1);

-- ============================================================
-- SECTION 8: GEMS
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,gem_family,weight,value,description,is_template) VALUES
('a clear quartz','clear quartz','quartz','quartz','a','gem','quartz',0.1,25,'A perfectly clear quartz crystal.',1),
('a smoky quartz','smoky quartz','quartz','quartz','a','gem','quartz',0.1,50,'A translucent smoky grey quartz.',1),
('a rose quartz','rose quartz','quartz','quartz','a','gem','quartz',0.1,75,'A pale pink rose quartz.',1),
('a citrine quartz','citrine quartz','quartz','quartz','a','gem','quartz',0.1,100,'A golden-yellow citrine quartz.',1),
('a blue lace agate','blue lace agate','agate','agate','a','gem','agate',0.1,150,'A blue-and-white banded agate.',1),
('a green jade','green jade','jade','jade','a','gem','jade',0.2,200,'A smooth piece of polished green jade.',1),
('a turquoise stone','turquoise stone','stone','turquoise','a','gem','turquoise',0.1,175,'A bright turquoise stone.',1),
('an amethyst','amethyst','amethyst','amethyst','an','gem','amethyst',0.1,300,'A faceted violet amethyst.',1),
('a moonstone','moonstone','moonstone','moonstone','a','gem','moonstone',0.1,350,'A pale shimmering moonstone.',1),
('a pale blue moonstone','pale blue moonstone','moonstone','moonstone','a','gem','moonstone',0.1,450,'A pale blue moonstone with an inner glow.',1),
('a peridot','peridot','peridot','peridot','a','gem','peridot',0.1,250,'A bright olive-green peridot.',1),
('a red carbuncle','red carbuncle','carbuncle','carbuncle','a','gem','carbuncle',0.1,400,'A deep red carbuncle.',1),
('a dark red garnet','dark red garnet','garnet','garnet','a','gem','garnet',0.1,350,'A deep red garnet.',1),
('a fire opal','fire opal','opal','opal','a','gem','opal',0.1,600,'A fire opal with shifting inner colors.',1),
('a tigerfang crystal','tigerfang crystal','crystal','crystal','a','gem','crystal',0.1,500,'A yellowish crystal with black inclusions.',1),
('a shard of glaes','shard of glaes','shard','glaes','a','gem','glaes',0.1,800,'A sharp fragment of natural glaes.',1),
('a piece of golden amber','piece of golden amber','amber','amber','a','gem','amber',0.2,450,'A piece of translucent golden amber.',1),
('an aquamarine gem','aquamarine gem','gem','aquamarine','an','gem','aquamarine',0.1,500,'A pale blue-green aquamarine.',1),
('a blue sapphire','blue sapphire','sapphire','sapphire','a','gem','sapphire',0.1,1500,'A brilliant blue sapphire.',1),
('a star sapphire','star sapphire','sapphire','sapphire','a','gem','sapphire',0.1,3000,'A rare star sapphire.',1),
('an uncut ruby','uncut ruby','ruby','ruby','an','gem','ruby',0.1,800,'A raw uncut ruby.',1),
('an uncut emerald','uncut emerald','emerald','emerald','an','gem','emerald',0.1,750,'A raw uncut emerald.',1),
('an uncut diamond','uncut diamond','diamond','diamond','an','gem','diamond',0.1,2000,'A raw uncut diamond.',1),
('a gold bracelet','gold bracelet','bracelet','bracelet','a','gem','jewelry',0.3,500,'A simple gold bracelet.',1),
('a gold necklace','gold necklace','necklace','necklace','a','gem','jewelry',0.3,800,'A simple gold necklace.',1),
('a gold ring','gold ring','ring','ring','a','gem','jewelry',0.2,300,'A simple gold ring.',1),
('a silver ring','silver ring','ring','ring','a','gem','jewelry',0.2,150,'A simple silver ring.',1),
('a silver bracelet','silver bracelet','bracelet','bracelet','a','gem','jewelry',0.3,200,'A simple silver bracelet.',1),
('a prayer bead necklace','prayer bead necklace','necklace','necklace','a','gem','jewelry',0.3,250,'A string of prayer beads.',1),
('a crystal amulet','crystal amulet','amulet','amulet','a','gem','crystal',0.2,400,'A crystal amulet on a silver chain.',1);

-- ============================================================
-- SECTION 9: MAGIC ITEMS
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,description,is_template) VALUES
('a silver wand','silver wand','wand','wand','a','magic','silver',0.5,500,'A slender silver wand humming with stored energy.',1),
('a glowing glowbark wand','glowing glowbark wand','wand','glowbark wand','a','magic','glowbark',0.5,800,'A glowbark wand pulsing with inner light.',1),
('a glowing white runestone','glowing white runestone','runestone','runestone','a','magic','glaes',0.3,300,'A white runestone etched with glowing symbols.',1),
('a smooth grey runestone','smooth grey runestone','runestone','runestone','a','magic','glaes',0.3,150,'A smooth grey runestone.',1),
('a small crystal runestone','small crystal runestone','runestone','runestone','a','magic','crystal',0.2,200,'A small crystal runestone with faint inscriptions.',1),
('an arcane wizard scroll','arcane wizard scroll','scroll','scroll','an','magic','paper',0.1,500,'A scroll bearing arcane wizard spells.',1),
('a dark sorcerer scroll','dark sorcerer scroll','scroll','scroll','a','magic','paper',0.1,500,'A scroll bearing dark sorcerer spells.',1),
('a musical bard scroll','musical bard scroll','scroll','scroll','a','magic','paper',0.1,400,'A scroll bearing bardic spells.',1),
('a leaf-bound ranger scroll','leaf-bound ranger scroll','scroll','scroll','a','magic','paper',0.1,400,'A leaf-bound ranger scroll.',1),
('a radiant paladin scroll','radiant paladin scroll','scroll','scroll','a','magic','paper',0.1,450,'A scroll bearing paladin prayers.',1),
('a glowing empath scroll','glowing empath scroll','scroll','scroll','a','magic','paper',0.1,450,'A scroll bearing empath healing spells.',1),
('a blessed cleric scroll','blessed cleric scroll','scroll','scroll','a','magic','paper',0.1,450,'A scroll bearing cleric blessings.',1),
('a weathered major spirit scroll','weathered major spirit scroll','scroll','scroll','a','magic','paper',0.1,600,'An ancient scroll of major spirit spells.',1),
('a crinkled minor spirit scroll','crinkled minor spirit scroll','scroll','scroll','a','magic','paper',0.1,350,'A scroll of minor spirit spells.',1),
('a deed of Lorminstra','deed of Lorminstra','deed','deed','a','magic','paper',0.1,50000,'A deed bearing the seal of Lorminstra.  Prevents one death.',1),
('a glowing deed of Lorminstra','glowing deed of Lorminstra','deed','deed','a','magic','paper',0.1,100000,'A glowing deed of Lorminstra emanating divine protection.',1);

-- ============================================================
-- SECTION 10: FOOD & TAVERN
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,is_stackable,description,is_template) VALUES
('a piece of bread','piece of bread','bread','bread','a','food','food',0.2,5,1,'A plain piece of bread.',1),
('a biscuit','biscuit','biscuit','biscuit','a','food','food',0.1,3,1,'A small plain biscuit.',1),
('a honey roll','honey roll','roll','honey roll','a','food','food',0.2,8,1,'A sweet roll drizzled with honey.',1),
('a meat pie','meat pie','pie','meat pie','a','food','food',0.5,25,1,'A savory meat pie.',1),
('a roasted haunch','roasted haunch','haunch','haunch','a','food','food',1,35,1,'A roasted haunch of meat.',1),
('an apple','apple','apple','apple','an','food','food',0.3,4,1,'A fresh crisp apple.',1),
('a cheese wedge','cheese wedge','cheese','cheese','a','food','food',0.3,10,1,'A wedge of aged cheese.',1),
('a waterskin','waterskin','waterskin','waterskin','a','food','leather',0.5,20,0,'A leather waterskin.',1),
('a flask of water','flask of water','flask','flask','a','food','glass',0.3,10,1,'A glass flask of cool water.',1),
('a flask of elven brandy','flask of elven brandy','flask','flask','a','food','glass',0.5,150,1,'A flask of smooth elven brandy.',1),
('a flask of elven spirits','flask of elven spirits','flask','flask','a','food','glass',0.5,120,1,'A flask of potent elven spirits.',1),
('a bottle of wine','bottle of wine','bottle','bottle','a','food','glass',1,80,1,'A bottle of fine Elven wine.',1),
('a glass of Vaalor red wine','glass of Vaalor red wine','glass','glass','a','food','glass',0.5,40,1,'A glass of fine Vaalor red wine.',1),
('a mug of dwarven stout','mug of dwarven stout','mug','mug','a','food','ceramic',0.8,30,1,'A heavy mug of dark dwarven stout.',1),
('a tankard of elven ale','tankard of elven ale','tankard','tankard','a','food','ceramic',0.8,25,1,'A tankard of light elven ale.',1),
('a bowl of hearty stew','bowl of hearty stew','bowl','stew','a','food','ceramic',1,50,1,'A bowl of thick hearty stew.',1),
('a loaf of elven waybread','loaf of elven waybread','loaf','waybread','a','food','food',1,60,1,'A loaf of elven waybread.  Sustains a traveler for days.',1),
('a strip of dried venison','strip of dried venison','venison','venison','a','food','food',0.1,12,1,'A strip of dried salted venison.',1),
('a pouch of trail mix','pouch of trail mix','mix','trail mix','a','food','food',0.3,15,1,'A small pouch of nuts, berries, and dried fruit.',1),
('a bundle of travel rations','bundle of travel rations','rations','rations','a','food','food',2,50,0,'A bundle of basic travel rations.',1);

-- ============================================================
-- SECTION 11: FORGING SUPPLIES
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,description,is_template) VALUES
('a chunk of iron ore','chunk of iron ore','ore','iron ore','a','material','iron',5,10,'A raw chunk of iron ore.',1),
('a chunk of copper ore','chunk of copper ore','ore','copper ore','a','material','copper',5,15,'A raw chunk of copper ore.',1),
('a chunk of silver ore','chunk of silver ore','ore','silver ore','a','material','silver',5,100,'A chunk of raw silver ore.',1),
('a chunk of gold ore','chunk of gold ore','ore','gold ore','a','material','gold',5,200,'A chunk of raw gold ore.',1),
('a chunk of mithril ore','chunk of mithril ore','ore','mithril ore','a','material','mithril',5,500,'A chunk of precious mithril ore.',1),
('a chunk of faenor ore','chunk of faenor ore','ore','faenor ore','a','material','faenor',5,300,'A chunk of faenor ore.',1),
('a chunk of eahnor ore','chunk of eahnor ore','ore','eahnor ore','a','material','eahnor',5,400,'A chunk of eahnor ore.',1),
('a chunk of invar ore','chunk of invar ore','ore','invar ore','a','material','invar',5,350,'A chunk of invar ore.',1),
('a chunk of vultite ore','chunk of vultite ore','ore','vultite ore','a','material','vultite',5,1500,'A chunk of rare vultite ore.',1),
('a chunk of ora ore','chunk of ora ore','ore','ora ore','a','material','ora',5,800,'A chunk of ora ore.',1),
('a chunk of kelyn ore','chunk of kelyn ore','ore','kelyn ore','a','material','kelyn',5,1200,'A chunk of kelyn ore.',1),
('a chunk of laje ore','chunk of laje ore','ore','laje ore','a','material','laje',5,700,'A chunk of laje ore.',1),
('a chunk of rolaren ore','chunk of rolaren ore','ore','rolaren ore','a','material','rolaren',5,900,'A chunk of rolaren ore.',1),
('some redite ore','redite ore','ore','redite ore','some','material','redite',5,600,'Some raw redite ore.',1),
('a hammer','hammer','hammer','hammer','a','misc','steel',2,50,'A sturdy steel forging hammer.',1),
('a pair of tongs','pair of tongs','tongs','tongs','a','misc','steel',1.5,40,'Iron tongs for handling hot metal.',1),
('a pickaxe','pickaxe','pickaxe','pickaxe','a','misc','steel',5,80,'A sturdy steel pickaxe.',1),
('a shovel','shovel','shovel','shovel','a','misc','steel',4,60,'A steel-headed shovel.',1),
('a coil of rope','coil of rope','rope','rope','a','misc','hemp',2,20,'A coil of sturdy hemp rope.',1),
('a wooden torch','wooden torch','torch','torch','a','misc','wood',0.5,5,'A pitch-soaked wooden torch.',1),
('an oil lantern','oil lantern','lantern','lantern','an','misc','brass',1,75,'A brass oil lantern.',1),
('a fishing pole','fishing pole','pole','fishing pole','a','misc','wood',2,30,'A simple wooden fishing pole.',1),
('a grappling hook','grappling hook','hook','grappling hook','a','misc','steel',1.5,100,'A steel grappling hook.',1),
('a needle and thread','needle and thread','needle','needle','a','misc','steel',0.1,10,'A sewing needle and thread.',1),
('a pair of scissors','pair of scissors','scissors','scissors','a','misc','steel',0.3,15,'A pair of steel scissors.',1);

-- ============================================================
-- SECTION 12: CONTAINERS / GENERAL GOODS
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,container_capacity,worn_location,description,is_template) VALUES
('a canvas haversack','canvas haversack','haversack','haversack','a','container','canvas',1.5,150,20,'back','A sturdy canvas haversack.',1),
('a dark leather satchel','dark leather satchel','satchel','satchel','a','container','leather',1,200,15,'shoulder','A dark leather satchel.',1),
('a hunting pack','hunting pack','pack','hunting pack','a','container','leather',2,300,25,'back','A ranger hunting pack of treated leather.',1),
('a small leather pouch','small leather pouch','pouch','pouch','a','container','leather',0.3,15,5,'belt','A small leather belt pouch.',1),
('a wooden coffer','wooden coffer','coffer','coffer','a','container','wood',3,200,10,NULL,'A small wooden coffer with iron fittings.',1),
('a small wooden box','small wooden box','box','box','a','container','wood',1,50,5,NULL,'A simple small wooden box.',1),
('a small steel lockbox','small steel lockbox','lockbox','lockbox','a','container','steel',3,500,8,NULL,'A small steel lockbox.',1),
('a dented iron box','dented iron box','box','box','a','container','iron',4,100,6,NULL,'A dented iron box that has seen better days.',1),
('a silk coin purse','silk coin purse','purse','coin purse','a','container','silk',0.2,100,0,'belt','A small silk pouch for coins.',1),
('a weapon harness','weapon harness','harness','harness','a','container','leather',1.5,200,4,'back','A leather harness for carrying weapons.',1);

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,material,weight,value,description,is_template) VALUES
('an ivory comb','ivory comb','comb','comb','an','misc','ivory',0.2,75,'A small finely carved ivory comb.',1),
('an embroidered cloak','embroidered cloak','cloak','cloak','an','clothing','velvet',1.5,800,'A richly embroidered velvet cloak.',1),
('a set of bone dice','set of bone dice','dice','dice','a','misc','bone',0.2,25,'A set of carved bone dice.',1);

-- ============================================================
-- SECTION 13: MISSING HERBS
-- ============================================================

INSERT IGNORE INTO items (name,short_name,noun,base_name,article,item_type,heal_type,heal_rank,heal_amount,herb_heal_type,herb_heal_amount,herb_roundtime,weight,value,description,is_template) VALUES
('some cuctucae berry','cuctucae berry','berry','cuctucae berry','some','herb','health',2,10,'health',10,10,0.1,100,'Round tart cuctucae berries with healing properties.',1),
('some tkaro root','tkaro root','root','tkaro root','some','herb','health',3,15,'head',15,15,0.1,150,'A twisted tkaro root for head injuries.',1),
('some wekaf berries','wekaf berries','berries','wekaf berries','some','herb','health',2,10,'chest',10,10,0.1,100,'Small dark wekaf berries for chest wounds.',1);

-- ============================================================
-- SECTION 14: CLEAR SHOP INVENTORY
-- ============================================================

DELETE FROM shop_inventory WHERE shop_id BETWEEN 1 AND 18;

-- ============================================================
-- SECTION 15: SHIND'S LOCKSMITH - correct GS4 inventory
-- The existing shops seed uses old fake pick names; override here.
-- stock -1 = unlimited
-- ============================================================

INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,0,3600 FROM items WHERE name='a copper lockpick'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,0,3600 FROM items WHERE name='a brass lockpick'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,0,3600 FROM items WHERE name='a steel lockpick'   AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,0,3600 FROM items WHERE name='an ivory lockpick'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,0,3600 FROM items WHERE name='a gold lockpick'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,0,3600 FROM items WHERE name='a silver lockpick'  AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,5,5,86400  FROM items WHERE name='a mithril lockpick' AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,3,3,86400  FROM items WHERE name='an ora lockpick'    AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,0,3600 FROM items WHERE name='a lockpick case'     AND is_template=1 LIMIT 1;
INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval) SELECT 7,id,-1,0,3600 FROM items WHERE name='a key ring'          AND is_template=1 LIMIT 1;

-- ============================================================
-- VERIFICATION
-- ============================================================

SELECT 'fix_items_master.sql complete.' AS status;
SELECT
    (SELECT COUNT(*) FROM items WHERE is_template=1)                         AS total_templates,
    (SELECT COUNT(*) FROM items WHERE item_type='misc' AND noun='lockpick')  AS good_lockpick_rows,
    (SELECT COUNT(*) FROM items WHERE item_type='lockpick')                  AS bad_lockpick_rows,
    (SELECT COUNT(*) FROM shop_inventory)                                    AS shop_inventory_rows;
