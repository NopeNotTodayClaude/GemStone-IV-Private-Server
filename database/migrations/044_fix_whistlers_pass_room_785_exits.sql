INSERT INTO room_exits (room_id, direction, target_room_id, exit_verb, is_hidden, is_special, search_dc)
SELECT 785, 'north', 784, NULL, 0, 0, 0
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1
    FROM room_exits
    WHERE room_id = 785
      AND direction = 'north'
);

INSERT INTO room_exits (room_id, direction, target_room_id, exit_verb, is_hidden, is_special, search_dc)
SELECT 785, 'west', 786, NULL, 0, 0, 0
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1
    FROM room_exits
    WHERE room_id = 785
      AND direction = 'west'
);
