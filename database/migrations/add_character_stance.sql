ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS stance VARCHAR(16) NOT NULL DEFAULT 'neutral'
    AFTER position;
