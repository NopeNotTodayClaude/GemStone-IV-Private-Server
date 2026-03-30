USE gemstone_dev;

UPDATE rooms
SET paths_text = 'Obvious exits: east, go door, go panel'
WHERE id = 17833;

UPDATE rooms
SET paths_text = 'Obvious exits: down, go trapdoor'
WHERE id = 18345;

INSERT INTO room_exits (
    room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc
) VALUES
    (17833, 'go_panel', 'go', 18347, 0, 1, 0),
    (18345, 'ask_pyll_about_train_gambits', 'ask', 30766, 0, 1, 0)
ON DUPLICATE KEY UPDATE
    exit_verb = VALUES(exit_verb),
    target_room_id = VALUES(target_room_id),
    is_hidden = VALUES(is_hidden),
    is_special = VALUES(is_special),
    search_dc = VALUES(search_dc);

DELETE FROM guild_master_registry
WHERE guild_id = 'rogue'
  AND npc_template_id IN (
      'tv_rogue_training_admin',
      'tv_rogue_guildmaster',
      'tv_rogue_master_pyll'
  );

INSERT INTO guild_master_registry (
    guild_id, npc_template_id, role_type, room_id, lich_room_id, city_name, notes, is_active
) VALUES
    ('rogue', 'tv_rogue_training_admin', 'administrator', 17836, 17836, 'Ta''Vaalor', 'Ta''Vaalor rogue training administrator keeping the guild ledgers and task records.', 1),
    ('rogue', 'tv_rogue_guildmaster', 'master', 17831, 17831, 'Ta''Vaalor', 'Ta''Vaalor rogue guildmaster working from the office off the inn hall.', 1),
    ('rogue', 'tv_rogue_master_pyll', 'trainer', 18345, 18345, 'Ta''Vaalor', 'Pyll handles the cellar-side rogue gambit training access.', 1);

INSERT INTO shops (id, name, room_id, shop_type, buy_multiplier, sell_multiplier, is_active)
VALUES (460, 'Ta''Vaalor Rogue Guild Specialty Shop', 17821, 'other', 1.0, 0.5, 1)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    room_id = VALUES(room_id),
    shop_type = VALUES(shop_type),
    buy_multiplier = VALUES(buy_multiplier),
    sell_multiplier = VALUES(sell_multiplier),
    is_active = VALUES(is_active);

DELETE FROM npc_state
WHERE template_id IN (
    'tv_rogue_training_admin',
    'tv_rogue_guildmaster',
    'tv_rogue_shopkeeper',
    'tv_rogue_master_pyll',
    'tv_rogue_scribe',
    'tv_rogue_warehouse_overseer',
    'tv_rogue_iron_door_sentry'
);

INSERT INTO npc_state (template_id, is_alive, current_room_id, respawn_at) VALUES
    ('tv_rogue_training_admin', 1, 17836, 0),
    ('tv_rogue_guildmaster', 1, 17831, 0),
    ('tv_rogue_shopkeeper', 1, 17821, 0),
    ('tv_rogue_master_pyll', 1, 18345, 0),
    ('tv_rogue_scribe', 1, 17835, 0),
    ('tv_rogue_warehouse_overseer', 1, 17820, 0),
    ('tv_rogue_iron_door_sentry', 1, 17829, 0)
ON DUPLICATE KEY UPDATE
    is_alive = VALUES(is_alive),
    current_room_id = VALUES(current_room_id),
    respawn_at = VALUES(respawn_at);
