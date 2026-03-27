-- ============================================================
-- Ta'Vaalor Shop Seeding Script
-- Uses real GS4 / Lich room IDs throughout.
-- Item inventory uses name-based SELECT to avoid hardcoding IDs.
-- ============================================================
USE gemstone_dev;

DELETE FROM shop_inventory;
DELETE FROM shops;
ALTER TABLE shops AUTO_INCREMENT = 1;

INSERT INTO shops (id, name, room_id, shop_type, buy_multiplier, sell_multiplier) VALUES
(1,  'The Ta''Vaalor Weaponry',         10367, 'weapon',  1.00, 0.50),
(2,  'The Ta''Vaalor Armory',           12350, 'armor',   1.00, 0.50),
(3,  'Sylindra''s Leathers',            10329, 'armor',   1.00, 0.50),
(4,  'Phisk''s Sundry Wares',           12348, 'general', 1.00, 0.40),
(5,  'Saphrie''s Herbs and Tinctures',  10396, 'herb',    1.00, 0.30),
(6,  'Ta''Vaalor Antique Goods',        10379, 'general', 0.80, 0.50),
(7,  'Shind''s Lockpicks',              10434, 'general', 1.00, 0.40),
(8,  'Elantaran''s Magic Supply',       10364, 'magic',   1.20, 0.40),
(9,  'Areacne''s Gems',                 10327, 'gem',     1.00, 0.60),
(10, 'Men''s Clothier',                 17292, 'other',   1.00, 0.30),
(11, 'Helgreth''s Tavern',              10424, 'food',    1.00, 0.10),
(12, 'Clentaran''s Clerical Supply',    10372, 'magic',   1.00, 0.40),
(13, 'Vonder''s Archery Supply',        10362, 'weapon',  1.00, 0.50),
(14, 'Annatto Rations Shop',            10368, 'food',    1.00, 0.20),
(15, 'Ambra''s Musicalities',           10395, 'other',   1.00, 0.30),
(16, 'Women''s Clothier',               17293, 'other',   1.00, 0.30),
(17, 'Sweethen''s Bakeshop',            12349, 'food',    1.00, 0.20),
(18, 'Ta''Vaalor Forging Supply',       10394, 'general', 1.00, 0.40);

