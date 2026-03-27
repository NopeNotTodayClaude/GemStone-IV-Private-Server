-- Glaise Cnoc Cemetery & Plains of Bone
-- Zone seed + room registry
-- Zone ID: 3
USE gemstone_dev;

-- ─────────────────────────────────────────────────────────────────────────────
-- ZONE
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO zones (id, slug, name, region, level_min, level_max, climate, is_enabled)
VALUES (3, 'glaise_cnoc', 'Glaise Cnoc', 'Elanith', 1, 20, 'temperate', TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ─────────────────────────────────────────────────────────────────────────────
-- ROOMS - Outer Fence Path (NE arc)
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO rooms (id, zone_id, title, is_safe, is_indoor, is_supernode, terrain_type) VALUES
(5834, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5835, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5836, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5837, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5838, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5839, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5840, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5841, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5842, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
-- East Mausoleum exterior
(5843, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
-- NW arc continuing
(5844, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5845, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5846, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5847, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5848, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5849, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5850, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
-- Storage Shed junction
(5851, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
-- SW arc
(5852, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5853, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5854, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5855, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5856, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5857, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5858, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
-- West Mausoleum (Cenotaph) exterior
(5859, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
-- South arc back to gate
(5860, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5861, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5862, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5863, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5864, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5865, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5866, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
-- Hillock
(5867, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),

-- ─────────────────────────────────────────────────────────────────────────────
-- ROOMS - Old Cemetery Interior
-- ─────────────────────────────────────────────────────────────────────────────
(5868, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5869, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5870, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5871, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5872, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5873, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5874, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5875, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5876, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5877, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5878, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5879, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5880, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5881, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5882, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5884, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5885, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5886, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5887, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5888, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5889, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5890, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5891, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5892, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(5893, 3, 'Glaise Cnoc, Cemetery',  FALSE, FALSE, FALSE, 'outdoor'),
(24559, 3, 'Glaise Cnoc, Cemetery', FALSE, FALSE, FALSE, 'outdoor'),
(29574, 3, 'Glaise Cnoc, Cemetery', FALSE, FALSE, FALSE, 'outdoor'),
(29575, 3, 'Glaise Cnoc, Cemetery', FALSE, FALSE, FALSE, 'outdoor'),
(29576, 3, 'Glaise Cnoc, Cemetery', FALSE, FALSE, FALSE, 'outdoor'),

-- ─────────────────────────────────────────────────────────────────────────────
-- ROOMS - Cemetery Structures
-- ─────────────────────────────────────────────────────────────────────────────
(10673, 3, 'Glaise Cnoc, Caretaker',     TRUE,  TRUE,  FALSE, 'indoor'),
(10674, 3, 'Glaise Cnoc, Mausoleum',     FALSE, TRUE,  FALSE, 'indoor'),
(10675, 3, 'Glaise Cnoc, Storage Shed',  FALSE, TRUE,  FALSE, 'indoor'),
(10676, 3, 'Glaise Cnoc, Columbarium',   FALSE, TRUE,  FALSE, 'indoor'),
(10677, 3, 'Glaise Cnoc, Columbarium',   FALSE, TRUE,  FALSE, 'indoor'),
(10679, 3, 'Glaise Cnoc, Cenotaph',      FALSE, TRUE,  FALSE, 'indoor'),
(10682, 3, 'Glaise Cnoc, Columbarium',   FALSE, TRUE,  FALSE, 'indoor'),
(10683, 3, 'Glaise Cnoc, Arbor',         TRUE,  FALSE, FALSE, 'outdoor'),
(10684, 3, 'Glaise Cnoc, Columbarium',   FALSE, TRUE,  FALSE, 'indoor'),

-- ─────────────────────────────────────────────────────────────────────────────
-- ROOMS - Catacombs
-- ─────────────────────────────────────────────────────────────────────────────
(10685, 3, 'Catacomb, Entrance',         TRUE,  TRUE,  FALSE, 'indoor'),
(10686, 3, 'Catacomb, Hall',             FALSE, TRUE,  FALSE, 'indoor'),
(10687, 3, 'Catacomb, Pyre',             FALSE, TRUE,  FALSE, 'indoor'),
(10688, 3, 'Catacomb, Ossuary',          FALSE, TRUE,  FALSE, 'indoor'),
(10689, 3, 'Catacomb, Ossuary',          FALSE, TRUE,  FALSE, 'indoor'),
(10690, 3, 'Catacomb, Preparation Room', FALSE, TRUE,  FALSE, 'indoor'),
(10691, 3, 'Catacomb, Morgue',           FALSE, TRUE,  FALSE, 'indoor'),
(10692, 3, 'Catacomb, Chapel',           TRUE,  TRUE,  FALSE, 'indoor'),
(10693, 3, 'Catacomb, Reposing Room',    TRUE,  TRUE,  FALSE, 'indoor'),

-- ─────────────────────────────────────────────────────────────────────────────
-- ROOMS - Plains of Bone: Outer Circle
-- ─────────────────────────────────────────────────────────────────────────────
(10694, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10695, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10696, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10697, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10698, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10699, 3, 'Plains of Bone, Plank',        FALSE, FALSE, FALSE, 'outdoor'),
(10700, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10701, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10702, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10703, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10704, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10705, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10706, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10707, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10708, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10709, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10710, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10711, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10712, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10713, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10714, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),
(10715, 3, 'Plains of Bone, Outer Circle', FALSE, FALSE, FALSE, 'outdoor'),

-- ─────────────────────────────────────────────────────────────────────────────
-- ROOMS - Plains of Bone: Boneyard
-- ─────────────────────────────────────────────────────────────────────────────
(10716, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10717, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10718, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10719, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10720, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10721, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10722, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10723, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10724, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10725, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10726, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10727, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),
(10728, 3, 'Plains of Bone, Boneyard', FALSE, FALSE, FALSE, 'outdoor'),

-- ─────────────────────────────────────────────────────────────────────────────
-- ROOMS - Plains of Bone: Virktoth's Path
-- ─────────────────────────────────────────────────────────────────────────────
(10729, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10730, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10731, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10732, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10733, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10734, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10735, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10736, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10737, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10738, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10739, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10740, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10741, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10742, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10743, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10744, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10745, 3, "Plains of Bone, Virktoth's Path", FALSE, FALSE, FALSE, 'outdoor'),
(10746, 3, 'Plains of Bone, Mound Top',       FALSE, FALSE, FALSE, 'outdoor'),
(10747, 3, 'Plains of Bone, Mound Top',       FALSE, FALSE, FALSE, 'outdoor'),
(10748, 3, 'Plains of Bone, Ruins',           FALSE, TRUE,  FALSE, 'indoor')

ON DUPLICATE KEY UPDATE title=VALUES(title), zone_id=VALUES(zone_id);
