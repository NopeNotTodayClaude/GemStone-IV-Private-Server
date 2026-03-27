-- ============================================================
-- Migration: populate_L2_L4_guessed_and_L6_L10.sql
-- Covers:
--   GUESSED (no wiki stats): coconut crab L2, cave nipper L3,
--     spotted velnalin L3, black urgh L4
--   WIKI-SOURCED: leaper x2 L6, lesser mummy L6, monkey L6,
--     snowy cockatrice L6, spectral fisherman L6,
--     blood eagle L7, greater kappa L7, hobgoblin acolyte L7,
--     hobgoblin shaman L7, lesser burrow orc L7,
--     shelfae guard L7 (guessed), shelfae soldier L7,
--     albino tomb spider L8, crystal crab L8,
--     greater burrow orc L8, mottled thrak L8 (guessed),
--     brown spinner L9, crocodile L9, snow spectre L9,
--     cave worm L10, crazed canine L10,
--     gnoll miner L10, rabid guard dog L10
--
-- Also updates zone level ranges for new zone folders.
-- Run after all prior migrations.
-- ============================================================

USE gemstone_dev;

-- ── ZONE LEVEL RANGE UPDATES ──────────────────────────────────────────
UPDATE `zones` SET level_min=6,  level_max=10 WHERE id=202;  -- muddy_village
UPDATE `zones` SET level_min=7,  level_max=12 WHERE id=204;  -- cliffwalk
UPDATE `zones` SET level_min=7,  level_max=12 WHERE id=75;   -- melgorehn_s_valley
UPDATE `zones` SET level_min=8,  level_max=14 WHERE id=103;  -- the_krag_slopes

-- ── LOOT TABLES ───────────────────────────────────────────────────────
-- Only creatures dropping boxes get a table.
-- L2: coconut crab — no | L3: cave nipper — no | spotted velnalin — no
-- L4: black urgh — no
-- L6: lesser mummy yes, monkey yes, spectral fisherman yes
-- L7: greater kappa yes, hobgoblin acolyte yes, hobgoblin shaman yes,
--     lesser burrow orc yes, shelfae guard yes, shelfae soldier yes
-- L8: greater burrow orc yes | L9: snow spectre yes | L10: gnoll miner yes
INSERT IGNORE INTO `loot_tables` (`id`,`name`) VALUES
    (421,'Lesser mummy drops'),
    (422,'Monkey drops'),
    (423,'Spectral fisherman drops'),
    (424,'Greater kappa drops'),
    (425,'Hobgoblin acolyte drops'),
    (426,'Hobgoblin shaman drops'),
    (427,'Lesser burrow orc drops'),
    (428,'Shelfae guard drops'),
    (429,'Shelfae soldier drops'),
    (430,'Greater burrow orc drops'),
    (431,'Snow spectre drops'),
    (432,'Gnoll miner drops');

-- ── LOOT TABLE ENTRIES ────────────────────────────────────────────────
-- item 1032=wooden coffer, 1035=dented iron box, 1082=ornate brass box
-- Entry IDs start at 6290 (safe gap after L5/catchup batches)
-- Scale by level: L6 ~22/18/8%, L7 ~25/20/10%, L8+ ~28/22/12%
INSERT IGNORE INTO `loot_table_entries`
    (`id`,`loot_table_id`,`item_id`,`drop_chance`,`quantity_min`,`quantity_max`)
