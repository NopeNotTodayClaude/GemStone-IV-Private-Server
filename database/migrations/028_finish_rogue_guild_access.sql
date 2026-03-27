-- 028_finish_rogue_guild_access.sql
-- Normalize rogue guild contacts and hidden access points across the supported towns.

UPDATE guild_master_registry
SET room_id = 8820,
    lich_room_id = 5059,
    city_name = 'Wehnimer''s Landing',
    notes = 'Beldrin serves from the Game Hall office, which fronts the hidden rogue guild path.'
WHERE guild_id = 'rogue' AND npc_template_id = 'wl_beldrin';

UPDATE npcs
SET home_room_id = 8820
WHERE template_id = 'wl_beldrin';

UPDATE npc_state
SET current_room_id = 8820
WHERE template_id = 'wl_beldrin';

DELETE FROM guild_access_points
WHERE guild_id = 'rogue';

INSERT INTO guild_access_points (
    guild_id, city_name, entry_room_id, target_room_id, access_keyword,
    primer_verb, pass_sequence, exit_keyword, notes, is_active
) VALUES
    (
        'rogue', 'Ta''Vaalor', 17805, 18348, 'panel',
        'lean', 'pull,pull,slap,rub,rub,push,turn', 'out',
        'Ta''Vaalor rogue access now begins from the hidden shed on Gaeld Var and opens into the basement hall.',
        1
    ),
    (
        'rogue', 'Wehnimer''s Landing', 8820, 16394, 'panel',
        'lean', 'pull,pull,slap,rub,rub,push,turn', 'out',
        'Wehnimer''s Landing rogue access is staged from Beldrin''s Game Hall office into the guild entry hall.',
        1
    ),
    (
        'rogue', 'Solhaven', 17931, 17933, 'panel',
        'lean', 'pull,pull,slap,rub,rub,push,turn', 'out',
        'Solhaven rogue access is staged from the concealed room into the guild entry hall.',
        1
    ),
    (
        'rogue', 'River''s Rest', 17984, 17988, 'panel',
        'lean', 'pull,pull,slap,rub,rub,push,turn', 'out',
        'River''s Rest rogue access is staged from the inn pantry storage into the guild entry hall.',
        1
    ),
    (
        'rogue', 'Mist Harbor', 19337, 21127, 'panel',
        'lean', 'pull,pull,slap,rub,rub,push,turn', 'out',
        'Mist Harbor rogue access is staged from the Broken Stein backroom into the guild entry.',
        1
    ),
    (
        'rogue', 'Zul Logoth', 16838, 17896, 'panel',
        'lean', 'pull,pull,slap,rub,rub,push,turn', 'out',
        'Zul Logoth rogue access is staged from the Bluerock Brewery office into the guild antechamber.',
        1
    ),
    (
        'rogue', 'Ta''Illistim', 13350, 17965, 'panel',
        'lean', 'pull,pull,slap,rub,rub,push,turn', 'out',
        'Ta''Illistim rogue access is staged from the arboretum and opens into the first usable rogue guild courtyard.',
        1
    )
ON DUPLICATE KEY UPDATE
    target_room_id = VALUES(target_room_id),
    access_keyword = VALUES(access_keyword),
    primer_verb = VALUES(primer_verb),
    pass_sequence = VALUES(pass_sequence),
    exit_keyword = VALUES(exit_keyword),
    notes = VALUES(notes),
    city_name = VALUES(city_name),
    is_active = VALUES(is_active);
