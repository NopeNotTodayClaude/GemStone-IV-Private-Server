-- Guild progression, rogue access gate, and data-driven task definitions.

ALTER TABLE guild_definitions
    ADD COLUMN IF NOT EXISTS progression_multiplier DECIMAL(8,2) NOT NULL DEFAULT 20.00 AFTER has_guildmaster;

ALTER TABLE guild_rank_definitions
    ADD COLUMN IF NOT EXISTS min_total_skill_ranks SMALLINT UNSIGNED NOT NULL DEFAULT 0 AFTER description,
    ADD COLUMN IF NOT EXISTS min_distinct_skills TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER min_total_skill_ranks;

ALTER TABLE character_guild_membership
    ADD COLUMN IF NOT EXISTS guild_training_points INT UNSIGNED NOT NULL DEFAULT 0 AFTER vouchers,
    ADD COLUMN IF NOT EXISTS active_skill_name VARCHAR(64) DEFAULT NULL AFTER guild_training_points,
    ADD COLUMN IF NOT EXISTS last_task_at DATETIME DEFAULT NULL AFTER next_checkin_due_at;

CREATE TABLE IF NOT EXISTS guild_access_points (
    id                   INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    guild_id             VARCHAR(32)       NOT NULL,
    city_name            VARCHAR(64)       DEFAULT NULL,
    entry_room_id        INT UNSIGNED      NOT NULL,
    target_room_id       INT UNSIGNED      NOT NULL,
    access_keyword       VARCHAR(32)       NOT NULL DEFAULT 'door',
    primer_verb          VARCHAR(16)       NOT NULL DEFAULT 'lean',
    pass_sequence        VARCHAR(255)      DEFAULT NULL,
    exit_keyword         VARCHAR(32)       NOT NULL DEFAULT 'out',
    notes                TEXT              DEFAULT NULL,
    is_active            TINYINT(1)        NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_guild_access_roompair (guild_id, entry_room_id, target_room_id),
    KEY idx_guild_access_entry (entry_room_id),
    KEY idx_guild_access_target (target_room_id),
    CONSTRAINT fk_guildaccess_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS character_guild_access (
    character_id         INT UNSIGNED      NOT NULL,
    guild_id             VARCHAR(32)       NOT NULL,
    is_invited           TINYINT(1)        NOT NULL DEFAULT 0,
    password_known       TINYINT(1)        NOT NULL DEFAULT 0,
    invited_at           DATETIME          DEFAULT NULL,
    invited_by_template_id VARCHAR(64)     DEFAULT NULL,
    sequence_step        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    sequence_room_id     INT UNSIGNED      DEFAULT NULL,
    sequence_started_at  DATETIME          DEFAULT NULL,
    updated_at           DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id, guild_id),
    CONSTRAINT fk_guildaccesschar_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildaccesschar_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

ALTER TABLE character_guild_skills
    ADD COLUMN IF NOT EXISTS last_trained_at DATETIME DEFAULT NULL AFTER is_mastered;

CREATE TABLE IF NOT EXISTS guild_skill_definitions (
    guild_id             VARCHAR(32)       NOT NULL,
    skill_name           VARCHAR(64)       NOT NULL,
    display_name         VARCHAR(64)       NOT NULL,
    skill_order          SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    max_rank             SMALLINT UNSIGNED NOT NULL DEFAULT 63,
    points_per_rank      INT UNSIGNED      NOT NULL DEFAULT 100,
    practice_only        TINYINT(1)        NOT NULL DEFAULT 0,
    is_active            TINYINT(1)        NOT NULL DEFAULT 1,
    PRIMARY KEY (guild_id, skill_name),
    KEY idx_guildskillsdefs_order (guild_id, skill_order),
    CONSTRAINT fk_guildskilldefs_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

ALTER TABLE character_guild_tasks
    ADD COLUMN IF NOT EXISTS task_code VARCHAR(64) DEFAULT NULL AFTER skill_name,
    ADD COLUMN IF NOT EXISTS objective_event VARCHAR(64) DEFAULT NULL AFTER task_text,
    ADD COLUMN IF NOT EXISTS target_count SMALLINT UNSIGNED NOT NULL DEFAULT 1 AFTER objective_event,
    ADD COLUMN IF NOT EXISTS progress_count SMALLINT UNSIGNED NOT NULL DEFAULT 0 AFTER target_count,
    ADD COLUMN IF NOT EXISTS award_points INT UNSIGNED NOT NULL DEFAULT 0 AFTER progress_count;

ALTER TABLE character_guild_tasks
    MODIFY COLUMN status ENUM('assigned','ready','complete','abandoned') NOT NULL DEFAULT 'assigned';

CREATE TABLE IF NOT EXISTS guild_task_definitions (
    id                   INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    guild_id             VARCHAR(32)       NOT NULL,
    skill_name           VARCHAR(64)       NOT NULL,
    task_code            VARCHAR(64)       NOT NULL,
    title                VARCHAR(64)       NOT NULL,
    description          TEXT              DEFAULT NULL,
    objective_event      VARCHAR(64)       NOT NULL,
    required_count       SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    base_points          INT UNSIGNED      NOT NULL DEFAULT 1,
    min_rank             SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    max_rank             SMALLINT UNSIGNED DEFAULT NULL,
    practice_room_id     INT UNSIGNED      DEFAULT NULL,
    requires_guild_authority TINYINT(1)    NOT NULL DEFAULT 0,
    is_active            TINYINT(1)        NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_guild_task_code (guild_id, task_code),
    KEY idx_guildtaskdefs_skill (guild_id, skill_name, min_rank),
    CONSTRAINT fk_guildtaskdefs_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

UPDATE guild_definitions
SET progression_multiplier = 20.00
WHERE guild_id = 'rogue';

INSERT INTO guild_rank_definitions (
    guild_id, rank_level, rank_name, description, min_total_skill_ranks, min_distinct_skills
) VALUES
    ('rogue', 1, 'Member', 'A recognized member of the Rogue Guild.', 0, 0),
    ('rogue', 2, 'Initiate', 'An initiated rogue making steady progress.', 8, 2),
    ('rogue', 3, 'Apprentice', 'An apprentice rogue trusted with wider training.', 16, 3),
    ('rogue', 4, 'Journeyman', 'A guild rogue with practical field experience.', 24, 3),
    ('rogue', 5, 'Senior Journeyman', 'A rogue who has diversified training beyond the basics.', 36, 4),
    ('rogue', 6, 'Expert', 'A practiced rogue with well-developed guild skills.', 48, 4),
    ('rogue', 7, 'Senior Expert', 'A rogue trusted with advanced guild work.', 60, 5),
    ('rogue', 8, 'Master', 'A master rogue recognized across the guild.', 72, 5),
    ('rogue', 9, 'Senior Master', 'A senior master who has rounded out every major track.', 84, 6),
    ('rogue', 10, 'Grandmaster', 'A grandmaster-level rogue by guild standards.', 96, 6)
ON DUPLICATE KEY UPDATE
    rank_name = VALUES(rank_name),
    description = VALUES(description),
    min_total_skill_ranks = VALUES(min_total_skill_ranks),
    min_distinct_skills = VALUES(min_distinct_skills);

INSERT INTO guild_access_points (
    guild_id, city_name, entry_room_id, target_room_id, access_keyword,
    primer_verb, pass_sequence, exit_keyword, notes
) VALUES
    (
        'rogue', 'Ta''Vaalor', 17806, 18348, 'door',
        'lean', 'pull,pull,slap,rub,rub,push,turn', 'out',
        'Ta''Vaalor rogue guild entry between the alley and hidden basement hall, keyed to the documented rogue pass sequence.'
    )
ON DUPLICATE KEY UPDATE
    access_keyword = VALUES(access_keyword),
    primer_verb = VALUES(primer_verb),
    pass_sequence = VALUES(pass_sequence),
    exit_keyword = VALUES(exit_keyword),
    city_name = VALUES(city_name),
    notes = VALUES(notes),
    is_active = 1;

INSERT INTO character_guild_access (
    character_id, guild_id, is_invited, password_known, invited_at,
    invited_by_template_id, sequence_step, sequence_room_id, sequence_started_at
)
SELECT
    character_id, guild_id, 1, 1, NOW(),
    NULL, 0, NULL, NULL
FROM character_guild_membership
WHERE guild_id = 'rogue' AND status = 'active'
ON DUPLICATE KEY UPDATE
    is_invited = VALUES(is_invited),
    password_known = VALUES(password_known),
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO guild_skill_definitions (
    guild_id, skill_name, display_name, skill_order, max_rank, points_per_rank, practice_only, is_active
) VALUES
    ('rogue', 'Sweep', 'Sweep', 1, 63, 100, 1, 1),
    ('rogue', 'Subdue', 'Subdue', 2, 63, 100, 1, 1),
    ('rogue', 'Stun Maneuvers', 'Stun Maneuvers', 3, 63, 100, 1, 1),
    ('rogue', 'Lock Mastery', 'Lock Mastery', 4, 63, 100, 0, 1),
    ('rogue', 'Cheapshots', 'Cheapshots', 5, 63, 100, 0, 1),
    ('rogue', 'Rogue Gambits', 'Rogue Gambits', 6, 63, 100, 1, 1)
ON DUPLICATE KEY UPDATE
    display_name = VALUES(display_name),
    skill_order = VALUES(skill_order),
    max_rank = VALUES(max_rank),
    points_per_rank = VALUES(points_per_rank),
    practice_only = VALUES(practice_only),
    is_active = VALUES(is_active);

INSERT INTO guild_task_definitions (
    guild_id, skill_name, task_code, title, description, objective_event,
    required_count, base_points, min_rank, max_rank, practice_room_id,
    requires_guild_authority, is_active
) VALUES
    ('rogue', 'Sweep', 'sweep_practice', 'Sweep Drill', 'Work through the guild''s sweep drill in the Ta''Vaalor hall.', 'guild_practice', 3, 2, 0, NULL, 18348, 1, 1),
    ('rogue', 'Subdue', 'subdue_practice', 'Subdue Drill', 'Practice controlled takedowns in the guild hall.', 'guild_practice', 3, 2, 0, NULL, 18348, 1, 1),
    ('rogue', 'Stun Maneuvers', 'stun_practice', 'Stun Maneuver Drill', 'Work through the guild''s stun maneuver forms.', 'guild_practice', 3, 2, 0, NULL, 18348, 1, 1),
    ('rogue', 'Lock Mastery', 'lock_detect', 'Detect Locks', 'Carefully examine and assess lockwork in the field.', 'detect_success', 3, 1, 0, NULL, NULL, 0, 1),
    ('rogue', 'Lock Mastery', 'lock_disarm', 'Disarm Traps', 'Neutralize detected box traps without triggering them.', 'disarm_success', 1, 2, 0, NULL, NULL, 0, 1),
    ('rogue', 'Lock Mastery', 'lock_pick', 'Pick Locks', 'Open a locked box cleanly in the field.', 'pick_success', 1, 2, 0, NULL, NULL, 0, 1),
    ('rogue', 'Cheapshots', 'cheap_hide', 'Shadowing Drill', 'Use stealth to disappear cleanly from sight.', 'hide_success', 3, 1, 0, NULL, NULL, 0, 1),
    ('rogue', 'Cheapshots', 'cheap_ambush', 'Cheapshot Strike', 'Ambush a target cleanly from hiding.', 'ambush_success', 2, 2, 0, NULL, NULL, 0, 1),
    ('rogue', 'Rogue Gambits', 'gambit_practice', 'Gambit Drill', 'Practice the timing and nerve of rogue gambits in the hall.', 'guild_practice', 3, 2, 0, NULL, 18348, 1, 1)
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
