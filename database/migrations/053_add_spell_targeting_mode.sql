ALTER TABLE spells
    ADD COLUMN targeting_mode VARCHAR(32) NOT NULL DEFAULT '' AFTER description;
