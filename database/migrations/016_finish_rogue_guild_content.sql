-- Finish Rogue Guild content: contacts, training tasks, and guided guild quests.

ALTER TABLE character_quests
    ADD COLUMN IF NOT EXISTS progress_count SMALLINT UNSIGNED NOT NULL DEFAULT 0 AFTER stage,
    ADD COLUMN IF NOT EXISTS target_count SMALLINT UNSIGNED NOT NULL DEFAULT 1 AFTER progress_count,
    ADD COLUMN IF NOT EXISTS quest_data JSON DEFAULT NULL AFTER target_count,
    ADD COLUMN IF NOT EXISTS updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER completed_at;

ALTER TABLE guild_ledger
    MODIFY COLUMN entry_type ENUM(
        'join','dues','checkin','task','promotion','resign',
        'invite','initiate','voucher','nominate','guildmaster','quest'
    ) NOT NULL;

INSERT INTO guild_master_registry (
    guild_id, npc_template_id, role_type, room_id, lich_room_id, city_name, notes, is_active
) VALUES
    ('rogue', 'tv_rogue_guild_contact', 'contact', 18348, 18348, 'Ta''Vaalor', 'Hidden Ta''Vaalor rogue contact inside the basement access hall.', 1),
    ('rogue', 'mh_rogue_contact_mh', 'contact', 19337, 19337, 'Mist Harbor', 'Mist Harbor rogue contact operating out of the Broken Stein back room.', 1),
    ('rogue', 'rr_rogue_contact_rr', 'contact', 17984, 17984, 'River''s Rest', 'River''s Rest rogue contact keeping quiet watch in the inn pantry.', 1),
    ('rogue', 'sol_rogue_contact', 'contact', 17931, 17931, 'Solhaven', 'Solhaven rogue contact near the hidden guild steps.', 1),
    ('rogue', 'tai_rogue_contact_tai', 'contact', 13350, 13350, 'Ta''Illistim', 'Ta''Illistim rogue contact seated discreetly in the arboretum.', 1),
    ('rogue', 'zl_rogue_contact_zl', 'contact', 16838, 16838, 'Zul Logoth', 'Zul Logoth rogue contact disguised as a brewery worker.', 1),
    ('rogue', 'wl_beldrin', 'master', 16393, 16393, 'Wehnimer''s Landing', 'Beldrin serves as a visible rogue guildmaster authority.', 1)
ON DUPLICATE KEY UPDATE
    role_type = VALUES(role_type),
    lich_room_id = VALUES(lich_room_id),
    city_name = VALUES(city_name),
    notes = VALUES(notes),
    is_active = VALUES(is_active);

INSERT INTO guild_task_definitions (
    guild_id, skill_name, task_code, title, description, objective_event,
    required_count, base_points, min_rank, max_rank, practice_room_id,
    requires_guild_authority, is_active
) VALUES
    ('rogue', 'Cheapshots', 'cheapshot_live', 'Dirty Fighting', 'Land a practiced cheapshot in the field without losing control of the exchange.', 'cheapshot_success', 2, 2, 0, NULL, NULL, 0, 1),
    ('rogue', 'Lock Mastery', 'lm_focus', 'Focus the Eye', 'Use LMASTER FOCUS before working a stubborn lock or trap.', 'lm_focus', 2, 1, 0, NULL, NULL, 0, 1),
    ('rogue', 'Lock Mastery', 'lm_sense', 'Read the Room', 'Use LMASTER SENSE to evaluate room conditions for locksmithing.', 'lm_sense', 2, 1, 0, NULL, NULL, 0, 1),
    ('rogue', 'Lock Mastery', 'lm_calipers', 'Measure the Tumblers', 'Use LMASTER CALIPERS on a locked container to size the mechanism.', 'lm_calipers', 2, 1, 0, NULL, NULL, 0, 1),
    ('rogue', 'Rogue Gambits', 'gambit_perform', 'Showmanship Drill', 'Perform rogue gambits cleanly and with confidence.', 'rgambit_perform', 4, 1, 0, NULL, NULL, 0, 1)
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    description = VALUES(description),
    objective_event = VALUES(objective_event),
    required_count = VALUES(required_count),
    base_points = VALUES(base_points),
    min_rank = VALUES(min_rank),
    max_rank = VALUES(max_rank),
    practice_room_id = VALUES(practice_room_id),
    requires_guild_authority = VALUES(requires_guild_authority),
    is_active = VALUES(is_active);

INSERT INTO quest_definitions (
    key_name, title, description, min_level, max_level, is_repeatable, lua_script
) VALUES
    (
        'rogue_entry',
        'Quiet Entry',
        'Learn the guild''s quiet ways, prove you can move through the hidden approach, and make your name known in the ledger.',
        15, 100, 0, 'quests/rogue/entry_trial'
    ),
    (
        'rogue_lockmastery',
        'Locks Within Locks',
        'Demonstrate the patience and feel expected of a guild locksmith by sensing conditions, measuring tumblers, and opening real work in the field.',
        15, 100, 0, 'quests/rogue/lockmastery_trial'
    ),
    (
        'rogue_dirty_fighting',
        'A Knife in the Dark',
        'Show the guild that you can win ugly, from the shadows when needed and in open motion when the work turns rough.',
        15, 100, 0, 'quests/rogue/dirty_fighting_trial'
    ),
    (
        'rogue_fieldcraft',
        'Never Lose the Edge',
        'Prove you can keep your feet, keep your nerve, and turn a bad exchange back in your favor.',
        15, 100, 0, 'quests/rogue/fieldcraft_trial'
    )
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    description = VALUES(description),
    min_level = VALUES(min_level),
    max_level = VALUES(max_level),
    is_repeatable = VALUES(is_repeatable),
    lua_script = VALUES(lua_script);
