UPDATE items
SET base_name = 'wooden coffer'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'wooden coffer';

UPDATE items
SET base_name = 'dented iron box'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'dented iron box';

UPDATE items
SET base_name = 'ornate brass box'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'ornate brass box' AND (base_name IS NULL OR base_name = '');

UPDATE items
SET base_name = 'iron coffer'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'iron coffer' AND (base_name IS NULL OR base_name = '');

UPDATE items
SET base_name = 'small chest'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'small chest' AND (base_name IS NULL OR base_name = '');

UPDATE items
SET base_name = 'medium chest'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'medium chest' AND (base_name IS NULL OR base_name = '');

UPDATE items
SET base_name = 'metal strongbox'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'metal strongbox' AND (base_name IS NULL OR base_name = '');

UPDATE items
SET base_name = 'small steel lockbox'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'small steel lockbox';

UPDATE items
SET base_name = 'heavy steel trunk'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'heavy steel trunk' AND (base_name IS NULL OR base_name = '');

UPDATE items
SET base_name = 'large chest'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'large chest' AND (base_name IS NULL OR base_name = '');

UPDATE items
SET base_name = 'mithril coffer'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'mithril coffer' AND (base_name IS NULL OR base_name = '');

UPDATE items
SET base_name = 'enruned strongbox'
WHERE item_type = 'container' AND is_template = 1 AND LOWER(short_name) = 'enruned strongbox' AND (base_name IS NULL OR base_name = '');

UPDATE picking_queue pq
JOIN items i
  ON i.item_type = 'container'
 AND i.is_template = 1
 AND LOWER(i.short_name) COLLATE utf8mb4_unicode_ci = LOWER(pq.item_short_name) COLLATE utf8mb4_unicode_ci
SET pq.item_id = i.id,
    pq.item_data = JSON_SET(
        pq.item_data,
        '$.item_id', i.id,
        '$.container_type', COALESCE(NULLIF(i.container_type, ''), 'treasure'),
        '$.base_name', COALESCE(NULLIF(i.base_name, ''), LOWER(i.short_name))
    )
WHERE pq.item_id = 0;