VALUES
    (6290,421,1032,22.00,1,1),(6291,421,1035,18.00,1,1),(6292,421,1082,8.00,1,1),  -- lesser mummy L6
    (6293,422,1032,22.00,1,1),(6294,422,1035,15.00,1,1),(6295,422,1082,8.00,1,1),  -- monkey L6
    (6296,423,1032,22.00,1,1),(6297,423,1035,15.00,1,1),(6298,423,1082,8.00,1,1),  -- spectral fisherman L6
    (6299,424,1032,25.00,1,1),(6300,424,1035,20.00,1,1),(6301,424,1082,10.00,1,1), -- greater kappa L7
    (6302,425,1032,25.00,1,1),(6303,425,1035,20.00,1,1),(6304,425,1082,10.00,1,1), -- hobgoblin acolyte L7
    (6305,426,1032,25.00,1,1),(6306,426,1035,20.00,1,1),(6307,426,1082,10.00,1,1), -- hobgoblin shaman L7
    (6308,427,1032,25.00,1,1),(6309,427,1035,20.00,1,1),(6310,427,1082,10.00,1,1), -- lesser burrow orc L7
    (6311,428,1032,25.00,1,1),(6312,428,1035,20.00,1,1),(6313,428,1082,10.00,1,1), -- shelfae guard L7
    (6314,429,1032,25.00,1,1),(6315,429,1035,20.00,1,1),(6316,429,1082,10.00,1,1), -- shelfae soldier L7
    (6317,430,1032,28.00,1,1),(6318,430,1035,22.00,1,1),(6319,430,1082,12.00,1,1), -- greater burrow orc L8
    (6320,431,1032,28.00,1,1),(6321,431,1035,22.00,1,1),(6322,431,1082,12.00,1,1), -- snow spectre L9
    (6323,432,1032,28.00,1,1),(6324,432,1035,22.00,1,1),(6325,432,1082,12.00,1,1); -- gnoll miner L10

-- ── CREATURES ─────────────────────────────────────────────────────────
-- XP: L2=56, L3=108, L4=176, L6=360, L7=476, L8=608, L9=756, L10=920
-- Silver scale: L2=4-16, L3=6-24, L4=8-32, L6=14-56, L7=18-72,
--               L8=22-88, L9=26-104, L10=30-120
INSERT INTO `creatures`
    (`id`,`name`,`article`,`level`,`creature_type`,`health_max`,
     `attack_strength`,`defense_strength`,`casting_strength`,`target_defense`,
     `action_timer`,`behavior_script`,`is_aggressive`,`can_cast`,`can_maneuver`,
     `is_undead`,`body_type`,`experience_value`,`silver_min`,`silver_max`,
     `loot_table_id`,`skin_noun`,`skin_item_id`,`description`,`death_message`)
VALUES

-- ══ GUESSED ═══════════════════════════════════════════════════════════
(10416,'coconut crab','a',2,'normal',45,
 45,30,0,6, 8,NULL,1,0,1, 0,'crustacean',56,0,0,
 NULL,'coconut crab claw',NULL,
 'The coconut crab is far larger than any crab has a right to be, its shell patterned in rings of dull brown and cream. Its claws are absurdly oversized relative to its body and capable of exerting crushing force sufficient to split bone.',
 'curls up on the black stone and goes still.'),

(9334,'cave nipper','a',3,'normal',44,
 65,42,0,9, 8,NULL,1,0,0, 0,'quadruped',108,0,0,
 NULL,'cave nipper skin',NULL,
 'The cave nipper is a compact, low-slung reptile with shovel-shaped claws adapted for burrowing through soft rock. Its scales are translucent pink-white from generations in lightless mines, and its eyes are vestigial — it hunts entirely by vibration and heat.',
 'convulses once and goes very still.'),

(10417,'spotted velnalin','a',3,'normal',48,
 72,36,0,9, 8,NULL,1,0,1, 0,'quadruped',108,0,0,
 NULL,'velnalin horn',NULL,
 'The spotted velnalin moves through the farm pastures with deceptive calm, its dappled coat shifting between gold and grey. Like its striped kin it has the wrong teeth for a deer — sharp, interlocking, and clearly not for grazing.',
 'crashes into the grass and does not rise.'),

(10418,'black urgh','a',4,'normal',88,
 80,62,0,12, 8,NULL,1,0,1, 0,'quadruped',176,0,0,
 NULL,'black urgh hide',NULL,
 'The herbivorous black urgh resembles an overgrown, hairy pig with a dusty black coat and a curled, hairless tail. Instead of the usual jaw, the black urgh has an extremely long upper lip it can extend two feet to drag vegetation into its mouth. Under the mouth reside two curved tusks it uses to root through earth.',
 'crashes to the earth with a grunt and does not rise.'),

