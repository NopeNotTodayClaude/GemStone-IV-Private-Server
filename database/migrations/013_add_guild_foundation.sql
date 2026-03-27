USE gemstone_dev;

CREATE TABLE IF NOT EXISTS guild_definitions (
    guild_id             VARCHAR(32)      NOT NULL,
    profession_id        TINYINT UNSIGNED NOT NULL,
    name                 VARCHAR(64)      NOT NULL,
    support_level        ENUM('complete','incomplete','social') NOT NULL DEFAULT 'social',
    initiation_fee       INT UNSIGNED     NOT NULL DEFAULT 0,
    monthly_dues         INT UNSIGNED     NOT NULL DEFAULT 0,
    join_level           SMALLINT UNSIGNED NOT NULL DEFAULT 15,
    max_prepay_months    TINYINT UNSIGNED NOT NULL DEFAULT 3,
    has_skill_training   TINYINT(1)       NOT NULL DEFAULT 0,
    has_guildmaster      TINYINT(1)       NOT NULL DEFAULT 0,
    description          TEXT             DEFAULT NULL,
    oath_text            TEXT             DEFAULT NULL,
    is_active            TINYINT(1)       NOT NULL DEFAULT 1,
    PRIMARY KEY (guild_id),
    UNIQUE KEY uq_guild_profession (profession_id),
    CONSTRAINT fk_guilddefs_profession FOREIGN KEY (profession_id)
        REFERENCES professions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS guild_rank_definitions (
    guild_id             VARCHAR(32)       NOT NULL,
    rank_level           SMALLINT UNSIGNED NOT NULL,
    rank_name            VARCHAR(64)       NOT NULL,
    description          TEXT              DEFAULT NULL,
    PRIMARY KEY (guild_id, rank_level),
    CONSTRAINT fk_guildranks_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS character_guild_membership (
    id                   INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    character_id         INT UNSIGNED      NOT NULL,
    guild_id             VARCHAR(32)       NOT NULL,
    status               ENUM('active','resigned','suspended') NOT NULL DEFAULT 'active',
    rank_level           SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    rank_visible         TINYINT(1)        NOT NULL DEFAULT 1,
    is_guildmaster       TINYINT(1)        NOT NULL DEFAULT 0,
    vouchers             INT UNSIGNED      NOT NULL DEFAULT 0,
    joined_at            DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dues_paid_through    DATETIME          DEFAULT NULL,
    last_checkin_at      DATETIME          DEFAULT NULL,
    next_checkin_due_at  DATETIME          DEFAULT NULL,
    resigned_at          DATETIME          DEFAULT NULL,
    notes                JSON              DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_character_guild (character_id, guild_id),
    KEY idx_guildmember_char (character_id),
    KEY idx_guildmember_guild (guild_id),
    CONSTRAINT fk_guildmember_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildmember_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS character_guild_skills (
    character_id         INT UNSIGNED      NOT NULL,
    guild_id             VARCHAR(32)       NOT NULL,
    skill_name           VARCHAR(64)       NOT NULL,
    ranks                SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    training_points      INT UNSIGNED      NOT NULL DEFAULT 0,
    is_mastered          TINYINT(1)        NOT NULL DEFAULT 0,
    PRIMARY KEY (character_id, guild_id, skill_name),
    CONSTRAINT fk_guildskills_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildskills_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS character_guild_tasks (
    id                    INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    character_id          INT UNSIGNED      NOT NULL,
    guild_id              VARCHAR(32)       NOT NULL,
    skill_name            VARCHAR(64)       DEFAULT NULL,
    task_type             VARCHAR(64)       DEFAULT NULL,
    task_text             TEXT              DEFAULT NULL,
    repetitions_remaining SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    task_data             JSON              DEFAULT NULL,
    status                ENUM('assigned','complete','abandoned') NOT NULL DEFAULT 'assigned',
    assigned_at           DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at          DATETIME          DEFAULT NULL,
    PRIMARY KEY (id),
    KEY idx_guildtasks_char (character_id),
    KEY idx_guildtasks_guild (guild_id),
    CONSTRAINT fk_guildtasks_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildtasks_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS guild_master_registry (
    id                   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    guild_id             VARCHAR(32)      NOT NULL,
    npc_template_id      VARCHAR(64)      NOT NULL,
    role_type            ENUM('master','administrator','contact','trainer') NOT NULL DEFAULT 'contact',
    room_id              INT UNSIGNED     NOT NULL DEFAULT 0,
    lich_room_id         INT UNSIGNED     DEFAULT NULL,
    city_name            VARCHAR(64)      DEFAULT NULL,
    is_active            TINYINT(1)       NOT NULL DEFAULT 1,
    notes                TEXT             DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_guildmaster_template (guild_id, npc_template_id, room_id),
    KEY idx_guildmaster_room (room_id),
    CONSTRAINT fk_guildmaster_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE IF NOT EXISTS guild_ledger (
    id                   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    character_id         INT UNSIGNED     NOT NULL,
    guild_id             VARCHAR(32)      NOT NULL,
    entry_type           ENUM('join','dues','checkin','resign','promotion','task') NOT NULL,
    amount               INT              NOT NULL DEFAULT 0,
    months_paid          TINYINT UNSIGNED NOT NULL DEFAULT 0,
    actor_template_id    VARCHAR(64)      DEFAULT NULL,
    notes                TEXT             DEFAULT NULL,
    created_at           DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_guildledger_char (character_id),
    KEY idx_guildledger_guild (guild_id),
    CONSTRAINT fk_guildledger_char FOREIGN KEY (character_id)
        REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT fk_guildledger_guild FOREIGN KEY (guild_id)
        REFERENCES guild_definitions(guild_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

INSERT INTO guild_definitions (
    guild_id, profession_id, name, support_level, initiation_fee, monthly_dues,
    join_level, max_prepay_months, has_skill_training, has_guildmaster, description
) VALUES
    ('warrior', 1, 'Warrior Guild', 'complete', 10500, 3500, 15, 3, 1, 1, 'Complete profession guild with full training support.'),
    ('rogue', 2, 'Rogue Guild', 'complete', 15000, 5000, 15, 3, 1, 1, 'Complete profession guild with full training support.'),
    ('wizard', 3, 'Wizard Guild', 'incomplete', 4500, 1500, 15, 3, 1, 1, 'Partial profession guild. Foundation supports membership and dues first.'),
    ('cleric', 4, 'Cleric Guild', 'incomplete', 0, 750, 15, 3, 1, 1, 'Partial profession guild. Foundation supports membership and dues first.'),
    ('empath', 5, 'Empath Guild', 'incomplete', 0, 500, 15, 3, 1, 1, 'Partial profession guild. Foundation supports membership and dues first.'),
    ('sorcerer', 6, 'Sorcerer Guild', 'incomplete', 4500, 1500, 15, 3, 1, 1, 'Partial profession guild. Foundation supports membership and dues first.'),
    ('ranger', 7, 'Ranger Guild', 'social', 0, 1000, 15, 3, 0, 0, 'Guild building exists, but no skill training is available.'),
    ('bard', 8, 'Bard Guild', 'social', 2250, 750, 15, 3, 0, 0, 'Guild building exists, but no skill training is available.')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    support_level = VALUES(support_level),
    initiation_fee = VALUES(initiation_fee),
    monthly_dues = VALUES(monthly_dues),
    join_level = VALUES(join_level),
    max_prepay_months = VALUES(max_prepay_months),
    has_skill_training = VALUES(has_skill_training),
    has_guildmaster = VALUES(has_guildmaster),
    description = VALUES(description),
    is_active = 1;

INSERT INTO guild_rank_definitions (guild_id, rank_level, rank_name, description) VALUES
    ('warrior', 1, 'Member', 'A recognized member of the Warrior Guild.'),
    ('rogue', 1, 'Member', 'A recognized member of the Rogue Guild.'),
    ('wizard', 1, 'Member', 'A recognized member of the Wizard Guild.'),
    ('cleric', 1, 'Member', 'A recognized member of the Cleric Guild.'),
    ('empath', 1, 'Member', 'A recognized member of the Empath Guild.'),
    ('sorcerer', 1, 'Member', 'A recognized member of the Sorcerer Guild.'),
    ('ranger', 1, 'Member', 'A recognized member of the Ranger Guild.'),
    ('bard', 1, 'Member', 'A recognized member of the Bard Guild.')
ON DUPLICATE KEY UPDATE
    rank_name = VALUES(rank_name),
    description = VALUES(description);

INSERT INTO guild_master_registry (
    guild_id, npc_template_id, role_type, room_id, lich_room_id, city_name, notes
) VALUES
    ('bard', 'bard_master', 'master', 10438, 10438, 'Ta''Vaalor', 'Placed bard guild authority in the Ta''Vaalor Bard Guild entry.'),
    ('rogue', 'tv_rogue_guild_contact', 'master', 18348, 18348, 'Ta''Vaalor', 'Hidden rogue guild contact in the Ta''Vaalor basement guild room.'),
    ('warrior', 'kreldor', 'administrator', 3521, 3521, 'Ta''Vaalor', 'Local warrior guild contact using the placed weapon trainer.'),
    ('empath', 'empath_healer', 'administrator', 10759, 10759, 'Ta''Vaalor', 'Local empath guild contact using the placed empath guild healer.')
ON DUPLICATE KEY UPDATE
    role_type = VALUES(role_type),
    lich_room_id = VALUES(lich_room_id),
    city_name = VALUES(city_name),
    notes = VALUES(notes),
    is_active = 1;
