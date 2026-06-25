DROP TABLE IF EXISTS raw.tickets CASCADE;
DROP TABLE IF EXISTS raw.users CASCADE;
DROP TABLE IF EXISTS raw.categories CASCADE;
DROP TABLE IF EXISTS raw.support_staff CASCADE;

CREATE TABLE raw.users (
    user_id BIGINT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    level TEXT
);

CREATE TABLE raw.categories (
    category_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE raw.support_staff (
    staff_id BIGINT PRIMARY KEY,
    full_name TEXT NOT NULL,
    department TEXT,
    resolved_tickets_count INTEGER
);

CREATE TABLE raw.tickets (
    ticket_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES raw.users(user_id),
    category_id BIGINT NOT NULL REFERENCES raw.categories(category_id),
    subject TEXT,
    description TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    staff_id BIGINT REFERENCES raw.support_staff(staff_id),
    comments_json JSONB
);