-- ══ L6 ════════════════════════════════════════════════════════════════
(10419,'leaper','a',6,'normal',69,
 94,19,0,18, 8,NULL,1,0,1, 0,'quadruped',360,0,0,
 NULL,'leaper hide',NULL,
 'The leaper is built entirely around the first strike: a compact body on four heavily-muscled legs that accelerates from stillness to full charge before you register the movement. Its hide is tough, its jaw strong, and the stomp at the apex of its leap hits harder than anything else in its arsenal.',
 'lands hard and does not get back up.'),

(10420,'leaper','a',6,'normal',69,
 94,19,0,18, 8,NULL,1,0,1, 0,'quadruped',360,0,0,
 NULL,'leaper hide',NULL,
 'The leaper haunting these frozen slopes is leaner than its coastal cousin, its pale grey hide blending with rocky snow-dusted terrain. The cold has done nothing to dampen its aggression. It crouches perfectly still until you are close enough that the lunge covers the distance before you can respond.',
 'slides to the frozen ground and goes still.'),

(9335,'lesser mummy','a',6,'normal',91,
 118,37,0,18, 9,NULL,1,0,1, 1,'biped',360,14,56,
 421,'mummy''s shroud',NULL,
 'The lesser mummy shuffles with the dead weight of something that should not be moving at all. Its wrappings are ancient and stained dark in old patterns, compressed so tightly against the desiccated form beneath that every joint bends wrong. The ensnare it delivers has nothing to do with training.',
 'collapses in a heap of dry wrappings and goes still.'),

(10421,'monkey','a',6,'normal',60,
 88,48,0,18, 8,NULL,1,0,1, 0,'biped',360,14,56,
 422,'monkey paw',NULL,
 'The monkey is barely two feet tall and completely convinced this gives it an advantage. It moves with erratic, unpredictable speed through the tunnel complex, armed with a wooden cane and a red vine whip. It will steal your focus, vanish into shadows, and reappear hitting you from a direction you were not watching.',
 'tumbles to the ground, cane clattering away.'),

(10422,'snowy cockatrice','a',6,'normal',69,
 109,38,0,18, 8,NULL,1,0,1, 0,'hybrid',360,0,0,
 NULL,'snowy cockatrice feather',NULL,
 'The snowy cockatrice has adapted to frozen terrain by developing stiff white feathers over its formidable frame. The leonine hindquarters provide the charge; the rooster head on the serpent neck provides the stare — a focused gaze that costs its target precious seconds of reaction time.',
 'collapses into the snow with a final, furious hiss.'),

(10423,'spectral fisherman','a',6,'normal',90,
 94,15,0,18, 8,NULL,1,0,0, 1,'biped',360,14,56,
 423,'',NULL,
 'The spectral fisherman still stands as it did in life — bent slightly at the knee, arm raised with a trident of cold spectral light. It has no memory of its name or crew. It has only the motion, repeated endlessly: the cast, the haul, the strike.',
 'scatters into cold sea-light and is gone.'),

-- ══ L7 ════════════════════════════════════════════════════════════════
(10424,'blood eagle','a',7,'normal',120,
 105,38,0,21, 9,NULL,1,0,1, 0,'avian',476,0,0,
 NULL,'blood eagle feather',NULL,
 'The blood eagle''s wingspan blocks a corridor when fully extended, and it uses this deliberately. The scarlet wash across its breast feathers is not plumage — it is accumulation. Its talons are built for carrying prey aloft and releasing it from height.',
 'crashes to the ground with a sound that carries.'),

(10425,'greater kappa','a',7,'normal',100,
 107,31,0,21, 9,NULL,1,0,0, 0,'biped',476,18,72,
 424,'kappa shell',NULL,
 'The greater kappa stands taller than a man and smells powerfully of brine and mud. Its shell carries the battered record of a long history of confrontations. It carries a handaxe with the casual grip of something that has held it for a very long time.',
 'slumps against the coastal rock and goes still.'),

(10426,'hobgoblin acolyte','a',7,'normal',100,
 104,50,0,21, 9,NULL,1,1,0, 0,'biped',476,18,72,
 425,'hobgoblin scalp',NULL,
 'The hobgoblin acolyte has traded physical size for the ability to hurl arcs of electricity and water from range. It is smaller than a standard hobgoblin and faster, and it uses that speed to maintain distance. The whip it carries is a last resort.',
 'pitches forward, twitching, and goes still.'),

