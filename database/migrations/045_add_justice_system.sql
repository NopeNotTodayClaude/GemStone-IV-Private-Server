CREATE TABLE IF NOT EXISTS character_justice_cases (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    character_id INT NOT NULL,
    jurisdiction_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'warrant',
    arrest_room_id INT NOT NULL DEFAULT 0,
    courtroom_room_id INT NOT NULL DEFAULT 0,
    jail_room_id INT NOT NULL DEFAULT 0,
    release_room_id INT NOT NULL DEFAULT 0,
    fine_amount INT NOT NULL DEFAULT 0,
    fine_due_at DATETIME NULL,
    incarceration_seconds INT NOT NULL DEFAULT 0,
    incarceration_end_at DATETIME NULL,
    service_seconds INT NOT NULL DEFAULT 0,
    service_task_key VARCHAR(64) NULL,
    service_state_json LONGTEXT NULL,
    question_set VARCHAR(64) NULL,
    question_prompt TEXT NULL,
    question_answer_key VARCHAR(64) NULL,
    question_due_at DATETIME NULL,
    banishment_expires_at DATETIME NULL,
    close_reason VARCHAR(128) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at DATETIME NULL,
    PRIMARY KEY (id),
    KEY idx_justice_cases_character_status (character_id, status),
    KEY idx_justice_cases_jurisdiction_status (jurisdiction_id, status),
    KEY idx_justice_cases_banishment (character_id, jurisdiction_id, banishment_expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS character_justice_case_charges (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    case_id BIGINT UNSIGNED NOT NULL,
    charge_code VARCHAR(64) NOT NULL,
    count INT NOT NULL DEFAULT 0,
    fine_amount INT NOT NULL DEFAULT 0,
    incarceration_seconds INT NOT NULL DEFAULT 0,
    service_seconds INT NOT NULL DEFAULT 0,
    severity INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_justice_case_charge (case_id, charge_code),
    KEY idx_justice_case_charges_case (case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS character_justice_history (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    character_id INT NOT NULL,
    jurisdiction_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    detail_text TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_justice_history_character_created (character_id, created_at),
    KEY idx_justice_history_jurisdiction_created (jurisdiction_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS character_justice_accusations (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    accuser_character_id INT NOT NULL,
    accused_character_id INT NOT NULL DEFAULT 0,
    accused_name VARCHAR(128) NOT NULL,
    jurisdiction_id VARCHAR(64) NOT NULL,
    charge_code VARCHAR(64) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_justice_accusations_accused (accused_character_id, created_at),
    KEY idx_justice_accusations_name (accused_name, created_at),
    KEY idx_justice_accusations_jurisdiction (jurisdiction_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
