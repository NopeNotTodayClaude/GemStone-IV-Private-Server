-- =============================================================
-- 017_add_forage_system.sql
--
-- Shared room-slot depletion keyed by LICH room id, plus bulk seeding
-- of forageable item templates from rooms.tags_json.
--
-- Run with:
--   mysql --ssl=0 -u root gemstone_dev < database/migrations/017_add_forage_system.sql
-- =============================================================

USE gemstone_dev;

CREATE TABLE IF NOT EXISTS forage_room_depletions (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    room_lich_uid   BIGINT UNSIGNED NOT NULL,
    consumed_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    regen_seconds   SMALLINT UNSIGNED NOT NULL,
    INDEX idx_room_lich_uid (room_lich_uid),
    INDEX idx_room_regen (room_lich_uid, consumed_at)
) ENGINE=InnoDB;

-- Canonical GS herbs that currently exist only as potion/root mismatches.
INSERT INTO items (
    name, short_name, noun, article, item_type, is_template,
    weight, value, herb_heal_type, herb_heal_amount, herb_heal_severity,
    description, lore_text
)
SELECT
    'some bolmara lichen', 'bolmara lichen', 'lichen', 'some', 'herb', 1,
    1, 500, herb_heal_type, herb_heal_amount, herb_heal_severity,
    'some bolmara lichen',
    lore_text
FROM items src
WHERE LOWER(src.short_name) = 'bolmara potion'
  AND NOT EXISTS (SELECT 1 FROM items dst WHERE LOWER(dst.short_name) = 'bolmara lichen');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template,
    weight, value, herb_heal_type, herb_heal_amount, herb_heal_severity,
    description, lore_text
)
SELECT
    'some brostheras grass', 'brostheras grass', 'grass', 'some', 'herb', 1,
    1, 900, herb_heal_type, herb_heal_amount, herb_heal_severity,
    'some brostheras grass',
    lore_text
FROM items src
WHERE LOWER(src.short_name) = 'brostheras potion'
  AND NOT EXISTS (SELECT 1 FROM items dst WHERE LOWER(dst.short_name) = 'brostheras grass');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template,
    weight, value, herb_heal_type, herb_heal_amount, herb_heal_severity,
    description, lore_text
)
SELECT
    'some rose-marrow root', 'rose-marrow root', 'root', 'some', 'herb', 1,
    1, 200, herb_heal_type, herb_heal_amount, herb_heal_severity,
    'some rose-marrow root',
    lore_text
FROM items src
WHERE LOWER(src.short_name) = 'rose-marrow potion'
  AND NOT EXISTS (SELECT 1 FROM items dst WHERE LOWER(dst.short_name) = 'rose-marrow root');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template,
    weight, value, herb_heal_type, herb_heal_amount, herb_heal_severity,
    description, lore_text
)
SELECT
    'some wingstem root', 'wingstem root', 'root', 'some', 'herb', 1,
    1, 700, herb_heal_type, herb_heal_amount, herb_heal_severity,
    'some wingstem root',
    lore_text
FROM items src
WHERE LOWER(src.short_name) = 'wingstem potion'
  AND NOT EXISTS (SELECT 1 FROM items dst WHERE LOWER(dst.short_name) = 'wingstem root');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template,
    weight, value, herb_heal_type, herb_heal_amount, herb_heal_severity,
    description, lore_text
)
SELECT
    'some bur-clover root', 'bur-clover root', 'root', 'some', 'herb', 1,
    1, 500, herb_heal_type, herb_heal_amount, herb_heal_severity,
    'some bur-clover root',
    lore_text
FROM items src
WHERE LOWER(src.short_name) = 'bur-clover potion'
  AND NOT EXISTS (SELECT 1 FROM items dst WHERE LOWER(dst.short_name) = 'bur-clover root');

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template,
    weight, value, description
)
SELECT
    CASE seeded.article
        WHEN 'some' THEN CONCAT('some ', seeded.short_name)
        WHEN 'an'   THEN CONCAT('an ', seeded.short_name)
        ELSE CONCAT('a ', seeded.short_name)
    END AS name,
    seeded.short_name,
    seeded.noun,
    seeded.article,
    'forage',
    1,
    1,
    25,
    CONCAT('A forageable specimen of ', seeded.short_name, '.')
