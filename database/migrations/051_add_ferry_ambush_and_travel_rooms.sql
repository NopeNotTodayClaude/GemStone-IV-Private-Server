-- Ferry overhaul support:
--   * underway travel rooms
--   * ferry anti-bypass exit cleanup
--   * pirate captain hat template

INSERT INTO rooms (
    id, zone_id, title, description, location_name,
    is_safe, is_supernode, terrain_type, climate, terrain, indoor
) VALUES
    (
        36784,
        126,
        'Lake of Fear, Underway Deck',
        'Black water heaves against the broad ferry''s hull while the striped awning snaps overhead and the far pier drifts in and out of the lake mist.',
        'the Lake of Fear',
        1, 0, 'water', 'temperate', 'water', 0
    ),
    (
        36785,
        126,
        'Lake of Fear, Underway Saloon',
        'A cramped saloon crouches beneath the awning, its benches slick with spray and its warped windows giving only broken glimpses of the black lake outside.',
        'the Lake of Fear',
        1, 0, 'water', 'temperate', 'water', 1
    ),
    (
        36786,
        31,
        'Locksmehr River Ferry, Midstream',
        'The narrow ferry groans against the guide rope while river spray lashes the deck and the current claws impatiently at the hull.',
        'the Vipershroud',
        1, 0, 'water', 'temperate', 'water', 0
    )
ON DUPLICATE KEY UPDATE
    zone_id = VALUES(zone_id),
    title = VALUES(title),
    description = VALUES(description),
    location_name = VALUES(location_name),
    is_safe = VALUES(is_safe),
    is_supernode = VALUES(is_supernode),
    terrain_type = VALUES(terrain_type),
    climate = VALUES(climate),
    terrain = VALUES(terrain),
    indoor = VALUES(indoor);

DELETE FROM room_exits
WHERE (room_id = 10117 AND direction = 'out' AND target_room_id = 10119)
   OR (room_id = 10119 AND direction = 'out' AND target_room_id = 10117)
   OR (room_id = 1190 AND direction = 'southwest' AND target_room_id = 1191)
   OR (room_id = 1191 AND direction = 'northeast' AND target_room_id = 1190)
   OR (room_id = 1191 AND direction = 'southwest' AND target_room_id = 1192)
   OR (room_id = 1192 AND direction = 'northeast' AND target_room_id = 1191);

INSERT INTO room_exits (
    room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc
) VALUES
    (36784, 'go_awning', 'go', 36785, 0, 0, 0),
    (36785, 'out', NULL, 36784, 0, 0, 0)
ON DUPLICATE KEY UPDATE
    exit_verb = VALUES(exit_verb),
    target_room_id = VALUES(target_room_id),
    is_hidden = VALUES(is_hidden),
    is_special = VALUES(is_special),
    search_dc = VALUES(search_dc);

INSERT INTO items (
    id, name, short_name, noun, article, item_type, is_template,
    is_stackable, weight, value, enchant_bonus, armor_group, armor_asg,
    defense_bonus, action_penalty, spell_hindrance, worn_location,
    material, color, description, examine_text, lore_text, base_name, display_order
) VALUES (
    7399,
    'a weathered black pirate hat',
    'weathered black pirate hat',
    'hat',
    'a',
    'armor',
    1,
    0,
    1,
    0,
    25,
    'cloth',
    2,
    25,
    0,
    0,
    'head',
    'cloth',
    'black',
    'Salt-stiffened and weather-beaten, the black pirate hat still carries the severe shape and swagger of some dead captain who never learned how to kneel.',
    'The hat is cut from black cloth gone stiff with salt and age.  A frayed inner band suggests it once belonged to someone who spent more nights under storm clouds than under a roof.',
    'Taken from a dead ferryside raider captain, the hat has become a grim badge of surviving the black-water ambush.',
    'weathered black pirate hat',
    65
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    short_name = VALUES(short_name),
    noun = VALUES(noun),
    article = VALUES(article),
    item_type = VALUES(item_type),
    is_template = VALUES(is_template),
    is_stackable = VALUES(is_stackable),
    weight = VALUES(weight),
    value = VALUES(value),
    enchant_bonus = VALUES(enchant_bonus),
    armor_group = VALUES(armor_group),
    armor_asg = VALUES(armor_asg),
    defense_bonus = VALUES(defense_bonus),
    action_penalty = VALUES(action_penalty),
    spell_hindrance = VALUES(spell_hindrance),
    worn_location = VALUES(worn_location),
    material = VALUES(material),
    color = VALUES(color),
    description = VALUES(description),
    examine_text = VALUES(examine_text),
    lore_text = VALUES(lore_text),
    base_name = VALUES(base_name),
    display_order = VALUES(display_order);
