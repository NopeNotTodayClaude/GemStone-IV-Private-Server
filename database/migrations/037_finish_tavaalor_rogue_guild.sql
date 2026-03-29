-- 037_finish_tavaalor_rogue_guild.sql
-- Complete the Ta'Vaalor Rogue Guild flow: shed proof, inner door, guild proper,
-- trainer rooms, and the orientation quest.

ALTER TABLE character_guild_access
    ADD COLUMN IF NOT EXISTS entry_proved_at DATETIME NULL AFTER sequence_started_at,
    ADD COLUMN IF NOT EXISTS member_access_at DATETIME NULL AFTER entry_proved_at,
    ADD COLUMN IF NOT EXISTS shind_unlock_until DATETIME NULL AFTER member_access_at;

INSERT INTO rooms (
    id, zone_id, title, description, lich_uid, paths_text, location_name,
    tags_json, is_safe, is_supernode, is_indoor, terrain_type, climate, terrain, indoor
) VALUES
    (
        36780, 2, 'Guild Alley',
        'Hemmed in by leaning warehouse walls and a soot-dark inn facade, this narrow alley serves as the quiet heart of Ta''Vaalor''s rogue chapter.  Rope ladders, shuttered windows, and a battered practice dummy crowd the edges, while a broad ironwood chute disappears up through the locksmith''s floorboards above.  Nothing here invites casual company, yet every board and bolt has clearly been placed with deliberate intent.',
        36780, 'north, east, west, chute', 'Ta''Vaalor',
        JSON_ARRAY('rogue guild','rogueguild','guild interior','guild alley'), 1, 0, 1, 'urban', NULL, NULL, 1
    ),
    (
        36781, 2, 'Lockmaster''s Workroom',
        'A scarred oak worktable dominates this cramped room, its surface crowded by blank boxes, tension tools, wires, calipers, and rows of exhausted picks sorted by damage.  Tiny chalk marks cover the walls, recording old lock difficulties, trap tells, and timing drills.  The entire place smells faintly of lamp oil, metal dust, and patience.',
        36781, 'south', 'Ta''Vaalor',
        JSON_ARRAY('rogue guild','rogueguild','lock mastery','guild trainer'), 1, 0, 1, 'urban', NULL, NULL, 1
    ),
    (
        36782, 2, 'Warehouse Floor',
        'Low beams cross above stacked crates, bundled rope, and a scattering of narrow tables scarred by knife points and spilled lampblack.  The room is open enough for a quick scuffle but cluttered enough to reward a dirty angle.  Marks on the floorboards show where rogues have practiced sweeps, reversals, and unpleasant surprises for years.',
        36782, 'west', 'Ta''Vaalor',
        JSON_ARRAY('rogue guild','rogueguild','dirty fighting','guild trainer'), 1, 0, 1, 'urban', NULL, NULL, 1
    ),
    (
        36783, 2, 'Drill Court',
        'Lantern light spills across a compact training court boxed in by weathered brick and timber.  Chalk circles, sanded lanes, and hanging targets divide the space into neat drill stations for feints, rushes, gambits, and fast recoveries.  The atmosphere is disciplined rather than comfortable, built for repetition instead of rest.',
        36783, 'east', 'Ta''Vaalor',
        JSON_ARRAY('rogue guild','rogueguild','drill court','guild trainer'), 1, 0, 1, 'urban', NULL, NULL, 1
    )
ON DUPLICATE KEY UPDATE
    zone_id = VALUES(zone_id),
    title = VALUES(title),
    description = VALUES(description),
    lich_uid = VALUES(lich_uid),
    paths_text = VALUES(paths_text),
    location_name = VALUES(location_name),
    tags_json = VALUES(tags_json),
    is_safe = VALUES(is_safe),
    is_supernode = VALUES(is_supernode),
    is_indoor = VALUES(is_indoor),
    terrain_type = VALUES(terrain_type),
    climate = VALUES(climate),
    terrain = VALUES(terrain),
    indoor = VALUES(indoor);

INSERT INTO room_exits (
    room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc
) VALUES
    (36780, 'north', NULL, 36781, 0, 0, 0),
    (36780, 'east', NULL, 36782, 0, 0, 0),
    (36780, 'west', NULL, 36783, 0, 0, 0),
    (36781, 'south', NULL, 36780, 0, 0, 0),
    (36782, 'west', NULL, 36780, 0, 0, 0),
    (36783, 'east', NULL, 36780, 0, 0, 0)
ON DUPLICATE KEY UPDATE
    exit_verb = VALUES(exit_verb),
    target_room_id = VALUES(target_room_id),
    is_hidden = VALUES(is_hidden),
    is_special = VALUES(is_special),
    search_dc = VALUES(search_dc);

UPDATE guild_master_registry
SET role_type = 'master',
    room_id = 36780,
    lich_room_id = 36780,
    notes = 'Ta''Vaalor rogue guild factor working from the inner alley after the basement password door.'
WHERE guild_id = 'rogue' AND npc_template_id = 'tv_rogue_guild_contact';

INSERT INTO guild_master_registry (
    guild_id, npc_template_id, role_type, room_id, lich_room_id, city_name, notes, is_active
) VALUES
    ('rogue', 'tv_rogue_lockmaster', 'trainer', 36781, 36781, 'Ta''Vaalor', 'Ta''Vaalor rogue trainer for Lock Mastery.', 1),
    ('rogue', 'tv_rogue_bruiser', 'trainer', 36782, 36782, 'Ta''Vaalor', 'Ta''Vaalor rogue trainer for Cheapshots, Sweep, and Subdue.', 1),
    ('rogue', 'tv_rogue_drillmaster', 'trainer', 36783, 36783, 'Ta''Vaalor', 'Ta''Vaalor rogue trainer for Stun Maneuvers and Rogue Gambits.', 1)
ON DUPLICATE KEY UPDATE
    role_type = VALUES(role_type),
    room_id = VALUES(room_id),
    lich_room_id = VALUES(lich_room_id),
    city_name = VALUES(city_name),
    notes = VALUES(notes),
    is_active = VALUES(is_active);

UPDATE guild_task_definitions
SET practice_room_id = 36783
WHERE guild_id = 'rogue' AND task_code IN ('gambit_practice','stun_practice','subdue_practice','sweep_practice');

UPDATE quest_definitions
SET description = 'Prove you can work the Ta''Vaalor shed, pass the inner basement door, join cleanly, and check in with the guild ledger.',
    lua_script = 'quests/rogue/entry_trial_tv'
WHERE key_name = 'rogue_entry';

INSERT INTO quest_definitions (
    key_name, title, description, min_level, max_level, is_repeatable, lua_script
) VALUES
    (
        'rogue_orientation',
        'The First Walkthrough',
        'Settle your ledger, learn the inner rooms, and meet the hands that actually keep the Ta''Vaalor chapter running.',
        15, 100, 0, 'quests/rogue/orientation_trial'
    )
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    description = VALUES(description),
    min_level = VALUES(min_level),
    max_level = VALUES(max_level),
    is_repeatable = VALUES(is_repeatable),
    lua_script = VALUES(lua_script);
