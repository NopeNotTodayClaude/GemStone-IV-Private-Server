CREATE TABLE IF NOT EXISTS character_hotbar_slots (
    character_id INT(10) UNSIGNED NOT NULL,
    slot_index TINYINT UNSIGNED NOT NULL,
    category_key VARCHAR(64) NOT NULL,
    action_key VARCHAR(128) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id, slot_index),
    CONSTRAINT fk_hotbar_character
        FOREIGN KEY (character_id) REFERENCES characters(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_hotbar_character ON character_hotbar_slots (character_id);
