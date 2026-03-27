-- Rogue guildmaster workflows, task vouchers, and richer invite tracking.

ALTER TABLE character_guild_access
    ADD COLUMN IF NOT EXISTS invited_by_character_id INT UNSIGNED DEFAULT NULL AFTER invited_by_template_id,
    ADD COLUMN IF NOT EXISTS password_shared_at DATETIME DEFAULT NULL AFTER invited_by_character_id;

SET @fk_inviter_exists := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'character_guild_access'
      AND CONSTRAINT_NAME = 'fk_guildaccesschar_inviter'
);
SET @sql := IF(
    @fk_inviter_exists = 0,
    'ALTER TABLE character_guild_access ADD CONSTRAINT fk_guildaccesschar_inviter FOREIGN KEY (invited_by_character_id) REFERENCES characters(id) ON DELETE SET NULL',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

ALTER TABLE guild_ledger
    MODIFY COLUMN entry_type ENUM('join','invite','initiate','dues','checkin','resign','promotion','task','voucher','nominate','guildmaster') NOT NULL;

CREATE TABLE IF NOT EXISTS guild_guildmaster_nominations (
    guild_id               VARCHAR(32)      NOT NULL,
    nominee_character_id   INT UNSIGNED     NOT NULL,
    nominator_character_id INT UNSIGNED     NOT NULL,
    status                 ENUM('active','used','revoked') NOT NULL DEFAULT 'active',
    notes                  TEXT             DEFAULT NULL,
    nominated_at           DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at                DATETIME         DEFAULT NULL,
    PRIMARY KEY (guild_id, nominee_character_id, nominator_character_id),
    KEY idx_guildnom_nominee (nominee_character_id),
    KEY idx_guildnom_nominator (nominator_character_id),
    CONSTRAINT fk_guildnom_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE,
    CONSTRAINT fk_guildnom_nominee FOREIGN KEY (nominee_character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildnom_nominator FOREIGN KEY (nominator_character_id)
        REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

INSERT INTO guild_task_definitions (
    guild_id, skill_name, task_code, title, description, objective_event,
    required_count, base_points, min_rank, max_rank, practice_room_id,
    requires_guild_authority, is_active
) VALUES
    ('rogue', 'Sweep', 'sweep_live', 'Sweep Opponents', 'Put an opponent on the ground with a clean sweep.', 'sweep_success', 2, 2, 0, NULL, NULL, 0, 1),
    ('rogue', 'Subdue', 'subdue_live', 'Subdue Opponents', 'Disable a foe from hiding with a controlled subdue.', 'subdue_success', 2, 2, 0, NULL, NULL, 0, 1),
    ('rogue', 'Stun Maneuvers', 'stun_live', 'Stunned Recovery', 'Use STUNMAN to act cleanly through a stun.', 'stunman_success', 2, 2, 0, NULL, NULL, 0, 1),
    ('rogue', 'Rogue Gambits', 'gambit_live', 'Divert Targets', 'Use rogue gambits to throw an opponent off balance.', 'rgambit_success', 2, 2, 0, NULL, NULL, 0, 1)
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    description = VALUES(description),
    objective_event = VALUES(objective_event),
    required_count = VALUES(required_count),
    base_points = VALUES(base_points),
    min_rank = VALUES(min_rank),
    max_rank = VALUES(max_rank),
    practice_room_id = VALUES(practice_room_id),
    requires_guild_authority = VALUES(requires_guild_authority),
    is_active = VALUES(is_active);