DROP PROCEDURE IF EXISTS stock;
DELIMITER //
CREATE PROCEDURE stock(IN sid INT, IN iname VARCHAR(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci, IN qty SMALLINT, IN rtime INT)
BEGIN
    DECLARE v INT DEFAULT NULL;
    SELECT id INTO v FROM items WHERE name = iname AND is_template = 1 LIMIT 1;
    IF v IS NOT NULL THEN
        INSERT IGNORE INTO shop_inventory (shop_id,item_id,stock,restock_amount,restock_interval)
        VALUES (sid, v, qty, qty, rtime);
    END IF;
END //
DELIMITER ;

-- ================================================================
-- SHOP 1: TA'VAALOR WEAPONRY (Aerhseth)
-- ================================================================
CALL stock(1,'a steel dagger',-1,3600);CALL stock(1,'a steel main gauche',-1,3600);
CALL stock(1,'a steel poignard',-1,3600);CALL stock(1,'a steel rapier',-1,3600);
CALL stock(1,'a steel short sword',-1,3600);CALL stock(1,'a steel scimitar',-1,3600);
CALL stock(1,'a steel longsword',-1,3600);CALL stock(1,'a steel broadsword',-1,3600);
CALL stock(1,'a steel backsword',-1,3600);CALL stock(1,'a steel bastard sword',-1,3600);
CALL stock(1,'a steel falchion',-1,3600);CALL stock(1,'a steel katana',5,7200);
CALL stock(1,'a steel estoc',-1,3600);CALL stock(1,'a steel handaxe',-1,3600);
CALL stock(1,'a steel double-bit axe',-1,3600);CALL stock(1,'a steel whip-blade',5,7200);
CALL stock(1,'a steel mace',-1,3600);CALL stock(1,'a steel war hammer',-1,3600);
CALL stock(1,'a steel flail',-1,3600);CALL stock(1,'a steel morning star',-1,3600);
CALL stock(1,'a steel ball and chain',5,7200);CALL stock(1,'a steel cudgel',-1,3600);
CALL stock(1,'a steel spear',-1,3600);CALL stock(1,'a steel halberd',5,7200);
CALL stock(1,'a steel claymore',5,7200);CALL stock(1,'a steel greatsword',5,7200);
CALL stock(1,'a steel battle axe',5,7200);CALL stock(1,'a steel maul',5,7200);
CALL stock(1,'a vaalorn dagger',3,14400);CALL stock(1,'a vaalorn longsword',3,14400);
CALL stock(1,'a vaalorn broadsword',3,14400);CALL stock(1,'a vaalorn short sword',3,14400);
CALL stock(1,'a mithril dagger',3,14400);CALL stock(1,'a mithril longsword',3,14400);

-- ================================================================
-- SHOP 2: TA'VAALOR ARMORY (Gearchel)
-- ================================================================
CALL stock(2,'some steel light leather armor',-1,3600);
CALL stock(2,'some steel full leather armor',-1,3600);
CALL stock(2,'some steel reinforced leather',-1,3600);
CALL stock(2,'some steel double leather',-1,3600);
CALL stock(2,'some steel leather breastplate',-1,3600);
CALL stock(2,'some steel studded leather',-1,3600);
CALL stock(2,'a steel brigandine armor',-1,3600);
CALL stock(2,'a steel chain mail',-1,3600);
CALL stock(2,'a steel double chain mail',-1,3600);
CALL stock(2,'some steel augmented chain',5,7200);
CALL stock(2,'a steel chain hauberk',5,7200);
CALL stock(2,'a steel metal breastplate',5,7200);
CALL stock(2,'some steel half plate',3,14400);
CALL stock(2,'some steel full plate',2,28800);
CALL stock(2,'a steel buckler',-1,3600);
CALL stock(2,'a steel target shield',-1,3600);
CALL stock(2,'a steel small shield',-1,3600);
CALL stock(2,'a steel medium shield',-1,3600);
CALL stock(2,'a steel heater shield',-1,3600);
CALL stock(2,"a steel knight's shield",5,7200);
CALL stock(2,'a steel kite shield',5,7200);
CALL stock(2,'a steel large shield',3,14400);
CALL stock(2,'a vaalorn chain mail',3,14400);
CALL stock(2,'a vaalorn metal breastplate',3,14400);
CALL stock(2,'a mithril chain mail',3,14400);

-- ================================================================
-- SHOP 3: SYLINDRA'S LEATHERS
-- ================================================================
CALL stock(3,'some leather light leather armor',-1,3600);
CALL stock(3,'some leather full leather armor',-1,3600);
CALL stock(3,'some leather reinforced leather',-1,3600);
CALL stock(3,'some leather double leather',-1,3600);
CALL stock(3,'some dark leather full leather armor',-1,3600);
CALL stock(3,'some dark leather leather breastplate',-1,3600);
CALL stock(3,'some reinforced leather studded leather',-1,7200);
CALL stock(3,'a leather medium shield',-1,3600);
CALL stock(3,'a leather large shield',-1,3600);
CALL stock(3,'a small leather pouch',-1,3600);
CALL stock(3,'a leather backpack',-1,3600);
CALL stock(3,'a large sack',-1,3600);
CALL stock(3,'a belt pouch',-1,3600);
CALL stock(3,'a gem pouch',-1,3600);
CALL stock(3,'an herb pouch',-1,3600);
CALL stock(3,"an adventurer's cloak",-1,3600);
CALL stock(3,"a traveler's pack",5,7200);
CALL stock(3,'a hunting pack',5,7200);
CALL stock(3,'a dark leather satchel',-1,3600);
CALL stock(3,'a canvas haversack',-1,3600);
CALL stock(3,'a silk coin purse',-1,3600);

-- ================================================================
-- SHOP 4: PHISK'S SUNDRY WARES
-- ================================================================
CALL stock(4,'a wooden torch',-1,1800);CALL stock(4,'an oil lantern',-1,3600);
CALL stock(4,'a coil of rope',-1,3600);CALL stock(4,'a grappling hook',-1,3600);
CALL stock(4,'a small leather pouch',-1,3600);CALL stock(4,'a belt pouch',-1,3600);
CALL stock(4,'a small wooden box',-1,3600);CALL stock(4,'a fishing pole',5,7200);
CALL stock(4,'a shovel',5,7200);CALL stock(4,'a pickaxe',5,7200);
CALL stock(4,'a waterskin',-1,1800);CALL stock(4,'a bundle of travel rations',-1,1800);
CALL stock(4,'a glowing glowbark wand',5,7200);
CALL stock(4,'a bundle of arrows',-1,3600);CALL stock(4,'a bundle of crossbow bolts',-1,3600);
CALL stock(4,'a silk coin purse',-1,3600);CALL stock(4,'a needle and thread',-1,3600);
CALL stock(4,'a pair of scissors',-1,3600);

-- ================================================================
-- SHOP 5: SAPHRIE'S HERBS
-- ================================================================
CALL stock(5,'a sprig of acantha leaf',-1,1800);
CALL stock(5,'a stem of ambrominas leaf',-1,1800);
CALL stock(5,'a sprig of cactacae spine',-1,1800);
CALL stock(5,'some wolifrew lichen',-1,1800);
CALL stock(5,'a sprig of torban leaf',-1,1800);
CALL stock(5,'some pothinir grass',-1,1800);
CALL stock(5,'some brostheras potion',-1,1800);
CALL stock(5,'some woth flower',-1,1800);
CALL stock(5,'some ephlox moss',-1,1800);
CALL stock(5,'some haphip root',-1,1800);
CALL stock(5,'a sprig of aloeas stem',-1,1800);
CALL stock(5,'some basal moss',-1,1800);
CALL stock(5,'some rose-marrow potion',5,3600);
CALL stock(5,'some sovyn clove',5,3600);
CALL stock(5,'some wingstem potion',5,3600);
CALL stock(5,'some bolmara potion',3,7200);
CALL stock(5,'some redite ore',5,3600);
CALL stock(5,"some troll's blood potion",3,7200);
CALL stock(5,'some calamia fruit',-1,1800);
CALL stock(5,'some tkaro root',-1,1800);
CALL stock(5,'some yabathilium fruit',3,7200);
CALL stock(5,'some cuctucae berry',-1,1800);
CALL stock(5,'some wekaf berries',-1,1800);
CALL stock(5,'an herb pouch',-1,3600);

-- ================================================================
-- SHOP 6: ANTIQUE GOODS / PAWNSHOP (Dakris)
-- ================================================================
CALL stock(6,'a steel dagger',3,7200);CALL stock(6,'a steel short sword',3,7200);
CALL stock(6,'a steel mace',3,7200);CALL stock(6,'some padded armor',3,7200);
CALL stock(6,'a small wooden box',-1,3600);CALL stock(6,'a wooden coffer',3,7200);
CALL stock(6,'a dented iron box',3,7200);CALL stock(6,'a small leather pouch',-1,3600);
CALL stock(6,'a crystal amulet',3,7200);CALL stock(6,'a silver ring',5,7200);
CALL stock(6,'a gold ring',3,14400);CALL stock(6,'a set of bone dice',-1,3600);
CALL stock(6,'a prayer bead necklace',-1,3600);

-- ================================================================
-- SHOP 7: SHIND'S LOCKPICKS
-- ================================================================
CALL stock(7,'a crude lockpick',-1,1800);CALL stock(7,'a simple lockpick',-1,1800);
CALL stock(7,'a standard lockpick',-1,3600);CALL stock(7,'a professional lockpick',-1,3600);
CALL stock(7,"a master's lockpick",5,7200);CALL stock(7,'a copper lockpick',-1,1800);
CALL stock(7,'a bronze lockpick',-1,3600);CALL stock(7,'a steel lockpick',-1,3600);
CALL stock(7,'a mithril lockpick',5,7200);CALL stock(7,'a vultite lockpick',3,14400);
CALL stock(7,'an alum lockpick',5,7200);CALL stock(7,'an invar lockpick',5,7200);
CALL stock(7,'a kelyn lockpick',3,14400);CALL stock(7,'a laje lockpick',3,14400);
CALL stock(7,'an ora lockpick',3,14400);CALL stock(7,'a glaes lockpick',2,28800);
CALL stock(7,'a rolaren lockpick',2,28800);CALL stock(7,'a veniom lockpick',1,86400);

-- ================================================================
-- SHOP 8: ELANTARAN'S MAGIC SUPPLY
-- ================================================================
CALL stock(8,'a crinkled minor spirit scroll',-1,3600);
CALL stock(8,'a weathered major spirit scroll',-1,3600);
CALL stock(8,'an arcane wizard scroll',-1,3600);
CALL stock(8,'a dark sorcerer scroll',-1,3600);
CALL stock(8,'a blessed cleric scroll',-1,3600);
CALL stock(8,'a glowing empath scroll',-1,3600);
CALL stock(8,'a leaf-bound ranger scroll',-1,3600);
CALL stock(8,'a musical bard scroll',-1,3600);
CALL stock(8,'a radiant paladin scroll',-1,3600);
CALL stock(8,'a small crystal runestone',-1,1800);
CALL stock(8,'a smooth grey runestone',5,7200);
CALL stock(8,'a glowing white runestone',3,14400);
CALL stock(8,'a silver wand',3,14400);
CALL stock(8,'an oak runestaff',-1,3600);CALL stock(8,'a yew runestaff',-1,3600);
CALL stock(8,'a hawthorn runestaff',-1,3600);CALL stock(8,'a haon runestaff',5,7200);
CALL stock(8,'an ironwood runestaff',5,7200);CALL stock(8,'a carmiln runestaff',3,14400);
CALL stock(8,'a kakore runestaff',2,28800);CALL stock(8,'a glowing glowbark wand',5,7200);

-- ================================================================
-- SHOP 9: AREACNE'S GEMS (Tmareantha)
-- ================================================================
CALL stock(9,'a piece of blue ridge coral',-1,3600);CALL stock(9,'a blood marble',-1,3600);
CALL stock(9,'a tigerfang crystal',-1,3600);CALL stock(9,'a turquoise stone',-1,3600);
CALL stock(9,'a smoky topaz',-1,3600);CALL stock(9,'a small golden topaz',5,7200);
CALL stock(9,'an aquamarine gem',5,7200);CALL stock(9,'a green beryl stone',-1,3600);
CALL stock(9,'a golden beryl gem',5,7200);CALL stock(9,'a clear quartz',-1,3600);
CALL stock(9,'a rose quartz',-1,3600);CALL stock(9,'an amethyst',-1,3600);
CALL stock(9,'a dark red garnet',5,3600);CALL stock(9,'a red spinel',3,7200);
CALL stock(9,'a ruby',2,14400);CALL stock(9,'a fire opal',3,7200);
CALL stock(9,'an emerald',2,14400);CALL stock(9,'a green jade',5,7200);
CALL stock(9,'a blue sapphire',2,14400);CALL stock(9,'a violet sapphire',2,14400);
CALL stock(9,'an uncut diamond',1,28800);CALL stock(9,'a white opal',3,7200);
CALL stock(9,'a small white pearl',-1,3600);CALL stock(9,'a large white pearl',5,7200);
CALL stock(9,'a black pearl',2,14400);CALL stock(9,'a gold ring',-1,3600);
CALL stock(9,'a silver ring',-1,3600);CALL stock(9,'a gold necklace',5,7200);
CALL stock(9,'a silver bracelet',-1,3600);CALL stock(9,'a crystal amulet',5,7200);
CALL stock(9,'a gem pouch',-1,3600);

-- ================================================================
-- SHOP 10: MEN'S CLOTHIER (Vendara)
-- ================================================================
CALL stock(10,'a black silk cloak',3,7200);CALL stock(10,'a crimson silk cloak',3,7200);
CALL stock(10,'a black velvet doublet',5,3600);CALL stock(10,'a crimson velvet doublet',5,3600);
CALL stock(10,'a black linen tunic',-1,3600);CALL stock(10,'a grey wool tunic',-1,3600);
CALL stock(10,'a black linen breeches',-1,3600);CALL stock(10,'a black leather boots',-1,3600);
CALL stock(10,'a black leather gloves',-1,3600);CALL stock(10,'a black silk shirt',5,3600);
CALL stock(10,'a grey linen hat',-1,3600);CALL stock(10,'a crimson silk sash',5,3600);
CALL stock(10,'a black leather belt',-1,3600);CALL stock(10,'a dark leather satchel',-1,3600);
CALL stock(10,'a gold velvet doublet',3,7200);CALL stock(10,'a white linen tunic',-1,3600);
CALL stock(10,'a purple velvet vest',3,7200);

-- ================================================================
-- SHOP 11: HELGRETH'S TAVERN
-- ================================================================
CALL stock(11,'a tankard of elven ale',-1,300);
CALL stock(11,'a glass of Vaalor red wine',-1,300);
CALL stock(11,'a mug of dwarven stout',-1,300);
CALL stock(11,'a flask of elven brandy',5,1800);
CALL stock(11,'a bowl of hearty stew',-1,300);
CALL stock(11,'a meat pie',-1,600);
CALL stock(11,'a roasted haunch',5,1800);
CALL stock(11,'a cheese wedge',-1,600);
CALL stock(11,'a honey roll',-1,600);
CALL stock(11,'a piece of bread',-1,300);

-- ================================================================
-- SHOP 12: CLENTARAN'S CLERICAL SUPPLY
-- ================================================================
CALL stock(12,'a deed of Lorminstra',5,7200);
CALL stock(12,'a glowing deed of Lorminstra',2,14400);
CALL stock(12,'a crystal amulet',-1,3600);
CALL stock(12,'a prayer bead necklace',-1,3600);
CALL stock(12,'a blessed cleric scroll',-1,3600);
CALL stock(12,'a glowing empath scroll',-1,3600);
CALL stock(12,'a radiant paladin scroll',-1,3600);
CALL stock(12,'a small crystal runestone',-1,1800);
CALL stock(12,'a wooden torch',-1,1800);
CALL stock(12,'some wolifrew lichen',-1,1800);
CALL stock(12,'a sprig of acantha leaf',-1,1800);

-- ================================================================
-- SHOP 13: VONDER'S ARCHERY SUPPLY
-- ================================================================
CALL stock(13,'an oak short bow',-1,3600);CALL stock(13,'an oak long bow',-1,3600);
CALL stock(13,'a yew long bow',-1,3600);CALL stock(13,'a hawthorn short bow',-1,3600);
CALL stock(13,'an oak composite bow',5,7200);CALL stock(13,'a haon long bow',5,7200);
CALL stock(13,'an oak hand crossbow',-1,3600);CALL stock(13,'a steel light crossbow',-1,3600);
CALL stock(13,'a steel heavy crossbow',5,7200);
CALL stock(13,'a steel throwing dagger',-1,3600);CALL stock(13,'a steel throwing axe',-1,3600);
CALL stock(13,'a steel dart',-1,3600);CALL stock(13,'a steel shuriken',-1,3600);
CALL stock(13,'a steel discus',-1,3600);
CALL stock(13,'a bundle of arrows',-1,1800);CALL stock(13,'a bundle of war arrows',-1,1800);
CALL stock(13,'a bundle of crossbow bolts',-1,1800);

-- ================================================================
-- SHOP 14: ANNATTO RATIONS SHOP
-- ================================================================
CALL stock(14,'a bundle of travel rations',-1,1800);
CALL stock(14,'a loaf of elven waybread',-1,1800);
CALL stock(14,'a strip of dried venison',-1,1800);
CALL stock(14,'a pouch of trail mix',-1,1800);
CALL stock(14,'a waterskin',-1,1800);CALL stock(14,'a flask of water',-1,900);
CALL stock(14,'a piece of bread',-1,900);CALL stock(14,'a biscuit',-1,900);
CALL stock(14,'a cheese wedge',-1,900);CALL stock(14,'an apple',-1,900);

-- ================================================================
-- SHOP 15: AMBRA'S MUSICALITIES
-- ================================================================
CALL stock(15,'a musical bard scroll',-1,3600);
CALL stock(15,'an oak runestaff',-1,3600);
CALL stock(15,'a small crystal runestone',-1,1800);
CALL stock(15,'a crimson silk cloak',3,7200);
CALL stock(15,'a gold velvet doublet',3,7200);
CALL stock(15,'a purple velvet vest',3,7200);

-- ================================================================
-- SHOP 16: WOMEN'S CLOTHIER
-- ================================================================
CALL stock(16,'a black silk gown',3,7200);CALL stock(16,'a crimson silk gown',3,7200);
CALL stock(16,'a white silk gown',3,7200);CALL stock(16,'a purple velvet bodice',5,3600);
CALL stock(16,'a crimson velvet bodice',5,3600);
CALL stock(16,'a forest green linen skirt',-1,3600);CALL stock(16,'a black silk skirt',5,3600);
CALL stock(16,'a white satin slippers',-1,3600);CALL stock(16,'a black leather boots',-1,3600);
CALL stock(16,'a grey silk shawl',-1,3600);CALL stock(16,'a silver silk shawl',5,7200);
CALL stock(16,'a black velvet cloak',3,7200);CALL stock(16,'a white linen scarf',-1,3600);
CALL stock(16,'a dark leather satchel',-1,3600);CALL stock(16,'an ivory silk gown',2,14400);

-- ================================================================
-- SHOP 17: SWEETHEN'S BAKESHOP
-- ================================================================
CALL stock(17,'a honey roll',-1,600);CALL stock(17,'a meat pie',-1,600);
CALL stock(17,'a piece of bread',-1,300);CALL stock(17,'a biscuit',-1,300);
CALL stock(17,'a cheese wedge',-1,900);CALL stock(17,'an apple',-1,600);
CALL stock(17,'a bundle of travel rations',-1,1800);
CALL stock(17,'a loaf of elven waybread',-1,1800);

-- ================================================================
-- SHOP 18: TA'VAALOR FORGING SUPPLY (Tarneth)
-- ================================================================
CALL stock(18,'a chunk of iron ore',-1,3600);CALL stock(18,'a chunk of copper ore',-1,3600);
CALL stock(18,'a chunk of silver ore',-1,3600);CALL stock(18,'a chunk of gold ore',5,7200);
CALL stock(18,'a chunk of mithril ore',3,14400);CALL stock(18,'a chunk of vultite ore',2,28800);
CALL stock(18,'a chunk of ora ore',3,14400);CALL stock(18,'a chunk of imflass ore',3,14400);
CALL stock(18,'a chunk of invar ore',3,14400);CALL stock(18,'a chunk of kelyn ore',2,28800);
CALL stock(18,'a shard of glaes',2,28800);
CALL stock(18,'a hammer',-1,3600);CALL stock(18,'a pair of tongs',-1,3600);
CALL stock(18,'a shovel',5,7200);CALL stock(18,'a pickaxe',5,7200);

DROP PROCEDURE IF EXISTS stock;

SELECT s.name, COUNT(si.id) as items
FROM shops s LEFT JOIN shop_inventory si ON s.id = si.shop_id
GROUP BY s.id, s.name ORDER BY s.id;
SELECT CONCAT('Total inventory entries: ', COUNT(*)) FROM shop_inventory;