FROM (
    SELECT DISTINCT
        TRIM(
            CASE
                WHEN LOWER(raw_tag) LIKE 'some %' THEN SUBSTRING(raw_tag, 6)
                WHEN LOWER(raw_tag) LIKE 'an %'   THEN SUBSTRING(raw_tag, 4)
                WHEN LOWER(raw_tag) LIKE 'a %'    THEN SUBSTRING(raw_tag, 3)
                ELSE raw_tag
            END
        ) AS short_name,
        LOWER(
            TRIM(
                CASE
                    WHEN LOWER(raw_tag) LIKE 'some %' THEN SUBSTRING(raw_tag, 6)
                    WHEN LOWER(raw_tag) LIKE 'an %'   THEN SUBSTRING(raw_tag, 4)
                    WHEN LOWER(raw_tag) LIKE 'a %'    THEN SUBSTRING(raw_tag, 3)
                    ELSE raw_tag
                END
            )
        ) AS short_name_lower,
        SUBSTRING_INDEX(
            TRIM(
                CASE
                    WHEN LOWER(raw_tag) LIKE 'some %' THEN SUBSTRING(raw_tag, 6)
                    WHEN LOWER(raw_tag) LIKE 'an %'   THEN SUBSTRING(raw_tag, 4)
                    WHEN LOWER(raw_tag) LIKE 'a %'    THEN SUBSTRING(raw_tag, 3)
                    ELSE raw_tag
                END
            ),
            ' ',
            -1
        ) AS noun,
        CASE
            WHEN LOWER(raw_tag) LIKE 'some %' THEN 'some'
            WHEN LOWER(
                TRIM(
                    CASE
                        WHEN LOWER(raw_tag) LIKE 'some %' THEN SUBSTRING(raw_tag, 6)
                        WHEN LOWER(raw_tag) LIKE 'an %'   THEN SUBSTRING(raw_tag, 4)
                        WHEN LOWER(raw_tag) LIKE 'a %'    THEN SUBSTRING(raw_tag, 3)
                        ELSE raw_tag
                    END
                )
            ) REGEXP '^(handful|sprig|stalk|stem|branch|cluster|ear) of '
                THEN 'a'
            WHEN LOWER(
                TRIM(
                    CASE
                        WHEN LOWER(raw_tag) LIKE 'some %' THEN SUBSTRING(raw_tag, 6)
                        WHEN LOWER(raw_tag) LIKE 'an %'   THEN SUBSTRING(raw_tag, 4)
                        WHEN LOWER(raw_tag) LIKE 'a %'    THEN SUBSTRING(raw_tag, 3)
                        ELSE raw_tag
                    END
                )
            ) REGEXP '(berries|grapes|sticks|leaves|flowers|fronds|needles|seeds|grass|moss|lichen|bark|parsley|broccoli|garlic|ramie|hemp|celery|lavender|scallions|chives)$'
                THEN 'some'
            WHEN LOWER(
                LEFT(
                    TRIM(
                        CASE
                            WHEN LOWER(raw_tag) LIKE 'some %' THEN SUBSTRING(raw_tag, 6)
                            WHEN LOWER(raw_tag) LIKE 'an %'   THEN SUBSTRING(raw_tag, 4)
                            WHEN LOWER(raw_tag) LIKE 'a %'    THEN SUBSTRING(raw_tag, 3)
                            ELSE raw_tag
                        END
                    ),
                    1
                )
            ) REGEXP '[aeiou]'
                THEN 'an'
            ELSE 'a'
        END AS article
    FROM (
        SELECT DISTINCT TRIM(JSON_UNQUOTE(j.val)) AS raw_tag
        FROM rooms r
        JOIN JSON_TABLE(r.tags_json, '$[*]' COLUMNS (val JSON PATH '$')) j
        WHERE JSON_VALID(r.tags_json)
          AND TRIM(JSON_UNQUOTE(j.val)) <> ''
          AND JSON_UNQUOTE(j.val) NOT LIKE 'meta:%'
          AND JSON_UNQUOTE(j.val) NOT IN ('no forageables', 'gone')
    ) raw
    WHERE
        LOWER(raw_tag) LIKE 'sprig of %'
        OR LOWER(raw_tag) LIKE 'stalk of %'
        OR LOWER(raw_tag) LIKE 'stem of %'
        OR LOWER(raw_tag) LIKE 'branch of %'
        OR LOWER(raw_tag) LIKE 'cluster of %'
        OR LOWER(raw_tag) LIKE 'handful of %'
        OR LOWER(raw_tag) LIKE 'ear of %'
        OR LOWER(raw_tag) REGEXP '(leaf|leaves|root|roots|mushroom|mushrooms|flower|flowers|blossom|blossoms|bloom|blooms|twig|twigs|berry|berries|fruit|fruits|grass|moss|lichen|bark|vine|bean|beans|seed|seeds|fern|frond|fronds|bulb|clove|cloves|petal|petals|reed|reeds|cabbage|broccoli|chard|parsley|celery|onion|onions|garlic|leek|shallot|squash|zucchini|apple|pear|kiwi|grapes|grape|strawberry|strawberries|cranberry|cranberries|mulberries|blueberries|gooseberry|gooseberries|cherry|cherries|rose|lily|daisy|orchid|aster|pansy|violet|jasmine|ivy|teaberry|primrose|buttercup|baneberry|honeysuckle|cardamom|nutmeg|peppercorn|anise|lettuce|ginger|lavender|kerria|pumpkin|tomato|potato|sage|oleander|plumeria|heliconia|hibiscus|hydrangea|petunia|passionflower|lantana|iceblossom|dianthus|needles|skin|acorn|spine|weed|wort|orange|corn|plum|fig|hemp|ramie|sunflower|dandelion|phlox|dragonstalk|burdock|monkeyflower|plantain|alyssum|larkspur|columbine|tarragon|sargassum|begonia|wisteria|protea|agapanthus|hellebore|lace|rhubarb|almonds|pepper|catnip|dill|beechnut|cone|pecans|cilantro|carrot|thorn|shockroot|yuzu|pods|guava|gardenia|peach|chestnut|lychee|olive|mango|papaya|pineapple|basil|thyme|parsnip|peony|anemone|turnip|spinach|quenepas|verbena|balm|oregano|beet|edelweiss|watermelon|lime|apricot|coconut|grapefruit|seaweed|radish|melon|frostflower|deathblossom|delphira|tulip|scapes|stalk|stems|stem|bud|buds|nut|nuts|lemon|arugula|cane|artichoke|vinca|crocus|poppy|daffodil|carnation|alpestris|thrift|feverfew|fritillary|eggplant|oats|kale|date|banana|rosehip|geranium|honeydew|direbloom|mistbloom|amaranth|sedge|spurge|gorse|toadstool|boll|plume|fan)$'
        OR LOWER(raw_tag) IN (
            'imaera''s lace',
            'chives',
            'scallions',
            'fresh lemongrass',
            'motherwort',
            'murdroot',
            'murkweed',
            'sticks',
            'stick',
            'raw almonds',
            'fresh catnip',
            'mistweed',
            'wiregrass',
            'agave heart',
            'bamboo cane'
        )
) seeded
LEFT JOIN items existing
    ON LOWER(existing.short_name) = seeded.short_name_lower
WHERE existing.id IS NULL
  AND seeded.short_name <> '';

SELECT
    (SELECT COUNT(*) FROM forage_room_depletions) AS forage_room_depletion_rows,
    (SELECT COUNT(*) FROM items WHERE item_type = 'forage') AS forage_item_templates;