(9336,'hobgoblin shaman','a',7,'normal',80,
 111,70,0,21, 9,NULL,1,1,0, 0,'biped',476,18,72,
 426,'hobgoblin scalp',NULL,
 'The hobgoblin shaman has learned enough elemental magic to be dangerous at all distances. The ornaments in its hair are bones of things it has killed, and the mace it carries has been wrapped in leather so many times the original is unrecognizable. It casts first, hits second, and has no preference for which kills you.',
 'crumples in a heap, mace clattering beside it.'),

(10427,'lesser burrow orc','a',7,'normal',100,
 127,90,0,21, 9,NULL,1,0,0, 0,'biped',476,18,72,
 427,'orc ear',NULL,
 'The lesser burrow orc is shorter and wider than surface orcs, built for fighting in tunnels where a taller weapon would catch the ceiling. Its skin is grey-green from rarely seeing sunlight and its eyes have expanded to compensate. It moves through the passages with the ease of something that knows every turn by memory.',
 'drops to the tunnel floor.'),

(10428,'shelfae guard','a',7,'normal',95,
 110,55,0,21, 9,NULL,1,0,0, 0,'biped',476,18,72,
 428,'shelfae scale',NULL,
 'The shelfae guard is a half-shell creature on a humanoid frame, its carapace covering torso and shoulders in overlapping grey-green chitin plates. It stands patrol with the rigid attention of something trained rather than instinctual, spear at a formal angle, tracking movement on the cliffface with patient eyes.',
 'sways and falls, spear clattering on the stone.'),

(10429,'shelfae soldier','a',7,'normal',100,
 102,41,0,21, 9,NULL,1,0,0, 0,'hybrid',476,18,72,
 429,'shelfae scale',NULL,
 'The shelfae soldier wades through shallows with equal confidence as it moves across rocks, trident ready, its shell offering lateral protection. It fights in formation when others are nearby and alone when not, and neither changes its expression.',
 'falls heavily into the water or onto the rocks.'),

-- ══ L8 ════════════════════════════════════════════════════════════════
(9337,'albino tomb spider','a',8,'normal',83,
 116,77,0,24, 9,NULL,1,0,1, 0,'arachnid',608,0,0,
 NULL,'tomb spider leg',NULL,
 'The albino tomb spider has spent so many generations in lightless crypts that colour has left it entirely. Its body is chalk-white and the silk it produces looks like frost and holds just as fast. It is patient in the way that only things which do not need to eat often can afford to be.',
 'curls inward, legs folding slowly.'),

(10430,'crystal crab','a',8,'normal',85,
 122,51,0,24, 9,NULL,1,0,1, 0,'crustacean',608,0,0,
 NULL,'crystal crab claw',NULL,
 'The crystal crab''s shell has the translucent quality of thick glass, refracting tunnel light in cold prismatic flashes. Its claws are disproportionately large and the ensnare they deliver is mechanical — a grip that closes and does not release without sustained effort to break it.',
 'goes still, claws slowly unclenching.'),

(10431,'greater burrow orc','a',8,'normal',110,
 128,86,0,24, 9,NULL,1,0,0, 0,'biped',608,22,88,
 430,'orc ear',NULL,
 'The greater burrow orc is the senior rank in the valley hierarchy and makes no effort to hide it. Its double leather is dark with use and its short sword has been resharpened so many times the blade is narrower than it started. It moves through tunnels with the unhurried competence of something that has fought here every day of its adult life.',
 'crashes to the tunnel floor.'),

(10432,'mottled thrak','a',8,'normal',130,
 125,65,0,24, 9,NULL,1,0,0, 0,'quadruped',608,0,0,
 NULL,'mottled thrak hide',NULL,
 'The mottled thrak is identified by the broken camouflage pattern of olive and rust across its scales. Where the standard thrak is an ambush predator, the mottled variant charges directly. Its armoured hide makes it indifferent to most glancing blows.',
 'crashes to the coastal rock.'),

