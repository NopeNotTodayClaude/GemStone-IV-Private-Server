USE gemstone_dev;

DROP TEMPORARY TABLE IF EXISTS shop_copy_map;
CREATE TEMPORARY TABLE shop_copy_map (
    dest_shop_id   INT NOT NULL,
    shop_name      VARCHAR(255) NOT NULL,
    room_id        INT NOT NULL,
    source_shop_id INT NOT NULL,
    PRIMARY KEY (dest_shop_id)
) ENGINE=Memory;

INSERT INTO shop_copy_map (dest_shop_id, shop_name, room_id, source_shop_id) VALUES
(300, 'General Store', 8664, 4),
(301, 'Cecelia''s Weaponry', 15249, 1),
(302, 'Aznell''s Armory', 401, 2),
(303, 'Dakris''s Furs', 405, 3),
(304, 'Locksmith', 4610, 7),
(305, 'Xanith''s Magic Shoppe', 15022, 8),
(306, 'Helga''s Tavern', 3809, 11),
(307, 'Quaeta''s Fletcher Shop', 8719, 13),
(308, 'Dari''s Clothiers', 8720, 10),
(309, 'Public Workshops Supply Stall', 8618, 18),
(310, 'Lute''s Liltings Music Shoppe', 8660, 15),
(311, 'Krythussa''s Confectionary Shop', 386, 17),
(320, 'Aegenis General Store', 4009, 4),
(321, 'Ta''Illistim Weaponry', 602, 1),
(322, 'Ta''Illistim Armory', 4012, 2),
(323, 'Gaedrein''s Furs and Pelts', 4019, 3),
(324, 'Valina''s Herbs and Tinctures', 640, 5),
(325, 'Ta''Illistim Locksmith', 4024, 7),
(326, 'Dralen''s Magic Shoppe', 13043, 8),
(327, 'Shimmarglin Jewels and Gems', 686, 9),
(328, 'Brother Aemis'' Clerical Supply', 13297, 12),
(329, 'The Feystone Inn', 15608, 11),
(330, 'Sylvarraend Clothiers', 10076, 10),
(331, 'Ta''Illistim Forging Supply Shop', 13270, 18),
(332, 'Elysiana''s Outfitting', 5036, 16),
(333, 'Journey''s End, Supply Depot', 27839, 14),
(340, 'Cigar''s General Store', 13543, 4),
(341, 'Krinchat''s Weaponry', 15857, 1),
(342, 'Fasthr''s Lance, Armory', 13195, 2),
(343, 'E and S''s Fine Furs', 13521, 3),
(344, 'Sargassa''s', 5722, 5),
(345, 'Requiell''s Magic Shoppe', 13593, 8),
(346, 'Kahlyr''s Precious Gems', 5719, 9),
(347, 'The Tentacled Tavern', 5717, 11),
(348, 'Galnuir''s Archery', 12818, 13),
(349, 'Midrian''s Dyes', 13476, 248),
(350, 'Market Bridge Bakery', 12808, 17),
(351, 'Savina''s Outfitting', 13742, 16),
(360, 'Berrytoe''s General Store', 2424, 4),
(361, 'Kontii''s Weaponry', 15640, 1),
(362, 'Haldrick''s Armory', 3455, 2),
(363, 'Blackfinger''s Locks', 2425, 7),
(364, 'Wondrous Wizardly Wares', 17696, 8),
(365, 'Xenophon''s Fletcher Shop', 3451, 13),
(366, 'Our Colorful Place', 3820, 248),
(367, 'Brother Stumbleskink''s Emporium', 2328, 6),
(368, 'Icemule Forging Supply Shop', 9007, 18),
(369, 'Bellaja''s Outfitting', 15623, 16),
(352, 'Icemule Hall, Supply Emporium', 26823, 14),
(380, 'General Store', 10916, 4),
(381, 'Ouna''s Weaponry', 33583, 1),
(382, 'Hortinger''s Armory', 10937, 2),
(383, 'Felinium''s Fur Emporium', 10934, 3),
(384, 'Town Gardens', 10858, 5),
(385, 'Galena''s Lockworks', 10943, 7),
(386, 'Lomara''s Supernatural Supplies', 11002, 8),
(387, 'Diamante''s Gemshop', 10935, 9),
(388, 'Targon''s Tavern', 10951, 11),
(389, 'Relegan''s Fletcher Shop', 10990, 13),
(390, 'Lomara''s, Used Emporium', 11004, 6),
(391, 'River''s Rest Forging Supply', 11015, 18),
(392, 'The Mist and Shore Bakery', 32583, 17),
(393, 'Kaldonis''s Outfitting', 24470, 16),
(394, 'Trident''s Voyage, Cafe', 32582, 14),
(400, 'Haegan''s Weaponry', 4668, 1),
(401, 'Morvaeyn''s Armory', 9684, 2),
(402, 'Maeve''s Furs', 9687, 3),
(403, 'Gaertira''s Herbs', 4647, 5),
(404, 'Hihaeim''s Locksmithery', 4663, 7),
(405, 'Gems of the Earth', 4655, 9),
(406, 'Naerine Hostelry', 4688, 11),
(407, 'Ariebaela''s Archery Nook', 17152, 13),
(408, 'Fluttering Myriad', 4675, 248),
(420, 'Zul Logoth General Store', 9493, 4),
(421, 'Brutarius Kodel Weaponry', 9480, 1),
(422, 'Gust''s Armory', 9474, 2),
(423, 'Dagresar''s Furs', 9471, 3),
(424, 'Virilneus'' Magic Shoppe', 16894, 8),
(425, 'Praeteria''s Gems and Jewels', 9475, 9),
(426, 'Bawdy Bard Inn', 16849, 11),
(427, 'The Waggler''s, Used Emporium', 9565, 6),
(428, 'Zul Logoth Forging Supply Shop', 9422, 18),
(440, 'Juergen''s General Store', 14740, 4),
(441, 'Erantok''s Emporium', 14735, 6),
(442, 'Teras Isle Forging Supply Shop', 1954, 18),
(443, 'Raggler''s Snack Pantry', 14756, 14)
;

INSERT INTO shops (id, name, room_id, shop_type, buy_multiplier, sell_multiplier, is_active)
SELECT m.dest_shop_id,
       m.shop_name,
       m.room_id,
       s.shop_type,
       s.buy_multiplier,
       s.sell_multiplier,
       1
FROM shop_copy_map m
JOIN shops s ON s.id = m.source_shop_id
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    room_id = VALUES(room_id),
    shop_type = VALUES(shop_type),
    buy_multiplier = VALUES(buy_multiplier),
    sell_multiplier = VALUES(sell_multiplier),
    is_active = VALUES(is_active);

DELETE FROM shop_inventory WHERE shop_id IN (300,301,302,303,304,305,306,307,308,309,310,311,320,321,322,323,324,325,326,327,328,329,330,331,332,333,340,341,342,343,344,345,346,347,348,349,350,351,352,360,361,362,363,364,365,366,367,368,369,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,400,401,402,403,404,405,406,407,408,420,421,422,423,424,425,426,427,428,440,441,442,443);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval, last_restock)
SELECT m.dest_shop_id,
       si.item_id,
       si.stock,
       si.restock_amount,
       si.restock_interval,
       si.last_restock
FROM shop_copy_map m
JOIN shop_inventory si ON si.shop_id = m.source_shop_id;

DROP TEMPORARY TABLE IF EXISTS shop_copy_map;
