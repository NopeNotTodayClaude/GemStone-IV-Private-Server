-- 050_add_beastmen_seals.sql
-- Run:
--   mysql --protocol=TCP --skip-ssl -u root gemstone_dev < database/migrations/050_add_beastmen_seals.sql

INSERT IGNORE INTO items (
    name,
    short_name,
    noun,
    base_name,
    article,
    item_type,
    is_template,
    is_stackable,
    weight,
    value,
    description
) VALUES (
    'a Beastmen Seal',
    'beastmen seal',
    'seal',
    'seal',
    'a',
    'seal',
    1,
    1,
    0,
    0,
    'A weightless Beastmen Seal stamped with a harsh tribal brand.'
);