-- ══ L9 ════════════════════════════════════════════════════════════════
(10433,'brown spinner','a',9,'normal',90,
 113,115,0,27, 9,NULL,1,0,1, 0,'arachnid',756,0,0,
 NULL,'brown spinner leg',NULL,
 'The brown spinner builds webs across tunnel junctions and waits in them — a flat shape indistinguishable from silk until it moves. Its defensive speed is remarkable; approaches that work against tomb spiders fail here, and it knows this.',
 'curls tightly and goes still.'),

(10434,'crocodile','a',9,'normal',90,
 137,75,0,27, 9,NULL,1,0,1, 0,'quadruped',756,0,0,
 NULL,'crocodile hide',NULL,
 'The crocodile lies still in the flooded passages with its back just below the waterline, indistinguishable from stone until the charge. The chain hauberk of its natural armour makes it nearly impervious to anything short of sustained assault. The disease it carries is a secondary concern but a real one.',
 'slides beneath the water and does not resurface.'),

(10435,'snow spectre','a',9,'normal',90,
 98,0,50,27, 9,NULL,1,1,0, 1,'biped',756,26,104,
 431,'',NULL,
 'The snow spectre is visible as a distortion in the blowing snow — a column of cold that moves against the wind and carries silence with it. It strikes with a cold fist that hits with more force than physics should allow, and the fear it channels is not a spell so much as the raw sensation of standing next to something that should not exist.',
 'disperses into a sudden cold gust and is gone.'),

-- ══ L10 ═══════════════════════════════════════════════════════════════
(9338,'cave worm','a',10,'normal',100,
 139,118,0,30, 9,NULL,1,0,1, 0,'worm',920,0,0,
 NULL,'cave worm hide',NULL,
 'The cave worm erupts from the mine floor with no warning, displacing rock and timber with equal indifference. Its ensnare coils quickly and holds with muscular force while its bite handles the rest. The brigandine-grade natural armour of its hide means weapons must find the right angle, and the worm is never still.',
 'convulses once and settles into the earth.'),

(10436,'crazed canine','a',10,'normal',100,
 128,80,0,30, 9,NULL,1,0,1, 0,'quadruped',920,0,0,
 NULL,'canine pelt',NULL,
 'The crazed canine is large, fast, and has been feral long enough that the domesticated animal underneath is entirely theoretical. Its eyes track too many things at once and it moves in stops and starts rather than a straight line. The leap from a crouch covers more ground than the approach distance suggests.',
 'tumbles to the ground and goes still.'),

(10437,'gnoll miner','a',10,'normal',105,
 125,84,0,30, 9,NULL,1,0,0, 0,'biped',920,30,120,
 432,'gnoll tooth',NULL,
 'The gnoll miner swings a handaxe with the efficiency of something that has spent its life bringing it down onto stone. The mining background has given it exceptional upper body strength and a complete indifference to dust, confined spaces, and the sound of things collapsing. It does not roar before attacking — it just swings.',
 'drops the handaxe and falls.'),

(10438,'rabid guard dog','a',10,'normal',100,
 123,77,0,30, 9,NULL,1,0,1, 0,'quadruped',920,0,0,
 NULL,'guard dog pelt',NULL,
 'The rabid guard dog was bred for this work and left here long enough to go wrong. Large, heavily built, it moves with the locked-jaw focus of an animal that has forgotten most things except the directive to stop anything entering this tunnel section. The disease it carries has progressed to the point where it affects its movement — making it faster, not slower.',
 'crashes to the tunnel floor, finally still.');

-- ── VERIFICATION ─────────────────────────────────────────────────────
-- SELECT id,name,level,experience_value,is_undead,can_cast,can_maneuver
-- FROM creatures
-- WHERE id IN (
--   10416,9334,10417,10418,
--   10419,10420,9335,10421,10422,10423,
--   10424,10425,10426,9336,10427,10428,10429,
--   9337,10430,10431,10432,
--   10433,10434,10435,
--   9338,10436,10437,10438
-- ) ORDER BY level,id;
-- Expected xp: 56,108,108,176,360x5,476x7,608x4,756x3,920x4
-- is_undead=1: 9335(lesser mummy),10423(spectral fisherman),10435(snow spectre)
-- can_cast=1:  10426(hob acolyte),9336(hob shaman),10435(snow spectre)
