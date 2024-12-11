DROP TABLE IF EXISTS events;
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_day INTEGER NOT NULL,
    event_month INTEGER NOT NULL,
    event_year INTEGER NOT NULL,
    event_name TEXT NOT NULL UNIQUE,
    is_religious BOOLEAN NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);