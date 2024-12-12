DROP TABLE IF EXISTS events;
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL UNIQUE,
    event_day INTEGER NOT NULL,
    event_month INTEGER NOT NULL,
    event_year INTEGER NOT NULL,
    is_religious BOOLEAN NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);