ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS starting_room_id INT UNSIGNED DEFAULT NULL
    AFTER current_room_id;
