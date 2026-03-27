-- 021_add_fletching_basics.sql
-- Starter fletching material templates + stocking for existing fletcher shops.

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a smooth branch', 'smooth branch', 'branch', 'a', 'crafting', 1, 0,
    1.00, 25, 'wood',
    'A smooth branch suitable for cutting into arrow shafts.',
    'The branch has already been trimmed clean enough for a novice fletcher to work.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'smooth branch' AND noun = 'branch'
);

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'an arrow shaft', 'arrow shaft', 'shaft', 'an', 'crafting', 1, 0,
    0.10, 15, 'wood',
    'A straight wooden shaft intended for arrow-making work.',
    'The shaft is plain and unfinished, ready for further fletching work.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'arrow shaft' AND noun = 'shaft'
);

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a bottle of fletching glue', 'bottle of fletching glue', 'glue', 'a', 'crafting', 1, 0,
    0.25, 60, 'resin',
    'A stoppered bottle filled with sticky fletching glue.',
    'The bottle holds a tacky adhesive used to fix feathers to a shaft.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'bottle of fletching glue' AND noun = 'glue'
);

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, material, description, examine_text
)
SELECT
    'a bundle of goose fletchings', 'bundle of goose fletchings', 'fletching', 'a', 'crafting', 1, 0,
    0.10, 45, 'feather',
    'A neatly tied bundle of trimmed goose fletchings.',
    'The feathers have already been matched and cut for arrow work.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'bundle of goose fletchings' AND noun = 'fletching'
);

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN rooms r ON r.id = s.room_id
JOIN items i ON i.short_name = 'smooth branch'
WHERE r.tags_json LIKE '%"fletcher"%'
  AND NOT EXISTS (
      SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id
  );

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN rooms r ON r.id = s.room_id
JOIN items i ON i.short_name = 'bottle of fletching glue'
WHERE r.tags_json LIKE '%"fletcher"%'
  AND NOT EXISTS (
      SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id
  );

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN rooms r ON r.id = s.room_id
JOIN items i ON i.short_name = 'bundle of goose fletchings'
WHERE r.tags_json LIKE '%"fletcher"%'
  AND NOT EXISTS (
      SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id
  );

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN rooms r ON r.id = s.room_id
JOIN items i ON i.id = 1
WHERE r.tags_json LIKE '%"fletcher"%'
  AND NOT EXISTS (
      SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id
  );

INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval)
SELECT s.id, i.id, -1, 5, 3600
FROM shops s
JOIN rooms r ON r.id = s.room_id
JOIN items i ON i.id = 10
WHERE r.tags_json LIKE '%"fletcher"%'
  AND NOT EXISTS (
      SELECT 1 FROM shop_inventory si WHERE si.shop_id = s.id AND si.item_id = i.id
  );
