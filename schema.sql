-- USCIS checklist database (SQLite dialect).
-- Same tables and columns as the original MySQL design; the only changes are
-- `UNIQUE KEY name (...)` -> `UNIQUE (...)` and dropping `NULL` after TIMESTAMP.

CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE uscis_forms (
    id VARCHAR(36) PRIMARY KEY,
    form_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    official_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE form_requirements (
    id VARCHAR(36) PRIMARY KEY,
    form_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_required BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES uscis_forms(id) ON DELETE CASCADE
);

CREATE TABLE checklists (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    form_id VARCHAR(36) NOT NULL,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, form_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (form_id) REFERENCES uscis_forms(id) ON DELETE CASCADE
);

CREATE TABLE checklist_items (
    id VARCHAR(36) PRIMARY KEY,
    checklist_id VARCHAR(36) NOT NULL,
    requirement_id VARCHAR(36) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    user_notes TEXT,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (checklist_id, requirement_id),
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE,
    FOREIGN KEY (requirement_id) REFERENCES form_requirements(id) ON DELETE CASCADE
);
