-- 040_fix_tavaalor_rogue_guild_real_rooms.sql
-- Retarget Ta'Vaalor rogue guild runtime data to the real Lich-mapped guild rooms.

DELETE FROM guild_master_registry
WHERE guild_id = 'rogue'
  AND city_name = 'Ta''Vaalor'
  AND npc_template_id IN (
      'tv_rogue_guild_contact',
      'tv_rogue_lockmaster',
      'tv_rogue_bruiser',
      'tv_rogue_drillmaster'
  )
  AND room_id IN (36780, 36781, 36782, 36783);

INSERT INTO guild_master_registry (
    guild_id, npc_template_id, role_type, room_id, lich_room_id, city_name, is_active, notes
) VALUES
    ('rogue', 'tv_rogue_guild_contact', 'master', 17806, 17806, 'Ta''Vaalor', 1,
     'Ta''Vaalor rogue guild factor working from the inner alley just beyond the basement password door.'),
    ('rogue', 'tv_rogue_lockmaster', 'trainer', 17827, 17827, 'Ta''Vaalor', 1,
     'Ta''Vaalor rogue trainer for Lock Mastery in the workshop.'),
    ('rogue', 'tv_rogue_bruiser', 'trainer', 17819, 17819, 'Ta''Vaalor', 1,
     'Ta''Vaalor rogue trainer for Cheapshots, Sweep, and Subdue on the warehouse floor.'),
    ('rogue', 'tv_rogue_drillmaster', 'trainer', 17822, 17822, 'Ta''Vaalor', 1,
     'Ta''Vaalor rogue trainer for Stun Maneuvers and Rogue Gambits in the drill corridor.')
ON DUPLICATE KEY UPDATE
    role_type = VALUES(role_type),
    room_id = VALUES(room_id),
    lich_room_id = VALUES(lich_room_id),
    city_name = VALUES(city_name),
    is_active = VALUES(is_active),
    notes = VALUES(notes);

UPDATE guild_task_definitions
SET practice_room_id = 17819
WHERE guild_id = 'rogue' AND task_code IN ('subdue_practice', 'sweep_practice');

UPDATE guild_task_definitions
SET practice_room_id = 17822
WHERE guild_id = 'rogue' AND task_code IN ('gambit_practice', 'stun_practice');

DELETE FROM room_exits
WHERE room_id IN (36780, 36781, 36782, 36783);

INSERT INTO room_exits (
    room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc
) VALUES
    (36780, 'north', NULL, 17827, 0, 0, 0),
    (36780, 'east', NULL, 17819, 0, 0, 0),
    (36780, 'west', NULL, 17822, 0, 0, 0),
    (36780, 'out', NULL, 17806, 0, 0, 0),
    (36781, 'south', NULL, 17806, 0, 0, 0),
    (36781, 'out', NULL, 17827, 0, 0, 0),
    (36782, 'west', NULL, 17806, 0, 0, 0),
    (36782, 'out', NULL, 17819, 0, 0, 0),
    (36783, 'east', NULL, 17806, 0, 0, 0),
    (36783, 'out', NULL, 17822, 0, 0, 0)
ON DUPLICATE KEY UPDATE
    exit_verb = VALUES(exit_verb),
    target_room_id = VALUES(target_room_id),
    is_hidden = VALUES(is_hidden),
    is_special = VALUES(is_special),
    search_dc = VALUES(search_dc);
