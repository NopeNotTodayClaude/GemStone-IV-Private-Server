USE gemstone_dev;

CREATE TABLE IF NOT EXISTS character_pet_progress (
    character_id        INT(10) UNSIGNED NOT NULL,
    quest_state         ENUM('locked','offered','accepted','completed') NOT NULL DEFAULT 'locked',
    sprite_name         VARCHAR(64) NOT NULL DEFAULT 'Twillip',
    first_pet_claimed   TINYINT(1) NOT NULL DEFAULT 0,
    path_unlocked       TINYINT(1) NOT NULL DEFAULT 0,
    active_pet_id       INT(10) UNSIGNED NULL,
    last_sprite_nag_at  BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    last_shop_nag_at    BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    room_moves_since_nag SMALLINT(5) UNSIGNED NOT NULL DEFAULT 0,
    accepted_at         DATETIME NULL,
    completed_at        DATETIME NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id),
    CONSTRAINT fk_pet_progress_character
        FOREIGN KEY (character_id) REFERENCES characters(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS character_pets (
    id                  INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
    character_id        INT(10) UNSIGNED NOT NULL,
    species_key         VARCHAR(64) NOT NULL,
    pet_name            VARCHAR(64) NOT NULL,
    pet_level           TINYINT(3) UNSIGNED NOT NULL DEFAULT 1,
    pet_xp              INT(10) UNSIGNED NOT NULL DEFAULT 0,
    is_active           TINYINT(1) NOT NULL DEFAULT 0,
    is_deleted          TINYINT(1) NOT NULL DEFAULT 0,
    is_released         TINYINT(1) NOT NULL DEFAULT 0,
    image_key           VARCHAR(64) NULL,
    last_fed_at         BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    last_random_emote_at BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    last_state_emote_at BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    extra_state_json    TEXT NULL,
    acquired_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_character_pet_name (character_id, pet_name),
    KEY idx_character_pets_character (character_id),
    KEY idx_character_pets_active (character_id, is_active),
    CONSTRAINT fk_character_pets_character
        FOREIGN KEY (character_id) REFERENCES characters(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS character_pet_abilities (
    id                  INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
    pet_id              INT(10) UNSIGNED NOT NULL,
    ability_key         VARCHAR(64) NOT NULL,
    charges_current     SMALLINT(5) UNSIGNED NOT NULL DEFAULT 0,
    cooldown_until      BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    last_triggered_at   BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    extra_state_json    TEXT NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_pet_ability (pet_id, ability_key),
    CONSTRAINT fk_pet_abilities_pet
        FOREIGN KEY (pet_id) REFERENCES character_pets(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS character_pet_equipment (
    id                  INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
    pet_id              INT(10) UNSIGNED NOT NULL,
    slot_name           VARCHAR(32) NOT NULL,
    inventory_item_id   INT(10) UNSIGNED NULL,
    item_snapshot_json  TEXT NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_pet_equipment_slot (pet_id, slot_name),
    CONSTRAINT fk_pet_equipment_pet
        FOREIGN KEY (pet_id) REFERENCES character_pets(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE character_pet_progress
    ADD CONSTRAINT fk_pet_progress_active_pet
    FOREIGN KEY (active_pet_id) REFERENCES character_pets(id)
    ON DELETE SET NULL;

INSERT INTO items (
    name, short_name, base_name, noun, article, item_type,
    is_template, is_stackable, material, weight, value,
    description, examine_text, lore_text
)
SELECT
    'a shimmer crumb', 'shimmer crumb', 'shimmer crumb', 'crumb', 'a', 'consumable',
    1, 1, 'sugar', 0.1, 150,
    'A tiny sugared morsel that leaves a faint glitter across the tongue.',
    'The crumb sparkles with pastel sugar and smells faintly of warm vanilla.',
    'A beginner treat meant to gently reward a young companion.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'shimmer crumb' AND is_template = 1
);

INSERT INTO items (
    name, short_name, base_name, noun, article, item_type,
    is_template, is_stackable, material, weight, value,
    description, examine_text, lore_text
)
SELECT
    'a moonmilk biscuit', 'moonmilk biscuit', 'moonmilk biscuit', 'biscuit', 'a', 'consumable',
    1, 1, 'flour', 0.15, 500,
    'A pale biscuit baked for companion training and quiet field rewards.',
    'The biscuit is stamped with a tiny crescent moon and dusted with lavender sugar.',
    'A steady mid-grade treat favored by patient trainers.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'moonmilk biscuit' AND is_template = 1
);

INSERT INTO items (
    name, short_name, base_name, noun, article, item_type,
    is_template, is_stackable, material, weight, value,
    description, examine_text, lore_text
)
SELECT
    'a starpetal chew', 'starpetal chew', 'starpetal chew', 'chew', 'a', 'consumable',
    1, 1, 'candy', 0.15, 1500,
    'A glossy chew infused with bright floral sugar and patient magic.',
    'The chewy sweet glimmers with tiny star-shaped flakes that never quite melt.',
    'The house standard for serious but sustainable companion training.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'starpetal chew' AND is_template = 1
);

INSERT INTO items (
    name, short_name, base_name, noun, article, item_type,
    is_template, is_stackable, material, weight, value,
    description, examine_text, lore_text
)
SELECT
    'a velvet comet tart', 'velvet comet tart', 'velvet comet tart', 'tart', 'a', 'consumable',
    1, 1, 'pastry', 0.2, 4000,
    'A rich sugared tart reserved for ambitious training sessions.',
    'Purple glaze curls over the tart in a comet-tail swirl that shimmers in the light.',
    'A premium reward that can turn a quiet lesson into a breakthrough.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'velvet comet tart' AND is_template = 1
);

INSERT INTO items (
    name, short_name, base_name, noun, article, item_type,
    is_template, is_stackable, material, weight, value,
    description, examine_text, lore_text
)
SELECT
    'an aurora heart treat', 'aurora heart treat', 'aurora heart treat', 'treat', 'an', 'consumable',
    1, 1, 'sugar', 0.2, 10000,
    'A jewel-bright luxury treat that hums with affectionate restorative magic.',
    'The heart-shaped sweet glows softly through bands of pink, violet, and silver.',
    'The most extravagant companion treat in the menagerie catalogue.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'aurora heart treat' AND is_template = 1
);

INSERT INTO rooms (
    id, zone_id, title, description, location_name, tags_json, is_safe, is_supernode, is_indoor, terrain_type, climate, terrain, indoor
)
SELECT
    36478, zone_id,
    'Moonwhisker Menagerie, Silver Gallery',
    'Lanternlight drifts through a vaulted boutique lined with floating ribbons, polished perches, and velvet display tables bearing tins of jewel-bright treats.  A softly glowing counter curves through the center of the room, while a wall of enchanted portrait frames cycles through companion likenesses and care notes.',
    'Moonwhisker Menagerie, Silver Gallery',
    JSON_ARRAY('pet_shop'),
    1, 0, 1, 'shop', climate, 'urban', 1
FROM rooms WHERE id = 166
AND NOT EXISTS (SELECT 1 FROM rooms WHERE id = 36478);

INSERT INTO rooms (
    id, zone_id, title, description, location_name, tags_json, is_safe, is_supernode, is_indoor, terrain_type, climate, terrain, indoor
)
SELECT
    36479, zone_id,
    'Moonwhisker Menagerie, Rose Court',
    'Silken pennants in pink and violet drift above low lacquered shelves loaded with treats, collars, and glittering training toys.  A warm perfume of sugar and cedar lingers in the air, and the polished floor reflects a wall of enchanted portraits showing companion species available through the menagerie.',
    'Moonwhisker Menagerie, Rose Court',
    JSON_ARRAY('pet_shop'),
    1, 0, 1, 'shop', climate, 'urban', 1
FROM rooms WHERE id = 3513
AND NOT EXISTS (SELECT 1 FROM rooms WHERE id = 36479);

INSERT INTO rooms (
    id, zone_id, title, description, location_name, tags_json, is_safe, is_supernode, is_indoor, terrain_type, climate, terrain, indoor
)
SELECT
    36480, zone_id,
    'Moonwhisker Menagerie, Lantern Nook',
    'A cozy storefront of polished oak and amber lanterns shelters neatly labeled treat jars, training ledgers, and velvet-lined perches.  Framed sketches of cherished companions cover the walls, each bordered in fine gilt and annotated with a few affectionate notes from prior owners.',
    'Moonwhisker Menagerie, Lantern Nook',
    JSON_ARRAY('pet_shop'),
    1, 0, 1, 'shop', climate, 'urban', 1
FROM rooms WHERE id = 1446
AND NOT EXISTS (SELECT 1 FROM rooms WHERE id = 36480);

INSERT INTO rooms (
    id, zone_id, title, description, location_name, tags_json, is_safe, is_supernode, is_indoor, terrain_type, climate, terrain, indoor
)
SELECT
    36481, zone_id,
    'Moonwhisker Menagerie, Garden Loft',
    'A bright loft above the clearing has been dressed with hanging charms, tiny sleeping nests, and trays of polished training baubles.  The scent of sweet herbs and warm milk drifts through the room, while animated portraits shimmer to life along one wall whenever someone pauses to admire them.',
    'Moonwhisker Menagerie, Garden Loft',
    JSON_ARRAY('pet_shop'),
    1, 0, 1, 'shop', climate, 'urban', 1
FROM rooms WHERE id = 10857
AND NOT EXISTS (SELECT 1 FROM rooms WHERE id = 36481);

INSERT INTO rooms (
    id, zone_id, title, description, location_name, tags_json, is_safe, is_supernode, is_indoor, terrain_type, climate, terrain, indoor
)
SELECT
    36482, zone_id,
    'Moonwhisker Menagerie, Bough Arcade',
    'Curving branch-walls frame a boutique of moss-soft carpets, moonlit glass jars, and suspended silver toys that drift gently through the air.  A series of glowing portrait panels shows available companion breeds, while a low counter offers treat tins, travel gear, and training guidance.',
    'Moonwhisker Menagerie, Bough Arcade',
    JSON_ARRAY('pet_shop'),
    1, 0, 1, 'shop', climate, 'urban', 1
FROM rooms WHERE id = 4649
AND NOT EXISTS (SELECT 1 FROM rooms WHERE id = 36482);

INSERT INTO room_exits (room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc)
SELECT 36478, 'out', NULL, 166, 0, 0, 0
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM room_exits WHERE room_id = 36478 AND direction = 'out');

INSERT INTO room_exits (room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc)
SELECT 36479, 'out', NULL, 3513, 0, 0, 0
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM room_exits WHERE room_id = 36479 AND direction = 'out');

INSERT INTO room_exits (room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc)
SELECT 36480, 'out', NULL, 1446, 0, 0, 0
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM room_exits WHERE room_id = 36480 AND direction = 'out');

INSERT INTO room_exits (room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc)
SELECT 36481, 'out', NULL, 10857, 0, 0, 0
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM room_exits WHERE room_id = 36481 AND direction = 'out');

INSERT INTO room_exits (room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc)
SELECT 36482, 'out', NULL, 4649, 0, 0, 0
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM room_exits WHERE room_id = 36482 AND direction = 'out');
